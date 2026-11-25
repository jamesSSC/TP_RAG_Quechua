import 'procedencia.dart';

/// Fragmento del corpus que sostiene una respuesta, con su puntuacion.
class FragmentoRespaldo {
  const FragmentoRespaldo({
    required this.id,
    required this.texto,
    required this.procedencia,
    required this.puntuacion,
    this.coincidenciaLema = false,
  });

  final String id;
  final String texto;
  final Procedencia procedencia;
  final double puntuacion;

  /// El lema de la entrada coincide exactamente con el termino consultado. Estos
  /// fragmentos se muestran aunque su puntuacion quede por debajo del umbral:
  /// un termino frecuente en el corpus recibe un IDF bajo y su propia entrada de
  /// diccionario puede no alcanzarlo.
  final bool coincidenciaLema;
}
