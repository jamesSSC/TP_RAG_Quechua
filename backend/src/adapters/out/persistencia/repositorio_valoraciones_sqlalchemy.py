from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from adapters.out.persistencia.modelos import ConsultaORM, ValoracionORM
from application.ports.out.repositorio_valoraciones_port import RepositorioValoracionesPort


class RepositorioValoracionesSqlalchemy(RepositorioValoracionesPort):
    """REF-07 (ADR-040). Mismo adaptador para SQLite y PostgreSQL: es una tabla nueva con una
    sola fila por consulta (la clave primaria es el id de la consulta)."""

    def __init__(self, sesion):
        self._sesion = sesion

    def existe_consulta(self, consulta_id: str) -> bool:
        with self._sesion() as s:
            return s.get(ConsultaORM, consulta_id) is not None

    def registrar(self, consulta_id: str, util: bool, momento: datetime) -> bool:
        with self._sesion() as s:
            s.add(ValoracionORM(consulta_id=consulta_id, util=util, momento=momento))
            try:
                s.commit()
            except IntegrityError:
                s.rollback()
                return False
        return True

    def resumen(self) -> dict[str, int]:
        with self._sesion() as s:
            filas = s.execute(
                select(ValoracionORM.util, func.count()).group_by(ValoracionORM.util)
            ).all()
        conteo = {bool(util): n for util, n in filas}
        return {"util": conteo.get(True, 0), "no_util": conteo.get(False, 0)}
