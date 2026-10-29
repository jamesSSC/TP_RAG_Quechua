"""Red de seguridad global: ninguna prueba escribe en la base real (backend/quechua_wanka.db)."""

import sys

import pytest


@pytest.fixture(autouse=True)
def _base_de_datos_en_tmp(tmp_path, monkeypatch):
    base = tmp_path / "pruebas_quechua_wanka.db"
    # Para configuraciones que se crean dentro de la prueba...
    monkeypatch.setenv("RUTA_SQLITE", str(base))
    # ...y para cada copia del singleton `configuracion` ya importada (config, contenedor, main;
    # una prueba que recarga el modulo deja dos instancias).
    for modulo in list(sys.modules.values()):
        objeto = getattr(modulo, "configuracion", None)
        if objeto is not None and hasattr(objeto, "ruta_sqlite"):
            monkeypatch.setattr(objeto, "ruta_sqlite", base)
