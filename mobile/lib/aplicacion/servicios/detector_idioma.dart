import '../../dominio/objetos_valor/idioma.dart';
import 'depurador_consulta.dart';

/// Decide en que idioma esta escrita la consulta contando palabras funcionales.
///
/// Basta para el alcance declarado, en el que el sistema solo admite espanol e ingles.
/// Una palabra suelta no tiene ninguna marca que contar, de modo que la heuristica no
/// puede resolverla sola: quien la resuelve es la evidencia lexica de la tabla de
/// traduccion, en el caso de uso.
class DetectorIdioma {
  const DetectorIdioma();

  static const _marcasEspanol = {
    'como',
    'que',
    'cual',
    'cuales',
    'se',
    'dice',
    'el',
    'la',
    'los',
    'las',
    'en',
    'del',
    'de',
    'para',
    'por',
    'significa',
    'palabra',
    'termino',
    'necesito',
    'estoy',
    'buscando',
    'designa',
    'variedad',
    'quiero',
    'saber',
    'es',
    'una',
    'un',
  };

  static const _marcasIngles = {
    'how',
    'what',
    'which',
    'the',
    'for',
    'do',
    'you',
    'say',
    'is',
    'are',
    'word',
    'mean',
    'means',
    'i',
    'need',
    'looking',
    'term',
    'in',
    'of',
    'to',
    'about',
  };

  static final _palabras = RegExp(r'[\p{L}\p{N}_]+', unicode: true);

  Idioma detectar(String texto) {
    final encontradas = _palabras
        .allMatches(DepuradorConsulta.normalizar(texto))
        .map((m) => m[0]!)
        .toSet();
    if (encontradas.isEmpty) return Idioma.noSoportado;

    final espanol = encontradas.intersection(_marcasEspanol).length;
    final ingles = encontradas.intersection(_marcasIngles).length;

    // Sin marcas funcionales se asume espanol, que es el idioma en el que esta
    // redactado el corpus.
    if (ingles > espanol) return Idioma.ingles;
    return Idioma.espanol;
  }
}
