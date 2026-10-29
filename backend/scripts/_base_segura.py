"""Red de seguridad: ningun script de medicion o de carga escribe en la base real.

La base real es `backend/quechua_wanka.db` (SQLite de uso) y `quechua_wanka` (PostgreSQL). Los
scripts usan `backend/carga.db`, una base temporal o una base de demostracion explicita."""

import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE_REAL_SQLITE = RAIZ / "quechua_wanka.db"
BASE_REAL_POSTGRES = "quechua_wanka"


def fijar_base_por_defecto(nombre: str = "carga.db") -> None:
    """Si nadie fijo RUTA_SQLITE, usa una base aparte (nunca la real). Llamar ANTES de importar
    infrastructure.config."""
    if not os.environ.get("RUTA_SQLITE"):
        os.environ["RUTA_SQLITE"] = str(RAIZ / nombre)


def base_temporal(prefijo: str = "qw_") -> Path:
    return Path(tempfile.mkdtemp(prefix=prefijo)) / "temporal.db"


def verificar(configuracion) -> None:
    """Aborta si la configuracion resuelta apunta a la base real."""
    if configuracion.base_datos == "sqlite":
        if Path(configuracion.ruta_sqlite).resolve() == BASE_REAL_SQLITE.resolve():
            sys.exit(
                f"ABORTADO: {configuracion.ruta_sqlite} es la base real. Use otra con RUTA_SQLITE."
            )
    elif configuracion.postgres_db == BASE_REAL_POSTGRES:
        sys.exit(
            "ABORTADO: la base PostgreSQL resuelta es la real. Use POSTGRES_DB=quechua_wanka_demo."
        )
