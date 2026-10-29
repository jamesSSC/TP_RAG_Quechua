"""Cabeceras de seguridad HTTP (RS-03). La app es local, pero el servicio sirve la interfaz y
la API, y las reglas pasivas de un escaner (p. ej. OWASP ZAP) las esperan."""

from starlette.middleware.base import BaseHTTPMiddleware

# La interfaz compilada no usa recursos de terceros (RS-03): todo sale del mismo origen.
CSP_INTERFAZ = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
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
