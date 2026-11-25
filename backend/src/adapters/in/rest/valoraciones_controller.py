import logging

from fastapi import APIRouter, Depends, HTTPException

from application.ports import ResultadoValoracion, ValorarRespuestaPort

from . import dependencias
from .esquemas import ValoracionEntrada, ValoracionSalida

log = logging.getLogger("rag.rest")
router = APIRouter(prefix="/api")


@router.post(
    "/valoraciones", response_model=ValoracionSalida, status_code=201, tags=["consulta"]
)
def valorar(
    entrada: ValoracionEntrada,
    puerto: ValorarRespuestaPort = Depends(dependencias.valorar_respuesta),
):
    """REF-07 (ADR-040): «¿te sirvió esta respuesta?». Una valoración por consulta; no guarda
    ningún dato personal. 404 si la consulta no existe; 409 si ya se valoró."""
    log.info("[REST] POST /api/valoraciones")
    resultado = puerto.ejecutar(entrada.consulta_id, entrada.util)
    if resultado is ResultadoValoracion.CONSULTA_INEXISTENTE:
        raise HTTPException(404, "No existe una consulta con ese identificador")
    if resultado is ResultadoValoracion.YA_VALORADA:
        raise HTTPException(409, "Esta respuesta ya fue valorada")
    return ValoracionSalida(registrada=True)
