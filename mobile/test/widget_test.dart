import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:quechua_wanka/dominio/entidades/entrada_historial.dart';
import 'package:quechua_wanka/dominio/entidades/fragmento_respaldo.dart';
import 'package:quechua_wanka/dominio/entidades/fuente.dart';
import 'package:quechua_wanka/dominio/entidades/prediccion_ml.dart';
import 'package:quechua_wanka/dominio/entidades/procedencia.dart';
import 'package:quechua_wanka/dominio/entidades/respuesta.dart';
import 'package:quechua_wanka/dominio/objetos_valor/idioma.dart';
import 'package:quechua_wanka/dominio/objetos_valor/modo_consulta.dart';
import 'package:quechua_wanka/dominio/puertos/asistente_port.dart';
import 'package:quechua_wanka/dominio/puertos/modo_port.dart';
import 'package:quechua_wanka/dominio/puertos/preferencias_port.dart';
import 'package:quechua_wanka/presentacion/pantalla_principal.dart';
import 'package:quechua_wanka/presentacion/tema.dart';
import 'package:quechua_wanka/presentacion/vistas/vista_consulta.dart';

// Los textos en quechua de estas pruebas son literales del corpus (fragmentos_v3.jsonl):
// ninguna forma se escribe a mano.
const _zorro = FragmentoRespaldo(
  id: '35d5d6d6b8a4',
  texto: 'ZORRO: Atuq.',
  procedencia: Procedencia(
    documento: '293274822-diccionario-quechua-Wanka-docx.pdf',
    pagina: 37,
  ),
  puntuacion: 0.61,
);

/// Doble del puerto: la pantalla se prueba sin red, que es lo que permite la hexagonal.
class AsistenteFalso implements AsistentePort {
  AsistenteFalso({this.respuesta, this.error, this.retraso = Duration.zero});

  Respuesta? respuesta;
  ErrorConsulta? error;
  final Duration retraso;
  final List<String> consultadas = [];
  final List<String> predichas = [];

  @override
  Future<Respuesta> consultar(String texto) async {
    consultadas.add(texto);
    if (retraso > Duration.zero) await Future<void>.delayed(retraso);
    if (error != null) throw error!;
    return respuesta!;
  }

  @override
  Future<List<EntradaHistorial>> historial({int limite = 20}) async => [
    EntradaHistorial(
      consulta: 'zorro',
      respuesta: 'ZORRO: Atuq.',
      abstenida: false,
      similitudMaxima: 0.61,
      momento: DateTime(2026, 11, 19),
      modo: ModoConsulta.enLinea,
    ),
  ];

  @override
  Future<EstadoSistema> estado() async => const EstadoSistema(
    fragmentosIndexados: 3605,
    umbralAbstencion: 0.48,
    disponible: true,
    documentos: 8,
  );

  @override
  Future<List<Fuente>> fuentes() async => const [
    Fuente(
      nombreArchivo: '293274822-diccionario-quechua-Wanka-docx.pdf',
      fragmentos: 2351,
    ),
  ];

  @override
  Future<PrediccionMl> predecir(String texto) async {
    predichas.add(texto);
    return PrediccionMl(
      texto: texto,
      probabilidadCobertura: 0.97,
      corteCobertura: 0.25,
      decisionCobertura: 'con respaldo probable',
      probabilidadPasajes: 0.12,
      cortePasajes: 0.5,
      decisionPasajes: 'retirar pasajes',
      caracteristicas: const {'similitud_maxima': 0.61, 'coincidencia_lema': 1},
      pesosCobertura: const {
        'similitud_maxima': 1.0218,
        'coincidencia_lema': 1.5836,
      },
    );
  }
}

class ModoFalso implements ModoPort {
  ModoFalso([PreferenciaModo inicial = PreferenciaModo.automatico])
    : preferencia = ValueNotifier(inicial),
      modoActivo = ValueNotifier(
        inicial == PreferenciaModo.sinConexion
            ? ModoConsulta.sinConexion
            : ModoConsulta.enLinea,
      );

  @override
  final ValueNotifier<PreferenciaModo> preferencia;

  @override
  final ValueNotifier<ModoConsulta> modoActivo;

  @override
  void cambiarPreferencia(PreferenciaModo nueva) {
    preferencia.value = nueva;
    modoActivo.value = nueva == PreferenciaModo.sinConexion
        ? ModoConsulta.sinConexion
        : ModoConsulta.enLinea;
  }
}

