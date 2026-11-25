import 'package:flutter/material.dart';

import '../dominio/puertos/asistente_port.dart';
import '../dominio/puertos/modo_port.dart';
import '../dominio/puertos/preferencias_port.dart';
import 'tema.dart';
import 'vistas/vista_consulta.dart';
import 'vistas/vista_fuentes.dart';
import 'vistas/vista_prediccion.dart';
import 'widgets/indicador_modo.dart';
import 'widgets/tamano_texto.dart';

/// Estructura de la app: cabecera con logo, tamaño de letra e indicador de modo, y tres
/// pestañas (Consultar, Fuentes, Predicción ML). No hay pestañas de administración: incorporar
/// documentos o borrar el historial del servidor queda en la web (ADR-038).
class PantallaPrincipal extends StatefulWidget {
  const PantallaPrincipal({
    super.key,
    required this.asistente,
    required this.modo,
    required this.preferencias,
    this.tamanoInicial = Tema.escalaNormal,
    this.avisoEspera = const Duration(milliseconds: 4000),
  });

  final AsistentePort asistente;
  final ModoPort modo;
  final PreferenciasPort preferencias;
  final int tamanoInicial;
  final Duration avisoEspera;

  @override
  State<PantallaPrincipal> createState() => _PantallaPrincipalState();
}

class _PantallaPrincipalState extends State<PantallaPrincipal> {
  int _pestana = 0;
  late int _tamano = widget.tamanoInicial;
  EstadoSistema? _estado;
  bool _comprobando = true;

  @override
  void initState() {
    super.initState();
    widget.modo.preferencia.addListener(_alCambiarPreferencia);
    _cargarEstado();
  }

  @override
  void dispose() {
    widget.modo.preferencia.removeListener(_alCambiarPreferencia);
    super.dispose();
  }

  void _alCambiarPreferencia() {
    widget.preferencias.guardarModo(widget.modo.preferencia.value);
    _cargarEstado();
  }

  /// Pedir el estado al arrancar despierta la nube si estaba dormida, como hace la web.
  Future<void> _cargarEstado() async {
    setState(() => _comprobando = true);
    try {
      final estado = await widget.asistente.estado();
      if (mounted) setState(() => _estado = estado);
    } catch (_) {
      if (mounted) setState(() => _estado = null);
    } finally {
      if (mounted) setState(() => _comprobando = false);
    }
  }

  void _cambiarTamano(int indice) {
    final acotado = indice.clamp(0, Tema.escalas.length - 1);
    setState(() => _tamano = acotado);
    widget.preferencias.guardarTamanoTexto(acotado);
  }

  String get _subtitulo {
    final e = _estado;
    if (e == null) {
      return _comprobando
          ? 'Conectando…'
          : 'Consulta sobre el corpus documental publicado';
    }
    final docs = e.documentos == null ? '' : ' · ${e.documentos} documentos';
    return '${_miles(e.fragmentosIndexados)} fragmentos$docs · umbral '
        '${e.umbralAbstencion.toStringAsFixed(2).replaceAll('.', ',')}';
  }

  static String _miles(int n) => n.toString().replaceAllMapped(
    RegExp(r'(\d)(?=(\d{3})+$)'),
    (m) => '${m[1]} ',
  );

  @override
  Widget build(BuildContext context) {
    final sistema = MediaQuery.textScalerOf(context);
    final escala = TextScaler.linear(sistema.scale(1) * Tema.escalas[_tamano]);
    final tema = Theme.of(context);

    return MediaQuery(
      data: MediaQuery.of(context).copyWith(textScaler: escala),
      child: Scaffold(
        body: SafeArea(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Image.asset(
                          'assets/marca/logo_contorno_1024.png',
                          key: const Key('logo'),
                          width: 44,
                          height: 44,
                          semanticLabel:
                              'Logo del asistente de consulta del quechua wanka',
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Quechua wanka',
                                style: tema.textTheme.headlineSmall,
                              ),
                              Text(
                                _subtitulo,
                                key: const Key('subtitulo-estado'),
                                style: tema.textTheme.bodySmall,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: Align(
                            alignment: Alignment.centerLeft,
                            child: IndicadorModo(
                              modo: widget.modo,
                              comprobando: _comprobando,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        TamanoTexto(indice: _tamano, onCambiar: _cambiarTamano),
                      ],
                    ),
                  ],
                ),
              ),
              const Divider(),
              Expanded(
                child: IndexedStack(
                  index: _pestana,
                  children: [
                    VistaConsulta(
                      asistente: widget.asistente,
                      modo: widget.modo,
                      avisoEspera: widget.avisoEspera,
                    ),
                    // Las otras pestañas se construyen al abrirlas, para no gastar
                    // peticiones a la nube que nadie pidió.
                    _pestana == 1
                        ? VistaFuentes(
                            asistente: widget.asistente,
                            modo: widget.modo,
                          )
                        : const SizedBox.shrink(),
                    VistaPrediccion(asistente: widget.asistente),
                  ],
                ),
              ),
            ],
          ),
        ),
        bottomNavigationBar: NavigationBar(
          selectedIndex: _pestana,
          onDestinationSelected: (i) => setState(() => _pestana = i),
          destinations: const [
            NavigationDestination(
              key: Key('pestana-consultar'),
              icon: Icon(Icons.search),
              label: 'Consultar',
            ),
            NavigationDestination(
              key: Key('pestana-fuentes'),
              icon: Icon(Icons.menu_book_outlined),
              label: 'Fuentes',
            ),
            NavigationDestination(
              key: Key('pestana-prediccion'),
              icon: Icon(Icons.insights_outlined),
              label: 'Predicción ML',
            ),
          ],
        ),
      ),
    );
  }
}
