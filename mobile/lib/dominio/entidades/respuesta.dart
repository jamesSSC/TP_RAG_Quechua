import '../objetos_valor/idioma.dart';
import '../objetos_valor/modo_consulta.dart';
import 'fragmento_respaldo.dart';

/// Resultado de una consulta al corpus.
///
/// Una respuesta abstenida no es un fallo: es la garantia de que el sistema no
/// propone formas en quechua que no esten documentadas.
class Respuesta {
  const Respuesta({
    required this.consultaId,
    required this.texto,
    required this.abstenida,
    required this.idioma,
    this.modo = ModoConsulta.sinConexion,
    this.similitudMaxima = 0.0,
    this.respaldo = const [],
    this.consultaTraducida,
    this.aviso,
    this.pasajes = const [],
    this.umbral,
    this.viaRespaldo,
    this.latenciaMs,
    this.redactadoPor,
    this.probabilidadCobertura,
    this.probabilidadPasajes,
    this.abstencionPorPredictor = false,
    this.avisoModo,
  });

  final String consultaId;
  final String texto;
  final bool abstenida;
  final Idioma idioma;

  /// Modo del que vino la respuesta: la nube o el corpus del propio telefono.
  final ModoConsulta modo;
  final double similitudMaxima;
  final List<FragmentoRespaldo> respaldo;

  /// Termino en espanol con el que se busco, cuando la consulta venia en ingles.
  /// Se muestra al usuario porque explica por que se recupero lo que se recupero.
  final String? consultaTraducida;
  final String? aviso;

  /// Pasajes de prosa que podrian tratar la consulta, sin que el sistema lo afirme.
  ///
  /// La similitud lexica no distingue una pregunta de gramatica que el corpus cubre de
  /// una que no: basta cambiar el nombre de la lengua para que deje de estarlo sin que
  /// las palabras cambien. En lugar de simular una certeza que no existe, el material se
  /// entrega literal y citado para que lo juzgue quien consulta.
  final List<FragmentoRespaldo> pasajes;

  /// Umbral τ con el que se decidio (0,48 en los dos modos).
  final double? umbral;

  /// "similitud" o "lema" cuando hay respuesta; nulo en una abstencion.
  final String? viaRespaldo;
  final double? latenciaMs;

  /// Quien redacto el texto en la nube (gemini, extractivo...). Sin conexion no hay
  /// generador: lo compone una plantilla determinista (ADR-026).
  final String? redactadoPor;

  /// Prediccion 1 (HU-08.1, RF-14) y prediccion 2 (HU-04, RF-15). Solo llegan en linea:
  /// el telefono no ejecuta el clasificador.
  final double? probabilidadCobertura;
  final double? probabilidadPasajes;

  /// La similitud permitia responder, pero el modelo estimo poca cobertura (RN-06).
  final bool abstencionPorPredictor;

  /// Explicacion del cambio de modo, p. ej. "la nube no respondio; se uso el corpus local".
  final String? avisoModo;

  bool get tienePasajes => pasajes.isNotEmpty;

  bool get tienePrediccion =>
      probabilidadCobertura != null || probabilidadPasajes != null;

  /// Copia de la respuesta marcada con el modo que la produjo.
  Respuesta conModo(ModoConsulta nuevoModo, {String? avisoModo}) => Respuesta(
    consultaId: consultaId,
    texto: texto,
    abstenida: abstenida,
    idioma: idioma,
    modo: nuevoModo,
    similitudMaxima: similitudMaxima,
    respaldo: respaldo,
    consultaTraducida: consultaTraducida,
    aviso: aviso,
    pasajes: pasajes,
    umbral: umbral,
    viaRespaldo: viaRespaldo,
    latenciaMs: latenciaMs,
    redactadoPor: redactadoPor,
    probabilidadCobertura: probabilidadCobertura,
    probabilidadPasajes: probabilidadPasajes,
    abstencionPorPredictor: abstencionPorPredictor,
    avisoModo: avisoModo ?? this.avisoModo,
  );
}
