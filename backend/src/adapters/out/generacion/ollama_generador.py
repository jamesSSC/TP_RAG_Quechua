import json
import logging

import httpx

from application.ports.out.generador_texto_port import GeneradorNoDisponible, GeneradorTextoPort
from domain.entities.fragmento import FragmentoRecuperado
from domain.value_objects.idioma import Idioma

log = logging.getLogger("rag.generador")

# Tope de tokens de la redaccion y de su reintento cuando Ollama informa done_reason == "length".
LIMITE_TOKENS = 300
LIMITE_TOKENS_REINTENTO = 900

INSTRUCCION = {
    Idioma.ESPANOL: (
        "Eres un asistente de consulta documental sobre el quechua wanka de Junin.\n"
        "Reglas estrictas:\n"
        "1. Responde UNICAMENTE con la informacion contenida en los fragmentos entregados.\n"
        "2. No inventes, no traduzcas y no completes ninguna forma en quechua wanka que no "
        "aparezca literalmente en los fragmentos.\n"
        "3. Copia la forma quechua exactamente como figura en el fragmento.\n"
        "4. NO expliques el significado de una palabra quechua ni de ninguna de sus partes "
        "si el fragmento no lo dice de forma expresa. No descompongas terminos, no analices "
        "morfemas y no deduzcas equivalencias por parecido con el castellano.\n"
        "5. Limitate a exponer la correspondencia tal como el fragmento la registra. Si el "
        "fragmento ofrece varias formas, enumeralas sin atribuir a cada una un matiz que el "
        "fragmento no declare.\n"
        "6. Si los fragmentos no contienen la respuesta, dilo de forma explicita.\n"
        "7. Responde en espanol, en un maximo de dos frases, sin encabezados ni listas y "
        "sin mencionar el numero de fragmento."
    ),
    Idioma.INGLES: (
        "You are a documentary consultation assistant for Wanka Quechua of Junin.\n"
        "Strict rules:\n"
        "1. Answer ONLY with information contained in the provided fragments.\n"
        "2. Never invent, translate or complete any Wanka Quechua form that does not appear "
        "literally in the fragments.\n"
        "3. Copy the Quechua form exactly as it appears in the fragment.\n"
        "4. Do NOT explain the meaning of a Quechua word or of any of its parts unless the "
        "fragment states it explicitly. Do not break terms apart, do not analyse morphemes "
        "and do not infer meanings from resemblance to Spanish or English words.\n"
        "5. Simply report the correspondence as the fragment records it. If the fragment "
        "offers several forms, list them without assigning each one a nuance the fragment "
        "does not state.\n"
        "6. If the fragments do not contain the answer, say so explicitly.\n"
        "7. Answer in English in at most two sentences, with no headings or lists and "
        "without mentioning fragment numbers. Keep the Quechua term untranslated."
    ),
}


