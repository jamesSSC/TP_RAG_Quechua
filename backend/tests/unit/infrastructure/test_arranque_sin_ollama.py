"""B14: sin Ollama el sistema arranca, lo avisa en /api/estado y responde con el literal."""

from importlib import import_module

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import infrastructure.contenedor as modulo
from infrastructure.config import Configuracion

BASE = (
    '{"id": "z", "documento": "293274822-diccionario-quechua-Wanka-docx.pdf", "pagina": 37, '
    '"texto": "ZORRO: Atuq.", "tipo": "lexicografico"}\n'
)


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    base = tmp_path / "base.jsonl"
    base.write_text(BASE, encoding="utf-8")
    config = Configuracion(
        _env_file=None,
        carpeta_datos=tmp_path / "datos",
        ruta_corpus_base=base,
        ruta_sqlite=tmp_path / "q.db",
        ollama_url="http://127.0.0.1:9",  # nadie escucha: Ollama inalcanzable
    )
    monkeypatch.setattr(modulo, "configuracion", config)
    contenedor = modulo.Contenedor(generador="ollama")
    app = FastAPI()
    for router in import_module("adapters.in.rest").routers:
        app.include_router(router)
    app.state.contenedor = contenedor
    return TestClient(app)


def test_el_estado_informa_que_ollama_no_responde(cliente):
    estado = cliente.get("/api/estado").json()
    assert estado["generador_disponible"] is False
    assert estado["base_datos_disponible"] is True
    assert estado["fragmentos_indexados"] == 1
    assert estado["modelo"]


@pytest.mark.salvaguarda
def test_sin_ollama_responde_con_el_fragmento_literal_citado_y_avisa(cliente):
    r = cliente.post("/api/consultas", json={"texto": "¿cómo se dice zorro en quechua wanka?"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert not cuerpo["abstenida"]
    assert cuerpo["texto"].startswith("ZORRO: Atuq.")
    assert cuerpo["respaldo"][0]["pagina"] == 37
    assert cuerpo["aviso_generacion"]
