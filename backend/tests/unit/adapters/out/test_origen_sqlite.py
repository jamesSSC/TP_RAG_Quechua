"""HU-09: origen de la consulta en SQLite (registro, filtro y migracion de una .db antigua)."""

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from adapters.out.persistencia.modelos import Base
from adapters.out.persistencia.repositorio_consultas_sqlalchemy import (
    RepositorioConsultasSqlAlchemy,
)
from domain.entities.consulta import Consulta
from domain.entities.respuesta import Respuesta
from domain.value_objects.origen_consulta import OrigenConsulta
from infrastructure.contenedor import Contenedor


@pytest.fixture
def motor(tmp_path):
    m = create_engine(f"sqlite:///{tmp_path / 'o.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(m)
    yield m
    m.dispose()


def _registrar(repo, texto, origen):
    c = Consulta(texto=texto, origen=origen)
    repo.registrar(c, Respuesta(consulta_id=c.id, texto="Sin respaldo", abstenida=True))


def test_registra_y_cuenta_por_origen_y_filtra_la_analitica(motor):
    repo = RepositorioConsultasSqlAlchemy(sessionmaker(motor, expire_on_commit=False))
    _registrar(repo, "uno", OrigenConsulta.USUARIO)
    _registrar(repo, "dos", OrigenConsulta.CARGA)
    _registrar(repo, "tres", OrigenConsulta.CARGA)
    _registrar(repo, "cuatro", OrigenConsulta.HUMO)

    assert repo.conteo_por_origen() == {"usuario": 1, "carga": 2, "humo": 1}
    assert repo.estadisticas()["total"] == 1
    assert repo.estadisticas(incluir_sinteticas=True)["total"] == 4
    assert [t for t, _ in repo.abstenciones_con_prediccion()] == ["uno"]
    assert len(repo.abstenciones_con_prediccion(incluir_sinteticas=True)) == 4
    assert {c.origen for c, _ in repo.historial(10)} == {
        OrigenConsulta.USUARIO,
        OrigenConsulta.CARGA,
        OrigenConsulta.HUMO,
    }  # el historial conserva el origen


def test_migra_una_base_antigua_sin_la_columna_origen(tmp_path):
    motor = create_engine(f"sqlite:///{tmp_path / 'vieja.db'}")
    Base.metadata.create_all(motor)
    with motor.begin() as c:
        c.execute(text("ALTER TABLE consultas DROP COLUMN origen"))
        c.execute(
            text(
                "INSERT INTO consultas (id, texto, idioma, momento, respuesta_texto, abstenida,"
                " similitud_maxima, abstencion_por_predictor, pasajes_ofrecidos)"
                " VALUES ('x','zorro','es','2026-01-01','r',1,0.1,0,0)"
            )
        )
    assert "origen" not in {c["name"] for c in inspect(motor).get_columns("consultas")}

    Contenedor._migrar_columnas_pmv2(motor)
    Contenedor._migrar_columnas_pmv2(motor)  # idempotente

    assert "origen" in {c["name"] for c in inspect(motor).get_columns("consultas")}
    repo = RepositorioConsultasSqlAlchemy(sessionmaker(motor, expire_on_commit=False))
    assert repo.conteo_por_origen() == {"usuario": 1}  # lo anterior era del usuario
