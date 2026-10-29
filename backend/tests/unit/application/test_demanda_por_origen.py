"""HU-09 (ADR-013): la demanda real nunca cuenta consultas sinteticas."""

from application.use_cases.analizar_demanda import AnalizarDemandaUseCase
from domain.entities.consulta import Consulta
from domain.value_objects.origen_consulta import OrigenConsulta
from tests.unit.application.test_prediccion_con_fakes import RepositorioDemanda

ABSTENCIONES = [("¿cómo se dice dron?", 0.1), ("¿cómo se dice dron?", 0.2)]


class RepoPorOrigen(RepositorioDemanda):
    """Doble del puerto: `usuario` y `carga` con el conteo que se le indique."""

    def __init__(self, usuario, carga):
        super().__init__(usuario + carga, ABSTENCIONES)
        self.por_origen = {"usuario": usuario, "carga": carga}
        self.pidio_sinteticas = None

    def conteo_por_origen(self):
        return {k: v for k, v in self.por_origen.items() if v}

    def estadisticas(self, incluir_sinteticas=False):
        self.pidio_sinteticas = incluir_sinteticas
        total = sum(self.por_origen.values()) if incluir_sinteticas else self.por_origen["usuario"]
        return {"total": total, "abstenidas": len(self._abst)}


def test_la_consulta_nace_con_origen_usuario():
    assert Consulta(texto="zorro").origen is OrigenConsulta.USUARIO


def test_los_origenes_validos():
    assert {o.value for o in OrigenConsulta} == {"usuario", "carga", "arnes", "humo"}


def test_99_de_usuario_y_800_de_carga_declaran_insuficiencia():
    salida = AnalizarDemandaUseCase(RepoPorOrigen(99, 800)).ejecutar()
    assert salida["suficiente"] is False
    assert salida["prioridades"] == []
    assert salida["modo"] == "real"
    assert salida["por_origen"] == {"usuario": 99, "carga": 800}
    assert "99" in salida["mensaje"] and "no cuentan" in salida["mensaje"]


def test_100_de_usuario_priorizan_sin_rotular_demostracion():
    salida = AnalizarDemandaUseCase(RepoPorOrigen(100, 800)).ejecutar()
    assert salida["suficiente"] is True
    assert salida["modo"] == "real" and salida["aviso"] is None
    assert salida["prioridades"][0]["termino"] == "dron"


def test_incluir_sinteticas_prioriza_y_rotula_demostracion():
    repo = RepoPorOrigen(99, 800)
    salida = AnalizarDemandaUseCase(repo).ejecutar(incluir_sinteticas=True)
    assert repo.pidio_sinteticas is True
    assert salida["suficiente"] is True
    assert salida["modo"] == "demostracion"
    assert salida["aviso"] == (
        "Demostración con 800 consultas generadas por la prueba de carga; no es demanda real"
    )
    assert salida["prioridades"]


def test_por_defecto_no_se_incluyen_sinteticas():
    repo = RepoPorOrigen(150, 800)
    AnalizarDemandaUseCase(repo).ejecutar()
    assert repo.pidio_sinteticas is False


def test_incluir_sinteticas_sin_sinteticas_no_rotula_demostracion():
    salida = AnalizarDemandaUseCase(RepoPorOrigen(150, 0)).ejecutar(incluir_sinteticas=True)
    assert salida["modo"] == "real" and salida["aviso"] is None
