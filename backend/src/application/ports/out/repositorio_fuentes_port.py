from abc import ABC, abstractmethod

from domain.entities.fuente import Fuente


class RepositorioFuentesPort(ABC):
    """Persistencia de la gobernanza documental (RNF-11). Es el puerto que implementa el
    adaptador de base de datos de escritorio y que en el incremento movil implementaria SQLite."""

    @abstractmethod
    def crear(self, fuente: Fuente) -> Fuente: ...

    @abstractmethod
    def obtener(self, fuente_id: str) -> Fuente | None: ...

    @abstractmethod
    def listar(self) -> list[Fuente]: ...

    @abstractmethod
    def actualizar(self, fuente: Fuente) -> Fuente: ...

    @abstractmethod
    def eliminar(self, fuente_id: str) -> bool: ...
