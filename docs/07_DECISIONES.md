# 07 · Registro de decisiones (ADR)

> Por qué el sistema es como es. Una decisión **aceptada** solo se cambia con otro ADR que la sustituya;
> nunca se reescribe. Estados: `Propuesta` · `Aceptada` · `Sustituida por ADR-nn` · `Rechazada` ·
> `Abierta` (hay que decidir antes de una fecha).
>
> Mantenido por: **archivista** · Última revisión: 2026-10-01 · Versión 1.3 (línea base v2, ver `09_LINEA_BASE_V2.md`)

---

## Índice

| ADR | Título | Estado | Origen | Decidir antes de |
|---|---|---|---|---|
| 001 | Recuperación aumentada en lugar de ajuste fino | Aceptada | Documento 0 | — |
| 002 | Arquitectura hexagonal | Aceptada | Documento 0 | — |
| 003 | Scrum con cuatro sprints de tres semanas y WIP de Kanban | Aceptada | Documento 4 | — |
| 004 | Modelos, motores y almacenes por plataforma | Sustituida en parte por ADR-019 y ADR-026 | Documento 5 | — |
| 005 | Híbrido léxico como línea base de recuperación | Aceptada | Documento 6 (C-2) | — |
| 006 | Umbral por ausencia de falsos positivos, versionado | Aceptada (el valor lo fija ADR-020) | Documento 6 (C-4) | — |
| 007 | Segmentación por tipo documental | Aceptada | Documento 6 (C-3) | — |
| 008 | Traducción de la consulta EN→ES antes de recuperar | Aceptada; el **mecanismo** lo fija ADR-023 | Documento 6 (C-1) + cuaderno | — |
| 009 | Desarrollo con orquestador y tres subagentes bajo SDD | Aceptada (2026-09-24) | Propuesta del usuario | — |
| 010 | SonarQube Cloud + Community local para calidad y cobertura (sustituye una exclusión del Documento 5) | Aceptada (2026-09-24) | Usuario | — |
| 011 | GitHub Flow, Conventional Commits y repositorio privado | Aceptada (2026-09-24) | Usuario | — |
| 012 | Estrategia de recuperación en el móvil | Aceptada: opción (b), índice léxico exportado (ADR-019) | Documentos 5 y 6 (C-5) | — |
| 013 | Registro de consultas para la analítica frente a RNF-06 | **Abierta** · el usuario no expresó preferencia (2026-10-01); propuesta del orquestador pendiente de confirmación | Documento 0 (RF-14…16) vs RNF-06 | Antes del PR 8 (texto de la consulta en el historial) y Planning del sprint 3 (2026-11-02) |
| 014 | Los modelos predictivos solo pueden añadir abstenciones | **Propuesta** | Salvaguarda + RF-14/15 | Planning del sprint 3 |
| 015 | El corpus y los modelos no se versionan en Git | Aceptada (2026-09-24) | Usuario; R-07, RNF-11 | — |
| 016 | Markdown como fuente única del tablero | **Propuesta** | Esta planificación | Revisión del sprint 1 (2026-10-11) |
| 017 | FastAPI para la aplicación y servidor MCP de solo lectura para el desarrollo | Aceptada (2026-09-24) | Usuario | — |
| 018 | Identificador de fragmento compatible con la prueba de concepto | **Propuesta** | Documento 6 + conjunto de evaluación | Inicio de HU-02 |
| 019 | Sin base vectorial: índice léxico persistente y exportado al móvil | Aceptada (línea base v2) | Revisión 2, Docs. 0, 2 y 5 | — |
| 020 | τ = 0,48 en la implementación; 0,41 queda como resultado de la PoC | Aceptada (línea base v2) · **τ 0,48 confirmado el 2026-10-01** sobre `fragmentos_v3` (nota) · re-medir con M3 | Revisión 2, Doc. 6 | Cierre del PMV1 |
| 021 | Coincidencia exacta de lema como segunda vía de respaldo | **Aceptada (2026-10-01)** con 5 condiciones · implementación en PR 3 | Código base; anexo Doc. 5; `13_BRECHAS_RUBRICA.md` §3 | — |
| 022 | Pasajes de prosa sin afirmación como tercer caso de RF-08 | Aceptada (línea base v2) · con condiciones | Revisión 2, Doc. 0 RF-08 | — |
| 023 | Tabla EN→ES de lemas calculada en tiempo de compilación | Aceptada (línea base v2) · con condiciones | Revisión 2, Doc. 0 RF-04 | — |
| 024 | Sin OCR: señalar páginas sin texto y reparar acentos | Aceptada (línea base v2) | Revisión 2, Doc. 0 RF-01; anexo Doc. 5 | — |
| 025 | Interfaz React + Vite sobre la API FastAPI (sustituye a Streamlit) | Aceptada (línea base v2) · endurecer la UI | Revisión 2, Doc. 5 | — |
| 026 | Sin modelo generador en el móvil: plantilla determinista | Aceptada (línea base v2) · **revisión abierta** (modo enriquecido opcional) | Anexo Doc. 5, tabla B | Planning del PMV3 |
| 027 | SQLite como persistencia en los tres PMV; PostgreSQL como segundo adaptador | **Propuesta** · el usuario no expresó preferencia (2026-10-01); pendiente de confirmación | Anexo Doc. 5, tabla E; RF-11; RNF-06 | Antes del PR 8 |

---

## ADR-001 · Recuperación aumentada en lugar de ajuste fino — Aceptada

**Contexto.** No existe corpus de entrenamiento suficiente para la variedad wanka. **Decisión.** El
conocimiento lingüístico procede del contexto recuperado, no de los pesos. **Consecuencias.** La calidad
depende de la recuperación y del corpus; la abstención es implementable porque hay una puntuación de
respaldo. **Fuente.** Documento 0; SOUDANI, KANOULAS y HASIBI (2024).

## ADR-002 · Arquitectura hexagonal — Aceptada

**Decisión.** Puertos y adaptadores (4,65 frente a 2,80 de microservicios y 3,10 orientada a eventos).
**Consecuencias.** El núcleo (normalización, depuración, recuperación, abstención, composición,
trazabilidad) no cambia entre plataformas; se verifica con una prueba de arquitectura. **Fuente.**
Documento 0; COCKBURN (2005).

## ADR-003 · Scrum, cuatro sprints de tres semanas y WIP — Aceptada

