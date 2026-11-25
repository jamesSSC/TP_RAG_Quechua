"""REF-07 (ADR-040): «¿te sirvió esta respuesta?».

Una valoración por consulta, sin datos personales; pública en la nube como la consulta, con su
mismo límite de peticiones. No toca τ, RN-06 ni la respuesta.
"""

from datetime import UTC, datetime
from importlib import import_module
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from adapters.out.persistencia.modelos import Base, ConsultaORM, ValoracionORM
from adapters.out.persistencia.repositorio_valoraciones_sqlalchemy import (
    RepositorioValoracionesSqlalchemy,
)
from application.ports import ResultadoValoracion
from application.use_cases.valorar_respuesta import ValorarRespuestaUseCase
from infrastructure.seguridad_nube import requiere_admin

rest = import_module("adapters.in.rest")
ID = "11111111-2222-3333-4444-555555555555"


@pytest.fixture
def sesion(tmp_path):
    motor = create_engine(f"sqlite:///{tmp_path / 'v.db'}")
    Base.metadata.create_all(motor)
    fabrica = sessionmaker(motor, expire_on_commit=False)
    with fabrica() as s:
        s.add(
            ConsultaORM(
                id=ID,
                texto="¿cómo se dice zorro?",
                idioma="es",
                momento=datetime.now(UTC),
                respuesta_texto="Atuq",
                abstenida=False,
                similitud_maxima=0.61,
            )
        )
        s.commit()
    return fabrica


def test_registra_una_valoracion_por_consulta(sesion):
    caso = ValorarRespuestaUseCase(RepositorioValoracionesSqlalchemy(sesion))
    assert caso.ejecutar(ID, True) is ResultadoValoracion.REGISTRADA
    assert caso.ejecutar(ID, False) is ResultadoValoracion.YA_VALORADA
    assert RepositorioValoracionesSqlalchemy(sesion).resumen() == {"util": 1, "no_util": 0}


def test_una_consulta_inexistente_no_se_valora(sesion):
    caso = ValorarRespuestaUseCase(RepositorioValoracionesSqlalchemy(sesion))
    assert caso.ejecutar("no-existe", True) is ResultadoValoracion.CONSULTA_INEXISTENTE
    assert RepositorioValoracionesSqlalchemy(sesion).resumen() == {"util": 0, "no_util": 0}


def test_la_tabla_no_guarda_datos_personales():
    columnas = {c.name for c in ValoracionORM.__table__.columns}
    assert columnas == {"consulta_id", "util", "momento"}


def test_create_all_crea_la_tabla_en_una_base_existente(tmp_path):
    motor = create_engine(f"sqlite:///{tmp_path / 'vieja.db'}")
    ConsultaORM.__table__.create(motor)  # base anterior: sin la tabla de valoraciones
    Base.metadata.create_all(motor)
    assert "valoraciones" in inspect(motor).get_table_names()


class _PuertoFalso:
    def __init__(self, resultado):
        self.resultado = resultado
        self.llamadas = []

    def ejecutar(self, consulta_id, util):
        self.llamadas.append((consulta_id, util))
        return self.resultado


def _cliente(puerto):
    app = FastAPI()
    for router in rest.routers:
        app.include_router(router)
    app.state.contenedor = SimpleNamespace(valorar_respuesta=puerto)
    return TestClient(app)


@pytest.mark.parametrize(
    ("resultado", "codigo"),
    [
        (ResultadoValoracion.REGISTRADA, 201),
        (ResultadoValoracion.CONSULTA_INEXISTENTE, 404),
        (ResultadoValoracion.YA_VALORADA, 409),
    ],
)
def test_controlador(resultado, codigo):
    puerto = _PuertoFalso(resultado)
    r = _cliente(puerto).post("/api/valoraciones", json={"consulta_id": ID, "util": False})
    assert r.status_code == codigo
    assert puerto.llamadas == [(ID, False)]


def test_no_acepta_texto_libre_ni_campos_extra():
    puerto = _PuertoFalso(ResultadoValoracion.REGISTRADA)
    cliente = _cliente(puerto)
    extra = {"consulta_id": ID, "util": True, "comentario": "mi nombre es…"}
    assert cliente.post("/api/valoraciones", json=extra).status_code == 422
    assert cliente.post("/api/valoraciones", json={"consulta_id": ID}).status_code == 422
    largo = {"consulta_id": "x" * 37, "util": True}
    assert cliente.post("/api/valoraciones", json=largo).status_code == 422
    assert puerto.llamadas == []


def test_sin_base_de_datos_responde_503():
    r = _cliente(None).post("/api/valoraciones", json={"consulta_id": ID, "util": True})
    assert r.status_code == 503


def test_en_la_nube_es_publica_como_la_consulta():
    assert requiere_admin("POST", "/api/valoraciones") is False
    # una ruta de escritura vecina sigue protegida por defecto
    assert requiere_admin("POST", "/api/valoraciones/borrar") is True


def test_borrar_el_historial_borra_tambien_las_valoraciones(sesion):
    from adapters.out.persistencia.repositorio_consultas_sqlalchemy import (
        RepositorioConsultasSqlAlchemy,
    )

    repositorio = RepositorioValoracionesSqlalchemy(sesion)
    repositorio.registrar(ID, True, datetime.now(UTC))
    assert RepositorioConsultasSqlAlchemy(sesion).borrar_todo() == 1
    assert repositorio.resumen() == {"util": 0, "no_util": 0}
