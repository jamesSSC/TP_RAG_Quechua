# B8 · Insumos del artículo (CIIS): PMV3 y nube

Solo insumos verificables, cada uno con su fuente; la redacción la hace el equipo. La guía pide
`./docs`; se usó `./docs_entrega_final`.

## 1. Medición final

| Qué | Valor | Fuente |
|---|---|---|
| Salvaguarda sin conexión, en el dispositivo (248 consultas) | recall@5 = 1,000 en A (120), B (60) y D (40); **0 FP de 28** en C | `docs/evidencias/pmv3/movil/HU-10.2_movil_arnes_248_resumen.txt` |
| Cota superior del 95 % de la tasa de FP en C (Clopper-Pearson) | 12,3 % (con n = 28 y 0 FP no puede afirmarse menos) | `docs_entrega_final/metricas/evidencias/metricas_ml_final.json` → `tau.calibracion_C` |
| τ en una muestra **independiente** de la calibración (F, 107 preguntas fuera de cobertura) | **0 FP** de 107; cota del 95 %: 3,4 % | ídem → `tau.muestra_independiente_F` |
| Barrido de τ | Primer τ sin FP: 0,47; τ vigente 0,48 (margen 0,01). La cobertura de A+B+D es 1,000 en todo el barrido porque esas consultas se atienden por coincidencia de lema; τ solo controla los FP | `…/barrido_tau.csv` |
| Predictor 1 (cobertura, n = 415) | AUC 0,996 (IC 95 % 0,993–0,999); F1 0,979 con el corte 0,25; Brier 0,027 | `metricas_ml_final.json` |
| Predictor 2 (pasajes, n = 167) | AUC 0,980 (IC 95 % 0,964–0,993); F1 0,898; Brier 0,057 | ídem |
| Línea base BM25 frente al híbrido E4 (solo puntuación, sin capa de lema) | recall@5 = 1,000 los dos; MRR@10 en D: BM25 0,850 y E4 0,833; cobertura con 0 FP: BM25 95,5 % y E4 93,2 % | `metricas_ml_final.json` → `bm25_frente_hibrido` |
| Latencia sin conexión en el dispositivo (N = 248) | P50 0,80 ms · P95 2,71 ms | `HU-10.2_movil_arnes_248_resumen.txt` |
| Latencia local (API, N = 248) | Extractivo: P50 6,8 ms · P95 15,0 ms. Qwen3.5 4B en GPU: ver `latencia_local_qwen_gpu.json` | `docs_entrega_final/metricas/evidencias/` |
| Tamaño del APK release arm64 | 22,6 MB (presupuesto: 1,2 GB) | `HU-10.3_movil_mediciones_emulador.txt` |

**Hallazgo que conviene declarar en la discusión.** En este corpus, BM25 iguala al híbrido E4 en
recuperación (recall@5) y lo supera ligeramente en cobertura sin falsos positivos (95,5 % frente a
93,2 %), cuando a ninguno de los dos se le aplica la capa de lema. El 100 % de cobertura del sistema
completo lo aporta la **coincidencia de lema** (ADR-021), no la elección de la función de puntuación.
Esto matiza la conclusión de la PoC (denso frente a léxico): lo decisivo es tratar la entrada de
diccionario como unidad, más que la variante léxica concreta.

## 2. Privacidad (corrección)

La afirmación «la consulta nunca sale del dispositivo» solo es cierta en el modo **sin conexión**.

| Modo | ¿Sale la consulta? | A dónde | Qué se guarda fuera del teléfono |
|---|---|---|---|
| Web en la nube | **Sí** | Render (API) y Google (Gemini, para redactar el texto con los fragmentos) | En Neon: texto de la consulta, respuesta, métricas y origen. Sin datos personales; la IP solo se registra como seudónimo SHA-256 truncado en la bitácora de seguridad |
| App, en línea | **Sí** | Igual que la web | Igual que la web. El historial que ve la persona está en el teléfono (SQLite) |
| App, sin conexión | **No** | — | Nada. El historial queda en el teléfono y, tras PMV3-D02, tampoco viaja en la copia de seguridad de Android |

Fuentes: `frontend/src/App.jsx` (aviso de privacidad de Gemini); `backend/src/infrastructure/seguridad_nube.py`
(`seudonimo`); ADR-038; `docs_auditoria/08_auditoria_delta_pmv3.md` (D-02).

## 3. ¿El móvil ejecuta el clasificador?

**No.** La app no ejecuta los predictores del PMV2 en el dispositivo:

- **Sin conexión,** `AsistenteLocal.predecir` lanza `ErrorConsulta` de tipo `noDisponible` y la
  interfaz lo dice. Fuente: `quechua-wanka-movil/lib/infraestructura/adaptadores/salida/asistente_local.dart`
  (método `predecir`). La decisión es solo τ = 0,48 más la coincidencia de lema.
- **En línea,** la app **muestra** las probabilidades que calcula la nube (`POST /api/consultas` y
  `POST /api/predicciones`), pero no las calcula.

Esto es coherente con el hallazgo H-17 de la ingeniería inversa: el móvil no tiene un predictor de ML
propio.

## 4. Reconocimiento de imágenes

El proyecto no tiene reconocimiento de imágenes. Si el criterio CIIS lo exige, **hay que avisar a Omar
antes de hacer nada**: no se implementó, y no hay que hacerlo sin preguntar.
