import '../objetos_valor/modo_consulta.dart';

/// Preferencias de quien usa la aplicacion, guardadas en el propio telefono.
abstract interface class PreferenciasPort {
  Future<PreferenciaModo> modo();

  Future<void> guardarModo(PreferenciaModo modo);

  /// Indice del tamano de letra (0 = A−, 1 = A, 2 y 3 = A+), como en la web.
  Future<int> tamanoTexto();

  Future<void> guardarTamanoTexto(int indice);
}

/// Preferencias en memoria: para las pruebas y para cuando la base local no abre.
class PreferenciasEnMemoria implements PreferenciasPort {
  PreferenciasEnMemoria({
    this._modo = PreferenciaModo.automatico,
    this._tamano = 1,
  });

  PreferenciaModo _modo;
  int _tamano;

  @override
  Future<PreferenciaModo> modo() async => _modo;

  @override
  Future<void> guardarModo(PreferenciaModo modo) async => _modo = modo;

  @override
  Future<int> tamanoTexto() async => _tamano;

  @override
  Future<void> guardarTamanoTexto(int indice) async => _tamano = indice;
}
