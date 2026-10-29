"""BASE_DATOS decide el adaptador de persistencia que cablea el contenedor."""

import pytest
from sqlalchemy import create_engine as crear_motor_real

import infrastructure.contenedor as modulo
from adapters.out.persistencia.repositorio_consultas_postgres import (
    RepositorioConsultasPostgres,
)
from adapters.out.persistencia.repositorio_consultas_sqlalchemy import (
    RepositorioConsultasSqlAlchemy,
)
from infrastructure.config import Configuracion

BASE = (
    '{"id": "b1", "documento": "base.pdf", "pagina": 1, "texto": "ZORRO: Atuq.", '
    '"tipo": "lexicografico"}\n'
)


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    base = tmp_path / "base.jsonl"
    base.write_text(BASE, encoding="utf-8")
    monkeypatch.delenv("BASE_DATOS", raising=False)

    def config(**extra):
        return Configuracion(
            _env_file=None,
            carpeta_datos=tmp_path / "datos",
            ruta_corpus_base=base,
            ruta_sqlite=tmp_path / "q.db",
            **extra,
        )

    return tmp_path, config, monkeypatch


def test_por_defecto_el_contenedor_usa_el_adaptador_sqlalchemy(entorno):
    _, config, monkeypatch = entorno
    monkeypatch.setattr(modulo, "configuracion", config())
    repo = modulo.Contenedor(generador="literal").repositorio_consultas
    assert type(repo) is RepositorioConsultasSqlAlchemy


def test_con_base_datos_postgres_cablea_el_repositorio_de_procedimientos(entorno):
    tmp_path, config, monkeypatch = entorno
    instalados = []
    pedidas = []

    def motor_falso(url, **opciones):
        # Sin servidor: se comprueba el cableado, no la conexion. Un SQLite hace de motor.
        pedidas.append((url, opciones))
        return crear_motor_real(f"sqlite:///{tmp_path / 'falso.db'}")

    monkeypatch.setattr(modulo, "create_engine", motor_falso)
    monkeypatch.setattr(modulo, "instalar_procedimientos", lambda motor: instalados.append(motor))
    monkeypatch.setattr(
        modulo,
        "configuracion",
        config(base_datos="postgres", postgres_host="h", postgres_db="d", postgres_password="p"),
    )
    contenedor = modulo.Contenedor(generador="literal")
    assert type(contenedor.repositorio_consultas) is RepositorioConsultasPostgres
    assert len(instalados) == 1  # los procedimientos se instalan al arrancar
    assert pedidas[0][0].startswith("postgresql+psycopg://")
    assert pedidas[0][1]["pool_pre_ping"] is True


def test_la_base_se_elige_por_variable_de_entorno(entorno):
    _, _, monkeypatch = entorno
    monkeypatch.setenv("BASE_DATOS", "postgres")
    assert Configuracion(_env_file=None).base_datos == "postgres"


def test_el_generador_se_elige_por_configuracion(monkeypatch):
    assert Configuracion(_env_file=None).generador == "ollama"
    monkeypatch.setenv("GENERADOR", "literal")
    assert Configuracion(_env_file=None).generador == "literal"


def test_sqlite_espera_los_bloqueos_y_usa_wal(entorno):
    """Consultas simultaneas escriben el historial sin 'database is locked'."""
    from sqlalchemy import create_engine as crear

    tmp_path, config, monkeypatch = entorno
    motores = []

    def espia(url, **opciones):
        motor = crear(url, **opciones)
        motores.append((motor, opciones))
        return motor

    monkeypatch.setattr(modulo, "create_engine", espia)
    monkeypatch.setattr(modulo, "configuracion", config())
    modulo.Contenedor(generador="literal")
    motor, opciones = motores[0]
    assert opciones["connect_args"]["timeout"] >= 30
    with motor.connect() as c:
        assert c.exec_driver_sql("PRAGMA journal_mode").scalar().lower() == "wal"


def test_los_errores_de_base_de_datos_no_muestran_los_parametros(entorno):
    from sqlalchemy import create_engine as crear

    tmp_path, config, monkeypatch = entorno
    opciones_vistas = []

    def espia(url, **opciones):
        opciones_vistas.append(opciones)
        return crear(url, **{k: v for k, v in opciones.items()})

    monkeypatch.setattr(modulo, "create_engine", espia)
    monkeypatch.setattr(modulo, "configuracion", config())
    modulo.Contenedor(generador="literal")
    assert opciones_vistas[0]["hide_parameters"] is True
