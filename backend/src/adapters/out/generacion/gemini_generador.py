"""Extraccion con la API de Gemini (nube, ADR-032).

Sustituye a Ollama solo en la nube, donde no hay GPU. Hace lo mismo que
`OllamaGenerador.extraer`: devuelve `{forma, glosa}` copiadas de los fragmentos, y quien lo
envuelve (GeneradorExtractivo, ADR-028) las verifica contra el fragmento y compone la plantilla.
Gemini nunca escribe la frase final, no traduce la consulta (eso sigue en la tabla) y no se
llama en una abstencion: el caso de uso decide antes.

Degradacion: sin clave, con error, con cuota agotada (429) o pasados `timeout` segundos se
lanza GeneradorNoDisponible y el caso de uso responde con el fragmento literal citado.

La clave nunca se registra: ni en los logs, ni en la base, ni en las respuestas. Los mensajes
de error solo llevan el codigo HTTP o el tipo de excepcion.
"""

import json
import logging
from contextvars import ContextVar

import httpx

from adapters.out.generacion.ollama_generador import LIMITE_TOKENS
from application.ports.out.generador_texto_port import GeneradorNoDisponible, GeneradorTextoPort
from domain.entities.fragmento import FragmentoRecuperado
from domain.value_objects.idioma import Idioma

log = logging.getLogger("rag.generador")

URL_API = "https://generativelanguage.googleapis.com/v1beta"
# Tokens extra para el razonamiento interno de los modelos Gemini 3.x (nivel "low").
MARGEN_RAZONAMIENTO = 1024

# BYOK: clave que el usuario aporta en la cabecera X-Gemini-Key de UNA peticion. La fija el
# middleware de infrastructure/main.py y caduca con la peticion.
clave_de_la_peticion: ContextVar[str | None] = ContextVar("clave_gemini", default=None)

INSTRUCCION = (
    "Del fragmento del diccionario extrae la correspondencia que responde a la consulta.\n"
    'Devuelve SOLO un JSON con dos campos: {"forma": ..., "glosa": ...}.\n'
    "- forma: la(s) forma(s) en quechua wanka COPIADA(S) letra por letra del fragmento.\n"
    "- glosa: la palabra castellana del fragmento a la que corresponde.\n"
    "No traduzcas, no corrijas, no completes ni agregues nada ajeno al fragmento.\n\n"
)


class GeminiGenerador(GeneradorTextoPort):
    nombre = "gemini"

    def __init__(
        self,
        clave: str = "",
        modelo: str = "gemini-3.5-flash-lite",
        temperatura: float = 0.1,
        timeout: float = 15.0,
        cliente: httpx.Client | None = None,
    ):
        self._clave = clave
        self._modelo = modelo
        self._temperatura = temperatura
        self._timeout = timeout
        self._cliente = cliente
        self.errores_429 = 0

    @property
    def modelo(self) -> str:
        return self._modelo

    def _clave_vigente(self) -> str | None:
        return clave_de_la_peticion.get() or self._clave or None

    def redactar(self, consulta: str, fragmentos: list[FragmentoRecuperado], idioma: Idioma) -> str:
        # Solo se usa envuelto en GeneradorExtractivo: Gemini no redacta texto libre.
        raise GeneradorNoDisponible("Gemini solo se usa para la extraccion verificada (ADR-028)")

    def extraer(self, consulta: str, fragmentos: list[FragmentoRecuperado], idioma: Idioma) -> dict:
        if not fragmentos:
            raise ValueError("El generador no puede invocarse sin fragmentos de respaldo")
        clave = self._clave_vigente()
        if not clave:
            raise GeneradorNoDisponible("sin clave de Gemini")
        contexto = "\n\n".join(f"[Fragmento {i}] {f.texto}" for i, f in enumerate(fragmentos, 1))
        prompt = f"{INSTRUCCION}Fragmentos:\n{contexto}\n\nConsulta: {consulta}\n\nJSON:"
        configuracion = {
            "temperature": self._temperatura,
            "maxOutputTokens": LIMITE_TOKENS,
            "responseMimeType": "application/json",
        }
        # El razonamiento interno consume el tope de salida; para copiar dos campos sobra. La
        # forma de limitarlo cambio entre generaciones de modelos.
        if self._modelo.startswith("gemini-2.5"):
            configuracion["thinkingConfig"] = {"thinkingBudget": 0}
        elif self._modelo.startswith("gemini-3"):
            # Gemini 3.x no admite "minimal" en todos los modelos (3.8 Flash devuelve error):
            # "low" es el nivel minimo comun. Sus tokens de razonamiento cuentan contra
            # maxOutputTokens, de modo que se suma un margen; el JSON visible sigue acotado y un
            # MAX_TOKENS se trata igual que en Ollama (fragmento literal).
            configuracion["thinkingConfig"] = {"thinkingLevel": "low"}
            configuracion["maxOutputTokens"] = LIMITE_TOKENS + MARGEN_RAZONAMIENTO
        cuerpo = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": configuracion,
        }
        try:
            datos = self._llamar(cuerpo, clave)
        except GeneradorNoDisponible as exc:
            if "HTTP 400" not in str(exc) or "thinkingConfig" not in configuracion:
                raise
            # El modelo no admite esa configuracion de razonamiento: un reintento sin ella.
            del configuracion["thinkingConfig"]
            datos = self._llamar(cuerpo, clave)
        try:
            candidato = datos["candidates"][0]
            if candidato.get("finishReason") == "MAX_TOKENS":
                raise GeneradorNoDisponible("extraccion truncada (MAX_TOKENS)")
            texto = "".join(p.get("text", "") for p in candidato["content"]["parts"])
        except (KeyError, IndexError, TypeError) as exc:
            raise GeneradorNoDisponible(f"respuesta inesperada ({type(exc).__name__})") from exc
        extraido = json.loads(texto)
        if not isinstance(extraido, dict):
            raise ValueError("la extraccion no es un objeto JSON")
        return extraido

    def _llamar(self, cuerpo: dict, clave: str) -> dict:
        url = f"{URL_API}/models/{self._modelo}:generateContent"
        # La clave va en cabecera y no en la URL: asi no aparece en ningun registro de acceso.
        cabeceras = {"x-goog-api-key": clave, "Content-Type": "application/json"}
        try:
            if self._cliente is not None:
                respuesta = self._cliente.post(
                    url, json=cuerpo, headers=cabeceras, timeout=self._timeout
                )
            else:
                respuesta = httpx.post(url, json=cuerpo, headers=cabeceras, timeout=self._timeout)
        except httpx.TimeoutException as exc:
            raise GeneradorNoDisponible(f"tiempo agotado ({self._timeout:.0f} s)") from exc
        except httpx.HTTPError as exc:
            raise GeneradorNoDisponible(f"error de red ({type(exc).__name__})") from exc
        if respuesta.status_code == 429:
            self.errores_429 += 1
            raise GeneradorNoDisponible("cuota agotada (429)")
        if respuesta.status_code >= 400:
            raise GeneradorNoDisponible(f"error HTTP {respuesta.status_code}")
        try:
            return respuesta.json()
        except ValueError as exc:
            raise GeneradorNoDisponible("respuesta no es JSON") from exc

    def precalentar(self) -> bool:
        return True

    def disponible(self) -> bool:
        # Sin llamada de red: /api/estado no debe gastar cuota.
        return bool(self._clave_vigente())
