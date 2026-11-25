/// Elimina de la consulta el fraseo que acompana a toda pregunta y que, por repetirse en
/// todas, no distingue ninguna.
///
/// Portado literalmente del servicio del escritorio: la depuracion forma parte de la
/// funcion de puntuacion contra la que se calibro el umbral, de modo que cualquier
/// diferencia aqui invalidaria el umbral que viaja con el indice.
class DepuradorConsulta {
  DepuradorConsulta(List<String> plantillas)
    : _plantillas = plantillas
          .map((p) => RegExp(p, caseSensitive: false, unicode: true))
          .toList();

  final List<RegExp> _plantillas;

  static final _sinPuntuacion = RegExp(r'[^\p{L}\p{N}_\s]', unicode: true);
  static final _espacios = RegExp(r'\s+');

  /// Minusculas y sin diacriticos. Se aplica por igual a la consulta y al corpus para que
  /// la variacion ortografica entre fuentes no impida la coincidencia.
  static String normalizar(String texto) {
    final buffer = StringBuffer();
    for (final rune in texto.toLowerCase().runes) {
      final sinTilde = _equivalencias[rune];
      buffer.write(sinTilde ?? String.fromCharCode(rune));
    }
    return buffer.toString();
  }

  String depurar(String texto) {
    var normalizado = normalizar(texto);
    for (final plantilla in _plantillas) {
      normalizado = normalizado.replaceAll(plantilla, ' ');
    }
    normalizado = normalizado.replaceAll(_sinPuntuacion, ' ');
    final depurado = normalizado.replaceAll(_espacios, ' ').trim();
    // Una consulta que era solo fraseo se devuelve intacta: vaciarla dejaria al
    // recuperador sin nada con que comparar y produciria una abstencion enganosa.
    return depurado.isEmpty ? normalizar(texto) : depurado;
  }

  /// Dart no trae normalizacion Unicode, de modo que la descomposicion NFD que hace el
  /// escritorio se resuelve con la tabla de las letras que el corpus realmente contiene.
  static const Map<int, String> _equivalencias = {
    0xE1: 'a',
    0xE9: 'e',
    0xED: 'i',
    0xF3: 'o',
    0xFA: 'u',
    0xFC: 'u',
    0xF1: 'n',
    0xE0: 'a',
    0xE8: 'e',
    0xEC: 'i',
    0xF2: 'o',
    0xF9: 'u',
    0xE4: 'a',
    0xEB: 'e',
    0xEF: 'i',
    0xF6: 'o',
    0xE2: 'a',
    0xEA: 'e',
    0xEE: 'i',
    0xF4: 'o',
    0xFB: 'u',
    0xE7: 'c',
    0x107: 'c',
  };
}
