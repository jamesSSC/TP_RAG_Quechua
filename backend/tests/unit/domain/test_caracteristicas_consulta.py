"""PMV2 · vector de caracteristicas de los modelos predictivos (dominio puro)."""

from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.services.caracteristicas_consulta import NOMBRES, extraer_caracteristicas
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud


def _rec(texto, p, tipo=TipoFragmento.LEXICOGRAFICO, lema=False, i="x"):
    return FragmentoRecuperado(
        fragmento=Fragmento(id=i, texto=texto, procedencia=Procedencia("doc.pdf", 1), tipo=tipo),
        puntuacion=PuntuacionSimilitud(p),
        coincidencia_lema=lema,
    )


def test_el_vector_sigue_el_orden_declarado():
    c = extraer_caracteristicas("zorro", ["zorro"], [_rec("ZORRO: Atuq.", 0.6)], [], 0.0)
    assert len(c.como_vector()) == len(NOMBRES)
    assert list(c.como_dict()) == list(NOMBRES)


def test_cuentas_de_similitud_margen_y_lema():
    recuperados = [_rec("A: a.", 0.6, lema=True, i="1"), _rec("B: b.", 0.4, i="2")]
    c = extraer_caracteristicas("zorro", ["zorro"], recuperados, [], 0.5)
    assert c.similitud_maxima == 0.6
    assert round(c.margen_top1_top2, 6) == 0.2
    assert round(c.similitud_media_top5, 6) == 0.5
    assert c.coincidencia_lema == 1.0
    assert c.proporcion_fuera_vocabulario == 0.5
    assert c.terminos_consulta == 1.0


def test_palabras_compartidas_con_la_prosa_ignoran_tildes_y_palabras_cortas():
    pasaje = _rec("El sufijo ablativo marca el origen", 0.3, tipo=TipoFragmento.PROSA)
    c = extraer_caracteristicas(
        "¿qué es el sufijo ablativo?", ["sufijo", "ablativo"], [], [pasaje], 0.0
    )
    assert c.palabras_compartidas_prosa == 2.0  # sufijo, ablativo ("el", "es" no cuentan)
    assert c.proporcion_compartida_prosa == 1.0
    assert c.similitud_prosa_maxima == 0.3


def test_sin_recuperados_el_vector_es_cero_y_no_falla():
    c = extraer_caracteristicas("nada", [], [], [], 1.0)
    assert c.similitud_maxima == 0.0 and c.dispersion_top5 == 0.0
