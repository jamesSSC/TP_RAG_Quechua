"""H-02 · Recuperacion real en un clon limpio, sin el corpus completo.

El corpus procesado no se versiona (ADR-015), asi que las pruebas que lo necesitan se omiten en
la CI y nada comprobaba alli la recuperacion de verdad. `data/corpus_minimo.jsonl` son 295
fragmentos literales del corpus (los oro de las 20 primeras consultas de A, las entradas de los
ejemplos de la interfaz, el pasaje del ablativo y uno de cada 15 del resto como distractores).
No contiene ninguna forma escrita a mano. Se reconstruye con `scripts/reconstruir_corpus.py`.

Con el mismo indice y el mismo umbral que el sistema (tau = 0,48) se exige:
- las 20 consultas de A: el fragmento oro entre los 5 primeros y respuesta con respaldo;
- las 28 consultas de C (fuera de cobertura): abstencion, 0 falsos positivos.
"""

import json
from pathlib import Path

import pytest

from adapters.out.documentos.corpus_jsonl import cargar_fragmentos
from adapters.out.recuperacion.indice_hibrido_lexico import IndiceHibridoLexico
from domain.services.evaluador_confianza import EvaluadorConfianza

DATOS = Path(__file__).resolve().parents[2] / "data"
TAU = 0.48


@pytest.fixture(scope="module")
def indice():
    idx = IndiceHibridoLexico()
    total = idx.indexar(cargar_fragmentos(DATOS / "corpus_minimo.jsonl"))
    assert total == 295
    return idx


@pytest.fixture(scope="module")
def evaluacion():
    return json.loads((DATOS / "evaluacion_v2.json").read_text(encoding="utf-8"))


@pytest.mark.salvaguarda
def test_a_recupera_el_oro_y_responde(indice, evaluacion):
    evaluador = EvaluadorConfianza(umbral=TAU)
    casos = [e for e in evaluacion if e["subconjunto"] == "A_lexico_es"][:20]
    for caso in casos:
        recuperados = indice.recuperar(caso["consulta"], k=5)
        assert set(caso["oro"]) & {r.id for r in recuperados}, caso["id"]
        assert evaluador.evaluar(recuperados).responder, caso["id"]


@pytest.mark.salvaguarda
def test_c_fuera_de_cobertura_se_abstiene_siempre(indice, evaluacion):
    evaluador = EvaluadorConfianza(umbral=TAU)
    casos = [e for e in evaluacion if e["subconjunto"].startswith("C")]
    assert len(casos) == 28
    falsos_positivos = [
        c["id"] for c in casos if evaluador.evaluar(indice.recuperar(c["consulta"], k=5)).responder
    ]
    assert falsos_positivos == []


def test_zorro_cita_el_diccionario_pagina_37(indice):
    primero = indice.recuperar("¿cómo se dice zorro en quechua wanka?", k=5)[0]
    assert primero.texto == "ZORRO: Atuq."
    assert primero.procedencia.pagina == 37