**Decisión.** Scrum (4,65) con límite de trabajo en curso de Kanban; sprints S1-S3, S4-S6, S7-S9,
S10-S12 que cierran en frontera de PMV; DoD-1…DoD-10 con DoD-4 transversal. **Fuente.** Documento 4.

## ADR-004 · Modelos, motores y almacenes — Aceptada

**Decisión.** Escritorio: Qwen3.5-4B sobre Ollama, ChromaDB, FastAPI + Streamlit. Móvil: Qwen3.5-0.8B
cuantizado sobre llama.cpp, sqlite-vec, Flutter. MediaPipe descartado salvo el disparador (paquete
> 1,2 GB → Gemma 3 1B + MediaPipe). **Nota.** La elección de codificador (bge-m3 en escritorio,
multilingual-E5-small en ONNX en móvil) queda matizada por ADR-005 y ADR-012. **Fuente.** Documento 5.

## ADR-005 · Híbrido léxico como línea base — Aceptada

**Contexto.** Medido sobre el corpus real: híbrido léxico recall@5 1,000 en A y B; E5-small 0,650; E5-base
0,600, con similitudes comprimidas (separación 0,024 y 0,009 frente a 0,403). **Decisión.** El PMV1 usa
TF-IDF de palabras (1–2 g) + caracteres (3–5 g, `char_wb`, `sublinear_tf`) con peso 0,5/0,5. Lo denso
solo entra como complemento medido (HT-07). **Consecuencias.** El puerto `EmbeddingsPort` admite
representaciones dispersas. **Fuente.** Documento 6, §6.7.

## ADR-006 · Umbral por ausencia de falsos positivos — Aceptada

**Decisión.** τ inicial = 0,41 (0 FP, 28/28, recall 0,856, F1 0,922), elegido como el primer valor sin
falsos positivos y no por F1 máximo (0,25 da F1 0,994 pero 1 FP). τ vive en `config/umbral.yaml` con su
fecha, el informe del arnés que lo justifica y la configuración (corpus, segmentación, codificador,
tratamiento de la consulta). **Consecuencias.** Todo cambio de τ es un commit enlazado a un informe y se
anota aquí. **Fuente.** Documento 6, §6.7.4.

## ADR-007 · Segmentación por tipo documental — Aceptada

**Decisión.** Material lexicográfico: una entrada por fragmento. Prosa: ~650 caracteres por límite de
párrafo. Campo `tipo` obligatorio. **Contexto.** La segmentación uniforme hunde el recall en el punto de
operación a 48,3 % (ingesta real) o 34,4 % (reconstrucción), frente a 85,6 %. **Fuente.** Documento 6,
§6.7.5, y cuaderno integral.

## ADR-008 · Traducción de la consulta antes de recuperar — Aceptada, recalibración pendiente

**Contexto.** Ninguna estrategia resuelve las consultas en inglés (recall@5 0,175 léxico, 0,275 denso);
agrandar el codificador no lo arregla (E5-base mantiene 0,275). Con traducción previa, recall@5 en D sube a
0,875, pero **solo 20 de 40** superan τ = 0,41. **Decisión.** Traducir solo la consulta, con el SLM local y
una instrucción acotada; recuperar con la original y la traducida y quedarse con la mejor puntuación;
registrar la traducción en la traza; **recalibrar τ** con el arnés completo antes de declarar RF-04
cumplido. Alternativa de reserva: indexar una glosa en inglés por entrada léxica. **Tensión abierta.**
El Documento 4 da prioridad media a HU-05, pero la especificación de construcción exige D ≥ 0,80 para el
Hito 1. **Propuesta del orquestador:** mantener D ≥ 0,80 como criterio del Hito 1 porque la solución ya
está medida y su costo es bajo; si el sprint 2 se estrecha, se declara como incumplimiento parcial
documentado en lugar de retirar el criterio. **Decide:** usuario, en el Planning del sprint 2.

## ADR-009 · Orquestador y tres subagentes bajo SDD — Aceptada (2026-09-24)

**Contexto.** Desarrollo asistido por Claude Code con especificaciones como fuente de verdad.
**Decisión.** Orquestador (Opus 5.5, sesión principal) que dialoga con el usuario y delega en
tres subagentes Sonnet 5: archivista, programador (TDD) y auditor. Ciclo de ocho pasos con cuatro
compuertas; propiedad de archivos definida. Detalle en `06_MODELO_AGENTES.md`. **Consecuencias.** La
documentación se convierte en la memoria compartida y debe mantenerse al día en cada sesión; el costo de
coordinación lo absorbe el orquestador. **Riesgo.** Los subagentes no recuerdan invocaciones anteriores:
todo encargo debe llevar sus referencias explícitas.

## ADR-010 · SonarQube Cloud + Community local — Aceptada (2026-09-24)

**Contexto.** El Documento 5 excluyó expresamente el análisis estático «por proporción», apoyándose en que
el sistema no expone servicios en red. Dos hechos cambian ese análisis: (1) el PMV1 **sí** expone un
servicio HTTP local (FastAPI); (2) el código lo generan agentes, lo que aumenta el valor de una revisión
automática independiente. El costo es nulo: SonarQube Cloud tiene plan gratuito (hasta 50 000 líneas
privadas) y el usuario ya tiene instalado el Community Build. **Decisión (elegida por el usuario).**
SonarQube Cloud gratuito como puerta de calidad en CI —analizado desde GitHub Actions para importar la
cobertura de `pytest-cov`— y consultado por el auditor mediante el servidor MCP oficial; Community Build
local como respaldo sin conexión. Los mínimos de cobertura (90 % en `dominio/`, 70 % global) se exigen con
`pytest --cov-fail-under`, independientemente de la puerta de Sonar. **Consecuencias.** Esta decisión **sustituye** la exclusión del
Documento 5 y debe declararse así en la documentación final; se añaden RS-01…RS-07 como criterios
verificables. **Pendiente de verificar en HT-00:** soporte de Dart en el plan gratuito.

## ADR-011 · GitHub Flow, Conventional Commits y repositorio privado — Aceptada (2026-09-24)

**Decisión (elegida por el usuario).** `main` protegida; una rama corta por historia (`feat/HU-03-…`); commits
convencionales con `Refs: <ID>`; fusión por *squash*; etiquetas `v0.1.0`, `v0.2.0`, `v1.0.0` por hito;
repositorio privado. **Por qué GitHub Flow y no Git Flow.** Con un solo programador y sprints de tres
semanas, una rama `develop` añade integración sin aportar control; además, el plan gratuito de SonarQube
Cloud solo analiza PR cuyo destino es la rama principal. **Por qué privado.** El corpus tiene licencias
heterogéneas (R-07) y el código no debe publicarse antes de revisar esas condiciones.

