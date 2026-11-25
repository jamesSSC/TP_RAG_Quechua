/// Documento publicado del que sale el corpus (HU-01).
///
/// En linea llega completo del registro de fuentes de la nube, con entidad y licencia. Sin
/// conexion solo se sabe lo que el indice exportado trae: el nombre del archivo y cuantos
/// fragmentos aporta; los campos ausentes quedan nulos y la interfaz lo dice, no los inventa.
class Fuente {
  const Fuente({
    required this.nombreArchivo,
    this.titulo,
    this.entidadPublicadora,
    this.licenciamiento,
    this.paginasTotales,
    this.fragmentos,
  });

  final String nombreArchivo;
  final String? titulo;
  final String? entidadPublicadora;
  final String? licenciamiento;
  final int? paginasTotales;
  final int? fragmentos;

  String get nombreVisible {
    if (titulo != null && titulo!.trim().isNotEmpty) return titulo!;
    final base = nombreArchivo.replaceAll(
      RegExp(r'\.pdf$', caseSensitive: false),
      '',
    );
    return base.replaceAll(RegExp(r'[_\-]+'), ' ').trim();
  }
}
