import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from application.ports import EstadoCorpus, IngestarDocumentoPort, ReindexarCorpusPort
from domain.entities.fragmento import TipoFragmento

from . import dependencias
from .esquemas import DocumentosCorpus, ResultadoIngestaSalida

log = logging.getLogger("rag.rest")
router = APIRouter(prefix="/api")

TAMANO_MAXIMO = 60 * 1024 * 1024
TAMANO_BLOQUE = 1024 * 1024


async def _leer_con_tope(archivo: UploadFile) -> bytes:
    """Lee por bloques y corta en cuanto se supera el tope, sin cargar todo en memoria."""
    partes: list[bytes] = []
    total = 0
    while bloque := await archivo.read(TAMANO_BLOQUE):
        total += len(bloque)
        if total > TAMANO_MAXIMO:
            raise HTTPException(413, "El archivo supera el tamano maximo admitido (60 MB)")
        partes.append(bloque)
    return b"".join(partes)


def _a_salida(estado: EstadoCorpus) -> DocumentosCorpus:
    return DocumentosCorpus(documentos=estado.documentos, total_fragmentos=estado.total_fragmentos)


@router.post("/corpus/documentos", response_model=ResultadoIngestaSalida, tags=["corpus"])
async def ingestar_documento(
    archivo: UploadFile = File(...),
    titulo: str = Form(...),
    entidad_publicadora: str = Form(...),
    licenciamiento: str = Form(...),
    tipo: str = Form("lexicografico"),
    puerto: IngestarDocumentoPort = Depends(dependencias.ingestar_documento),
):
    """RF-01, RF-02 y RF-13: incorpora un PDF al corpus, lo segmenta segun su tipo y
    reconstruye el indice sin reiniciar el servicio."""
    log.info("[REST] POST /api/corpus/documentos")
    if not archivo.filename or not archivo.filename.lower().endswith(".pdf"):
        raise HTTPException(422, "Solo se admiten archivos PDF")

    contenido = await _leer_con_tope(archivo)

    try:
        tipo_fragmento = TipoFragmento(tipo)
    except ValueError:
        raise HTTPException(422, "El tipo debe ser 'lexicografico' o 'prosa'") from None

    try:
        log.info("[PUERTO-IN] IngestarDocumentoPort.ejecutar")
        resultado = puerto.ejecutar(
            contenido=contenido,
            nombre_archivo=archivo.filename,
            tipo=tipo_fragmento,
            titulo=titulo,
            entidad_publicadora=entidad_publicadora,
            licenciamiento=licenciamiento,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

    aviso = None
    if resultado.requiere_ocr:
        aviso = (
            "No se extrajo texto de ninguna pagina: el documento parece una imagen "
            "escaneada y requeriria reconocimiento optico, que no forma parte del flujo "
            "ordinario del sistema."
        )
    elif resultado.fragmentos_nuevos == 0:
        aviso = "Todos los fragmentos ya estaban en el corpus; el indice no ha cambiado."

    return ResultadoIngestaSalida(
        nombre_archivo=archivo.filename,
        titulo=titulo,
        paginas_totales=resultado.paginas_totales,
        paginas_con_texto=resultado.paginas_con_texto,
        cobertura_extraccion=round(resultado.paginas_con_texto / resultado.paginas_totales, 4)
        if resultado.paginas_totales
        else 0.0,
        fragmentos_generados=resultado.fragmentos_generados,
        fragmentos_nuevos=resultado.fragmentos_nuevos,
        total_indexado=resultado.total_indexado,
        requiere_ocr=resultado.requiere_ocr,
        aviso=aviso,
    )


@router.get("/corpus/documentos", response_model=DocumentosCorpus, tags=["corpus"])
def listar_documentos(puerto: ReindexarCorpusPort = Depends(dependencias.reindexar_corpus)):
    log.info("[REST] GET /api/corpus/documentos")
    return _a_salida(puerto.estado())


@router.post("/corpus/reindexar", response_model=DocumentosCorpus, tags=["corpus"])
def reindexar(puerto: ReindexarCorpusPort = Depends(dependencias.reindexar_corpus)):
    log.info("[REST] POST /api/corpus/reindexar")
    log.info("[PUERTO-IN] ReindexarCorpusPort.ejecutar")
    return _a_salida(puerto.ejecutar())
