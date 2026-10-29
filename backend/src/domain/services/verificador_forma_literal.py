import re

SEPARADOR_DE_FORMAS = re.compile(r"\s*(?:,|;|/)\s*")


class VerificadorFormaLiteral:
    """ADR-028: comprueba que la forma y la glosa que propone el modelo aparecen literalmente en
    los fragmentos de respaldo. Nunca corrige ni completa una forma: si algo no esta, lo descarta.

    - La forma quechua se compara EXACTA (mayusculas y signos incluidos): se copia, no se reescribe.
      Si el modelo da varias formas separadas por coma, punto y coma o barra, cada una debe estar.
    - La glosa castellana se compara sin distinguir mayusculas (los lemas del diccionario van en
      mayusculas), pero si distingue acentos.
    Solo usa la biblioteca estandar."""

    def verificar(self, forma, glosa, fragmentos: list[str]) -> bool:
        if not isinstance(forma, str) or not isinstance(glosa, str):
            return False
        forma, glosa = forma.strip(), glosa.strip()
        if not forma or not glosa or not fragmentos:
            return False
        texto = "\n".join(fragmentos)
        formas = [f for f in SEPARADOR_DE_FORMAS.split(forma) if f]
        if not formas or any(f not in texto for f in formas):
            return False
        return glosa.lower() in texto.lower()
