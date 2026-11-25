import '../../dominio/entidades/fragmento_respaldo.dart';
import 'depurador_consulta.dart';

/// Unico punto de la aplicacion donde se decide entre responder y abstenerse.
///
/// El punto de operacion no es el que maximiza F1 sino el primero que no produce ningun
/// falso positivo. Los dos errores no son simetricos: una consulta legitima sin respuesta
/// deja al usuario donde estaba, mientras que una forma inventada sobre una lengua
/// seriamente en peligro entra en circulacion y no se retira.
class EvaluadorConfianza {
  const EvaluadorConfianza({this.umbral = umbralCalibrado});

  /// Recalibrado sobre esta implementacion. Viaja en el manifiesto del indice para que no
  /// pueda quedar desincronizado del ajuste con el que se calculo.
  static const double umbralCalibrado = 0.48;

  /// Piso por debajo del cual un pasaje de prosa ni siquiera se ofrece. No es un umbral de
  /// confianza y no autoriza ninguna afirmacion: solo descarta lo degenerado.
  static const double pisoPasajes = 0.12;

  /// Longitud minima de una palabra para considerarla de contenido. Por debajo son
  /// articulos, preposiciones y desinencias, que comparten todos los pasajes del corpus.
  static const int largoPalabraContenido = 5;

  /// Palabras de contenido que la consulta y el pasaje deben compartir para que el pasaje
  /// se muestre. Con una sola bastaba un termino suelto para sacar un pasaje ante
  /// cualquier consulta: "cual es la capital de Francia" compartia *capital* con un pasaje
  /// de la gramatica. Medido, exigir dos elimina los falsos positivos del subconjunto C y
  /// conserva el 85 % de cobertura.
  static const int palabrasCompartidas = 2;

  final double umbral;

  bool responder(List<FragmentoRespaldo> recuperados) {
    if (recuperados.isEmpty) return false;
    // La coincidencia de lema no puede producir un falso positivo: solo se activa cuando
    // el termino consultado figura literalmente como entrada del corpus indexado.
    if (recuperados.any((r) => r.coincidenciaLema)) return true;
    return recuperados
            .map((r) => r.puntuacion)
            .reduce((a, b) => a > b ? a : b) >=
        umbral;
  }

  double similitudMaxima(List<FragmentoRespaldo> recuperados) =>
      recuperados.isEmpty
      ? 0.0
      : recuperados.map((r) => r.puntuacion).reduce((a, b) => a > b ? a : b);

  /// Pasajes que merece la pena mostrar sin afirmar que responden a la consulta.
  ///
  /// La condicion no es de similitud sino de solapamiento explicito, que se puede auditar
  /// a diferencia de un umbral de coseno: la similitud lexica no distingue una pregunta de
  /// gramatica que el corpus cubre de una que no, porque basta cambiar el nombre de la
  /// lengua para que deje de estarlo sin que las palabras cambien.
  List<FragmentoRespaldo> ofrecerPasajes(
    List<FragmentoRespaldo> recuperados, {
    String consulta = '',
  }) {
    final delUsuario = palabrasDeContenido(consulta);
    // Una consulta con una sola palabra de contenido no puede compartir dos.
    final exigidas = palabrasCompartidas < delUsuario.length
        ? palabrasCompartidas
        : delUsuario.length;

    return recuperados.where((r) {
      if (r.puntuacion < pisoPasajes) return false;
      final comunes = delUsuario.intersection(palabrasDeContenido(r.texto));
      return comunes.length >= exigidas;
    }).toList();
  }

  static final _soloLetras = RegExp(r'[a-z]+');

  static Set<String> palabrasDeContenido(String texto) => _soloLetras
      .allMatches(DepuradorConsulta.normalizar(texto))
      .map((m) => m[0]!)
      .where((p) => p.length >= largoPalabraContenido)
      .toSet();
}
