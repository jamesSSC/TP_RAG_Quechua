import '../dominio/puertos/preferencias_port.dart';
import 'adaptadores/salida/asistente_conmutado.dart';
import 'adaptadores/salida/asistente_local.dart';
import 'adaptadores/salida/asistente_nube.dart';
import 'adaptadores/salida/historial_sqlite.dart';

/// Unico lugar donde se decide con que tecnologia se cumple cada puerto.
///
/// Historia del archivo, que es la de la arquitectura: primero aqui estaba `AsistenteHttp()`
/// contra el escritorio; luego `AsistenteLocal.cargar()` y la app dejo de necesitar red sin
/// tocar una sola pantalla. En el PMV3 (ADR-038) el puerto lo cumple `AsistenteConmutado`,
/// que compone los otros dos: la nube como modo principal y el corpus local de respaldo.
/// De nuevo, ni el dominio ni los casos de uso cambiaron.
class Contenedor {
  const Contenedor._(this.asistente, this.preferencias);

  final AsistenteConmutado asistente;
  final PreferenciasPort preferencias;

  static Future<Contenedor> cargar() async {
    HistorialSqlite? base;
    try {
      base = await HistorialSqlite.abrir();
    } catch (_) {
      // Sin base local la app sigue respondiendo; solo pierde historial y preferencias.
      base = null;
    }
    final local = await AsistenteLocal.cargar(historial: base);
    final PreferenciasPort preferencias = base ?? PreferenciasEnMemoria();
    final asistente = AsistenteConmutado(
      nube: AsistenteNube(),
      local: local,
      historial: base,
      preferencia: await preferencias.modo(),
    );
    return Contenedor._(asistente, preferencias);
  }
}
