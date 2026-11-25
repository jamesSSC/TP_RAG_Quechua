/// Configuracion de la aplicacion. Nada de esto es secreto: la app no lleva ADMIN_TOKEN,
/// TOKEN_PRUEBAS ni claves de API (ADR-038).
class Configuracion {
  /// API de la nube. Se puede cambiar al compilar, sin tocar el codigo:
  ///   flutter build apk --dart-define=API_URL=https://otra-api.example
  /// Para apuntar al backend del escritorio desde el emulador: http://10.0.2.2:8000
  static const String urlApi = String.fromEnvironment(
    'API_URL',
    defaultValue: 'https://quechua-api.onrender.com',
  );

  /// Mismo umbral que la web (`AVISO_ESPERA_MS` en frontend/src/api.js): pasado este tiempo
  /// sin respuesta se muestra el aviso de arranque en frio de Render.
  static const Duration avisoEspera = Duration(milliseconds: 4000);

  /// En modo automatico, si la nube no responde en este tiempo se contesta con el corpus
  /// local. Render tarda 62-72 s en despertar (medido): no tiene sentido hacer esperar eso
  /// a quien solo quiere una palabra, cuando el telefono la tiene.
  static const Duration esperaAutomatica = Duration(seconds: 20);

  /// En "solo en linea" se espera lo que tarda Render en despertar, con margen.
  static const Duration esperaEnLinea = Duration(seconds: 90);

  /// Lecturas cortas (estado, fuentes, modelos).
  static const Duration esperaLectura = Duration(seconds: 15);
}
