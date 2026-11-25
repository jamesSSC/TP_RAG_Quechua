import 'dart:async';
import 'dart:convert';
import 'dart:io' show SocketException, HandshakeException;

import 'package:http/http.dart' as http;

import '../../../dominio/entidades/entrada_historial.dart';
import '../../../dominio/entidades/fragmento_respaldo.dart';
import '../../../dominio/entidades/fuente.dart';
import '../../../dominio/entidades/prediccion_ml.dart';
import '../../../dominio/entidades/procedencia.dart';
import '../../../dominio/entidades/respuesta.dart';
import '../../../dominio/objetos_valor/idioma.dart';
import '../../../dominio/objetos_valor/modo_consulta.dart';
import '../../../dominio/puertos/asistente_port.dart';
import '../../configuracion.dart';

/// Adaptador del puerto contra la API desplegada (Render), con los mismos endpoints
/// publicos que la web: `POST /api/consultas`, `POST /api/predicciones`, `GET /api/modelos`,
/// `GET /api/fuentes` y `GET /api/estado`.
///
/// No envia ningun token: ni `X-Admin-Token` (la app no administra nada) ni el de pruebas.
/// Ante un 429 devuelve el error con la espera que pide el servidor y no reintenta: decidir
/// cuando volver a intentar es de quien consulta, no de un bucle (ADR-037).
class AsistenteNube implements AsistentePort {
  AsistenteNube({
    String? urlBase,
    http.Client? cliente,
    this.espera = Configuracion.esperaEnLinea,
  }) : _url = (urlBase ?? Configuracion.urlApi).replaceAll(RegExp(r'/$'), ''),
       _cliente = cliente ?? http.Client();

  final String _url;
  final http.Client _cliente;

  /// Tiempo maximo de una peticion. En modo automatico el conmutador corta antes.
  final Duration espera;

  Map<String, double>? _pesosCobertura;

  String get url => _url;

  @override
  Future<Respuesta> consultar(String texto) async {
    final datos =
        await _pedir(
              () => _cliente.post(
                Uri.parse('$_url/api/consultas'),
                headers: const {'Content-Type': 'application/json'},
                body: jsonEncode({'texto': texto}),
              ),
              espera,
            )
            as Map<String, dynamic>;
    return _aRespuesta(datos);
  }

  /// El historial del servidor exige el token de administracion en la nube (ADR-036): la app
  /// no lo lee. El historial que se muestra es el del telefono, y lo lleva el conmutador,
  /// que es quien sabe si la respuesta de la nube llego a usarse.
  @override
  Future<List<EntradaHistorial>> historial({int limite = 20}) async => const [];

  @override
  Future<EstadoSistema> estado() async {
    final datos =
        await _pedir(() => _cliente.get(Uri.parse('$_url/api/estado')), espera)
            as Map<String, dynamic>;
    return EstadoSistema(
      fragmentosIndexados: datos['fragmentos_indexados'] as int,
      umbralAbstencion: (datos['umbral_abstencion'] as num).toDouble(),
      disponible: datos['generador_disponible'] as bool? ?? true,
      modo: ModoConsulta.enLinea,
      documentos: datos['documentos_corpus'] as int?,
      generador: datos['generador'] as String?,
      predictoresDisponibles:
          datos['predictores_disponibles'] as bool? ?? false,
    );
  }

  @override
  Future<List<Fuente>> fuentes() async {
    final lista =
        await _pedir(() => _cliente.get(Uri.parse('$_url/api/fuentes')), espera)
            as List<dynamic>;
    return lista
        .cast<Map<String, dynamic>>()
        .map(
          (f) => Fuente(
            nombreArchivo: f['nombre_archivo'] as String,
            titulo: f['titulo'] as String?,
            entidadPublicadora: f['entidad_publicadora'] as String?,
            licenciamiento: f['licenciamiento'] as String?,
            paginasTotales: f['paginas_totales'] as int?,
          ),
        )
        .toList();
  }

  @override
  Future<PrediccionMl> predecir(String texto) async {
    final datos =
        await _pedir(
              () => _cliente.post(
                Uri.parse('$_url/api/predicciones'),
                headers: const {'Content-Type': 'application/json'},
                body: jsonEncode({'texto': texto}),
              ),
              espera,
            )
            as Map<String, dynamic>;
    final pesos = await _pesos();
    final cobertura = datos['cobertura'] as Map<String, dynamic>? ?? const {};
    final pasajes = datos['pasajes'] as Map<String, dynamic>? ?? const {};
    return PrediccionMl(
      texto: datos['texto'] as String? ?? texto,
      probabilidadCobertura: (cobertura['probabilidad'] as num?)?.toDouble(),
      corteCobertura: (cobertura['corte'] as num?)?.toDouble() ?? 0.25,
      decisionCobertura: cobertura['decision'] as String?,
      bloquearia: cobertura['bloquearia_respuesta'] as bool? ?? false,
      probabilidadPasajes: (pasajes['probabilidad'] as num?)?.toDouble(),
      cortePasajes: (pasajes['corte'] as num?)?.toDouble() ?? 0.5,
      decisionPasajes: pasajes['decision'] as String?,
      caracteristicas: _aMapaNumerico(datos['caracteristicas']),
      pesosCobertura: pesos,
    );
  }

