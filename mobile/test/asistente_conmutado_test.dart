import 'package:flutter_test/flutter_test.dart';
import 'package:quechua_wanka/dominio/entidades/entrada_historial.dart';
import 'package:quechua_wanka/dominio/entidades/fuente.dart';
import 'package:quechua_wanka/dominio/entidades/prediccion_ml.dart';
import 'package:quechua_wanka/dominio/entidades/respuesta.dart';
import 'package:quechua_wanka/dominio/objetos_valor/idioma.dart';
import 'package:quechua_wanka/dominio/objetos_valor/modo_consulta.dart';
import 'package:quechua_wanka/dominio/puertos/asistente_port.dart';
import 'package:quechua_wanka/infraestructura/adaptadores/salida/asistente_conmutado.dart';

/// Doble de un adaptador: responde, falla o tarda según se le pida.
class Adaptador implements AsistentePort {
  Adaptador(this.modo, {this.error, this.retraso = Duration.zero});

  final ModoConsulta modo;
  ErrorConsulta? error;
  Duration retraso;
  int llamadas = 0;

  @override
  Future<Respuesta> consultar(String texto) async {
    llamadas++;
    if (retraso > Duration.zero) await Future<void>.delayed(retraso);
    if (error != null) throw error!;
    return Respuesta(
      consultaId: '${modo.codigo}-$llamadas',
      texto: 'respuesta ${modo.codigo}',
      abstenida: false,
      idioma: Idioma.espanol,
      modo: modo,
    );
  }

  @override
  Future<EstadoSistema> estado() async {
    llamadas++;
    if (error != null) throw error!;
    return EstadoSistema(
      fragmentosIndexados: 3605,
      umbralAbstencion: 0.48,
      disponible: true,
      modo: modo,
    );
  }

  @override
  Future<List<Fuente>> fuentes() async => [Fuente(nombreArchivo: modo.codigo)];

  @override
  Future<List<EntradaHistorial>> historial({int limite = 20}) async => const [];

  @override
  Future<PrediccionMl> predecir(String texto) async {
    if (modo == ModoConsulta.sinConexion) {
      throw const ErrorConsulta('no', tipo: TipoErrorConsulta.noDisponible);
    }
    if (error != null) throw error!;
    return PrediccionMl(
      texto: texto,
      probabilidadCobertura: 0.9,
      corteCobertura: 0.25,
      probabilidadPasajes: 0.1,
      cortePasajes: 0.5,
    );
  }
}

const _sinRed = ErrorConsulta('sin red', tipo: TipoErrorConsulta.red);

void main() {
  late Adaptador nube;
  late Adaptador local;

  setUp(() {
    nube = Adaptador(ModoConsulta.enLinea);
    local = Adaptador(ModoConsulta.sinConexion);
  });

  AsistenteConmutado conmutador([
    PreferenciaModo p = PreferenciaModo.automatico,
  ]) => AsistenteConmutado(
    nube: nube,
    local: local,
    preferencia: p,
    esperaAutomatica: const Duration(milliseconds: 200),
  );

  test('automático: con red responde la nube', () async {
    final c = conmutador();
    final r = await c.consultar('zorro');
    expect(r.modo, ModoConsulta.enLinea);
    expect(c.modoActivo.value, ModoConsulta.enLinea);
    expect(local.llamadas, 0);
  });

  test('automático: sin red pasa al corpus local y lo dice', () async {
    nube.error = _sinRed;
    final c = conmutador();
    final r = await c.consultar('zorro');
    expect(r.modo, ModoConsulta.sinConexion);
    expect(r.avisoModo, contains('Sin conexión con la nube'));
    expect(c.modoActivo.value, ModoConsulta.sinConexion);
  });

  test(
    'automático: si la nube tarda más de la espera, contesta el teléfono',
    () async {
      nube.retraso = const Duration(seconds: 2);
      final c = conmutador();
      final r = await c.consultar('zorro');
      expect(r.modo, ModoConsulta.sinConexion);
      expect(r.avisoModo, contains('no respondió'));
    },
  );

  test('automático: un 5xx también pasa al corpus local', () async {
    nube.error = const ErrorConsulta(
      'caída',
      tipo: TipoErrorConsulta.servicio,
      estado: 503,
    );
    final r = await conmutador().consultar('zorro');
    expect(r.modo, ModoConsulta.sinConexion);
  });

  test('automático: vuelve a la nube en cuanto hay red', () async {
    nube.error = _sinRed;
    final c = conmutador();
    await c.consultar('zorro');
    nube.error = null;
    final r = await c.consultar('zorro');
    expect(r.modo, ModoConsulta.enLinea);
    expect(c.modoActivo.value, ModoConsulta.enLinea);
  });

  test('un 429 no cambia de modo ni reintenta: llega tal cual', () async {
    nube.error = const ErrorConsulta(
      'límite',
      tipo: TipoErrorConsulta.limite,
      estado: 429,
      reintentarEn: Duration(seconds: 30),
    );
    final c = conmutador();
    await expectLater(
      c.consultar('zorro'),
      throwsA(
        isA<ErrorConsulta>().having(
          (e) => e.tipo,
          'tipo',
          TipoErrorConsulta.limite,
        ),
      ),
    );
    expect(nube.llamadas, 1);
    expect(local.llamadas, 0);
  });

  test(
    'solo en línea: los errores de red llegan a la pantalla, sin respaldo local',
    () async {
      nube.error = _sinRed;
      final c = conmutador(PreferenciaModo.enLinea);
      await expectLater(c.consultar('zorro'), throwsA(isA<ErrorConsulta>()));
      expect(local.llamadas, 0);
    },
  );

  test('solo sin conexión: nunca se llama a la nube', () async {
    final c = conmutador(PreferenciaModo.sinConexion);
    final r = await c.consultar('zorro');
    await c.estado();
    await c.fuentes();
    expect(r.modo, ModoConsulta.sinConexion);
    expect(nube.llamadas, 0);
  });

  test('cambiar la preferencia cambia el modo activo al momento', () {
    final c = conmutador();
    c.cambiarPreferencia(PreferenciaModo.sinConexion);
    expect(c.modoActivo.value, ModoConsulta.sinConexion);
    c.cambiarPreferencia(PreferenciaModo.enLinea);
    expect(c.modoActivo.value, ModoConsulta.enLinea);
  });

  test(
    'la predicción sin conexión se declara no disponible, no se simula',
    () async {
      final c = conmutador(PreferenciaModo.sinConexion);
      await expectLater(
        c.predecir('zorro'),
        throwsA(
          isA<ErrorConsulta>().having(
            (e) => e.tipo,
            'tipo',
            TipoErrorConsulta.noDisponible,
          ),
        ),
      );
    },
  );
}
