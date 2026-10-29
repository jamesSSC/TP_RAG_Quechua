"""Recrea la base de demostracion de PostgreSQL (`quechua_wanka_demo`), vacia.

Nunca toca otra base: el nombre esta fijo. Las credenciales salen de backend/.env o de las
variables POSTGRES_*; no se imprimen. Los procedimientos almacenados los instala el contenedor
al arrancar con BASE_DATOS=postgres.

Uso, desde backend/:  python scripts/preparar_base_demo_postgres.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import create_engine, text  # noqa: E402

from infrastructure.config import configuracion  # noqa: E402

BASE_DEMO = "quechua_wanka_demo"


def main() -> int:
    c = configuracion
    url = (
        f"postgresql+psycopg://{c.postgres_user}:{c.postgres_password}"
        f"@{c.postgres_host}:{c.postgres_port}/postgres"
    )
    motor = create_engine(url, isolation_level="AUTOCOMMIT")
    with motor.connect() as conexion:
        conexion.execute(text(f"DROP DATABASE IF EXISTS {BASE_DEMO} WITH (FORCE)"))
        conexion.execute(text(f"CREATE DATABASE {BASE_DEMO}"))
    print(f"[PG] base de demostracion {BASE_DEMO} recreada en {c.postgres_host}:{c.postgres_port}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
