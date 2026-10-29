"""Despliegue en la nube (ADR-030 a 032): configuracion por variables, /api/estado sin secretos y
clave de Gemini por peticion (BYOK) que no se registra ni se devuelve."""

import json
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import infrastructure.contenedor as modulo
from adapters.out.generacion.gemini_generador import clave_de_la_peticion
from infrastructure.config import Configuracion, normalizar_database_url
from infrastructure.seguridad import ClaveGeminiDeLaPeticion

BASE = (
    '{"id": "b1", "documento": "base.pdf", "pagina": 1, "texto": "ZORRO: Atuq.", '
    '"tipo": "lexicografico"}\n'
)
SECRETO = "secreto-que-no-debe-salir"


@pytest.mark.parametrize(
    ("entrada", "esperada"),
    [
        (
            "postgres://u:p@ep-x-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require",
            "postgresql+psycopg://u:p@ep-x-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require",
        ),
        (
            "postgresql://u:p@ep-x.neon.tech/neondb",
            "postgresql+psycopg://u:p@ep-x.neon.tech/neondb?sslmode=require",
        ),
        (
            "postgresql://u:p@ep-x.neon.tech/neondb?channel_binding=require",
            "postgresql+psycopg://u:p@ep-x.neon.tech/neondb?channel_binding=require&sslmode=require",
        ),
        ("postgresql://u@localhost/q", "postgresql+psycopg://u@localhost/q"),
    ],
)
def test_database_url_de_neon_se_normaliza_con_tls(entrada, esperada):
    assert normalizar_database_url(entrada) == esperada