## ADR-012 · Estrategia de recuperación en el móvil — Abierta

**Contexto.** El Documento 5 eligió multilingual-E5-small en ONNX para el móvil, pero la PoC midió que
ese codificador rinde por debajo del híbrido léxico (recall@5 0,650 frente a 1,000) y que su umbral sin
falsos positivos solo conserva el 30 % de las consultas. **Opciones.**

| Opción | A favor | En contra |
|---|---|---|
| (a) E5-small ONNX, como en el Documento 5 | Coherente con la planificación | Peor recuperación; exige abstención por margen o calibración (C-5); índice distinto del de escritorio |
| (b) Llevar el híbrido léxico al móvil (matrices TF-IDF precalculadas) | Mismo núcleo, mismo τ, misma salvaguarda en ambas plataformas; sin modelo de representaciones en el paquete | Implementar TF-IDF y n-gramas en Dart o precalcular vocabularios; tamaño del índice por medir |
| (c) Híbrido léxico + E5-small como complemento | Mejor recall potencial en inglés | Más complejidad y más peso en 1,2 GB |

**Inclinación del orquestador:** (b), porque es la única que conserva el núcleo invariante que exige la
arquitectura y evita recalibrar la salvaguarda en la última fase. **Requiere** medir el tamaño del índice
disperso y la latencia en Dart. **Decide:** usuario, a más tardar en el Planning del sprint 3. Si se elige
(b), sustituye parcialmente a ADR-004 en lo relativo al codificador móvil.

## ADR-013 · Registro de consultas para la analítica frente a RNF-06 — Abierta

**Contexto.** RF-14, RF-15 y RF-16 necesitan un registro de consultas entre sesiones; RNF-06 prohíbe
recolectar datos personales y RF-11 solo pide historial de la sesión activa. Una consulta de texto libre
puede contener datos personales. **Propuesta.** Registro local, sin identificador de persona ni de
dispositivo, que guarda la consulta depurada, la similitud, la decisión y la fecha; desactivable; nunca
sale del equipo; con aviso en la interfaz. **Riesgo declarado.** En doce semanas el volumen real puede no
alcanzar las 100 consultas de HU-09; no se completará con consultas fabricadas. **Decide:** usuario, en el
Planning del sprint 3.

**Nota 2026-10-01 (cierre del PMV1).** Para el historial del PMV1 (RF-11, PR 8) se preguntó al usuario si se
guarda el texto de la consulta. El usuario respondió «sin preferencia» el 2026-10-01. **Sigue abierta.**
Propuesta del orquestador, pendiente de confirmación antes del PR 8: guardar el texto de la consulta con aviso
visible en la interfaz y borrado del historial (`DELETE /api/historial`), sin identificadores. No se marca como
aceptada. Fuente: encargo del orquestador del 2026-10-01.

## ADR-014 · Los modelos predictivos solo pueden añadir abstenciones — Propuesta

**Decisión propuesta.** El predictor de cobertura y el umbral adaptativo pueden convertir una respuesta en
abstención, nunca una abstención en respuesta; el umbral adaptado nunca desciende del último τ sin falsos
positivos calibrado con el arnés. **Por qué.** RF-15 pide un umbral «no fijado a un valor arbitrario»;
sin esta cota, un ajuste automático podría erosionar la salvaguarda sin que nadie lo decidiera.
**Verificación.** RN-06 con prueba de monotonía.

## ADR-015 · El corpus y los modelos no se versionan en Git — Aceptada (2026-09-24)

**Decisión (elegida por el usuario).** Los PDF viven en `corpus/pdf/` en el equipo pero están en
`.gitignore`, igual que `data/`, los índices, los pesos y `referencia_poc/datos/fragmentos_v2.jsonl`. En
el repositorio se versionan `corpus/MANIFIESTO.yaml` (título, fuente, fecha, licencia, huella SHA-256 de
cada PDF), el conjunto de evaluación y los scripts que reconstruyen todo. **Por qué.** Licenciamiento (R-07), gobernanza CARE (RNF-11) y tamaño de los pesos.

## ADR-016 · Markdown como fuente única del tablero — Propuesta

**Contexto.** El Documento 5 eligió GitHub Projects para la gestión. **Decisión propuesta.**
`05_KANBAN.md` es la fuente de verdad porque los agentes la leen y escriben sin credenciales ni API;
GitHub Projects puede reflejarlo como vista opcional, nunca al revés. **Consecuencia.** Si se usa GitHub
Projects, el archivista lo sincroniza al cierre de sesión y cualquier discrepancia se resuelve a favor del
markdown.

---

## ADR-017 · FastAPI para la aplicación y servidor MCP de solo lectura para el desarrollo — Aceptada (2026-09-24)

**Contexto.** El usuario preguntó si convenía algo mejor integrado con Claude Code que FastAPI. **Análisis.**
MCP no sustituye a FastAPI: el producto debe funcionar sin conexión y sin ningún LLM externo (RF-12), y
Streamlit (PMV1) y la referencia para el móvil necesitan una API local convencional. Lo que MCP sí aporta
es que los agentes prueben el sistema real durante el desarrollo. **Decisión.** FastAPI sigue siendo la
API del producto (solo en `127.0.0.1`). Se añade un **segundo adaptador de entrada**, un servidor MCP
(SDK oficial de MCP para Python, transporte `stdio`) que llama a los **mismos casos de uso** —no a los
endpoints HTTP—, con herramientas de **solo lectura**: `consultar`, `buscar_fragmentos`, `ejecutar_arnes`,
`verificar_salvaguarda`, `estado_indice`. Se construye en HT-08 y entonces se registra en `.mcp.json`.
**Alternativa descartada.** Envolver los endpoints de FastAPI con `fastapi-mcp`: obliga a tener el servidor
HTTP levantado y acopla las herramientas a la forma de la API en vez de a los casos de uso.
**Consecuencias.** Al usar esas herramientas, fragmentos del corpus viajan a la API de Claude: aceptable
solo en desarrollo y con herramientas de lectura; se declara en `CLAUDE.md` §12. Ninguna herramienta
escribe en el índice, en `config/` ni en `corpus/`.

