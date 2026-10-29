import re
from dataclasses import dataclass

from domain.services.entradas_lexicas import EntradaLexica, segmentar_entradas

SEPARADOR_DE_FORMAS = re.compile(r"\s*(?:,|;|/)\s*")
# Un token es una secuencia sin espacios ni signos de puntuacion; los apostrofos y guiones de las
# formas quechuas forman parte del token.
SEPARADORES_DE_TOKEN = re.compile(r"[\s,;:.()\[\]¿?¡!\"«»]+")


@dataclass(frozen=True)
class FormaVerificada:
    """Lo que SI figura en el fragmento: la forma tal como esta escrita y el lema de su entrada."""

    forma: str
    glosa: str


def _tokens(texto: str) -> list[str]:
    return [t for t in SEPARADORES_DE_TOKEN.split(texto) if t]


def _contiene_secuencia(tokens: list[str], buscada: list[str]) -> list[str] | None:
    """Devuelve la secuencia completa de tokens del cuerpo que coincide (solo mayusculas
    normalizadas), o None. Limites de palabra: nunca una subcadena de un token."""
    n = len(buscada)
    clave = [t.lower() for t in buscada]
    for i in range(len(tokens) - n + 1):
        if [t.lower() for t in tokens[i : i + n]] == clave:
            return tokens[i : i + n]
    return None


class VerificadorFormaLiteral:
    """ADR-028: comprueba que la forma y la glosa que propone el modelo son la correspondencia
    que registra UNA entrada del diccionario. Nunca corrige ni completa una forma: si algo no
    cuadra, lo descarta y quien llama muestra el fragmento literal.

    - La glosa debe ser el lema castellano de una entrada (sin distinguir mayusculas; si acentos).
    - Cada forma debe ser un token completo o una secuencia completa de tokens del cuerpo de ESA
      misma entrada: nada de subcadenas ("Atu" no vale por "Atuq") ni formas de otra entrada.
    - La forma no puede ser el propio lema castellano de la entrada.
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
        cuerpo = _tokens(entrada.cuerpo)
        encontradas = []
        for forma in formas:
            if [t.lower() for t in forma] == lema:
                return None  # la forma es el propio lema castellano
            coincidencia = _contiene_secuencia(cuerpo, forma)
            if coincidencia is None:
                return None
            encontradas.append(" ".join(coincidencia))
        return encontradas
