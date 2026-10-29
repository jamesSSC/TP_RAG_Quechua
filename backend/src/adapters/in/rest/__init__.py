"""Adaptador de entrada REST: un controlador por recurso.

Cada controlador solo traduce HTTP <-> DTO y depende del puerto de entrada, que obtiene del
contenedor a traves de `dependencias`. No importa casos de uso ni adaptadores de salida.
"""

from . import (
    consultas_controller,
    corpus_controller,
    fuentes_controller,
    historial_controller,
    prediccion_controller,
    sistema_controller,
)

routers = [
    sistema_controller.router,
    consultas_controller.router,
    historial_controller.router,
    corpus_controller.router,
    fuentes_controller.router,
    prediccion_controller.router,
]
