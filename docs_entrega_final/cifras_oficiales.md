# B7 · Cifras oficiales (fuente única)

El informe, el artículo, el póster y el video se corrigen **contra este archivo**. Cada cifra sale de un
comando y dice en qué commit se midió. Si una cifra del informe no coincide con esta, manda esta. La
guía pide `./docs`; se usó `./docs_entrega_final`.

Fecha de medición: 19 y 20/11/2026; actualizado el 24/11 (ronda 2, P7) y **recontado el 25/11/2026 sobre
`main` = `8d8969d`**, con los PR #35 a #41 fusionados. Repositorio base original:
`omarpiero/TP_RAG_Quechua@8088193`.

## Producto y proceso

| # | Cifra | Valor | Comando | Commit / rama |
|---|---|---|---|---|
| C-01 | Historias de usuario | **14** HU (HU-01 a HU-07, HU-08.1, HU-08.2, HU-09, HU-10.1 a HU-10.3, HU-11) y **9** historias técnicas (HT-00 a HT-08) | `grep -cE '^\| HU-[0-9]+(\.[0-9]+)? \|' docs/03_HISTORIAS_USUARIO.md` | `8088193` |
| C-02 | Pull requests | **42**: 40 fusionados (#1–#41 salvo #22), 1 cerrado sin fusionar (#22, keep-alive) y el #42 (restauración de documentos tras las fusiones). Más el PR #1 de `DalgomXD-byte/quechua-wanka-movil` (fusionado) | `gh pr list -R omarpiero/TP_RAG_Quechua --state all` | 25/11 |
| C-03 | Commits en `main` | **194** (157 en `4448478`; 137 en `8088193`) | `git log --oneline main \| wc -l` | `8d8969d` |
| C-04 | Puertos | **17**: 7 de entrada y 10 de salida | `ls backend/src/application/ports/{in,out}/*.py` | `8088193` |
| C-05 | Casos de uso / controladores REST / middleware | **8 / 6 / 7** | ver `docs_ingenieria_inversa/evidencias/fase_arquitectura/` | `8088193` |
| C-06 | Rutinas en PostgreSQL | **7**: 2 procedimientos y 5 funciones | `grep -hoiE "create (or replace )?(function\|procedure) [a-z_]+" backend/db/postgres/*.sql` | `8088193` |
| C-07 | WIP del Kanban | **Trello: 3** («una tarjeta por integrante», tarjeta en IN PROGRESS). `docs/05_KANBAN.md:15-24` dice 1 en desarrollo y 2 en las demás columnas: **unificar** (el tablero real usa 3) | Export JSON del tablero (20/11); `docs/05_KANBAN.md` | 20/11 |
| C-08 | Corpus | **3 605** fragmentos, **8** documentos (nube tras la limpieza H-14) | `curl -s https://quechua-api.onrender.com/api/estado` | 20/11 00:59 UTC |
| C-09 | Umbral τ | **0,48** (en local, en la nube y en el teléfono) | `config.py:75`; `manifiesto.json` de la app | `8088193` |

## Pruebas

| # | Cifra | Valor | Comando | Commit / rama |
|---|---|---|---|---|
| C-10 | pytest sin corpus | **406** aprobadas, **16** omitidas | `cd backend && pytest -q` en un clon limpio | `8088193` |
| C-11 | pytest con corpus (v2 + v3, sin PostgreSQL) | **416** aprobadas, **6** omitidas | ídem con `data/fragmentos_v2.jsonl` y `v3` | `8088193` |
| C-12 | pytest tras los arreglos de la S14 | **416** aprobadas, **16** omitidas (sin corpus; incluye la prueba sobre el corpus mínimo) | `pytest -q` | `fix/s14-arreglos-rapidos` (`54385b0`) |
| C-12b | pytest en `main` con corpus | **469** aprobadas, **6** omitidas (426 antes de la ronda 2) | `cd backend && pytest -q` | `8d8969d` |
| C-13 | Vitest | **65** en `main` (48 antes de la ronda 2: +5 P1, +3 P5, +9 P8) | `npx vitest run` | `8d8969d` |
| C-14 | Pruebas de Flutter | **45** (widget, adaptador de la nube, conmutador, seguridad, paridad, compositor) + 1 de integración en el dispositivo; `flutter analyze` sin avisos | `flutter test` | app `aead5e8` (v1.1.0, `master` de `DalgomXD-byte/quechua-wanka-movil` y `mobile/` en el #38) |
| C-15 | Arnés del sistema (248) | recall@5 **1,000** en A, B y D; **0 FP** en C | `metricas_ml_final.py` (barrido con τ = 0,48) | `docs/metricas-ml-final` |
| C-16 | Arnés en el teléfono (248, sin red) | recall@5 **1,000** en A, B y D; **0 FP** en C | `flutter test integration_test/arnes_dispositivo_test.dart -d emulator-5554` | app `ccb4e29` |
| C-17 | Paridad móvil ↔ web | **10/10** archivos del índice idénticos (sha256); paridad Dart **5/5**; `paridad_esperada.json` idéntico | `docs/evidencias/pmv3/movil/HT-05_movil_paridad_indice.txt` | `8088193` / `ccb4e29` |
| C-18 | τ en una muestra independiente (F, 107) | **0 FP**; cota del 95 % 3,4 % | `metricas_ml_final.py` | `docs/metricas-ml-final` |

## Machine learning

| # | Cifra | Valor | Fuente |
|---|---|---|---|
| C-19 | Predictor 1 (cobertura, n = 415) | AUC **0,996** (IC 95 % 0,993–0,999) · F1 0,979 con el corte 0,25 · Brier 0,027 | `docs_entrega_final/metricas/evidencias/metricas_ml_final.json` |
| C-20 | Predictor 2 (pasajes, n = 167) | AUC **0,980** (IC 95 % 0,964–0,993) · F1 0,898 · Brier 0,057 | ídem |
| C-21 | Abstenciones añadidas por el ML en el conjunto de evaluación | **0** con el corte 0,25 | `backend/modelos/metricas.json` → `compuerta_rn06` |

## Rendimiento

| # | Cifra | Valor | Fuente |
|---|---|---|---|
| C-22 | **Mediana de latencia** local con Qwen3.5 4B en GPU (respuestas, N = 220) | **2 744 ms** (P95 2 830) | `metricas/evidencias/latencia_local_qwen_gpu.json` |
| C-23 | Mediana local con el redactor extractivo (N = 248) | 6,8 ms (P95 15,0) | `…/latencia_local_extractivo.json` |
| C-24 | Mediana en la nube con Gemini (20/11, N = 220 respuestas, origen `humo`) | **6 424 ms** (P95 15 366; 55 de 220 por el respaldo extractivo, por el límite de 15 s). Abstenciones: P50 158 ms. Referencia U3: 923 ms. **Tras ADR-039 (tiempo máximo de Gemini 10 s, PR #39):** por medir con N ≥ 30 en dos franjas | `metricas/evidencias/latencia_nube_gemini.json`; `docs/17_…:75` |
| C-24b | Arnés de 248 consultas **en la nube** | recall@5 **1,000** en A, B y D; **0 FP** en C; 0 errores HTTP | ídem |
| C-25 | Arranque en frío de Render | 62,4 s y 72,4 s (U3); 67,6 s (19/11) | `docs/17_…:74`; bitácora del PMV3 |
| C-26 | Mediana sin conexión en el dispositivo (N = 248) | **0,80 ms** (P95 2,71) | `HU-10.2_movil_arnes_248_resumen.txt` |
| C-27 | APK release arm64 | **22,6 MB** | `flutter build apk --release --split-per-abi` |
| C-28 | Energía de GPU por respuesta / por abstención | **44,2 J / 0,07 J** | `latencia_local_qwen_gpu.json` |

## Teléfono físico (P3 de la ronda 2, por medir)

| # | Cifra | Valor | Fuente |
|---|---|---|---|
| C-33 | Teléfono (modelo, Android, RAM) | por medir | `docs/18_REPORTE_PMV3.md` §1 |
| C-34 | Latencia en línea y en modo avión, P50 / P95 (N ≥ 30 por modo) | por medir | `docs/evidencias/pmv3/movil/*_fisico*` |
| C-35 | Arnés de 248 consultas en el teléfono, sin red (FP en C) | por medir | ídem |
| C-36 | Tamaño instalado y memoria (`dumpsys meminfo`) | por medir | ídem |
| C-37 | Accessibility Scanner | por medir | ídem |

## Calidad y seguridad

| # | Cifra | Valor | Fuente |
|---|---|---|---|
| C-29 | FURPS+ | 6,9 (antes de la S13) → **7,4** (S13) → **7,6** (delta del PMV3, en la rama) | `docs_auditoria/07…`; `docs_auditoria/08_auditoria_delta_pmv3.md` |
| C-30 | OWASP | 61,0 → **79,0** → **82,0** (en la rama) | ídem |
| C-31 | ZAP | **Pasivo, solo local, 0 altas y 0 medias** (M-21, U3). No hay ZAP contra la nube ni escaneo activo | `docs_auditoria/04_auditoria_owasp.md:33,544` |
| C-32 | `npm audit` / `pip-audit` | 3 altas → **0** / **0** | `docs_ingenieria_inversa/evidencias/{antes,despues}/H-05_*`; `pip-audit -r requirements.txt` |

## Discrepancias que corrige este archivo

| Dónde decía | Valor anterior | Valor oficial |
|---|---|---|
| Reporte de ingeniería inversa v1.1 | 408/14 con corpus | 416/6 (C-11) |
| Informe S13 | Predicciones 20/min | 60/min (`config.py:93`) |
| Informe S13 | Aviso de arranque a los 5 s | 4 s (`api.js:8`) |
