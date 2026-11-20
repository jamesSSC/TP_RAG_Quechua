# B6 · Insumos para el informe final

Solo hechos verificables, cada uno con su `ruta:línea` (rutas relativas a la raíz del repositorio,
commit `8088193` salvo que se indique otro). **La redacción del informe la hace el equipo.** Atiende las
secciones II, III, V, VI y VIII de la consigna del informe final. La guía pide `./docs`; se usó
`./docs_entrega_final`.

## II. Conocimientos de ingeniería

| Área | Concepto | Dónde se aplica | `ruta:línea` / comprobación |
|---|---|---|---|
| Matemáticas | Ponderación TF-IDF por palabras y por n-gramas de caracteres (3 a 5) | Índice híbrido léxico (E4) | `backend/src/adapters/out/recuperacion/indice_hibrido_lexico.py:75-76` |
| Matemáticas | Similitud coseno (producto punto de vectores normalizados L2) y promedio de las dos vistas | Puntuación de cada fragmento | `…/indice_hibrido_lexico.py:130-136` |
| Matemáticas | BM25 Okapi (k1 = 1,5; b = 0,75) como línea base | Comparación con el híbrido (B3) | `backend/scripts/metricas_ml_final.py` (clase `Bm25`) |
| Estadística | Regresión logística con rasgos estandarizados y clases equilibradas; bosque aleatorio como comparación | Predictores 1 (cobertura) y 2 (pasajes) | `backend/scripts/entrenar_predictores.py:100-110` |
| Estadística | Validación cruzada estratificada k = 5, semilla 2026 | Evaluación de los predictores | `…/entrenar_predictores.py:172`; `metricas_ml_final.py` (`evaluar_predictor`) |
| Estadística | Bootstrap de 1 000 remuestreos (IC 95 % percentil) y cota exacta de Clopper-Pearson | IC de AUC, F1 y Brier; cota de la tasa de FP | `metricas_ml_final.py` (`evaluar_predictor`, `clopper_pearson_superior`) |
| Estadística | Métricas: precisión, exhaustividad, especificidad, F1, ROC-AUC, Brier | B3 | `docs_entrega_final/metricas/evidencias/metricas_ml_final.json` |
| Optimización | Umbral τ como «maximizar la cobertura sujeto a FP = 0»; τ = 0,48 | Salvaguarda de abstención | `backend/src/infrastructure/config.py:75`; regla en `backend/src/domain/services/evaluador_confianza.py:111-131`; barrido en `docs_entrega_final/metricas/evidencias/barrido_tau.csv` |
| Optimización | Cortes de operación de los modelos (0,25 y 0,50) | RN-06: el modelo solo añade abstenciones | `config.py:113-114` |
| Ciencias naturales (lingüística) | Normalización Unicode NFD sin diacríticos para comparar formas con y sin tilde | Depuración de la consulta y del corpus | `backend/src/domain/services/depurador_consulta.py:44-58` |
| Ciencias naturales (lingüística) | Estructura de la entrada lexicográfica `LEMA: formas` como unidad de segmentación y de coincidencia | Capa de lema (ADR-021) | `backend/src/domain/services/entradas_lexicas.py:7`; `indice_hibrido_lexico.py:85-94` |
| Ciencias naturales (lingüística) | Detección de idioma por palabras funcionales | Consulta en español o inglés | `backend/src/adapters/out/idioma/detector_idioma_heuristico.py:18-31` |
| Ciencias naturales (física) | Energía como integral de la potencia medida en el tiempo, E = ∫ (P − P_reposo) dt | Energía por respuesta y por abstención (B10) | `backend/scripts/medir_latencia_energia.py` (`MedidorGpu.energia_j`) |
| Ciencias naturales (física) | Latencia de red y arranque en frío del servidor | 62–72 s medidos en Render | `docs/17_REPORTE_METRICAS_U3.md:74` (N-01) |
| Ingeniería | Arquitectura hexagonal verificada por pruebas | El dominio solo usa la biblioteca estándar; la aplicación no importa adaptadores | `backend/tests/architecture/test_arquitectura.py:37-56` |
| Ingeniería | Inyección de dependencias en un único punto | Contenedor | `backend/src/infrastructure/contenedor.py:65` (y `quechua-wanka-movil/lib/infraestructura/contenedor.dart`) |
| Ingeniería | Pruebas automatizadas | pytest 416 (rama `fix/s14-arreglos-rapidos`), Vitest 48 (rama del logo), Flutter 45 | `docs_entrega_final/cifras_oficiales.md` |
| Ingeniería | Integración continua | ruff, Bandit, pytest con cobertura ≥ 85 %, pip-audit, oxlint, Vitest, `npm audit`, build | `.github/workflows/ci.yml` (rama `fix/s14-arreglos-rapidos`) |
| Ingeniería | Seguridad (OWASP) | Token de administración, límite por IP, HSTS, CSP | `backend/src/infrastructure/seguridad_nube.py`; `docs_auditoria/04` a `08` |
| Ingeniería | Calidad (FURPS+) | 7,4 (S13) → 7,6 (delta PMV3) | `docs_auditoria/07_auditoria_final.md:69-74`; `docs_auditoria/08_auditoria_delta_pmv3.md` §4 |

