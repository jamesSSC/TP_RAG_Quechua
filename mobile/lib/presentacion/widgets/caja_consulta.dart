import 'package:flutter/material.dart';

import '../tema.dart';

/// Campo de consulta. Acepta español o inglés sin que el usuario elija idioma: el idioma se
/// detecta y, si hace falta, el término se traduce antes de buscar. Mismos límites (1 a 300
/// caracteres) y mismos ejemplos que la web.
class CajaConsulta extends StatelessWidget {
  const CajaConsulta({
    super.key,
    required this.controlador,
    required this.cargando,
    required this.onEnviar,
  });

  static const int maximo = 300;
  static const List<String> ejemplos = ['perro', 'agua', 'zorro', 'casa'];

  final TextEditingController controlador;
  final bool cargando;
  final ValueChanged<String> onEnviar;

  void _enviar() {
    final texto = controlador.text.trim();
    if (texto.isNotEmpty && !cargando) onEnviar(texto);
  }

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Paleta.papelHundido,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Paleta.borde),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Escriba su consulta en español o inglés',
            style: tema.textTheme.titleMedium,
          ),
          const SizedBox(height: 10),
          TextField(
            key: const Key('campo-consulta'),
            controller: controlador,
            enabled: !cargando,
            maxLength: maximo,
            textInputAction: TextInputAction.search,
            onSubmitted: (_) => _enviar(),
            style: tema.textTheme.bodyLarge,
            decoration: const InputDecoration(
              hintText: '¿cómo se dice zorro en quechua wanka?',
            ),
            buildCounter:
                (
                  context, {
                  required currentLength,
                  required isFocused,
                  required maxLength,
                }) => Text(
                  '$currentLength / $maxLength caracteres',
                  style: tema.textTheme.bodySmall,
                ),
          ),
          const SizedBox(height: 6),
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              key: const Key('boton-consultar'),
              onPressed: cargando ? null : _enviar,
              child: cargando
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Paleta.papel,
                      ),
                    )
                  : const Text('Consultar'),
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              Text('Ejemplos:', style: tema.textTheme.bodySmall),
              for (final ejemplo in ejemplos)
                ActionChip(
                  label: Text(ejemplo),
                  backgroundColor: Paleta.blanco,
                  side: const BorderSide(color: Paleta.borde),
                  shape: const StadiumBorder(),
                  onPressed: cargando
                      ? null
                      : () {
                          controlador.text = ejemplo;
                          onEnviar(ejemplo);
                        },
                ),
            ],
          ),
        ],
      ),
    );
  }
}
