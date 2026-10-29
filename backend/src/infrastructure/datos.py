import logging
import shutil
from pathlib import Path

log = logging.getLogger(__name__)


def preparar_carpeta_datos(carpeta: Path, corpus_base: Path, ruta_corpus: Path) -> bool:
    """Crea la carpeta de datos modificables y, en el primer arranque, copia en ella el
    corpus base empaquetado (de solo lectura). Devuelve True si copio.

    Nunca sobrescribe una copia existente y no toca el corpus base."""
    (carpeta / "documentos").mkdir(parents=True, exist_ok=True)
    if ruta_corpus.exists() or not corpus_base.exists():
        return False
    if corpus_base.resolve() == ruta_corpus.resolve():
        return False
    ruta_corpus.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(corpus_base, ruta_corpus)
    log.info("[DATOS] primer arranque: corpus base copiado a %s", ruta_corpus)
    return True
