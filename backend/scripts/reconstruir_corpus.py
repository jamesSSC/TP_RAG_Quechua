"""H-02 · Reconstruye `data/fragmentos_v3.jsonl` desde el indice exportado de la app movil.

El corpus procesado no se versiona en este repositorio (ADR-015), de modo que un clon limpio no
podia reproducir las pruebas ni las metricas que dependen de el. El indice que la app movil lleva
en `assets/indice/fragmentos.json` (repositorio quechua-wanka-movil) contiene los mismos 3 605
fragmentos con su documento, pagina, texto y tipo: la conversion es exacta, sin perdida.

Uso:
    python scripts/reconstruir_corpus.py RUTA/assets/indice/fragmentos.json [salida.jsonl]

Comprueba que salen 3 605 fragmentos y, si coincide, informa el sha256 esperado. No inventa ni
corrige ningun texto: copia literal.
"""

import hashlib
import json
import sys
from pathlib import Path

# Prefijo del sha256 del fragmentos_v3.jsonl de referencia con finales de linea LF (la copia
# historica en Windows tiene CRLF: d6200ed9e992e7dc; los datos son identicos).
SHA256_ESPERADO = "6452e7b91347e7df"
TOTAL_ESPERADO = 3605


def reconstruir(origen: Path, destino: Path) -> tuple[int, str]:
    crudos = json.loads(origen.read_text(encoding="utf-8"))
    lineas = [
        json.dumps(
            {
                "id": f["id"],
                "documento": f["d"],
                "pagina": f["p"],
                "texto": f["t"],
                "tipo": "lexicografico" if f["x"] == 1 else "prosa",
            },
            ensure_ascii=False,
        )
        for f in crudos
    ]
    contenido = "\n".join(lineas) + "\n"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(contenido, encoding="utf-8", newline="\n")
    return len(lineas), hashlib.sha256(contenido.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    origen = Path(sys.argv[1])
    destino = Path(sys.argv[2]) if len(sys.argv) > 2 else raiz / "data" / "fragmentos_v3.jsonl"
    total, huella = reconstruir(origen, destino)
    print(f"{total} fragmentos escritos en {destino}")
    print(f"sha256 {huella}")
    if total != TOTAL_ESPERADO:
        sys.exit(f"ERROR: se esperaban {TOTAL_ESPERADO} fragmentos")
    print("coincide con la referencia" if huella.startswith(SHA256_ESPERADO) else
          "AVISO: el contenido no coincide con el fragmentos_v3.jsonl de referencia")
