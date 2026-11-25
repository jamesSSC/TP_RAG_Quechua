import 'dart:async';

import 'package:flutter/material.dart';

import '../../dominio/entidades/entrada_historial.dart';
import '../../dominio/entidades/respuesta.dart';
import '../../dominio/objetos_valor/modo_consulta.dart';
import '../../dominio/puertos/asistente_port.dart';
import '../../dominio/puertos/modo_port.dart';
import '../tema.dart';
import '../widgets/caja_consulta.dart';
import '../widgets/lista_historial.dart';
import '../widgets/tarjeta_respuesta.dart';

/// Texto del aviso de arranque en frio: el mismo de la web (frontend/src/App.jsx).
const avisoArranqueEnFrio =
    'El servicio en la nube se está activando tras un periodo sin uso (plan gratuito). La '
    'primera respuesta puede tardar hasta un minuto; no hace falta recargar.';

/// Vista principal: consulta, respuesta con cita, abstención, pasajes, predicción ML e
/// historial de este teléfono (HU-03, HU-04, HU-06, HU-07, HU-08.1, HU-10.x).
class VistaConsulta extends StatefulWidget {
  const VistaConsulta({
    super.key,
    required this.asistente,
    required this.modo,
    this.avisoEspera = const Duration(milliseconds: 4000),
  });

  final AsistentePort asistente;
  final ModoPort modo;

  /// Mismo umbral que la web (`AVISO_ESPERA_MS`).
  final Duration avisoEspera;

  @override
  State<VistaConsulta> createState() => _VistaConsultaState();
}

class _VistaConsultaState extends State<VistaConsulta> {
  final _controlador = TextEditingController();
  bool _cargando = false;
  bool _esperaLarga = false;
  Respuesta? _respuesta;
  ErrorConsulta? _error;
  String? _ultima;
  List<EntradaHistorial> _historial = const [];
  Timer? _temporizadorAviso;
  Timer? _temporizadorLimite;
  int _segundosLimite = 0;

  @override
  void initState() {
    super.initState();
    _cargarHistorial();
  }

  @override
  void dispose() {
    _temporizadorAviso?.cancel();
    _temporizadorLimite?.cancel();
    _controlador.dispose();
    super.dispose();
  }

  Future<void> _cargarHistorial() async {
    try {
      final entradas = await widget.asistente.historial(limite: 8);
      if (mounted) setState(() => _historial = entradas);
    } catch (_) {
      // El historial es accesorio: su ausencia no debe impedir consultar.
    }
  }

