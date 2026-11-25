import '../../dominio/objetos_valor/idioma.dart';
import 'depurador_consulta.dart';

/// Compone la respuesta a una consulta de diccionario sin intervencion de ningun modelo.
///
/// Sustituye al generador por lenguaje. La medicion de la fase de viabilidad mostro que
/// ningun modelo que quepa en un telefono lee una entrada lexicografica con fidelidad:
/// qwen3.5:0.8b llego a afirmar que *ashuti* significa "una", y qwen3.5:2b invirtio la
/// correspondencia de *agua*. El extractor determinista, en cambio, acerto las 180 de 180
/// consultas de los subconjuntos A y B.
///
/// Lo que aqui se compone no es una redaccion: es la correspondencia que la entrada
/// registra, reordenada en una frase. Ninguna forma quechua se altera, se deduce ni se
/// explica.
class CompositorRespuesta {
  const CompositorRespuesta();

  /// Cabecera de entrada: una palabra en mayusculas seguida de dos puntos.
  static final _cabecera = RegExp(r'(?=\b[A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s\-]{1,30}:)');
  static final _entrada = RegExp(
    r'^\s*([A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s\-]*?)\s*:\s*([\s\S]*)$',
  );
  static final _matiz = RegExp(r'\(([^)]+)\)\s*([^(]*)');

  /// Extrae de un fragmento la entrada cuyo lema coincide con [termino].
  EntradaLexica? extraer(String texto, String termino) {
    final buscado = DepuradorConsulta.normalizar(termino).trim();
    for (final bloque in texto.split(_cabecera)) {
      final m = _entrada.firstMatch(bloque);
      if (m == null) continue;
      final lema = m[1]!.trim();
      if (DepuradorConsulta.normalizar(lema).trim() != buscado) continue;

      final cuerpo = m[2]!;
      final principal = cuerpo
          .split('(')
          .first
          .trim()
          .replaceAll(RegExp(r'\.+$'), '');
      final formas = _separar(principal);
      if (formas.isEmpty) continue;

      final matices = <Matiz>[];
      for (final coincidencia in _matiz.allMatches(cuerpo)) {
        final formasMatiz = _separar(
          coincidencia[2]!.trim().replaceAll(RegExp(r'\.+$'), ''),
        );
        if (formasMatiz.isNotEmpty) {
          matices.add(Matiz(coincidencia[1]!.trim(), formasMatiz));
        }
      }
      return EntradaLexica(lema: lema, formas: formas, matices: matices);
    }
    return null;
  }

  static List<String> _separar(String texto) =>
      texto.split(',').map((f) => f.trim()).where((f) => f.isNotEmpty).toList();

  /// Redacta la correspondencia. El texto sale de una plantilla fija, de modo que no
  /// puede introducir nada que la entrada no registre.
  String componer(
    EntradaLexica entrada,
    Idioma idioma,
    String terminoConsultado,
  ) {
    final termino = terminoConsultado.trim().isEmpty
        ? entrada.lema.toLowerCase()
        : terminoConsultado.trim().toLowerCase();

    if (idioma == Idioma.ingles) {
      final buffer = StringBuffer(
        'In Wanka Quechua, "$termino" is ${_unir(entrada.formas, 'or')}.',
      );
      for (final matiz in entrada.matices) {
        buffer.write(' For "${matiz.sentido}": ${_unir(matiz.formas, 'or')}.');
      }
      return buffer.toString();
    }

    final buffer = StringBuffer(
      'En quechua wanka, "$termino" se dice ${_unir(entrada.formas, 'o')}.',
    );
    for (final matiz in entrada.matices) {
      buffer.write(' Para "${matiz.sentido}": ${_unir(matiz.formas, 'o')}.');
    }
    return buffer.toString();
  }

  /// Redacta varias lecturas cuando el termino consultado corresponde a mas de una
  /// entrada del corpus.
  ///
  /// Una palabra inglesa corriente no tiene un solo equivalente espanol: "boiled corn"
  /// lleva a comijn, mote y choclo, y las tres son entradas reales del diccionario.
  /// Elegir una por su puntuacion seria elegir por ruido, porque la puntuacion de cada
  /// candidata mide lo bien que casa consigo misma y no lo bien que responde a la
  /// consulta: buscar "choclo" hace que la entrada CHOCLO puntue alto por fuerza. Quien
  /// pregunta sabe que sentido queria, de modo que se le entregan todos y elige el.
  String componerVarios(
    List<LecturaLexica> lecturas,
    Idioma idioma,
    String terminoConsultado,
  ) {
    final termino = terminoConsultado.trim().toLowerCase();
    final buffer = StringBuffer(
      idioma == Idioma.ingles
          ? '"$termino" corresponds to several entries in the corpus:'
          : '"$termino" corresponde a varias entradas del corpus:',
    );
    // Una por linea: puestas seguidas, cinco correspondencias se leen como una frase
    // atropellada y dejan de poder compararse de un vistazo, que es justo para lo que se
    // entregan todas.
    for (final lectura in lecturas) {
      final formas = _unir(
        lectura.entrada.formas,
        idioma == Idioma.ingles ? 'or' : 'o',
      );
      buffer.write('\n${lectura.sentido} — $formas');
    }
    return buffer.toString();
  }

  static String _unir(List<String> formas, String conjuncion) {
    if (formas.length == 1) return formas.single;
    return '${formas.sublist(0, formas.length - 1).join(', ')} '
        '$conjuncion ${formas.last}';
  }
}

/// Entrada de diccionario ya descompuesta en sus partes.
class EntradaLexica {
  const EntradaLexica({
    required this.lema,
    required this.formas,
    this.matices = const [],
  });

  /// El termino en espanol que encabeza la entrada.
  final String lema;

  /// Las formas en quechua wanka, literales.
  final List<String> formas;

  /// Sentidos matizados que la entrada distingue, como "(perrito)".
  final List<Matiz> matices;
}

/// Una de las lecturas espanolas de un termino consultado, con su entrada.
class LecturaLexica {
  const LecturaLexica(this.sentido, this.entrada);

  /// El termino espanol por el que se llego a la entrada.
  final String sentido;
  final EntradaLexica entrada;
}

class Matiz {
  const Matiz(this.sentido, this.formas);

  final String sentido;
  final List<String> formas;
}
