"""PMV2 · controlador REST de prediccion y analitica con fakes de los puertos de entrada."""

from importlib import import_module
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from application.ports import AnalizarDemandaPort, PredecirConsultaPort

rest = import_module("adapters.in.rest")


class PredecirFake(PredecirConsultaPort):
    def ejecutar(self, texto):
        return {"texto": texto, "cobertura": {"probabilidad": 0.97}, "pasajes": {}}

    def modelos(self):
        return [{"clave": "cobertura", "disponible": True}]


class DemandaFake(AnalizarDemandaPort):
    def ejecutar(self, top=15):
        return {"suficiente": True, "prioridades": [{"termino": "dron"}][:top]}


def _cliente(con_base_datos=True):
    app = FastAPI()
    for router in rest.routers:
        app.include_router(router)
    app.state.contenedor = SimpleNamespace(
        predecir_consulta=PredecirFake(),
        analizar_demanda=DemandaFake() if con_base_datos else None,
    )
    return TestClient(app)


def test_post_predicciones_devuelve_la_probabilidad():
    r = _cliente().post("/api/predicciones", json={"texto": "  zorro  "})
    assert r.status_code == 200
    assert r.json()["texto"] == "zorro"
    assert r.json()["cobertura"]["probabilidad"] == 0.97


def test_post_predicciones_valida_la_longitud():
    assert _cliente().post("/api/predicciones", json={"texto": ""}).status_code == 422
    assert _cliente().post("/api/predicciones", json={"texto": "x" * 301}).status_code == 422


def test_get_modelos():
    assert _cliente().get("/api/modelos").json()[0]["clave"] == "cobertura"


def test_get_demanda_y_503_sin_base_de_datos():
    assert _cliente().get("/api/analitica/demanda?top=1").json()["prioridades"] == [
        {"termino": "dron"}
    ]
    assert _cliente(con_base_datos=False).get("/api/analitica/demanda").status_code == 503
