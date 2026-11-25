import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// ADR-038: la app no lleva ni el token de administración ni el de pruebas, ni ninguna
/// función que escriba en la nube. Se comprueba sobre el código fuente: si alguien los añade,
/// esta prueba falla antes de que llegue a un APK.
void main() {
  final fuentes = Directory('lib')
      .listSync(recursive: true)
      .whereType<File>()
      .where((f) => f.path.endsWith('.dart'))
      .toList();

  String codigo(File f) => f
      .readAsLinesSync()
      // Los comentarios pueden nombrar los tokens para explicar que no se usan.
      .where((l) => !l.trimLeft().startsWith('//'))
      .join('\n');

  test('ningún archivo envía X-Admin-Token ni el token de pruebas', () {
    for (final f in fuentes) {
      final c = codigo(f);
      expect(
        c.toLowerCase().contains('x-admin-token'),
        isFalse,
        reason: f.path,
      );
      expect(c.contains('ADMIN_TOKEN'), isFalse, reason: f.path);
      expect(c.contains('TOKEN_PRUEBAS'), isFalse, reason: f.path);
      expect(
        c.toLowerCase().contains('x-token-pruebas'),
        isFalse,
        reason: f.path,
      );
    }
  });

  test('la app no borra, edita ni incorpora nada en la nube', () {
    final adaptador = File(
      'lib/infraestructura/adaptadores/salida/asistente_nube.dart',
    );
    final c = codigo(adaptador);
    expect(c.contains('.delete('), isFalse);
    expect(c.contains('.put('), isFalse);
    expect(c.contains('.patch('), isFalse);
    // Los únicos POST son los públicos de lectura: consultar y predecir.
    final posts = RegExp(
      r"\.post\(\s*Uri\.parse\('\$_url(/api/[a-z]+)'",
    ).allMatches(c);
    expect(posts.map((m) => m.group(1)).toSet(), {
      '/api/consultas',
      '/api/predicciones',
    });
  });
}
