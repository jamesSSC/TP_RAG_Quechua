import logging
import time

from application.ports import ConsultarCorpusPort
from application.ports.out.detector_idioma_port import DetectorIdiomaPort
from application.ports.out.generador_texto_port import GeneradorNoDisponible, GeneradorTextoPort
from application.ports.out.indice_recuperacion_port import IndiceRecuperacionPort
from application.ports.out.predictor_port import PredictorPort
from application.ports.out.repositorio_consultas_port import RepositorioConsultasPort
from application.ports.out.traductor_port import TraductorPort
from domain.entities.consulta import Consulta
from domain.entities.fragmento import FragmentoRecuperado
from domain.entities.respuesta import Respuesta
from domain.services.caracteristicas_consulta import (
    CaracteristicasConsulta,
    extraer_caracteristicas,
)
from domain.services.clasificador_consulta import ClasificadorConsulta
from domain.services.depurador_consulta import DepuradorConsulta
from domain.services.evaluador_confianza import EvaluadorConfianza
from domain.value_objects.idioma import Idioma
from domain.value_objects.origen_consulta import OrigenConsulta

log = logging.getLogger("rag.caso_uso")

MENSAJE_CON_PASAJES = {
    Idioma.ESPANOL: (
        "No tengo una respuesta confirmada para esa consulta. Estos pasajes del corpus "
        "podrían tratarla; léelos y juzga tú."
    ),
    Idioma.INGLES: (
        "I have no confirmed answer for that query. These passages from the corpus may "
        "deal with it; read them and judge for yourself."
    ),
}
MENSAJE_SIN_RESPALDO = {
    Idioma.ESPANOL: (
        "No dispongo de respaldo documental para esa consulta en el corpus indexado. "
        "No propongo ninguna traducción, para evitar introducir una forma no documentada."
    ),
    Idioma.INGLES: (
        "I have no documentary support for that query in the indexed corpus. "
        "I will not propose a translation, to avoid introducing an undocumented form."
    ),
}

AVISO_GENERACION = "El servicio de redacción no está disponible; se muestra el fragmento literal."

MENSAJE_PREDICTOR = {
    Idioma.ESPANOL: (
        "El modelo predictivo estima que esta consulta no tiene respaldo suficiente en el "
        "corpus. Me abstengo para no proponer una forma no documentada."
    ),
    Idioma.INGLES: (
        "The predictive model estimates that this query lacks enough support in the corpus. "
        "I abstain so as not to propose an undocumented form."
    ),
}

MENSAJE_IDIOMA = (
    "Solo se admiten consultas en español o en inglés. "
    "Only queries in Spanish or English are supported."
)


