import 'package:flutter/foundation.dart' show debugPrint, kReleaseMode;

import '../../../aplicacion/servicios/compositor_respuesta.dart';
import '../../../aplicacion/servicios/detector_idioma.dart';
import '../../../aplicacion/servicios/evaluador_confianza.dart';
import '../../../dominio/entidades/entrada_historial.dart';
import '../../../dominio/entidades/fragmento_respaldo.dart';
import '../../../dominio/entidades/fuente.dart';
import '../../../dominio/entidades/prediccion_ml.dart';
import '../../../dominio/entidades/respuesta.dart';
import '../../../dominio/objetos_valor/idioma.dart';
import '../../../dominio/objetos_valor/modo_consulta.dart';
import '../../../dominio/puertos/asistente_port.dart';
import 'historial_sqlite.dart';
import 'indice_portable.dart';
import 'traductor_tabla.dart';

const _avisoAlcance =
    'Esta es una consulta sobre fuentes documentales publicadas; no constituye una '
    'validación por hablantes de la comunidad.';

const _sinRespaldo = {
  Idioma.espanol:
      'No dispongo de respaldo documental para esa consulta en el corpus indexado. '
      'No propongo ninguna traducción, para evitar introducir una forma no documentada.',
  Idioma.ingles:
      'I have no documentary support for that query in the indexed corpus. I will not '
      'propose a translation, to avoid introducing an undocumented form.',
};

const _conPasajes = {
  Idioma.espanol:
      'No tengo una respuesta confirmada para esa consulta. Estos pasajes del corpus '
      'podrían tratarla; léelos y juzga tú.',
  Idioma.ingles:
      'I have no confirmed answer for that query. These passages from the corpus may '
      'deal with it; read them and judge for yourself.',
};

/// Resuelve la consulta en el propio dispositivo, sin red de ninguna clase.
///
/// Cumple el mismo puerto que el adaptador HTTP, de modo que sustituirlo no obliga a
/// tocar el dominio, los casos de uso ni una sola pantalla: es el cambio de una linea en
/// el contenedor. Nada sale del telefono, que es lo que exigen RF-12 y RNF-06 y lo que
/// sostiene el marco de soberania de datos del proyecto.
class AsistenteLocal implements AsistentePort {
  AsistenteLocal._(this._indice, this._traductor, this._historial);

  final IndicePortable _indice;
  final TraductorTabla _traductor;

  /// Nulo cuando la base no pudo abrirse. El historial es accesorio: su ausencia degrada
  /// la aplicacion pero no debe impedir consultar, que es lo que el usuario vino a hacer.
  final HistorialSqlite? _historial;

  static const _detector = DetectorIdioma();
  static const _evaluador = EvaluadorConfianza();
  static const _compositor = CompositorRespuesta();

  var _contador = 0;

  /// [sinHistorial] evita abrir la base: lo usa el arnes del dispositivo, que no debe dejar
  /// 248 consultas de prueba en el historial del telefono.
  static Future<AsistenteLocal> cargar({
    HistorialSqlite? historial,
    bool sinHistorial = false,
  }) async {
    // Las mediciones de RNF-01 y RNF-02 se toman aqui, en el dispositivo real, y no en
    // el escritorio de desarrollo: la arquitectura y la memoria son otras.
    final reloj = Stopwatch()..start();
    final indice = await IndicePortable.cargar();
    final traductor = await TraductorTabla.cargar();
    if (!kReleaseMode) {
      debugPrint(
        'MEDICION arranque_ms=${reloj.elapsedMilliseconds} '
        'fragmentos=${indice.fragmentos.length}',
      );
    }
    HistorialSqlite? base = historial;
    if (base == null && !sinHistorial) {
      try {
        base = await HistorialSqlite.abrir();
      } catch (_) {
        base = null;
      }
    }
    return AsistenteLocal._(indice, traductor, base);
  }

  HistorialSqlite? get almacen => _historial;

  @override
  Future<EstadoSistema> estado() async => EstadoSistema(
    fragmentosIndexados: _indice.fragmentos.length,
    umbralAbstencion: _indice.umbralAbstencion,
    disponible: true,
    modo: ModoConsulta.sinConexion,
    documentos: _indice.fragmentos.map((f) => f.documento).toSet().length,
    generador: 'compositor determinista',
  );

