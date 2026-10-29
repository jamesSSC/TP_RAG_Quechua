from datetime import date

from application.ports.out.almacen_documentos_port import (
    AlmacenDocumentosPort,
    DocumentoAlmacenado,
)
from application.ports.out.repositorio_corpus_port import RepositorioCorpusPort
from application.ports.out.repositorio_fuentes_port import RepositorioFuentesPort
from application.use_cases.verificar_consistencia_datos import VerificarConsistenciaDatos
from domain.entities.fuente import Fuente


class Corpus(RepositorioCorpusPort):
    def __init__(self, docs):
        self._docs = docs

    def cargar(self):
        return []

    def agregar(self, fragmentos):
        return 0

    def documentos(self):
        return self._docs


class Fuentes(RepositorioFuentesPort):
    def __init__(self, nombres):
        self._f = [Fuente("t", "e", "l", date.today(), n) for n in nombres]

    def crear(self, fuente):
        return fuente

    def obtener(self, fuente_id):
        return None

    def listar(self):
        return self._f

    def actualizar(self, fuente):
        return fuente

    def eliminar(self, fuente_id):
        return False


class Almacen(AlmacenDocumentosPort):
    def __init__(self, nombres):
        self._n = {n: "h" for n in nombres}

    def guardar(self, contenido, nombre) -> DocumentoAlmacenado:
        raise NotImplementedError

    def listar(self):
        return dict(self._n)


def _verificar(docs, fuentes, pdfs):
    return VerificarConsistenciaDatos(Corpus(docs), Fuentes(fuentes), Almacen(pdfs)).ejecutar()


def test_todo_consistente_no_da_avisos():
    assert _verificar(["a.pdf"], ["a.pdf"], ["a.pdf"]) == []


def test_corpus_base_sin_fuente_ni_pdf_no_es_discrepancia():
    assert _verificar(["base.pdf", "a.pdf"], ["a.pdf"], ["a.pdf"]) == []


def test_fuente_sin_fragmentos_se_avisa():
    avisos = _verificar([], ["a.pdf"], ["a.pdf"])
    assert any("a.pdf" in a and "fragmentos" in a for a in avisos)


def test_fuente_sin_pdf_guardado_se_avisa():
    avisos = _verificar(["a.pdf"], ["a.pdf"], [])
    assert any("a.pdf" in a and "PDF" in a for a in avisos)


def test_pdf_guardado_sin_fragmentos_se_avisa():
    avisos = _verificar([], [], ["z.pdf"])
    assert any("z.pdf" in a and "fragmentos" in a for a in avisos)


def test_pdf_guardado_sin_fuente_se_avisa():
    avisos = _verificar(["z.pdf"], [], ["z.pdf"])
    assert any("z.pdf" in a and "fuente" in a for a in avisos)


def test_sin_fuentes_ni_almacen_no_falla():
    assert VerificarConsistenciaDatos(Corpus(["a.pdf"]), None, None).ejecutar() == []
