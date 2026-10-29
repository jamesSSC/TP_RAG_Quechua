from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class FuenteORM(Base):
    __tablename__ = "fuentes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    entidad_publicadora: Mapped[str] = mapped_column(String(200), nullable=False)
    licenciamiento: Mapped[str] = mapped_column(String(300), nullable=False)
    fecha_extraccion: Mapped[date] = mapped_column(Date, nullable=False)
    nombre_archivo: Mapped[str] = mapped_column(String(300), nullable=False)
    paginas_totales: Mapped[int] = mapped_column(Integer, default=0)
    paginas_con_texto: Mapped[int] = mapped_column(Integer, default=0)
    derivado_ocr: Mapped[bool] = mapped_column(Boolean, default=False)


class ConsultaORM(Base):
    __tablename__ = "consultas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    idioma: Mapped[str] = mapped_column(String(2), nullable=False)
    texto_traducido: Mapped[str | None] = mapped_column(Text, nullable=True)
    momento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    respuesta_texto: Mapped[str] = mapped_column(Text, nullable=False)
    abstenida: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    similitud_maxima: Mapped[float] = mapped_column(Float, nullable=False)
    # "similitud" | "lema"; NULL en una abstencion. Sin datos personales en este modelo.
    via_respaldo: Mapped[str | None] = mapped_column(String(10), nullable=True)
    # PMV2: lo que estimaron los modelos predictivos, junto con el resultado real, para poder
    # auditarlos y reentrenarlos (HU-08.1, escenario "registra la prediccion junto con el
    # resultado real").
    probabilidad_cobertura: Mapped[float | None] = mapped_column(Float, nullable=True)
    probabilidad_pasajes: Mapped[float | None] = mapped_column(Float, nullable=True)
    abstencion_por_predictor: Mapped[bool] = mapped_column(Boolean, default=False)
    pasajes_ofrecidos: Mapped[int] = mapped_column(Integer, default=0)
    latencia_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    # HU-09 (ADR-013): usuario | carga | arnes | humo. Solo `usuario` cuenta como demanda real.
    origen: Mapped[str] = mapped_column(
        String(10), nullable=False, default="usuario", server_default="usuario"
    )

    respaldos: Mapped[list["RespaldoORM"]] = relationship(
        back_populates="consulta", cascade="all, delete-orphan", lazy="selectin"
    )


class RespaldoORM(Base):
    """Trazabilidad persistida: sin documento y pagina no hay forma de verificar una
    respuesta en la fuente original (RNF-08)."""

    __tablename__ = "respaldos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    consulta_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("consultas.id", ondelete="CASCADE"), nullable=False
    )
    fragmento_id: Mapped[str] = mapped_column(String(64), nullable=False)
    documento: Mapped[str] = mapped_column(String(300), nullable=False)
    pagina: Mapped[int] = mapped_column(Integer, nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    puntuacion: Mapped[float] = mapped_column(Float, nullable=False)
    derivado_ocr: Mapped[bool] = mapped_column(Boolean, default=False)

    consulta: Mapped[ConsultaORM] = relationship(back_populates="respaldos")


# Columnas que el PMV2 añadio a una tabla que ya existe en las bases creadas por el PMV1.
# create_all() no altera tablas existentes, de modo que se añaden al arrancar.
COLUMNAS_PMV2 = {
    "probabilidad_cobertura": "FLOAT",
    "probabilidad_pasajes": "FLOAT",
    "abstencion_por_predictor": "BOOLEAN DEFAULT FALSE",
    "pasajes_ofrecidos": "INTEGER DEFAULT 0",
    "latencia_ms": "FLOAT",
}

# HU-09: columna de origen en las bases creadas antes de existir. Mismo mecanismo que arriba.
COLUMNAS_HU09 = {"origen": "VARCHAR(10) NOT NULL DEFAULT 'usuario'"}
