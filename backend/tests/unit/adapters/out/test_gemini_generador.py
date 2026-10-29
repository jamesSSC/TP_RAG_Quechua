"""ADR-032 · adaptador de Gemini con dobles HTTP: la CI nunca llama a Google.

Gemini solo extrae {forma, glosa}; GeneradorExtractivo las verifica (ADR-028). Sin clave, con
429, con error o con tiempo agotado se degrada al fragmento literal, y la clave no aparece en
ningun mensaje.
"""

import json
import logging

import httpx
import pytest

from adapters.out.generacion.gemini_generador import GeminiGenerador, clave_de_la_peticion
from adapters.out.generacion.generador_extractivo import GeneradorExtractivo
from application.ports.out.generador_texto_port import GeneradorNoDisponible
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.value_objects.idioma import Idioma
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud

CLAVE = "clave-de-prueba-que-no-debe-filtrarse"


def _zorro():
    return FragmentoRecuperado(
        fragmento=Fragmento(
            id="zorro-37",
            texto="ZORRO: Atuq.",
            procedencia=Procedencia("diccionario.pdf", 37),
            tipo=TipoFragmento.LEXICOGRAFICO,
        ),
        puntuacion=PuntuacionSimilitud(0.61),
    )


def _respuesta_gemini(datos: dict, motivo: str = "STOP") -> dict:
    return {
        "candidates": [
            {"content": {"parts": [{"text": json.dumps(datos)}]}, "finishReason": motivo}
        ]
    }


def _gemini(manejador, clave=CLAVE) -> tuple[GeminiGenerador, list[httpx.Request]]:
    peticiones: list[httpx.Request] = []

    def registrar(peticion: httpx.Request) -> httpx.Response:
        peticiones.append(peticion)
        return manejador(peticion)

    cliente = httpx.Client(transport=httpx.MockTransport(registrar))
    return GeminiGenerador(clave=clave, modelo="gemini-prueba", cliente=cliente), peticiones


def test_extrae_forma_y_glosa_y_la_clave_va_en_cabecera_no_en_la_url():
    gemini, peticiones = _gemini(
        lambda _: httpx.Response(200, json=_respuesta_gemini({"forma": "Atuq", "glosa": "ZORRO"}))
    )
    datos = gemini.extraer("¿cómo se dice zorro?", [_zorro()], Idioma.ESPANOL)
    assert datos == {"forma": "Atuq", "glosa": "ZORRO"}
    assert peticiones[0].headers["x-goog-api-key"] == CLAVE
    assert CLAVE not in str(peticiones[0].url)
    cuerpo = json.loads(peticiones[0].content)
    assert cuerpo["generationConfig"]["temperature"] <= 0.2
    assert "ZORRO: Atuq." in cuerpo["contents"][0]["parts"][0]["text"]


def test_envuelto_en_el_extractivo_compone_la_plantilla_y_rotula_gemini():
    gemini, _ = _gemini(
        lambda _: httpx.Response(200, json=_respuesta_gemini({"forma": "Atuq", "glosa": "ZORRO"}))
    )
    generador = GeneradorExtractivo(gemini)
    texto = generador.redactar("¿cómo se dice zorro?", [_zorro()], Idioma.ESPANOL)
    assert "Atuq" in texto
    assert generador.procedencia_redaccion() == ("gemini", None)


def test_una_forma_que_no_esta_en_el_fragmento_se_sustituye_por_el_literal():
    """Salvaguarda: Gemini no puede introducir una forma quechua que el corpus no registra."""
    gemini, _ = _gemini(
        lambda _: httpx.Response(
            200, json=_respuesta_gemini({"forma": "Atoq inventado", "glosa": "ZORRO"})
        )
    )
    generador = GeneradorExtractivo(gemini)
    texto = generador.redactar("¿cómo se dice zorro?", [_zorro()], Idioma.ESPANOL)
    assert texto.startswith("ZORRO: Atuq.")
    assert "inventado" not in texto
    quien, motivo = generador.procedencia_redaccion()
    assert quien == "extractivo" and "verificador" in motivo


