from abc import ABC, abstractmethod


class AnalizarDemandaPort(ABC):
    """Puerto de entrada de HU-09 (RF-16): demanda insatisfecha y priorizacion del corpus."""

    @abstractmethod
    def ejecutar(self, top: int = 15) -> dict: ...
