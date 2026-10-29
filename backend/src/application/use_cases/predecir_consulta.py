import logging
from collections.abc import Callable

from application.ports import PredecirConsultaPort
from application.ports.out.predictor_port import PredictorPort
from domain.services.caracteristicas_consulta import CaracteristicasConsulta

log = logging.getLogger("rag.caso_uso")


class PredecirConsultaUseCase(PredecirConsultaPort):
    """PMV2 · expone las dos predicciones sin responder la consulta ni registrarla.

    Sirve para inspeccionar el modelo (vista "Predicción ML" y Postman): el mismo vector de
    caracteristicas que usa la consulta real, las dos probabilidades y la decision que cada
    modelo tomaria con su corte de operacion."""

    def __init__(
        self,
        caracteristicas: Callable[[str], CaracteristicasConsulta],
        predictor_cobertura: PredictorPort,
        predictor_pasajes: PredictorPort,
        corte_cobertura: float,
        corte_pasajes: float,
    ):
        self._caracteristicas = caracteristicas
        self._cobertura = predictor_cobertura
        self._pasajes = predictor_pasajes
        self._corte_cobertura = corte_cobertura
        self._corte_pasajes = corte_pasajes

    def ejecutar(self, texto: str) -> dict:
        vector = self._caracteristicas(texto)
        p_cob = self._cobertura.probabilidad(vector)
        p_pas = self._pasajes.probabilidad(vector)
        log.info("[CASO-USO] PredecirConsulta: cobertura=%s pasajes=%s", p_cob, p_pas)
        return {
            "texto": texto,
            "caracteristicas": vector.como_dict(),
            "cobertura": {
                "probabilidad": p_cob,
                "corte": self._corte_cobertura,
                "decision": self._decision_cobertura(p_cob),
                "bloquearia_respuesta": p_cob is not None and p_cob < self._corte_cobertura,
            },
            "pasajes": {
                "probabilidad": p_pas,
                "corte": self._corte_pasajes,
                "decision": self._decision_pasajes(p_pas),
            },
        }

    @staticmethod
    def _decision_cobertura(p) -> str | None:
        if p is None:
            return None
        return "con respaldo probable" if p >= 0.5 else "sin respaldo probable"

    def _decision_pasajes(self, p) -> str | None:
        if p is None:
            return None
        return "mostrar pasajes" if p >= self._corte_pasajes else "retirar pasajes"

    def modelos(self) -> list[dict]:
        return [
            {"clave": clave, "disponible": p.disponible(), **p.metadatos()}
            for clave, p in (("cobertura", self._cobertura), ("pasajes", self._pasajes))
        ]