@pytest.mark.parametrize(
    ("respuesta", "motivo"),
    [
        (httpx.Response(429, json={"error": {"message": "quota"}}), "429"),
        (httpx.Response(500, text="boom"), "500"),
        (httpx.Response(200, json=_respuesta_gemini({}, motivo="MAX_TOKENS")), "MAX_TOKENS"),
    ],
)
def test_errores_de_la_api_degradan_sin_filtrar_la_clave(respuesta, motivo):
    gemini, _ = _gemini(lambda _: respuesta)
    with pytest.raises(GeneradorNoDisponible) as exc:
        gemini.extraer("zorro", [_zorro()], Idioma.ESPANOL)
    assert motivo in str(exc.value)
    assert CLAVE not in str(exc.value)


def test_el_429_se_cuenta_para_la_medicion():
    gemini, _ = _gemini(lambda _: httpx.Response(429))
    with pytest.raises(GeneradorNoDisponible):
        gemini.extraer("zorro", [_zorro()], Idioma.ESPANOL)
    assert gemini.errores_429 == 1


def test_tiempo_agotado_degrada():
    def lento(peticion):
        raise httpx.ReadTimeout("lento", request=peticion)

    gemini, _ = _gemini(lento)
    with pytest.raises(GeneradorNoDisponible, match="tiempo agotado"):
        gemini.extraer("zorro", [_zorro()], Idioma.ESPANOL)


def test_sin_clave_no_llama_a_la_api():
    gemini, peticiones = _gemini(lambda _: httpx.Response(200), clave="")
    assert gemini.disponible() is False
    with pytest.raises(GeneradorNoDisponible, match="sin clave"):
        gemini.extraer("zorro", [_zorro()], Idioma.ESPANOL)
    assert peticiones == []


def test_la_clave_de_la_peticion_tiene_prioridad_y_caduca():
    gemini, peticiones = _gemini(
        lambda _: httpx.Response(200, json=_respuesta_gemini({"forma": "Atuq", "glosa": "ZORRO"})),
        clave="",
    )
    ficha = clave_de_la_peticion.set("clave-del-usuario")
    try:
        gemini.extraer("zorro", [_zorro()], Idioma.ESPANOL)
    finally:
        clave_de_la_peticion.reset(ficha)
    assert peticiones[0].headers["x-goog-api-key"] == "clave-del-usuario"
    assert gemini.disponible() is False


def test_ninguna_traza_contiene_la_clave(caplog):
    gemini, _ = _gemini(lambda _: httpx.Response(429))
    generador = GeneradorExtractivo(gemini)
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(GeneradorNoDisponible):
            generador.redactar("zorro", [_zorro()], Idioma.ESPANOL)
    assert CLAVE not in caplog.text


def test_no_se_invoca_sin_fragmentos():
    gemini, peticiones = _gemini(lambda _: httpx.Response(200))
    with pytest.raises(ValueError):
        gemini.extraer("zorro", [], Idioma.ESPANOL)
    assert peticiones == []


def test_si_el_modelo_rechaza_la_configuracion_de_razonamiento_se_reintenta_sin_ella():
    respuestas = iter(
        [
            httpx.Response(400, json={"error": {"message": "thinking"}}),
            httpx.Response(200, json=_respuesta_gemini({"forma": "Atuq", "glosa": "ZORRO"})),
        ]
    )
    peticiones: list[httpx.Request] = []

    def manejador(peticion):
        peticiones.append(peticion)
        return next(respuestas)

    cliente = httpx.Client(transport=httpx.MockTransport(manejador))
    gemini = GeminiGenerador(clave=CLAVE, modelo="gemini-3-flash", cliente=cliente)
    assert gemini.extraer("zorro", [_zorro()], Idioma.ESPANOL)["forma"] == "Atuq"
    assert "thinkingConfig" in json.loads(peticiones[0].content)["generationConfig"]
    assert "thinkingConfig" not in json.loads(peticiones[1].content)["generationConfig"]


def test_gemini_3_usa_razonamiento_bajo_con_margen_de_salida():
    gemini, peticiones = _gemini(
        lambda _: httpx.Response(200, json=_respuesta_gemini({"forma": "Atuq", "glosa": "ZORRO"}))
    )
    gemini._modelo = "gemini-3.8-flash"
    gemini.extraer("zorro", [_zorro()], Idioma.ESPANOL)
    config = json.loads(peticiones[0].content)["generationConfig"]
    assert config["thinkingConfig"] == {"thinkingLevel": "low"}
    assert config["maxOutputTokens"] > 300
