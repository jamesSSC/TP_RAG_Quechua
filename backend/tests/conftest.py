import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from adapters.out.documentos.corpus_jsonl import cargar_fragmentos  # noqa: E402
from adapters.out.recuperacion.indice_hibrido_lexico import (  # noqa: E402
    IndiceHibridoLexico,
)

DATOS = RAIZ / "data"
# Datos fuera de Git (ADR-015). En la CI no estan: las pruebas que los necesitan se omiten.
CORPUS_V2 = DATOS / "fragmentos_v2.jsonl"
CORPUS_V3 = DATOS / "fragmentos_v3.jsonl"


def pytest_collection_modifyitems(config, items):
    if CORPUS_V3.exists():
        return
    omitir = pytest.mark.skip(reason="sin backend/data/fragmentos_v3.jsonl (fuera de Git)")
    for item in items:
        if "datos" in item.keywords:
            item.add_marker(omitir)


@pytest.fixture(scope="session")
def fragmentos():
    if not CORPUS_V2.exists():
        pytest.skip("sin backend/data/fragmentos_v2.jsonl (fuera de Git)")
    return cargar_fragmentos(CORPUS_V2)


@pytest.fixture(scope="session")
def indice(fragmentos):
    idx = IndiceHibridoLexico()
    idx.indexar(fragmentos)
    return idx


@pytest.fixture(scope="session")
def evaluacion():
    return json.loads((DATOS / "evaluacion_v2.json").read_text(encoding="utf-8"))
