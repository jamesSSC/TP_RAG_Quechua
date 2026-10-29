from abc import ABC, abstractmethod

from domain.services.caracteristicas_consulta import CaracteristicasConsulta


class PredictorPort(ABC):
    """Modelo predictivo del PMV2 (RF-14, RF-15).

    El nucleo no sabe que tecnica hay detras: solo pide una probabilidad entre 0 y 1. Hoy la
    atiende una regresion logistica de scikit-learn; mañana podria ser un modelo exportado al
    telefono sin tocar los casos de uso."""

    @abstractmethod
    def probabilidad(self, caracteristicas: CaracteristicasConsulta) -> float | None:
        """Probabilidad estimada, o None si el modelo no esta disponible."""

    @abstractmethod
    def disponible(self) -> bool: ...

    @abstractmethod
    def metadatos(self) -> dict:
        """Nombre, version, fecha de entrenamiento y metricas de validacion cruzada."""
