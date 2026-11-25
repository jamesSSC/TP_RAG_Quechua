/// De dónde sale una respuesta. Se muestra siempre: quien consulta tiene derecho a saber si
/// su consulta salió del teléfono (en línea) o se resolvió en él (sin conexión), porque la
/// privacidad no es la misma en los dos casos (ADR-038).
enum ModoConsulta {
  enLinea('En línea · nube', 'Respondido en línea · nube'),
  sinConexion(
    'Sin conexión · corpus local',
    'Respondido sin conexión · corpus local',
  );

  const ModoConsulta(this.rotulo, this.origenRespuesta);

  /// Texto del indicador permanente de la cabecera.
  final String rotulo;

  /// Texto con el que cada respuesta declara de qué modo vino.
  final String origenRespuesta;

  static ModoConsulta desdeCodigo(String? codigo) => codigo == 'sin_conexion'
      ? ModoConsulta.sinConexion
      : ModoConsulta.enLinea;

  String get codigo =>
      this == ModoConsulta.sinConexion ? 'sin_conexion' : 'en_linea';
}

/// Lo que elige la persona en el selector. En automático la aplicación usa la nube y pasa
/// al corpus local si no hay red o la API no responde a tiempo.
enum PreferenciaModo {
  automatico(
    'Automático',
    'Usa la nube y, si no hay red, el corpus del teléfono',
  ),
  enLinea('Solo en línea', 'Siempre la nube; espera si se está activando'),
  sinConexion(
    'Solo sin conexión',
    'Siempre el corpus del teléfono; nada sale del dispositivo',
  );

  const PreferenciaModo(this.rotulo, this.descripcion);

  final String rotulo;
  final String descripcion;

  static PreferenciaModo desdeNombre(String? nombre) =>
      PreferenciaModo.values.firstWhere(
        (p) => p.name == nombre,
        orElse: () => PreferenciaModo.automatico,
      );
}