## ADR-018 · Identificador de fragmento compatible con la prueba de concepto — Propuesta

**Contexto.** `02_REQUERIMIENTOS.md` pedía un identificador «derivado del contenido», pero la PoC usa
`md5("<archivo>|<página>|<índice>")[:12]` y los 248 casos de `evaluacion_v2.json` referencian esos
identificadores. Cambiar el esquema invalidaría el conjunto de evaluación. **Decisión propuesta.** Conservar
el esquema de la PoC; fijar los nombres de archivo del corpus en `MANIFIESTO.yaml` (por eso el PDF de
*Saberes y haceres* se copió con el nombre usado en la indexación); añadir a HU-02 una prueba de regresión:
la nueva ingesta reproduce los mismos identificadores sobre el mismo corpus. La reindexación sigue siendo
idempotente porque la segmentación es determinista. **Si se quisiera cambiar el esquema:** remapear
`evaluacion_v2.json` con un script versionado y registrar un ADR que sustituya a este.

---

## ADR-019 · Sin base vectorial: índice léxico persistente y exportado — Aceptada (línea base v2)

**Contexto.** ADR-005 hizo del híbrido léxico la línea base; la implementación no produjo ningún vector
denso, de modo que ChromaDB y sqlite-vec perdieron su objeto. **Decisión.** Escritorio: índice léxico
persistente (TF-IDF de palabras y de n-gramas de caracteres 3–5, promediados). Móvil: el mismo índice,
**exportado** en tiempo de compilación a binarios planos por columnas (vocabulario, IDF y matriz), de modo
que el dispositivo solo ejecuta el producto escalar. **Verificación obligatoria:** paridad aritmética entre
motores (criterio < 1 × 10⁻⁶ y top-5 idéntico). Resuelve ADR-012 con la opción (b).

## ADR-020 · τ = 0,48 en la implementación — Aceptada (línea base v2)

**Contexto.** La PoC midió 0,41 con su formulación; al fijar la formulación exacta del híbrido, el primer
τ sin FP pasó a 0,48 (92,8 % de consultas atendibles). Con esa puntuación, usar 0,41 **produciría falsos
positivos**. **Decisión.** τ vigente = 0,48, leído de configuración. El Documento 6 conserva 0,41 como
resultado de la PoC, con una nota. **Condición.** Se vuelve a barrer (M3) sobre el código final; si cambia,
nuevo ADR con su barrido.

**Nota 2026-10-01 · τ se conserva en 0,48 (no sustituye la decisión; la confirma con una medición nueva).**
Medido el 2026-10-01 con el arnés del caso de uso sobre **`fragmentos_v3.jsonl`** (el corpus de la aplicación;
línea base congelada en `docs/evidencias/2026-10-01_base-integrante_pc-rtx4060/`):

| Dato (solo corpus v3) | Valor medido |
|---|---|
| Primer τ sin falsos positivos | **0,47** |
| Similitud máxima de una consulta de C | **0,4698** (margen de 0,47: 0,0002; margen de 0,48: 0,010) |
| A+B respondidas con τ 0,48, **sin** regla de lema | **165/180 (91,7 %)** |
| A+B respondidas con τ 0,48, **con** regla de lema | **180/180**, 0 FP en C |
| A+B con τ 0,47, sin regla de lema | 167/180 (92,8 %) |
| Consultas que responde **solo** la regla de lema | 18 (A 12 · B 3 · D 3) |
| Más cercanas a τ | A038, B038 y D023 («diablo» / «devil»): 0,4799, a 0,0001 de τ; hoy las salva la regla de lema |

**Decisión del usuario (2026-10-01):** mantener 0,48 **por margen** sobre la consulta de C más alta; 0,47 queda
registrado como primer τ sin FP en v3 y **no se adopta** (ganaría 2 consultas a costa de 0,0002 de margen).
**Aclaración de cifras:** la cifra «0,48 → 167/180 (92,8 %)» que aparece en la revisión 2 y en la pregunta
de ADR-021 sale de `scripts/calibrar_umbral.py` sobre `fragmentos_v2.jsonl` (PoC/revisión 2). Los informes y las
diapositivas citan **solo v3** y lo declaran. Fuente: `resumen_arnes.json`, `barrido_umbral.csv`,
`docs/13_BRECHAS_RUBRICA.md` §2.

## ADR-021 · Coincidencia exacta de lema como segunda vía de respaldo — Aceptada (2026-10-01) con condiciones

**Contexto.** El código base responde cuando el término depurado coincide exactamente con el lema de una
entrada del diccionario, aunque el coseno quede bajo τ (visto: «sol», 0,351). En la auditoría no produjo
ningún FP en C. No figura en RF-08 del Documento 0 (sí en el anexo del Doc. 5). **Propuesta original (2026-09-24).**
Aceptarla como segunda vía explícita: *respaldo = coseno ≥ τ **o** lema exacto*, con cuatro condiciones: (1) RF-08
la menciona; (2) la interfaz muestra «respaldo: entrada exacta del diccionario»; (3) prueba `@salvaguarda` con
0 FP en C; (4) M4 reporta cuántas respuestas llegan por esta vía.

**Decisión (usuario, 2026-10-01): ACEPTADA con las cinco condiciones de `13_BRECHAS_RUBRICA.md` §3**, que
amplían las cuatro originales y se implementan en el PR 3:

1. **Solo fragmentos lexicográficos** y solo si el término depurado es **un único lema**. Las consultas de varias
   palabras no la activan; prueba obligatoria: «banco de peces» no responde por el lema «banco».
2. **Normalización declarada y probada** de tildes y mayúsculas (p. ej. «cuanto» y «cuánto»), porque cambia qué
   consultas activan la regla.
3. **Entrada completa y literal** (depende de corregir D-4, truncado, en el PR 6); el generador recibe solo esa
   entrada y el `VerificadorFormaLiteral` se aplica igual.
4. **Rótulo visible** «respaldo: entrada exacta del diccionario», con la similitud (< τ) a la vista; nunca se
   presenta como respuesta por similitud.
5. **Reporte separado** en M4 y M15: respondidas por similitud y respondidas por lema. Se declara que la evidencia
   «0 FP en C» es **débil** para esta regla, porque ninguna de las 28 consultas de C es un lema. Las negativas
   que sí sean lemas (palabras funcionales o ambiguas usadas en otro sentido) **solo las formula el equipo**; los
   agentes no fabrican consultas de evaluación.

