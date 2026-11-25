import 'dart:convert';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/services.dart' show rootBundle;

import '../../../aplicacion/servicios/depurador_consulta.dart';
import '../../../dominio/entidades/fragmento_respaldo.dart';
import '../../../dominio/entidades/procedencia.dart';

const carpetaIndice = 'assets/indice';

/// Puntuador TF-IDF que reproduce el del escritorio sin reimplementar el ajuste.
///
/// El indice no se construye aqui: Python exporta el vocabulario, los pesos IDF y la
/// matriz ya ajustada, y este motor solo ejecuta el producto punto. Por eso el umbral
/// calibrado en el escritorio sigue siendo valido sin recalibrar. Validado en
/// scripts/validar_indice_movil.py: sobre las 248 consultas del conjunto de evaluacion la
/// diferencia maxima frente a scikit-learn es 2,5e-08, que es el redondeo de float32, y no
/// hay ningun desajuste en el top-5.
///
/// La matriz llega en orden por columnas, es decir como indice invertido: se recorren solo
/// los terminos presentes en la consulta y no los 3605 fragmentos.
class IndicePortable {
  IndicePortable._({
    required this.fragmentos,
    required this.umbralAbstencion,
    required this._depurador,
    required this._palabras,
    required this._caracteres,
    required this._lemario,
  });

  final List<FragmentoIndexado> fragmentos;
  final double umbralAbstencion;
  final DepuradorConsulta _depurador;
  final Campo _palabras;
  final Campo _caracteres;
  final Map<String, List<int>> _lemario;

  DepuradorConsulta get depurador => _depurador;

  static Future<IndicePortable> cargar() async {
    final manifiesto =
        jsonDecode(
              await rootBundle.loadString('$carpetaIndice/manifiesto.json'),
            )
            as Map<String, dynamic>;

    final crudos =
        jsonDecode(
              await rootBundle.loadString('$carpetaIndice/fragmentos.json'),
            )
            as List<dynamic>;
    final fragmentos = crudos
        .cast<Map<String, dynamic>>()
        .map(FragmentoIndexado.desdeJson)
        .toList(growable: false);

    final lemarioCrudo =
        jsonDecode(await rootBundle.loadString('$carpetaIndice/lemario.json'))
            as Map<String, dynamic>;

    return IndicePortable._(
      fragmentos: fragmentos,
      umbralAbstencion: (manifiesto['umbral_abstencion'] as num).toDouble(),
      depurador: DepuradorConsulta(
        (manifiesto['plantillas_depuracion'] as List<dynamic>).cast<String>(),
      ),
      palabras: await Campo.cargar('palabras', manifiesto, fragmentos.length),
      caracteres: await Campo.cargar(
        'caracteres',
        manifiesto,
        fragmentos.length,
      ),
      lemario: {
        for (final entrada in lemarioCrudo.entries)
          entrada.key: (entrada.value as List<dynamic>).cast<int>(),
      },
    );
  }

  /// Puntuacion de la consulta frente a todo el indice, en el orden de [fragmentos].
  Float64List puntuar(String consulta) {
    final depurada = _depurador.depurar(consulta);
    final porPalabras = _palabras.similitudes(tokensPalabra(depurada));
    final porCaracteres = _caracteres.similitudes(tokensCaracter(depurada));

    final salida = Float64List(fragmentos.length);
    for (var i = 0; i < salida.length; i++) {
      final media = (porPalabras[i] + porCaracteres[i]) / 2.0;
      salida[i] = media.clamp(0.0, 1.0);
    }
    return salida;
  }

  List<FragmentoRespaldo> recuperar(String consulta, {int k = 5}) {
    final puntuaciones = puntuar(consulta);
    final orden = List<int>.generate(fragmentos.length, (i) => i)
      ..sort((a, b) => puntuaciones[b].compareTo(puntuaciones[a]));

    final porLema = _lemario[_depurador.depurar(consulta)] ?? const <int>[];
    // Las entradas cuyo lema coincide encabezan el resultado aunque su similitud quede por
    // debajo del umbral: un termino frecuente en el corpus recibe un IDF bajo y su propia
    // entrada de diccionario puede no alcanzarlo (caso medido: "perro", 0,271).
    final elegidos = <int>[...porLema];
    for (final i in orden) {
      if (elegidos.length >= k) break;
      if (!elegidos.contains(i)) elegidos.add(i);
    }

    return [
      for (final i in elegidos.take(k))
        fragmentos[i].aRespaldo(puntuaciones[i], porLema.contains(i)),
    ];
  }

  /// Los k pasajes de prosa mas similares, al margen de las entradas de diccionario, que
  /// por ser mucho mas cortas copan siempre las primeras posiciones.
  List<FragmentoRespaldo> recuperarProsa(String consulta, {int k = 3}) {
    final puntuaciones = puntuar(consulta);
    final prosa = [
      for (var i = 0; i < fragmentos.length; i++)
        if (!fragmentos[i].esLexicografico) i,
    ]..sort((a, b) => puntuaciones[b].compareTo(puntuaciones[a]));

    return [
      for (final i in prosa.take(k))
        fragmentos[i].aRespaldo(puntuaciones[i], false),
    ];
  }

  bool esLema(String termino) =>
      _lemario.containsKey(_depurador.depurar(termino));

