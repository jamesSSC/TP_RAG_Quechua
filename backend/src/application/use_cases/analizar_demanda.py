import logging
from collections import defaultdict

from application.ports import AnalizarDemandaPort
from application.ports.out.repositorio_consultas_port import RepositorioConsultasPort
from domain.services.depurador_consulta import DepuradorConsulta

log = logging.getLogger("rag.caso_uso")

# HU-09, escenario 2: por debajo de este volumen el sistema no emite priorizacion.
MINIMO_CONSULTAS = 100


class AnalizarDemandaUseCase(AnalizarDemandaPort):
    """HU-09 / RF-16 · que material conviene incorporar.

    Agrupa las consultas en las que el sistema se abstuvo por termino depurado y las ordena
    por demanda insatisfecha ponderada: frecuencia x (1 - probabilidad media de cobertura
    estimada por el modelo de RF-14). Un termino muy pedido que el modelo considera fuera del
    corpus es el candidato mas claro a ampliar el corpus; uno que el modelo cree cubierto
    apunta mas bien a un problema de recuperacion que a una falta de material."""

    def __init__(
        self,
        repositorio: RepositorioConsultasPort,
        depurador: DepuradorConsulta | None = None,
        minimo: int = MINIMO_CONSULTAS,
    ):
        self._repositorio = repositorio
        self._depurador = depurador or DepuradorConsulta()
        self._minimo = minimo

    def ejecutar(self, top: int = 15) -> dict:
        estadisticas = self._repositorio.estadisticas()
        total = estadisticas["total"]
        log.info("[CASO-USO] AnalizarDemanda: %d consultas registradas", total)
        if total < self._minimo:
            return {
                "suficiente": False,
                "minimo": self._minimo,
                "mensaje": (
                    f"Historial insuficiente: hay {total} consultas registradas y se necesitan "
                    f"al menos {self._minimo}. No se emite priorización."
                ),
                "estadisticas": estadisticas,
                "prioridades": [],
            }

        grupos: dict[str, list[float | None]] = defaultdict(list)
        for texto, probabilidad in self._repositorio.abstenciones_con_prediccion():
            grupos[self._depurador.depurar(texto)].append(probabilidad)

        prioridades = []
        for termino, probabilidades in grupos.items():
            conocidas = [p for p in probabilidades if p is not None]
            p_media = sum(conocidas) / len(conocidas) if conocidas else None
            peso = 1.0 - p_media if p_media is not None else 0.5
            prioridades.append(
                {
                    "termino": termino,
                    "consultas": len(probabilidades),
                    "probabilidad_cobertura_media": p_media,
                    "demanda_insatisfecha": round(len(probabilidades) * peso, 4),
                    "diagnostico": (
                        "ampliar el corpus"
                        if p_media is None or p_media < 0.5
                        else "revisar la recuperación"
                    ),
                }
            )
        prioridades.sort(key=lambda p: (-p["demanda_insatisfecha"], p["termino"]))
        return {
            "suficiente": True,
            "minimo": self._minimo,
            "mensaje": None,
            "estadisticas": estadisticas,
            "terminos_distintos_no_cubiertos": len(prioridades),
            "prioridades": prioridades[:top],
        }