**Consecuencias.** RF-08, RN-01, HU-06 y la prueba `@salvaguarda` se alinean con esta regla (L-8 de
`09_LINEA_BASE_V2.md`); la propagación a `02_REQUERIMIENTOS.md` y `03_HISTORIAS_USUARIO.md` queda por hacer y
no modifica criterios Gherkin sin su cambio explícito. Con τ 0,48 la regla responde 18 consultas de A, B y D
que por similitud no pasarían (ADR-020, nota). **Fuente:** decisión del usuario del 2026-10-01 (texto del §8 de
`13_BRECHAS_RUBRICA.md`, transmitida por el orquestador).

## ADR-022 · Pasajes de prosa sin afirmación — Aceptada (línea base v2) con condiciones

**Decisión.** Ante material de prosa, el sistema no afirma: entrega pasajes literales y citados si
comparten ≥ 2 palabras de contenido con la consulta depurada (piso de similitud 0,12). **Condiciones:** se
cuenta como **abstención** en todas las métricas; la interfaz lo rotula «no es una respuesta»; el
conjunto de prosa (60 + 135) es sintético y así se declara; HU-06 incorpora el escenario.

## ADR-023 · Tabla EN→ES de lemas en tiempo de compilación — Aceptada (línea base v2) con condiciones

**Decisión.** La consulta en inglés se traduce con una tabla de los 2 257 lemas del corpus generada por el
SLM en tiempo de compilación; se muestran todas las lecturas. Funciona sin modelo (requisito del móvil).
**Condiciones:** el resultado en D se declara **techo** (consultas y tabla derivan de los mismos lemas);
se revisan los errores conocidos; se añade, cuando exista, un conjunto de consultas en inglés formuladas
de forma independiente. `OllamaTraductor` puede conservarse en escritorio como estrategia alternativa.

## ADR-024 · Sin OCR — Aceptada (línea base v2)

**Decisión.** No se incorpora Tesseract. Las páginas sin capa de texto se señalan; un reparador une los
acentos separados por la extracción (70,6 % de los fragmentos de prosa, cifra a verificar en M1).
Limitación declarada: de 1 135 fragmentos de prosa, 723 son castellano legible.

## ADR-025 · React + Vite sobre FastAPI — Aceptada (línea base v2)

**Decisión.** Sustituye a Streamlit porque la asignatura evalúa la integración front-end ↔ back-end.
**Condición:** endurecer la interfaz actual, que es un prototipo (p. ej. aumenta el tamaño de texto pero no
lo reduce), según la lista de `CONSIDERACIONES.md` §5 (PR 7).

## ADR-026 · Sin modelo generador en el móvil — Aceptada (línea base v2) · revisión abierta

**Decisión vigente.** Plantilla determinista sobre la entrada extraída (180/180 en A+B; cubre el 90,2 % de
los fragmentos lexicográficos). **Revisión abierta** para el PMV3: «modo enriquecido» opcional con un
modelo de 4B solo en dispositivos que lo soporten, con verificador de forma literal, prueba de fidelidad
ampliada (≥ 60 casos) y descarga separada del modelo. Ver `09_LINEA_BASE_V2.md` §4. **Decide:** usuario,
en el Planning del PMV3.

## ADR-027 · SQLite en los tres PMV — Propuesta

**Propuesta.** `RepositorioConsultasPort` con adaptador SQLite por defecto (escritorio y móvil) y
PostgreSQL como segundo adaptador opcional. El archivo SQLite del escritorio es además el conjunto de datos
de RF-14–16 (sujeto a ADR-013). El índice no se guarda en SQLite. **Condiciones de privacidad:** sin
identificadores, aviso en la interfaz y borrado del historial. **Decide:** usuario.

**Nota 2026-10-01.** El usuario no expresó preferencia el 2026-10-01. Propuesta del orquestador: SQLite por
defecto, PostgreSQL opcional como segundo adaptador (P2). **Sigue en propuesta; pendiente de confirmación antes
del PR 8.** Fuente: encargo del orquestador del 2026-10-01.

---

## ADR-030 · Escucha en 0.0.0.0 solo en la nube — Propuesta (Guía 11)

**Contexto.** Render enruta el tráfico HTTPS hacia el puerto que indica `$PORT`; un servicio que
escucha en `127.0.0.1` no recibe nada. En local, en cambio, escuchar en todas las interfaces
expone la API a la red del aula.

**Decisión.** `127.0.0.1` sigue siendo el valor por defecto en local (uvicorn, ejecutable, Vite).
Solo el `startCommand` de `render.yaml` usa `--host 0.0.0.0 --port $PORT`. No hay variable que lo
cambie en local: el cambio vive en la orden de arranque de la plataforma.

**Consecuencias.** Ningún cambio de comportamiento en E1. En la nube la exposición la limita
Render (solo HTTPS en el puerto asignado).

## ADR-031 · Corpus en PostgreSQL y Neon como base de staging — Propuesta (Guía 11)

**Contexto.** El disco de Render es efímero: el archivo `fragmentos_v3.jsonl` y lo que se
incorpora por HU-02 se perderían en cada redespliegue. La Guía 11 exige una base gestionada y
con los datos cargados.

**Decisión.** Nuevo adaptador `RepositorioCorpusPostgres` del puerto `RepositorioCorpusPort`
(tabla `fragmentos`, `db/postgres/esquema.sql`, idempotente), elegido con `CORPUS_ORIGEN=postgres`
(por defecto `jsonl`). Conexión por `DATABASE_URL` (TLS obligatorio, *pooling* de Neon, sin
sentencias preparadas persistentes). Neon (plan gratuito, AWS us-east-1) como base de staging:
editor SQL y vista de tablas en el navegador, sin expiración a los 30 días. La siembra la hace
`scripts/sembrar_nube.py`. El dominio no cambia (lo verifica la prueba de arquitectura).

**Consecuencias.** Los PDF incorporados en la nube persisten como fragmentos, no como archivos.
Con `CORPUS_ORIGEN=postgres` y sin base, el servicio no arranca (fallo visible, no un índice
vacío en silencio).

## ADR-032 · Redacción con Gemini en la nube, extractivo como respaldo — Propuesta (Guía 11)

**Contexto.** Ollama/Qwen necesita GPU y los planes gratuitos de CPU lo harían inutilizable. La
nube necesita un módulo de IA que responda.