  static final _patronToken = RegExp(r'[\p{L}\p{N}_]+', unicode: true);
  static final _espaciosMultiples = RegExp(r'\s\s+');

  static List<String> tokensPalabra(String texto) =>
      _patronToken.allMatches(texto.toLowerCase()).map((m) => m[0]!).toList();

  /// Reproduce el analizador `char_wb` de scikit-learn: cada palabra se rodea de espacios y
  /// se extraen sus n-gramas de 3 a 5; una palabra mas corta que n se cuenta una sola vez.
  static List<String> tokensCaracter(
    String texto, {
    int nMin = 3,
    int nMax = 5,
  }) {
    final limpio = texto.toLowerCase().replaceAll(_espaciosMultiples, ' ');
    final salida = <String>[];
    for (final palabra in limpio.split(' ')) {
      if (palabra.isEmpty) continue;
      final w = ' $palabra ';
      final largo = w.length;
      for (var n = nMin; n <= nMax; n++) {
        var desplazamiento = 0;
        salida.add(w.substring(0, math.min(n, largo)));
        while (desplazamiento + n < largo) {
          desplazamiento++;
          salida.add(
            w.substring(desplazamiento, math.min(desplazamiento + n, largo)),
          );
        }
        if (desplazamiento == 0) break;
      }
    }
    return salida;
  }
}

/// Uno de los dos espacios TF-IDF: palabras o n-gramas de caracteres.
class Campo {
  Campo({
    required this.vocabulario,
    required this.idf,
    required this.indptr,
    required this.indices,
    required this.datos,
    required this.filas,
  });

  final Map<String, int> vocabulario;
  final Float32List idf;
  final Uint32List indptr;
  final Uint32List indices;
  final Float32List datos;
  final int filas;

  static Future<Campo> cargar(
    String nombre,
    Map<String, dynamic> manifiesto,
    int filas,
  ) async {
    final terminos =
        (jsonDecode(
                  await rootBundle.loadString(
                    '$carpetaIndice/vocab_$nombre.json',
                  ),
                )
                as List<dynamic>)
            .cast<String>();

    final idfCrudo = await rootBundle.load('$carpetaIndice/idf_$nombre.bin');
    final meta = manifiesto['matriz_$nombre'] as Map<String, dynamic>;
    final matriz = await rootBundle.load('$carpetaIndice/${meta['archivo']}');

    final columnas = meta['columnas'] as int;
    final nnz = meta['nnz'] as int;
    final corte1 = (columnas + 1) * 4;
    final corte2 = corte1 + nnz * 4;

    return Campo(
      vocabulario: {for (var i = 0; i < terminos.length; i++) terminos[i]: i},
      idf: idfCrudo.buffer.asFloat32List(
        idfCrudo.offsetInBytes,
        terminos.length,
      ),
      indptr: matriz.buffer.asUint32List(matriz.offsetInBytes, columnas + 1),
      indices: matriz.buffer.asUint32List(matriz.offsetInBytes + corte1, nnz),
      datos: matriz.buffer.asFloat32List(matriz.offsetInBytes + corte2, nnz),
      filas: filas,
    );
  }

  /// Producto punto de la consulta contra el indice invertido.
  ///
  /// La consulta se pesa con el mismo IDF y se normaliza en L2, igual que hace
  /// TfidfVectorizer, de modo que el producto punto es el coseno.
  Float64List similitudes(List<String> tokens) {
    final conteo = <String, int>{};
    for (final token in tokens) {
      conteo[token] = (conteo[token] ?? 0) + 1;
    }

    final pesos = <int, double>{};
    for (final entrada in conteo.entries) {
      final columna = vocabulario[entrada.key];
      if (columna != null) {
        pesos[columna] = entrada.value * idf[columna];
      }
    }

    final acumulado = Float64List(filas);
    if (pesos.isEmpty) return acumulado;

    var suma = 0.0;
    for (final peso in pesos.values) {
      suma += peso * peso;
    }
    final norma = math.sqrt(suma);
    if (norma == 0.0) return acumulado;

    for (final entrada in pesos.entries) {
      final columna = entrada.key;
      final peso = entrada.value / norma;
      for (var i = indptr[columna]; i < indptr[columna + 1]; i++) {
        acumulado[indices[i]] += datos[i] * peso;
      }
    }
    return acumulado;
  }
}

/// Fragmento tal como viaja en el indice exportado.
class FragmentoIndexado {
  const FragmentoIndexado({
    required this.id,
    required this.texto,
    required this.documento,
    required this.pagina,
    required this.esLexicografico,
  });

  factory FragmentoIndexado.desdeJson(Map<String, dynamic> json) =>
      FragmentoIndexado(
        id: json['id'] as String,
        texto: json['t'] as String,
        documento: json['d'] as String,
        pagina: json['p'] as int,
        esLexicografico: (json['x'] as int) == 1,
      );

  final String id;
  final String texto;
  final String documento;
  final int pagina;
  final bool esLexicografico;

  FragmentoRespaldo aRespaldo(double puntuacion, bool coincidenciaLema) =>
      FragmentoRespaldo(
        id: id,
        texto: texto,
        procedencia: Procedencia(documento: documento, pagina: pagina),
        puntuacion: puntuacion,
        coincidenciaLema: coincidenciaLema,
      );
}
