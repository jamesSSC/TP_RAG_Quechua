import logging

from fastapi import APIRouter, Depends

from application.ports import ConsultarCorpusPort
from domain.entities.fragmento import FragmentoRecuperado

from . import dependencias
from .esquemas import ConsultaEntrada, RespaldoSalida, RespuestaSalida

log = logging.getLogger("rag.rest")
router = APIRouter(prefix="/api")

ROTULO_PASAJES = "no es una respuesta"


def _respaldo(r: FragmentoRecuperado, rotulo: str | None = None) -> RespaldoSalida:
    return RespaldoSalida(
        fragmento_id=r.id,
        texto=r.texto,
        documento=r.procedencia.documento,
        pagina=r.procedencia.pagina,
        puntuacion=round(r.puntuacion.valor, 4),
        similitud=round(r.puntuacion.valor, 4),
        derivado_ocr=r.procedencia.derivado_ocr,
        coincidencia_lema=r.coincidencia_lema,
        rotulo=rotulo,
    )


@router.post("/consultas", response_model=RespuestaSalida, tags=["consulta"])
def consultar(
    entrada: ConsultaEntrada,
    puerto: ConsultarCorpusPort = Depends(dependencias.consultar_corpus),
):
    """HU-03, HU-06 y HU-07. La respuesta no puede emitirse sin los campos de documento y
    pagina cuando no es una abstencion: el contrato lo hace verificable."""
    log.info("[REST] POST /api/consultas")
    log.info("[PUERTO-IN] ConsultarCorpusPort.ejecutar")
    respuesta = puerto.ejecutar(entrada.texto)
    return RespuestaSalida(
        consulta_id=respuesta.consulta_id,
        texto=respuesta.texto,
        abstenida=respuesta.abstenida,
        idioma=respuesta.idioma.value,
        similitud_maxima=round(respuesta.similitud_maxima, 4),
        aviso=respuesta.aviso,
        consulta_traducida=respuesta.consulta_traducida,
        respaldo=[_respaldo(r) for r in respuesta.respaldo],
        pasajes=[_respaldo(r, ROTULO_PASAJES) for r in respuesta.pasajes],
        via_respaldo=respuesta.via_respaldo,
        umbral=respuesta.umbral,
        latencia_ms=respuesta.latencia_ms,
        lecturas_traduccion=respuesta.lecturas_traduccion,
        traduccion_usada=respuesta.consulta_traducida,
        generador_invocado=respuesta.generador_invocado,
        aviso_generacion=respuesta.aviso_generacion,
        redactado_por=respuesta.redactado_por,
        motivo_redaccion=respuesta.motivo_redaccion,
        probabilidad_cobertura=_redondear(respuesta.probabilidad_cobertura),
        probabilidad_pasajes=_redondear(respuesta.probabilidad_pasajes),
        abstencion_por_predictor=respuesta.abstencion_por_predictor,
    )


def _redondear(valor: float | None) -> float | None:
    return None if valor is None else round(valor, 4)
