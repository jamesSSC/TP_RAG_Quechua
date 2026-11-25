import 'package:path/path.dart' as p;
import 'package:sqflite/sqflite.dart';

import '../../../dominio/entidades/entrada_historial.dart';
import '../../../dominio/objetos_valor/modo_consulta.dart';
import '../../../dominio/puertos/preferencias_port.dart';

/// Historial de consultas y preferencias en SQLite, dentro del dispositivo.
///
/// Es la contrapartida movil del PostgreSQL del escritorio, y la misma entidad de dominio
/// sirve para las dos: lo unico que cambia es este adaptador. La base no sale del
/// telefono, de modo que el historial de lo que alguien consulta sobre su propia lengua
/// tampoco. Tambien en linea: el historial del servidor solo lo lee el administrador
/// (ADR-036), asi que el de la app es siempre el de este dispositivo.
class HistorialSqlite implements PreferenciasPort {
  HistorialSqlite._(this._base);

  final Database _base;

  static const _tabla = 'consultas';
  static const _preferencias = 'preferencias';

  static Future<HistorialSqlite> abrir({String? rutaBase}) async {
    final ruta =
        rutaBase ?? p.join(await getDatabasesPath(), 'quechua_wanka.db');
    final base = await openDatabase(
      ruta,
      version: 2,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE $_tabla (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consulta TEXT NOT NULL,
            respuesta TEXT NOT NULL,
            abstenida INTEGER NOT NULL,
            similitud REAL NOT NULL,
            momento TEXT NOT NULL,
            modo TEXT NOT NULL DEFAULT 'sin_conexion'
          )
        ''');
        await _crearPreferencias(db);
      },
      // v1 (PMV3 inicial, solo sin conexion) -> v2: el modo de cada consulta y las
      // preferencias. Las filas antiguas se resolvieron todas en el telefono.
      onUpgrade: (db, anterior, nueva) async {
        if (anterior < 2) {
          await db.execute(
            "ALTER TABLE $_tabla ADD COLUMN modo TEXT NOT NULL DEFAULT 'sin_conexion'",
          );
          await _crearPreferencias(db);
        }
      },
    );
    return HistorialSqlite._(base);
  }

  static Future<void> _crearPreferencias(Database db) => db.execute(
    'CREATE TABLE IF NOT EXISTS $_preferencias '
    '(clave TEXT PRIMARY KEY, valor TEXT NOT NULL)',
  );

  Future<void> registrar(EntradaHistorial entrada) async {
    await _base.insert(_tabla, {
      'consulta': entrada.consulta,
      'respuesta': entrada.respuesta,
      'abstenida': entrada.abstenida ? 1 : 0,
      'similitud': entrada.similitudMaxima,
      'momento': entrada.momento.toIso8601String(),
      'modo': entrada.modo.codigo,
    });
  }

  Future<List<EntradaHistorial>> recientes({int limite = 20}) async {
    final filas = await _base.query(_tabla, orderBy: 'id DESC', limit: limite);
    return filas
        .map(
          (f) => EntradaHistorial(
            consulta: f['consulta'] as String,
            respuesta: f['respuesta'] as String,
            abstenida: (f['abstenida'] as int) == 1,
            similitudMaxima: (f['similitud'] as num).toDouble(),
            momento: DateTime.parse(f['momento'] as String),
            modo: ModoConsulta.desdeCodigo(f['modo'] as String?),
          ),
        )
        .toList();
  }

  Future<String?> _leer(String clave) async {
    final filas = await _base.query(
      _preferencias,
      where: 'clave = ?',
      whereArgs: [clave],
      limit: 1,
    );
    return filas.isEmpty ? null : filas.first['valor'] as String;
  }

  Future<void> _escribir(String clave, String valor) => _base.insert(
    _preferencias,
    {'clave': clave, 'valor': valor},
    conflictAlgorithm: ConflictAlgorithm.replace,
  );

  @override
  Future<PreferenciaModo> modo() async =>
      PreferenciaModo.desdeNombre(await _leer('modo'));

  @override
  Future<void> guardarModo(PreferenciaModo modo) =>
      _escribir('modo', modo.name);

  @override
  Future<int> tamanoTexto() async =>
      int.tryParse(await _leer('tamano') ?? '') ?? 1;

  @override
  Future<void> guardarTamanoTexto(int indice) => _escribir('tamano', '$indice');

  Future<void> cerrar() => _base.close();
}
