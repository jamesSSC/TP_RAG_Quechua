import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:quechua_wanka/infraestructura/adaptadores/salida/indice_portable.dart';

/// Comprueba que el motor del telefono puntua exactamente igual que el del escritorio.
///
/// El indice no se reimplementa, pero la preparacion de la consulta si: la depuracion, la
/// tokenizacion por palabras y el analizador char_wb de scikit-learn. Una diferencia en
/// cualquiera de esos tres pasos desplazaria las puntuaciones y con ellas el umbral
/// calibrado, que es la salvaguarda contra las formas inventadas. Por eso la equivalencia
/// se demuestra en lugar de suponerse.
///
/// Las referencias las genera backend/scripts/generar_paridad_dart.py.
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late List<dynamic> casos;
  late IndicePortable indice;

  setUpAll(() async {
    casos =
        jsonDecode(File('test/paridad_esperada.json').readAsStringSync())
            as List<dynamic>;
    indice = await IndicePortable.cargar();
  });

  test('el indice carga los 3605 fragmentos y su umbral', () {
    expect(indice.fragmentos.length, 3605);
    expect(indice.umbralAbstencion, 0.48);
  });

  test('la depuracion de la consulta coincide con la del escritorio', () {
    for (final caso in casos.cast<Map<String, dynamic>>()) {
      expect(
        indice.depurador.depurar(caso['consulta'] as String),
        caso['depurada'],
        reason: 'depuracion de "${caso['consulta']}"',
      );
    }
  });

  test('el lemario reconoce los mismos terminos', () {
    for (final caso in casos.cast<Map<String, dynamic>>()) {
      expect(
        indice.esLema(caso['depurada'] as String),
        caso['es_lema'],
        reason: 'es_lema de "${caso['depurada']}"',
      );
    }
  });

  test('las puntuaciones coinciden hasta el redondeo de float32', () {
    // 1e-5 cubre el redondeo acumulado del producto punto en precision simple. Una
    // diferencia mayor significaria que los analizadores divergen, no que se redondea.
    const tolerancia = 1e-5;
    for (final caso in casos.cast<Map<String, dynamic>>()) {
      final consulta = caso['consulta'] as String;
      final esperados = (caso['top'] as List<dynamic>)
          .cast<Map<String, dynamic>>();
      final obtenidos = indice.recuperar(consulta, k: 5);

      expect(
        obtenidos.map((r) => r.id).toList(),
        esperados.map((e) => e['id']).toList(),
        reason: 'orden del top-5 de "$consulta"',
      );
      for (var i = 0; i < esperados.length; i++) {
        expect(
          obtenidos[i].puntuacion,
          closeTo(esperados[i]['puntuacion'] as double, tolerancia),
          reason: 'puntuacion $i de "$consulta"',
        );
        expect(
          obtenidos[i].coincidenciaLema,
          esperados[i]['lema'],
          reason: 'coincidencia de lema $i de "$consulta"',
        );
      }
    }
  });

  test('la recuperacion de prosa coincide', () {
    for (final caso in casos.cast<Map<String, dynamic>>()) {
      final consulta = caso['consulta'] as String;
      final esperados = (caso['prosa'] as List<dynamic>)
          .cast<Map<String, dynamic>>();
      final obtenidos = indice.recuperarProsa(consulta, k: 3);
      expect(
        obtenidos.map((r) => r.id).toList(),
        esperados.map((e) => e['id']).toList(),
        reason: 'pasajes de prosa de "$consulta"',
      );
    }
  });
}