def test_database_url_tiene_prioridad_sobre_postgres(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@ep-x.neon.tech/neondb")
    c = Configuracion(_env_file=None, base_datos="postgres", postgres_host="otro")
    assert "ep-x.neon.tech" in c.url_base_datos


def test_valores_por_defecto_locales_no_cambian():
    c = Configuracion(_env_file=None)
    assert (c.corpus_origen, c.entorno, c.generador, c.base_datos) == (
        "jsonl",
        "local",
        "ollama",
        "sqlite",
    )
    assert c.umbral_abstencion == 0.48


@pytest.fixture
def config_local(tmp_path, monkeypatch):
    base = tmp_path / "base.jsonl"
    base.write_text(BASE, encoding="utf-8")

    def config(**extra):
        return Configuracion(
            _env_file=None,
            carpeta_datos=tmp_path / "datos",
            ruta_corpus_base=base,
            ruta_sqlite=tmp_path / "q.db",
            **extra,
        )

    return config, monkeypatch


def test_estado_informa_el_entorno_sin_secretos(config_local):
    config, monkeypatch = config_local
    monkeypatch.setattr(
        modulo,
        "configuracion",
        config(entorno="staging", gemini_api_key=SECRETO, postgres_password=SECRETO),
    )
    contenedor = modulo.Contenedor(generador="gemini")
    estado = contenedor.estado()
    assert estado["entorno"] == "staging"
    assert estado["origen_corpus"] == "jsonl"
    assert estado["motor_base_datos"] == "sqlite"
    assert estado["generador"] == "gemini"
    assert estado["fragmentos_indexados"] == 1
    assert estado["documentos_corpus"] == 1
    assert set(estado["modelos_ml"]) == {"cobertura_hu08_1", "pasajes_rf15"}
    assert SECRETO not in json.dumps(estado, default=str)


def test_generador_extractivo_no_necesita_ollama(config_local):
    config, monkeypatch = config_local
    monkeypatch.setattr(modulo, "configuracion", config())
    contenedor = modulo.Contenedor(generador="extractivo")
    assert contenedor.generador.nombre == "extractivo"
    assert contenedor.generador.disponible() is True
    respuesta = contenedor.consultar_corpus.ejecutar("¿cómo se dice zorro en quechua wanka?")
    if not respuesta.abstenida:
        assert respuesta.redactado_por == "extractivo"


def test_gemini_sin_clave_degrada_al_fragmento_literal_y_lo_dice(config_local):
    config, monkeypatch = config_local
    monkeypatch.setattr(modulo, "configuracion", config(gemini_api_key=""))
    contenedor = modulo.Contenedor(generador="gemini")
    respuesta = contenedor.consultar_corpus.ejecutar("¿cómo se dice zorro en quechua wanka?")
    assert not respuesta.abstenida
    assert respuesta.redactado_por == "extractivo"
    assert respuesta.motivo_redaccion == "sin clave de Gemini"
    assert respuesta.texto.startswith("ZORRO: Atuq.")


def test_corpus_en_postgres_sin_base_no_arranca_en_silencio(config_local):
    config, monkeypatch = config_local
    monkeypatch.setattr(modulo, "configuracion", config(corpus_origen="postgres"))
    with pytest.raises(RuntimeError, match="CORPUS_ORIGEN=postgres"):
        modulo.Contenedor(generador="extractivo")


def _app_espia():
    vistas = []
    app = FastAPI()
    app.add_middleware(ClaveGeminiDeLaPeticion)

    @app.get("/eco")
    def eco():
        vistas.append(clave_de_la_peticion.get())
        logging.getLogger("rag.rest").info("[REST] GET /eco")
        return {"clave_presente": clave_de_la_peticion.get() is not None}

    return app, vistas


def test_byok_la_clave_vale_solo_para_su_peticion_y_no_se_devuelve(caplog):
    app, vistas = _app_espia()
    cliente = TestClient(app)
    with caplog.at_level(logging.DEBUG):
        con = cliente.get("/eco", headers={"X-Gemini-Key": SECRETO})
        sin = cliente.get("/eco")
    assert con.json() == {"clave_presente": True}
    assert sin.json() == {"clave_presente": False}
    assert vistas == [SECRETO, None]
    assert SECRETO not in con.text and SECRETO not in str(con.headers)
    assert SECRETO not in caplog.text
    assert clave_de_la_peticion.get() is None


def _app_origen(token):
    from fastapi import Request

    from infrastructure.seguridad import OrigenDePruebasAutorizado

    app = FastAPI()
    app.add_middleware(OrigenDePruebasAutorizado, token=token)

    @app.get("/origen")
    def origen(request: Request):
        return {"origen": request.scope.get("state", {}).get("origen_pruebas")}

    return TestClient(app)


@pytest.mark.parametrize(
    ("token_servidor", "cabeceras", "esperado"),
    [
        ("t0k3n", {"X-Token-Pruebas": "t0k3n", "X-Origen-Consultas": "carga"}, "carga"),
        ("t0k3n", {"X-Token-Pruebas": "t0k3n", "X-Origen-Consultas": "humo"}, "humo"),
        ("t0k3n", {"X-Token-Pruebas": "otro", "X-Origen-Consultas": "carga"}, None),
        ("t0k3n", {"X-Origen-Consultas": "carga"}, None),
        ("t0k3n", {"X-Token-Pruebas": "t0k3n", "X-Origen-Consultas": "usuario"}, None),
        ("", {"X-Token-Pruebas": "", "X-Origen-Consultas": "carga"}, None),
    ],
)
def test_solo_el_token_del_servidor_permite_rotular_carga_o_humo(
    token_servidor, cabeceras, esperado
):
    assert _app_origen(token_servidor).get("/origen", headers=cabeceras).json() == {
        "origen": esperado
    }


def test_el_contenedor_registra_con_el_origen_autorizado(config_local):
    config, monkeypatch = config_local
    monkeypatch.setattr(modulo, "configuracion", config())
    contenedor = modulo.Contenedor(generador="extractivo")
    assert contenedor.consultar_corpus_para(None) is contenedor.consultar_corpus
    assert contenedor.consultar_corpus_para("carga")._origen.value == "carga"
    assert contenedor.consultar_corpus_para("desconocido") is contenedor.consultar_corpus
