"""La regla de fidelidad declarada para P1-B11, probada con frases propias en espanol y formas
verificadas del diccionario (ZORRO: Atuq. · CONFESAR: Kunfisay. · CÓNCAVO: Puklu.)."""

import importlib.util
import sys
from pathlib import Path

RUTA = Path(__file__).resolve().parents[2] / "scripts" / "medir_fidelidad.py"
spec = importlib.util.spec_from_file_location("medir_fidelidad", RUTA)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

ZORRO = ["ZORRO: Atuq."]


def test_separa_glosa_y_formas_quechuas():
    glosa, formas = m.separar_glosa_y_formas(["CONFESAR: Kunfisay.", "CÓNCAVO: Puklu."])
    assert {"confesar", "concavo"} <= glosa
    assert {"kunfisay", "puklu"} <= formas and not (formas & glosa)


def test_una_redaccion_fiel_no_se_marca():
    r = m.evaluar_fidelidad(
        "La palabra zorro se dice Atuq.", "¿cómo se dice zorro en quechua wanka?", ZORRO
    )
    assert not r["contradiccion_potencial"] and r["forma_quechua_presente"]


def test_la_forma_quechua_del_fragmento_no_cuenta_como_palabra_espanola():
    r = m.evaluar_fidelidad("Atuq", "zorro", ZORRO)
    assert r["palabras_extranas"] == 0


def test_un_significado_distinto_al_de_la_glosa_se_marca():
    r = m.evaluar_fidelidad("Atuq significa lobo feroz de la montana.", "zorro", ZORRO)
    assert r["contradiccion_potencial"] and r["palabras_extranas"] >= 2


def test_tolera_flexiones_por_raiz():
    r = m.evaluar_fidelidad("Los zorros se llaman Atuq.", "zorro", ZORRO)
    assert not r["contradiccion_potencial"]


def test_el_resultado_nunca_incluye_texto():
    r = m.evaluar_fidelidad("Atuq significa lobo.", "zorro", ZORRO)
    assert set(r) == {
        "palabras_extranas",
        "negaciones_ajenas",
        "contradiccion_potencial",
        "forma_quechua_presente",
    }


# --- Regla v2: mas conservadora ---


def test_v2_marca_una_negacion_que_el_diccionario_no_dice():
    assert m.evaluar_fidelidad("Atuq no es zorro.", "zorro", ZORRO)["contradiccion_potencial"]
    assert m.evaluar_fidelidad("Nunca se dice Atuq.", "zorro", ZORRO)["negaciones_ajenas"] == 1
    assert not m.evaluar_fidelidad_v1("Atuq no es zorro.", "zorro", ZORRO)[
        "contradiccion_potencial"
    ]


def test_v2_tolera_la_negacion_que_viene_de_la_consulta():
    r = m.evaluar_fidelidad("No hay otra forma que Atuq.", "no hay zorro", ZORRO)
    assert r["negaciones_ajenas"] == 0


def test_v2_marca_palabras_cortas_de_contenido():
    r = m.evaluar_fidelidad("Atuq es un oso.", "zorro", ZORRO)
    assert r["contradiccion_potencial"] and r["palabras_extranas"] == 1
    assert not m.evaluar_fidelidad_v1("Atuq es un oso.", "zorro", ZORRO)["contradiccion_potencial"]


def test_v2_no_marca_las_palabras_funcionales_cortas():
    r = m.evaluar_fidelidad("Se dice Atuq por zorro.", "zorro", ZORRO)
    assert not r["contradiccion_potencial"]
