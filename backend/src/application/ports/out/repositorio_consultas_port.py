from abc import ABC, abstractmethod

from domain.entities.consulta import Consulta
from domain.entities.respuesta import Respuesta


class RepositorioConsultasPort(ABC):
    @abstractmethod
    def registrar(self, consulta: Consulta, respuesta: Respuesta) -> None: ...

    @abstractmethod
    def historial(self, limite: int = 50) -> list[tuple[Consulta, Respuesta]]:
        """Consultas y respuestas de la sesion activa (RF-11)."""

    @abstractmethod
    def no_cubiertas(self, limite: int = 500) -> list[Consulta]:
        """Consultas en las que el sistema se abstuvo. Es el insumo con el que el PMV2
        entrenara los modelos de prediccion de cobertura y de demanda lexica."""

    @abstractmethod
    def borrar_todo(self) -> int:
        """Borra el historial completo y devuelve cuantas consultas se eliminaron."""

    @abstractmethod
    def total_registradas(self) -> int: ...

    def estadisticas(self) -> dict:
        """Agregados del historial (HU-09). No es abstracto: un repositorio que no los
        calcule deja la analitica sin datos sin romper la consulta."""
        raise NotImplementedError

    def abstenciones_con_prediccion(self, limite: int = 5000) -> list[tuple[str, float | None]]:
        """Texto de cada consulta abstenida y la probabilidad de cobertura que se estimo."""
        raise NotImplementedError
