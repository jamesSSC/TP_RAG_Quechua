import '../entidades/entrada_historial.dart';
import '../entidades/fuente.dart';
import '../entidades/prediccion_ml.dart';
import '../entidades/respuesta.dart';
import '../objetos_valor/modo_consulta.dart';

/// Puerto de consulta al corpus.
///
/// El unico contrato que la interfaz conoce. Lo cumplen tres adaptadores: el de la nube
/// (`AsistenteNube`), el del corpus del telefono (`AsistenteLocal`) y el que elige entre
/// ambos (`AsistenteConmutado`). La pantalla no sabe cual tiene delante.
abstract interface class AsistentePort {
  Future<Respuesta> consultar(String texto);

  Future<List<EntradaHistorial>> historial({int limite});

  Future<EstadoSistema> estado();

  /// Documentos de los que sale el corpus.
  Future<List<Fuente>> fuentes();

  /// Predicciones ML de una consulta. Lanza [ErrorConsulta] con tipo
  /// [TipoErrorConsulta.noDisponible] si el modo activo no ejecuta los modelos.
  Future<PrediccionMl> predecir(String texto);
}

/// Estado del motor de consulta, para poder decir al usuario que ocurre.
class EstadoSistema {
  const EstadoSistema({
    required this.fragmentosIndexados,
    required this.umbralAbstencion,
    required this.disponible,
    this.modo = ModoConsulta.sinConexion,
    this.documentos,
    this.generador,
    this.predictoresDisponibles = false,
  });

  final int fragmentosIndexados;
  final double umbralAbstencion;
  final bool disponible;
  final ModoConsulta modo;
  final int? documentos;
  final String? generador;
  final bool predictoresDisponibles;
}

enum TipoErrorConsulta {
  /// Sin red o el servidor no se alcanza.
  red,

  /// El servidor no respondio a tiempo.
  tiempo,

  /// 429: limite de consultas por minuto superado (ADR-037).
  limite,

  /// 422: la consulta no es valida.
  validacion,

  /// Cualquier otro error devuelto por el servicio.
  servicio,

  /// La operacion no existe en este modo (p. ej. la prediccion ML sin conexion).
  noDisponible,
}

/// Fallo que la interfaz puede mostrar al usuario tal cual.
class ErrorConsulta implements Exception {
  const ErrorConsulta(
    this.mensaje, {
    this.tipo = TipoErrorConsulta.servicio,
    this.estado,
    this.reintentarEn,
  });

  final String mensaje;
  final TipoErrorConsulta tipo;
  final int? estado;

  /// Espera que pide el servidor antes de volver a intentar (cabecera Retry-After).
  final Duration? reintentarEn;

  /// Fallos que significan "la nube no esta": justifican pasar al corpus local.
  bool get esFaltaDeServicio =>
      tipo == TipoErrorConsulta.red ||
      tipo == TipoErrorConsulta.tiempo ||
      (tipo == TipoErrorConsulta.servicio && (estado ?? 0) >= 500);

  @override
  String toString() => mensaje;
}
