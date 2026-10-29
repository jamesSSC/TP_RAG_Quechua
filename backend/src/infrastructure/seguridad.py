"""Cabeceras de seguridad HTTP (RS-03). La app es local, pero el servicio sirve la interfaz y
la API, y las reglas pasivas de un escaner (p. ej. OWASP ZAP) las esperan."""

import hmac

from starlette.middleware.base import BaseHTTPMiddleware

from adapters.out.generacion.gemini_generador import clave_de_la_peticion

# La interfaz compilada no usa recursos de terceros (RS-03): todo sale del mismo origen. Sin
# 'unsafe-inline': el CSS sale a un archivo y React aplica `style` por CSSOM, que la CSP permite.
CSP_INTERFAZ = (
    "default-src 'self'; script-src 'self'; style-src 'self'; "
    "img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; "
    "frame-ancestors 'none'; form-action 'self'"
)
# La documentacion interactiva (Swagger/ReDoc) carga su interfaz desde un CDN: sin CSP estricta.
RUTAS_DOCUMENTACION = ("/docs", "/redoc", "/openapi.json")

CABECERAS_BASE = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Resource-Policy": "same-origin",
}


CABECERA_CLAVE_GEMINI = b"x-gemini-key"


class ClaveGeminiDeLaPeticion:
    """BYOK (ADR-032): la clave de Gemini que el usuario aporta en `X-Gemini-Key` vale solo para
    esa peticion. Middleware ASGI puro para que la variable de contexto se fije en el mismo
    contexto que ejecuta la ruta y se restablezca al terminar. La clave no se registra en
    ningun log, ni en la base, ni se devuelve."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        clave = None
        if scope["type"] == "http":
            for nombre, valor in scope.get("headers", []):
                if nombre == CABECERA_CLAVE_GEMINI:
                    clave = valor.decode("latin-1").strip() or None
                    break
        if clave is None:
            await self.app(scope, receive, send)
            return
        ficha = clave_de_la_peticion.set(clave)
        try:
            await self.app(scope, receive, send)
        finally:
            clave_de_la_peticion.reset(ficha)


ORIGENES_DE_PRUEBA = {"carga", "humo"}


class OrigenDePruebasAutorizado:
    """HU-09 en la nube: las pruebas de carga y de humo contra la API publica deben registrarse
    como `carga`/`humo` y no como demanda real. El cliente normal no elige el origen; solo una
    peticion con `X-Token-Pruebas` igual a TOKEN_PRUEBAS (secreto del servidor; vacio =
    desactivado) puede fijarlo con `X-Origen-Consultas`. El token no se registra."""

    def __init__(self, app, token: str = ""):
        self.app = app
        self._token = token.encode()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and self._token:
            cabeceras = dict(scope.get("headers", []))
            token = cabeceras.get(b"x-token-pruebas", b"")
            origen = cabeceras.get(b"x-origen-consultas", b"").decode("latin-1").strip()
            if (
                token
                and origen in ORIGENES_DE_PRUEBA
                and hmac.compare_digest(token, self._token)
            ):
                scope.setdefault("state", {})["origen_pruebas"] = origen
        await self.app(scope, receive, send)


class CabecerasDeSeguridad(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        respuesta = await call_next(request)
        for nombre, valor in CABECERAS_BASE.items():
            respuesta.headers.setdefault(nombre, valor)
        ruta = request.url.path
        if not ruta.startswith(RUTAS_DOCUMENTACION):
            respuesta.headers.setdefault("Content-Security-Policy", CSP_INTERFAZ)
        if ruta.startswith("/api"):
            # Las respuestas de la API (historial, consultas) no se guardan en caches.
            respuesta.headers.setdefault("Cache-Control", "no-store")
        return respuesta
