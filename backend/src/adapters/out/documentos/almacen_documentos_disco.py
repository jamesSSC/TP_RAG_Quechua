import hashlib
import json
import logging
from pathlib import Path

from application.ports.out.almacen_documentos_port import (
    AlmacenDocumentosPort,
    DocumentoAlmacenado,
    ErrorAlmacenDocumentos,
)

log = logging.getLogger("rag.almacen")

MANIFIESTO = "manifiesto.json"
TAMANO_MAXIMO = 60 * 1024 * 1024
# Nombres de dispositivo de Windows: no son archivos validos con ninguna extension.
RESERVADOS = (
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)


def _nombre_seguro(nombre: str) -> str:
    """Devuelve el nombre admitido o lanza ErrorAlmacenDocumentos. Solo `.pdf`; nada de
    rutas con `..`, flujos alternos NTFS (`:`), nombres reservados ni el manifiesto."""
    bruto = (nombre or "").replace("\\", "/")
    if not bruto.strip():
        raise ErrorAlmacenDocumentos("El nombre del archivo esta vacio")
    if ".." in bruto.split("/"):
        raise ErrorAlmacenDocumentos("El nombre del archivo no puede contener '..'")
    if ":" in bruto or any(ord(c) < 32 for c in bruto):
        raise ErrorAlmacenDocumentos("El nombre del archivo contiene caracteres no admitidos")
    limpio = Path(bruto).name
    if not limpio.strip() or limpio in {".", ".."}:
        raise ErrorAlmacenDocumentos("El nombre del archivo no es valido")
    if limpio != limpio.rstrip(" ."):
        raise ErrorAlmacenDocumentos("El nombre del archivo no puede terminar en punto o espacio")
    if limpio.lower() == MANIFIESTO:
        raise ErrorAlmacenDocumentos("Nombre reservado por el sistema")
    if Path(limpio).suffix.lower() != ".pdf" or Path(limpio).stem in {"", " "}:
        raise ErrorAlmacenDocumentos("Solo se admiten archivos con extension .pdf")
    if limpio.split(".")[0].strip().upper() in RESERVADOS:
        raise ErrorAlmacenDocumentos("Nombre reservado del sistema operativo")
    return limpio


class AlmacenDocumentosDisco(AlmacenDocumentosPort):
    """PDF en `<carpeta>/<nombre>` y manifiesto local `nombre -> sha256`."""

    def __init__(self, carpeta: Path):
        self._carpeta = carpeta

    def _leer(self) -> dict[str, str]:
        ruta = self._carpeta / MANIFIESTO
        if not ruta.exists():
            return {}
        registrado = json.loads(ruta.read_text(encoding="utf-8"))
        # Solo cuentan los PDF que siguen en disco: si alguien borra uno, se nota.
        return {n: h for n, h in registrado.items() if (self._carpeta / n).is_file()}

    def listar(self) -> dict[str, str]:
        return self._leer()

    def guardar(self, contenido: bytes, nombre: str) -> DocumentoAlmacenado:
        limpio = _nombre_seguro(nombre)
        if len(contenido) > TAMANO_MAXIMO:
            raise ErrorAlmacenDocumentos(
                f"El archivo supera el tamano maximo admitido ({TAMANO_MAXIMO // (1024 * 1024)} MB)"
            )
        sha = hashlib.sha256(contenido).hexdigest()
        try:
            return self._guardar(contenido, limpio, sha)
        except PermissionError as exc:
            log.error("[ALMACEN] sin permisos sobre %s: %s", self._carpeta, exc)
            raise ErrorAlmacenDocumentos(
                "Sin permisos para guardar el documento en la carpeta de datos"
            ) from exc
        except OSError as exc:
            log.error("[ALMACEN] no se pudo guardar %s: %s", limpio, exc)
            raise ErrorAlmacenDocumentos(
                "No se pudo guardar el documento en la carpeta de datos"
            ) from exc

    def _guardar(self, contenido: bytes, limpio: str, sha: str) -> DocumentoAlmacenado:
        manifiesto = self._leer()
        for existente, huella in manifiesto.items():
            if huella == sha:
                return DocumentoAlmacenado(nombre=existente, sha256=sha, duplicado=True)

        self._carpeta.mkdir(parents=True, exist_ok=True)
        destino = limpio
        if (self._carpeta / destino).exists():
            # Un archivo con ese nombre ya esta en disco (otro documento o un huerfano que el
            # manifiesto no conoce): nunca se sobrescribe en silencio.
            if hashlib.sha256((self._carpeta / destino).read_bytes()).hexdigest() == sha:
                log.warning("[ALMACEN] %s existia sin registro y es identico: se adopta", destino)
                manifiesto[destino] = sha
                self._escribir_manifiesto(manifiesto)
                return DocumentoAlmacenado(nombre=destino, sha256=sha, duplicado=False)
            ruta = Path(destino)
            destino = f"{ruta.stem}-{sha[:8]}{ruta.suffix}"
            log.warning(
                "[ALMACEN] %s ya existe (huerfano u otro contenido); se guarda como %s",
                limpio,
                destino,
            )
            if (self._carpeta / destino).exists():
                raise ErrorAlmacenDocumentos(
                    f"Ya existen archivos con el nombre '{limpio}' y no se sobrescriben"
                )
        (self._carpeta / destino).write_bytes(contenido)
        manifiesto[destino] = sha
        self._escribir_manifiesto(manifiesto)
        return DocumentoAlmacenado(nombre=destino, sha256=sha, duplicado=False)

    def _escribir_manifiesto(self, manifiesto: dict[str, str]) -> None:
        (self._carpeta / MANIFIESTO).write_text(
            json.dumps(manifiesto, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )
