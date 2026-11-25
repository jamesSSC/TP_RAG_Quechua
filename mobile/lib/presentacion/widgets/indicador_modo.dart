import 'package:flutter/material.dart';

import '../../dominio/objetos_valor/modo_consulta.dart';
import '../../dominio/puertos/modo_port.dart';
import '../tema.dart';

/// Indicador permanente del modo activo («En línea · nube» o «Sin conexión · corpus local»).
/// Al tocarlo se abre el selector manual.
class IndicadorModo extends StatelessWidget {
  const IndicadorModo({
    super.key,
    required this.modo,
    this.comprobando = false,
  });

  final ModoPort modo;

  /// Verdadero mientras se averigua si la nube responde (arranque en frio de Render).
  final bool comprobando;

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<PreferenciaModo>(
      valueListenable: modo.preferencia,
      builder: (context, preferencia, _) =>
          ValueListenableBuilder<ModoConsulta>(
            valueListenable: modo.modoActivo,
            builder: (context, activo, _) {
              final enLinea = activo == ModoConsulta.enLinea;
              final rotulo = comprobando && enLinea
                  ? 'En línea · nube (conectando…)'
                  : activo.rotulo;
              return Semantics(
                button: true,
                label:
                    'Modo activo: $rotulo. Preferencia: ${preferencia.rotulo}. '
                    'Toca para cambiar de modo.',
                excludeSemantics: true,
                child: Material(
                  color: enLinea ? Paleta.acentoClaro : Paleta.papelHundido,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(999),
                    side: BorderSide(
                      color: enLinea ? Paleta.acento : Paleta.borde,
                    ),
                  ),
                  child: InkWell(
                    key: const Key('indicador-modo'),
                    borderRadius: BorderRadius.circular(999),
                    onTap: () => _abrirSelector(context, preferencia),
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(minHeight: 44),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 14,
                          vertical: 8,
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              enLinea
                                  ? Icons.cloud_outlined
                                  : Icons.phone_android,
                              size: 18,
                              color: enLinea
                                  ? Paleta.acento
                                  : Paleta.tintaSuave,
                            ),
                            const SizedBox(width: 8),
                            Flexible(
                              child: Text(
                                rotulo,
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: enLinea ? Paleta.acento : Paleta.tinta,
                                ),
                              ),
                            ),
                            if (preferencia != PreferenciaModo.automatico) ...[
                              const SizedBox(width: 6),
                              Text(
                                '· manual',
                                style: const TextStyle(
                                  fontSize: 13,
                                  color: Paleta.tintaSuave,
                                ),
                              ),
                            ],
                            const SizedBox(width: 4),
                            const Icon(
                              Icons.expand_more,
                              size: 18,
                              color: Paleta.tintaSuave,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
    );
  }

  Future<void> _abrirSelector(
    BuildContext context,
    PreferenciaModo actual,
  ) async {
    final elegida = await showModalBottomSheet<PreferenciaModo>(
      context: context,
      backgroundColor: Paleta.papel,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (context) => SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.zero,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Modo de consulta',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 4),
                Text(
                  'En línea, la consulta se envía a la nube. Sin conexión, se resuelve en el '
                  'teléfono con el corpus incorporado y nada sale del dispositivo.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 12),
                RadioGroup<PreferenciaModo>(
                  groupValue: actual,
                  onChanged: (p) => Navigator.of(context).pop(p),
                  child: Column(
                    children: [
                      for (final p in PreferenciaModo.values)
                        RadioListTile<PreferenciaModo>(
                          key: Key('preferencia-${p.name}'),
                          value: p,
                          contentPadding: EdgeInsets.zero,
                          title: Text(p.rotulo),
                          subtitle: Text(p.descripcion),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
    if (elegida != null) modo.cambiarPreferencia(elegida);
  }
}
