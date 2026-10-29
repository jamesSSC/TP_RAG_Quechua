import sys
from pathlib import Path
from typing import Literal

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


def normalizar_database_url(url: str) -> str:
    """Adapta la cadena que entrega Neon (`postgres://` o `postgresql://`) al controlador
    psycopg de SQLAlchemy y exige TLS si la cadena no lo fija."""
    for prefijo in ("postgres://", "postgresql://"):
        if url.startswith(prefijo):
            url = "postgresql+psycopg://" + url[len(prefijo) :]
            break
    if "sslmode=" not in url and not any(h in url for h in ("@localhost", "@127.0.0.1")):
        url += ("&" if "?" in url else "?") + "sslmode=require"
    return url


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

    # Nube (ADR-031): cadena de conexion completa de la base gestionada (Neon). Tiene prioridad
    # sobre POSTGRES_*. Es un secreto: se pega en el panel de Render o en el .env local y nunca
    # se imprime ni se devuelve por la API.
    database_url: str = ""
    # Origen del corpus: "jsonl" (archivo local, E1) o "postgres" (tabla `fragmentos`, nube).
    corpus_origen: Literal["jsonl", "postgres"] = "jsonl"
    # Rotulo del entorno que se muestra en /api/estado y en el pie de la interfaz.
    entorno: str = "local"

    ruta_tabla_traduccion: Path = RAIZ / "data" / "traduccion_en_es.json"
    ollama_url: str = "http://localhost:11434"
    ollama_modelo: str = "qwen3.5:4b"

    umbral_abstencion: float = 0.48
    # Generador: "ollama" (modelo), "literal" (fragmento literal sin modelo, para pruebas de carga
    # que miden la API y no la GPU) o "auto" (Ollama si responde).
    # "extractivo": sin modelo, compone el fragmento literal citado (nube sin clave de Gemini).
    # "gemini": la API de Google extrae {forma, glosa} y se verifica como en ADR-028 (ADR-032).
    generador: Literal["ollama", "literal", "auto", "extractivo", "gemini"] = "ollama"
    # ADR-032. La clave es un secreto del servicio (panel de Render); nunca se registra.
    gemini_api_key: str = ""
    gemini_modelo: str = "gemini-3.5-flash-lite"
    gemini_timeout: float = 15.0
    # Secreto que autoriza a las pruebas contra la nube a registrar sus consultas como `carga` o
    # `humo` (cabeceras X-Token-Pruebas y X-Origen-Consultas). Vacio: desactivado.
    token_pruebas: str = ""
    # Redaccion con modelo: "extractiva" (ADR-028: el modelo extrae {forma, glosa}, se verifica
    # contra el fragmento y se compone en una plantilla) o "libre" (el modelo escribe la frase).
    modo_redaccion: Literal["extractiva", "libre"] = "extractiva"
    # Origen con el que este proceso registra las consultas (HU-09). Lo fija el servidor:
    # `usuario` salvo en las corridas de prueba (carga, arnes, humo). La API no lo acepta.
    origen_consultas: Literal["usuario", "carga", "arnes", "humo"] = "usuario"
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
        if self.database_url:
            return normalizar_database_url(self.database_url)
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
