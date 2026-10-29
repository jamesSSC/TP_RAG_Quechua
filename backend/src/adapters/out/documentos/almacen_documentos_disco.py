import hashlib
import json
from pathlib import Path

from application.ports.out.almacen_documentos_port import (
    AlmacenDocumentosPort,
    DocumentoAlmacenado,
)

MANIFIESTO = "manifiesto.json"


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
        sha = hashlib.sha256(contenido).hexdigest()
        manifiesto = self._leer()
        for existente, huella in manifiesto.items():
            if huella == sha:
                return DocumentoAlmacenado(nombre=existente, sha256=sha, duplicado=True)

        self._carpeta.mkdir(parents=True, exist_ok=True)
        # `.name` impide que el nombre recibido escape de la carpeta (RS-04).
        limpio = Path(nombre.replace("\\", "/")).name or "documento.pdf"
        if limpio in manifiesto:
            ruta = Path(limpio)
            limpio = f"{ruta.stem}-{sha[:8]}{ruta.suffix}"
        (self._carpeta / limpio).write_bytes(contenido)
        manifiesto[limpio] = sha
        (self._carpeta / MANIFIESTO).write_text(
            json.dumps(manifiesto, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )
        return DocumentoAlmacenado(nombre=limpio, sha256=sha, duplicado=False)
