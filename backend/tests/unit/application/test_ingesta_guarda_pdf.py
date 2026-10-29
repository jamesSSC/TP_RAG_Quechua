import pytest

from application.ports.out.almacen_documentos_port import (
    AlmacenDocumentosPort,
    DocumentoAlmacenado,
)
from application.use_cases.ingestar_documento import IngestarDocumentoUseCase
from domain.entities.fragmento import TipoFragmento
from tests.unit.application.test_ingesta import (
    PAGINA_DICCIONARIO,
    CorpusFalso,
    ExtractorFalso,
    IndiceFalso,
    _documento,
)


class AlmacenFalso(AlmacenDocumentosPort):
    def __init__(self):
        self.guardados = []

    def guardar(self, contenido, nombre):
        self.guardados.append((contenido, nombre))
        return DocumentoAlmacenado(nombre=nombre, sha256="h", duplicado=False)

    def listar(self):
        return {}


def _caso(almacen):
    return IngestarDocumentoUseCase(
        extractor=ExtractorFalso(_documento([(1, PAGINA_DICCIONARIO)])),
        corpus=CorpusFalso(),
        indice=IndiceFalso(),
        almacen_documentos=almacen,
    )


def test_la_ingesta_guarda_el_pdf_original():
    almacen = AlmacenFalso()
    _caso(almacen).ejecutar(b"%PDF", "prueba.pdf", TipoFragmento.LEXICOGRAFICO, "T", "E", "L")
    assert almacen.guardados == [(b"%PDF", "prueba.pdf")]


def test_sin_licenciamiento_no_se_guarda_nada():
    almacen = AlmacenFalso()
    with pytest.raises(ValueError):
        _caso(almacen).ejecutar(b"%PDF", "prueba.pdf", TipoFragmento.LEXICOGRAFICO, "T", "E", " ")
    assert almacen.guardados == []
