import sys
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Al empaquetar con PyInstaller el codigo vive dentro de un directorio temporal que el
# propio ejecutable descomprime, de modo que la raiz del proyecto deja de ser la carpeta
# del archivo. Los datos de solo lectura (corpus, tabla de traduccion, interfaz compilada)
# viajan ahi dentro; lo que el usuario puede modificar va junto al ejecutable.
# Fuera del ejecutable, este archivo vive en backend/src/infrastructure/: la raiz de datos
# sigue siendo backend/ (parents[2]).
EMPAQUETADO = getattr(sys, "frozen", False)
RAIZ = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
CARPETA_EJECUTABLE = Path(sys.executable).parent if EMPAQUETADO else RAIZ


def resolver_carpeta_datos(empaquetado: bool, carpeta_ejecutable: Path, raiz: Path) -> Path:
    """Carpeta de datos modificables (corpus ampliado y PDF incorporados). Empaquetado:
    `datos/` junto al ejecutable, porque `_MEIPASS` se borra al cerrar. Desarrollo:
    `backend/data/`."""
    return carpeta_ejecutable / "datos" if empaquetado else raiz / "data"


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=CARPETA_EJECUTABLE / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Motor de persistencia: "postgres" o "sqlite".
    #
    # SQLite no exige instalar un servidor de base de datos a quien solo quiere usar el
    # sistema; PostgreSQL queda como segundo motor. Ambos recorren el
    # mismo adaptador y los mismos modelos, porque ninguno usa tipos ni sentencias
    # propias de un motor concreto: la sustitucion es un parametro, que es justo lo que
    # RNF-07 compromete.
    # SQLite por defecto en todos los modos (ADR-027): sin servidor ni credenciales. PostgreSQL
    # sigue seleccionable con BASE_DATOS=postgres (+ POSTGRES_*).
    base_datos: str = "sqlite"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "quechua_wanka"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    ruta_sqlite: Path = CARPETA_EJECUTABLE / "quechua_wanka.db"

    ruta_tabla_traduccion: Path = RAIZ / "data" / "traduccion_en_es.json"
    ollama_url: str = "http://localhost:11434"
    ollama_modelo: str = "qwen3.5:4b"

    umbral_abstencion: float = 0.48
    fragmentos_recuperados: int = 5
    # Corpus base (solo lectura, viaja en el paquete) y copia modificable (BUG-01). La copia
    # se hace en el primer arranque; en desarrollo ambos coinciden en backend/data/.
    ruta_corpus_base: Path = RAIZ / "data" / "fragmentos_v3.jsonl"
    carpeta_datos: Path = resolver_carpeta_datos(EMPAQUETADO, CARPETA_EJECUTABLE, RAIZ)
    ruta_corpus: Path | None = None

    # PMV2 · modelos predictivos (scripts/entrenar_predictores.py). Los cortes salen de la
    # validacion cruzada documentada en modelos/metricas.json; si el artefacto no existe el
    # sistema opera exactamente como en el PMV1 (RN-06).
    ruta_modelo_cobertura: Path = RAIZ / "modelos" / "cobertura.joblib"
    ruta_modelo_pasajes: Path = RAIZ / "modelos" / "relevancia_pasajes.joblib"
    ruta_metricas_modelos: Path = RAIZ / "modelos" / "metricas.json"
    probabilidad_minima_cobertura: float = 0.25
    probabilidad_minima_pasajes: float = 0.50

    # Interfaz ya compilada. Cuando existe, el servicio la sirve y no hace falta ningun
    # proceso aparte para el front-end.
    ruta_interfaz: Path = RAIZ / "interfaz"

    cors_origenes: str = "http://localhost:5173"

    @model_validator(mode="after")
    def _derivar_rutas_de_datos(self):
        if self.ruta_corpus is None:
            self.ruta_corpus = self.carpeta_datos / "fragmentos_v3.jsonl"
        return self

    @property
    def ruta_documentos(self) -> Path:
        return self.carpeta_datos / "documentos"

    @property
    def url_base_datos(self) -> str:
        if self.base_datos == "sqlite":
            return f"sqlite:///{self.ruta_sqlite}"
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def lista_cors(self) -> list[str]:
        return [o.strip() for o in self.cors_origenes.split(",") if o.strip()]

    @property
    def sirve_interfaz(self) -> bool:
        return (self.ruta_interfaz / "index.html").exists()


configuracion = Configuracion()
