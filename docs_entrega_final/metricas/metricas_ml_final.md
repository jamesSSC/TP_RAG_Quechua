# B3 · Rendimiento y métricas de ML finales

Atiende el **indicador 10** de la lista de cotejo U4 (6 puntos) y la sección 8.8 del informe. La guía
pide `./docs`; se usó `./docs_entrega_final` para no mezclarla con la documentación SDD.

**Reproducción** (desde `backend/`, con `data/fragmentos_v3.jsonl`, reconstruible con
`scripts/reconstruir_corpus.py`):

```bash
python scripts/metricas_ml_final.py                     # predictores, τ, BM25 y figuras (≈ 1 min)
python scripts/medir_latencia_energia.py http://127.0.0.1:8000 ../docs_entrega_final/metricas/evidencias \
       --energia --etiqueta local_qwen_gpu              # con GENERADOR=ollama y Ollama en marcha
python scripts/figura_latencias.py ../docs_entrega_final/metricas/evidencias
```

Datos: 415 consultas etiquetadas (A 120, B 60, D 40, E 60 con respaldo; C 28, F 107 sin respaldo), las
mismas 11 características y la misma semilla (2026) que `entrenar_predictores.py`. Ninguna consulta
nueva ni inventada. Todo en `evidencias/`.

## 1. Los dos predictores

Validación cruzada **estratificada k = 5**. Las métricas «fuera de partición» se calculan sobre las
predicciones de cada partición de prueba juntas. Los IC 95 % son de **bootstrap con 1 000
remuestreos** de esas predicciones.

### Predicción 1 · Cobertura documental (HU-08.1, RF-14) · n = 415 (280 positivas) · corte de operación 0,25

| Métrica | Fuera de partición | Media ± desv. por partición | IC 95 % (bootstrap) |
|---|---|---|---|
| ROC-AUC | **0,996** | 0,997 ± 0,002 | 0,993 – 0,999 |
| Precisión | 0,969 | 0,969 ± 0,022 | — |
| Exhaustividad | 0,989 | 0,989 ± 0,016 | — |
| Especificidad | 0,933 | 0,933 ± 0,048 | — |
| F1 | **0,979** | 0,979 ± 0,013 | 0,966 – 0,990 |
| Brier | 0,027 | 0,027 ± 0,013 | 0,018 – 0,037 |
| Matriz (corte 0,25) | VP 277 · FP 9 · VN 126 · FN 3 | | |

Comparación: el bosque aleatorio obtiene AUC 0,994 ± 0,005 y F1 0,950 ± 0,010, por debajo de la
regresión logística, que es la que se usa.

### Predicción 2 · Relevancia de pasajes (HU-04, RF-15) · n = 167 (60 positivas) · corte 0,50

| Métrica | Fuera de partición | Media ± desv. | IC 95 % |
|---|---|---|---|
| ROC-AUC | **0,980** | 0,977 ± 0,019 | 0,964 – 0,993 |
| Precisión | 0,851 | 0,857 ± 0,095 | — |
| Exhaustividad | 0,950 | 0,950 ± 0,046 | — |
| Especificidad | 0,907 | 0,907 ± 0,067 | — |
| F1 | **0,898** | 0,900 ± 0,068 | 0,839 – 0,947 |
| Brier | 0,057 | 0,057 ± 0,032 | 0,036 – 0,080 |
| Matriz | VP 57 · FP 10 · VN 97 · FN 3 | | |

Las cifras coinciden con las del PMV2 (AUC 0,996 y 0,980; `backend/modelos/metricas.json`): el cálculo
reproduce el entrenamiento.

**RN-06 en este conjunto:** con el corte vigente (0,25), el modelo de cobertura **no retira ninguna**
de las respuestas que el umbral habría dado; con 0,30 retiraría una
(`modelos/metricas.json → compuerta_rn06`). En el conjunto de evaluación, las abstenciones que se ven
las produce τ, no el modelo.

Figuras: `evidencias/roc_predictores.png`, `evidencias/matriz_cobertura.png` y `evidencias/matriz_pasajes.png`
(y sus versiones `_poster` a 300 ppp).

## 2. El umbral τ

**Formulación.** τ\* = argmax_τ cobertura(A ∪ B ∪ D), sujeto a FP(C) = 0.

| | Valor |
|---|---|
| Barrido | τ de 0,05 a 0,95, paso 0,01, con el caso de uso completo sin predictores (`evidencias/barrido_tau.csv`) |
| Primer τ con 0 FP en C | **0,47** |
| τ vigente | **0,48**: cobertura 1,000, FP 0 (margen de 0,01 sobre el mínimo factible) |
| Cobertura de A+B+D a lo largo del barrido | 1,000 en todo el rango: esas 220 consultas se atienden por coincidencia de lema (ADR-021), así que τ solo gobierna los falsos positivos |
| FP en C (calibración, n = 28) | 0. Cota superior del 95 % (Clopper-Pearson): **12,3 %** |
| **Muestra independiente** (F, 107 preguntas fuera de cobertura de `negativas_prosa.json`, que no intervino en la calibración de τ) | **0 FP** (ninguna respuesta afirmada). Cota superior del 95 %: **3,4 %** |

El bootstrap de la tasa de FP es degenerado cuando hay 0 FP: todas las remuestras dan 0. Por eso se
informa la cota exacta de Clopper-Pearson, que sí dice qué tasa no se puede descartar con esa muestra.
Esto responde a la observación del artículo: τ no solo tiene 0 FP en la muestra con la que se calibró,
sino también en una muestra separada casi cuatro veces mayor.

