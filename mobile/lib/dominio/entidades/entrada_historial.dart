import '../objetos_valor/modo_consulta.dart';

/// Consulta ya resuelta, tal como se guarda para poder volver a ella.
///
/// El historial vive solo en el telefono, tambien en linea: en la nube la lectura del
/// historial del servidor exige el token de administracion (ADR-036), y la app no lo lleva.
class EntradaHistorial {
  const EntradaHistorial({
    required this.consulta,
    required this.respuesta,
    required this.abstenida,
    required this.similitudMaxima,
    required this.momento,
    this.modo = ModoConsulta.sinConexion,
  });

  final String consulta;
  final String respuesta;
  final bool abstenida;
  final double similitudMaxima;
  final DateTime momento;
  final ModoConsulta modo;
}
