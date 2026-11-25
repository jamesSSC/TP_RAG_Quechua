"""Arreglos rapidos de la ingenieria inversa (B13): H-09 (nombre del repositorio de fuentes y
nivel del registro), H-10 (/api/estado no informa un modelo que no redacta) y la variable
TRADUCTOR, que antes se ignoraba."""

from importlib import import_module

import pytest

import infrastructure.contenedor as modulo
from adapters.out.persistencia.repositorio_fuentes_sqlalchemy import RepositorioFuentesSqlalchemy
from adapters.out.traduccion.ollama_traductor import OllamaTraductor
from adapters.out.traduccion.traductor_tabla import TraductorTabla
from infrastructure.config import Configuracion

BASE = (
    '{"id": "b1", "documento": "base.pdf", "pagina": 1, "texto": "ZORRO: Atuq.", '
    '"tipo": "lexicografico"}\n'
)


@pytest.fixture
def config(tmp_path, monkeypatch):
    base = tmp_path / "base.jsonl"
    base.write_text(BASE, encoding="utf-8")

    def crear(**extra):
        c = Configuracion(
            _env_file=None,
            carpeta_datos=tmp_path / "datos",
            ruta_corpus_base=base,
            ruta_sqlite=tmp_path / "q.db",
            **extra,
        )
        monkeypatch.setattr(modulo, "configuracion", c)
        return c

    return crear


def test_h10_con_el_extractivo_el_estado_no_informa_el_modelo_de_ollama(config):
    config(generador="extractivo")
    estado = modulo.Contenedor(generador="extractivo").estado()
    assert estado["generador"] == "extractivo"
    assert estado["modelo"] == "ninguno (extractivo)"
    assert "qwen" not in estado["modelo"]


def test_h10_con_ollama_el_estado_sigue_informando_su_modelo(config):
    c = config(generador="literal")
    estado = modulo.Contenedor(generador="literal").estado()
    # "literal" es el respaldo sin Ollama: el aviso de la web pide descargar este modelo.
    assert estado["modelo"] == c.ollama_modelo


def test_traductor_por_defecto_es_la_tabla(config):
    config()
    assert isinstance(modulo.Contenedor(generador="literal").traductor, TraductorTabla)


def test_traductor_ollama_se_respeta(config):
    config(traductor="ollama")
    assert isinstance(modulo.Contenedor(generador="literal").traductor, OllamaTraductor)


def test_traductor_desconocido_se_rechaza_al_arrancar():
    with pytest.raises(ValueError):
        Configuracion(_env_file=None, traductor="otro")


def test_h09_el_repositorio_de_fuentes_es_el_de_sqlalchemy_tambien_en_sqlite(config):
    config(base_datos="sqlite")
    assert isinstance(
        modulo.Contenedor(generador="literal").repositorio_fuentes, RepositorioFuentesSqlalchemy
    )


def test_h09_nivel_del_registro_configurable():
    assert Configuracion(_env_file=None).nivel_log == "INFO"
    assert Configuracion(_env_file=None, nivel_log="WARNING").nivel_log == "WARNING"
    with pytest.raises(ValueError):
        Configuracion(_env_file=None, nivel_log="RUIDOSO")


# --- P5 (ronda 2): /api/estado informa el commit desplegado -------------------------------------


def test_p5_en_local_la_version_es_local(config):
    config()
    assert modulo.Contenedor(generador="literal").estado()["version"] == "local"


def test_p5_en_render_la_version_es_el_commit_corto(config):
    config(render_git_commit="4448478a1b2c3d4e5f60718293a4b5c6d7e8f901")
    assert modulo.Contenedor(generador="literal").estado()["version"] == "4448478"


def test_p5_render_git_commit_se_lee_del_entorno(monkeypatch):
    monkeypatch.setenv("RENDER_GIT_COMMIT", "abcdef0123456789")
    assert Configuracion(_env_file=None).version == "abcdef0"


def test_p5_el_esquema_de_estado_publica_la_version():
    # `in` es palabra reservada: el paquete se importa por nombre.
    esquemas = import_module("adapters.in.rest.esquemas")

    assert esquemas.EstadoSistema.model_fields["version"].default == "local"