  /// Coeficientes del modelo de cobertura, de `GET /api/modelos`. Se piden una vez.
  Future<Map<String, double>> _pesos() async {
    if (_pesosCobertura != null) return _pesosCobertura!;
    try {
      final modelos =
          await _pedir(
                () => _cliente.get(Uri.parse('$_url/api/modelos')),
                Configuracion.esperaLectura,
              )
              as List<dynamic>;
      final cobertura = modelos.cast<Map<String, dynamic>>().firstWhere(
        (m) => m['clave'] == 'cobertura',
        orElse: () => const {},
      );
      _pesosCobertura = _aMapaNumerico(cobertura['coeficientes']);
    } on ErrorConsulta {
      return const {};
    }
    return _pesosCobertura!;
  }

  static Map<String, double> _aMapaNumerico(Object? crudo) => {
    for (final e in ((crudo as Map<String, dynamic>?) ?? const {}).entries)
      if (e.value is num) e.key: (e.value as num).toDouble(),
  };

  /// Ejecuta la peticion y traduce cualquier fallo a un [ErrorConsulta] con su tipo.
  Future<Object?> _pedir(
    Future<http.Response> Function() peticion,
    Duration limite,
  ) async {
    final http.Response respuesta;
    try {
      respuesta = await peticion().timeout(limite);
    } on TimeoutException {
      throw const ErrorConsulta(
        'La nube tardó demasiado en responder. Si estuvo sin uso, puede tardar hasta un '
        'minuto en activarse.',
        tipo: TipoErrorConsulta.tiempo,
      );
    } on SocketException {
      throw const ErrorConsulta(
        'No hay conexión con el servicio en la nube.',
        tipo: TipoErrorConsulta.red,
      );
    } on HandshakeException {
      throw const ErrorConsulta(
        'No se pudo establecer una conexión segura con la nube.',
        tipo: TipoErrorConsulta.red,
      );
    } on http.ClientException {
      throw const ErrorConsulta(
        'No hay conexión con el servicio en la nube.',
        tipo: TipoErrorConsulta.red,
      );
    }

    final texto = utf8.decode(respuesta.bodyBytes);
    final codigo = respuesta.statusCode;
    if (codigo >= 400) {
      Object? cuerpo;
      try {
        cuerpo = texto.isEmpty ? null : jsonDecode(texto);
      } on FormatException {
        cuerpo = null;
      }
      final detalle = cuerpo is Map && cuerpo['detail'] is String
          ? cuerpo['detail'] as String
          : null;
      if (codigo == 429) {
        final segundos = int.tryParse(respuesta.headers['retry-after'] ?? '');
        throw ErrorConsulta(
          detalle ??
              'Demasiadas consultas seguidas. Espera un momento antes de volver a intentar.',
          tipo: TipoErrorConsulta.limite,
          estado: 429,
          reintentarEn: Duration(seconds: segundos ?? 60),
        );
      }
      if (codigo == 422) {
        throw ErrorConsulta(
          detalle ??
              'La consulta no es válida: escribe entre 1 y 300 caracteres.',
          tipo: TipoErrorConsulta.validacion,
          estado: 422,
        );
      }
      throw ErrorConsulta(
        detalle ?? 'El servicio en la nube devolvió un error ($codigo).',
        tipo: TipoErrorConsulta.servicio,
        estado: codigo,
      );
    }
    return texto.isEmpty ? null : jsonDecode(texto);
  }

  Respuesta _aRespuesta(Map<String, dynamic> datos) => Respuesta(
    consultaId: datos['consulta_id'] as String,
    texto: datos['texto'] as String,
    abstenida: datos['abstenida'] as bool,
    idioma: Idioma.desdeCodigo(datos['idioma'] as String?),
    modo: ModoConsulta.enLinea,
    similitudMaxima: (datos['similitud_maxima'] as num?)?.toDouble() ?? 0.0,
    consultaTraducida:
        (datos['traduccion_usada'] ?? datos['consulta_traducida']) as String?,
    aviso: datos['aviso'] as String?,
    respaldo: _aFragmentos(datos['respaldo']),
    pasajes: _aFragmentos(datos['pasajes']),
    umbral: (datos['umbral'] as num?)?.toDouble(),
    viaRespaldo: datos['via_respaldo'] as String?,
    latenciaMs: (datos['latencia_ms'] as num?)?.toDouble(),
    redactadoPor: datos['redactado_por'] as String?,
    probabilidadCobertura: (datos['probabilidad_cobertura'] as num?)
        ?.toDouble(),
    probabilidadPasajes: (datos['probabilidad_pasajes'] as num?)?.toDouble(),
    abstencionPorPredictor: datos['abstencion_por_predictor'] as bool? ?? false,
  );

  List<FragmentoRespaldo> _aFragmentos(Object? crudo) =>
      ((crudo as List<dynamic>?) ?? const [])
          .cast<Map<String, dynamic>>()
          .map(
            (f) => FragmentoRespaldo(
              id: f['fragmento_id'] as String,
              texto: f['texto'] as String,
              procedencia: Procedencia(
                documento: f['documento'] as String,
                pagina: f['pagina'] as int,
              ),
              puntuacion: ((f['similitud'] ?? f['puntuacion']) as num)
                  .toDouble(),
              coincidenciaLema: f['coincidencia_lema'] as bool? ?? false,
            ),
          )
          .toList();
}
