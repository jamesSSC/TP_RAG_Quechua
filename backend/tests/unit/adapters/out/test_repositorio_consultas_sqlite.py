"""Repositorio de consultas sobre SQLite en archivo temporal: registrar, listar, borrar."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from adapters.out.persistencia.modelos import Base
from adapters.out.persistencia.repositorio_consultas_sqlalchemy import (
    RepositorioConsultasSqlAlchemy,
)
from domain.entities.consulta import Consulta
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.entities.respuesta import Respuesta
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud

DOCUMENTO = "293274822-diccionario-quechua-Wanka-docx.pdf"


@pytest.fixture
def repo(tmp_path):
    motor = create_engine(
        f"sqlite:///{tmp_path / 'historial.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(motor)
    yield RepositorioConsultasSqlAlchemy(sessionmaker(motor, expire_on_commit=False))
    motor.dispose()


def _respondida(consulta: Consulta) -> Respuesta:
    zorro = FragmentoRecuperado(
        fragmento=Fragmento(
            id="zorro-37",
            texto="ZORRO: Atuq.",
            procedencia=Procedencia(DOCUMENTO, 37),
            tipo=TipoFragmento.LEXICOGRAFICO,
        ),
        puntuacion=PuntuacionSimilitud(0.61),
        coincidencia_lema=True,
    )
    return Respuesta(
        consulta_id=consulta.id,
        texto="ZORRO: Atuq.",
        respaldo=[zorro],
        similitud_maxima=0.61,
        via_respaldo="similitud",
    )


def test_registrar_listar_y_borrar(repo):
    c1, c2 = Consulta(texto="zorro"), Consulta(texto="criptomoneda")
    repo.registrar(c1, _respondida(c1))
    repo.registrar(c2, Respuesta(consulta_id=c2.id, texto="Sin respaldo", abstenida=True))

    historial = repo.historial(50)
    assert len(historial) == 2
    por_texto = {c.texto: r for c, r in historial}
    assert por_texto["zorro"].via_respaldo == "similitud"
    assert por_texto["zorro"].respaldo[0].procedencia.pagina == 37
    assert por_texto["criptomoneda"].abstenida and por_texto["criptomoneda"].via_respaldo is None

    assert repo.borrar_todo() == 2
    assert repo.historial(50) == []
    assert repo.total_registradas() == 0


def test_el_historial_sobrevive_a_una_nueva_conexion(tmp_path):
    url = f"sqlite:///{tmp_path / 'persistente.db'}"
    for _ in range(2):
        motor = create_engine(url)
        Base.metadata.create_all(motor)
        repo = RepositorioConsultasSqlAlchemy(sessionmaker(motor, expire_on_commit=False))
        if _ == 0:
            c = Consulta(texto="zorro")
            repo.registrar(c, _respondida(c))
        else:
            assert repo.total_registradas() == 1
        motor.dispose()


def test_el_modelo_no_guarda_datos_personales():
    nombres = {c.name for t in ("consultas", "respaldos") for c in Base.metadata.tables[t].columns}
    prohibidos = {"ip", "usuario", "user_agent", "useragent", "email", "nombre", "sesion"}
    assert not (nombres & prohibidos)


def test_pmv2_registra_la_prediccion_y_calcula_los_agregados(repo):
    c1 = Consulta(texto="zorro")
    r1 = _respondida(c1)
    r1.probabilidad_cobertura = 0.95
    r1.latencia_ms = 12.0
    repo.registrar(c1, r1)
    c2 = Consulta(texto="¿cómo se dice dron?")
    r2 = Respuesta(consulta_id=c2.id, texto="sin respaldo", abstenida=True)
    r2.probabilidad_cobertura = 0.05
    r2.latencia_ms = 3.0
    repo.registrar(c2, r2)

    e = repo.estadisticas()
    assert e["total"] == 2 and e["abstenidas"] == 1
    assert e["respaldo_por_documento"] == {DOCUMENTO: 1}
    assert round(e["probabilidad_cobertura_media"], 2) == 0.5
    assert repo.abstenciones_con_prediccion() == [("¿cómo se dice dron?", 0.05)]
    assert repo.historial()[1][1].probabilidad_cobertura == 0.95
