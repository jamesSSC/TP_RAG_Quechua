"""PMV2 · controlador REST de los casos de uso de prediccion y de analitica (HU-08.1, HU-04,
HU-09). Solo traduce HTTP <-> DTO y depende de los puertos de entrada."""

import logging

from fastapi import APIRouter, Depends

from application.ports import AnalizarDemandaPort, PredecirConsultaPort

from . import dependencias
from .esquemas import ConsultaEntrada

log = logging.getLogger("rag.rest")
router = APIRouter(prefix="/api")


@router.post("/predicciones", tags=["prediccion"])
def predecir(
    entrada: ConsultaEntrada,
    puerto: PredecirConsultaPort = Depends(dependencias.predecir_consulta),
):
    """Casos de uso de prediccion 1 y 2: probabilidad de cobertura documental (RF-14) y de
    relevancia de los pasajes de prosa (RF-15). No responde ni registra la consulta."""
    log.info("[REST] POST /api/predicciones")
    log.info("[PUERTO-IN] PredecirConsultaPort.ejecutar")
    return puerto.ejecutar(entrada.texto)


@router.get("/modelos", tags=["prediccion"])
def modelos(puerto: PredecirConsultaPort = Depends(dependencias.predecir_consulta)):
    """Modelos cargados, su algoritmo y sus metricas de validacion cruzada."""
    log.info("[REST] GET /api/modelos")
    return puerto.modelos()


@router.get("/analitica/demanda", tags=["prediccion"])
def demanda(
    top: int = 15,
    puerto: AnalizarDemandaPort = Depends(dependencias.analizar_demanda),
):
    """HU-09: demanda insatisfecha ponderada por el modelo de cobertura."""
    log.info("[REST] GET /api/analitica/demanda")
    log.info("[PUERTO-IN] AnalizarDemandaPort.ejecutar")
    return puerto.ejecutar(top)
