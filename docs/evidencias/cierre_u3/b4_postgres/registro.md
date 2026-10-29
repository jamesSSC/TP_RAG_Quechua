# B4 · procedimientos almacenados visibles y probados

- PostgreSQL 16 local. Pruebas de integración contra `quechua_wanka_pruebas`: **4 aprobadas, 0 omitidas** (las 3 originales
  más la de origen de B3); `pruebas_integracion_postgres.txt`. Sin la variable `POSTGRES_PRUEBAS_URL` las 4 se omiten, como en CI.
- Suite completa con esa variable: 216 aprobadas, 0 omitidas (`suite_completa.txt`).
- `docs/video/consultas_postgres.sql` ejecutado con psql contra `quechua_wanka_demo` (800 consultas `carga` generadas
  por `generar_transacciones.py` y 5 `usuario`; los procedimientos los instala el contenedor al arrancar): `salida_consultas_postgres.txt`.
  Muestra el CALL con origen dentro de BEGIN/ROLLBACK (el conteo vuelve a 5 usuario), el rechazo de una respuesta
  sin respaldo, el resumen real (5) frente al de demostración (805), el respaldo por documento y la demanda insatisfecha.
- Nuevas pruebas: `tests/architecture/test_arquitectura.py` (dominio solo biblioteca estándar; aplicación sin adaptadores
  ni infraestructura; ni una ni otra conocen PostgreSQL, SQLAlchemy ni FastAPI) y `test_seleccion_repositorio.py`
  (por defecto SQLAlchemy/SQLite; con `BASE_DATOS=postgres` el contenedor cablea `RepositorioConsultasPostgres` e instala los procedimientos).
- Se neutralizó una mención a PostgreSQL en el docstring de `repositorio_fuentes_port.py` (capa de aplicación).
