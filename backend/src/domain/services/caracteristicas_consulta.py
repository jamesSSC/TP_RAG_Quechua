"""Caracteristicas de una consulta para los modelos predictivos del PMV2 (RF-14, RF-15).

Todo se calcula a partir de lo que el sistema ya mide al recuperar: no hay ninguna senal
nueva que el usuario no pueda ver en la interfaz. Por eso vive en el dominio y no depende de
ninguna biblioteca de aprendizaje automatico: el adaptador de prediccion recibe el vector ya
construido y el script de entrenamiento lo obtiene por esta misma via, de modo que entrenar y
predecir usan exactamente las mismas cuentas.
"""

import re
import unicodedata
from dataclasses import asdict, dataclass

from domain.entities.fragmento import FragmentoRecuperado

LARGO_PALABRA_CONTENIDO = 5

# Orden fijo del vector. Cambiarlo invalida los modelos entrenados: el artefacto guarda esta
# lista y el adaptador la compara al cargarlo.
NOMBRES = (
    "similitud_maxima",
    "margen_top1_top2",
    "similitud_media_top5",
    "dispersion_top5",
    "similitud_prosa_maxima",
    "similitud_prosa_media_top3",
    "palabras_compartidas_prosa",
    "proporcion_compartida_prosa",
    "terminos_consulta",
    "proporcion_fuera_vocabulario",
    "coincidencia_lema",
)


def palabras_de_contenido(texto: str) -> set[str]:
    normalizado = "".join(
        c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn"
    )
    return {p for p in re.findall(r"[a-z]+", normalizado) if len(p) >= LARGO_PALABRA_CONTENIDO}


@dataclass(frozen=True)
class CaracteristicasConsulta:
    similitud_maxima: float
    margen_top1_top2: float
    similitud_media_top5: float
    dispersion_top5: float
    similitud_prosa_maxima: float
    similitud_prosa_media_top3: float
    palabras_compartidas_prosa: float
    proporcion_compartida_prosa: float
    terminos_consulta: float
    proporcion_fuera_vocabulario: float
    coincidencia_lema: float

    def como_vector(self) -> list[float]:
        return [float(getattr(self, n)) for n in NOMBRES]

    def como_dict(self) -> dict[str, float]:
        return asdict(self)


def extraer_caracteristicas(
    consulta: str,
    terminos_depurados: list[str],
    recuperados: list[FragmentoRecuperado],
    pasajes: list[FragmentoRecuperado],
    proporcion_fuera_vocabulario: float,
) -> CaracteristicasConsulta:
    """`recuperados`: los k mejores fragmentos (todas las variantes de la consulta).
    `pasajes`: los mejores pasajes de prosa, sin filtrar."""
    puntos = sorted((r.puntuacion.valor for r in recuperados), reverse=True)[:5]
    maxima = puntos[0] if puntos else 0.0
    segunda = puntos[1] if len(puntos) > 1 else 0.0
    media = sum(puntos) / len(puntos) if puntos else 0.0
    dispersion = (sum((p - media) ** 2 for p in puntos) / len(puntos)) ** 0.5 if puntos else 0.0

    prosa = sorted((p.puntuacion.valor for p in pasajes), reverse=True)[:3]
    del_usuario = palabras_de_contenido(consulta)
    compartidas = max(
        (len(del_usuario & palabras_de_contenido(p.texto)) for p in pasajes), default=0
    )

    return CaracteristicasConsulta(
        similitud_maxima=maxima,
        margen_top1_top2=maxima - segunda,
        similitud_media_top5=media,
        dispersion_top5=dispersion,
        similitud_prosa_maxima=prosa[0] if prosa else 0.0,
        similitud_prosa_media_top3=sum(prosa) / len(prosa) if prosa else 0.0,
        palabras_compartidas_prosa=float(compartidas),
        proporcion_compartida_prosa=compartidas / max(1, len(del_usuario)),
        terminos_consulta=float(len(terminos_depurados)),
        proporcion_fuera_vocabulario=proporcion_fuera_vocabulario,
        coincidencia_lema=1.0 if any(r.coincidencia_lema for r in recuperados) else 0.0,
    )
