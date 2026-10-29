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
from infrastructure.seguridad import CabecerasDeSeguridad

# `in` es palabra reservada de Python: el paquete adapters/in solo se importa por cadena.
routers = import_module("adapters.in.rest").routers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")


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

app.add_middleware(CabecerasDeSeguridad)
app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.lista_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        archivo = configuracion.ruta_interfaz / recurso
        if archivo.is_file():
            return FileResponse(archivo)
        # Cualquier otra ruta devuelve la interfaz: el enrutado es del lado del cliente.
        return FileResponse(configuracion.ruta_interfaz / "index.html")

else:

    @app.get("/", tags=["sistema"])
    def raiz():
        return {"servicio": "asistente-quechua-wanka", "documentacion": "/docs"}
