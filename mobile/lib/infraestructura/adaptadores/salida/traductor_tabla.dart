import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;

import '../../../aplicacion/servicios/depurador_consulta.dart';
import 'indice_portable.dart' show carpetaIndice;

/// Traduce la consulta del ingles al espanol por tabla calculada en tiempo de compilacion.
///
/// El corpus esta indexado en espanol, de modo que una consulta inglesa tiene que pasar
/// por el espanol antes de poder buscarse: ingles -> espanol -> quechua, nunca directo.
///
/// La tabla sustituye al modelo que resolvia ese paso. Ningun modelo que quepa en un
/// telefono lo hace bien (gemma3:1b alcanza 57,5 % de recall y traduce "cave" por "tumba"),
/// mientras que la tabla, generada una sola vez con qwen3.5:4b sobre los 2257 lemas del
/// corpus, alcanza el 100 % y ocupa 177 KB. Ademas se puede revisar y corregir a mano, que
/// es lo que un modelo no permite.
class TraductorTabla {
  TraductorTabla._(this._tabla);

  final Map<String, List<String>> _tabla;

  static final _prefijoInfinitivo = RegExp(r'^to\s+');
  static const _largoMinimoCompuesto = 7;

  static Future<TraductorTabla> cargar() async {
    final crudo =
        jsonDecode(
              await rootBundle.loadString(
                '$carpetaIndice/traduccion_en_es.json',
              ),
            )
            as Map<String, dynamic>;
    return TraductorTabla._({
      for (final entrada in crudo.entries)
        DepuradorConsulta.normalizar(entrada.key).trim():
            (entrada.value as List<dynamic>).cast<String>(),
    });
  }

  /// Todas las lecturas espanolas plausibles del termino, no solo la mejor.
  ///
  /// Un termino ingles corriente corresponde a varios lemas del corpus ("twin" -> doble,
  /// gemelo, mellizo) y elegir uno de antemano descarta el correcto la mayoria de las
  /// veces. La recuperacion se ejecuta con todas y el umbral decide.
  ///
  /// [aproximar] habilita las busquedas por aproximacion, que solo son seguras cuando ya
  /// consta que la consulta esta en ingles: "panel solar" y "placa base" son sintagmas
  /// espanoles cuya ultima palabra existe en ingles.
  List<String> candidatas(String texto, {bool aproximar = false}) {
    final clave = DepuradorConsulta.normalizar(texto).trim();
    if (clave.isEmpty) return const [];

    // La busqueda exacta es segura en cualquier idioma: si el termino figura tal cual
    // como palabra inglesa, es que lo es. Se unen todas las lecturas en lugar de
    // quedarse con la primera que acierte, porque la tabla contiene a la vez "burp"
    // (de eructar) y "to burp" (de pedar).
    final claves = <String>[clave, clave.replaceFirst(_prefijoInfinitivo, '')];

    if (aproximar) {
      if (clave.contains(' ')) {
        claves.add(clave.split(' ').last);
      } else if (clave.length >= _largoMinimoCompuesto) {
        claves.addAll(_descomponer(clave));
      }
    }

    final reunidas = <String>[];
    for (final candidata in claves.toSet()) {
      for (final opcion in _tabla[candidata] ?? const <String>[]) {
        if (!reunidas.contains(opcion)) reunidas.add(opcion);
      }
    }
    return reunidas;
  }

  /// Parte un compuesto ingles ("lightweight", "hillside") y lo acepta solo si AMBAS
  /// mitades son claves conocidas, de modo que la descomposicion no invente terminos.
  List<String> _descomponer(String clave) {
    for (var corte = 3; corte < clave.length - 2; corte++) {
      final izquierda = clave.substring(0, corte);
      final derecha = clave.substring(corte);
      if (_tabla.containsKey(izquierda) && _tabla.containsKey(derecha)) {
        return [izquierda, derecha];
      }
    }
    return const [];
  }

  bool conoce(String texto) => candidatas(texto).isNotEmpty;
}