Lo que **no** existe en el código: reglas fonológicas del quechua wanka. El sistema no analiza la
morfología ni la fonología; compara cadenas. Si el informe menciona fonología, debe ser como
limitación o trabajo futuro.

## III. Acontecimientos tecnológicos

| Fecha | Acontecimiento | Impacto en el proyecto | Commit / PR |
|---|---|---|---|
| 2026-03-02 | Publicación de la familia Qwen3.5 (0,8B a 122B; fuente: fichas de Hugging Face y biblioteca de Ollama, consultadas el 21/09/2026) | SLM local del escritorio (`qwen3.5:4b`). La medición de 0,8B/2B llevó a no embarcar modelo en el móvil (ADR-026) | `docs/07_DECISIONES.md` (ADR-026); `docs/17_…:13` (E1) |
| 2026-10-29 | Retiro de `gemini-2.5-flash` (404 en la API) | La redacción en la nube cayó al respaldo extractivo durante la carga; se cambió a `gemini-3.8-flash` | PR **#18** (`5a4ad44`); `docs/16_REPORTE_DESPLIEGUE_NUBE.md:104,130,225` |
| 2026-10-29 | Gemini 3.8 Flash agotaba los 15 s en el plan gratuito | Cambio a **Gemini 3.5 Flash-Lite** (P50 772 ms, P95 1 017 ms en 120 consultas) | `e7476cd` |
| 2026-10/11 | Plan gratuito de Neon: 100 CU-h al mes | PR **#22** (keep-alive) **no se fusiona**: consumiría unas 90 CU-h | PR #22, abierto desde 2026-11-11 (`2b50e69`) |
| 2026-10/11 | Plan gratuito de Render: suspensión tras ~15 min sin tráfico | Arranque en frío de 62–72 s; aviso en la interfaz (ADR-033) y en la app (ADR-038); respaldo sin conexión en la app | `docs/17_…:74`; ADR-033; ADR-038 |
| 2026-11-19 | El índice del móvil sigue siendo el mismo del backend tras 2 meses de cambios | No hizo falta reexportar (HT-05) | `docs/evidencias/pmv3/movil/HT-05_movil_paridad_indice.txt` |

## V. Uso de herramientas modernas

| Herramienta | Versión | Uso | Resultado medido | Captura |
|---|---|---|---|---|
| Python | 3.12 | Backend, métricas y guiones | — | `informe_final/capturas/` (terminal) |
| FastAPI + uvicorn | ver `backend/requirements.txt` | API REST hexagonal | P50 6,8 ms local (extractivo) | Swagger `/docs` |
| scikit-learn | 1.6.0 (entorno de medición) | TF-IDF, regresión logística, validación cruzada | AUC 0,996 / 0,980 | — |
| React + Vite | ver `frontend/package.json` | Web | Vitest 48/48 | Web local y en la nube |
| Flutter | 3.44.9 | App en dos modos | 45 pruebas; APK de 22,6 MB | Emulador |
| PostgreSQL / Neon | 16 (CI) / Neon | Persistencia y 7 rutinas | 3 605 fragmentos y 8 documentos | **Por capturar (cuenta de James/Render)** |
| Render | plan gratuito | Despliegue | Arranque en frío 62–72 s | **Por capturar (cuenta de otro integrante)** |
| Gemini | 3.5 Flash-Lite | Redacción en la nube | P50 772 ms | — |
| Ollama + Qwen3.5 4B | Ollama 0.35 / `qwen3.5:4b` | Redacción local | ver B3 (`latencia_local_qwen_gpu.json`) | — |
| GitHub Actions | — | CI | CI en verde en las ramas del PMV3 | Página de *Actions* del fork |
| Playwright | 1.64.1 | Capturas y prueba de CSP | 0 violaciones de CSP | `docs_entrega_final/logo/` |
| Android Studio (emulador) | Pixel 9 Pro, API 37 | Pruebas del PMV3 | 248 consultas en el dispositivo | `docs/evidencias/pmv3/movil/` |
| Trello | — | Kanban | — | Lo actualiza Omar |
| Postman / Newman | Newman 6 | Colección de endpoints | — | `docs/Asistente_Quechua_Wanka.postman_collection.json` |
| Asistente de IA (Claude Code) | — | Programación asistida, mediciones y redacción de evidencias bajo revisión humana | — | Declarar en la nota sobre asistentes de IA (quién hizo qué) |

## VI. Diseño de base de datos

- **Diagrama ER:** `docs/diagramas/er.dot` (Graphviz), generado de los modelos SQLAlchemy de
  `backend/src/adapters/out/persistencia/modelos.py`. Ya existe; no hace falta completarlo para el PMV3,
  porque el PMV3 **no añade tablas en el servidor**.
- **Lado del teléfono:** SQLite con dos tablas, `consultas` (id, consulta, respuesta, abstenida,
  similitud, momento, modo) y `preferencias` (clave, valor).
  Fuente: `quechua-wanka-movil/lib/infraestructura/adaptadores/salida/historial_sqlite.dart`. Versión
  2 de la base, con migración desde la 1.
- **Rutinas en PostgreSQL:** 7 (2 procedimientos y 5 funciones):
  - `sp_registrar_consulta`, `sp_borrar_historial`, `fn_resumen_demanda`, `fn_respaldo_por_documento`,
    `fn_demanda_insatisfecha` y `fn_conteo_por_origen`, en `backend/db/postgres/procedimientos.sql`;
  - `fn_fragmentos_por_documento`, en `backend/db/postgres/esquema.sql`.

## VIII. Pruebas en otra plataforma

| Plataforma | Qué se ejecutó | Resultado | Evidencia |
|---|---|---|---|
| Windows 11 (PC de desarrollo, RTX 4060 Ti) | pytest y Vitest | 416 y 48 aprobadas | `docs_ingenieria_inversa/evidencias/despues/` |
| Ubuntu (`ubuntu-latest`, GitHub Actions) | pytest con PostgreSQL 16 efímero, pip-audit, oxlint, Vitest, build | CI en verde en `feat/pmv3-app-movil`, `feat/logo-proyecto` y `fix/s14-arreglos-rapidos` (esta última ya con ruff, Bandit, `npm audit` y la prueba del corpus mínimo, run 44656608139) | `gh run list -R jamesSSC/TP_RAG_Quechua` |
| Android x86_64 (emulador Pixel 9 Pro, API 37) | Arnés de 248 consultas sin red | A, B y D 1,000; C 0 FP | `docs/evidencias/pmv3/movil/HU-10.2_movil_arnes_248_resumen.png` |
| Android ARM64 de gama media (teléfono físico) | — | **Por medir** | — |
