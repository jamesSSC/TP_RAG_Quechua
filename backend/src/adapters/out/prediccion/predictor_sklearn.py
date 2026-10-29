"""Adaptador de salida: modelo de scikit-learn entrenado por scripts/entrenar_predictores.py.

El artefacto es un diccionario serializado con joblib que contiene el estimador, la lista de
caracteristicas con la que se entreno y las metricas de validacion. Si el archivo no existe
o fue entrenado con otro vector, el predictor se declara no disponible y el sistema opera
como en el PMV1: la salvaguarda no depende de el (RN-06).
"""

import logging
from pathlib import Path

import joblib

from application.ports.out.predictor_port import PredictorPort
from domain.services.caracteristicas_consulta import NOMBRES, CaracteristicasConsulta

log = logging.getLogger("rag.prediccion")


class PredictorSklearn(PredictorPort):
    def __init__(self, ruta: Path):
        self._ruta = Path(ruta)
        self._estimador = None
        self._metadatos: dict = {}
        self._cargar()

    def _cargar(self) -> None:
        if not self._ruta.exists():
            log.warning("[PREDICTOR] sin artefacto en %s: prediccion desactivada", self._ruta)
            return
        artefacto = joblib.load(self._ruta)
        if tuple(artefacto.get("caracteristicas", ())) != NOMBRES:
            log.warning("[PREDICTOR] %s entrenado con otro vector: desactivado", self._ruta.name)
            return
        self._estimador = artefacto["estimador"]
        self._metadatos = artefacto.get("metadatos", {})
        log.info("[PREDICTOR] cargado %s", self._ruta.name)

    def disponible(self) -> bool:
        return self._estimador is not None

    def probabilidad(self, caracteristicas: CaracteristicasConsulta) -> float | None:
        if self._estimador is None:
            return None
        return float(self._estimador.predict_proba([caracteristicas.como_vector()])[0][1])

    def metadatos(self) -> dict:
        return dict(self._metadatos)
