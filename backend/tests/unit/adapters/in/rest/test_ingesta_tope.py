"""Auditoria PR #4 (M1, M3): tope por bloques en el controlador y errores de dominio como 4xx."""

from importlib import import_module
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.datastructures import UploadFile as StarletteUploadFile

from application.ports import IngestarDocumentoPort
from application.ports.out.almacen_documentos_port import ErrorAlmacenDocumentos

rest = import_module("adapters.in.rest")
controlador = import_module("adapters.in.rest.corpus_controller")

DATOS = {"titulo": "t", "entidad_publicadora": "e", "licenciamiento": "l"}


class IngestaQueFalla(IngestarDocumentoPort):
    def __init__(self, error=None):
        self.llamadas = 0
        self._error = error

    def ejecutar(self, **kwargs):
        self.llamadas += 1
        raise self._error


def _cliente(puerto):
    app = FastAPI()
    for router in rest.routers:
        app.include_router(router)
    app.state.contenedor = SimpleNamespace(ingestar_documento=puerto)
    return TestClient(app)


def test_corta_la_lectura_al_superar_el_tope_sin_leer_todo(monkeypatch):
    monkeypatch.setattr(controlador, "TAMANO_MAXIMO", 10)
    monkeypatch.setattr(controlador, "TAMANO_BLOQUE", 4)
    lecturas = []
    original = StarletteUploadFile.read

    async def espia(self, size=-1):
        lecturas.append(size)
        return await original(self, size)

    monkeypatch.setattr(StarletteUploadFile, "read", espia)
    puerto = IngestaQueFalla(ValueError("no debe llegar"))
    r = _cliente(puerto).post(
        "/api/corpus/documentos",
        files={"archivo": ("grande.pdf", b"x" * 1000, "application/pdf")},
        data=DATOS,
    )
    assert r.status_code == 413
    assert puerto.llamadas == 0
    assert lecturas == [4, 4, 4]  # 12 > 10 en la tercera lectura: no se leyeron los 1000 bytes


def test_un_archivo_dentro_del_tope_llega_al_caso_de_uso(monkeypatch):
    monkeypatch.setattr(controlador, "TAMANO_MAXIMO", 10)
    monkeypatch.setattr(controlador, "TAMANO_BLOQUE", 4)
    puerto = IngestaQueFalla(ValueError("llego"))
    r = _cliente(puerto).post(
        "/api/corpus/documentos",
        files={"archivo": ("ok.pdf", b"0123456789", "application/pdf")},
        data=DATOS,
    )
    assert puerto.llamadas == 1
    assert r.status_code == 422


def test_el_error_del_almacen_sale_como_4xx_no_como_500():
    puerto = IngestaQueFalla(ErrorAlmacenDocumentos("Nombre reservado del sistema operativo"))
    r = _cliente(puerto).post(
        "/api/corpus/documentos",
        files={"archivo": ("CON.pdf", b"x", "application/pdf")},
        data=DATOS,
    )
    assert r.status_code == 422
    assert "reservado" in r.json()["detail"]
