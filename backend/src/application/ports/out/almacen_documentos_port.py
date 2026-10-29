from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentoAlmacenado:
    nombre: str
    sha256: str
    duplicado: bool


class AlmacenDocumentosPort(ABC):
    """Conserva los PDF incorporados por el usuario, con su SHA-256, en una carpeta de datos
    modificable (BUG-01). Un contenido ya guardado no se duplica."""

    @abstractmethod
    def guardar(self, contenido: bytes, nombre: str) -> DocumentoAlmacenado: ...

    @abstractmethod
    def listar(self) -> dict[str, str]:
        """Nombre del archivo guardado -> SHA-256."""
