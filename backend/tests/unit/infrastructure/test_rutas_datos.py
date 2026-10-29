"""BUG-01: separar los datos de solo lectura (empaquetados) de los modificables."""

import importlib
import sys
from pathlib import Path

import pytest

from infrastructure import config as cfg
from infrastructure.config import Configuracion, resolver_carpeta_datos
from infrastructure.datos import preparar_carpeta_datos

TEXTO = (
    '{"id": "a", "documento": "d.pdf", "pagina": 1, "texto": "ZORRO: Atuq.", '
    '"tipo": "lexicografico"}\n'
)


def test_empaquetado_los_datos_van_junto_al_ejecutable(tmp_path):
    exe = tmp_path / "app"
    meipass = tmp_path / "_MEI123"
    carpeta = resolver_carpeta_datos(True, exe, meipass)
    assert carpeta == exe / "datos"
    assert meipass not in carpeta.parents


def test_desarrollo_los_datos_siguen_en_backend_data(tmp_path):
    assert resolver_carpeta_datos(False, tmp_path, tmp_path) == tmp_path / "data"


def test_configuracion_en_modo_empaquetado_simulado(monkeypatch, tmp_path):
    # El modo empaquetado se decide al importar config: se recarga con sys.frozen falso.
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path / "_MEI9"), raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "exe" / "app.exe"))
    monkeypatch.delenv("CARPETA_DATOS", raising=False)
    try:
        recargado = importlib.reload(cfg)
        c = recargado.Configuracion(_env_file=None)
        assert c.ruta_modelo_cobertura == tmp_path / "_MEI9" / "modelos" / "cobertura.joblib"
        assert c.ruta_tabla_traduccion.parent == tmp_path / "_MEI9" / "data"
        assert c.ruta_corpus_base == tmp_path / "_MEI9" / "data" / "fragmentos_v3.jsonl"
        assert c.carpeta_datos == tmp_path / "exe" / "datos"
        assert c.ruta_corpus == tmp_path / "exe" / "datos" / "fragmentos_v3.jsonl"
        assert c.ruta_documentos == tmp_path / "exe" / "datos" / "documentos"
        assert c.ruta_sqlite == tmp_path / "exe" / "quechua_wanka.db"
    finally:
        monkeypatch.undo()
        importlib.reload(cfg)


def test_carpeta_datos_configurable_por_entorno(monkeypatch, tmp_path):
    monkeypatch.setenv("CARPETA_DATOS", str(tmp_path / "otra"))
    c = Configuracion(_env_file=None)
    assert c.carpeta_datos == tmp_path / "otra"
    assert c.ruta_corpus == tmp_path / "otra" / "fragmentos_v3.jsonl"


def test_ruta_corpus_explicita_tiene_prioridad(tmp_path):
    c = Configuracion(_env_file=None, carpeta_datos=tmp_path, ruta_corpus=tmp_path / "x.jsonl")
    assert c.ruta_corpus == tmp_path / "x.jsonl"


def test_en_desarrollo_el_corpus_sigue_en_backend_data(monkeypatch):
    monkeypatch.delenv("CARPETA_DATOS", raising=False)
    c = Configuracion(_env_file=None)
    assert c.ruta_corpus == c.ruta_corpus_base


def test_primer_arranque_copia_el_corpus_base_sin_tocarlo(tmp_path):
    base = tmp_path / "paquete" / "fragmentos_v3.jsonl"
    base.parent.mkdir()
    base.write_text(TEXTO, encoding="utf-8")
    destino = tmp_path / "datos" / "fragmentos_v3.jsonl"

    assert preparar_carpeta_datos(destino.parent, base, destino) is True

    assert destino.read_text(encoding="utf-8") == TEXTO
    assert (destino.parent / "documentos").is_dir()
    assert base.read_text(encoding="utf-8") == TEXTO


def test_si_la_copia_ya_existe_no_se_sobrescribe(tmp_path):
    base = tmp_path / "base.jsonl"
    base.write_text(TEXTO, encoding="utf-8")
    destino = tmp_path / "datos" / "fragmentos_v3.jsonl"
    destino.parent.mkdir()
    destino.write_text(TEXTO + TEXTO, encoding="utf-8")

    assert preparar_carpeta_datos(destino.parent, base, destino) is False
    assert destino.read_text(encoding="utf-8") == TEXTO + TEXTO


def test_en_desarrollo_base_y_destino_coinciden_y_no_se_copia(tmp_path):
    ruta = tmp_path / "data" / "fragmentos_v3.jsonl"
    ruta.parent.mkdir()
    ruta.write_text(TEXTO, encoding="utf-8")
    assert preparar_carpeta_datos(ruta.parent, ruta, ruta) is False


def test_sin_corpus_base_no_falla(tmp_path):
    destino = tmp_path / "datos" / "f.jsonl"
    assert preparar_carpeta_datos(destino.parent, tmp_path / "no.jsonl", destino) is False
    assert not destino.exists()


@pytest.mark.parametrize("modo", [True, False])
def test_resolver_devuelve_path(modo, tmp_path):
    assert isinstance(resolver_carpeta_datos(modo, tmp_path, tmp_path), Path)