  Future<void> _consultar(String texto) async {
    _temporizadorAviso?.cancel();
    setState(() {
      _cargando = true;
      _esperaLarga = false;
      _error = null;
      _ultima = texto;
    });
    // El aviso solo tiene sentido si la consulta va a la nube.
    if (widget.modo.preferencia.value != PreferenciaModo.sinConexion) {
      _temporizadorAviso = Timer(widget.avisoEspera, () {
        if (mounted && _cargando) setState(() => _esperaLarga = true);
      });
    }
    try {
      final respuesta = await widget.asistente.consultar(texto);
      if (!mounted) return;
      setState(() => _respuesta = respuesta);
      _cargarHistorial();
    } on ErrorConsulta catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e;
        _respuesta = null;
      });
      if (e.tipo == TipoErrorConsulta.limite) {
        _iniciarCuentaAtras(e.reintentarEn);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = ErrorConsulta('No se pudo completar la consulta: $e');
        _respuesta = null;
      });
    } finally {
      _temporizadorAviso?.cancel();
      if (mounted) {
        setState(() {
          _cargando = false;
          _esperaLarga = false;
        });
      }
    }
  }

  /// Ante un 429 no se reintenta solo: se muestra cuánto falta y el botón se habilita después.
  void _iniciarCuentaAtras(Duration? espera) {
    _temporizadorLimite?.cancel();
    setState(
      () => _segundosLimite = (espera ?? const Duration(seconds: 60)).inSeconds,
    );
    _temporizadorLimite = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) return t.cancel();
      setState(
        () => _segundosLimite = _segundosLimite > 0 ? _segundosLimite - 1 : 0,
      );
      if (_segundosLimite == 0) t.cancel();
    });
  }

  void _repetir(String consulta) {
    _controlador.text = consulta;
    _consultar(consulta);
  }

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return ListView(
      key: const Key('vista-consulta'),
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
      children: [
        if (_esperaLarga) ...[
          const _AvisoArranque(),
          const SizedBox(height: 12),
        ],
        CajaConsulta(
          controlador: _controlador,
          cargando: _cargando,
          onEnviar: _consultar,
        ),
        if (_cargando) ...[
          const SizedBox(height: 14),
          Row(
            children: [
              const SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
              const SizedBox(width: 10),
              Text('Buscando en el corpus…', style: tema.textTheme.bodyMedium),
            ],
          ),
        ],
        if (_error != null) ...[
          const SizedBox(height: 14),
          _CajaError(
            error: _error!,
            segundosRestantes: _segundosLimite,
            onReintentar: _cargando || _ultima == null
                ? null
                : () => _consultar(_ultima!),
          ),
        ],
        if (_respuesta != null && !_cargando) ...[
          const SizedBox(height: 16),
          TarjetaRespuesta(respuesta: _respuesta!),
        ],
        if (_respuesta == null && _error == null && !_cargando) ...[
          const SizedBox(height: 16),
          Text(
            'Las respuestas salen únicamente de fuentes publicadas y se citan con documento '
            'y página. Si no hay respaldo, el sistema lo dice en lugar de proponer una forma. '
            'No es un traductor ni una autoridad lingüística.',
            style: tema.textTheme.bodySmall,
          ),
        ],
        const SizedBox(height: 24),
        ListaHistorial(entradas: _historial, onRepetir: _repetir),
      ],
    );
  }
}

class _AvisoArranque extends StatelessWidget {
  const _AvisoArranque();

  @override
  Widget build(BuildContext context) {
    return Semantics(
      liveRegion: true,
      child: Container(
        key: const Key('aviso-arranque'),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Paleta.abstencionFondo,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Paleta.abstencion),
        ),
        child: Text(
          avisoArranqueEnFrio,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: Paleta.abstencion,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}

class _CajaError extends StatelessWidget {
  const _CajaError({
    required this.error,
    required this.segundosRestantes,
    required this.onReintentar,
  });

  final ErrorConsulta error;
  final int segundosRestantes;
  final VoidCallback? onReintentar;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final esLimite = error.tipo == TipoErrorConsulta.limite;
    final bloqueado = esLimite && segundosRestantes > 0;
    return Semantics(
      liveRegion: true,
      child: Container(
        key: Key(esLimite ? 'error-limite' : 'error-consulta'),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Paleta.blanco,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Paleta.error.withValues(alpha: 0.5)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  esLimite ? Icons.hourglass_bottom : Icons.cloud_off,
                  size: 18,
                  color: Paleta.error,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    error.mensaje,
                    style: tema.textTheme.bodyMedium?.copyWith(
                      color: Paleta.error,
                    ),
                  ),
                ),
              ],
            ),
            if (error.esFaltaDeServicio) ...[
              const SizedBox(height: 6),
              Text(
                'Puedes cambiar a «Sin conexión» tocando el indicador de modo de arriba.',
                style: tema.textTheme.bodySmall,
              ),
            ],
            const SizedBox(height: 8),
            OutlinedButton(
              key: const Key('boton-reintentar'),
              onPressed: bloqueado ? null : onReintentar,
              child: Text(
                bloqueado ? 'Reintentar en $segundosRestantes s' : 'Reintentar',
              ),
            ),
          ],
        ),
      ),
    );
  }
}
