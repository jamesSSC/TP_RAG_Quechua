import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:quechua_wanka/infraestructura/adaptadores/salida/asistente_local.dart';

import 'datos_evaluacion.dart';

/// Arnés de las 248 consultas de `evaluacion_v2.json` ejecutado EN EL DISPOSITIVO, sobre el
/// modo sin conexión (índice exportado + compositor determinista), sin red (HU-10.2).
///
/// Mide lo mismo que `evaluar_pipeline_movil.py` en el escritorio:
/// - A, B y D: recall@5 (algún fragmento oro entre los 5 de respaldo) y consultas atendidas;
/// - C: falsos positivos (consultas fuera de cobertura que NO se abstuvieron). Debe ser 0.
/// Y además la latencia de cada consulta en el dispositivo (P50 y P95) y el arranque.
///
/// Ejecutar: `flutter test integration_test/arnes_dispositivo_test.dart -d DISPOSITIVO`
/// La salida se marca con la línea `RESULTADO_ARNES` en JSON para guardarla como evidencia.
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('arnés de 248 consultas sin conexión en el dispositivo', (tester) async {
    final reloj = Stopwatch()..start();
    // Sin base de historial: el arnés no debe dejar 248 consultas en el teléfono.
    late AsistenteLocal asistente;
    await tester.runAsync(() async {
      asistente = await AsistenteLocal.cargar(historial: null, sinHistorial: true);
    });
    final arranqueMs = reloj.elapsedMilliseconds;

    final porSubconjunto = <String, Map<String, int>>{};
    final latencias = <double>[];
    final fallos = <String>[];

    for (final caso in evaluacion) {
      final sub = caso['subconjunto']! as String;
      final oro = (caso['oro']! as List<String>).toSet();
      final consulta = caso['consulta']! as String;

      final t = Stopwatch()..start();
      late final dynamic r;
      await tester.runAsync(() async => r = await asistente.consultar(consulta));
      latencias.add(t.elapsedMicroseconds / 1000);

      final c = porSubconjunto.putIfAbsent(
        sub,
        () => {'n': 0, 'atendidas': 0, 'recall5': 0, 'falsos_positivos': 0},
      );
      c['n'] = c['n']! + 1;
      final atendida = !(r.abstenida as bool);
      if (atendida) c['atendidas'] = c['atendidas']! + 1;
      final ids = (r.respaldo as List).take(5).map((f) => f.id as String).toSet();
      if (sub.startsWith('C')) {
        if (atendida) {
          c['falsos_positivos'] = c['falsos_positivos']! + 1;
          fallos.add('${caso['id']} FP');
        }
      } else if (ids.intersection(oro).isNotEmpty) {
        c['recall5'] = c['recall5']! + 1;
      } else {
        fallos.add('${caso['id']} sin oro en top-5');
      }
    }

    latencias.sort();
    double percentil(double p) => latencias[((latencias.length - 1) * p).round()];
    final resultado = {
      'n_consultas': latencias.length,
      'arranque_ms': arranqueMs,
      'latencia_ms': {
        'p50': percentil(0.50),
        'p95': percentil(0.95),
        'max': latencias.last,
        'media': latencias.reduce((a, b) => a + b) / latencias.length,
      },
      'por_subconjunto': porSubconjunto,
      'fallos': fallos,
    };
    // ignore: avoid_print
    print('RESULTADO_ARNES ${jsonEncode(resultado)}');

    expect(porSubconjunto['C_fuera_de_cobertura']!['falsos_positivos'], 0);
  });
}
