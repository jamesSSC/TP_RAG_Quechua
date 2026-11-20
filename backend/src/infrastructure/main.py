import logging
import threading
from contextlib import asynccontextmanager
from importlib import import_module

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from infrastructure.config import configuracion
from infrastructure.contenedor import Contenedor
from infrastructure.seguridad import (
    CabecerasDeSeguridad,
    ClaveGeminiDeLaPeticion,
    OrigenDePruebasAutorizado,
)
from infrastructure.seguridad_nube import CabeceraHsts, EscrituraProtegida, LimitePeticiones


def resolver_recurso_interfaz(raiz, recurso: str):
    """OW-05: devuelve el archivo pedido solo si esta contenido en `raiz`; si no, index.html."""
    base = raiz.resolve()
    try:
        archivo = (base / recurso).resolve()
    except (OSError, ValueError):
        return base / "index.html"
    if archivo.is_relative_to(base) and archivo.is_file():
        return archivo
    return base / "index.html"


# `in` es palabra reservada de Python: el paquete adapters/in solo se importa por cadena.
routers = import_module("adapters.in.rest").routers

logging.basicConfig(
    level=getattr(logging, configuracion.nivel_log),
    format="%(asctime)s %(levelname)-7s %(name)s %(message)s",
    datefmt="%H:%M:%S",
)


@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    contenedor = Contenedor(generador=configuracion.generador)
    app.state.contenedor = contenedor
    # En un hilo aparte para que el servicio acepte peticiones mientras el modelo se carga.
    threading.Thread(target=contenedor.generador.precalentar, daemon=True).start()
    yield


app = FastAPI(
    title="Asistente de consulta del quechua wanka",
    description=(
        "Consulta documental sobre el corpus publicado de quechua wanka de Junin. "
        "Toda respuesta cita el documento y la pagina que la sustentan, y el sistema "
        "declara explicitamente la ausencia de informacion en lugar de proponer una "
        "forma no documentada."
    ),
    version="1.0.0",
    lifespan=ciclo_vida,
)

# Orden: el ultimo registrado es el mas externo. OrigenDePruebas va por fuera del limite para que
# las corridas de humo/carga autorizadas queden exentas (ADR-037); CORS envuelve a todos, de modo
# que un 401/403/429 tambien lleva las cabeceras CORS y el navegador puede leer el mensaje.
app.add_middleware(ClaveGeminiDeLaPeticion)
app.add_middleware(
    LimitePeticiones,
    limites={
        "/api/consultas": configuracion.limite_consultas_por_minuto,
        "/api/predicciones": configuracion.limite_predicciones_por_minuto,
    }
    if configuracion.modo_nube
    else {},
)
app.add_middleware(
    EscrituraProtegida, activo=configuracion.modo_nube, token=configuracion.admin_token
)
app.add_middleware(OrigenDePruebasAutorizado, token=configuracion.token_pruebas)
app.add_middleware(CabecerasDeSeguridad)
app.add_middleware(CabeceraHsts, activo=configuracion.modo_nube)
# S13 (OW-11): metodos y cabeceras explicitos y sin credenciales (la API no usa cookies).
app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.lista_cors,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "X-Gemini-Key",
        "X-Admin-Token",
        "X-Token-Pruebas",
        "X-Origen-Consultas",
    ],
)

for router in routers:
    app.include_router(router)


if configuracion.sirve_interfaz:
    # La interfaz ya compilada se sirve desde el propio servicio. Asi la distribucion no
    # exige un segundo proceso ni el entorno de Node, que solo hace falta para compilarla.
    # El montaje va despues del router para que las rutas de la interfaz de programacion
    # conserven prioridad sobre los archivos estaticos.
    app.mount(
        "/assets",
        StaticFiles(directory=configuracion.ruta_interfaz / "assets"),
        name="assets",
    )

    @app.get("/", include_in_schema=False)
    def interfaz():
        return FileResponse(configuracion.ruta_interfaz / "index.html")

    @app.get("/{recurso:path}", include_in_schema=False)
    def interfaz_o_recurso(recurso: str):
        # OW-05 (S13): solo se sirve lo que queda DENTRO de la carpeta de la interfaz; `..`,
        # `%2e%2e` o una ruta absoluta (`/C:/...`) caen en index.html, como una ruta del cliente.
        return FileResponse(resolver_recurso_interfaz(configuracion.ruta_interfaz, recurso))
        # Cualquier otra ruta devuelve la interfaz: el enrutado es del lado del cliente.
        return FileResponse(configuracion.ruta_interfaz / "index.html")

else:

    @app.get("/", tags=["sistema"])
    def raiz():
        return {"servicio": "asistente-quechua-wanka", "documentacion": "/docs"}
