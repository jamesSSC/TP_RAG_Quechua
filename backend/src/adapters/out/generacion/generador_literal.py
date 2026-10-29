import logging

from application.ports.out.generador_texto_port import GeneradorTextoPort
from domain.entities.fragmento import FragmentoRecuperado
from domain.value_objects.idioma import Idioma

log = logging.getLogger("rag.generador")


class GeneradorLiteral(GeneradorTextoPort):
    # Rotulo de la nube sin modelo (GENERADOR=extractivo): el texto es el fragmento citado.
    nombre = "extractivo"

    """Compone la respuesta con el texto literal de los fragmentos, sin modelo de lenguaje.

    Sirve a la CLI y a los equipos sin Ollama. No aporta ni reformula nada: cada linea es el
    fragmento tal como esta indexado, con su documento y pagina. Como el resto de
    generadores, solo se invoca cuando el evaluador ya decidio que hay respaldo."""

    def redactar(
        self,
        consulta: str,
        fragmentos: list[FragmentoRecuperado],
        idioma: Idioma,
    ) -> str:
        if not fragmentos:
            raise ValueError("El generador no puede invocarse sin fragmentos de respaldo")
        log.info("[GENERADOR] texto literal de %d fragmento(s), sin modelo", len(fragmentos))
        return "\n".join(
            f"{f.texto} ({f.procedencia.documento}, p. {f.procedencia.pagina})" for f in fragmentos
        )

    def precalentar(self) -> bool:
        return True

    def disponible(self) -> bool:
        return True
