"""PMV2 · procedimientos almacenados de PostgreSQL (db/postgres/procedimientos.sql).

Prueba de integracion: necesita un servidor PostgreSQL y se omite si no se define
POSTGRES_PRUEBAS_URL, p. ej.
    POSTGRES_PRUEBAS_URL=postgresql+psycopg://postgres@127.0.0.1:55432/quechua_wanka
"""

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from adapters.out.persistencia.modelos import Base
from adapters.out.persistencia.repositorio_consultas_postgres import (
    RepositorioConsultasPostgres,
    instalar_procedimientos,
)
from domain.entities.consulta import Consulta
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.entities.respuesta import Respuesta
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud

URL = os.environ.get("POSTGRES_PRUEBAS_URL")
pytestmark = pytest.mark.skipif(not URL, reason="sin POSTGRES_PRUEBAS_URL")
DOCUMENTO = "293274822-diccionario-quechua-Wanka-docx.pdf"


@pytest.fixture
def repo():
    motor = create_engine(URL)
    Base.metadata.drop_all(motor)
    Base.metadata.create_all(motor)
    instalar_procedimientos(motor)
    yield RepositorioConsultasPostgres(sessionmaker(motor, expire_on_commit=False))
    Base.metadata.drop_all(motor)
    motor.dispose()


def _zorro():
    return FragmentoRecuperado(
        fragmento=Fragmento(
            id="zorro-37",
            texto="ZORRO: Atuq.",
            procedencia=Procedencia(DOCUMENTO, 37),
            tipo=TipoFragmento.LEXICOGRAFICO,
        ),
        puntuacion=PuntuacionSimilitud(0.61),
        coincidencia_lema=True,
    )


def test_los_procedimientos_existen(repo):
    with repo._sesion() as s:
        nombres = set(
            s.scalars(
                text(
                    "SELECT proname FROM pg_proc WHERE proname IN ('sp_registrar_consulta',"
                    "'sp_borrar_historial','fn_resumen_demanda','fn_respaldo_por_documento',"
                    "'fn_demanda_insatisfecha')"
                )
            ).all()
        )
    assert len(nombres) == 5


def test_registrar_por_procedimiento_y_agregar_por_funcion(repo):
    c1 = Consulta(texto="zorro")
    r1 = Respuesta(consulta_id=c1.id, texto="ZORRO: Atuq.", respaldo=[_zorro()])
    r1.probabilidad_cobertura, r1.latencia_ms = 0.95, 10.0
    repo.registrar(c1, r1)
    c2 = Consulta(texto="¿cómo se dice dron?")
    r2 = Respuesta(consulta_id=c2.id, texto="sin respaldo", abstenida=True)
    r2.probabilidad_cobertura, r2.latencia_ms = 0.05, 2.0
    repo.registrar(c2, r2)

    e = repo.estadisticas()
    assert e["origen"] == "procedimientos almacenados"
    assert e["total"] == 2 and e["abstenidas"] == 1
    assert e["respaldo_por_documento"] == {DOCUMENTO: 1}
    assert repo.abstenciones_con_prediccion() == [("¿cómo se dice dron?", 0.05)]
    assert repo.historial()[-1][1].respaldo[0].procedencia.pagina == 37
    assert repo.borrar_todo() == 2
    assert repo.total_registradas() == 0


def test_el_procedimiento_rechaza_una_respuesta_sin_respaldo(repo):
    with pytest.raises(Exception, match="sin respaldo documental"):
        with repo._sesion() as s, s.begin():
            s.execute(
                text(
                    "CALL sp_registrar_consulta('x','t','es',NULL,now(),'r',FALSE,0.9,"
                    "'similitud',NULL,NULL,FALSE,0,1.0,'[]'::jsonb)"
                )
            )
