# B5 · data masiva lista para el video

Scripts en `scripts/demo/` (PowerShell, UTF-8 con BOM, rutas con espacios). Generador: `backend/scripts/generar_transacciones.py`
(semilla 2026, generador literal sin Ollama, origen `carga`). Ninguna base real se tocó.

| Medida | SQLite (`backend/carga.db`, 800) | PostgreSQL (`quechua_wanka_demo`, 1000, por procedimientos) |
|---|---|---|
| Transacciones por segundo | 60,9 | 114,6 |
| Latencia media / P50 / P95 / máxima (ms) | 8,12 / 6,3 / 13,9 / 27,3 | 7,6 / 5,8 / 14,1 / 26,0 |
| Falsos positivos en las negativas etiquetadas | 0 | 0 |
| Filas en la base, por origen | carga 800 | carga 1000 |
| Abstenciones registradas | 186 | 187 |
| Documentos con respaldo | 2 | 2 |

- Idempotencia: dos corridas de 02 dan el mismo CSV salvo la columna de latencia.
- Privacidad: el CSV publica el texto solo de las particiones versionadas (A, B, C, D y F). Las de `evaluacion_prosa.json` (E) y las derivadas
  del corpus (lema_es, lema_en) salen como `[huella:…]`. El informe JSON de Newman, que trae respuestas completas, no se versiona.
- `metricas/`: salida de `04_metricas.ps1` (pytest, vitest, arnés idéntico a la línea base, entrenar_predictores sobre carpeta temporal con
  modelos versionados intactos, evaluar_pmv2, Newman 15 solicitudes y 39 afirmaciones sin fallos, pip-audit limpio).
- Interfaz: con `01_arrancar_app.ps1 -BaseDemo`, la API devuelve `base_demostracion: true`; en «Predicción ML › Analítica de demanda» la casilla de
  demostración muestra el aviso rotulado, el total, la distribución por idioma y por vía, la probabilidad media y el P95.
