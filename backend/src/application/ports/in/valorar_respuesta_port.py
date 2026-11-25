from abc import ABC, abstractmethod
from enum import Enum


class ResultadoValoracion(Enum):
    REGISTRADA = "registrada"
    CONSULTA_INEXISTENTE = "consulta_inexistente"
    YA_VALORADA = "ya_valorada"


class ValorarRespuestaPort(ABC):
    """Puerto de entrada de REF-07 (ADR-040): «¿te sirvió esta respuesta?».

    Solo se guarda el identificador de la consulta, si sirvió y la hora. Ningún dato personal:
    ni el texto, ni la IP, ni un comentario libre."""

    @abstractmethod
    def ejecutar(self, consulta_id: str, util: bool) -> ResultadoValoracion: ...
