"""Obtiene del contenedor el puerto de entrada que necesita cada controlador.

El contenedor se cuelga de `app.state` al arrancar (infrastructure/main.py); aqui solo se
lee, de modo que los controladores no importan la infraestructura.
"""

from fastapi import HTTPException, Request

from application.ports import (
    AnalizarDemandaPort,
    ConsultarCorpusPort,
    ConsultarHistorialPort,
    GestionarFuentesPort,
    IngestarDocumentoPort,
    PredecirConsultaPort,
    ReindexarCorpusPort,
)


def _contenedor(request: Request):
    return request.app.state.contenedor


def consultar_corpus(request: Request) -> ConsultarCorpusPort:
    # `origen_pruebas` solo existe si la peticion trajo el token de pruebas del servidor
    # (infrastructure/seguridad.py); el cliente normal nunca elige el origen (HU-09).
    origen = request.scope.get("state", {}).get("origen_pruebas")
    contenedor = _contenedor(request)
    if origen and hasattr(contenedor, "consultar_corpus_para"):
        return contenedor.consultar_corpus_para(origen)
    return contenedor.consultar_corpus


def ingestar_documento(request: Request) -> IngestarDocumentoPort:
    return _contenedor(request).ingestar_documento


def reindexar_corpus(request: Request) -> ReindexarCorpusPort:
    return _contenedor(request).reindexar_corpus


def consultar_historial(request: Request) -> ConsultarHistorialPort:
    puerto = _contenedor(request).consultar_historial
    if puerto is None:
        raise HTTPException(503, "El historial requiere la base de datos y no esta conectada")
    return puerto


def gestionar_fuentes(request: Request) -> GestionarFuentesPort:
    puerto = _contenedor(request).gestionar_fuentes
    if puerto is None:
        raise HTTPException(503, "La gestion de fuentes requiere la base de datos")
    return puerto


def predecir_consulta(request: Request) -> PredecirConsultaPort:
    return _contenedor(request).predecir_consulta


def analizar_demanda(request: Request) -> AnalizarDemandaPort:
    puerto = _contenedor(request).analizar_demanda
    if puerto is None:
        raise HTTPException(503, "La analitica de demanda requiere la base de datos")
    return puerto


def estado_sistema(request: Request) -> dict:
    return _contenedor(request).estado()
