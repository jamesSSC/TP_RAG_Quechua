# B10 · carga HTTP con Locust

`scripts/demo/05_carga_http.ps1` arranca la API con `GENERADOR=literal` (mide la API, no la GPU) y `ORIGEN_CONSULTAS=carga`
sobre una base temporal, y corre Locust 60 s con 1, 5 y 10 usuarios sobre `POST /api/consultas`, con las consultas de
`evaluacion_v2.json`. La analítica de demanda real no cuenta ninguna de estas consultas (`analitica_tras_la_carga.json`).

Resultados en `resumen.json` (CSV de Locust en esta carpeta). Resumen tras la corrección:

| Usuarios | Solicitudes/min | P50 (ms) | P95 (ms) | Errores |
|---|---|---|---|---|
| 1 | 5 448 | 10 | 16 | 0 % |
| 5 | 8 128 | 33 | 61 | 0 % |
| 10 | 8 015 | 70 | 100 | 0 % |

**Hallazgo.** La primera pasada (`antes_de_la_correccion/`) dio 0,1 % de errores con 5 usuarios y 0,9 % con 10: HTTP 500 por
`database is locked` de SQLite al registrar el historial desde varios hilos. Se corrigió con espera de bloqueo (30 s) y modo WAL, y
un fallo al registrar el historial ya no tumba la respuesta; el segundo run no tuvo errores.

**Por qué no se mide con 500 usuarios.** La aplicación es local y de un solo usuario (RNF-06): corre en la PC de quien consulta, sin
acceso remoto. 500 usuarios concurrentes no corresponden a ningún escenario de uso, y con el generador real el cuello de botella sería la GPU,
no la API; medirlo daría una cifra sin significado para el producto.
