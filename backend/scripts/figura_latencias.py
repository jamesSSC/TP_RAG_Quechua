"""B3 · Histograma de latencias (local con Qwen en GPU y local extractivo) a partir de los CSV de
`medir_latencia_energia.py`. Uso: python scripts/figura_latencias.py CARPETA_EVIDENCIAS"""

import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ACENTO, AVISO, TINTA = "#8A5A2B", "#86581A", "#1C1A17"


def leer(ruta):
    with ruta.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f)]


def main(carpeta: Path):
    qwen = leer(carpeta / "latencia_local_qwen_gpu.csv")
    resp = [float(r["total_ms"]) / 1000 for r in qwen if r["abstenida"] == "False"]
    abst = [float(r["total_ms"]) for r in qwen if r["abstenida"] == "True"]
    for poster in (False, True):
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 6) if poster else (11, 4.2))
        a1.hist(resp, bins=30, color="white", edgecolor=ACENTO, linewidth=1.5)
        a1.set_title(f"Respuestas con Qwen3.5 4B en GPU (n = {len(resp)})", color=TINTA)
        a1.set_xlabel("Latencia de extremo a extremo (s)")
        a1.set_ylabel("Consultas")
        a2.hist(abst, bins=15, color="white", edgecolor=AVISO, linewidth=1.5)
        a2.set_title(f"Abstenciones: no invocan el modelo (n = {len(abst)})", color=TINTA)
        a2.set_xlabel("Latencia de extremo a extremo (ms)")
        fig.suptitle("Latencia local, 248 consultas de evaluacion_v2.json", color=TINTA)
        fig.tight_layout()
        fig.savefig(
            carpeta / f"histograma_latencias{'_poster' if poster else ''}.png",
            dpi=300 if poster else 150,
            facecolor="white",
        )
        plt.close(fig)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
