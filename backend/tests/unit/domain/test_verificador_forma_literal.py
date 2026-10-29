"""ADR-028: forma y glosa del modelo deben ser de la MISMA entrada del fragmento, con limites de
palabra. Formas verificadas del diccionario: ZORRO: Atuq. · CONFESAR: Kunfisay. · CÓNCAVO: Puklu."""

import pytest

from domain.services.entradas_lexicas import PATRON_LEMA, segmentar_entradas
from domain.services.verificador_forma_literal import VerificadorFormaLiteral

ZORRO_Y_CONFESAR = ["ZORRO: Atuq.", "CONFESAR: Kunfisay."]
v = VerificadorFormaLiteral()


# --- Segmentacion en entradas (misma regla de lema que el indice) ---


def test_el_indice_y_el_verificador_comparten_el_patron_de_lema():
    from adapters.out.recuperacion import indice_hibrido_lexico

    assert indice_hibrido_lexico.PATRON_LEMA is PATRON_LEMA


def test_segmenta_un_fragmento_con_varias_entradas():
    entradas = segmentar_entradas("CONFESAR: Kunfisay. CÓNCAVO: Puklu.")
    assert [e.lema for e in entradas] == ["CONFESAR", "CÓNCAVO"]
    assert "Kunfisay" in entradas[0].cuerpo and "Puklu" not in entradas[0].cuerpo
    assert "Puklu" in entradas[1].cuerpo


# --- Aceptaciones ---


@pytest.mark.salvaguarda
def test_acepta_forma_y_glosa_de_la_misma_entrada():
    assert v.verificar("Atuq", "zorro", ZORRO_Y_CONFESAR)
    assert v.verificar("Kunfisay", "confesar", ZORRO_Y_CONFESAR)


def test_la_forma_aceptada_se_devuelve_tal_como_esta_en_el_fragmento():
    r = v.comprobar("atuq", "Zorro", ZORRO_Y_CONFESAR)  # solo se normalizan mayusculas
    assert r is not None and r.forma == "Atuq" and r.glosa == "zorro"


def test_varias_formas_de_la_misma_entrada():
    assert v.verificar("Atuq, Kunfisay", "zorro", ["ZORRO: Atuq, Kunfisay."])
    assert not v.verificar("Atuq, Atoq", "zorro", ["ZORRO: Atuq."])


def test_secuencia_completa_de_tokens():
    assert v.verificar("Kunfisay Puklu", "confesar", ["CONFESAR: Kunfisay Puklu."])
    assert not v.verificar("Kunfisay Pukl", "confesar", ["CONFESAR: Kunfisay Puklu."])


# --- Rechazos: cada fallo del auditor ---


@pytest.mark.salvaguarda
@pytest.mark.parametrize("forma", ["Atu", "tuq", "Atuqa", "Atoq", "Atuq'a"])
def test_rechaza_una_forma_truncada_o_alterada(forma):
    assert not v.verificar(forma, "zorro", ZORRO_Y_CONFESAR)


@pytest.mark.salvaguarda
def test_rechaza_el_lema_castellano_usado_como_forma():
    # "perro" figura en el cuerpo (nota entre parentesis) pero es la glosa, no la forma quechua.
    fragmento = ["PERRO: Allqu (perro doméstico)."]
    assert not v.verificar("perro", "perro", fragmento)
    assert v.verificar("Allqu", "perro", fragmento)


@pytest.mark.salvaguarda
def test_rechaza_una_forma_de_una_entrada_distinta():
    fragmento = ["MIEDOSO: Manchakug. MIEL: Añalla, mishki."]
    assert not v.verificar("Añalla", "miedoso", fragmento)
    assert v.verificar("Añalla", "miel", fragmento)


@pytest.mark.salvaguarda
def test_rechaza_el_par_cruzado_forma_de_una_entrada_y_glosa_de_otra():
    # Cada una existe en el fragmento, pero el diccionario no las une.
    assert not v.verificar("Atuq", "confesar", ZORRO_Y_CONFESAR)
    assert not v.verificar("Kunfisay", "zorro", ZORRO_Y_CONFESAR)


