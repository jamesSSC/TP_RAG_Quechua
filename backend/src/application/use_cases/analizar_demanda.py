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

    def _priorizar(self, incluir_sinteticas: bool) -> list[dict]:
        grupos: dict[str, list[float | None]] = defaultdict(list)
        for texto, probabilidad in self._repositorio.abstenciones_con_prediccion(
            incluir_sinteticas=incluir_sinteticas
        ):
            grupos[self._depurador.depurar(texto)].append(probabilidad)
        return [self._prioridad(termino, probs) for termino, probs in grupos.items()]

    @staticmethod
    def _prioridad(termino: str, probabilidades: list[float | None]) -> dict:
        conocidas = [p for p in probabilidades if p is not None]
        p_media = sum(conocidas) / len(conocidas) if conocidas else None
        peso = 1.0 - p_media if p_media is not None else 0.5
        ampliar = p_media is None or p_media < 0.5
        return {
            "termino": termino,
            "consultas": len(probabilidades),
            "probabilidad_cobertura_media": p_media,
            "demanda_insatisfecha": round(len(probabilidades) * peso, 4),
            "diagnostico": "ampliar el corpus" if ampliar else "revisar la recuperación",
        }

    def ejecutar(self, top: int = 15, incluir_sinteticas: bool = False) -> dict:
        """Por defecto solo cuenta la demanda real (origen `usuario`). Con
        `incluir_sinteticas` prioriza tambien con las consultas de prueba y lo rotula como
        demostracion: nunca es el modo predeterminado."""
        por_origen = self._repositorio.conteo_por_origen()
        sinteticas = sum(n for origen, n in por_origen.items() if origen != "usuario")
        demostracion = incluir_sinteticas and sinteticas > 0
        estadisticas = self._repositorio.estadisticas(incluir_sinteticas=incluir_sinteticas)
        total = estadisticas["total"]
        log.info("[CASO-USO] AnalizarDemanda: %d consultas contadas (%s)", total, por_origen)
        base = {
            "minimo": self._minimo,
            "modo": "demostracion" if demostracion else "real",
            "aviso": (
                f"Demostración con {sinteticas} consultas generadas por la prueba de carga; "
                "no es demanda real"
                if demostracion
                else None
            ),
            "por_origen": por_origen,
            "estadisticas": estadisticas,
        }
        if total < self._minimo:
            ajenas = (
                f" Otras {sinteticas} consultas de prueba no cuentan como demanda real."
                if sinteticas and not incluir_sinteticas
                else ""
            )
            return {
                **base,
                "suficiente": False,
                "mensaje": (
                    f"Historial insuficiente: hay {total} consultas registradas y se necesitan "
                    f"al menos {self._minimo}. No se emite priorización.{ajenas}"
                ),
                "prioridades": [],
            }

        prioridades = self._priorizar(incluir_sinteticas)
        prioridades.sort(key=lambda p: (-p["demanda_insatisfecha"], p["termino"]))
        return {
            **base,
            "suficiente": True,
            "mensaje": None,
            "terminos_distintos_no_cubiertos": len(prioridades),
            "prioridades": prioridades[:top],
        }
