"""Composition root: el unico lugar donde el dominio se conecta con tecnologias concretas.

Cableado puertos -> implementaciones (inyeccion de dependencias):

    ConsultarCorpusPort    -> ConsultarCorpusUseCase    (indice, generador, evaluador, ...)
    IngestarDocumentoPort  -> IngestarDocumentoUseCase  (extractor, corpus, indice, fuentes)
    ReindexarCorpusPort    -> ReindexarCorpusUseCase    (corpus, indice)
    ConsultarHistorialPort -> ConsultarHistorialUseCase (repositorio de consultas; opcional)
    GestionarFuentesPort   -> GestionarFuentesUseCase   (repositorio de fuentes; opcional)

Sustituir PostgreSQL por SQLite, u Ollama por el motor de inferencia embebido del
incremento movil, se resuelve aqui sin tocar el nucleo ni los casos de uso.
"""

import logging

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker

from adapters.out.documentos.almacen_documentos_disco import AlmacenDocumentosDisco
from adapters.out.documentos.corpus_jsonl import CorpusJsonl
from adapters.out.documentos.extractor_pdf import ExtractorPdf
from adapters.out.generacion.generador_literal import GeneradorLiteral
from adapters.out.generacion.ollama_generador import OllamaGenerador
from adapters.out.idioma.detector_idioma_heuristico import (
    DetectorIdiomaHeuristico,
)
from adapters.out.persistencia.modelos import COLUMNAS_HU09, COLUMNAS_PMV2, Base
from adapters.out.persistencia.repositorio_consultas_postgres import (
    RepositorioConsultasPostgres,
    instalar_procedimientos,
)
from adapters.out.persistencia.repositorio_consultas_sqlalchemy import (
    RepositorioConsultasSqlAlchemy,
)
from adapters.out.persistencia.repositorio_fuentes_postgres import (
    RepositorioFuentesPostgres,
)
from adapters.out.prediccion.predictor_sklearn import PredictorSklearn
from adapters.out.recuperacion.indice_hibrido_lexico import IndiceHibridoLexico
from adapters.out.traduccion.traductor_tabla import TraductorTabla
from application.use_cases.analizar_demanda import AnalizarDemandaUseCase
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase
from application.use_cases.consultar_historial import ConsultarHistorialUseCase
from application.use_cases.gestionar_fuentes import GestionarFuentesUseCase
from application.use_cases.ingestar_documento import IngestarDocumentoUseCase
from application.use_cases.predecir_consulta import PredecirConsultaUseCase
from application.use_cases.reindexar_corpus import ReindexarCorpusUseCase
from application.use_cases.verificar_consistencia_datos import VerificarConsistenciaDatos
from domain.services.evaluador_confianza import EvaluadorConfianza
from domain.value_objects.origen_consulta import OrigenConsulta
from infrastructure.config import configuracion
from infrastructure.datos import preparar_carpeta_datos

log = logging.getLogger(__name__)


