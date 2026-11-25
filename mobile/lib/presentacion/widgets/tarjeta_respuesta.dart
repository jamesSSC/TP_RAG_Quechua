import 'package:flutter/material.dart';

import '../../dominio/entidades/fragmento_respaldo.dart';
import '../../dominio/entidades/respuesta.dart';
import '../../dominio/objetos_valor/modo_consulta.dart';
import '../tema.dart';
import 'barra_probabilidad.dart';

/// Muestra la respuesta con su cita visible y, plegado debajo, el respaldo completo.
///
/// La abstencion se presenta con el mismo peso visual que una respuesta, no como un error:
/// que el sistema diga "no hay respaldo" es el comportamiento correcto. Cada respuesta dice
/// de que modo vino (ADR-038).
class TarjetaRespuesta extends StatefulWidget {
  const TarjetaRespuesta({super.key, required this.respuesta});

  final Respuesta respuesta;

  @override
  State<TarjetaRespuesta> createState() => _TarjetaRespuestaState();
}

class _TarjetaRespuestaState extends State<TarjetaRespuesta> {
  bool _abierto = false;

  @override
  void didUpdateWidget(covariant TarjetaRespuesta anterior) {
    super.didUpdateWidget(anterior);
    if (anterior.respuesta.consultaId != widget.respuesta.consultaId) {
      _abierto = false;
    }
  }

  String get _titulo {
    final r = widget.respuesta;
    if (!r.abstenida) return 'Respuesta';
    return r.tienePasajes
        ? 'Sin respuesta confirmada'
        : 'Sin respaldo documental';
  }

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final r = widget.respuesta;

