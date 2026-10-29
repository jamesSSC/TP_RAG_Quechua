"""Refactor de `_resolver` (P1-B9): cada paso extraido se prueba por separado."""

import pytest

from application.ports.out.generador_texto_port import GeneradorNoDisponible
from domain.entities.consulta import Consulta
from domain.services.evaluador_confianza import Veredicto
from domain.value_objects.idioma import Idioma
from tests.unit.application.test_consultar_corpus_con_fakes import _recuperado
from tests.unit.application.test_prediccion_con_fakes import _caso


def _consulta(texto="¿cómo se dice zorro en quechua wanka?"):
    return Consulta(texto=texto, idioma=Idioma.ESPANOL)


def test_idioma_no_soportado_se_abstiene_sin_respaldo():
    consulta = Consulta(texto="x", idioma=Idioma.NO_SOPORTADO)
    caso, _, _ = _caso(0.9)
    r = caso._respuesta_idioma_no_soportado(consulta)
    assert r.abstenida and r.respaldo == [] and r.idioma is Idioma.NO_SOPORTADO


@pytest.mark.salvaguarda
def test_respaldo_por_similitud_conserva_solo_lo_que_alcanza_tau_o_es_lema():
    caso, _, _ = _caso(0.9)
    veredicto = Veredicto(
        responder=True, similitud_maxima=0.6, umbral=0.48, via_respaldo="similitud"
    )
    alto, bajo, lema = _recuperado(0.6), _recuperado(0.2), _recuperado(0.1, lema=True)
    assert caso._seleccionar_respaldo(veredicto, [alto, bajo, lema]) == [alto, lema]


@pytest.mark.salvaguarda
def test_respaldo_por_lema_solo_recibe_las_entradas_cuyo_lema_coincide():
    caso, _, _ = _caso(0.9)
    veredicto = Veredicto(responder=True, similitud_maxima=0.6, umbral=0.48, via_respaldo="lema")
    alto, lema = _recuperado(0.6), _recuperado(0.1, lema=True)
    assert caso._seleccionar_respaldo(veredicto, [alto, lema]) == [lema]


@pytest.mark.salvaguarda
@pytest.mark.parametrize(
    "responder,p,esperado",
    [
        (True, 0.05, True),  # añade una abstencion
        (True, 0.97, False),
        (True, None, False),  # sin modelo, opera como el PMV1
        (False, 0.05, False),  # nunca convierte (ni cambia) una abstencion de la regla
        (False, 0.99, False),  # RN-06: tampoco puede convertirla en respuesta
    ],
)
def test_el_predictor_solo_puede_anadir_abstenciones(responder, p, esperado):
    caso, _, _ = _caso(0.9, corte_cob=0.25)
    v = Veredicto(responder=responder, similitud_maxima=0.5, umbral=0.48)
    assert caso._abstiene_por_predictor(v, p) is esperado


def test_respuesta_por_predictor_no_afirma_ni_cita():
    caso, _, _ = _caso(0.9)
    v = Veredicto(responder=True, similitud_maxima=0.5, umbral=0.48, via_respaldo="similitud")
    r = caso._respuesta_por_predictor(_consulta(), Idioma.ESPANOL, v, 0.05)
    assert r.abstenida and r.abstencion_por_predictor and r.respaldo == []
    assert r.probabilidad_cobertura == 0.05


def test_filtro_de_pasajes_retira_los_poco_probables_y_conserva_los_probables():
    caso, _, _ = _caso(0.9, p_pas=0.2, corte_pas=0.5)
    assert caso._filtrar_pasajes_por_predictor(["a"], {"vector": [1]}) == ([], 0.2)
    caso, _, _ = _caso(0.9, p_pas=0.9, corte_pas=0.5)
    assert caso._filtrar_pasajes_por_predictor(["a"], {"vector": [1]}) == (["a"], 0.9)


def test_filtro_de_pasajes_sin_pasajes_o_sin_vector_no_consulta_al_modelo():
    caso, _, _ = _caso(0.9, p_pas=0.2)
    assert caso._filtrar_pasajes_por_predictor([], {"vector": [1]}) == ([], None)
    assert caso._filtrar_pasajes_por_predictor(["a"], {"vector": None}) == (["a"], None)
    assert caso._predictor_pasajes.llamadas == 0


def test_redactar_usa_el_generador_y_sin_aviso():
    caso, generador, _ = _caso(0.9)
    texto, aviso = caso._redactar(_consulta(), [_recuperado(0.6)], Idioma.ESPANOL)
    assert texto == "ZORRO: Atuq." and aviso is None and generador.invocaciones == 1


@pytest.mark.salvaguarda
def test_redactar_sin_generador_devuelve_el_fragmento_literal_con_cita_y_aviso():
    caso, _, _ = _caso(0.9)

    class Caido:
        def redactar(self, *a):
            raise GeneradorNoDisponible("x")

    caso._generador = Caido()
    texto, aviso = caso._redactar(_consulta(), [_recuperado(0.6)], Idioma.ESPANOL)
    assert texto.startswith("ZORRO: Atuq. (") and "37" in texto
    assert aviso is not None


def test_anotar_lectura_ganadora_solo_si_hay_variantes_y_cambia_el_texto():
    consulta = _consulta("zorro")
    consulta.variantes = ["fox"]
    r = _recuperado(0.6)
    from application.use_cases.consultar_corpus import ConsultarCorpusUseCase as C

    C._anotar_lectura_ganadora(consulta, [r], {r.id: "fox"})
    assert consulta.texto_traducido == "fox"
    otra = _consulta("zorro")
    C._anotar_lectura_ganadora(otra, [r], {r.id: "fox"})  # sin variantes: no anota
    assert otra.texto_traducido is None


def test_traducir_sin_traductor_no_cambia_el_idioma():
    caso, _, _ = _caso(0.9)
    caso._traductor = None
    assert caso._traducir(_consulta(), Idioma.ESPANOL) is Idioma.ESPANOL


@pytest.mark.salvaguarda
def test_un_fallo_al_registrar_no_tumba_la_respuesta():
    """Si el historial no se puede escribir, la consulta se responde igual."""
    caso, _, repo = _caso(0.61, p_cob=0.97)

    def falla(consulta, respuesta):
        raise RuntimeError("database is locked")

    repo.registrar = falla
    r = caso.ejecutar("¿cómo se dice zorro en quechua wanka?")
    assert not r.abstenida and r.respaldo  # sigue citando documento y pagina


def test_el_aviso_de_registro_fallido_lleva_id_causa_y_traza_sin_el_texto(caplog):
    caso, _, repo = _caso(0.61, p_cob=0.97)

    def falla(consulta, respuesta):
        raise RuntimeError("database is locked")

    repo.registrar = falla
    texto = "¿cómo se dice zorro en quechua wanka?"
    with caplog.at_level("WARNING"):
        caso.ejecutar(texto)
    registro = next(r for r in caplog.records if "no se pudo registrar" in r.getMessage())
    mensaje = registro.getMessage()
    assert "consulta_id=" in mensaje and "RuntimeError" in mensaje
    assert registro.exc_info is not None and "database is locked" in str(registro.exc_info[1])
    assert texto not in mensaje
