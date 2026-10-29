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
    assert set(r) == {"palabras_extranas", "contradiccion_potencial", "forma_quechua_presente"}
