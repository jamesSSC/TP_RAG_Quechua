"""REF-08 (ADR-041): tolerancia a erratas en la consulta en español, nunca en formas quechuas.

El sistema NO corrige por su cuenta: cuando se abstiene, propone «¿quiso escribir…?» con lemas
castellanos del diccionario que están a una o dos letras del término consultado, y quien consulta
decide. Así la salvaguarda no cambia: τ, RN-06, la respuesta y la abstención son las mismas.

Por qué nunca toca el quechua:
- Las sugerencias salen solo del lemario, es decir de las palabras CASTELLANAS que encabezan las
  entradas del diccionario («ZORRO: Atuq.»), nunca del cuerpo con las formas quechuas.
- No se sugiere nada si el término ya figura en el corpus (es una palabra conocida, quizá
  quechua) ni si tiene ortografía quechua: k, w, o q sin u (en castellano la q va siempre con u).
"""

import re

MAXIMO_SUGERENCIAS = 3
LONGITUD_MINIMA = 4
_SOLO_LETRAS = re.compile(r"^[a-z]+$")
_Q_SIN_U = re.compile(r"q(?!u)")


def parece_quechua(termino: str) -> bool:
    return "k" in termino or "w" in termino or bool(_Q_SIN_U.search(termino))


def distancia_maxima(termino: str) -> int:
    return 1 if len(termino) <= 5 else 2


def distancia(a: str, b: str, tope: int) -> int:
    """Distancia de edición con transposiciones (Damerau, alineamiento óptimo). Devuelve
    tope + 1 en cuanto se sabe que lo supera."""
    if abs(len(a) - len(b)) > tope:
        return tope + 1
    previa2: list[int] | None = None
    previa = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        actual = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            costo = 0 if ca == cb else 1
            actual[j] = min(previa[j] + 1, actual[j - 1] + 1, previa[j - 1] + costo)
            if previa2 is not None and i > 1 and j > 1 and ca == b[j - 2] and a[i - 2] == cb:
                actual[j] = min(actual[j], previa2[j - 2] + 1)
        if min(actual) > tope:
            return tope + 1
        previa2, previa = previa, actual
    return previa[-1]


def sugerir(termino: str, lemas: dict[str, int], palabras_del_corpus) -> list[str]:
    """Lemas castellanos parecidos a `termino` (ya normalizado), del más cercano y frecuente al
    menos. `lemas` va de lema a número de entradas; `palabras_del_corpus` es el vocabulario."""
    if (
        len(termino) < LONGITUD_MINIMA
        or not _SOLO_LETRAS.match(termino)
        or termino in lemas
        or termino in palabras_del_corpus
        or parece_quechua(termino)
    ):
        return []
    tope = distancia_maxima(termino)
    candidatos = []
    for lema, frecuencia in lemas.items():
        if " " in lema:
            continue
        d = distancia(termino, lema, tope)
        if d <= tope:
            # Desempate: misma primera letra (las erratas suelen estar en medio de la
            # palabra), luego la mas frecuente en el diccionario.
            candidatos.append((d, lema[0] != termino[0], -frecuencia, lema))
    return [c[-1] for c in sorted(candidatos)[:MAXIMO_SUGERENCIAS]]