**Decisión.** Adaptador `GeminiGenerador` (API REST con `httpx`, sin SDK) que **solo extrae**
`{forma, glosa}`; lo envuelve `GeneradorExtractivo`, de modo que pasa por el mismo
`VerificadorFormaLiteral` de ADR-028. Gemini no traduce (sigue la tabla, `TRADUCTOR=tabla`), no
produce formas quechuas y no se llama en una abstención. RN-06 y τ = 0,48 no cambian. Sin clave,
con error, con 429 o pasados 15 s se responde con el fragmento literal citado; la respuesta
indica «Redactado por: gemini | extractivo» y el motivo. Clave principal `GEMINI_API_KEY` como
secreto de Render; opcional BYOK por la cabecera `X-Gemini-Key`, solo en memoria de la pestaña, nunca
registrada.

**Excepción a RNF-06 (solo staging).** En la nube el texto de la consulta y los fragmentos
recuperados se envían a la API de Google para la extracción; no se envían datos personales (la
consulta no lleva identificadores, ADR-027). La interfaz muestra el aviso. Base legal de referencia:
Ley 29733 (Protección de Datos Personales, Perú), que no aplica a datos no personales, y los
términos del plan gratuito de la API de Gemini (Google puede usar el contenido para mejorar sus
productos). E1 (local) sigue sin enviar nada fuera del equipo.

**Consecuencias.** Depende de la cuota gratuita, que es baja y variable; la medición frente a Qwen
declara el tamaño de muestra alcanzado.

## ADR-033 · Aviso de arranque en frío en la interfaz (REF-02) — Propuesta (S13, fase 1)

**Contexto.** En el plan gratuito, Render suspende el servicio tras 15 min sin tráfico. La U3 midió
un arranque en frío de 62–72 s (`docs/17` N-01) y el 2026-11-12 se midieron 72,65 s
(`docs_auditoria/evidencias/antes/salidas/arranque_estado_antes.txt`). Durante ese tiempo la
interfaz no avisaba de nada y, si fallaba, mostraba «Sin conexión con el servicio local», un texto
pensado para el escritorio (hallazgos U-01 y U-02 de `docs_auditoria/01_auditoria_furps.md`). La experta lo
registró como REF-02.

**Decisión.** Si `/api/estado` o una consulta tardan más de 4 s, la interfaz muestra un aviso
`role="status"`: el servicio se está activando y la primera respuesta puede tardar hasta un minuto.
Si la API es remota (`VITE_API_URL` definido), los errores de red lo explican y el estado inicial
ofrece «Reintentar». En local los errores conservan su texto de escritorio y, si una
consulta tarda más de 4 s (p. ej. Qwen en CPU), el aviso dice que el modelo puede estar cargándose.
No se toca la API.

**Consecuencias.** El aviso no acelera el arranque: solo lo explica. La reducción real del tiempo
es ADR-034. En la web, una consulta lenta con el servicio ya despierto (p. ej. Gemini con 429)
también se atribuye a la activación: es una simplificación aceptada (OBS-02 de `docs_auditoria/03_auditoria_implementacion_furps.md`).

## ADR-034 · Ruta de vida sin base para el ping programado (REF-01) — Propuesta (S13, fase 1)

