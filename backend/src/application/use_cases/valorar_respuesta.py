import logging
from datetime import UTC, datetime

from application.ports import ResultadoValoracion, ValorarRespuestaPort
from application.ports.out.repositorio_valoraciones_port import RepositorioValoracionesPort

log = logging.getLogger("rag.caso_uso")


class ValorarRespuestaUseCase(ValorarRespuestaPort):
    """REF-07 (ADR-040): registra si una respuesta le sirvió a quien la pidió. Una sola
    valoración por consulta; no cambia la respuesta, τ ni ninguna regla del sistema."""

    def __init__(self, repositorio: RepositorioValoracionesPort):
        self._repositorio = repositorio

    def ejecutar(self, consulta_id: str, util: bool) -> ResultadoValoracion:
        log.info("[CASO-USO] ValorarRespuesta: util=%s", util)
        if not self._repositorio.existe_consulta(consulta_id):
            return ResultadoValoracion.CONSULTA_INEXISTENTE
        if not self._repositorio.registrar(consulta_id, util, datetime.now(UTC)):
            return ResultadoValoracion.YA_VALORADA
        return ResultadoValoracion.REGISTRADA
