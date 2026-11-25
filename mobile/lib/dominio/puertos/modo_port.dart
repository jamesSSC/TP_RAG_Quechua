import 'package:flutter/foundation.dart' show ValueListenable;

import '../objetos_valor/modo_consulta.dart';

/// Puerto del selector de modo: que modo esta en uso y que eligio la persona.
///
/// Lo cumple el adaptador que conmuta entre la nube y el corpus local. La pantalla solo ve
/// este contrato, de modo que puede probarse con un doble sin red. `ValueListenable` es la
/// unica pieza de Flutter que entra en el dominio: un valor observable, sin interfaz grafica.
abstract interface class ModoPort {
  ValueListenable<ModoConsulta> get modoActivo;

  ValueListenable<PreferenciaModo> get preferencia;

  void cambiarPreferencia(PreferenciaModo nueva);
}
