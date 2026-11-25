from abc import ABC, abstractmethod
from datetime import datetime


class RepositorioValoracionesPort(ABC):
    """Persistencia de las valoraciones de REF-07 (ADR-040): una por consulta."""

    @abstractmethod
    def existe_consulta(self, consulta_id: str) -> bool: ...

    @abstractmethod
    def registrar(self, consulta_id: str, util: bool, momento: datetime) -> bool:
        """Guarda la valoración. Devuelve False si la consulta ya estaba valorada."""

    @abstractmethod
    def resumen(self) -> dict[str, int]:
        """Conteo agregado: {"util": n, "no_util": m}."""
