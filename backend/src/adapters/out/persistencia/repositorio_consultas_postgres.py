"""Historial de consultas sobre PostgreSQL mediante procedimientos almacenados.

Mismo puerto (RepositorioConsultasPort) y mismos modelos que el repositorio SQLAlchemy; lo
que cambia es que la escritura, el borrado y los agregados de la analitica se delegan en
procedimientos y funciones del servidor (db/postgres/procedimientos.sql). SQLite no admite
procedimientos almacenados, por eso es un adaptador aparte y no un parametro.
"""

import json
import logging
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from adapters.out.persistencia.repositorio_consultas_sqlalchemy import (
    RepositorioConsultasSqlAlchemy,
)
from domain.entities.consulta import Consulta
from domain.entities.respuesta import Respuesta

log = logging.getLogger("rag.repositorio")

SCRIPT = Path(__file__).resolve().parents[4] / "db" / "postgres" / "procedimientos.sql"


def instalar_procedimientos(motor: Engine, script: Path = SCRIPT) -> None:
    """Crea o reemplaza los procedimientos. Idempotente: se ejecuta en cada arranque."""
    # Se envia por la conexion del controlador y sin parametros: el script contiene '%' en
    # los mensajes de RAISE, que la capa de parametros interpretaria como marcadores.
    with motor.begin() as conexion:
        conexion.connection.driver_connection.execute(script.read_text(encoding="utf-8"))
    log.info("[REPOSITORIO] procedimientos almacenados instalados (%s)", script.name)


class RepositorioConsultasPostgres(RepositorioConsultasSqlAlchemy):
    def registrar(self, consulta: Consulta, respuesta: Respuesta) -> None:
        respaldos = [
            {
                "fragmento_id": r.id,
                "documento": r.procedencia.documento,
                "pagina": r.procedencia.pagina,
                "texto": r.texto,
                "puntuacion": r.puntuacion.valor,
                "derivado_ocr": r.procedencia.derivado_ocr,
            }
            for r in respuesta.respaldo
        ]
        with self._sesion() as s, s.begin():
            s.execute(
                text(
                    "CALL sp_registrar_consulta(:id, :texto, :idioma, :traducido, :momento, "
                    ":respuesta, :abstenida, :similitud, :via, :p_cob, :p_pas, :abst_pred, "
                    ":pasajes, :latencia, CAST(:respaldos AS JSONB))"
                ),
                {
                    "id": consulta.id,
                    "texto": consulta.texto,
                    "idioma": consulta.idioma.value,
                    "traducido": consulta.texto_traducido,
                    "momento": consulta.momento,
                    "respuesta": respuesta.texto,
                    "abstenida": respuesta.abstenida,
                    "similitud": respuesta.similitud_maxima,
                    "via": respuesta.via_respaldo,
                    "p_cob": respuesta.probabilidad_cobertura,
                    "p_pas": respuesta.probabilidad_pasajes,
                    "abst_pred": respuesta.abstencion_por_predictor,
                    "pasajes": len(respuesta.pasajes),
                    "latencia": respuesta.latencia_ms,
                    "respaldos": json.dumps(respaldos, ensure_ascii=False),
                },
            )

    def borrar_todo(self) -> int:
        with self._sesion() as s, s.begin():
            borradas = s.execute(text("CALL sp_borrar_historial(0)")).scalar() or 0
        log.info("[REPOSITORIO] historial borrado por procedimiento (%d consultas)", borradas)
        return int(borradas)

    def estadisticas(self) -> dict:
        base = super().estadisticas()
        with self._sesion() as s:
            fila = s.execute(text("SELECT * FROM fn_resumen_demanda()")).mappings().one()
            documentos = s.execute(text("SELECT * FROM fn_respaldo_por_documento()")).all()
        base.update(
            {
                "total": int(fila["total"]),
                "abstenidas": int(fila["abstenidas"]),
                "abstenciones_por_predictor": int(fila["abstenciones_por_predictor"]),
                "probabilidad_cobertura_media": fila["probabilidad_cobertura_media"],
                "latencia_media_ms": fila["latencia_media_ms"],
                "latencia_p95_ms": fila["latencia_p95_ms"],
                "respaldo_por_documento": {d: int(n) for d, n in documentos},
                "origen": "procedimientos almacenados",
            }
        )
        return base

    def abstenciones_con_prediccion(self, limite: int = 5000) -> list[tuple[str, float | None]]:
        with self._sesion() as s:
            return [
                (t, p)
                for t, p in s.execute(
                    text("SELECT * FROM fn_demanda_insatisfecha(:limite)"), {"limite": limite}
                ).all()
            ]