**Contexto.** REF-01 propone mantener despierto el servicio con un ping programado. El PR #22
(abierto por otro integrante) lo implementa con `GET /api/estado` cada 10 min, 24/7. Hay dos
presupuestos en juego:
- **Render free:** 750 h de instancia al mes por *workspace*. Si se agotan, Render suspende todos
  los servicios free del *workspace* hasta el mes siguiente. Un servicio dormido no consume horas
  (<https://render.com/docs/free>, consultado el 2026-11-12). 24/7 son 720–744 h.
- **Neon free:** 100 CU-h al mes por proyecto y suspensión de la computación a los 5 min sin
  actividad (<https://neon.com/faqs/free-plan-limits-and-quotas>, consultado el 2026-11-12).
  `/api/estado` consulta la base, así que un ping cada 10 min tendría Neon activo cerca de la mitad
  del tiempo: ~360 h × 0,25 CU ≈ 90 CU-h, casi toda la cuota.

**Decisión.** Nueva ruta `GET /api/vivo` → `{"vivo": true}`, que no toca la base, el corpus ni
Gemini. El ping debe apuntar a ella, de modo que Render no se suspenda y Neon sí pueda hacerlo. Se
recomienda además limitar el ping a una franja horaria; por ejemplo, cron `*/10 11-23,0-4 * * *`
(UTC), que en Perú es de 06:00 a 23:59 y suma unas 560 h al mes. Así quedan unas 190 h de margen
en el *workspace*. El repositorio es público, de modo que los minutos de GitHub Actions no se
facturan. `/api/estado` sigue siendo la comprobación completa (`healthCheckPath`).

**Consecuencias.** La primera petición que llegue fuera de la franja seguirá pagando el arranque en
frío, y ADR-033 lo explica en la interfaz. Para fusionar el PR #22 con el cambio de ruta y de
franja hace falta una decisión del equipo (acción para personas).

## ADR-035 · Token de administración para las escrituras en modo nube — Propuesta (S13, fase 2)

**Contexto.** `docs_auditoria/04_auditoria_owasp.md` (OW-01, OW-02, OW-04, OW-16) demostró en local que cualquier
visitante podía incorporar un PDF al corpus, que pasaba a ser respaldo citado y rompía RN-06; también
podía falsificar fuentes y borrar el historial de todos. No existía autenticación para administrar.

**Decisión.** En modo nube (`ENTORNO` ≠ `local`), el middleware `EscrituraProtegida`
(`infrastructure/seguridad_nube.py`) exige la cabecera `X-Admin-Token`, comparada con
`hmac.compare_digest` contra `ADMIN_TOKEN`, en toda petición `/api/*` que no sea GET, HEAD u OPTIONS,
salvo `POST /api/consultas` y `POST /api/predicciones`. La protección es por defecto: una ruta de
escritura nueva queda protegida sin registrarla. Sin cabecera → 401. Token incorrecto o `ADMIN_TOKEN`
vacío → 403 (falla de forma segura). El token no se registra en la bitácora. La interfaz pide el token
en un campo (solo en memoria) o muestra «Modo solo lectura». En local no cambia nada.

**Consecuencias.** Acción para el dueño de Render: definir `ADMIN_TOKEN` (secreto, `sync: false`).
Mientras no lo haga, nadie puede administrar el corpus en la nube, ni siquiera el equipo.
`humo_nube.py` envía el token si existe la variable de entorno `ADMIN_TOKEN` del operador.

## ADR-036 · Historial por sesión en la nube; el del servidor, solo para el administrador — Propuesta (S13, fase 2)

**Contexto.** OW-03 y U-03: `GET /api/historial` mostraba a cualquiera las consultas de todos.

**Decisión.** En modo nube, `GET` y `DELETE /api/historial` exigen el token (ADR-035). La interfaz
pública muestra solo las consultas de la pestaña actual, guardadas en memoria; «Borrar» vacía esa
lista. El servidor sigue registrando las consultas sin datos personales, de modo que HU-09 no pierde
datos. En local, RF-11 sigue mostrando el historial de la base.

**Alternativas descartadas.** (a) Un identificador de sesión persistido en la base, que exige migrar
el esquema de Neon (base de otro integrante) y crea un dato persistente por visitante. (b) Retirar el
historial de la nube.

**Riesgo residual.** `GET /api/analitica/demanda` sigue siendo público, porque la Predicción ML no puede
cambiar para el público. Expone términos agregados sin respaldo, no consultas completas.

## ADR-037 · Límite de peticiones por IP sin dependencias — Propuesta (S13, fase 2)

**Contexto.** OW-08 y P-01: 60 consultas seguidas obtuvieron 60 respuestas 200, de modo que la cuota
compartida de Gemini se podía agotar.

**Decisión.** El middleware `LimitePeticiones` aplica una ventana deslizante de 60 s en memoria (un
solo proceso uvicorn) por IP y ruta: `POST /api/consultas` 20/min y `POST /api/predicciones` 60/min
(`LIMITE_CONSULTAS_POR_MINUTO` y `LIMITE_PREDICCIONES_POR_MINUTO`; 0 = desactivado). Solo se aplica en
modo nube. Al superarlo responde 429 con `Retry-After` y un mensaje en español. La IP se toma de
`CF-Connecting-IP` (Render sirve detrás de Cloudflare), luego de `X-Forwarded-For` y luego del
socket. Quedan exentas las corridas con un token de pruebas válido (`humo` y `carga`). Se guardan
como máximo 10 000 IP.

**Consecuencias.** Al reiniciar el servicio el contador se pierde, lo cual es aceptable. Si alguien
llegara al origen sin pasar por Cloudflare podría falsificar `CF-Connecting-IP` (riesgo residual
bajo). Detrás de un NAT, varios usuarios comparten el límite: 20/min sigue siendo holgado.

---

## ADR-038 · App móvil: cliente de la nube con respaldo sin conexión — Propuesta (PMV3, B0)

**Contexto.** El PMV3 se planificó como una app 100 % sin conexión (HU-10.x, ADR-019 y ADR-026): índice
léxico exportado, compositor determinista y ningún modelo en el teléfono. Después del PMV2 el sistema
desplegado (Render + Neon + Gemini) tiene funciones que el teléfono no puede reproducir: los dos
predictores ML (HU-08.1, RF-14 y RF-15), la redacción con Gemini y el registro de fuentes con entidad y
licencia. El usuario aclaró el alcance (B0): el modo principal es la nube y el sin conexión es el respaldo.

**Decisión.** La app `quechua-wanka-movil` cumple su único puerto (`AsistentePort`) con tres adaptadores:
`AsistenteNube` (cliente HTTP de los endpoints públicos de lectura: `POST /api/consultas`,
`POST /api/predicciones`, `GET /api/modelos`, `GET /api/fuentes`, `GET /api/estado`), `AsistenteLocal`
(el adaptador sin conexión ya existente, sin cambios en su lógica) y `AsistenteConmutado`, que compone
los dos y es el que inyecta el contenedor.

- **Automático** (por defecto): se pregunta a la nube; si no hay red, si no responde en 20 s o si
  devuelve un 5xx, contesta el corpus del teléfono y la respuesta lo declara. La consulta siguiente
  vuelve a intentar la nube.
- **Solo en línea** y **Solo sin conexión**: selector manual, guardado en SQLite.
- El modo activo se ve siempre en la cabecera («En línea · nube» / «Sin conexión · corpus local») y
  cada respuesta dice de qué modo vino.
- Un **429** no cambia de modo ni se reintenta: se muestra el mensaje del servidor y el botón
  «Reintentar» se habilita al cumplirse `Retry-After` (ADR-037).
- El aviso de arranque en frío usa el mismo texto y el mismo umbral (4 s) que la web (ADR-033).
- La app **no lleva** `ADMIN_TOKEN`, `TOKEN_PRUEBAS` ni claves de API, y no tiene funciones de
  administración (incorporar, editar o borrar fuentes, borrar el historial). Una prueba
  (`test/seguridad_test.dart`) lo comprueba sobre el código fuente.
- El historial es siempre el del teléfono (SQLite, con el modo de cada consulta): en la nube la
  lectura del historial del servidor exige el token (ADR-036).
- La URL de la API va en `--dart-define=API_URL` (por defecto, `https://quechua-api.onrender.com`).
- Paleta y logo de la web (B11).

**Consecuencias.**
- En línea, la consulta **sí sale del teléfono** (a Render y, para redactar, a Gemini); sin conexión,
  no. La interfaz lo hace visible y el artículo debe corregir la afirmación de privacidad (B8).
- Las dos vías no son idénticas: en línea el predictor puede **añadir** abstenciones (RN-06) y la
  redacción es de Gemini; sin conexión decide solo el umbral τ = 0,48 con la coincidencia de lema, y
  redacta el compositor determinista. La salvaguarda se conserva en ambas (0 FP en C medido en las dos).
- Las consultas que la app hace a la nube se registran con origen `usuario`, porque la app no puede
  llevar el token de pruebas. Las pruebas automatizadas de la app usan un doble de la API; las
  capturas contra la nube se limitaron a unas pocas consultas, anotadas en la bitácora.
- La dependencia nueva es solo de desarrollo (`flutter_launcher_icons`, para el ícono). La conectividad
  se infiere del propio fallo HTTP, sin paquetes de red adicionales.

## ADR-040 · REF-07: valoración «¿le sirvió esta respuesta?» sin datos personales — Propuesta (S14, P8)

**Contexto.** El experto temático pidió saber si las respuestas le sirven a quien consulta (REF-07).
HU-09 cuenta la demanda, pero no si la respuesta fue útil. La regla del proyecto es no guardar datos
personales (RNF de privacidad, ADR-036).

**Decisión.**
- Debajo de cada respuesta de la web, «¿Le sirvió esta respuesta?» con **Sí** y **No** (botones de
  44 px o más). No hay campo de texto libre, para que nadie escriba datos personales.
- `POST /api/valoraciones {consulta_id, util}` (201). Responde 404 si la consulta no existe, 409 si ya
  se valoró, 422 ante cualquier campo extra y 503 sin base de datos.
- Tabla nueva `valoraciones`: `consulta_id` (clave primaria y clave foránea a `consultas`, con borrado
  en cascada), `util` y `momento`. **Una valoración por consulta.** No guarda IP, texto ni comentario.
  `create_all()` la crea al arrancar, también en Neon: es una tabla nueva y no altera ninguna otra, así
  que no hace falta ejecutar SQL a mano.
- En la nube es **pública**, como la consulta (`POST_PUBLICOS`), con el mismo límite por minuto
  (ADR-037). El `consulta_id` es un UUID que solo recibe quien hizo la consulta.
- Puerto de entrada `ValorarRespuestaPort`, caso de uso `ValorarRespuestaUseCase` y puerto de salida
  `RepositorioValoracionesPort`, con un adaptador SQLAlchemy común a SQLite y PostgreSQL.
- **No cambia** la respuesta, τ, RN-06 ni el registro de HU-09. La app móvil v1.1.0 no la incluye.

**Consecuencias.**
- La utilidad percibida se puede medir con
  `SELECT util, COUNT(*) FROM valoraciones GROUP BY util`, o con `RepositorioValoracionesPort.resumen()`.
  Junto con el origen de HU-09, separa la de usuarios reales de la de las pruebas.
- Con pocas valoraciones, el dato es un indicio y no una métrica (igual que el SUS con n < 10).
- Para borrar las valoraciones basta con borrar la consulta (cascada). «Borrar todo el historial» las
  elimina también.

## ADR-041 · REF-08: «¿quiso escribir…?» ante erratas en la consulta en español, nunca en quechua — Propuesta (S14, P8)

**Contexto.** El experto temático pidió tolerar erratas (REF-08): «zoro» o «mujr» terminaban en una
abstención aunque «zorro» y «mujer» están en el diccionario. Corregir por cuenta propia podría hacer
que el sistema responda algo que no se preguntó (por ejemplo, «caza» por «casa») y, sobre todo, nunca
debe alterar una forma quechua.

**Decisión.**
- El sistema **no corrige**. Cuando se abstiene ante una consulta **en español**, propone hasta 3 lemas
  del diccionario («¿Quiso escribir…?») y la consulta reescrita con cada uno. Solo se consulta de nuevo
  si la persona elige una propuesta, y esa nueva consulta pasa por τ y la regla de lema como cualquier
  otra.
- **Candidatos:** solo los **lemas castellanos** (las palabras que encabezan las entradas:
  «ZORRO: Atuq.»), nunca el cuerpo con las formas quechuas. Distancia de edición con transposiciones
  de **1** si el término tiene hasta 5 letras y de **2** si tiene más. Desempate: misma primera letra y,
  luego, mayor frecuencia en el diccionario.
- **No se propone nada** cuando:
  - el término tiene menos de 4 letras o más de una palabra;
  - ya es un lema;
  - ya figura en el vocabulario del corpus (no es una errata; puede ser quechua);
  - tiene ortografía quechua (k, w, o q sin u);
  - la consulta es en inglés o se tradujo.
- Lógica pura en `domain/services/sugerencia_errata.py`. `IndiceRecuperacionPort.lemas_parecidos()` es
  no abstracto y por defecto no devuelve nada. Campo nuevo `sugerencias` en la respuesta.
- **No cambia:** la abstención, τ = 0,48, RN-06, el verificador, el registro de HU-09 ni el
  predictor. La app móvil v1.1.0 no lo incluye.

**Consecuencias.**
- 0 FP en C se mantiene por construcción: la decisión es la misma con o sin sugerencias. La suite con
  el corpus real (marcador `salvaguarda`) pasa entera.
- Puede proponer una palabra que no era la buscada («zoro» → «zorro» y «oro»). Por eso es una propuesta
  explícita y la interfaz aclara que son palabras en español parecidas a la escrita.

---

## Registro de cambios

| Fecha | Cambio |
|---|---|
| 2026-09-24 | Creación: ADR-001…008 trasladados de la serie documental; ADR-009…016 propuestos o abiertos |
| 2026-09-24 | Aceptadas ADR-009, 010, 011 y 015 por decisión del usuario; nuevas ADR-017 (aceptada) y ADR-018 (propuesta) |
| 2026-09-24 | Línea base v2: ADR-019, 020, 022–026 aceptadas; ADR-021 y 027 propuestas; ADR-004, 008 y 012 actualizadas |
| 2026-10-01 | **ADR-021 aceptada** con las cinco condiciones de `13_BRECHAS_RUBRICA.md` §3 (decisión del usuario). ADR-020: nota con la medición sobre `fragmentos_v3` y confirmación de τ 0,48 (no se reescribe el texto aceptado). ADR-013 y ADR-027: nota «sin preferencia del usuario; pendiente de confirmación antes del PR 8»; siguen abiertas y en propuesta |
| 2026-10-29 | Guía 11 (despliegue en la nube): ADR-030, 031 y 032 propuestas en la rama `feat/despliegue-nube` |
| 2026-11-12 | S13 fase 1 (FURPS+): ADR-033 (aviso de arranque en frío, REF-02) y ADR-034 (`/api/vivo` y presupuesto de horas del ping, REF-01) propuestas en `s13/furps-owasp` |
| 2026-11-12 | S13 fase 2 (OWASP): ADR-035 (token de administración), ADR-036 (historial por sesión) y ADR-037 (límite de peticiones) propuestas en `s13/owasp` |
| 2026-11-19 | PMV3 (B0): ADR-038 propuesta (app móvil: cliente de la nube con respaldo sin conexión) en `feat/pmv3-app-movil` |
| 2026-11-24 | S14 ronda 2 (P8): ADR-040 propuesta (REF-07, valoración «¿le sirvió?» sin datos personales) en `feat/p8-ref-05-07-08` |
| 2026-11-24 | S14 ronda 2 (P8): ADR-041 propuesta (REF-08, «¿quiso escribir…?» ante erratas en español, nunca en quechua) en `feat/p8-ref-05-07-08` |
