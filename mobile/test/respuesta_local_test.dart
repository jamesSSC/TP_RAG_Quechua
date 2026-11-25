import 'package:flutter_test/flutter_test.dart';
import 'package:quechua_wanka/dominio/objetos_valor/idioma.dart';
import 'package:quechua_wanka/infraestructura/adaptadores/salida/asistente_local.dart';

/// Pruebas del asistente offline contra el indice real empaquetado.
///
/// No hay dobles: se carga el corpus de 3605 fragmentos y la tabla de traduccion tal como
/// viajan en la aplicacion, porque lo que se quiere comprobar es precisamente que esos
/// datos y este codigo producen juntos la respuesta correcta.
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late AsistenteLocal asistente;

  setUpAll(() async {
    // El historial va a SQLite, que no esta disponible fuera del dispositivo. La carga es
    // tolerante y sigue sin el, que es justo el comportamiento que interesa asegurar.
    asistente = await AsistenteLocal.cargar();
  });

  test(
    'una consulta en espanol compone la correspondencia con sus matices',
    () async {
      final r = await asistente.consultar('perro');

      expect(r.abstenida, isFalse);
      expect(r.idioma, Idioma.espanol);
      expect(r.texto, contains('Allqu'));
      expect(r.texto, contains('ashuti'));
      // El matiz de la entrada se conserva como tal, sin mezclarse con la forma principal.
      expect(r.texto, contains('perrito'));
      expect(r.texto, contains('Pichi'));
      // Y no se explica el significado de ninguna parte, que es lo que el modelo hacia.
      expect(r.texto.toLowerCase(), isNot(contains('significa')));
      expect(r.respaldo.first.procedencia.pagina, greaterThan(0));
    },
  );

  test(
    'una palabra inglesa suelta se resuelve pasando por el espanol',
    () async {
      final r = await asistente.consultar('love');

      expect(r.abstenida, isFalse);
      expect(r.idioma, Idioma.ingles);
      // La frase nombra lo que escribio el usuario, no el termino intermedio.
      expect(r.texto, contains('"love"'));
      expect(r.texto, isNot(contains('"amor"')));
      expect(r.texto, contains('Kuyay'));
      // Con que se busco se dice aparte, no dentro de la respuesta.
      expect(r.consultaTraducida, 'amor');
    },
  );

  test('un termino con varios sentidos los entrega todos', () async {
    // "boiled corn" lleva a comijn, mote, moteado y choclo, y las cuatro son entradas
    // reales. Elegir una por su puntuacion seria elegir por ruido: la puntuacion de cada
    // candidata mide lo bien que casa consigo misma.
    final r = await asistente.consultar('boiled corn');

    expect(r.abstenida, isFalse);
    expect(r.texto, contains('several entries'));
    expect(r.texto, contains('mote'));
    expect(r.texto, contains('Muti'));
    expect(r.respaldo.length, greaterThan(1));
  });

  test(
    'una consulta fuera de cobertura se abstiene y no ofrece nada',
    () async {
      final r = await asistente.consultar('cual es la capital de francia');

      expect(r.abstenida, isTrue);
      expect(r.respaldo, isEmpty);
      expect(r.pasajes, isEmpty);
    },
  );

  test('una pregunta de gramatica entrega pasajes sin afirmar nada', () async {
    final r = await asistente.consultar('que es el sufijo ablativo');

    expect(r.abstenida, isTrue, reason: 'sobre prosa el sistema no afirma');
    expect(r.pasajes, isNotEmpty);
    expect(r.pasajes.first.texto.toLowerCase(), contains('ablativo'));
    expect(r.pasajes.first.procedencia.pagina, greaterThan(0));
  });

  test('el corpus reparado llega legible a la respuesta', () async {
    // El OCR habia separado los acentos de su palabra en el 70,6 % de la prosa. Como los
    // pasajes se muestran literales, que esten rejuntados es visible para el usuario.
    final r = await asistente.consultar(
      'como se forma el plural de los pronombres',
    );

    expect(r.pasajes, isNotEmpty);
    final texto = r.pasajes.map((p) => p.texto).join(' ');
    expect(
      RegExp(r'(?<=[A-Za-zÀ-ÿ])\s[áéíóúüñ]\s(?=[A-Za-zÀ-ÿ])').hasMatch(texto),
      isFalse,
      reason: 'no deben quedar acentos sueltos entre espacios',
    );
  });
}