@pytest.mark.salvaguarda
def test_rechaza_una_glosa_que_no_esta_en_el_fragmento():
    assert not v.verificar("Atuq", "lobo", ZORRO_Y_CONFESAR)


@pytest.mark.salvaguarda
def test_si_falla_cualquier_comprobacion_comprobar_devuelve_none():
    assert v.comprobar("Atu", "zorro", ZORRO_Y_CONFESAR) is None
    assert v.comprobar("Atuq", "confesar", ZORRO_Y_CONFESAR) is None


def test_la_glosa_ignora_mayusculas_pero_no_acentos():
    assert v.verificar("Puklu", "cóncavo", ["CÓNCAVO: Puklu."])
    assert not v.verificar("Puklu", "concavo", ["CÓNCAVO: Puklu."])


def test_las_letras_quechuas_no_se_normalizan():
    assert not v.verificar("Pukľu", "cóncavo", ["CÓNCAVO: Puklu."])
    assert not v.verificar("Puklú", "cóncavo", ["CÓNCAVO: Puklu."])


def test_un_fragmento_sin_entradas_no_verifica_nada():
    assert not v.verificar("Atuq", "zorro", ["texto de prosa sin lema Atuq zorro"])


@pytest.mark.parametrize(
    "forma,glosa", [("", "zorro"), ("Atuq", ""), (None, "zorro"), ("Atuq", None)]
)
def test_vacio_o_ausente_se_rechaza(forma, glosa):
    assert not v.verificar(forma, glosa, ZORRO_Y_CONFESAR)


def test_sin_fragmentos_no_se_acepta_nada():
    assert not v.verificar("Atuq", "zorro", [])


# --- Re-auditoria del PR #13: formas fusionadas y castellano entre parentesis ---

PERRO = ["PERRO: Allqu, ashuti."]


@pytest.mark.salvaguarda
def test_rechaza_dos_formas_fusionadas_sin_la_coma():
    assert not v.verificar("Allqu ashuti", "perro", PERRO)
    assert v.verificar("Allqu, ashuti", "perro", PERRO)
    assert v.verificar("Allqu", "perro", PERRO) and v.verificar("ashuti", "perro", PERRO)


@pytest.mark.salvaguarda
@pytest.mark.parametrize("cuerpo", ["Atuq. Wayqu.", "Atuq; Wayqu.", "Atuq (nota) Wayqu."])
def test_una_forma_no_cruza_puntos_ni_punto_y_coma_ni_parentesis(cuerpo):
    assert not v.verificar("Atuq Wayqu", "zorro", [f"ZORRO: {cuerpo}"])


@pytest.mark.salvaguarda
def test_acepta_una_secuencia_contigua_dentro_de_un_solo_segmento():
    assert v.verificar("Kunfisay Puklu", "confesar", ["CONFESAR: Kunfisay Puklu, Atuq."])
    assert not v.verificar("Puklu Atuq", "confesar", ["CONFESAR: Kunfisay Puklu, Atuq."])


@pytest.mark.salvaguarda
@pytest.mark.parametrize("forma", ["doméstico", "perro doméstico", "domestico"])
def test_el_castellano_entre_parentesis_no_cuenta_como_forma(forma):
    assert not v.verificar(forma, "perro", ["PERRO: Allqu (perro doméstico)."])


@pytest.mark.salvaguarda
def test_la_forma_antes_o_despues_de_un_parentesis_si_se_acepta():
    assert v.verificar("Allqu", "perro", ["PERRO: Allqu (perro doméstico)."])
    assert v.verificar("Ushtuchiy", "ensartar", ["ENSARTAR: Ushtuchiy (ensartar cuentas)"])


@pytest.mark.salvaguarda
@pytest.mark.parametrize(
    "cuerpo",
    [
        "Ayka (¿ Cuántos años tienes?) ¿Aykataq watayki?",  # frases de ejemplo: no se distingue
        "Allqu (perro",  # parentesis sin cerrar
        "Allqu perro) mansos",  # parentesis sin abrir
    ],
)
def test_si_la_estructura_no_permite_distinguir_se_descarta(cuerpo):
    assert not v.verificar("Allqu", "perro", [f"PERRO: {cuerpo}"])
