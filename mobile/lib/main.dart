import 'package:flutter/material.dart';

import 'infraestructura/contenedor.dart';
import 'presentacion/pantalla_principal.dart';
import 'presentacion/tema.dart';

void main() {
  runApp(const AplicacionQuechuaWanka());
}

class AplicacionQuechuaWanka extends StatefulWidget {
  const AplicacionQuechuaWanka({super.key});

  @override
  State<AplicacionQuechuaWanka> createState() => _AplicacionQuechuaWankaState();
}

class _AplicacionQuechuaWankaState extends State<AplicacionQuechuaWanka> {
  /// El indice son 12 MB que hay que leer y estructurar una sola vez al arrancar. Se hace
  /// aqui, y no en cada consulta, para que consultar sin conexion sea inmediato.
  late final Future<(Contenedor, int)> _arranque = () async {
    final contenedor = await Contenedor.cargar();
    final tamano = await contenedor.preferencias.tamanoTexto();
    return (contenedor, tamano);
  }();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Quechua Wanka',
      debugShowCheckedModeBanner: false,
      theme: Tema.claro(),
      home: FutureBuilder<(Contenedor, int)>(
        future: _arranque,
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return _Arranque(
              mensaje: 'No se pudo abrir el corpus.\n${snapshot.error}',
            );
          }
          final datos = snapshot.data;
          if (datos == null) {
            return const _Arranque(mensaje: 'Abriendo el corpus…');
          }
          final (contenedor, tamano) = datos;
          return PantallaPrincipal(
            asistente: contenedor.asistente,
            modo: contenedor.asistente,
            preferencias: contenedor.preferencias,
            tamanoInicial: tamano,
          );
        },
      ),
    );
  }
}

/// Pantalla de los pocos instantes que tarda el indice en quedar disponible.
class _Arranque extends StatelessWidget {
  const _Arranque({required this.mensaje});

  final String mensaje;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Image.asset(
                'assets/marca/logo_icono_1024.png',
                width: 96,
                height: 96,
              ),
              const SizedBox(height: 16),
              Text('Quechua wanka', style: tema.textTheme.headlineSmall),
              const SizedBox(height: 10),
              Text(
                mensaje,
                textAlign: TextAlign.center,
                style: tema.textTheme.bodyMedium,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
