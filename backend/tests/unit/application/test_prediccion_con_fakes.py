"""PMV2 · casos de uso de prediccion con dobles de todos los puertos (HU-08.1, HU-04, HU-09).

La regla que no puede romperse es RN-06: los modelos predictivos solo AÑADEN abstenciones o
retiran pasajes; nunca convierten en respuesta lo que la regla del umbral rechaza.
"""

import pytest

from application.ports.out.predictor_port import PredictorPort
from application.use_cases.analizar_demanda import AnalizarDemandaUseCase
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase
from application.use_cases.predecir_consulta import PredecirConsultaUseCase
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.services.evaluador_confianza import EvaluadorConfianza
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud
from tests.unit.application.test_consultar_corpus_con_fakes import (
    DetectorFake,
    GeneradorFake,
    IndiceFake,
    RepositorioFake,
    TraductorFake,
)


class PredictorFijo(PredictorPort):
    def __init__(self, p: float | None):
        self.p, self.llamadas = p, 0

    def probabilidad(self, caracteristicas):
        self.llamadas += 1
        return self.p

    def disponible(self):
        return self.p is not None

    def metadatos(self):
        return {"nombre": "fijo", "validacion_cruzada": {"auc_roc": 0.99}}


class IndiceConProsa(IndiceFake):
    def recuperar_prosa(self, consulta, k=3):
        return [
            FragmentoRecuperado(
                fragmento=Fragmento(
                    id="p1",
                    texto="El sufijo ablativo indica el origen del movimiento",
                    procedencia=Procedencia("gramatica.pdf", 120),
                    tipo=TipoFragmento.PROSA,
                ),
                puntuacion=PuntuacionSimilitud(0.30),
            )
        ]


def _caso(puntuacion, p_cob=None, p_pas=None, corte_cob=0.25, corte_pas=0.5, indice=None):
    generador, repo = GeneradorFake(), RepositorioFake()
    caso = ConsultarCorpusUseCase(
        indice=indice or IndiceFake(puntuacion),
        generador=generador,
        evaluador=EvaluadorConfianza(umbral=0.48),
        detector_idioma=DetectorFake(),
        repositorio=repo,
        traductor=TraductorFake(),
        predictor_cobertura=PredictorFijo(p_cob),
        predictor_pasajes=PredictorFijo(p_pas),
        probabilidad_minima_cobertura=corte_cob,
        probabilidad_minima_pasajes=corte_pas,
    )
    return caso, generador, repo


def test_cobertura_alta_responde_y_registra_la_prediccion():
    caso, generador, repo = _caso(0.61, p_cob=0.97)
    r = caso.ejecutar("¿cómo se dice zorro en quechua wanka?")
    assert not r.abstenida
    assert r.probabilidad_cobertura == 0.97
    assert generador.invocaciones == 1
    assert repo.registros[0][1].probabilidad_cobertura == 0.97


@pytest.mark.salvaguarda
def test_cobertura_baja_se_abstiene_sin_invocar_al_generador():
    caso, generador, _ = _caso(0.61, p_cob=0.05)
    r = caso.ejecutar("¿cómo se dice zorro en quechua wanka?")
    assert r.abstenida and r.abstencion_por_predictor
    assert r.respaldo == []
    assert generador.invocaciones == 0


@pytest.mark.salvaguarda
def test_rn06_el_predictor_no_anula_la_regla_del_umbral():
    # Similitud bajo tau y probabilidad estimada alta: el sistema se abstiene igual.
    caso, generador, _ = _caso(0.20, p_cob=0.99)
    r = caso.ejecutar("¿cómo se dice zorro en quechua wanka?")
    assert r.abstenida
    assert not r.abstencion_por_predictor
    assert generador.invocaciones == 0


def test_sin_modelo_el_sistema_opera_como_en_el_pmv1():
    caso, generador, _ = _caso(0.61, p_cob=None, p_pas=None)
    r = caso.ejecutar("¿cómo se dice zorro en quechua wanka?")
    assert not r.abstenida
    assert r.probabilidad_cobertura is None


def test_el_modelo_de_pasajes_retira_pasajes_poco_probables():
    caso, _, _ = _caso(0.10, p_cob=0.4, p_pas=0.2, indice=IndiceConProsa(0.10))
    r = caso.ejecutar("¿qué indica el sufijo ablativo?")
    assert r.abstenida
    assert r.pasajes == []
    assert r.probabilidad_pasajes == 0.2


def test_el_modelo_de_pasajes_conserva_los_probables_sin_afirmarlos():
    caso, generador, _ = _caso(0.10, p_cob=0.4, p_pas=0.9, indice=IndiceConProsa(0.10))
    r = caso.ejecutar("¿qué indica el sufijo ablativo?")
    assert r.abstenida  # RN-09: con pasajes sigue siendo una abstencion
    assert len(r.pasajes) == 1
    assert generador.invocaciones == 0


def test_predecir_consulta_devuelve_las_dos_predicciones_sin_registrar():
    caso, _, repo = _caso(0.61)
    uc = PredecirConsultaUseCase(
        caracteristicas=caso.caracteristicas,
        predictor_cobertura=PredictorFijo(0.9),
        predictor_pasajes=PredictorFijo(0.3),
        corte_cobertura=0.25,
        corte_pasajes=0.5,
    )
    salida = uc.ejecutar("¿cómo se dice zorro en quechua wanka?")
    assert salida["cobertura"]["probabilidad"] == 0.9
    assert salida["cobertura"]["decision"] == "con respaldo probable"
    assert salida["pasajes"]["decision"] == "retirar pasajes"
    assert "similitud_maxima" in salida["caracteristicas"]
    assert repo.registros == []
    assert [m["clave"] for m in uc.modelos()] == ["cobertura", "pasajes"]


class RepositorioDemanda(RepositorioFake):
    def __init__(self, total, abstenciones):
        super().__init__()
        self._total, self._abst = total, abstenciones

    def estadisticas(self, incluir_sinteticas=False):
        return {"total": self._total, "abstenidas": len(self._abst)}

    def abstenciones_con_prediccion(self, limite=5000, incluir_sinteticas=False):
        return self._abst

    def conteo_por_origen(self):
        return {"usuario": self._total}


def test_hu09_historial_insuficiente_no_emite_priorizacion():
    uc = AnalizarDemandaUseCase(RepositorioDemanda(99, [("¿cómo se dice dron?", 0.1)]))
    salida = uc.ejecutar()
    assert salida["suficiente"] is False
    assert salida["prioridades"] == []
    assert "insuficiente" in salida["mensaje"]


def test_hu09_ordena_por_demanda_insatisfecha_ponderada():
    abstenciones = [
        ("¿cómo se dice dron en quechua wanka?", 0.05),
        ("¿cómo se dice dron?", 0.10),
        ("¿cómo se dice dron?", 0.15),
        ("¿cómo se dice tristeza?", 0.80),
        ("¿cómo se dice tristeza?", 0.90),
    ]
    salida = AnalizarDemandaUseCase(RepositorioDemanda(150, abstenciones)).ejecutar()
    primero, segundo = salida["prioridades"][:2]
    assert primero["termino"] == "dron" and primero["consultas"] == 3
    assert primero["diagnostico"] == "ampliar el corpus"
    assert segundo["termino"] == "tristeza"
    assert segundo["diagnostico"] == "revisar la recuperación"
    assert primero["demanda_insatisfecha"] > segundo["demanda_insatisfecha"]
