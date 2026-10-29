import hashlib

from adapters.out.documentos.almacen_documentos_disco import AlmacenDocumentosDisco


def test_guarda_el_pdf_con_su_sha256(tmp_path):
    almacen = AlmacenDocumentosDisco(tmp_path / "documentos")
    r = almacen.guardar(b"%PDF-contenido", "uno.pdf")
    assert r.sha256 == hashlib.sha256(b"%PDF-contenido").hexdigest()
    assert r.duplicado is False
    assert (tmp_path / "documentos" / "uno.pdf").read_bytes() == b"%PDF-contenido"
    assert almacen.listar() == {"uno.pdf": r.sha256}


def test_el_mismo_hash_no_se_duplica_ni_con_otro_nombre(tmp_path):
    almacen = AlmacenDocumentosDisco(tmp_path / "documentos")
    almacen.guardar(b"abc", "uno.pdf")
    r = almacen.guardar(b"abc", "otro.pdf")
    assert r.duplicado is True
    assert r.nombre == "uno.pdf"
    assert sorted(p.name for p in (tmp_path / "documentos").glob("*.pdf")) == ["uno.pdf"]


def test_mismo_nombre_con_otro_contenido_no_pisa_el_anterior(tmp_path):
    almacen = AlmacenDocumentosDisco(tmp_path / "documentos")
    a = almacen.guardar(b"uno", "x.pdf")
    b = almacen.guardar(b"dos", "x.pdf")
    assert b.nombre != "x.pdf"
    assert (tmp_path / "documentos" / "x.pdf").read_bytes() == b"uno"
    assert len(almacen.listar()) == 2 and a.sha256 != b.sha256


def test_el_manifiesto_sobrevive_a_un_reinicio(tmp_path):
    AlmacenDocumentosDisco(tmp_path / "d").guardar(b"abc", "uno.pdf")
    assert "uno.pdf" in AlmacenDocumentosDisco(tmp_path / "d").listar()
