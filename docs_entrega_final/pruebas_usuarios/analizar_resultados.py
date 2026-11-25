"""Analiza los resultados de la prueba con usuarios (B4, indicador 9).

Lee el CSV con el formato de `resultados_plantilla.csv` (una fila por participante) y calcula:
- el puntaje SUS de cada participante y su media, desviación y rango;
- el éxito por tarea (1 = sin ayuda, 0,5 = con ayuda, 0 = no) y el global;
- la mediana y el rango del tiempo por tarea y los errores totales.

Uso:  python analizar_resultados.py resultados.csv
Solo usa la biblioteca estándar. No contiene datos: los datos los aporta la prueba real.
"""

import csv
import statistics
import sys

TAREAS = ["t1", "t2", "t3", "t4", "t5", "t6", "t7"]
NOMBRES = {
    "t1": "T1 forma y página (HU-03/07)",
    "t2": "T2 abstención (HU-06)",
    "t3": "T3 consulta en inglés (HU-05)",
    "t4": "T4 predicción ML (HU-08.1)",
    "t5": "T5 pasajes (HU-04)",
    "t6": "T6 en línea y modo avión (HU-10.1)",
    "t7": "T7 letra grande (HU-11)",
}


def sus(fila: dict) -> float:
    total = 0
    for i in range(1, 11):
        r = int(fila[f"sus{i}"])
        if not 1 <= r <= 5:
            raise ValueError(f"{fila['participante']}: sus{i} fuera de 1..5")
        total += (r - 1) if i % 2 else (5 - r)
    return total * 2.5


def numero(valor: str) -> float | None:
    valor = (valor or "").strip().replace(",", ".")
    return float(valor) if valor else None


def analizar(filas: list[dict]) -> str:
    if not filas:
        return "Sin datos: el CSV no tiene participantes."
    lineas = [f"Participantes: {len(filas)}", ""]

    puntajes = [sus(f) for f in filas]
    lineas.append("SUS por participante: " + ", ".join(
        f"{f['participante']} {p:.1f}" for f, p in zip(filas, puntajes, strict=True)))
    desv = statistics.stdev(puntajes) if len(puntajes) > 1 else 0.0
    lineas.append(f"SUS media {statistics.mean(puntajes):.1f} · desviación {desv:.1f} · "
                  f"rango {min(puntajes):.1f}–{max(puntajes):.1f} (referencia: 68)")
    lineas.append("")
    lineas.append(f"{'Tarea':40s} {'éxito':>7s} {'t mediana':>10s} {'t rango':>12s} {'errores':>8s}")

    exitos_globales = []
    for t in TAREAS:
        exitos = [numero(f[f"{t}_exito"]) for f in filas]
        exitos = [e for e in exitos if e is not None]
        tiempos = [numero(f[f"{t}_seg"]) for f in filas]
        tiempos = [s for s in tiempos if s is not None]
        errores = sum(int(numero(f[f"{t}_errores"]) or 0) for f in filas)
        exitos_globales += exitos
        exito = f"{100 * statistics.mean(exitos):.0f} %" if exitos else "—"
        med = f"{statistics.median(tiempos):.0f} s" if tiempos else "—"
        rango = f"{min(tiempos):.0f}–{max(tiempos):.0f} s" if tiempos else "—"
        lineas.append(f"{NOMBRES[t]:40s} {exito:>7s} {med:>10s} {rango:>12s} {errores:>8d}")
    if exitos_globales:
        lineas += ["", f"Éxito global: {100 * statistics.mean(exitos_globales):.0f} %"]
    return "\n".join(lineas)


def con_datos(filas: list[dict]) -> list[dict]:
    """Descarta las filas preparadas de antemano (P05, P06…) que quedaron sin llenar."""
    return [f for f in filas if any((f.get(f"sus{i}") or "").strip() for i in range(1, 11))]


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8", newline="") as f:
        print(analizar(con_datos(list(csv.DictReader(f)))))
