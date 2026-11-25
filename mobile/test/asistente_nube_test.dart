import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:quechua_wanka/dominio/objetos_valor/modo_consulta.dart';
import 'package:quechua_wanka/dominio/puertos/asistente_port.dart';
import 'package:quechua_wanka/infraestructura/adaptadores/salida/asistente_nube.dart';

/// Doble de la API: respuestas con la forma exacta de `RespuestaSalida` (esquemas.py).
http.Response _json(
  Object cuerpo, {
  int estado = 200,
  Map<String, String>? cabeceras,
}) => http.Response.bytes(
  utf8.encode(jsonEncode(cuerpo)),
  estado,
  headers: {'content-type': 'application/json', ...?cabeceras},
);

const _respuestaZorro = {
  'consulta_id': 'c1',
  'texto': 'En quechua wanka, «zorro» se dice Atuq.',
  'abstenida': false,
  'idioma': 'es',
  'similitud_maxima': 0.6104,
  'aviso': 'Consulta sobre fuentes documentales publicadas.',
  'respaldo': [
    {
      'fragmento_id': '35d5d6d6b8a4',
      'texto': 'ZORRO: Atuq.',
      'documento': '293274822-diccionario-quechua-Wanka-docx.pdf',
      'pagina': 37,
      'puntuacion': 0.6104,
      'similitud': 0.6104,
      'derivado_ocr': false,
      'coincidencia_lema': true,
      'rotulo': null,
    },
  ],
  'pasajes': [],
  'via_respaldo': 'similitud',
  'umbral': 0.48,
  'latencia_ms': 652.0,
  'redactado_por': 'gemini',
  'probabilidad_cobertura': 0.9993,
  'probabilidad_pasajes': 0.0412,
  'abstencion_por_predictor': false,
};

void main() {
  test(
    'convierte la respuesta de la API, con cita, modo y predicción ML',
    () async {
      late http.Request enviada;
      final nube = AsistenteNube(
        urlBase: 'https://api.prueba',
        cliente: MockClient((peticion) async {
          enviada = peticion;
          return _json(_respuestaZorro);
        }),
      );

      final r = await nube.consultar('zorro');

      expect(enviada.method, 'POST');
      expect(enviada.url.toString(), 'https://api.prueba/api/consultas');
      expect(jsonDecode(enviada.body), {'texto': 'zorro'});
      expect(
        enviada.headers.keys.map((k) => k.toLowerCase()),
        isNot(contains('x-admin-token')),
      );
      expect(r.modo, ModoConsulta.enLinea);
      expect(r.respaldo.single.procedencia.pagina, 37);
      expect(r.umbral, 0.48);
      expect(r.probabilidadCobertura, 0.9993);
      expect(r.redactadoPor, 'gemini');
    },
  );

  test(
    'un 429 se convierte en error de límite con la espera de Retry-After',
    () async {
      var llamadas = 0;
      final nube = AsistenteNube(
        urlBase: 'https://api.prueba',
        cliente: MockClient((_) async {
          llamadas++;
          return _json(
            {
              'detail':
                  'Demasiadas consultas seguidas: el límite es 20 por minuto.',
            },
            estado: 429,
            cabeceras: {'retry-after': '37'},
          );
        }),
      );

      await expectLater(
        nube.consultar('zorro'),
        throwsA(
          isA<ErrorConsulta>()
              .having((e) => e.tipo, 'tipo', TipoErrorConsulta.limite)
              .having(
                (e) => e.reintentarEn,
                'espera',
                const Duration(seconds: 37),
              )
              .having((e) => e.esFaltaDeServicio, 'pasa a local', isFalse),
        ),
      );
      expect(llamadas, 1, reason: 'ante un 429 no se reintenta');
    },
  );

  test('sin red se informa como falta de servicio', () async {
    final nube = AsistenteNube(
      urlBase: 'https://api.prueba',
      cliente: MockClient((_) async => throw const SocketException('sin red')),
    );
    await expectLater(
      nube.consultar('zorro'),
      throwsA(
        isA<ErrorConsulta>()
            .having((e) => e.tipo, 'tipo', TipoErrorConsulta.red)
            .having((e) => e.esFaltaDeServicio, 'pasa a local', isTrue),
      ),
    );
  });

  test('un 422 se informa como consulta no válida y no como caída', () async {
    final nube = AsistenteNube(
      urlBase: 'https://api.prueba',
      cliente: MockClient((_) async => _json({'detail': []}, estado: 422)),
    );
    await expectLater(
      nube.consultar(''),
      throwsA(
        isA<ErrorConsulta>()
            .having((e) => e.tipo, 'tipo', TipoErrorConsulta.validacion)
            .having((e) => e.esFaltaDeServicio, 'pasa a local', isFalse),
      ),
    );
  });

  test(
    'la predicción ML incluye las variables y los pesos del modelo',
    () async {
      final nube = AsistenteNube(
        urlBase: 'https://api.prueba',
        cliente: MockClient((p) async {
          if (p.url.path == '/api/modelos') {
            return _json([
              {
                'clave': 'cobertura',
                'coeficientes': {
                  'similitud_maxima': 1.0218,
                  'coincidencia_lema': 1.5836,
                },
              },
            ]);
          }
          return _json({
            'texto': 'zorro',
            'caracteristicas': {
              'similitud_maxima': 0.61,
              'coincidencia_lema': 1.0,
            },
            'cobertura': {
              'probabilidad': 0.99,
              'corte': 0.25,
              'decision': 'con respaldo probable',
              'bloquearia_respuesta': false,
            },
            'pasajes': {
              'probabilidad': 0.04,
              'corte': 0.5,
              'decision': 'retirar pasajes',
            },
          });
        }),
      );

      final p = await nube.predecir('zorro');
      expect(p.probabilidadCobertura, 0.99);
      expect(p.cortePasajes, 0.5);
      expect(p.caracteristicas['similitud_maxima'], 0.61);
      expect(p.pesosCobertura['coincidencia_lema'], 1.5836);
    },
  );

  test('las fuentes se leen del registro público', () async {
    final nube = AsistenteNube(
      urlBase: 'https://api.prueba',
      cliente: MockClient(
        (p) async => _json([
          {
            'id': 'f1',
            'titulo': 'Diccionario quechua wanka',
            'entidad_publicadora': 'Entidad',
            'licenciamiento': 'Uso académico',
            'fecha_extraccion': '2026-09-21',
            'nombre_archivo': '293274822-diccionario-quechua-Wanka-docx.pdf',
            'paginas_totales': 37,
            'paginas_con_texto': 37,
            'derivado_ocr': false,
            'cobertura_extraccion': 1.0,
          },
        ]),
      ),
    );
    final fuentes = await nube.fuentes();
    expect(fuentes.single.nombreVisible, 'Diccionario quechua wanka');
    expect(fuentes.single.licenciamiento, 'Uso académico');
  });
}
