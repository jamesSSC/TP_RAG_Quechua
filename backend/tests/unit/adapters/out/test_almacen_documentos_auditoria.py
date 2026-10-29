"""Auditoria PR #4 (M1, M2, M3): nombres, huerfanos y tamano en el almacen."""

import hashlib

import pytest

from adapters.out.documentos import almacen_documentos_disco as modulo
from adapters.out.documentos.almacen_documentos_disco import AlmacenDocumentosDisco
from application.ports.out.almacen_documentos_port import ErrorAlmacenDocumentos


@pytest.fixture
def almacen(tmp_path):
    return AlmacenDocumentosDisco(tmp_path / "documentos")


@pytest.mark.parametrize("nombre", ["uno.PDF", "Uno.Pdf", "a b.pdf"])
def test_acepta_pdf_sin_distinguir_mayusculas(almacen, nombre):
    assert almacen.guardar(b"x" + nombre.encode(), nombre).nombre == nombre


@pytest.mark.parametrize(
    "nombre",
    [
        "texto.txt",
        "sin_extension",
        "manifiesto.json",
        "MANIFIESTO.JSON",
        "",
        "   ",
        "..",
        "../x.pdf",
        "a/../b.pdf",
        "flujo.pdf:oculto",
        "C:evil.pdf",
        "CON.pdf",
        "con.PDF",
        "NUL.pdf",
        "PRN.pdf",
        "AUX.pdf",
        "COM1.pdf",
        "lpt9.pdf",
        "com3.otro.pdf",
        "punto.pdf.",
        "espacio.pdf ",
        ".pdf",
    ],
)
def test_rechaza_nombres_peligrosos(almacen, nombre):
    with pytest.raises(ErrorAlmacenDocumentos):
        almacen.guardar(b"x", nombre)
    assert almacen.listar() == {}


def test_un_error_de_dominio_es_valueerror_para_que_la_api_lo_devuelva_como_4xx():
    assert issubclass(ErrorAlmacenDocumentos, ValueError)


def test_huerfano_con_otro_contenido_no_se_sobrescribe(almacen, tmp_path, caplog):
    carpeta = tmp_path / "documentos"
    carpeta.mkdir()
    (carpeta / "x.pdf").write_bytes(b"huerfano")
    with caplog.at_level("WARNING"):
        r = almacen.guardar(b"nuevo", "x.pdf")
    assert (carpeta / "x.pdf").read_bytes() == b"huerfano"
    assert r.nombre != "x.pdf" and (carpeta / r.nombre).read_bytes() == b"nuevo"
    assert any("huerfano" in m.lower() or "existe" in m.lower() for m in caplog.messages)


def test_huerfano_con_el_mismo_contenido_se_adopta_sin_escribir(almacen, tmp_path):
    carpeta = tmp_path / "documentos"
    carpeta.mkdir()
    (carpeta / "x.pdf").write_bytes(b"igual")
    r = almacen.guardar(b"igual", "x.pdf")
    assert r.nombre == "x.pdf" and r.sha256 == hashlib.sha256(b"igual").hexdigest()
    assert almacen.listar() == {"x.pdf": r.sha256}


def test_si_tambien_el_nombre_con_sufijo_esta_ocupado_se_rechaza(almacen, tmp_path):
    carpeta = tmp_path / "documentos"
    carpeta.mkdir()
    sha = hashlib.sha256(b"nuevo").hexdigest()
    (carpeta / "x.pdf").write_bytes(b"huerfano")
    (carpeta / f"x-{sha[:8]}.pdf").write_bytes(b"otro huerfano")
    with pytest.raises(ErrorAlmacenDocumentos):
        almacen.guardar(b"nuevo", "x.pdf")
    assert (carpeta / "x.pdf").read_bytes() == b"huerfano"


def test_tope_de_tamano_en_el_adaptador(almacen, monkeypatch):
    monkeypatch.setattr(modulo, "TAMANO_MAXIMO", 10)
    almacen.guardar(b"0123456789", "justo.pdf")
    with pytest.raises(ErrorAlmacenDocumentos, match="tamano"):
        almacen.guardar(b"0123456789X", "grande.pdf")


def test_tope_por_defecto_es_60_mb():
    assert modulo.TAMANO_MAXIMO == 60 * 1024 * 1024


def test_errores_de_permisos_salen_como_error_de_dominio(almacen, monkeypatch):
    def denegado(*_a, **_k):
        raise PermissionError("denegado")

    monkeypatch.setattr(modulo.Path, "write_bytes", denegado)
    with pytest.raises(ErrorAlmacenDocumentos, match="permisos"):
        almacen.guardar(b"x", "uno.pdf")
