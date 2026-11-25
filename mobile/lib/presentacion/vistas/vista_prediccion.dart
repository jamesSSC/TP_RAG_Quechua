import 'package:flutter/material.dart';

import '../../dominio/entidades/prediccion_ml.dart';
import '../../dominio/puertos/asistente_port.dart';
import '../tema.dart';
import '../widgets/barra_probabilidad.dart';

const _nombres = {
  'similitud_maxima': 'Similitud máxima',
  'margen_top1_top2': 'Margen 1.º − 2.º',
  'similitud_media_top5': 'Similitud media top-5',
  'dispersion_top5': 'Dispersión top-5',
  'similitud_prosa_maxima': 'Similitud prosa máx.',
  'similitud_prosa_media_top3': 'Similitud prosa media',
  'palabras_compartidas_prosa': 'Palabras compartidas',
  'proporcion_compartida_prosa': 'Proporción compartida',
  'terminos_consulta': 'Términos de la consulta',
  'proporcion_fuera_vocabulario': 'Fuera de vocabulario',
  'coincidencia_lema': 'Coincidencia de lema',
};

/// Prueba de los dos modelos predictivos del PMV2 (`POST /api/predicciones`), sin responder
/// ni registrar la consulta. Solo en línea: el teléfono no ejecuta los modelos.
class VistaPrediccion extends StatefulWidget {
  const VistaPrediccion({super.key, required this.asistente});

  final AsistentePort asistente;

  @override
  State<VistaPrediccion> createState() => _VistaPrediccionState();
}

class _VistaPrediccionState extends State<VistaPrediccion> {
  static const _ejemplos = [
    '¿cómo se dice zorro en quechua wanka?',
    '¿cómo se dice criptomoneda en quechua wanka?',
    '¿Para qué sirven los sufijos en la gramática?',
  ];

  final _controlador = TextEditingController();
  bool _cargando = false;
  PrediccionMl? _prediccion;
  ErrorConsulta? _error;

  @override
  void dispose() {
    _controlador.dispose();
    super.dispose();
  }

  Future<void> _predecir(String texto) async {
    final limpio = texto.trim();
    if (limpio.isEmpty) return;
    _controlador.text = limpio;
    setState(() {
      _cargando = true;
      _error = null;
    });
    try {
      final p = await widget.asistente.predecir(limpio);
      if (mounted) setState(() => _prediccion = p);
    } on ErrorConsulta catch (e) {
      if (mounted) {
        setState(() {
          _error = e;
          _prediccion = null;
        });
      }
    } finally {
      if (mounted) setState(() => _cargando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final p = _prediccion;
    return ListView(
      key: const Key('vista-prediccion'),
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
      children: [
        Text('Predicción ML', style: tema.textTheme.titleLarge),
        const SizedBox(height: 4),
        Text(
          'Prueba los dos modelos de aprendizaje automático con una consulta. No se responde '
          'ni se registra. Predicción 1: probabilidad de respaldo documental (corte 0,25). '
          'Predicción 2: probabilidad de que los pasajes de prosa traten la pregunta (corte 0,50).',
          style: tema.textTheme.bodySmall,
        ),
        const SizedBox(height: 12),
        TextField(
          key: const Key('campo-prediccion'),
          controller: _controlador,
          maxLength: 300,
          enabled: !_cargando,
          textInputAction: TextInputAction.done,
          onSubmitted: _predecir,
          decoration: const InputDecoration(
            hintText: 'Escribe una consulta en español o inglés',
          ),
        ),
        SizedBox(
          width: double.infinity,
          child: FilledButton(
            key: const Key('boton-predecir'),
            onPressed: _cargando ? null : () => _predecir(_controlador.text),
            child: _cargando
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Paleta.papel,
                    ),
                  )
                : const Text('Predecir'),
          ),
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final e in _ejemplos)
              ActionChip(
                label: Text(e),
                backgroundColor: Paleta.blanco,
                side: const BorderSide(color: Paleta.borde),
                onPressed: _cargando ? null : () => _predecir(e),
              ),
          ],
        ),
        if (_error != null) ...[
          const SizedBox(height: 16),
          Container(
            key: Key(
              _error!.tipo == TipoErrorConsulta.noDisponible
                  ? 'prediccion-no-disponible'
                  : 'prediccion-error',
            ),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Paleta.abstencionFondo,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Paleta.abstencion),
            ),
            child: Text(
              _error!.mensaje,
              style: tema.textTheme.bodyMedium?.copyWith(
                color: Paleta.abstencion,
              ),
            ),
          ),
        ],
        if (p != null) ...[
          const SizedBox(height: 16),
          Container(
            key: const Key('resultado-prediccion'),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Paleta.blanco,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Paleta.borde),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Predicción para «${p.texto}»',
                  style: tema.textTheme.titleMedium,
                ),
                const SizedBox(height: 12),
                if (p.probabilidadCobertura != null)
                  BarraProbabilidad(
                    etiqueta:
                        'Predicción 1 · probabilidad de respaldo documental',
                    valor: p.probabilidadCobertura!,
                    corte: p.corteCobertura,
                  ),
                if (p.decisionCobertura != null)
                  Text(
                    '${p.decisionCobertura}'
                    '${p.bloquearia ? ' · por debajo del corte: el sistema se abstendría aunque la similitud lo permitiera' : ''}',
                    style: tema.textTheme.bodySmall,
                  ),
                const SizedBox(height: 10),
                if (p.probabilidadPasajes != null)
                  BarraProbabilidad(
                    etiqueta:
                        'Predicción 2 · probabilidad de que los pasajes traten la pregunta',
                    valor: p.probabilidadPasajes!,
                    corte: p.cortePasajes,
                  ),
                if (p.decisionPasajes != null)
                  Text(p.decisionPasajes!, style: tema.textTheme.bodySmall),
                if (p.caracteristicas.isNotEmpty) ...[
                  const SizedBox(height: 14),
                  const Divider(),
                  const SizedBox(height: 8),
                  Text(
                    'Variables del modelo de cobertura',
                    style: tema.textTheme.titleSmall,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Valor que recibió el modelo y peso de cada variable (coeficiente '
                    'estandarizado de la regresión logística): un peso positivo empuja hacia '
                    '«hay respaldo» y uno negativo hacia la abstención.',
                    style: tema.textTheme.bodySmall,
                  ),
                  const SizedBox(height: 8),
                  _TablaVariables(prediccion: p),
                ],
              ],
            ),
          ),
        ],
      ],
    );
  }
}