class Contenedor:
    def __init__(self, generador: str = "ollama", origen: OrigenConsulta | None = None):
        """`generador`: "ollama" (API), "literal" (sin modelo) o "auto" (Ollama si responde).

        `origen`: de quien son las consultas que registra este proceso (HU-09). Por defecto
        el de la configuracion del servidor (`usuario`); los scripts de carga y de humo lo
        fijan al construir. El cliente de la API nunca lo elige."""
        self.origen = origen or OrigenConsulta(configuracion.origen_consultas)
        preparar_carpeta_datos(
            configuracion.carpeta_datos,
            configuracion.ruta_corpus_base,
            configuracion.ruta_corpus,
        )
        self.corpus = CorpusJsonl(configuracion.ruta_corpus)
        self.almacen_documentos = AlmacenDocumentosDisco(configuracion.ruta_documentos)
        self.indice = IndiceHibridoLexico()
        total = self.indice.indexar(self.corpus.cargar())
        log.info("[INDICE] construido con %s fragmentos", total)

        self.extractor = ExtractorPdf()

        self.generador = OllamaGenerador(
            url_base=configuracion.ollama_url, modelo=configuracion.ollama_modelo
        )
        if generador == "literal" or (generador == "auto" and not self.generador.disponible()):
            # Sin modelo (CLI, pruebas, equipo sin Ollama) la respuesta se compone con el
            # texto literal del fragmento; la salvaguarda no cambia: el generador solo
            # se invoca si hay respaldo.
            log.warning("[GENERADOR] sin Ollama: se compone el texto literal del fragmento")
            self.generador = GeneradorLiteral()
        # La traduccion de la consulta se resuelve por tabla precalculada y no por
        # modelo: sobre el subconjunto D alcanza 100 % de recall frente al 95 % del
        # mismo modelo en el momento, sin coste de inferencia y de forma revisable.
        self.traductor = TraductorTabla(configuracion.ruta_tabla_traduccion)
        self.evaluador = EvaluadorConfianza(umbral=configuracion.umbral_abstencion)
        self.detector = DetectorIdiomaHeuristico()
        self.predictor_cobertura = PredictorSklearn(configuracion.ruta_modelo_cobertura)
        self.predictor_pasajes = PredictorSklearn(configuracion.ruta_modelo_pasajes)

        self.repositorio_consultas = None
        self.consultar_historial = None
        self.gestionar_fuentes = None
        self.repositorio_fuentes = None
        self.analizar_demanda = None
        self.base_datos_disponible = self._conectar_base_datos()

        self.reindexar_corpus = ReindexarCorpusUseCase(corpus=self.corpus, indice=self.indice)
        self.ingestar_documento = IngestarDocumentoUseCase(
            extractor=self.extractor,
            corpus=self.corpus,
            indice=self.indice,
            repositorio_fuentes=self.repositorio_fuentes,
            almacen_documentos=self.almacen_documentos,
        )
        self.avisos_consistencia = self._verificar_consistencia()

        self.consultar_corpus = ConsultarCorpusUseCase(
            indice=self.indice,
            generador=self.generador,
            evaluador=self.evaluador,
            detector_idioma=self.detector,
            repositorio=self.repositorio_consultas,
            traductor=self.traductor,
            k=configuracion.fragmentos_recuperados,
            predictor_cobertura=self.predictor_cobertura,
            predictor_pasajes=self.predictor_pasajes,
            probabilidad_minima_cobertura=configuracion.probabilidad_minima_cobertura,
            probabilidad_minima_pasajes=configuracion.probabilidad_minima_pasajes,
            origen=self.origen,
        )
        self.predecir_consulta = PredecirConsultaUseCase(
            caracteristicas=self.consultar_corpus.caracteristicas,
            predictor_cobertura=self.predictor_cobertura,
            predictor_pasajes=self.predictor_pasajes,
            corte_cobertura=configuracion.probabilidad_minima_cobertura,
            corte_pasajes=configuracion.probabilidad_minima_pasajes,
        )

    def estado(self) -> dict:
        return {
            "fragmentos_indexados": self.indice.total_indexado(),
            "umbral_abstencion": self.evaluador.umbral,
            "generador_disponible": self.generador.disponible(),
            "base_datos_disponible": self.base_datos_disponible,
            "modelo": configuracion.ollama_modelo,
            "predictores_disponibles": self.predictor_cobertura.disponible()
            and self.predictor_pasajes.disponible(),
            "consistencia": {
                "estado": "avisos" if self.avisos_consistencia else "ok",
                "avisos": self.avisos_consistencia,
            },
            **self._rotulo_de_demostracion(),
        }

    def _rotulo_de_demostracion(self) -> dict:
        """HU-09: si la base tiene mayoritariamente consultas de prueba, la interfaz lo dice."""
        por_origen: dict[str, int] = {}
        if self.repositorio_consultas is not None:
            try:
                por_origen = self.repositorio_consultas.conteo_por_origen()
            except Exception as exc:  # noqa: BLE001
                log.warning("[REPOSITORIO] no se pudo contar por origen: %s", exc)
        total = sum(por_origen.values())
        sinteticas = total - por_origen.get("usuario", 0)
        return {
            "consultas_por_origen": por_origen,
            "base_demostracion": total > 0 and sinteticas * 2 > total,
        }

    def _verificar_consistencia(self) -> list[str]:
        try:
            # Solo informa; nunca borra ni corrige nada.
            return VerificarConsistenciaDatos(
                self.corpus, self.repositorio_fuentes, self.almacen_documentos
            ).ejecutar()
        except Exception as exc:  # noqa: BLE001
            log.warning("[CONSISTENCIA] no se pudo verificar: %s", exc)
            return []

    @staticmethod
    def _migrar_columnas_pmv2(motor) -> None:
        existentes = {c["name"] for c in inspect(motor).get_columns("consultas")}
        faltantes = {
            n: t for n, t in {**COLUMNAS_PMV2, **COLUMNAS_HU09}.items() if n not in existentes
        }
        if not faltantes:
            return
        with motor.begin() as conexion:
            for nombre, tipo in faltantes.items():
                conexion.execute(text(f"ALTER TABLE consultas ADD COLUMN {nombre} {tipo}"))
        log.info("[REPOSITORIO] columnas añadidas: %s", ", ".join(faltantes))

    def _conectar_base_datos(self) -> bool:
        try:
            # SQLite atiende desde varios hilos del servidor, de modo que hay que
            # levantar la comprobacion de hilo que trae por defecto; PostgreSQL no la
            # necesita ni la admite.
            opciones = (
                # `timeout`: espera de hasta 30 s a que se libere un bloqueo de escritura.
                {"connect_args": {"check_same_thread": False, "timeout": 30}}
                if configuracion.base_datos == "sqlite"
                else {"pool_pre_ping": True}
            )
            motor = create_engine(configuracion.url_base_datos, **opciones)
            if configuracion.base_datos == "sqlite":
                # WAL: las lecturas no bloquean a la escritura y varias consultas simultaneas
                # pueden registrar su historial sin "database is locked".
                @event.listens_for(motor, "connect")
                def _wal(conexion, _registro):
                    conexion.execute("PRAGMA journal_mode=WAL")
                    conexion.execute("PRAGMA synchronous=NORMAL")

            with motor.connect() as conexion:
                conexion.execute(text("SELECT 1"))
            Base.metadata.create_all(motor)
            self._migrar_columnas_pmv2(motor)
            sesion = sessionmaker(motor, expire_on_commit=False)
            if configuracion.base_datos == "postgres":
                # Con PostgreSQL la escritura y los agregados van por procedimientos
                # almacenados; SQLite no los admite y usa el adaptador SQLAlchemy.
                instalar_procedimientos(motor)
                self.repositorio_consultas = RepositorioConsultasPostgres(sesion)
            else:
                self.repositorio_consultas = RepositorioConsultasSqlAlchemy(sesion)
            self.repositorio_fuentes = RepositorioFuentesPostgres(sesion)
            self.gestionar_fuentes = GestionarFuentesUseCase(self.repositorio_fuentes)
            self.consultar_historial = ConsultarHistorialUseCase(self.repositorio_consultas)
            self.analizar_demanda = AnalizarDemandaUseCase(self.repositorio_consultas)
            log.info("[REPOSITORIO] base de datos conectada")
            return True
        except Exception as exc:  # noqa: BLE001
            # El sistema sigue respondiendo consultas sin persistencia: la recuperacion y la
            # salvaguarda no dependen de la base de datos. Se pierde el historial (RF-11) y
            # el registro que alimentara los modelos predictivos del PMV2.
            log.warning(
                "[REPOSITORIO] sin base de datos, se opera sin historial: %s",
                str(exc).splitlines()[0],
            )
            return False
