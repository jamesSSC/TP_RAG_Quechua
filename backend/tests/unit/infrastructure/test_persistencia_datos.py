"""BUG-01: un PDF incorporado sobrevive al cierre y reapertura (dos contenedores)."""

import json

import pytest

import infrastructure.contenedor as modulo
from application.ports.out.extraccion_documental_port import (
    DocumentoExtraido,
    ExtraccionDocumentalPort,
    PaginaExtraida,
)
from domain.entities.fragmento import TipoFragmento
from infrastructure.config import Configuracion

# Fragmento real del diccionario (pag. 37) usado como contenido del documento de prueba.
PAGINA = "ZORRO: Atuq.\n"
BASE = {
    "id": "base-1",
    "documento": "base.pdf",
    "pagina": 1,
    "texto": "CONFESAR: Kunfisay.",
    "tipo": "lexicografico",
}


class ExtractorFalso(ExtraccionDocumentalPort):
    def extraer(self, contenido, nombre_archivo):
        return DocumentoExtraido(nombre_archivo, [PaginaExtraida(37, PAGINA)])


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    paquete = tmp_path / "paquete"
    paquete.mkdir()
    base = paquete / "fragmentos_v3.jsonl"
    base.write_text(json.dumps(BASE, ensure_ascii=False) + "\n", encoding="utf-8")
    datos = tmp_path / "datos"
    config = Configuracion(
        _env_file=None,
        carpeta_datos=datos,
        ruta_corpus_base=base,
        ruta_sqlite=tmp_path / "q.db",
    )
    monkeypatch.setattr(modulo, "configuracion", config)
    return config, base


def _abrir():
    c = modulo.Contenedor(generador="literal")
    c.ingestar_documento._extractor = ExtractorFalso()
    return c


def test_el_documento_incorporado_sigue_tras_reiniciar(entorno):
    config, base = entorno
    primero = _abrir()
    assert (config.carpeta_datos / "fragmentos_v3.jsonl").exists()
    primero.ingestar_documento.ejecutar(
        b"%PDF-falso", "nuevo.pdf", TipoFragmento.LEXICOGRAFICO, "T", "E", "L"
    )
    assert primero.estado()["fragmentos_indexados"] == 2

    segundo = _abrir()  # "reinicio" sobre la misma carpeta de datos
    assert segundo.estado()["fragmentos_indexados"] == 2
    assert "nuevo.pdf" in segundo.corpus.documentos()
    resultado = segundo.indice.recuperar("zorro", 1)[0]
    assert resultado.fragmento.procedencia.documento == "nuevo.pdf"
    assert (config.ruta_documentos / "nuevo.pdf").read_bytes() == b"%PDF-falso"
    # El corpus empaquetado de solo lectura no se modifica.
    assert len(base.read_text(encoding="utf-8").splitlines()) == 1


def test_estado_informa_consistencia_sin_borrar_nada(entorno):
    config, _ = entorno
    primero = _abrir()
    primero.ingestar_documento.ejecutar(
        b"%PDF-falso", "nuevo.pdf", TipoFragmento.LEXICOGRAFICO, "T", "E", "L"
    )
    assert _abrir().estado()["consistencia"] == {"estado": "ok", "avisos": []}

    # Se pierde el PDF guardado: la discrepancia se avisa y no se toca el resto.
    (config.ruta_documentos / "nuevo.pdf").unlink()
    estado = _abrir().estado()["consistencia"]
    assert estado["estado"] == "avisos"
    assert any("nuevo.pdf" in a for a in estado["avisos"])
    assert "nuevo.pdf" in _abrir().corpus.documentos()
