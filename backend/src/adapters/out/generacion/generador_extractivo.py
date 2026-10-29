import json
import logging

from adapters.out.generacion.ollama_generador import OllamaGenerador
from application.ports.out.generador_texto_port import GeneradorTextoPort
from domain.entities.fragmento import FragmentoRecuperado
from domain.services.verificador_forma_literal import VerificadorFormaLiteral
from domain.value_objects.idioma import Idioma

log = logging.getLogger("rag.generador")

PLANTILLA = {
    Idioma.ESPANOL: "En quechua wanka, \u00ab{glosa}\u00bb se dice {forma}.",
    Idioma.INGLES: "In Wanka Quechua, \u00ab{glosa}\u00bb is {forma}.",
}


class GeneradorExtractivo(GeneradorTextoPort):
    """Redaccion extractiva verificada (ADR-028). El modelo solo extrae `{forma, glosa}`; si ambas
    aparecen literalmente en los fragmentos se componen en una plantilla fija, y si no (o si el
    JSON no es valido) se muestra el fragmento literal con su cita. El modelo nunca escribe la
    frase final, de modo que no puede alterar el significado ni una forma quechua."""

    def __init__(self, ollama: OllamaGenerador, verificador: VerificadorFormaLiteral | None = None):
        self._ollama = ollama
        self._verificador = verificador or VerificadorFormaLiteral()
        self.aceptadas = 0
        self.descartadas = 0

    def redactar(self, consulta: str, fragmentos: list[FragmentoRecuperado], idioma: Idioma) -> str:
        if not fragmentos:
            raise ValueError("El generador no puede invocarse sin fragmentos de respaldo")
        # GeneradorNoDisponible (modelo caido, extraccion truncada) se propaga: el caso de uso
        # responde con el fragmento literal y el aviso de redaccion.
        try:
            datos = self._ollama.extraer(consulta, fragmentos, idioma)
        except (json.JSONDecodeError, ValueError):
            datos = {}
        verificada = self._verificador.comprobar(
            datos.get("forma"), datos.get("glosa"), [f.texto for f in fragmentos]
        )
        if verificada is not None:
            self.aceptadas += 1
            plantilla = PLANTILLA.get(idioma, PLANTILLA[Idioma.ESPANOL])
            # Se compone con la forma y el lema TAL COMO ESTAN en el fragmento, no con lo que
            # escribio el modelo.
            return plantilla.format(glosa=verificada.glosa, forma=verificada.forma)
        self.descartadas += 1
        log.info("[GENERADOR] extraccion descartada: no figura literalmente en el fragmento")
        primero = fragmentos[0]
        return f"{primero.texto} ({primero.procedencia.citar()})"

    def precalentar(self) -> bool:
        return self._ollama.precalentar()

    def disponible(self) -> bool:
        return self._ollama.disponible()
