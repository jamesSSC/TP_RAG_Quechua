"""P1-B11: respuestas cortadas (done_reason) y redaccion extractiva verificada (ADR-028)."""

import json

import httpx
import pytest

from adapters.out.generacion.generador_extractivo import GeneradorExtractivo
from adapters.out.generacion.ollama_generador import OllamaGenerador
from application.ports.out.generador_texto_port import GeneradorNoDisponible
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.value_objects.idioma import Idioma
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud

DOC = "293274822-diccionario-quechua-Wanka-docx.pdf"


def _zorro():
    return FragmentoRecuperado(
        fragmento=Fragmento("z", "ZORRO: Atuq.", Procedencia(DOC, 37), TipoFragmento.LEXICOGRAFICO),
        puntuacion=PuntuacionSimilitud(0.61),
    )


class Ollama:
    """Doble de httpx.post: responde en orden y recuerda lo que se le pidio."""

    def __init__(self, *cuerpos):
        self.cuerpos = list(cuerpos)
        self.peticiones = []

    def __call__(self, url, **kwargs):
        self.peticiones.append(kwargs["json"])
        cuerpo = self.cuerpos.pop(0)
        return httpx.Response(200, json=cuerpo, request=httpx.Request("POST", url))


def _ollama(monkeypatch, *cuerpos):
    doble = Ollama(*cuerpos)
    monkeypatch.setattr(httpx, "post", doble)
    return doble


def _fin(texto, razon="stop"):
    return {"response": texto, "done_reason": razon}


# --- Corte de respuestas ---


def test_una_respuesta_completa_se_entrega_tal_cual(monkeypatch):
    doble = _ollama(monkeypatch, _fin("Se dice Atuq."))
    assert OllamaGenerador().redactar("zorro", [_zorro()], Idioma.ESPANOL) == "Se dice Atuq."
    assert len(doble.peticiones) == 1


def test_si_topa_con_el_limite_se_reintenta_con_mas_margen(monkeypatch):
    doble = _ollama(monkeypatch, _fin("Se dice At", "length"), _fin("Se dice Atuq.", "stop"))
    texto = OllamaGenerador().redactar("zorro", [_zorro()], Idioma.ESPANOL)
    assert texto == "Se dice Atuq."
    primero, segundo = (p["options"]["num_predict"] for p in doble.peticiones)
    assert segundo > primero


@pytest.mark.salvaguarda
def test_una_respuesta_truncada_nunca_se_entrega(monkeypatch):
    _ollama(monkeypatch, _fin("Se dice At", "length"), _fin("Se dice At", "length"))
    with pytest.raises(GeneradorNoDisponible, match="truncada"):
        OllamaGenerador().redactar("zorro", [_zorro()], Idioma.ESPANOL)


# --- Redaccion extractiva ---


def _extractivo(monkeypatch, *cuerpos):
    doble = _ollama(monkeypatch, *cuerpos)
    return GeneradorExtractivo(OllamaGenerador()), doble


def _json(forma, glosa):
    return _fin(json.dumps({"forma": forma, "glosa": glosa}))


@pytest.mark.salvaguarda
def test_la_forma_verificada_se_compone_en_una_plantilla(monkeypatch):
    g, doble = _extractivo(monkeypatch, _json("Atuq", "zorro"))
    texto = g.redactar("¿cómo se dice zorro?", [_zorro()], Idioma.ESPANOL)
    assert "Atuq" in texto and "zorro" in texto
    assert (g.aceptadas, g.descartadas) == (1, 0)
    assert doble.peticiones[0]["format"] == "json"


@pytest.mark.salvaguarda
def test_una_forma_alterada_se_descarta_y_se_muestra_el_fragmento_literal(monkeypatch):
    g, _ = _extractivo(monkeypatch, _json("Atoq", "zorro"))
    texto = g.redactar("¿cómo se dice zorro?", [_zorro()], Idioma.ESPANOL)
    assert texto.startswith("ZORRO: Atuq.") and DOC in texto and "37" in texto
    assert "Atoq" not in texto
    assert (g.aceptadas, g.descartadas) == (0, 1)


@pytest.mark.salvaguarda
def test_una_glosa_inventada_se_descarta(monkeypatch):
    g, _ = _extractivo(monkeypatch, _json("Atuq", "lobo"))
    texto = g.redactar("¿cómo se dice zorro?", [_zorro()], Idioma.ESPANOL)
    assert texto.startswith("ZORRO: Atuq.") and "lobo" not in texto
    assert g.descartadas == 1


def test_un_json_malformado_se_descarta_sin_romper(monkeypatch):
    g, _ = _extractivo(monkeypatch, _fin("esto no es json"))
    assert g.redactar("zorro", [_zorro()], Idioma.ESPANOL).startswith("ZORRO: Atuq.")
    assert g.descartadas == 1


def test_si_el_modelo_no_responde_se_propaga_para_el_aviso_de_redaccion(monkeypatch):
    def cae(url, **kw):
        raise httpx.ConnectError("sin red")

    monkeypatch.setattr(httpx, "post", cae)
    with pytest.raises(GeneradorNoDisponible):
        GeneradorExtractivo(OllamaGenerador()).redactar("zorro", [_zorro()], Idioma.ESPANOL)


def test_la_plantilla_en_ingles(monkeypatch):
    g, _ = _extractivo(monkeypatch, _json("Atuq", "zorro"))
    texto = g.redactar("how do you say fox?", [_zorro()], Idioma.INGLES)
    assert "Atuq" in texto and "Wanka Quechua" in texto


# --- Fallos de la auditoria del PR #13: nada de esto debe llegar a la plantilla ---


def _dos_entradas():
    texto = "MIEDOSO: Manchakug. MIEL: Añalla, mishki. PERRO: Allqu (perro doméstico)."
    return [
        FragmentoRecuperado(
            fragmento=Fragmento("m", texto, Procedencia(DOC, 20), TipoFragmento.LEXICOGRAFICO),
            puntuacion=PuntuacionSimilitud(0.6),
        )
    ]


@pytest.mark.salvaguarda
@pytest.mark.parametrize(
    "forma,glosa,caso",
    [
        ("Manchak", "miedoso", "forma truncada"),
        ("perro", "perro", "el lema castellano como forma"),
        ("Añalla", "miedoso", "forma de otra entrada"),
        ("Manchakug", "miel", "par cruzado: forma de una entrada y glosa de otra"),
    ],
)
def test_el_generador_extractivo_muestra_el_fragmento_literal_ante_cada_fallo(
    monkeypatch, forma, glosa, caso
):
    g, _ = _extractivo(monkeypatch, _json(forma, glosa))
    texto = g.redactar("consulta", _dos_entradas(), Idioma.ESPANOL)
    assert texto.startswith("MIEDOSO: Manchakug."), caso  # fragmento literal, no la plantilla
    assert "se dice" not in texto
    assert (g.aceptadas, g.descartadas) == (0, 1)


@pytest.mark.salvaguarda
def test_la_plantilla_usa_la_forma_tal_como_esta_en_el_fragmento(monkeypatch):
    g, _ = _extractivo(monkeypatch, _json("añalla, MISHKI", "Miel"))
    texto = g.redactar("consulta", _dos_entradas(), Idioma.ESPANOL)
    assert "Añalla, mishki" in texto and "«miel»" in texto
    assert g.aceptadas == 1
