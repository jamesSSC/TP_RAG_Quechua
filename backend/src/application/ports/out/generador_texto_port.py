from abc import ABC, abstractmethod

from domain.entities.fragmento import FragmentoRecuperado
from domain.value_objects.idioma import Idioma


class GeneradorNoDisponible(Exception):
    """El servicio de redaccion no respondio (modelo caido, tiempo agotado, error de red).

    El caso de uso la captura y responde con el fragmento literal citado: la falta del
    generador nunca debe convertirse en un error del servicio ni en una forma inventada."""


class GeneradorTextoPort(ABC):
    # Quien redacta, para el rotulo «Redactado por» de la respuesta (ADR-032).
    nombre: str = "modelo"

    @abstractmethod
    def redactar(
        self,
        consulta: str,
        fragmentos: list[FragmentoRecuperado],
        idioma: Idioma,
    ) -> str:
        """Redacta la respuesta ciniendose a los fragmentos recibidos.

        El generador no aporta conocimiento linguistico: la informacion sustantiva proviene
        del fragmento recuperado y no de los pesos del modelo. Ninguna implementacion debe
        invocarse sin fragmentos."""

    @abstractmethod
    def disponible(self) -> bool: ...

    def procedencia_redaccion(self) -> tuple[str, str | None]:
        """(quien redacto, motivo) de la ultima redaccion de ESTE hilo. Por defecto, el propio
        generador y sin motivo; GeneradorExtractivo lo sobrescribe cuando el verificador
        sustituye la extraccion por el fragmento literal."""
        return self.nombre, None