  /// Sin conexion solo se sabe lo que trae el indice exportado: el archivo y cuantos
  /// fragmentos aporta. La entidad y la licencia viven en el registro de fuentes de la nube.
  @override
  Future<List<Fuente>> fuentes() async {
    final conteo = <String, int>{};
    final paginas = <String, Set<int>>{};
    for (final f in _indice.fragmentos) {
      conteo[f.documento] = (conteo[f.documento] ?? 0) + 1;
      (paginas[f.documento] ??= <int>{}).add(f.pagina);
    }
    final documentos = conteo.keys.toList()..sort();
    return [
      for (final d in documentos)
        Fuente(
          nombreArchivo: d,
          fragmentos: conteo[d],
          paginasTotales: paginas[d]!.length,
        ),
    ];
  }

  /// El telefono no ejecuta los clasificadores del PMV2 (ADR-026, ADR-038): no se simula.
  @override
  Future<PrediccionMl> predecir(
    String texto,
  ) async => throw const ErrorConsulta(
    'La predicción ML se calcula en la nube. Sin conexión el teléfono no ejecuta los '
    'modelos: responde solo con el umbral τ = 0,48 y la coincidencia de lema.',
    tipo: TipoErrorConsulta.noDisponible,
  );

  @override
  Future<List<EntradaHistorial>> historial({int limite = 20}) async =>
      await _historial?.recientes(limite: limite) ?? const [];

  @override
  Future<Respuesta> consultar(String texto) async {
    final reloj = Stopwatch()..start();
    final resuelta = _resolver(texto);
    final ms = reloj.elapsedMicroseconds / 1000;
    final respuesta = Respuesta(
      consultaId: resuelta.consultaId,
      texto: resuelta.texto,
      abstenida: resuelta.abstenida,
      idioma: resuelta.idioma,
      modo: ModoConsulta.sinConexion,
      similitudMaxima: resuelta.similitudMaxima,
      respaldo: resuelta.respaldo,
      consultaTraducida: resuelta.consultaTraducida,
      aviso: resuelta.aviso,
      pasajes: resuelta.pasajes,
      umbral: _indice.umbralAbstencion,
      viaRespaldo: resuelta.abstenida
          ? null
          : (resuelta.similitudMaxima >= _indice.umbralAbstencion
                ? 'similitud'
                : 'lema'),
      latenciaMs: ms,
      redactadoPor: resuelta.abstenida ? null : 'compositor determinista',
    );
    if (!kReleaseMode) {
      debugPrint('MEDICION consulta_ms=$ms abstenida=${respuesta.abstenida}');
    }
    await _historial?.registrar(
      EntradaHistorial(
        consulta: texto,
        respuesta: respuesta.texto,
        abstenida: respuesta.abstenida,
        similitudMaxima: respuesta.similitudMaxima,
        momento: DateTime.now(),
        modo: ModoConsulta.sinConexion,
      ),
    );
    return respuesta;
  }

