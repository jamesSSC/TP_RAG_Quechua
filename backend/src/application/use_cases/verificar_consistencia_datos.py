import logging

from application.ports.out.almacen_documentos_port import AlmacenDocumentosPort
from application.ports.out.repositorio_corpus_port import RepositorioCorpusPort
from application.ports.out.repositorio_fuentes_port import RepositorioFuentesPort

log = logging.getLogger("rag.caso_uso")


class VerificarConsistenciaDatos:
    """Cruza las fuentes registradas, los documentos con fragmentos y los PDF guardados.
    Solo informa: nunca borra ni corrige nada (BUG-01).

    Los documentos del corpus base no tienen fuente en la base de datos ni PDF guardado (se
    registran en el manifiesto del corpus), por lo que no cuentan como discrepancia."""

    def __init__(
        self,
        corpus: RepositorioCorpusPort,
        repositorio_fuentes: RepositorioFuentesPort | None,
        almacen: AlmacenDocumentosPort | None,
    ):
        self._corpus = corpus
        self._fuentes = repositorio_fuentes
        self._almacen = almacen

    @staticmethod
    def _avisos_de_fuentes(fuentes, pdfs, con_fragmentos) -> list[str]:
        avisos = []
        for nombre in sorted(fuentes or ()):
            if nombre not in con_fragmentos:
                avisos.append(f"La fuente '{nombre}' no tiene fragmentos en el corpus")
            if pdfs is not None and nombre not in pdfs:
                avisos.append(
                    f"La fuente '{nombre}' no tiene su PDF guardado en la carpeta de datos"
                )
        return avisos

    @staticmethod
    def _avisos_de_pdfs(fuentes, pdfs, con_fragmentos) -> list[str]:
        avisos = []
        for nombre in sorted(pdfs or ()):
            if nombre not in con_fragmentos:
                avisos.append(f"El PDF guardado '{nombre}' no tiene fragmentos en el corpus")
            if fuentes is not None and nombre not in fuentes:
                avisos.append(f"El PDF guardado '{nombre}' no tiene fuente registrada")
        return avisos

    def ejecutar(self) -> list[str]:
        con_fragmentos = set(self._corpus.documentos())
        fuentes = {f.nombre_archivo for f in self._fuentes.listar()} if self._fuentes else None
        pdfs = set(self._almacen.listar()) if self._almacen else None

        avisos = self._avisos_de_fuentes(fuentes, pdfs, con_fragmentos)
        avisos += self._avisos_de_pdfs(fuentes, pdfs, con_fragmentos)
        for aviso in avisos:
            log.warning("[CONSISTENCIA] AVISO: %s", aviso)
        return avisos
