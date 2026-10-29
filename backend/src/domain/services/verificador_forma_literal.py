import re
from dataclasses import dataclass

from domain.services.entradas_lexicas import EntradaLexica, segmentar_entradas

SEPARADOR_DE_FORMAS = re.compile(r"\s*(?:,|;|/)\s*")
# Un token es una secuencia sin espacios ni signos de puntuacion; los apostrofos y guiones de las
# formas quechuas forman parte del token.
SEPARADORES_DE_TOKEN = re.compile(r"[\s,;:.()\[\]¿?¡!\"«»]+")
# Signos que separan una forma de otra dentro del cuerpo de una entrada: una forma no los cruza.
SEPARADORES_DE_FORMA = re.compile(r"[,;.:\n]+")
# Un cuerpo con frases de ejemplo no permite distinguir formas de oraciones: se descarta.
SIGNOS_DE_FRASE = "¿?¡!"


@dataclass(frozen=True)
class FormaVerificada:
    """Lo que SI figura en el fragmento: la forma tal como esta escrita y el lema de su entrada."""

    forma: str
    glosa: str


def _tokens(texto: str) -> list[str]:
    return [t for t in SEPARADORES_DE_TOKEN.split(texto) if t]


def _segmentos_de_formas(cuerpo: str) -> list[list[str]] | None:
    """Formas candidatas de una entrada: el cuerpo sin los segmentos entre parentesis (glosas y
    aclaraciones en castellano), partido por comas, puntos y punto y coma. Devuelve None si la
    estructura no es fiable (parentesis sin cerrar o frases de ejemplo): nunca se adivina."""
    if any(signo in cuerpo for signo in SIGNOS_DE_FRASE):
        return None
    fuera, profundidad = [], 0
    for caracter in cuerpo:
        if caracter == "(":
            profundidad += 1
            fuera.append(";")  # el parentesis tambien corta una forma
        elif caracter == ")":
            profundidad -= 1
            if profundidad < 0:
                return None
            fuera.append(";")
        elif profundidad == 0:
            fuera.append(caracter)
    if profundidad != 0:
        return None
    segmentos = [_tokens(s) for s in SEPARADORES_DE_FORMA.split("".join(fuera))]
    return [s for s in segmentos if s]


def _en_un_segmento(segmentos: list[list[str]], buscada: list[str]) -> list[str] | None:
    """Secuencia completa de tokens, contigua DENTRO de un solo segmento (solo mayusculas
    normalizadas). Nunca una subcadena de un token ni una secuencia que salte puntuacion."""
    n = len(buscada)
    clave = [t.lower() for t in buscada]
    for segmento in segmentos:
        for i in range(len(segmento) - n + 1):
            if [t.lower() for t in segmento[i : i + n]] == clave:
                return segmento[i : i + n]
    return None


class VerificadorFormaLiteral:
    """ADR-028: comprueba que la forma y la glosa que propone el modelo son la correspondencia
    que registra UNA entrada del diccionario. Nunca corrige ni completa una forma: si algo no
    cuadra, lo descarta y quien llama muestra el fragmento literal.

    - La glosa debe ser el lema castellano de una entrada (sin distinguir mayusculas; si acentos).
    - Cada forma debe ser un token completo o una secuencia contigua de tokens de UN segmento del
      cuerpo de esa misma entrada: no cruza comas, puntos, punto y coma ni parentesis, y el texto
      entre parentesis (castellano) no cuenta como forma.
    - La forma no puede ser el propio lema castellano de la entrada.
    - Si el cuerpo trae parentesis sin cerrar o frases de ejemplo, no se distingue y se descarta.
    - Solo se normalizan mayusculas y espacios; las letras quechuas se comparan tal cual.
    Solo usa la biblioteca estandar."""

    def comprobar(self, forma, glosa, fragmentos: list[str]) -> FormaVerificada | None:
        if not isinstance(forma, str) or not isinstance(glosa, str):
            return None
        formas = [_tokens(f) for f in SEPARADOR_DE_FORMAS.split(forma.strip()) if f.strip()]
        glosa_tokens = _tokens(glosa)
        if not formas or not glosa_tokens or any(not f for f in formas):
            return None
        for texto in fragmentos:
            for entrada in segmentar_entradas(texto):
                literal = self._forma_literal(entrada, formas, glosa_tokens)
                if literal is not None:
                    return FormaVerificada(forma=", ".join(literal), glosa=entrada.lema.lower())
        return None

    def verificar(self, forma, glosa, fragmentos: list[str]) -> bool:
        return self.comprobar(forma, glosa, fragmentos) is not None

    @staticmethod
    def _forma_literal(
        entrada: EntradaLexica, formas: list[list[str]], glosa_tokens: list[str]
    ) -> list[str] | None:
        lema = [t.lower() for t in _tokens(entrada.lema)]
        if [t.lower() for t in glosa_tokens] != lema:
            return None
        segmentos = _segmentos_de_formas(entrada.cuerpo)
        if segmentos is None:
            return None
        encontradas = []
        for forma in formas:
            if [t.lower() for t in forma] == lema:
                return None  # la forma es el propio lema castellano
            coincidencia = _en_un_segmento(segmentos, forma)
            if coincidencia is None:
                return None
            encontradas.append(" ".join(coincidencia))
        return encontradas
