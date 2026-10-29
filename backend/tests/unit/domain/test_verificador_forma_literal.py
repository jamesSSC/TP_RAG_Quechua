"""ADR-028: forma y glosa del modelo deben aparecer literalmente en el fragmento."""

import pytest

from domain.services.verificador_forma_literal import VerificadorFormaLiteral

# Formas verificadas del diccionario: ZORRO: Atuq. · CONFESAR: Kunfisay. · CÓNCAVO: Puklu.
FRAGMENTOS = ["ZORRO: Atuq.", "CONFESAR: Kunfisay."]
v = VerificadorFormaLiteral()


@pytest.mark.salvaguarda
def test_acepta_forma_y_glosa_que_estan_en_el_fragmento():
    assert v.verificar("Atuq", "zorro", FRAGMENTOS)
    assert v.verificar("Kunfisay", "confesar", FRAGMENTOS)


@pytest.mark.salvaguarda
def test_rechaza_una_forma_alterada_aunque_sea_casi_igual():
    assert not v.verificar("Atoq", "zorro", FRAGMENTOS)  # una letra distinta
    assert not v.verificar("atuq", "zorro", FRAGMENTOS)  # la forma se copia con sus mayusculas
    assert not v.verificar("Atuq'a", "zorro", FRAGMENTOS)


@pytest.mark.salvaguarda
def test_rechaza_una_glosa_que_no_esta_en_el_fragmento():
    assert not v.verificar("Atuq", "lobo", FRAGMENTOS)
    assert not v.verificar("Atuq", "confesar", ["ZORRO: Atuq."])


def test_la_glosa_ignora_mayusculas_pero_no_acentos():
    assert v.verificar("Puklu", "cóncavo", ["CÓNCAVO: Puklu."])
    assert not v.verificar("Puklu", "concavo", ["CÓNCAVO: Puklu."])


def test_varias_formas_se_verifican_una_a_una():
    assert v.verificar("Atuq, Kunfisay", "zorro", ["ZORRO: Atuq, Kunfisay."])
    assert not v.verificar("Atuq, Atoq", "zorro", ["ZORRO: Atuq."])


@pytest.mark.parametrize(
    "forma,glosa", [("", "zorro"), ("Atuq", ""), (None, "zorro"), ("Atuq", None)]
)
def test_vacio_o_ausente_se_rechaza(forma, glosa):
    assert not v.verificar(forma, glosa, FRAGMENTOS)


def test_sin_fragmentos_no_se_acepta_nada():
    assert not v.verificar("Atuq", "zorro", [])
