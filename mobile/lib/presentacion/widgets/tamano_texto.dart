import 'package:flutter/material.dart';

import '../tema.dart';

/// Botones A−, A y A+ para el tamaño de letra, como en la web.
class TamanoTexto extends StatelessWidget {
  const TamanoTexto({super.key, required this.indice, required this.onCambiar});

  final int indice;
  final ValueChanged<int> onCambiar;

  @override
  Widget build(BuildContext context) {
    final maximo = Tema.escalas.length - 1;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _Boton(
          clave: 'tamano-menos',
          texto: 'A−',
          etiqueta: 'Reducir tamaño del texto',
          activo: indice > 0,
          onTap: () => onCambiar(indice - 1),
        ),
        const SizedBox(width: 6),
        _Boton(
          clave: 'tamano-normal',
          texto: 'A',
          etiqueta: 'Restablecer tamaño del texto',
          activo: indice != Tema.escalaNormal,
          onTap: () => onCambiar(Tema.escalaNormal),
        ),
        const SizedBox(width: 6),
        _Boton(
          clave: 'tamano-mas',
          texto: 'A+',
          etiqueta: 'Aumentar tamaño del texto',
          activo: indice < maximo,
          onTap: () => onCambiar(indice + 1),
        ),
      ],
    );
  }
}

class _Boton extends StatelessWidget {
  const _Boton({
    required this.clave,
    required this.texto,
    required this.etiqueta,
    required this.activo,
    required this.onTap,
  });

  final String clave;
  final String texto;
  final String etiqueta;
  final bool activo;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      enabled: activo,
      label: etiqueta,
      excludeSemantics: true,
      child: SizedBox(
        width: 48,
        height: 48,
        child: Material(
          color: Paleta.papelHundido,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: const BorderSide(color: Paleta.borde),
          ),
          child: InkWell(
            key: Key(clave),
            borderRadius: BorderRadius.circular(8),
            onTap: activo ? onTap : null,
            child: Center(
              // El rotulo no escala con el texto: es el mando que lo cambia.
              child: MediaQuery.withNoTextScaling(
                child: Text(
                  texto,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: activo
                        ? Paleta.tinta
                        : Paleta.tintaSuave.withValues(alpha: 0.6),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
