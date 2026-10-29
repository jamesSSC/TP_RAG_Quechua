import logging

from sqlalchemy import case, func, select, true
from sqlalchemy.orm import Session, sessionmaker

from adapters.out.persistencia.modelos import ConsultaORM, RespaldoORM
from application.ports.out.repositorio_consultas_port import RepositorioConsultasPort
from domain.entities.consulta import Consulta
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.entities.respuesta import Respuesta
from domain.value_objects.idioma import Idioma
from domain.value_objects.origen_consulta import OrigenConsulta
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud

log = logging.getLogger("rag.repositorio")


class RepositorioConsultasSqlAlchemy(RepositorioConsultasPort):
    """Historial de consultas (RF-11) sobre SQLAlchemy: sirve a SQLite (defecto) y a PostgreSQL.

    Guarda el texto de la consulta, la decision, la via de respaldo, la similitud, el
    documento y la pagina, y la fecha. No guarda IP, usuario ni user-agent."""

    def __init__(self, sesion: sessionmaker[Session]):
        self._sesion = sesion

    def registrar(self, consulta: Consulta, respuesta: Respuesta) -> None:
        with self._sesion() as s, s.begin():
            s.add(
                ConsultaORM(
                    id=consulta.id,
                    texto=consulta.texto,
                    idioma=consulta.idioma.value,
                    texto_traducido=consulta.texto_traducido,
                    momento=consulta.momento,
                    respuesta_texto=respuesta.texto,
                    abstenida=respuesta.abstenida,
                    similitud_maxima=respuesta.similitud_maxima,
                    via_respaldo=respuesta.via_respaldo,
                    probabilidad_cobertura=respuesta.probabilidad_cobertura,
                    probabilidad_pasajes=respuesta.probabilidad_pasajes,
                    abstencion_por_predictor=respuesta.abstencion_por_predictor,
                    pasajes_ofrecidos=len(respuesta.pasajes),
                    latencia_ms=respuesta.latencia_ms,
                    origen=consulta.origen.value,
                    respaldos=[
                        RespaldoORM(
                            fragmento_id=r.id,
                            documento=r.procedencia.documento,
                            pagina=r.procedencia.pagina,
                            texto=r.texto,
                            puntuacion=r.puntuacion.valor,
                            derivado_ocr=r.procedencia.derivado_ocr,
                        )
                        for r in respuesta.respaldo
                    ],
                )
            )

    def historial(self, limite: int = 50) -> list[tuple[Consulta, Respuesta]]:
        with self._sesion() as s:
            registros = s.scalars(
                select(ConsultaORM).order_by(ConsultaORM.momento.desc()).limit(limite)
            ).all()
            return [self._a_dominio(r) for r in registros]

    def borrar_todo(self) -> int:
        with self._sesion() as s, s.begin():
            registros = s.scalars(select(ConsultaORM)).all()
            for registro in registros:
                s.delete(registro)  # los respaldos caen en cascada
            borradas = len(registros)
        log.info("[REPOSITORIO] historial borrado (%d consultas)", borradas)
        return borradas

    def no_cubiertas(self, limite: int = 500) -> list[Consulta]:
        with self._sesion() as s:
            registros = s.scalars(
                select(ConsultaORM)
                .where(ConsultaORM.abstenida.is_(True))
                .order_by(ConsultaORM.momento.desc())
                .limit(limite)
            ).all()
            return [self._a_dominio(r)[0] for r in registros]

    @staticmethod
    def _solo_reales(incluir_sinteticas: bool):
        """Filtro de origen: sin `incluir_sinteticas` solo cuenta la demanda real."""
        return true() if incluir_sinteticas else ConsultaORM.origen == OrigenConsulta.USUARIO.value

    def conteo_por_origen(self) -> dict[str, int]:
        with self._sesion() as s:
            return {
                origen: int(n)
                for origen, n in s.execute(
                    select(ConsultaORM.origen, func.count()).group_by(ConsultaORM.origen)
                ).all()
            }

    def estadisticas(self, incluir_sinteticas: bool = False) -> dict:
        """Agregados del historial para la analitica del PMV2 (HU-09). Se calculan en la base
        de datos, no trayendo las filas a memoria. Solo cuentan las consultas de origen
        `usuario`, salvo que se pidan tambien las sinteticas."""
        filtro = self._solo_reales(incluir_sinteticas)
        with self._sesion() as s:
            total, abstenidas, por_predictor, p_media, lat_media = s.execute(
                select(
                    func.count(ConsultaORM.id),
                    func.coalesce(func.sum(case((ConsultaORM.abstenida.is_(True), 1), else_=0)), 0),
                    func.coalesce(
                        func.sum(
                            case((ConsultaORM.abstencion_por_predictor.is_(True), 1), else_=0)
                        ),
                        0,
                    ),
                    func.avg(ConsultaORM.probabilidad_cobertura),
                    func.avg(ConsultaORM.latencia_ms),
                ).where(filtro)
            ).one()
            por_idioma = dict(
                s.execute(
                    select(ConsultaORM.idioma, func.count())
                    .where(filtro)
                    .group_by(ConsultaORM.idioma)
                ).all()
            )
            por_via = {
                (via or "abstencion"): n
                for via, n in s.execute(
                    select(ConsultaORM.via_respaldo, func.count())
                    .where(filtro)
                    .group_by(ConsultaORM.via_respaldo)
                ).all()
            }
            por_documento = dict(
                s.execute(
                    select(
                        RespaldoORM.documento, func.count(func.distinct(RespaldoORM.consulta_id))
                    )
                    .join(ConsultaORM, ConsultaORM.id == RespaldoORM.consulta_id)
                    .where(filtro)
                    .group_by(RespaldoORM.documento)
                    .order_by(func.count(func.distinct(RespaldoORM.consulta_id)).desc())
                ).all()
            )
            latencias = sorted(
                v
                for v in s.scalars(select(ConsultaORM.latencia_ms).where(filtro)).all()
                if v is not None
            )
        return {
            "total": int(total or 0),
            "abstenidas": int(abstenidas or 0),
            "abstenciones_por_predictor": int(por_predictor or 0),
            "probabilidad_cobertura_media": float(p_media) if p_media is not None else None,
            "latencia_media_ms": float(lat_media) if lat_media is not None else None,
            "latencia_p95_ms": latencias[int(0.95 * (len(latencias) - 1))] if latencias else None,
            "por_idioma": por_idioma,
            "por_via": por_via,
            "respaldo_por_documento": por_documento,
        }

    def abstenciones_con_prediccion(
        self, limite: int = 5000, incluir_sinteticas: bool = False
    ) -> list[tuple[str, float | None]]:
        with self._sesion() as s:
            return [
                (texto, p)
                for texto, p in s.execute(
                    select(ConsultaORM.texto, ConsultaORM.probabilidad_cobertura)
                    .where(ConsultaORM.abstenida.is_(True))
                    .where(self._solo_reales(incluir_sinteticas))
                    .order_by(ConsultaORM.momento.desc())
                    .limit(limite)
                ).all()
            ]

    def total_registradas(self) -> int:
        with self._sesion() as s:
            return s.scalar(select(func.count()).select_from(ConsultaORM)) or 0

    @staticmethod
    def _a_dominio(r: ConsultaORM) -> tuple[Consulta, Respuesta]:
        consulta = Consulta(
            id=r.id,
            texto=r.texto,
            idioma=Idioma(r.idioma),
            momento=r.momento,
            texto_traducido=r.texto_traducido,
            origen=OrigenConsulta(r.origen or "usuario"),
        )
        respaldo = [
            FragmentoRecuperado(
                fragmento=Fragmento(
                    id=b.fragmento_id,
                    texto=b.texto,
                    procedencia=Procedencia(b.documento, b.pagina, b.derivado_ocr),
                    tipo=TipoFragmento.LEXICOGRAFICO,
                ),
                puntuacion=PuntuacionSimilitud(b.puntuacion),
            )
            for b in r.respaldos
        ]
        respuesta = Respuesta(
            consulta_id=r.id,
            texto=r.respuesta_texto,
            respaldo=respaldo,
            abstenida=r.abstenida,
            idioma=Idioma(r.idioma),
            similitud_maxima=r.similitud_maxima,
            momento=r.momento,
            via_respaldo=r.via_respaldo,
            probabilidad_cobertura=r.probabilidad_cobertura,
            probabilidad_pasajes=r.probabilidad_pasajes,
            abstencion_por_predictor=bool(r.abstencion_por_predictor),
        )
        return consulta, respuesta