class ConsultarCorpusUseCase(ConsultarCorpusPort):
    """HU-03 (consulta lexica), HU-06 (salvaguarda antialucinacion) y HU-07 (trazabilidad).

    El orden importa: la decision de abstenerse se toma ANTES de invocar al generador, de
    modo que ante una consulta sin respaldo el modelo de lenguaje no llega a ejecutarse y
    no tiene ocasion de inventar una forma."""

    def __init__(
        self,
        indice: IndiceRecuperacionPort,
        generador: GeneradorTextoPort,
        evaluador: EvaluadorConfianza,
        detector_idioma: DetectorIdiomaPort,
        repositorio: RepositorioConsultasPort | None = None,
        traductor: TraductorPort | None = None,
        depurador: DepuradorConsulta | None = None,
        clasificador: ClasificadorConsulta | None = None,
        k: int = 5,
        predictor_cobertura: PredictorPort | None = None,
        predictor_pasajes: PredictorPort | None = None,
        probabilidad_minima_cobertura: float = 0.0,
        probabilidad_minima_pasajes: float = 0.0,
        origen: OrigenConsulta = OrigenConsulta.USUARIO,
    ):
        self._indice = indice
        self._generador = generador
        self._evaluador = evaluador
        self._detector = detector_idioma
        self._repositorio = repositorio
        self._traductor = traductor
        self._depurador = depurador or DepuradorConsulta()
        self._clasificador = clasificador or ClasificadorConsulta(self._depurador)
        self._k = k
        # Lo fija quien construye el caso de uso (servidor o script), nunca el cliente.
        self._origen = origen
        # PMV2 (RF-14 y RF-15). Ambos predictores solo pueden AÑADIR abstenciones o retirar
        # pasajes (RN-06): nunca convierten en respuesta lo que la regla del umbral rechaza.
        self._predictor_cobertura = predictor_cobertura
        self._predictor_pasajes = predictor_pasajes
        self._p_min_cobertura = probabilidad_minima_cobertura
        self._p_min_pasajes = probabilidad_minima_pasajes

    def ejecutar(self, texto_consulta: str) -> Respuesta:
        return self._resolver(texto_consulta, time.perf_counter())

    def _resolver(self, texto_consulta: str, t0: float) -> Respuesta:
        idioma = self._detector.detectar(texto_consulta)
        consulta = Consulta(texto=texto_consulta, idioma=idioma, origen=self._origen)
        log.info("[CASO-USO] ConsultarCorpus: idioma=%s", idioma.value)

        if not idioma.soportado:
            return self._registrar(t0, consulta, self._respuesta_idioma_no_soportado(consulta))

        idioma = self._traducir(consulta, idioma)
        recuperados, origen = self._recuperar_con_variantes(consulta)
        self._anotar_lectura_ganadora(consulta, recuperados, origen)
        log.info(
            "[INDICE] k=%d recuperados=%d sim_max=%.3f%s",
            self._k,
            len(recuperados),
            max((r.puntuacion.valor for r in recuperados), default=0.0),
            self._cita_mejor(recuperados),
        )
        veredicto = self._evaluador.evaluar(recuperados)
        log.info(
            "[EVALUADOR] responder=%s via=%s tau=%.2f",
            veredicto.responder,
            veredicto.via_respaldo or "ninguna",
            veredicto.umbral,
        )

        prediccion = self._predecir(consulta, recuperados)
        p_cobertura = prediccion["cobertura"]
        if self._abstiene_por_predictor(veredicto, p_cobertura):
            return self._registrar(
                t0,
                consulta,
                self._respuesta_por_predictor(consulta, idioma, veredicto, p_cobertura),
            )

        if not veredicto.responder:
            return self._registrar(
                t0,
                consulta,
                self._respuesta_sin_respaldo(consulta, idioma, veredicto, prediccion),
            )

        respaldo = self._seleccionar_respaldo(veredicto, recuperados)
        return self._registrar(
            t0,
            consulta,
            self._respuesta_con_respaldo(consulta, idioma, veredicto, respaldo, p_cobertura),
        )

    # --- Pasos de _resolver: cada uno conserva exactamente el comportamiento anterior ---

    @staticmethod
    def _respuesta_idioma_no_soportado(consulta: Consulta) -> Respuesta:
        log.info("[GENERADOR] NO invocado (idioma no soportado)")
        return Respuesta(
            consulta_id=consulta.id,
            texto=MENSAJE_IDIOMA,
            abstenida=True,
            idioma=consulta.idioma,
        )

    def _traducir(self, consulta: Consulta, idioma: Idioma) -> Idioma:
        """Traduce solo la consulta (RN-05) y devuelve el idioma efectivo."""
        if self._traductor is None:
            return idioma
        # Se traduce la consulta ya depurada, es decir el termino solo y no la pregunta
        # completa. Traducir la frase entera devuelve el fraseo en espanol ("como se
        # dice X en quechua de Wanka"), que reintroduce en la consulta las palabras que
        # la depuracion existe para eliminar y hunde la similitud del fragmento.
        termino = self._depurador.depurar(consulta.texto)
        candidatas = self._traductor.candidatas(termino, aproximar=idioma is Idioma.INGLES)

        # Una palabra inglesa suelta ("love") no trae ninguna marca funcional que
        # contar, de modo que el detector la asume espanola y nunca se traducia. Si el
        # termino no encabeza ninguna entrada del corpus pero si figura en la tabla
        # como palabra inglesa, la evidencia lexica pesa mas que la heuristica.
        if (
            candidatas
            and idioma is Idioma.ESPANOL
            and termino not in candidatas
            and not self._indice.es_lema(termino)
        ):
            idioma = Idioma.INGLES
            consulta.idioma = idioma
            candidatas = self._traductor.candidatas(termino, aproximar=True)

        consulta.variantes = candidatas
        log.info("[TRADUCTOR] lecturas candidatas=%d", len(candidatas))
        return idioma

    @staticmethod
    def _anotar_lectura_ganadora(consulta: Consulta, recuperados, origen: dict) -> None:
        if not (recuperados and consulta.variantes):
            return
        # Se informa de la variante que realmente sostiene la respuesta, no de la
        # primera de la lista: las candidatas salen en orden alfabetico, de modo que
        # "boiled corn" anunciaba haber buscado "comijn" cuando el fragmento que
        # respondia lo habia encontrado "mote".
        ganadora = origen.get(recuperados[0].id)
        if ganadora and ganadora != consulta.texto:
            consulta.texto_traducido = ganadora

    def _abstiene_por_predictor(self, veredicto, p_cobertura) -> bool:
        """RN-06: el predictor puede añadir una abstencion, nunca quitarla."""
        abstiene = (
            veredicto.responder and p_cobertura is not None and p_cobertura < self._p_min_cobertura
        )
        if abstiene:
            log.info(
                "[PREDICTOR] cobertura=%.3f < %.2f -> abstencion",
                p_cobertura,
                self._p_min_cobertura,
            )
        return abstiene

    @staticmethod
    def _respuesta_por_predictor(consulta, idioma, veredicto, p_cobertura) -> Respuesta:
        return Respuesta(
            consulta_id=consulta.id,
            texto=MENSAJE_PREDICTOR[idioma],
            abstenida=True,
            idioma=idioma,
            similitud_maxima=veredicto.similitud_maxima,
            consulta_traducida=consulta.texto_traducido,
            probabilidad_cobertura=p_cobertura,
            abstencion_por_predictor=True,
        )

    def _pasajes_de_prosa(self, consulta: Consulta) -> list:
        """Antes de abstenerse del todo se busca en la prosa, que se consulta aparte porque
        las entradas de diccionario, mucho mas cortas, copan siempre las primeras posiciones.
        Lo recuperado no se afirma: se entrega literal y citado."""
        if self._clasificador.es_lexica(consulta.texto):
            # D-1: ante una peticion de termino no se ofrecen parrafos de prosa.
            log.info("[CASO-USO] consulta lexica: sin pasajes de prosa")
            return []
        return self._evaluador.ofrecer_pasajes(
            self._indice.recuperar_prosa(consulta.texto_para_recuperar, k=3),
            # El solapamiento se mide contra la consulta depurada, no contra la
            # cruda: "en quechua wanka" acompana a casi toda consulta y a ningun
            # pasaje distingue, de modo que sin depurar bastaba esa palabra para
            # sacar el prologo del libro ante cualquier termino no cubierto.
            consulta=self._depurador.depurar(consulta.texto_para_recuperar),
        )

    def _filtrar_pasajes_por_predictor(self, pasajes: list, prediccion: dict):
        """RF-15: el segundo modelo estima si los pasajes tratan de verdad la pregunta.
        Solo puede retirarlos; los que muestra siguen rotulados "no es una respuesta".
        Devuelve (pasajes, probabilidad)."""
        if not (pasajes and self._predictor_pasajes is not None and prediccion["vector"]):
            return pasajes, None
        p_pasajes = self._predictor_pasajes.probabilidad(prediccion["vector"])
        if p_pasajes is not None and p_pasajes < self._p_min_pasajes:
            log.info(
                "[PREDICTOR] pasajes=%.3f < %.2f -> se retiran", p_pasajes, self._p_min_pasajes
            )
            return [], p_pasajes
        return pasajes, p_pasajes

    def _respuesta_sin_respaldo(self, consulta, idioma, veredicto, prediccion) -> Respuesta:
        pasajes, p_pasajes = self._filtrar_pasajes_por_predictor(
            self._pasajes_de_prosa(consulta), prediccion
        )
        log.info("[GENERADOR] NO invocado (sin respaldo)")
        log.info("[CASO-USO] pasajes de prosa ofrecidos=%d (no es una respuesta)", len(pasajes))
        return Respuesta(
            consulta_id=consulta.id,
            texto=(MENSAJE_CON_PASAJES if pasajes else MENSAJE_SIN_RESPALDO)[idioma],
            abstenida=True,
            idioma=idioma,
            similitud_maxima=veredicto.similitud_maxima,
            consulta_traducida=consulta.texto_traducido,
            pasajes=pasajes,
            probabilidad_cobertura=prediccion["cobertura"],
            probabilidad_pasajes=p_pasajes,
        )

    def _seleccionar_respaldo(self, veredicto, recuperados: list) -> list:
        if veredicto.por_lema:
            # ADR-021, condicion 3: por la via de lema el generador recibe SOLO las entradas
            # cuyo lema coincide con el termino consultado.
            return [r for r in recuperados if r.coincidencia_lema]
        return [
            r
            for r in recuperados
            if r.coincidencia_lema or r.puntuacion.valor >= self._evaluador.umbral
        ]

    def _redactar(self, consulta: Consulta, respaldo: list, idioma: Idioma):
        """Devuelve (texto, aviso). D-6: sin redactor se muestra el fragmento literal con su
        cita; nunca un error del servicio ni una forma que no este en el corpus."""
        log.info("[GENERADOR] invocado (%d fragmentos de respaldo)", len(respaldo))
        try:
            return self._generador.redactar(consulta.texto, respaldo, idioma), None
        except GeneradorNoDisponible as exc:
            log.warning("[GENERADOR] fallo: %s -> plantilla literal", type(exc).__name__)
            primero = respaldo[0]
            return f"{primero.texto} ({primero.procedencia.citar()})", AVISO_GENERACION

    def _respuesta_con_respaldo(self, consulta, idioma, veredicto, respaldo, p_cobertura):
        texto, aviso_generacion = self._redactar(consulta, respaldo, idioma)
        return Respuesta(
            consulta_id=consulta.id,
            texto=texto,
            respaldo=respaldo,
            abstenida=False,
            idioma=idioma,
            similitud_maxima=veredicto.similitud_maxima,
            consulta_traducida=consulta.texto_traducido,
            via_respaldo=veredicto.via_respaldo,
            generador_invocado=True,
            aviso_generacion=aviso_generacion,
            probabilidad_cobertura=p_cobertura,
        )

    def caracteristicas(self, texto_consulta: str) -> CaracteristicasConsulta:
        """Vector de caracteristicas de una consulta, calculado por el mismo camino que la
        consulta real (deteccion, traduccion, recuperacion). Lo usa el script de
        entrenamiento para que entrenar y predecir hagan exactamente las mismas cuentas."""
        idioma = self._detector.detectar(texto_consulta)
        consulta = Consulta(texto=texto_consulta, idioma=idioma)
        if self._traductor is not None:
            termino = self._depurador.depurar(consulta.texto)
            candidatas = self._traductor.candidatas(termino, aproximar=idioma is Idioma.INGLES)
            if (
                candidatas
                and idioma is Idioma.ESPANOL
                and termino not in candidatas
                and not self._indice.es_lema(termino)
            ):
                idioma = Idioma.INGLES
                consulta.idioma = idioma
                candidatas = self._traductor.candidatas(termino, aproximar=True)
            consulta.variantes = candidatas
        recuperados, origen = self._recuperar_con_variantes(consulta)
        if recuperados and consulta.variantes:
            ganadora = origen.get(recuperados[0].id)
            if ganadora and ganadora != consulta.texto:
                consulta.texto_traducido = ganadora
        return self._vector(consulta, recuperados)

    def _vector(
        self, consulta: Consulta, recuperados: list[FragmentoRecuperado]
    ) -> CaracteristicasConsulta:
        texto = consulta.texto_para_recuperar
        return extraer_caracteristicas(
            consulta=texto,
            terminos_depurados=self._depurador.depurar(texto).split(),
            recuperados=recuperados,
            pasajes=self._indice.recuperar_prosa(texto, k=3),
            proporcion_fuera_vocabulario=self._indice.proporcion_fuera_de_vocabulario(texto),
        )

    def _predecir(self, consulta: Consulta, recuperados: list[FragmentoRecuperado]) -> dict:
        activos = [
            p
            for p in (self._predictor_cobertura, self._predictor_pasajes)
            if p is not None and p.disponible()
        ]
        if not activos:
            return {"vector": None, "cobertura": None}
        vector = self._vector(consulta, recuperados)
        cobertura = (
            self._predictor_cobertura.probabilidad(vector)
            if self._predictor_cobertura is not None
            else None
        )
        if cobertura is not None:
            log.info("[PREDICTOR] probabilidad de cobertura=%.3f", cobertura)
        return {"vector": vector, "cobertura": cobertura}

    def _recuperar_con_variantes(
        self, consulta: Consulta
    ) -> tuple[list[FragmentoRecuperado], dict[str, str]]:
        """Recupera con la consulta original y con cada lectura espanola plausible,
        conservando para cada fragmento la mejor puntuacion obtenida.

        Buscar con todas es lo que impide que una traduccion defectuosa anule el resultado:
        en el peor caso degrada al comportamiento que ya se tenia sin traducir.

        Devuelve tambien, por fragmento, la variante que logro esa mejor puntuacion, para
        poder decir al usuario con que termino se encontro lo que se le muestra."""
        variantes = [consulta.texto]
        for candidata in consulta.variantes:
            if candidata and candidata not in variantes:
                variantes.append(candidata)

        mejores: dict[str, FragmentoRecuperado] = {}
        origen: dict[str, str] = {}
        for variante in variantes:
            for recuperado in self._indice.recuperar(variante, k=self._k):
                previo = mejores.get(recuperado.id)
                if previo is None or self._orden(recuperado) > self._orden(previo):
                    mejores[recuperado.id] = recuperado
                    origen[recuperado.id] = variante

        ordenados = sorted(mejores.values(), key=self._orden, reverse=True)[: self._k]
        return ordenados, origen

    @staticmethod
    def _orden(recuperado: FragmentoRecuperado) -> tuple[bool, float]:
        return (recuperado.coincidencia_lema, recuperado.puntuacion.valor)

    @staticmethod
    def _cita_mejor(recuperados: list[FragmentoRecuperado]) -> str:
        if not recuperados:
            return ""
        mejor = recuperados[0]
        return f" mejor={mejor.id} ({mejor.procedencia.documento}, p. {mejor.procedencia.pagina})"

    def _registrar(self, t0: float, consulta: Consulta, respuesta: Respuesta) -> Respuesta:
        # Latencia extremo a extremo del caso de uso (incluye la redaccion, si la hubo).
        respuesta.latencia_ms = round((time.perf_counter() - t0) * 1000, 1)
        respuesta.umbral = self._evaluador.umbral
        respuesta.lecturas_traduccion = list(consulta.variantes)
        if self._repositorio is not None:
            self._repositorio.registrar(consulta, respuesta)
            log.info(
                "[REPOSITORIO] registrada consulta_id=%s abstenida=%s",
                consulta.id,
                respuesta.abstenida,
            )
        else:
            log.info("[REPOSITORIO] omitido (sin base de datos)")
        return respuesta
