# B3 · origen de las consultas (HU-09, ADR-013)

| Base | Consultas por origen | Analítica por defecto | Con `incluir_sinteticas` |
|---|---|---|---|
| Base real de desarrollo (`backend/quechua_wanka.db`, 65 consultas, sin columna `origen`; leída en solo lectura, analítica sobre una copia migrada) | usuario 65 | Insuficiencia: 65 < 100 | Igual (no hay sintéticas), modo real |
| `carga.db` (800 transacciones de `generar_transacciones.py`, semilla 2026, origen `carga`) | carga 800 | Insuficiencia: 0 consultas reales de 100 necesarias; avisa que 800 de prueba no cuentan | Prioriza (800 consultas, 186 abstenciones, 15 términos) y rotula «Demostración con 800 consultas generadas por la prueba de carga; no es demanda real» |

- `/api/estado` sobre `carga.db`: `base_demostracion: true`; sobre la base real: `false`.
- Las 65 consultas anteriores a este cambio quedan como `usuario` por el valor por defecto de la migración;
  no hay forma de saber cuáles fueron pruebas manuales. Es lo que dice el rótulo, no una afirmación sobre su procedencia.
- Los 800 sintéticos se generaron sin tocar la base real: `RUTA_SQLITE` apuntó a un archivo temporal.