Respuesta _enLinea() => const Respuesta(
  consultaId: 'x',
  texto: 'En quechua wanka, «zorro» se dice Atuq.',
  abstenida: false,
  idioma: Idioma.espanol,
  modo: ModoConsulta.enLinea,
  similitudMaxima: 0.61,
  umbral: 0.48,
  viaRespaldo: 'similitud',
  latenciaMs: 652,
  redactadoPor: 'gemini',
  probabilidadCobertura: 0.97,
  probabilidadPasajes: 0.12,
  respaldo: [_zorro],
);

Future<(AsistenteFalso, ModoFalso, PreferenciasEnMemoria)> _montar(
  WidgetTester tester, {
  Respuesta? respuesta,
  ErrorConsulta? error,
  Duration retraso = Duration.zero,
  PreferenciaModo preferencia = PreferenciaModo.automatico,
}) async {
  tester.view.physicalSize = const Size(1080, 2400);
  tester.view.devicePixelRatio = 2.625;
  addTearDown(tester.view.reset);
  final asistente = AsistenteFalso(
    respuesta: respuesta ?? _enLinea(),
    error: error,
    retraso: retraso,
  );
  final modo = ModoFalso(preferencia);
  final preferencias = PreferenciasEnMemoria();
  await tester.pumpWidget(
    MaterialApp(
      theme: Tema.claro(),
      home: PantallaPrincipal(
        asistente: asistente,
        modo: modo,
        preferencias: preferencias,
      ),
    ),
  );
  await tester.pumpAndSettle();
  return (asistente, modo, preferencias);
}

Future<void> _consultar(WidgetTester tester, String texto) async {
  await tester.enterText(find.byKey(const Key('campo-consulta')), texto);
  await tester.testTextInput.receiveAction(TextInputAction.search);
  await tester.pumpAndSettle();
}

/// Desplaza la vista de consulta hasta que [buscado] quede a la vista.
Future<void> _verHasta(WidgetTester tester, Finder buscado) async {
  await tester.scrollUntilVisible(
    buscado,
    200,
    scrollable: find
        .descendant(
          of: find.byKey(const Key('vista-consulta')),
          matching: find.byType(Scrollable),
        )
        .first,
  );
  await tester.pumpAndSettle();
}

