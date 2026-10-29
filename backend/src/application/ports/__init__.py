"""Puertos de la capa de aplicacion.

`in` es palabra reservada de Python: el paquete `application.ports.in` no puede escribirse
en una sentencia `import`. Por eso los puertos de entrada se reexportan aqui por nombre y el
resto del codigo hace `from application.ports import ConsultarCorpusPort`. Los puertos de
salida viven en `application.ports.out` y se importan de la forma habitual.
"""

from importlib import import_module

_entrada = "application.ports.in."

ConsultarCorpusPort = import_module(_entrada + "consultar_corpus_port").ConsultarCorpusPort

_ingesta = import_module(_entrada + "ingestar_documento_port")
IngestarDocumentoPort = _ingesta.IngestarDocumentoPort
ResultadoIngesta = _ingesta.ResultadoIngesta

GestionarFuentesPort = import_module(_entrada + "gestionar_fuentes_port").GestionarFuentesPort

ConsultarHistorialPort = import_module(_entrada + "consultar_historial_port").ConsultarHistorialPort

_reindexar = import_module(_entrada + "reindexar_corpus_port")
ReindexarCorpusPort = _reindexar.ReindexarCorpusPort
EstadoCorpus = _reindexar.EstadoCorpus

PredecirConsultaPort = import_module(_entrada + "predecir_consulta_port").PredecirConsultaPort

AnalizarDemandaPort = import_module(_entrada + "analizar_demanda_port").AnalizarDemandaPort

__all__ = [
    "AnalizarDemandaPort",
    "PredecirConsultaPort",
    "ConsultarCorpusPort",
    "ConsultarHistorialPort",
    "EstadoCorpus",
    "GestionarFuentesPort",
    "IngestarDocumentoPort",
    "ReindexarCorpusPort",
    "ResultadoIngesta",
]
