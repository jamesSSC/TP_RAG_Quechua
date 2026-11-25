import 'package:flutter/material.dart';

import '../../dominio/entidades/entrada_historial.dart';
import '../../dominio/objetos_valor/modo_consulta.dart';
import '../tema.dart';

/// Consultas anteriores de este teléfono. Se puede volver a cualquiera con un toque.
class ListaHistorial extends StatelessWidget {
  const ListaHistorial({
    super.key,
    required this.entradas,
    required this.onRepetir,
  });

  final List<EntradaHistorial> entradas;
  final ValueChanged<String> onRepetir;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Historial de consultas', style: tema.textTheme.titleMedium),
        const SizedBox(height: 4),
        Text(
          'No se guardan datos personales: las consultas se almacenan solo en este teléfono.',
          style: tema.textTheme.bodySmall,
        ),
        const SizedBox(height: 6),
        if (entradas.isEmpty)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Text(
              'Todavía no hay consultas.',
              style: tema.textTheme.bodySmall,
            ),
          ),
        ...entradas.map(
          (e) => InkWell(
            onTap: () => onRepetir(e.consulta),
            child: ConstrainedBox(
              constraints: const BoxConstraints(minHeight: 48),
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Row(
                  children: [
                    Icon(
                      e.modo == ModoConsulta.enLinea
                          ? Icons.cloud_outlined
                          : Icons.phone_android,
                      size: 16,
                      color: Paleta.tintaSuave,
                      semanticLabel: e.modo.origenRespuesta,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        e.consulta,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: tema.textTheme.bodyMedium,
                      ),
                    ),
                    Text(
                      e.abstenida ? 'sin respaldo' : 'con respaldo',
                      style: tema.textTheme.bodySmall?.copyWith(
                        color: e.abstenida ? Paleta.abstencion : Paleta.acento,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