class _TablaVariables extends StatelessWidget {
  const _TablaVariables({required this.prediccion});

  final PrediccionMl prediccion;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final claves = prediccion.caracteristicas.keys.toList()
      ..sort(
        (a, b) => (prediccion.pesosCobertura[b]?.abs() ?? 0).compareTo(
          prediccion.pesosCobertura[a]?.abs() ?? 0,
        ),
      );
    final maximo = prediccion.pesosCobertura.values.fold<double>(
      0.0001,
      (m, v) => v.abs() > m ? v.abs() : m,
    );
    String fmt(double v, int d) => v.toStringAsFixed(d).replaceAll('.', ',');
    return Column(
      key: const Key('tabla-variables'),
      children: [
        for (final k in claves)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 5),
            child: Row(
              children: [
                Expanded(
                  flex: 5,
                  child: Text(
                    _nombres[k] ?? k,
                    style: tema.textTheme.bodySmall,
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    fmt(prediccion.caracteristicas[k]!, 3),
                    textAlign: TextAlign.right,
                    style: tema.textTheme.bodySmall?.copyWith(
                      color: Paleta.tinta,
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  flex: 4,
                  child: prediccion.pesosCobertura[k] == null
                      ? const SizedBox.shrink()
                      : _BarraPeso(
                          valor: prediccion.pesosCobertura[k]!,
                          maximo: maximo,
                        ),
                ),
              ],
            ),
          ),
      ],
    );
  }
}

class _BarraPeso extends StatelessWidget {
  const _BarraPeso({required this.valor, required this.maximo});

  final double valor;
  final double maximo;

  @override
  Widget build(BuildContext context) {
    final positivo = valor >= 0;
    final fraccion = (valor.abs() / maximo).clamp(0.0, 1.0);
    return Row(
      children: [
        Expanded(
          child: Align(
            alignment: Alignment.centerRight,
            child: FractionallySizedBox(
              widthFactor: positivo ? 0 : fraccion,
              child: Container(
                height: 8,
                color: Paleta.abstencion.withValues(alpha: 0.6),
              ),
            ),
          ),
        ),
        Container(width: 1, height: 14, color: Paleta.tinta),
        Expanded(
          child: Align(
            alignment: Alignment.centerLeft,
            child: FractionallySizedBox(
              widthFactor: positivo ? fraccion : 0,
              child: Container(height: 8, color: Paleta.acento),
            ),
          ),
        ),
        const SizedBox(width: 6),
        SizedBox(
          width: 42,
          child: Text(
            '${positivo ? '+' : '−'}${valor.abs().toStringAsFixed(2).replaceAll('.', ',')}',
            textAlign: TextAlign.right,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
      ],
    );
  }
}
