import 'package:flutter/material.dart';

/// Paleta de la web (`frontend/src/index.css`), para que la app y la web se vean iguales.
class Paleta {
  static const Color papel = Color(0xFFFAF7F2);
  static const Color papelHundido = Color(0xFFF0EBE2);
  static const Color borde = Color(0xFFDED5C7);
  static const Color acento = Color(0xFF8A5A2B);
  static const Color acentoClaro = Color(0xFFF5EDE2);
  static const Color abstencion = Color(0xFF86581A);
  static const Color abstencionFondo = Color(0xFFFDF6E6);
  static const Color tinta = Color(0xFF1C1A17);
  static const Color tintaSuave = Color(0xFF5D574F);
  static const Color error = Color(0xFFA1301F);
  static const Color blanco = Color(0xFFFFFFFF);
}

/// Tema sobrio: la aplicacion consulta fuentes documentales y la interfaz no debe competir
/// con el contenido que cita. Botones de al menos 48 px de alto (HU-11, WCAG 2.5.5).
class Tema {
  /// Factores de A−, A, A+ y A++, los mismos que la web (0,9 · 1 · 1,15 · 1,35 rem).
  static const List<double> escalas = [0.9, 1.0, 1.15, 1.35];
  static const int escalaNormal = 1;

  static ThemeData claro() {
    final esquema =
        ColorScheme.fromSeed(
          seedColor: Paleta.acento,
          brightness: Brightness.light,
        ).copyWith(
          primary: Paleta.acento,
          onPrimary: Paleta.papel,
          surface: Paleta.papel,
          onSurface: Paleta.tinta,
          onSurfaceVariant: Paleta.tintaSuave,
          surfaceContainerHighest: Paleta.papelHundido,
          outline: Paleta.borde,
          error: Paleta.error,
        );

    return ThemeData(
      useMaterial3: true,
      colorScheme: esquema,
      scaffoldBackgroundColor: Paleta.papel,
      textTheme: _tipografia(),
      materialTapTargetSize: MaterialTapTargetSize.padded,
      appBarTheme: const AppBarTheme(
        backgroundColor: Paleta.papel,
        foregroundColor: Paleta.tinta,
        elevation: 0,
        scrolledUnderElevation: 0,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: Paleta.papel,
        indicatorColor: Paleta.acentoClaro,
        height: 68,
        labelTextStyle: WidgetStateProperty.resolveWith(
          (estados) => TextStyle(
            fontSize: 13,
            fontWeight: estados.contains(WidgetState.selected)
                ? FontWeight.w600
                : FontWeight.w400,
            color: estados.contains(WidgetState.selected)
                ? Paleta.acento
                : Paleta.tintaSuave,
          ),
        ),
        iconTheme: WidgetStateProperty.resolveWith(
          (estados) => IconThemeData(
            color: estados.contains(WidgetState.selected)
                ? Paleta.acento
                : Paleta.tintaSuave,
          ),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: Paleta.acento,
          foregroundColor: Paleta.papel,
          minimumSize: const Size(48, 52),
          textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: Paleta.tinta,
          minimumSize: const Size(48, 48),
          side: const BorderSide(color: Paleta.borde),
          backgroundColor: Paleta.papelHundido,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Paleta.blanco,
        hintStyle: const TextStyle(color: Paleta.tintaSuave),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 16,
        ),
        border: _borde(false),
        enabledBorder: _borde(false),
        focusedBorder: _borde(true),
      ),
      dividerTheme: const DividerThemeData(
        color: Paleta.borde,
        space: 1,
        thickness: 1,
      ),
    );
  }

  static OutlineInputBorder _borde(bool enfocado) => OutlineInputBorder(
    borderRadius: BorderRadius.circular(8),
    borderSide: BorderSide(
      color: enfocado ? Paleta.acento : Paleta.borde,
      width: enfocado ? 1.6 : 1,
    ),
  );

  static TextTheme _tipografia() => const TextTheme(
    headlineSmall: TextStyle(
      fontSize: 22,
      fontWeight: FontWeight.w700,
      letterSpacing: -0.3,
      color: Paleta.tinta,
    ),
    titleLarge: TextStyle(
      fontSize: 19,
      fontWeight: FontWeight.w700,
      color: Paleta.tinta,
    ),
    titleMedium: TextStyle(
      fontSize: 16,
      fontWeight: FontWeight.w600,
      color: Paleta.tinta,
    ),
    titleSmall: TextStyle(
      fontSize: 13,
      fontWeight: FontWeight.w600,
      letterSpacing: 0.4,
      color: Paleta.tintaSuave,
    ),
    bodyLarge: TextStyle(fontSize: 17, height: 1.5, color: Paleta.tinta),
    bodyMedium: TextStyle(fontSize: 15, height: 1.45, color: Paleta.tinta),
    bodySmall: TextStyle(fontSize: 13, height: 1.4, color: Paleta.tintaSuave),
    labelLarge: TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
  );
}
