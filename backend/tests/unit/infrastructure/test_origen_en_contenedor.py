"""HU-09: el origen lo fija el servidor (nunca el cliente) y /api/estado rotula la base."""

import pytest
from fastapi.testclient import TestClient

import infrastructure.contenedor as modulo
from domain.value_objects.origen_consulta import OrigenConsulta
from infrastructure.config import Configuracion

BASE = (
    '{"id": "b1", "documento": "base.pdf", "pagina": 1, "texto": "ZORRO: Atuq.", '
    '"tipo": "lexicografico"}\n'
)


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    base = tmp_path / "base.jsonl"
    base.write_text(BASE, encoding="utf-8")
    monkeypatch.delenv("ORIGEN_CONSULTAS", raising=False)
    config = Configuracion(
        _env_file=None,
        carpeta_datos=tmp_path / "datos",
        ruta_corpus_base=base,
        ruta_sqlite=tmp_path / "q.db",
    )
    monkeypatch.setattr(modulo, "configuracion", config)
    return config


def test_por_defecto_todo_es_usuario(entorno):
    c = modulo.Contenedor(generador="literal")
    c.consultar_corpus.ejecutar("zorro")
    assert c.repositorio_consultas.conteo_por_origen() == {"usuario": 1}
    assert c.estado()["base_demostracion"] is False


def test_el_script_de_carga_fija_el_origen_al_construir(entorno):
    c = modulo.Contenedor(generador="literal", origen=OrigenConsulta.CARGA)
    c.consultar_corpus.ejecutar("zorro")
    assert c.repositorio_consultas.conteo_por_origen() == {"carga": 1}
    estado = c.estado()
    assert estado["base_demostracion"] is True
    assert estado["consultas_por_origen"] == {"carga": 1}


def test_el_origen_se_lee_de_la_configuracion_del_servidor(entorno, monkeypatch):
    monkeypatch.setenv("ORIGEN_CONSULTAS", "humo")
    monkeypatch.setattr(
        modulo,
        "configuracion",
        Configuracion(
            _env_file=None,
            carpeta_datos=entorno.carpeta_datos,
            ruta_corpus_base=entorno.ruta_corpus_base,
            ruta_sqlite=entorno.ruta_sqlite,
        ),
    )
    c = modulo.Contenedor(generador="literal")
    c.consultar_corpus.ejecutar("zorro")
    assert c.repositorio_consultas.conteo_por_origen() == {"humo": 1}


def test_la_api_publica_ignora_un_origen_enviado_por_el_cliente(entorno):
    from importlib import import_module

    from fastapi import FastAPI

    c = modulo.Contenedor(generador="literal")
    app = FastAPI()
    for router in import_module("adapters.in.rest").routers:
        app.include_router(router)
    app.state.contenedor = c
    r = TestClient(app).post("/api/consultas", json={"texto": "zorro", "origen": "carga"})
    assert r.status_code == 200
    assert c.repositorio_consultas.conteo_por_origen() == {"usuario": 1}
    estado = TestClient(app).get("/api/estado").json()
    assert estado["base_demostracion"] is False
    assert estado["consultas_por_origen"] == {"usuario": 1}