  Respuesta _resolver(String texto) {
    final id = '${DateTime.now().millisecondsSinceEpoch}-${_contador++}';
    var idioma = _detector.detectar(texto);
    final termino = _indice.depurador.depurar(texto);

    var candidatas = _traductor.candidatas(
      termino,
      aproximar: idioma == Idioma.ingles,
    );
    // Una palabra inglesa suelta ("love") no trae ninguna marca funcional que contar, de
    // modo que el detector la asume espanola y nunca se traduciria. Si el termino no
    // encabeza ninguna entrada del corpus pero si figura en la tabla como palabra
    // inglesa, la evidencia lexica pesa mas que la heuristica.
    if (candidatas.isNotEmpty &&
        idioma == Idioma.espanol &&
        !candidatas.contains(termino) &&
        !_indice.esLema(termino)) {
      idioma = Idioma.ingles;
      candidatas = _traductor.candidatas(termino, aproximar: true);
    }

    final variantes = <String>[texto, ...candidatas.where((c) => c != texto)];
    final (recuperados, origen) = _recuperarConVariantes(variantes);

    if (!_evaluador.responder(recuperados)) {
      // Antes de abstenerse del todo se busca en la prosa, que se consulta aparte porque
      // las entradas de diccionario, mucho mas cortas, copan siempre las primeras
      // posiciones. Lo recuperado no se afirma: se entrega literal y citado.
      final pasajes = _evaluador.ofrecerPasajes(
        _indice.recuperarProsa(texto, k: 3),
        consulta: termino,
      );
      return Respuesta(
        consultaId: id,
        texto: (pasajes.isNotEmpty ? _conPasajes : _sinRespaldo)[idioma]!,
        abstenida: true,
        idioma: idioma,
        similitudMaxima: _evaluador.similitudMaxima(recuperados),
        pasajes: pasajes,
        aviso: _avisoAlcance,
      );
    }

    final mejor = recuperados.first;
    final buscado = origen[mejor.id] ?? texto;
    final terminoBuscado = _indice.depurador.depurar(buscado);
    final entrada = _compositor.extraer(mejor.texto, terminoBuscado);

    // Cuando el termino lleva a varias entradas distintas del corpus se entregan todas,
    // en el orden de precision con que la tabla ofrecio cada candidata. Es el unico orden
    // con sentido: las puntuaciones no son comparables entre candidatas, porque la de
    // cada una mide lo bien que casa consigo misma y no lo bien que responde a la
    // consulta. Buscar "choclo" hace que la entrada CHOCLO puntue alto por fuerza.
    final lecturas = _lecturas(recuperados, origen, candidatas);

    return Respuesta(
      consultaId: id,
      // Sin entrada que descomponer no se redacta nada: se entrega el fragmento literal.
      // Es el caso de un fragmento de prosa que supero el umbral, donde no hay una
      // correspondencia que reordenar y cualquier parafrasis seria invencion.
      // La frase nombra el termino que escribio el usuario, no el que se uso para
      // buscar: quien pregunta por "love" espera leer "love" y no "amor", que es un
      // detalle interno de como se alcanzo la entrada. Con que se busco se dice aparte.
      texto: lecturas.length > 1
          ? _compositor.componerVarios(lecturas, idioma, termino)
          : entrada == null
          ? mejor.texto
          : _compositor.componer(entrada, idioma, termino),
      abstenida: false,
      idioma: idioma,
      similitudMaxima: _evaluador.similitudMaxima(recuperados),
      respaldo: recuperados,
      // Con varias lecturas no se anuncia una sola: decir que se busco "choclo" cuando
      // se busco con cinco terminos seria falso, y los cinco ya figuran en la respuesta.
      consultaTraducida: lecturas.length > 1 || buscado == texto
          ? null
          : terminoBuscado,
      aviso: _avisoAlcance,
    );
  }

  /// Entradas distintas del corpus a las que lleva la consulta, en el orden en que la
  /// tabla ofrecio las candidatas: primero las de coincidencia exacta y al final las
  /// obtenidas por aproximacion, que son las menos fiables.
  List<LecturaLexica> _lecturas(
    List<FragmentoRespaldo> recuperados,
    Map<String, String> origen,
    List<String> candidatas,
  ) {
    final porSentido = <String, LecturaLexica>{};
    for (final recuperado in recuperados) {
      if (!recuperado.coincidenciaLema) continue;
      final sentido = _indice.depurador.depurar(origen[recuperado.id] ?? '');
      if (sentido.isEmpty || porSentido.containsKey(sentido)) continue;
      final entrada = _compositor.extraer(recuperado.texto, sentido);
      if (entrada != null) {
        porSentido[sentido] = LecturaLexica(sentido, entrada);
      }
    }

    final ordenadas = <LecturaLexica>[];
    for (final candidata in candidatas) {
      final lectura = porSentido.remove(candidata);
      if (lectura != null) ordenadas.add(lectura);
    }
    return [...ordenadas, ...porSentido.values];
  }

  /// Recupera con la consulta original y con cada lectura espanola plausible, conservando
  /// para cada fragmento la mejor puntuacion, y registrando con que variante se logro.
  (List<FragmentoRespaldo>, Map<String, String>) _recuperarConVariantes(
    List<String> variantes,
  ) {
    final mejores = <String, FragmentoRespaldo>{};
    final origen = <String, String>{};

    for (final variante in variantes) {
      for (final recuperado in _indice.recuperar(variante, k: 5)) {
        final previo = mejores[recuperado.id];
        if (previo == null || _orden(recuperado) > _orden(previo)) {
          mejores[recuperado.id] = recuperado;
          origen[recuperado.id] = variante;
        }
      }
    }

    final ordenados = mejores.values.toList()
      ..sort((a, b) => _orden(b).compareTo(_orden(a)));
    return (ordenados.take(5).toList(), origen);
  }

  /// La coincidencia de lema manda sobre la puntuacion.
  static double _orden(FragmentoRespaldo r) =>
      (r.coincidenciaLema ? 1.0 : 0.0) + r.puntuacion;
}
