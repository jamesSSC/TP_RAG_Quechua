"""Llena la sección 6 (Resultados) del acta en Word de la prueba con usuarios finales (B4).

Toma el CSV de la prueba, con el formato de `resultados_plantilla.csv` y una fila por participante,
y escribe en una COPIA del acta:
- tabla 6.1: por tarea, cuántos lo lograron sin ayuda (1), con ayuda (0,5) o no (0), la tasa de
  éxito (suma de puntajes / n × 100, como dice el acta) y el tiempo mediano;
- tabla 6.2: el puntaje SUS de cada participante (P01 a P06), la media y el mínimo y máximo.

No toca nada más: los nombres, las firmas, la retroalimentación, los acuerdos y las fotos los llena
el equipo a mano. Los cálculos son los mismos de `analizar_resultados.py`.

Uso:
    python llenar_acta.py resultados.csv Acta_Prueba_Usuarios_Finales.docx Acta_llena.docx

Requiere `python-docx` (solo para este script; no es una dependencia del backend).
"""

import csv
import statistics
import sys
from pathlib import Path

import docx

sys.path.insert(0, str(Path(__file__).parent))
from analizar_resultados import TAREAS, numero, sus  # noqa: E402

TABLA_EXITO = 4  # «6.1 Éxito y tiempo por tarea»
TABLA_SUS = 5  # «6.2 Usabilidad percibida (SUS)»


def _coma(valor: float, decimales: int = 1) -> str:
    texto = f"{valor:.{decimales}f}".replace(".", ",")
    return texto.removesuffix(",0") if decimales == 1 else texto


def _escribir(celda, texto: str) -> None:
    parrafo = celda.paragraphs[0]
    for run in parrafo.runs:
        run.text = ""
    if parrafo.runs:
        parrafo.runs[0].text = texto
    else:
        parrafo.add_run(texto)


def resumen_por_tarea(filas: list[dict]) -> dict[str, dict]:
    resumen = {}
    todos_puntajes: list[float] = []
    todos_tiempos: list[float] = []
    for t in TAREAS:
        puntajes = [p for p in (numero(f[f"{t}_exito"]) for f in filas) if p is not None]
        tiempos = [s for s in (numero(f[f"{t}_seg"]) for f in filas) if s is not None]
        todos_puntajes += puntajes
        todos_tiempos += tiempos
        resumen[t] = _fila(puntajes, tiempos)
    resumen["total"] = _fila(todos_puntajes, todos_tiempos)
    return resumen


def _fila(puntajes: list[float], tiempos: list[float]) -> dict:
    return {
        "sin_ayuda": sum(1 for p in puntajes if p == 1),
        "con_ayuda": sum(1 for p in puntajes if p == 0.5),
        "no_logrado": sum(1 for p in puntajes if p == 0),
        "tasa": 100 * sum(puntajes) / len(puntajes) if puntajes else None,
        "mediana": statistics.median(tiempos) if tiempos else None,
    }


def llenar(filas: list[dict], plantilla: Path, salida: Path) -> None:
    documento = docx.Document(plantilla)
    exito = documento.tables[TABLA_EXITO]
    tabla_sus = documento.tables[TABLA_SUS]
    if exito.rows[0].cells[0].text.strip() != "Tarea" or tabla_sus.rows[0].cells[0].text != "P01":
        raise SystemExit("El acta no tiene la estructura esperada: no se escribió nada.")

    resumen = resumen_por_tarea(filas)
    for fila in exito.rows[1:]:
        clave = fila.cells[0].text.strip().lower()
        datos = resumen.get(clave)
        if datos is None:
            continue
        valores = [
            str(datos["sin_ayuda"]),
            str(datos["con_ayuda"]),
            str(datos["no_logrado"]),
            "—" if datos["tasa"] is None else f"{_coma(datos['tasa'])} %",
            "—" if datos["mediana"] is None else _coma(datos["mediana"]),
        ]
        for celda, valor in zip(fila.cells[1:], valores, strict=True):
            _escribir(celda, valor)

    puntajes = {f["participante"].strip(): sus(f) for f in filas}
    cabecera = [c.text.strip() for c in tabla_sus.rows[0].cells]
    for indice, codigo in enumerate(cabecera):
        celda = tabla_sus.rows[1].cells[indice]
        if codigo in puntajes:
            _escribir(celda, _coma(puntajes[codigo]))
        elif codigo == "Media" and puntajes:
            _escribir(celda, _coma(statistics.mean(puntajes.values())))
        elif codigo.startswith("Mín") and puntajes:
            _escribir(
                celda, f"{_coma(min(puntajes.values()))}–{_coma(max(puntajes.values()))}"
            )
    documento.save(salida)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    with open(sys.argv[1], encoding="utf-8", newline="") as f:
        datos = list(csv.DictReader(f))
    if not datos:
        raise SystemExit("El CSV no tiene participantes.")
    llenar(datos, Path(sys.argv[2]), Path(sys.argv[3]))
    print(f"Acta con resultados: {sys.argv[3]}")
