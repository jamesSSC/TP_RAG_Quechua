"""Verificacion previa a la grabacion de la demostracion (P0-B7).

Imprime una linea por comprobacion (✔ o ✖, con la causa) y sale con codigo distinto de 0 si falla
algo CRITICO. Los AVISOS (⚠) no cambian el codigo de salida.

Uso, desde backend/:
    python scripts/verificar_entorno_demo.py [--postgres] [--app-levantada] [--sin-precalentar]

  --postgres          comprueba tambien la conexion a PostgreSQL (credenciales de backend/.env)
  --app-levantada     la app ya esta en marcha: exige GET /api/estado = 200, no puertos libres
  --sin-precalentar   no precalienta el modelo de Ollama
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import socket
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

PUERTO_API = 8000
PUERTO_WEB = 5173
MODELO = "qwen3.5:4b"
DEPENDENCIAS = (
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic_settings",
    "sqlalchemy",
    "sklearn",
    "numpy",
    "scipy",
    "joblib",
    "pypdf",
    "httpx",
    "multipart",
    "dotenv",
)


@dataclass(frozen=True)
class Resultado:
    nombre: str
    ok: bool
    detalle: str
    critico: bool = True

    @property
    def simbolo(self) -> str:
        if self.ok:
            return "✔"
        return "✖" if self.critico else "⚠"


# --- Comprobaciones: cada una recibe lo que necesita y no toca el entorno por su cuenta ---


def comprobar_python(version: tuple[int, int] | None = None) -> Resultado:
    v = version or sys.version_info[:2]
    return Resultado(
        "Python 3.12 o superior",
        v >= (3, 12),
        f"Python {v[0]}.{v[1]}" if v >= (3, 12) else f"Python {v[0]}.{v[1]}: se necesita 3.12+",
    )


def comprobar_dependencias(
    nombres: tuple[str, ...] = DEPENDENCIAS,
    buscar: Callable[[str], object] = importlib.util.find_spec,
) -> Resultado:
    faltan = [n for n in nombres if buscar(n) is None]
    if faltan:
        return Resultado(
            "Dependencias de Python",
            False,
            "faltan: " + ", ".join(faltan) + " (pip install -r requirements.txt)",
        )
    return Resultado("Dependencias de Python", True, f"{len(nombres)} paquetes importables")


def comprobar_archivo(nombre: str, ruta: Path, critico: bool = True, ayuda: str = "") -> Resultado:
    if ruta.is_file():
        return Resultado(
            nombre, True, f"{ruta.name} ({ruta.stat().st_size / 1_048_576:.1f} MB)", critico
        )
    sufijo = f" · {ayuda}" if ayuda else ""
    return Resultado(nombre, False, f"no existe {ruta.as_posix()}{sufijo}", critico)


def comprobar_datos_fuera_de_git(carpeta_datos: Path, ruta_corpus: Path) -> list[Resultado]:
    return [
        comprobar_archivo(
            "Corpus segmentado (fuera de Git)",
            ruta_corpus,
            ayuda="copielo de la copia de seguridad o reingiera los PDF",
        ),
        comprobar_archivo("Conjunto de evaluacion v2", carpeta_datos / "evaluacion_v2.json"),
        comprobar_archivo("Tabla de traduccion EN->ES", carpeta_datos / "traduccion_en_es.json"),
        comprobar_archivo(
            "Evaluacion de prosa (fuera de Git)",
            carpeta_datos / "evaluacion_prosa.json",
            critico=False,
            ayuda="sin ella no se pueden reentrenar los modelos ni correr el arnes de prosa",
        ),
    ]


def comprobar_modelos(carpeta: Path) -> list[Resultado]:
    return [
        comprobar_archivo(
            "Modelo de cobertura",
            carpeta / "cobertura.joblib",
            ayuda="python scripts/entrenar_predictores.py",
        ),
        comprobar_archivo(
            "Modelo de relevancia de pasajes",
            carpeta / "relevancia_pasajes.joblib",
            ayuda="python scripts/entrenar_predictores.py",
        ),
    ]


def comprobar_ollama(
    url: str,
    modelo: str,
    obtener: Callable[[str], dict],
    precalentar: Callable[[], bool] | None = None,
) -> list[Resultado]:
    """`obtener(url)` devuelve el JSON de /api/tags o lanza OSError si no responde."""
    try:
        etiquetas = obtener(f"{url}/api/tags")
    except Exception as exc:  # noqa: BLE001
        return [
            Resultado(
                f"Ollama con {modelo}",
                False,
                f"no responde en {url} ({type(exc).__name__}). Inicie Ollama (ollama serve)",
            )
        ]
    nombres = [m.get("name", "") for m in etiquetas.get("models", [])]
    if not any(n == modelo or n.startswith(modelo.split(":")[0] + ":") for n in nombres):
        return [
            Resultado(
                f"Ollama con {modelo}",
                False,
                f"responde, pero falta el modelo: ollama pull {modelo}",
            )
        ]
    resultados = [Resultado(f"Ollama con {modelo}", True, f"responde en {url}")]
    if precalentar is not None:
        t0 = time.perf_counter()
        cargado = precalentar()
        segundos = time.perf_counter() - t0
        resultados.append(
            Resultado(
                "Modelo precalentado",
                cargado,
                f"cargado en memoria en {segundos:.1f} s"
                if cargado
                else "no se pudo precalentar: la primera respuesta sera lenta",
                critico=False,
            )
        )
    return resultados


def comprobar_postgres(conectar: Callable[[], str]) -> Resultado:
    """`conectar()` devuelve una descripcion corta (sin credenciales) o lanza una excepcion."""
    try:
        return Resultado("PostgreSQL", True, conectar())
    except Exception as exc:  # noqa: BLE001
        return Resultado(
            "PostgreSQL",
            False,
            f"no se pudo conectar ({type(exc).__name__}): revise el servicio y POSTGRES_* de .env",
        )


def comprobar_puertos(
    ocupado: Callable[[int], bool],
    app_levantada: bool,
    estado: Callable[[], int],
) -> list[Resultado]:
    if app_levantada:
        codigo = estado()
        return [
            Resultado(
                "API en marcha (GET /api/estado)",
                codigo == 200,
                "responde 200" if codigo == 200 else f"no responde 200 (codigo {codigo})",
            ),
            Resultado(
                f"Interfaz en el puerto {PUERTO_WEB}",
                ocupado(PUERTO_WEB),
                "Vite escucha" if ocupado(PUERTO_WEB) else "nadie escucha: arranque la interfaz",
                critico=False,
            ),
        ]
    resultados = []
    for puerto, quien in ((PUERTO_API, "API"), (PUERTO_WEB, "interfaz")):
        libre = not ocupado(puerto)
        resultados.append(
            Resultado(
                f"Puerto {puerto} libre ({quien})",
                libre,
                "libre"
                if libre
                else "ocupado por otro programa (o la app ya esta levantada: use --app-levantada)",
            )
        )
    return resultados


def comprobar_frontend(
    interfaz: Path,
    frontend: Path,
    hay_npm: Callable[[], bool] = lambda: shutil.which("npm") is not None,
) -> Resultado:
    if (interfaz / "index.html").is_file():
        return Resultado("Interfaz compilada o arrancable", True, "compilada en backend/interfaz")
    if (frontend / "node_modules").is_dir() and hay_npm():
        return Resultado("Interfaz compilada o arrancable", True, "arrancable con npm run dev")
    return Resultado(
        "Interfaz compilada o arrancable",
        False,
        "ni compilada ni arrancable: en frontend/ ejecute npm ci",
    )


# --- Entorno real ---


def _puerto_ocupado(puerto: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex(("127.0.0.1", puerto)) == 0


def _estado_api() -> int:
    import httpx

    try:
        return httpx.get(f"http://127.0.0.1:{PUERTO_API}/api/estado", timeout=30.0).status_code
    except httpx.HTTPError:
        return 0


def _json(url: str) -> dict:
    import httpx

    r = httpx.get(url, timeout=5.0)
    r.raise_for_status()
    return r.json()


def _conectar_postgres() -> str:
    from sqlalchemy import create_engine, text

    from infrastructure.config import configuracion as c

    url = (
        f"postgresql+psycopg://{c.postgres_user}:{c.postgres_password}"
        f"@{c.postgres_host}:{c.postgres_port}/postgres"
    )
    with create_engine(url, connect_args={"connect_timeout": 5}).connect() as conexion:
        version = conexion.execute(text("SHOW server_version")).scalar()
        existe = conexion.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'quechua_wanka_demo'")
        ).scalar()
    base = (
        "base quechua_wanka_demo presente"
        if existe
        else "falta quechua_wanka_demo (03_carga_postgres.ps1)"
    )
    return f"PostgreSQL {version} en {c.postgres_host}:{c.postgres_port}; {base}"


def reunir(args: argparse.Namespace) -> list[Resultado]:
    from infrastructure.config import configuracion as c

    resultados: list[Resultado] = [comprobar_python(), comprobar_dependencias()]
    resultados += comprobar_datos_fuera_de_git(RAIZ / "data", c.ruta_corpus)
    resultados += comprobar_modelos(RAIZ / "modelos")

    precalentar = None
    if not args.sin_precalentar:
        from adapters.out.generacion.ollama_generador import OllamaGenerador

        precalentar = OllamaGenerador(url_base=c.ollama_url, modelo=MODELO).precalentar
    resultados += comprobar_ollama(c.ollama_url, MODELO, _json, precalentar)

    if args.postgres:
        resultados.append(comprobar_postgres(_conectar_postgres))
    resultados += comprobar_puertos(_puerto_ocupado, args.app_levantada, _estado_api)
    resultados.append(
        comprobar_archivo(
            "Base de demostracion carga.db",
            RAIZ / "carga.db",
            ayuda="scripts/demo/02_carga_sqlite.ps1",
        )
    )
    resultados.append(comprobar_frontend(c.ruta_interfaz, RAIZ.parent / "frontend"))
    return resultados


def imprimir_y_codigo(resultados: list[Resultado], segundos: float) -> int:
    for r in resultados:
        print(f" {r.simbolo} {r.nombre}: {r.detalle}")
    criticos = [r for r in resultados if not r.ok and r.critico]
    avisos = [r for r in resultados if not r.ok and not r.critico]
    print("-" * 70)
    print(
        f" {len(resultados)} comprobaciones en {segundos:.1f} s · "
        f"{len(criticos)} fallo(s) critico(s) · {len(avisos)} aviso(s)"
    )
    print(" LISTO PARA GRABAR" if not criticos else " NO ESTA LISTO: corrija los ✖ antes de grabar")
    return 1 if criticos else 0


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--postgres", action="store_true")
    parser.add_argument("--app-levantada", action="store_true")
    parser.add_argument("--sin-precalentar", action="store_true")
    args = parser.parse_args(argv)
    t0 = time.perf_counter()
    resultados = reunir(args)
    return imprimir_y_codigo(resultados, time.perf_counter() - t0)


if __name__ == "__main__":
    sys.exit(main())