void main() {
  testWidgets(
    'la cabecera muestra el logo, el corpus y el modo activo siempre',
    (tester) async {
      await _montar(tester);
      expect(find.byKey(const Key('logo')), findsOneWidget);
      expect(
        find.textContaining('3 605 fragmentos · 8 documentos'),
        findsOneWidget,
      );
      expect(find.text('En línea · nube'), findsOneWidget);
    },
  );

  testWidgets(
    'una respuesta en línea muestra la cita, de qué modo vino y la predicción ML',
    (tester) async {
      final (asistente, _, _) = await _montar(tester);
      await _consultar(tester, 'zorro');

      expect(asistente.consultadas, ['zorro']);
      expect(
        find.text('En quechua wanka, «zorro» se dice Atuq.'),
        findsOneWidget,
      );
      expect(find.byKey(const Key('origen-en_linea')), findsOneWidget);
      expect(find.textContaining('página 37'), findsOneWidget);
      expect(find.byKey(const Key('prediccion-ml')), findsOneWidget);
      expect(find.textContaining('97,0 %'), findsOneWidget);
    },
  );

  testWidgets(
    'sin conexión la respuesta lo declara y explica que no hay ML en el teléfono',
    (tester) async {
      await _montar(
        tester,
        preferencia: PreferenciaModo.sinConexion,
        respuesta: const Respuesta(
          consultaId: 'l',
          texto: 'ZORRO: Atuq.',
          abstenida: false,
          idioma: Idioma.espanol,
          modo: ModoConsulta.sinConexion,
          similitudMaxima: 0.61,
          respaldo: [_zorro],
        ),
      );
      expect(find.text('Sin conexión · corpus local'), findsOneWidget);
      await _consultar(tester, 'zorro');

      await _verHasta(tester, find.byKey(const Key('prediccion-ml-ausente')));
      expect(find.byKey(const Key('origen-sin_conexion')), findsOneWidget);
      expect(find.byKey(const Key('prediccion-ml-ausente')), findsOneWidget);
      expect(
        find.textContaining('el teléfono no ejecuta los modelos'),
        findsOneWidget,
      );
    },
  );

  testWidgets(
    'la abstención se muestra como resultado, sin ninguna forma quechua',
    (tester) async {
      await _montar(
        tester,
        respuesta: const Respuesta(
          consultaId: 'y',
          texto:
              'No dispongo de respaldo documental para esa consulta en el corpus indexado.',
          abstenida: true,
          idioma: Idioma.espanol,
          modo: ModoConsulta.enLinea,
          similitudMaxima: 0.19,
        ),
      );
      await _consultar(tester, '¿cómo se dice criptomoneda en quechua wanka?');

      expect(find.text('Sin respaldo documental'), findsOneWidget);
      expect(find.byKey(const Key('cita-principal')), findsNothing);
      expect(find.byKey(const Key('error-consulta')), findsNothing);
    },
  );

  testWidgets('una abstención con pasajes los muestra citados y rotulados', (
    tester,
  ) async {
    await _montar(
      tester,
      respuesta: const Respuesta(
        consultaId: 'z',
        texto: 'No tengo una respuesta confirmada para esa consulta.',
        abstenida: true,
        idioma: Idioma.espanol,
        similitudMaxima: 0.21,
        pasajes: [
          FragmentoRespaldo(
            id: '6bd37bce2eef',
            texto: 'El ablativo. Se marca este caso mediante el sufijopiqta',
            procedencia: Procedencia(documento: 'gramatica.pdf', pagina: 133),
            puntuacion: 0.208,
          ),
        ],
      ),
    );
    await _consultar(tester, 'que es el sufijo ablativo');

    expect(find.text('Sin respuesta confirmada'), findsOneWidget);
    expect(find.textContaining('NO ES UNA RESPUESTA'), findsOneWidget);
    expect(find.textContaining('gramatica.pdf — página 133'), findsOneWidget);
  });

  testWidgets(
    'el respaldo completo llega plegado y se despliega con un toque',
    (tester) async {
      await _montar(tester);
      await _consultar(tester, 'zorro');

      expect(find.text('ZORRO: Atuq.'), findsNothing);
      await _verHasta(tester, find.byKey(const Key('plegar-respaldo')));
      await tester.tap(find.byKey(const Key('plegar-respaldo')));
      await tester.pumpAndSettle();
      await _verHasta(tester, find.text('ZORRO: Atuq.'));
      expect(find.text('ZORRO: Atuq.'), findsOneWidget);
    },
  );

  testWidgets(
    'pasados 4 s sin respuesta aparece el aviso de arranque en frío de la web',
    (tester) async {
      await _montar(tester, retraso: const Duration(seconds: 10));
      await tester.enterText(find.byKey(const Key('campo-consulta')), 'zorro');
      await tester.testTextInput.receiveAction(TextInputAction.search);

      await tester.pump(const Duration(seconds: 3));
      expect(find.byKey(const Key('aviso-arranque')), findsNothing);
      await tester.pump(const Duration(seconds: 2));
      expect(find.text(avisoArranqueEnFrio), findsOneWidget);

      await tester.pump(const Duration(seconds: 6));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('aviso-arranque')), findsNothing);
    },
  );

  testWidgets('sin conexión no se muestra el aviso de arranque en frío', (
    tester,
  ) async {
    await _montar(
      tester,
      preferencia: PreferenciaModo.sinConexion,
      retraso: const Duration(seconds: 6),
    );
    await tester.enterText(find.byKey(const Key('campo-consulta')), 'zorro');
    await tester.testTextInput.receiveAction(TextInputAction.search);
    await tester.pump(const Duration(seconds: 5));
    expect(find.byKey(const Key('aviso-arranque')), findsNothing);
    await tester.pumpAndSettle(const Duration(seconds: 2));
  });

  testWidgets('ante un 429 se informa y no se reintenta solo', (tester) async {
    final (asistente, _, _) = await _montar(
      tester,
      error: const ErrorConsulta(
        'Demasiadas consultas seguidas: el límite es 20 por minuto. Inténtalo de nuevo en 30 s.',
        tipo: TipoErrorConsulta.limite,
        estado: 429,
        reintentarEn: Duration(seconds: 30),
      ),
    );
    await tester.enterText(find.byKey(const Key('campo-consulta')), 'zorro');
    await tester.testTextInput.receiveAction(TextInputAction.search);
    await tester.pump();
    await tester.pump();

    expect(find.byKey(const Key('error-limite')), findsOneWidget);
    expect(find.textContaining('límite es 20 por minuto'), findsOneWidget);
    expect(find.text('Reintentar en 30 s'), findsOneWidget);

    // Pasa el tiempo: ni un solo reintento automático.
    await tester.pump(const Duration(seconds: 40));
    expect(asistente.consultadas, ['zorro']);
    expect(find.text('Reintentar'), findsOneWidget);
  });

  testWidgets('el selector manual cambia el modo y la preferencia se guarda', (
    tester,
  ) async {
    final (_, modo, preferencias) = await _montar(tester);
    await tester.tap(find.byKey(const Key('indicador-modo')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('preferencia-sinConexion')));
    await tester.pumpAndSettle();

    expect(modo.preferencia.value, PreferenciaModo.sinConexion);
    expect(find.text('Sin conexión · corpus local'), findsOneWidget);
    expect(await preferencias.modo(), PreferenciaModo.sinConexion);
  });

  testWidgets(
    'A+ agranda el texto y A lo restablece, y la preferencia se guarda',
    (tester) async {
      final (_, _, preferencias) = await _montar(tester);
      double escala() => MediaQuery.textScalerOf(
        tester.element(find.byKey(const Key('subtitulo-estado'))),
      ).scale(1);

      expect(escala(), 1.0);
      await tester.tap(find.byKey(const Key('tamano-mas')));
      await tester.pumpAndSettle();
      expect(escala(), closeTo(1.15, 1e-9));
      expect(await preferencias.tamanoTexto(), 2);
      await tester.tap(find.byKey(const Key('tamano-normal')));
      await tester.pumpAndSettle();
      expect(escala(), 1.0);
    },
  );

  testWidgets(
    'con la letra al máximo se leen la forma, la fuente y el aviso (HU-11)',
    (tester) async {
      await _montar(tester);
      await tester.tap(find.byKey(const Key('tamano-mas')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('tamano-mas')));
      await tester.pumpAndSettle();
      await _consultar(tester, 'zorro');

      expect(tester.takeException(), isNull);
      expect(
        find.text('En quechua wanka, «zorro» se dice Atuq.'),
        findsOneWidget,
      );
      expect(find.textContaining('página 37'), findsOneWidget);
    },
  );

  testWidgets('los botones táctiles miden al menos 48 px', (tester) async {
    await _montar(tester);
    for (final clave in [
      'tamano-menos',
      'tamano-normal',
      'tamano-mas',
      'boton-consultar',
    ]) {
      final tamano = tester.getSize(find.byKey(Key(clave)));
      expect(tamano.height, greaterThanOrEqualTo(48), reason: clave);
    }
    final indicador = tester.getSize(find.byKey(const Key('indicador-modo')));
    expect(indicador.height, greaterThanOrEqualTo(44));
  });

  testWidgets('la pestaña de fuentes lista los documentos', (tester) async {
    await _montar(tester);
    await tester.tap(find.byKey(const Key('pestana-fuentes')));
    await tester.pumpAndSettle();
    expect(
      find.text('293274822 diccionario quechua Wanka docx'),
      findsOneWidget,
    );
    expect(find.textContaining('2351 fragmentos'), findsOneWidget);
  });

  testWidgets(
    'la pestaña de predicción ML muestra las dos probabilidades y las variables',
    (tester) async {
      final (asistente, _, _) = await _montar(tester);
      await tester.tap(find.byKey(const Key('pestana-prediccion')));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.byKey(const Key('campo-prediccion')),
        'zorro',
      );
      await tester.tap(find.byKey(const Key('boton-predecir')));
      await tester.pumpAndSettle();

      expect(asistente.predichas, ['zorro']);
      expect(find.byKey(const Key('resultado-prediccion')), findsOneWidget);
      expect(find.textContaining('97,0 %'), findsOneWidget);
      expect(find.textContaining('12,0 %'), findsOneWidget);
      expect(find.byKey(const Key('tabla-variables')), findsOneWidget);
    },
  );

  testWidgets('tocar una consulta del historial la repite', (tester) async {
    final (asistente, _, _) = await _montar(tester);
    await tester.ensureVisible(find.text('zorro').last);
    await tester.tap(find.text('zorro').last);
    await tester.pumpAndSettle();
    expect(asistente.consultadas, ['zorro']);
  });
}
