"""Corpus segmentado en PostgreSQL (nube, ADR-031).

Mismo puerto que el archivo JSONL (RepositorioCorpusPort): el indice se reconstruye desde la
tabla `fragmentos` en lugar de desde el disco. En Render el disco es efimero, de modo que lo
que se incorpora en la nube (HU-02) solo sobrevive a un redespliegue si queda en la base.
"""

import logging
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from adapters.out.persistencia.modelos import Base
from adapters.out.persistencia.repositorio_consultas_postgres import instalar_procedimientos
from application.ports.out.repositorio_corpus_port import RepositorioCorpusPort
from domain.entities.fragmento import Fragmento, TipoFragmento
from domain.value_objects.procedencia import Procedencia

log = logging.getLogger("rag.repositorio")

ESQUEMA = Path(__file__).resolve().parents[4] / "db" / "postgres" / "esquema.sql"

INSERTAR = text(
    "INSERT INTO fragmentos (id, documento, pagina, texto, tipo, derivado_ocr) "
    "VALUES (:id, :documento, :pagina, :texto, :tipo, :derivado_ocr) "
    "ON CONFLICT (id) DO NOTHING"
)


def instalar_esquema(motor: Engine, esquema: Path = ESQUEMA) -> None:
    """Tabla `fragmentos` y su funcion de conteo. Idempotente: se aplica en cada arranque."""
    with motor.begin() as conexion:
        conexion.connection.driver_connection.execute(esquema.read_text(encoding="utf-8"))
    log.info("[REPOSITORIO] esquema instalado (%s)", esquema.name)


def instalar_todo(motor: Engine) -> None:
    """Lo que hace el contenedor al arrancar con PostgreSQL, para el seeding: tablas de los
    modelos, esquema del corpus y procedimientos, en ese orden."""
    Base.metadata.create_all(motor)
    instalar_esquema(motor)
    instalar_procedimientos(motor)


class RepositorioCorpusPostgres(RepositorioCorpusPort):
    def __init__(self, motor: Engine):
        self._motor = motor

    def cargar(self) -> list[Fragmento]:
        with self._motor.connect() as conexion:
            filas = conexion.execute(
                text(
                    "SELECT id, documento, pagina, texto, tipo, derivado_ocr "
                    "FROM fragmentos ORDER BY orden"
                )
            ).all()
        return [
            Fragmento(
                id=f.id,
                texto=f.texto,
                procedencia=Procedencia(
                    documento=f.documento, pagina=int(f.pagina), derivado_ocr=bool(f.derivado_ocr)
                ),
                tipo=TipoFragmento(f.tipo),
            )
            for f in filas
        ]

    def agregar(self, fragmentos: list[Fragmento]) -> int:
        if not fragmentos:
            return 0
        filas = [
            {
                "id": f.id,
                "documento": f.procedencia.documento,
                "pagina": f.procedencia.pagina,
                "texto": f.texto,
                "tipo": f.tipo.value,
                "derivado_ocr": f.procedencia.derivado_ocr,
            }
            for f in fragmentos
        ]
        with self._motor.begin() as conexion:
            antes = conexion.execute(text("SELECT COUNT(*) FROM fragmentos")).scalar_one()
            conexion.execute(INSERTAR, filas)
            despues = conexion.execute(text("SELECT COUNT(*) FROM fragmentos")).scalar_one()
        return int(despues - antes)

    def documentos(self) -> list[str]:
        with self._motor.connect() as conexion:
            return [
                d for (d,) in conexion.execute(
                    text("SELECT DISTINCT documento FROM fragmentos ORDER BY documento")
                )
            ]

    def total(self) -> int:
        with self._motor.connect() as conexion:
            return int(conexion.execute(text("SELECT COUNT(*) FROM fragmentos")).scalar_one())
