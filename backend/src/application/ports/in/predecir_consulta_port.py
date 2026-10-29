from abc import ABC, abstractmethod


class PredecirConsultaPort(ABC):
    """Puerto de entrada del PMV2: los dos casos de uso de prediccion.

    - ejecutar(texto): estima, sin registrar ni responder, la probabilidad de cobertura
      documental (RF-14, HU-08.1) y la de relevancia de los pasajes de prosa (RF-15, HU-04).
    - modelos(): describe los modelos cargados y sus metricas de validacion cruzada."""

    @abstractmethod
    def ejecutar(self, texto: str) -> dict: ...

    @abstractmethod
    def modelos(self) -> list[dict]: ...
