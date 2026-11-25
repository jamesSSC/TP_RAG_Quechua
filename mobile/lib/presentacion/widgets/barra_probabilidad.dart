import 'package:flutter/material.dart';

import '../tema.dart';

/// Barra de una probabilidad (o una similitud) con la marca de su corte, como en la web.
class BarraProbabilidad extends StatelessWidget {
  const BarraProbabilidad({
    super.key,
    required this.etiqueta,
    required this.valor,
    this.corte,
    this.comoPorcentaje = true,
  });

  final String etiqueta;
  final double valor;
  final double? corte;
  final bool comoPorcentaje;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final alta = valor >= (corte ?? 0.5);
    final texto = comoPorcentaje
        ? '${(valor * 100).toStringAsFixed(1).replaceAll('.', ',')} %'
        : valor.toStringAsFixed(3).replaceAll('.', ',');
    return Semantics(
      label:
          '$etiqueta: $texto${corte == null ? '' : ', corte ${_fmt(corte!)}'}',
      excludeSemantics: true,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Text(etiqueta, style: tema.textTheme.bodySmall),
                ),
                const SizedBox(width: 8),
                Text(
                  texto,
                  style: tema.textTheme.titleMedium?.copyWith(
                    color: alta ? Paleta.acento : Paleta.abstencion,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            LayoutBuilder(
              builder: (context, limites) {
                final ancho = limites.maxWidth;
                return SizedBox(
                  height: 10,
                  child: Stack(
                    clipBehavior: Clip.none,
                    children: [
                      Container(
                        decoration: BoxDecoration(
                          color: Paleta.papelHundido,
                          borderRadius: BorderRadius.circular(5),
                          border: Border.all(color: Paleta.borde),
                        ),
                      ),
                      FractionallySizedBox(
                        widthFactor: valor.clamp(0.0, 1.0),
                        child: Container(
                          decoration: BoxDecoration(
                            color: alta
                                ? Paleta.acento
                                : Paleta.abstencion.withValues(alpha: 0.55),
                            borderRadius: BorderRadius.circular(5),
                          ),
                        ),
                      ),
                      if (corte != null)
                        Positioned(
                          left: (ancho * corte!.clamp(0.0, 1.0)) - 1,
                          top: -3,
                          bottom: -3,
                          child: Container(width: 2, color: Paleta.tinta),
                        ),
                    ],
                  ),
                );
              },
            ),
            if (corte != null)
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text(
                  'corte ${_fmt(corte!)}',
                  style: tema.textTheme.bodySmall,
                ),
              ),
          ],
        ),
      ),
    );
  }

  static String _fmt(double v) => v.toStringAsFixed(2).replaceAll('.', ',');
}
