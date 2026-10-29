"""Prueba de arquitectura hexagonal (CONSIDERACIONES.md 4.2): el nucleo no conoce la tecnologia."""

import ast
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"
TECNOLOGIA = ("sqlalchemy", "psycopg", "psycopg2", "asyncpg", "sqlite3", "fastapi", "starlette")
CAPAS_EXTERNAS = ("adapters", "infrastructure")


def _importaciones(carpeta: Path):
    for archivo in sorted(carpeta.rglob("*.py")):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    yield archivo, alias.name
            elif isinstance(nodo, ast.ImportFrom) and nodo.level == 0:
                yield archivo, nodo.module or ""
        # Las importaciones dinamicas tambien cuentan (ports/__init__ usa import_module).
        for nodo in ast.walk(arbol):
            if (
                isinstance(nodo, ast.Call)
                and getattr(nodo.func, "id", getattr(nodo.func, "attr", "")) == "import_module"
                and nodo.args
                and isinstance(nodo.args[0], ast.Constant)
                and isinstance(nodo.args[0].value, str)
            ):
                yield archivo, nodo.args[0].value


def _raiz(modulo: str) -> str:
    return modulo.split(".")[0]


def test_el_dominio_solo_usa_la_biblioteca_estandar():
    propios = {"domain"}
    for archivo, modulo in _importaciones(SRC / "domain"):
        raiz = _raiz(modulo)
        assert raiz in sys.stdlib_module_names or raiz in propios, (archivo.name, modulo)


def test_la_aplicacion_no_importa_adaptadores_ni_infraestructura():
    for archivo, modulo in _importaciones(SRC / "application"):
        assert _raiz(modulo) not in CAPAS_EXTERNAS, (archivo.name, modulo)


def test_dominio_y_aplicacion_no_conocen_postgresql_ni_sqlalchemy():
    for capa in ("domain", "application"):
        for archivo, modulo in _importaciones(SRC / capa):
            assert _raiz(modulo) not in TECNOLOGIA, (capa, archivo.name, modulo)
            assert "postgres" not in modulo.lower(), (capa, archivo.name, modulo)


def test_el_codigo_del_dominio_y_la_aplicacion_no_nombra_postgres():
    """Ni siquiera como cadena: los procedimientos almacenados son un detalle del adaptador."""
    for capa in ("domain", "application"):
        for archivo in sorted((SRC / capa).rglob("*.py")):
            texto = archivo.read_text(encoding="utf-8").lower()
            assert "postgres" not in texto, (capa, archivo.name)
