"""Cabeceras de seguridad en cada respuesta (hallazgos tipicos de un escaneo pasivo)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.seguridad import CABECERAS_BASE, CabecerasDeSeguridad


def _cliente():
    app = FastAPI()
    app.add_middleware(CabecerasDeSeguridad)

    @app.get("/api/x")
    def x():
        return {"ok": True}

    @app.get("/")
    def raiz():
        return {"interfaz": True}

    @app.get("/docs-falsa")
    def otra():
        return {}

    return TestClient(app)


def test_toda_respuesta_lleva_las_cabeceras_base():
    r = _cliente().get("/api/x")
    for nombre, valor in CABECERAS_BASE.items():
        assert r.headers[nombre] == valor
    assert r.headers["X-Frame-Options"] == "DENY"


def test_la_api_no_se_guarda_en_cache():
    assert _cliente().get("/api/x").headers["Cache-Control"] == "no-store"
    assert "Cache-Control" not in _cliente().get("/").headers


def test_la_interfaz_lleva_csp_sin_recursos_de_terceros():
    csp = _cliente().get("/").headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp and "frame-ancestors 'none'" in csp
    assert "http" not in csp  # ningun origen externo permitido


def test_la_documentacion_interactiva_queda_fuera_de_la_csp_estricta():
    app = FastAPI()
    app.add_middleware(CabecerasDeSeguridad)
    cliente = TestClient(app)
    assert "Content-Security-Policy" not in cliente.get("/docs").headers
    assert cliente.get("/docs").headers["X-Content-Type-Options"] == "nosniff"
