import 'package:flutter/material.dart';

import '../../dominio/entidades/fuente.dart';
import '../../dominio/objetos_valor/modo_consulta.dart';
import '../../dominio/puertos/asistente_port.dart';
import '../../dominio/puertos/modo_port.dart';
import '../tema.dart';

/// Fuentes del corpus (HU-01), en solo lectura. La gestión (incorporar, editar, borrar) queda
/// en la web con el token de administración: la app no lo lleva (ADR-038).
class VistaFuentes extends StatefulWidget {
  const VistaFuentes({super.key, required this.asistente, required this.modo});

  final AsistentePort asistente;
  final ModoPort modo;

  @override
  State<VistaFuentes> createState() => _VistaFuentesState();
}

class _VistaFuentesState extends State<VistaFuentes> {
  late Future<List<Fuente>> _fuentes = widget.asistente.fuentes();

  void _recargar() => setState(() => _fuentes = widget.asistente.fuentes());

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return RefreshIndicator(
      onRefresh: () async => _recargar(),
      child: FutureBuilder<List<Fuente>>(
        future: _fuentes,
        builder: (context, snapshot) {
          final cargando = snapshot.connectionState != ConnectionState.done;
          final fuentes = snapshot.data ?? const <Fuente>[];
          final sinConexion =
              widget.modo.modoActivo.value == ModoConsulta.sinConexion;
          return ListView(
            key: const Key('vista-fuentes'),
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
            children: [
              Text('Fuentes del corpus', style: tema.textTheme.titleLarge),
              const SizedBox(height: 4),
              Text(
                'Documentos publicados de los que salen todas las respuestas. La gestión de '
                'fuentes solo está disponible en la web, para el administrador.',
                style: tema.textTheme.bodySmall,
              ),
              const SizedBox(height: 12),
              if (cargando)
                const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (snapshot.hasError)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('${snapshot.error}', style: tema.textTheme.bodyMedium),
                    const SizedBox(height: 8),
                    OutlinedButton(
                      onPressed: _recargar,
                      child: const Text('Reintentar'),
                    ),
                  ],
                )
              else ...[
                if (sinConexion)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: Text(
                      'Sin conexión: se listan los documentos del corpus incorporado en el '
                      'teléfono. La entidad publicadora y la licencia se consultan en línea.',
                      style: tema.textTheme.bodySmall?.copyWith(
                        color: Paleta.abstencion,
                      ),
                    ),
                  ),
                Text(
                  '${fuentes.length} documentos',
                  style: tema.textTheme.titleSmall,
                ),
                const SizedBox(height: 8),
                ...fuentes.map((f) => _TarjetaFuente(fuente: f)),
              ],
            ],
          );
        },
      ),
    );
  }
}

class _TarjetaFuente extends StatelessWidget {
  const _TarjetaFuente({required this.fuente});

  final Fuente fuente;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final f = fuente;
    final detalles = [
      if (f.entidadPublicadora != null) f.entidadPublicadora!,
      if (f.paginasTotales != null) '${f.paginasTotales} páginas',
      if (f.fragmentos != null) '${f.fragmentos} fragmentos',
    ];
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Paleta.blanco,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Paleta.borde),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(f.nombreVisible, style: tema.textTheme.titleMedium),
          const SizedBox(height: 4),
          Text(f.nombreArchivo, style: tema.textTheme.bodySmall),
          if (detalles.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(detalles.join(' · '), style: tema.textTheme.bodySmall),
          ],
          if (f.licenciamiento != null) ...[
            const SizedBox(height: 4),
            Text(
              'Licencia: ${f.licenciamiento}',
              style: tema.textTheme.bodySmall,
            ),
          ],
        ],
      ),
    );
  }
}