Figura: `evidencias/barrido_tau.png`.

## 3. Línea base: BM25 frente al híbrido

Las dos variantes reciben la **misma** preparación de la consulta: depuración y, en D, las variantes
de traducción de la tabla. A **ninguna** se le aplica la capa de lema.

| Partición | BM25 recall@5 | BM25 MRR@10 | Híbrido E4 recall@5 | Híbrido E4 MRR@10 |
|---|---|---|---|---|
| A (120) | 1,000 | 0,996 | 1,000 | 0,992 |
| B (60) | 1,000 | 1,000 | 1,000 | 1,000 |
| D (40) | 1,000 | 0,850 | 1,000 | 0,833 |
| Cobertura de A+B+D con 0 FP en C (solo puntuación) | **95,5 %** | | **93,2 %** | |

**Lectura honesta.** En este corpus, BM25 iguala al híbrido en recuperación y lo supera ligeramente
en cobertura sin falsos positivos. El 100 % del sistema completo **lo aporta la capa de lema**, no la
función de puntuación. Se mantiene E4 porque su puntuación es un coseno acotado en [0, 1], comparable
entre consultas, sobre el que está calibrado τ. La de BM25 no está acotada (umbral equivalente 9,85),
de modo que adoptarla obligaría a recalibrar y a reexportar el índice móvil.

## 4. Rendimiento

| Medición | Entorno | N | P50 | P95 | Fuente |
|---|---|---|---|---|---|
| Consulta completa con **Qwen3.5 4B en GPU** (RTX 4060 Ti), respuestas | Local | 220 | 2 744 ms | 2 830 ms | `evidencias/latencia_local_qwen_gpu.json` |
| Ídem, abstenciones (no invocan el modelo) | Local | 28 | 7,0 ms | 8,5 ms | ídem |
| Primera consulta (carga del modelo en VRAM) | Local | 1 | 12 537 ms | — | ídem (`calentamiento_ms`) |
| Consulta completa con el redactor **extractivo** | Local | 248 | 6,8 ms | 15,0 ms | `evidencias/latencia_local_extractivo.json` |
| Consulta completa con **Gemini**, respuestas (20/11, desde Perú, origen `humo`, 20/min) | Nube | 220 | **6 424 ms** | **15 366 ms** | `evidencias/latencia_nube_gemini.json` |
| Abstenciones en la nube (no invocan Gemini) | Nube | 28 | 158 ms | 349 ms | ídem |
| Referencia U3 (02/11): consultas con Gemini / abstención | Nube | — | 923 / 192 ms | 977 / 207 ms | `docs/17_REPORTE_METRICAS_U3.md:75` (N-02) |
| **Arranque en frío** de Render | Nube | 2 + 1 | 62,4 s y 72,4 s (U3); **67,6 s** el 19/11 (`GET /api/vivo` con `curl`, antes de la limpieza de Neon) | — | `docs/17_…:74`; bitácora del PMV3 |
| Consulta sin conexión **en el dispositivo** | Emulador x86_64 | 248 | 0,80 ms | 2,71 ms | `docs/evidencias/pmv3/movil/HU-10.2_movil_arnes_248_resumen.txt` |
| Tamaño del índice móvil | — | — | 12 MB (10 archivos) | — | `docs/18_REPORTE_PMV3.md` P3-10 |
| APK release arm64 | — | — | 22,6 MB | — | ídem P3-09 |

**Arnés en la nube (20/11, 248 consultas, origen `humo`):** A, B y D con recall@5 = **1,000** y
respondidas 220/220; **C: 0 falsos positivos** (0/28 respondidas); 0 errores HTTP. La salvaguarda se
mantiene igual en local, en la nube y en el teléfono.

**Lectura de la latencia en la nube.** Es unas 7 veces la de la U3: P50 6,4 s frente a 0,9 s. En 55 de
las 220 respuestas (25 %), Gemini no respondió dentro del límite de 15 s (`gemini_timeout`) y redactó el
respaldo extractivo, como prevé ADR-032; de ahí el P95 de 15,4 s. Las respuestas siguen siendo
correctas, pero el tiempo del modelo externo empeoró desde la U3. Para el informe: P50 6,4 s cumple el
RNF de 8 s, y el P95 no. Recomendación: bajar `GEMINI_TIMEOUT` a unos 6 s para que el respaldo actúe
antes, o volver a medir otro día para descartar una congestión puntual del plan gratuito.

**Por medir:** consulta en el **teléfono físico** ARM64, sin dispositivo conectado en esta sesión.

Figura: `evidencias/histograma_latencias.png`.

## 5. Energía (insumo de B10)

Potencia real de la GPU medida con `nvidia-smi` cada 100 ms durante las 248 consultas con Qwen. La
energía de cada consulta es ∫ (P − P_reposo) dt sobre su intervalo; potencia en reposo: 19,7 W.

| | n | Energía media por consulta | Total |
|---|---|---|---|
| Respuesta (invoca Qwen) | 220 | **44,2 J** | 9 727 J |
| Abstención (no invoca el modelo) | 28 | **0,07 J** | 2,0 J |

Cada abstención ahorra unos 44 J de GPU frente a una respuesta. En las 248 consultas, las 28
abstenciones (todas por τ; el modelo no añadió ninguna) evitaron unos 1,24 kJ. Para la nube y el
móvil solo hay datos medidos de latencia y tamaño. La estimación de la energía en Render o Gemini con
fuentes publicadas la hace Omar (B10).
