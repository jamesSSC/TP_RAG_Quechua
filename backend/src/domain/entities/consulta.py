from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from domain.value_objects.idioma import Idioma
from domain.value_objects.origen_consulta import OrigenConsulta


@dataclass
class Consulta:
    texto: str
    idioma: Idioma = Idioma.ESPANOL
    id: str = field(default_factory=lambda: str(uuid4()))
    momento: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    texto_traducido: str | None = None
    variantes: list[str] = field(default_factory=list)
    origen: OrigenConsulta = OrigenConsulta.USUARIO

    def __post_init__(self):
        self.texto = self.texto.strip()
        if not self.texto:
            raise ValueError("La consulta no puede estar vacia")

    @property
    def texto_para_recuperar(self) -> str:
        """La consulta traducida al espanol cuando la hay. Solo se traduce la consulta:
        nunca el corpus ni la respuesta, para que el traductor no intervenga en ningun
        punto sobre la lengua que el sistema documenta."""
        return self.texto_traducido or self.texto
