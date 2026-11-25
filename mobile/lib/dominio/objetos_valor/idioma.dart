/// Idioma de la consulta. El corpus esta indexado en espanol, de modo que una
/// consulta en ingles se traduce antes de recuperar, nunca despues.
enum Idioma {
  espanol('es'),
  ingles('en'),
  noSoportado('xx');

  const Idioma(this.codigo);

  final String codigo;

  static Idioma desdeCodigo(String? codigo) => switch (codigo) {
    'es' => Idioma.espanol,
    'en' => Idioma.ingles,
    _ => Idioma.noSoportado,
  };
}
