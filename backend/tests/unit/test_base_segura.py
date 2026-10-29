"""Red de seguridad: ni las pruebas ni los scripts escriben en la base real."""

import importlib.util
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("_base_segura", RAIZ / "scripts" / "_base_segura.py")
seguro = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = seguro
spec.loader.exec_module(seguro)


def test_el_conftest_apunta_la_base_a_tmp_en_cada_prueba(tmp_path):
    from infrastructure.config import configuracion

    assert Path(configuracion.ruta_sqlite).parent == tmp_path
    assert Path(os.environ["RUTA_SQLITE"]).parent == tmp_path
    assert Path(configuracion.ruta_sqlite).resolve() != (RAIZ / "quechua_wanka.db").resolve()


def test_una_configuracion_nueva_tampoco_apunta_a_la_base_real(tmp_path):
    from infrastructure.config import Configuracion

    assert Path(Configuracion(_env_file=None).ruta_sqlite).parent == tmp_path


def test_verificar_aborta_si_la_base_sqlite_es_la_real():
    real = SimpleNamespace(base_datos="sqlite", ruta_sqlite=RAIZ / "quechua_wanka.db")
    with pytest.raises(SystemExit, match="base real"):
        seguro.verificar(real)


def test_verificar_acepta_carga_db_y_bases_temporales(tmp_path):
    seguro.verificar(SimpleNamespace(base_datos="sqlite", ruta_sqlite=RAIZ / "carga.db"))
    seguro.verificar(SimpleNamespace(base_datos="sqlite", ruta_sqlite=tmp_path / "x.db"))


def test_verificar_aborta_con_la_base_postgres_real():
    with pytest.raises(SystemExit):
        seguro.verificar(SimpleNamespace(base_datos="postgres", postgres_db="quechua_wanka"))
    seguro.verificar(SimpleNamespace(base_datos="postgres", postgres_db="quechua_wanka_demo"))


def test_sin_ruta_explicita_los_scripts_usan_carga_db(monkeypatch):
    monkeypatch.delenv("RUTA_SQLITE", raising=False)
    seguro.fijar_base_por_defecto()
    assert Path(os.environ["RUTA_SQLITE"]) == RAIZ / "carga.db"


def test_una_ruta_explicita_se_respeta(monkeypatch, tmp_path):
    monkeypatch.setenv("RUTA_SQLITE", str(tmp_path / "mia.db"))
    seguro.fijar_base_por_defecto()
    assert Path(os.environ["RUTA_SQLITE"]) == tmp_path / "mia.db"
