import logging
from datetime import date

from application.ports import IngestarDocumentoPort, ResultadoIngesta
from application.ports.out.almacen_documentos_port import AlmacenDocumentosPort
from application.ports.out.extraccion_documental_port import ExtraccionDocumentalPort
from application.ports.out.indice_recuperacion_port import IndiceRecuperacionPort
from application.ports.out.repositorio_corpus_port import RepositorioCorpusPort
from application.ports.out.repositorio_fuentes_port import RepositorioFuentesPort
from domain.entities.fragmento import TipoFragmento
from domain.entities.fuente import Fuente
from domain.services.segmentador import Segmentador

log = logging.getLogger("rag.caso_uso")


class IngestarDocumentoUseCase(IngestarDocumentoPort):
    """RF-01, RF-02 y RF-13: incorpora un documento al corpus, lo segmenta segun su tipo,
    registra su procedencia y reconstruye el indice.

    El registro de la fuente ocurre antes de indexar: si el documento no declara
    licenciamiento, la entidad Fuente lo rechaza y nada llega al indice."""

    def __init__(
        self,
        extractor: ExtraccionDocumentalPort,
        corpus: RepositorioCorpusPort,
        indice: IndiceRecuperacionPort,
        repositorio_fuentes: RepositorioFuentesPort | None = None,
        segmentador: Segmentador | None = None,
        almacen_documentos: AlmacenDocumentosPort | None = None,
    ):
        self._extractor = extractor
        self._corpus = corpus
        self._indice = indice
        self._repositorio_fuentes = repositorio_fuentes
        self._segmentador = segmentador or Segmentador()
        self._almacen = almacen_documentos

    def ejecutar(
        self,
        contenido: bytes,
        nombre_archivo: str,
        tipo: TipoFragmento,
        titulo: str,
        entidad_publicadora: str,
        licenciamiento: str,
        derivado_ocr: bool = False,
    ) -> ResultadoIngesta:
        log.info("[CASO-USO] IngestarDocumento: tipo=%s", tipo.value)
        documento = self._extractor.extraer(contenido, nombre_archivo)

        fuente = Fuente(
            titulo=titulo,
            entidad_publicadora=entidad_publicadora,
            licenciamiento=licenciamiento,
            fecha_extraccion=date.today(),
            nombre_archivo=nombre_archivo,
            paginas_totales=documento.paginas_totales,
            paginas_con_texto=documento.paginas_con_texto,
            derivado_ocr=derivado_ocr,
        )

        if self._almacen is not None:
            guardado = self._almacen.guardar(contenido, nombre_archivo)
            log.info(
                "[DATOS] PDF guardado sha256=%s duplicado=%s",
                guardado.sha256[:12],
                guardado.duplicado,
            )

        fragmentos = self._segmentador.segmentar(documento, tipo, derivado_ocr)
        nuevos = self._corpus.agregar(fragmentos)

        if nuevos:
            self._indice.indexar(self._corpus.cargar())

        if self._repositorio_fuentes is not None:
            self._repositorio_fuentes.crear(fuente)

        log.info("[INDICE] fragmentos generados=%d nuevos=%d", len(fragmentos), nuevos)
        return ResultadoIngesta(
            fuente=fuente,
            paginas_totales=documento.paginas_totales,
            paginas_con_texto=documento.paginas_con_texto,
            fragmentos_generados=len(fragmentos),
            fragmentos_nuevos=nuevos,
            total_indexado=self._indice.total_indexado(),
        )


__all__ = ["IngestarDocumentoUseCase", "ResultadoIngesta"]