    return Semantics(
      liveRegion: true,
      container: true,
      // Flutter no pinta un borde redondeado con lados de distinto color: el marco va fuera
      // (uniforme y redondeado) y la franja de color, dentro y recortada.
      child: Container(
        key: const Key('tarjeta-respuesta'),
        width: double.infinity,
        decoration: BoxDecoration(
          color: r.abstenida ? Paleta.abstencionFondo : Paleta.blanco,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: Paleta.borde),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(9),
          child: Container(
            padding: const EdgeInsets.fromLTRB(16, 14, 16, 12),
            decoration: BoxDecoration(
              border: Border(
                left: BorderSide(
                  color: r.abstenida ? Paleta.abstencion : Paleta.acento,
                  width: 4,
                ),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _OrigenModo(modo: r.modo),
                if (r.avisoModo != null) ...[
                  const SizedBox(height: 6),
                  Text(r.avisoModo!, style: tema.textTheme.bodySmall),
                ],
                const SizedBox(height: 10),
                Text(
                  _titulo,
                  style: tema.textTheme.titleLarge?.copyWith(
                    color: r.abstenida ? Paleta.abstencion : Paleta.tinta,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  r.texto,
                  key: const Key('texto-respuesta'),
                  style: r.abstenida
                      ? tema.textTheme.bodyMedium
                      : tema.textTheme.bodyLarge,
                ),
                if (r.consultaTraducida != null) ...[
                  const SizedBox(height: 10),
                  Text(
                    'La consulta se tradujo al español para buscar en el corpus: '
                    '"${r.consultaTraducida}". El término en quechua se toma literal del '
                    'fragmento, sin traducir.',
                    style: tema.textTheme.bodySmall,
                  ),
                ],
                if (!r.abstenida && r.respaldo.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _Cita(fragmento: r.respaldo.first),
                ],
                if (r.abstencionPorPredictor) ...[
                  const SizedBox(height: 10),
                  Text(
                    'La similitud permitía responder, pero el modelo estimó una probabilidad de '
                    'respaldo por debajo del corte y el sistema se abstuvo (RN-06: el modelo '
                    'solo añade abstenciones).',
                    style: tema.textTheme.bodySmall?.copyWith(
                      color: Paleta.abstencion,
                    ),
                  ),
                ],
                if (r.tienePasajes) ...[
                  const SizedBox(height: 14),
                  const Divider(),
                  const SizedBox(height: 10),
                  Text(
                    'PASAJES RELACIONADOS — NO ES UNA RESPUESTA',
                    style: tema.textTheme.titleSmall,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'El sistema no afirma que respondan a la consulta: el material se entrega '
                    'literal y citado para que lo juzgue quien consulta.',
                    style: tema.textTheme.bodySmall,
                  ),
                  const SizedBox(height: 10),
                  ...r.pasajes.map((p) => _Pasaje(fragmento: p)),
                ],
                if (!r.abstenida && r.respaldo.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  const Divider(),
                  InkWell(
                    key: const Key('plegar-respaldo'),
                    onTap: () => setState(() => _abierto = !_abierto),
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(minHeight: 48),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              'FUENTE CONSULTADA · ${r.respaldo.length} '
                              '${r.respaldo.length == 1 ? 'FRAGMENTO' : 'FRAGMENTOS'}',
                              style: tema.textTheme.titleSmall,
                            ),
                          ),
                          Icon(
                            _abierto
                                ? Icons.keyboard_arrow_up
                                : Icons.keyboard_arrow_down,
                            color: Paleta.tintaSuave,
                          ),
                        ],
                      ),
                    ),
                  ),
                  if (_abierto)
                    ...r.respaldo.map((f) => _Fragmento(fragmento: f)),
                ],
                const SizedBox(height: 6),
                _Indicadores(respuesta: r),
                const SizedBox(height: 8),
                _BloquePrediccion(respuesta: r),
                if (r.aviso != null) ...[
                  const SizedBox(height: 8),
                  Text(r.aviso!, style: tema.textTheme.bodySmall),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _OrigenModo extends StatelessWidget {
  const _OrigenModo({required this.modo});

  final ModoConsulta modo;

  @override
  Widget build(BuildContext context) {
    final enLinea = modo == ModoConsulta.enLinea;
    return Row(
      key: Key('origen-${modo.codigo}'),
      children: [
        Icon(
          enLinea ? Icons.cloud_outlined : Icons.phone_android,
          size: 16,
          color: Paleta.tintaSuave,
        ),
        const SizedBox(width: 6),
        Flexible(
          child: Text(
            modo.origenRespuesta,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
      ],
    );
  }
}

class _Cita extends StatelessWidget {
  const _Cita({required this.fragmento});

  final FragmentoRespaldo fragmento;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Container(
      key: const Key('cita-principal'),
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Paleta.papel,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Paleta.borde),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Fuente', style: tema.textTheme.titleSmall),
          const SizedBox(height: 4),
          Text(
            '${fragmento.procedencia.documento} — página ${fragmento.procedencia.pagina}',
            style: tema.textTheme.bodyMedium?.copyWith(
              color: Paleta.acento,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

class _Fragmento extends StatelessWidget {
  const _Fragmento({required this.fragmento});

  final FragmentoRespaldo fragmento;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final f = fragmento;
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.only(left: 12),
            decoration: const BoxDecoration(
              border: Border(left: BorderSide(color: Paleta.borde, width: 3)),
            ),
            child: Text(f.texto, style: tema.textTheme.bodyMedium),
          ),
          const SizedBox(height: 4),
          Text(
            '${f.procedencia.documento} — página ${f.procedencia.pagina}',
            style: tema.textTheme.bodySmall?.copyWith(color: Paleta.acento),
          ),
          Text(
            'Similitud ${f.puntuacion.toStringAsFixed(3).replaceAll('.', ',')}'
            '${f.coincidenciaLema ? ' · entrada exacta del diccionario' : ''}',
            style: tema.textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}

class _Pasaje extends StatelessWidget {
  const _Pasaje({required this.fragmento});

  final FragmentoRespaldo fragmento;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.only(left: 12),
            decoration: const BoxDecoration(
              border: Border(
                left: BorderSide(color: Paleta.abstencion, width: 2),
              ),
            ),
            child: Text(fragmento.texto, style: tema.textTheme.bodyMedium),
          ),
          const SizedBox(height: 4),
          Padding(
            padding: const EdgeInsets.only(left: 12),
            child: Text(
              '${fragmento.procedencia.documento} — página ${fragmento.procedencia.pagina}',
              style: tema.textTheme.bodySmall?.copyWith(color: Paleta.acento),
            ),
          ),
        ],
      ),
    );
  }
}

class _Indicadores extends StatelessWidget {
  const _Indicadores({required this.respuesta});

  final Respuesta respuesta;

  @override
  Widget build(BuildContext context) {
    final r = respuesta;
    final tema = Theme.of(context);
    final tau = r.umbral;
    String? via;
    if (!r.abstenida && r.viaRespaldo == 'lema') {
      via =
          'Respaldo: entrada exacta del diccionario'
          '${tau == null ? '' : ' (la similitud queda bajo τ)'}';
    } else if (!r.abstenida && r.viaRespaldo == 'similitud') {
      via = 'Respaldo: similitud ≥ τ';
    }
    final partes = [
      'Similitud ${r.similitudMaxima.toStringAsFixed(3).replaceAll('.', ',')}',
      if (tau != null) 'τ = ${tau.toStringAsFixed(2).replaceAll('.', ',')}',
      if (r.latenciaMs != null) 'Latencia: ${r.latenciaMs!.round()} ms',
      if (r.redactadoPor != null) 'Redactado por: ${r.redactadoPor}',
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          partes.join(' · '),
          key: const Key('indicadores'),
          style: tema.textTheme.bodySmall,
        ),
        if (via != null) Text(via, style: tema.textTheme.bodySmall),
      ],
    );
  }
}

/// Bloque de prediccion ML (PMV2). En linea muestra las dos probabilidades; sin conexion
/// dice que el telefono no ejecuta los modelos, en lugar de ocultarlo.
class _BloquePrediccion extends StatelessWidget {
  const _BloquePrediccion({required this.respuesta});

  final Respuesta respuesta;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final r = respuesta;
    return Container(
      key: Key(r.tienePrediccion ? 'prediccion-ml' : 'prediccion-ml-ausente'),
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Paleta.papelHundido,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Predicción del modelo (aprendizaje automático)',
            style: tema.textTheme.titleSmall,
          ),
          const SizedBox(height: 8),
          if (!r.tienePrediccion)
            Text(
              r.modo == ModoConsulta.sinConexion
                  ? 'No disponible sin conexión: el teléfono no ejecuta los modelos. La '
                        'decisión se tomó solo con el umbral τ y la coincidencia de lema.'
                  : 'El servicio no devolvió predicciones para esta consulta.',
              style: tema.textTheme.bodySmall,
            )
          else ...[
            if (r.probabilidadCobertura != null)
              BarraProbabilidad(
                etiqueta: 'Predicción 1 · probabilidad de respaldo documental',
                valor: r.probabilidadCobertura!,
                corte: 0.25,
              ),
            if (r.probabilidadPasajes != null)
              BarraProbabilidad(
                etiqueta:
                    'Predicción 2 · probabilidad de que los pasajes traten la pregunta',
                valor: r.probabilidadPasajes!,
                corte: 0.5,
              ),
          ],
        ],
      ),
    );
  }
}