class OllamaGenerador(GeneradorTextoPort):
    """Adaptador del puerto de generacion contra el servicio HTTP local de Ollama.

    Cumple la integracion con un servicio externo exigida por la consigna sin contradecir
    RF-12 y RNF-06: el servicio es externo al proceso pero interno al equipo, de modo que
    ninguna consulta ni fragmento del corpus sale del dispositivo."""

    def __init__(
        self,
        url_base: str = "http://localhost:11434",
        modelo: str = "qwen3.5:4b",
        temperatura: float = 0.1,
        timeout: float = 120.0,
        permanencia: str = "30m",
    ):
        self._url_base = url_base.rstrip("/")
        self._modelo = modelo
        self._temperatura = temperatura
        self._timeout = timeout
        self._permanencia = permanencia

    def precalentar(self) -> bool:
        """Carga el modelo en memoria antes de la primera consulta real.

        Sin esto la primera respuesta tarda unos 47 segundos frente a los 3,3 habituales,
        porque incluye el traslado de los pesos a la memoria de video. RNF-01 fija el limite
        en 8 segundos, de modo que la precarga no es una optimizacion sino la condicion para
        cumplirlo en la consulta inicial."""
        try:
            respuesta = httpx.post(
                f"{self._url_base}/api/generate",
                json={
                    "model": self._modelo,
                    "prompt": "ok",
                    "stream": False,
                    "think": False,
                    "keep_alive": self._permanencia,
                    "options": {"num_predict": 1},
                },
                timeout=self._timeout,
            )
            respuesta.raise_for_status()
            return True
        except httpx.HTTPError:
            return False

    def redactar(
        self,
        consulta: str,
        fragmentos: list[FragmentoRecuperado],
        idioma: Idioma,
    ) -> str:
        if not fragmentos:
            raise ValueError(
                "El generador no puede invocarse sin fragmentos: la decision de abstencion "
                "se toma antes, en EvaluadorConfianza"
            )

        contexto = "\n\n".join(
            f"[Fragmento {i}] {f.texto}\n(Fuente: {f.procedencia.citar()})"
            for i, f in enumerate(fragmentos, start=1)
        )
        instruccion = INSTRUCCION.get(idioma, INSTRUCCION[Idioma.ESPANOL])
        prompt = f"{instruccion}\n\nFragmentos:\n{contexto}\n\nConsulta: {consulta}\n\nRespuesta:"

        texto, razon = self._generar(prompt, LIMITE_TOKENS)
        if razon == "length":
            # La respuesta topo con el limite de tokens: nunca se entrega recortada. Se reintenta
            # una vez con mas margen y, si vuelve a toparse, se descarta (el caso de uso muestra
            # entonces el fragmento literal con su aviso).
            log.warning("[GENERADOR] respuesta truncada (done_reason=length); se reintenta")
            texto, razon = self._generar(prompt, LIMITE_TOKENS_REINTENTO)
            if razon == "length":
                raise GeneradorNoDisponible("respuesta truncada (done_reason=length)")
        return texto

    def extraer(self, consulta: str, fragmentos: list[FragmentoRecuperado], idioma: Idioma) -> dict:
        """Extraccion restringida (ADR-028): el modelo devuelve solo JSON con `forma` y `glosa`,
        copiadas de los fragmentos. No redacta nada; lo verifica quien lo llama."""
        contexto = "\n\n".join(f"[Fragmento {i}] {f.texto}" for i, f in enumerate(fragmentos, 1))
        prompt = (
            "Del fragmento del diccionario extrae la correspondencia que responde a la consulta.\n"
            'Devuelve SOLO un JSON con dos campos: {"forma": ..., "glosa": ...}.\n'
            "- forma: la(s) forma(s) en quechua wanka COPIADA(S) letra por letra del fragmento.\n"
            "- glosa: la palabra castellana del fragmento a la que corresponde.\n"
            "No traduzcas, no corrijas, no completes y no agregues nada que no este en el fragmento.\n\n"
            f"Fragmentos:\n{contexto}\n\nConsulta: {consulta}\n\nJSON:"
        )
        texto, razon = self._generar(prompt, LIMITE_TOKENS, formato="json")
        if razon == "length":
            raise GeneradorNoDisponible("extraccion truncada (done_reason=length)")
        datos = json.loads(texto)
        if not isinstance(datos, dict):
            raise ValueError("la extraccion no es un objeto JSON")
        return datos

    def _generar(self, prompt: str, num_predict: int, formato: str | None = None):
        """Llama a Ollama y devuelve (texto, done_reason)."""
        cuerpo = {
            "model": self._modelo,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "keep_alive": self._permanencia,
            "options": {"temperature": self._temperatura, "num_predict": num_predict},
        }
        if formato:
            cuerpo["format"] = formato
        try:
            respuesta = httpx.post(
                f"{self._url_base}/api/generate", json=cuerpo, timeout=self._timeout
            )
            respuesta.raise_for_status()
            datos = respuesta.json()
            return datos["response"].strip(), datos.get("done_reason")
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            # Incluye tiempo agotado (httpx.TimeoutException) y respuesta malformada.
            raise GeneradorNoDisponible(f"{type(exc).__name__}: {exc}") from exc

    def disponible(self) -> bool:
        try:
            r = httpx.get(f"{self._url_base}/api/tags", timeout=5.0)
            r.raise_for_status()
            modelos = {m["name"] for m in r.json().get("models", [])}
            return any(m.startswith(self._modelo.split(":")[0]) for m in modelos)
        except (httpx.HTTPError, KeyError):
            return False
