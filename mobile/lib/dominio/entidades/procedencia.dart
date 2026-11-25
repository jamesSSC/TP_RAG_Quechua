/// Origen documental de un fragmento. La pagina no es un adorno: es lo que
/// permite que cualquier respuesta se pueda verificar en la fuente impresa.
class Procedencia {
  const Procedencia({required this.documento, required this.pagina});

  final String documento;
  final int pagina;

  /// Nombre legible del documento, sin la extension ni el ruido del archivo.
  String get titulo {
    final base = documento.replaceAll(
      RegExp(r'\.pdf$', caseSensitive: false),
      '',
    );
    return base.replaceAll(RegExp(r'[_\-]+'), ' ').trim();
  }

  String citar() => '$titulo, p. $pagina';
}
