from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class ConsultaEntrada(BaseModel):
    # De 1 a 300 caracteres tras quitar los espacios de los extremos (la interfaz valida lo
    # mismo; el backend no se fia del cliente).
    texto: str = Field(min_length=1, max_length=300)

    @field_validator("texto", mode="before")
    @classmethod
    def _sin_espacios_extremos(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor


class RespaldoSalida(BaseModel):
    fragmento_id: str
    texto: str
    documento: str
    pagina: int
    puntuacion: float
    # Misma cifra que `puntuacion`, con el nombre que usa la interfaz.
    similitud: float
    derivado_ocr: bool
    coincidencia_lema: bool
    # "no es una respuesta" en los pasajes de prosa; None en el respaldo.
    rotulo: str | None = None


class RespuestaSalida(BaseModel):
    consulta_id: str
    texto: str
    abstenida: bool
    idioma: str
    similitud_maxima: float
    aviso: str
    respaldo: list[RespaldoSalida]
    consulta_traducida: str | None = None
    # Pasajes de prosa ofrecidos sin afirmar que respondan. Llegan solo con abstenida=True.
    pasajes: list[RespaldoSalida] = []
    # Via del respaldo ("similitud" | "lema"; None si el sistema se abstuvo) y tau vigente.
    via_respaldo: str | None = None
    umbral: float | None = None
    latencia_ms: float = 0.0
    # Todas las lecturas candidatas de la traduccion y la que sostuvo la respuesta.
    lecturas_traduccion: list[str] = []
    traduccion_usada: str | None = None
    generador_invocado: bool = False
    aviso_generacion: str | None = None
    # ADR-032: «Redactado por: gemini | ollama | extractivo» y el motivo si hubo degradacion.
    redactado_por: str | None = None
    motivo_redaccion: str | None = None
    # PMV2: probabilidades estimadas por los modelos predictivos (None si no hay modelo).
    probabilidad_cobertura: float | None = None
    probabilidad_pasajes: float | None = None
    abstencion_por_predictor: bool = False


class EntradaHistorial(BaseModel):
    consulta: str
    respuesta: str
    abstenida: bool
    similitud_maxima: float
    via_respaldo: str | None = None
    momento: datetime
    probabilidad_cobertura: float | None = None


class FuenteEntrada(BaseModel):
    titulo: str = Field(min_length=1, max_length=300)
    entidad_publicadora: str = Field(min_length=1, max_length=200)
    licenciamiento: str = Field(min_length=1, max_length=300)
    fecha_extraccion: date
    nombre_archivo: str = Field(min_length=1, max_length=300)
    paginas_totales: int = 0
    paginas_con_texto: int = 0
    derivado_ocr: bool = False


class FuenteSalida(FuenteEntrada):
    id: str
    cobertura_extraccion: float


class ResultadoIngestaSalida(BaseModel):
    nombre_archivo: str
    titulo: str
    paginas_totales: int
    paginas_con_texto: int
    cobertura_extraccion: float
    fragmentos_generados: int
    fragmentos_nuevos: int
    total_indexado: int
    requiere_ocr: bool
    aviso: str | None = None


class DocumentosCorpus(BaseModel):
    documentos: list[str]
    total_fragmentos: int


class ConsistenciaDatos(BaseModel):
    estado: str
    avisos: list[str] = []


class EstadoSistema(BaseModel):
    fragmentos_indexados: int
    umbral_abstencion: float
    generador_disponible: bool
    base_datos_disponible: bool
    modelo: str
    predictores_disponibles: bool = False
    consistencia: ConsistenciaDatos | None = None
    # HU-09: consultas registradas por origen y rotulo de base de demostracion.
    consultas_por_origen: dict[str, int] = {}
    base_demostracion: bool = False
    # Nube (ADR-030 a 032). Solo nombres y conteos: ningun secreto ni cadena de conexion.
    entorno: str = "local"
    motor_base_datos: str = "sqlite"
    origen_corpus: str = "jsonl"
    generador: str = "ollama"
    modelos_ml: dict[str, bool] = {}
    documentos_corpus: int = 0
