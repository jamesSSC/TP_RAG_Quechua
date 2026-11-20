"""B12 · Figuras del póster A0 que no salen de las métricas: diagrama de despliegue y códigos QR.

Estilo del póster (`ESPEC_POSTER_A0.md`): fondo blanco, contornos en lugar de rellenos y la paleta de
la web. Salida a 300 ppp, con más de 3 000 px de ancho.

Uso (desde la raíz del repositorio, con el entorno del backend):
    backend/.venv/Scripts/python docs_entrega_final/poster/generar_figuras_poster.py
Requiere matplotlib y qrcode[pil] (solo para generar estas figuras).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import qrcode  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

AQUI = Path(__file__).resolve().parent / "figuras"
ACENTO, AVISO, TINTA, SUAVE, BORDE, CREMA = (
    "#8A5A2B", "#86581A", "#1C1A17", "#5D574F", "#DED5C7", "#FAF7F2",
)


def caja(ax, x, y, w, h, titulo, lineas, color=ACENTO, crema=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=CREMA if crema else "white", ec=color, lw=2.6))
    ax.text(x + w / 2, y + h - 0.32, titulo, ha="center", va="top", fontsize=17,
            fontweight="bold", color=TINTA)
    for i, linea in enumerate(lineas):
        ax.text(x + w / 2, y + h - 0.95 - i * 0.42, linea, ha="center", va="top", fontsize=12.5,
                color=SUAVE)


def flecha(ax, a, b, texto=None, estilo="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=estilo, mutation_scale=22, lw=2,
                                 color=TINTA, linestyle=ls))
    if texto:
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 0.18, texto, ha="center", fontsize=11.5,
                color=TINTA, bbox={"fc": "white", "ec": "none", "pad": 1})


def despliegue():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.set_title("Arquitectura tecnológica · vista de despliegue", fontsize=22, color=TINTA,
                 fontweight="bold", pad=12)

    caja(ax, 0.3, 5.6, 3.2, 2.6, "Navegador", ["Web React 19 + Vite", "(cualquier equipo)"])
    caja(ax, 0.3, 1.0, 3.2, 3.4, "Teléfono Android", ["App Flutter 3.44", "AsistenteConmutado",
                                                       "corpus local 12 MB", "SQLite (historial)"],
         crema=True)
    caja(ax, 5.2, 5.6, 3.6, 2.6, "Render · quechua-web", ["Sitio estático", "CSP, HSTS, nosniff"])
    caja(ax, 5.2, 1.6, 3.6, 3.2, "Render · quechua-api", ["FastAPI (hexagonal)", "índice E4 · τ = 0,48",
                                                          "2 predictores sklearn", "token, límite, HSTS"])
    caja(ax, 10.8, 5.6, 4.8, 2.6, "Neon PostgreSQL", ["AWS us-east-1", "corpus · consultas · 7 rutinas"])
    caja(ax, 10.8, 1.6, 4.8, 3.0, "Google Gemini", ["3.5 Flash-Lite", "redacta con los fragmentos",
                                                     "(solo si hay respaldo)"])

    flecha(ax, (3.5, 6.9), (5.2, 6.9), "HTTPS")
    flecha(ax, (3.5, 6.2), (5.2, 3.9), "HTTPS /api")
    flecha(ax, (3.5, 3.2), (5.2, 3.2), "HTTPS (en línea)")
    flecha(ax, (8.8, 3.9), (10.8, 6.4), "SQL (TLS)")
    flecha(ax, (8.8, 3.0), (10.8, 3.0), "HTTPS")
    ax.text(1.9, 0.55, "sin conexión: nada sale del teléfono", ha="center", fontsize=12,
            color=AVISO, style="italic")
    fig.tight_layout()
    fig.savefig(AQUI / "despliegue_poster.png", dpi=300, facecolor="white")
    plt.close(fig)


def qr():
    destinos = {
        "qr_web_render.png": "https://quechua-web.onrender.com",
        "qr_repositorio.png": "https://github.com/omarpiero/TP_RAG_Quechua",
        "qr_app_movil.png": "https://github.com/DalgomXD-byte/quechua-wanka-movil",
    }
    for archivo, url in destinos.items():
        codigo = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=40,
                               border=4)
        codigo.add_data(url)
        codigo.make(fit=True)
        codigo.make_image(fill_color=TINTA, back_color="white").save(AQUI / archivo)


if __name__ == "__main__":
    AQUI.mkdir(parents=True, exist_ok=True)
    despliegue()
    qr()
    print("figuras en", AQUI)
