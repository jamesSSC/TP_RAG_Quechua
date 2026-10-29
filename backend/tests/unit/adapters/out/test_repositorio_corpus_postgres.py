"""ADR-031 · corpus en la tabla `fragmentos` de PostgreSQL.

Prueba de integracion: necesita un servidor PostgreSQL y se omite si no se define
POSTGRES_PRUEBAS_URL (la CI levanta uno). Nunca apuntarla a la base de Neon: borra las tablas.
"""

import os

import pytest
from sqlalchemy import create_engine, text

from adapters.out.persistencia.modelos import Base
from adapters.out.persistencia.repositorio_corpus_postgres import (
    RepositorioCorpusPostgres,
    instalar_todo,
)
from domain.entities.fragmento import Fragmento, TipoFragmento
from domain.value_objects.procedencia import Procedencia

URL = os.environ.get("POSTGRES_PRUEBAS_URL")
pytestmark = pytest.mark.skipif(not URL, reason="sin POSTGRES_PRUEBAS_URL")


def _f(id_, documento="diccionario.pdf", pagina=1, texto="ZORRO: Atuq.", ocr=False):
    return Fragmento(
        id=id_,
        texto=texto,
        procedencia=Procedencia(documento, pagina, derivado_ocr=ocr),
        tipo=TipoFragmento.LEXICOGRAFICO,
    )


@pytest.fixture
def motor():
    motor = create_engine(URL)
    with motor.begin() as c:
        c.execute(text("DROP TABLE IF EXISTS fragmentos"))
    Base.metadata.drop_all(motor)
    instalar_todo(motor)
    instalar_todo(motor)  # idempotente
    yield motor
    with motor.begin() as c:
        c.execute(text("DROP TABLE IF EXISTS fragmentos"))
    Base.metadata.drop_all(motor)
    motor.dispose()


def test_agrega_sin_duplicar_y_conserva_procedencia_y_orden(motor):
    repo = RepositorioCorpusPostgres(motor)
    assert repo.agregar([_f("b"), _f("a", "gramatica.pdf", 12, "texto", ocr=True)]) == 2
    assert repo.agregar([_f("a"), _f("c")]) == 1
    cargados = repo.cargar()
    assert [f.id for f in cargados] == ["b", "a", "c"]
    a = cargados[1]
    assert (a.procedencia.documento, a.procedencia.pagina, a.procedencia.derivado_ocr) == (
        "gramatica.pdf",
        12,
        True,
    )
    assert repo.documentos() == ["diccionario.pdf", "gramatica.pdf"]
    assert repo.total() == 3


def test_funcion_de_conteo_por_documento(motor):
    RepositorioCorpusPostgres(motor).agregar([_f("x", pagina=1), _f("y", pagina=2)])
    with motor.connect() as c:
        filas = c.execute(text("SELECT * FROM fn_fragmentos_por_documento()")).all()
    assert [tuple(f) for f in filas] == [("diccionario.pdf", 2, 2)]
