import re
from dataclasses import dataclass

# Lema de una entrada lexicografica: la parte en mayusculas que precede a los dos puntos,
# como en "PERRO: Allqu, ashuti." Un mismo fragmento puede contener mas de una entrada.
# Es la unica definicion: el indice de recuperacion y el verificador de formas la comparten.
PATRON_LEMA = re.compile(r"([A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s\-]*?)\s*:")


@dataclass(frozen=True)
class EntradaLexica:
    lema: str
    cuerpo: str


def segmentar_entradas(texto: str) -> list[EntradaLexica]:
    """Divide un fragmento lexicografico en sus entradas: cada lema y lo que le sigue hasta el
    lema siguiente. Un texto sin lema (prosa) no tiene entradas."""
    marcas = list(PATRON_LEMA.finditer(texto))
    entradas = []
    for i, marca in enumerate(marcas):
        fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        entradas.append(EntradaLexica(lema=marca.group(1).strip(), cuerpo=texto[marca.end() : fin]))
    return entradas
