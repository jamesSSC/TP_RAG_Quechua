"""S13 · fase 2 (OWASP). Controles que solo se activan en modo nube (ENTORNO != local):
token de administracion (ADR-035, ADR-036), limite de peticiones (ADR-037) y HSTS.
Middlewares ASGI puros, con el mismo patron que `OrigenDePruebasAutorizado`."""

import hashlib
import hmac
import json
import logging
import time
from collections import deque

log_seguridad = logging.getLogger("rag.seguridad")

METODOS_DE_LECTURA = {"GET", "HEAD", "OPTIONS"}
# POST de solo lectura que siguen siendo publicos (Consultar y Prediccion ML).
# REF-07 (ADR-040): la valoración es pública como la consulta, y lleva el mismo límite.
POST_PUBLICOS = {"/api/consultas", "/api/predicciones", "/api/valoraciones"}
# GET que tambien exigen token en la nube: el historial del servidor (ADR-036).
GET_PROTEGIDOS = {"/api/historial"}
CABECERA_ADMIN = b"x-admin-token"


def huella_cliente(scope) -> str:
    """IP del cliente para el limite y la bitacora. En Render la peticion llega por Cloudflare
    (CF-Connecting-IP); si no, el primer X-Forwarded-For y, en ultimo caso, el socket."""
    cabeceras = dict(scope.get("headers", []))
    ip = cabeceras.get(b"cf-connecting-ip", b"").decode("latin-1").strip()
    if not ip:
        ip = cabeceras.get(b"x-forwarded-for", b"").decode("latin-1").split(",")[0].strip()
    if not ip and scope.get("client"):
        ip = scope["client"][0]
    return ip or "desconocido"


def seudonimo(ip: str) -> str:
    """En la bitacora solo va un SHA-256 truncado de la IP, nunca la IP en claro (RNF-06)."""
    return hashlib.sha256(ip.encode()).hexdigest()[:10]


async def _responder(send, codigo: int, detalle: str, extra: dict | None = None):
    cuerpo = json.dumps({"detail": detalle}, ensure_ascii=False).encode()
    cabeceras = [(b"content-type", b"application/json"), (b"cache-control", b"no-store")]
    for nombre, valor in (extra or {}).items():
        cabeceras.append((nombre.encode(), valor.encode()))
    await send({"type": "http.response.start", "status": codigo, "headers": cabeceras})
    await send({"type": "http.response.body", "body": cuerpo})


def requiere_admin(metodo: str, ruta: str) -> bool:
    """Proteccion por defecto: toda escritura en /api salvo los POST publicos de lectura."""
    if not ruta.startswith("/api/"):
        return False
    ruta = ruta.rstrip("/")
    if metodo in METODOS_DE_LECTURA:
        return metodo == "GET" and ruta in GET_PROTEGIDOS
    return ruta not in POST_PUBLICOS


class EscrituraProtegida:
    """ADR-035 (A01/A07). En modo nube, las escrituras en /api (y la lectura del historial del
    servidor) exigen `X-Admin-Token` igual a ADMIN_TOKEN, comparado en tiempo constante.
    Sin cabecera: 401. Token incorrecto o ADMIN_TOKEN vacio: 403 (falla de forma segura).
    El token no se registra. En local no actua."""

    def __init__(self, app, activo: bool = False, token: str = ""):
        self.app = app
        self._activo = activo
        self._token = token.encode()

    async def __call__(self, scope, receive, send):
        if not (self._activo and scope["type"] == "http"):
            await self.app(scope, receive, send)
            return
        metodo, ruta = scope["method"], scope["path"]
        if not requiere_admin(metodo, ruta):
            await self.app(scope, receive, send)
            return
        aportado = dict(scope.get("headers", [])).get(CABECERA_ADMIN, b"").strip()
        cliente = seudonimo(huella_cliente(scope))
        if not aportado:
            log_seguridad.warning(
                "[SEGURIDAD] rechazada 401 %s %s cliente=%s", metodo, ruta, cliente
            )
            await _responder(
                send,
                401,
                "Esta operación requiere el token de administración (cabecera X-Admin-Token). "
                "En la versión pública la consulta es de solo lectura.",
                {"www-authenticate": 'ApiKey header="X-Admin-Token"'},
            )
            return
        if not self._token or not hmac.compare_digest(aportado, self._token):
            log_seguridad.warning(
                "[SEGURIDAD] rechazada 403 %s %s cliente=%s", metodo, ruta, cliente
            )
            await _responder(
                send,
                403,
                "Token de administración no válido o administración deshabilitada "
                "en este servicio.",
            )
            return
        log_seguridad.info("[SEGURIDAD] autorizada %s %s cliente=%s", metodo, ruta, cliente)
        await self.app(scope, receive, send)


class LimitePeticiones:
    """ADR-037 (A04). Ventana deslizante de 60 s por IP y ruta, en memoria (un solo proceso en
    Render). Al superarla: 429 con Retry-After. Exentas las peticiones con token de pruebas
    valido (origen humo/carga, HU-09). Limite 0 = sin limite."""

    MAXIMO_CLIENTES = 10_000

    def __init__(self, app, limites: dict[str, int] | None = None, reloj=time.monotonic):
        self.app = app
        self._limites = {r: n for r, n in (limites or {}).items() if n and n > 0}
        self._reloj = reloj
        self._ventanas: dict[tuple[str, str], deque] = {}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST":
            await self.app(scope, receive, send)
            return
        ruta = scope["path"].rstrip("/")
        limite = self._limites.get(ruta)
        if not limite or scope.get("state", {}).get("origen_pruebas"):
            await self.app(scope, receive, send)
            return
        ip = huella_cliente(scope)
        ahora = self._reloj()
        if len(self._ventanas) > self.MAXIMO_CLIENTES:
            self._purgar(ahora)
        ventana = self._ventanas.setdefault((ip, ruta), deque())
        while ventana and ahora - ventana[0] >= 60:
            ventana.popleft()
        if len(ventana) >= limite:
            espera = max(1, int(60 - (ahora - ventana[0])) + 1)
            log_seguridad.warning("[SEGURIDAD] 429 %s cliente=%s", ruta, seudonimo(ip))
            await _responder(
                send,
                429,
                f"Demasiadas consultas seguidas: el límite es {limite} por minuto. "
                f"Inténtalo de nuevo en {espera} s.",
                {"retry-after": str(espera)},
            )
            return
        ventana.append(ahora)
        await self.app(scope, receive, send)

    def _purgar(self, ahora: float):
        for clave in [c for c, v in self._ventanas.items() if not v or ahora - v[-1] >= 60]:
            del self._ventanas[clave]


class CabeceraHsts:
    """A02/A05: HSTS solo en modo nube (en 127.0.0.1 por HTTP no tiene sentido)."""

    def __init__(self, app, activo: bool = False):
        self.app = app
        self._activo = activo

    async def __call__(self, scope, receive, send):
        if not (self._activo and scope["type"] == "http"):
            await self.app(scope, receive, send)
            return

        async def enviar(mensaje):
            if mensaje["type"] == "http.response.start":
                mensaje["headers"] = list(mensaje.get("headers", [])) + [
                    (b"strict-transport-security", b"max-age=31536000; includeSubDomains")
                ]
            await send(mensaje)

        await self.app(scope, receive, enviar)
