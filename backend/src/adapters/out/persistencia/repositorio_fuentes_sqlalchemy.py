from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from adapters.out.persistencia.modelos import FuenteORM
from application.ports.out.repositorio_fuentes_port import RepositorioFuentesPort
from domain.entities.fuente import Fuente


class RepositorioFuentesSqlalchemy(RepositorioFuentesPort):
    """Registro de fuentes (HU-01) sobre SQLAlchemy. Sirve igual con SQLite (local) que con
    PostgreSQL/Neon (nube): el nombre anterior, `RepositorioFuentesPostgres`, sugeria que solo
    funcionaba con PostgreSQL (H-09)."""

    def __init__(self, sesion: sessionmaker[Session]):
        self._sesion = sesion

    def crear(self, fuente: Fuente) -> Fuente:
        with self._sesion() as s, s.begin():
            s.add(self._a_orm(fuente))
        return fuente

    def obtener(self, fuente_id: str) -> Fuente | None:
        with self._sesion() as s:
            registro = s.get(FuenteORM, fuente_id)
            return self._a_dominio(registro) if registro else None

    def listar(self) -> list[Fuente]:
        with self._sesion() as s:
            registros = s.scalars(select(FuenteORM).order_by(FuenteORM.titulo)).all()
            return [self._a_dominio(r) for r in registros]

    def actualizar(self, fuente: Fuente) -> Fuente:
        with self._sesion() as s, s.begin():
            registro = s.get(FuenteORM, fuente.id)
            if registro is None:
                raise KeyError(f"No existe la fuente {fuente.id}")
            for campo, valor in self._a_orm(fuente).__dict__.items():
                if not campo.startswith("_"):
                    setattr(registro, campo, valor)
        return fuente

    def eliminar(self, fuente_id: str) -> bool:
        with self._sesion() as s, s.begin():
            registro = s.get(FuenteORM, fuente_id)
            if registro is None:
                return False
            s.delete(registro)
            return True

    @staticmethod
    def _a_orm(f: Fuente) -> FuenteORM:
        return FuenteORM(
            id=f.id,
            titulo=f.titulo,
            entidad_publicadora=f.entidad_publicadora,
            licenciamiento=f.licenciamiento,
            fecha_extraccion=f.fecha_extraccion,
            nombre_archivo=f.nombre_archivo,
            paginas_totales=f.paginas_totales,
            paginas_con_texto=f.paginas_con_texto,
            derivado_ocr=f.derivado_ocr,
        )

    @staticmethod
    def _a_dominio(r: FuenteORM) -> Fuente:
        return Fuente(
            id=r.id,
            titulo=r.titulo,
            entidad_publicadora=r.entidad_publicadora,
            licenciamiento=r.licenciamiento,
            fecha_extraccion=r.fecha_extraccion,
            nombre_archivo=r.nombre_archivo,
            paginas_totales=r.paginas_totales,
            paginas_con_texto=r.paginas_con_texto,
            derivado_ocr=r.derivado_ocr,
        )
