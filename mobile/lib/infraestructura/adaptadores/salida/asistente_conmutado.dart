import 'dart:async';

import 'package:flutter/foundation.dart'
    show ValueNotifier, debugPrint, kReleaseMode;

import '../../../dominio/entidades/entrada_historial.dart';
import '../../../dominio/entidades/fuente.dart';
import '../../../dominio/entidades/prediccion_ml.dart';
import '../../../dominio/entidades/respuesta.dart';
import '../../../dominio/objetos_valor/modo_consulta.dart';
import '../../../dominio/puertos/asistente_port.dart';
import '../../../dominio/puertos/modo_port.dart';
import '../../configuracion.dart';
import 'historial_sqlite.dart';

/// Cumple el puerto eligiendo entre la nube (principal) y el corpus del telefono (respaldo).
///
/// Es un adaptador mas: la pantalla le habla igual que hablaria a cualquiera de los otros
/// dos, y ninguno de ellos sabe que existe el otro (ADR-038).
///
/// - **Automatico:** se pregunta a la nube; si no hay red, si no responde en
///   [esperaAutomatica] o si devuelve un 5xx, contesta el corpus local y la respuesta lo dice.
/// - **Solo en linea:** siempre la nube; sus errores llegan tal cual a la pantalla.
/// - **Solo sin conexion:** siempre el corpus local; nada sale del telefono.
///
/// Un 429 nunca provoca el cambio de modo ni un reintento: se informa y se espera a que la
/// persona vuelva a intentar (ADR-037). Pasar al corpus local para esquivar el limite
/// convertiria una regla de la nube en un comportamiento distinto sin que nadie lo decida.
class AsistenteConmutado implements AsistentePort, ModoPort {
  AsistenteConmutado({
    required this._nube,
    required this._local,
    this._historial,
    PreferenciaModo preferencia = PreferenciaModo.automatico,
    this.esperaAutomatica = Configuracion.esperaAutomatica,
  }) : preferencia = ValueNotifier(preferencia),
       modoActivo = ValueNotifier(
         preferencia == PreferenciaModo.sinConexion
             ? ModoConsulta.sinConexion
             : ModoConsulta.enLinea,
       );

  final AsistentePort _nube;
  final AsistentePort _local;
  final HistorialSqlite? _historial;
  final Duration esperaAutomatica;

  /// Lo que eligio la persona en el selector.
  @override
  final ValueNotifier<PreferenciaModo> preferencia;

  /// El modo que esta en uso ahora mismo. Es lo que muestra el indicador de la cabecera.
  @override
  final ValueNotifier<ModoConsulta> modoActivo;

  @override
  void cambiarPreferencia(PreferenciaModo nueva) {
    preferencia.value = nueva;
    modoActivo.value = nueva == PreferenciaModo.sinConexion
        ? ModoConsulta.sinConexion
        : ModoConsulta.enLinea;
  }

  @override
  Future<Respuesta> consultar(String texto) async {
    final reloj = Stopwatch()..start();
    final respuesta = await _conRespaldo(
      enNube: () => _nube.consultar(texto),
      enLocal: () => _local.consultar(texto),
      marcar: (r, aviso) =>
          r.conModo(ModoConsulta.sinConexion, avisoModo: aviso),
    );
    // Se registra aqui, y no dentro de la llamada a la nube: si la nube contesta tarde, despues
    // de que ya respondio el telefono, esa respuesta no se uso y no debe figurar en el
    // historial. El adaptador local registra las suyas.
    if (respuesta.modo == ModoConsulta.enLinea) {
      await _registrar(texto, respuesta);
    }
    if (!kReleaseMode) {
      debugPrint(
        'MEDICION total_ms=${reloj.elapsedMilliseconds} '
        'modo=${respuesta.modo.codigo} abstenida=${respuesta.abstenida}',
      );
    }
    return respuesta;
  }

  @override
  Future<EstadoSistema> estado() => _conRespaldo(
    enNube: _nube.estado,
    enLocal: _local.estado,
    marcar: (e, _) => e,
  );

  @override
  Future<List<Fuente>> fuentes() => _conRespaldo(
    enNube: _nube.fuentes,
    enLocal: _local.fuentes,
    marcar: (f, _) => f,
  );

  @override
  Future<PrediccionMl> predecir(String texto) => _conRespaldo(
    enNube: () => _nube.predecir(texto),
    enLocal: () => _local.predecir(texto),
    marcar: (p, _) => p,
  );

  /// El historial es siempre el del telefono, con el modo de cada consulta.
  @override
  Future<List<EntradaHistorial>> historial({int limite = 20}) =>
      _local.historial(limite: limite);

  Future<T> _conRespaldo<T>({
    required Future<T> Function() enNube,
    required Future<T> Function() enLocal,
    required T Function(T, String) marcar,
  }) async {
    switch (preferencia.value) {
      case PreferenciaModo.sinConexion:
        modoActivo.value = ModoConsulta.sinConexion;
        return enLocal();
      case PreferenciaModo.enLinea:
        final valor = await enNube();
        modoActivo.value = ModoConsulta.enLinea;
        return valor;
      case PreferenciaModo.automatico:
        try {
          final valor = await enNube().timeout(
            esperaAutomatica,
            onTimeout: () => throw const ErrorConsulta(
              'La nube no respondió a tiempo.',
              tipo: TipoErrorConsulta.tiempo,
            ),
          );
          modoActivo.value = ModoConsulta.enLinea;
          return valor;
        } on ErrorConsulta catch (e) {
          if (!e.esFaltaDeServicio) rethrow;
          modoActivo.value = ModoConsulta.sinConexion;
          final aviso = switch (e.tipo) {
            TipoErrorConsulta.tiempo =>
              'La nube no respondió en ${esperaAutomatica.inSeconds} s (puede estar '
                  'activándose): se respondió con el corpus del teléfono.',
            TipoErrorConsulta.red =>
              'Sin conexión con la nube: se respondió con el corpus del teléfono.',
            _ =>
              'La nube devolvió un error: se respondió con el corpus del teléfono.',
          };
          return marcar(await enLocal(), aviso);
        }
    }
  }

  Future<void> _registrar(String texto, Respuesta r) async {
    try {
      await _historial?.registrar(
        EntradaHistorial(
          consulta: texto,
          respuesta: r.texto,
          abstenida: r.abstenida,
          similitudMaxima: r.similitudMaxima,
          momento: DateTime.now(),
          modo: ModoConsulta.enLinea,
        ),
      );
    } catch (_) {
      // El historial es accesorio: un fallo al guardarlo no invalida la respuesta.
    }
  }
}
