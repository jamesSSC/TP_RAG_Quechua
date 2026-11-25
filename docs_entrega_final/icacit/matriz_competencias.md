# Matriz de evidencias por competencia ICACIT 2025

Insumo para el **reporte de cumplimiento ICACIT** (anexo C del informe). La consigna, `S14. Evaluación
de evidencias de ICACIT.docx`, pide: «Como evaluador de ICACIT, elaborar reporte de cumplimiento
tomando el informe de proyecto adjunto de los atributos de graduado ICACIT 2025 para las siguientes
competencias […]. Mostrar los hallazgos y mejoras a realizar ordenado por atributo del graduado y qué
sección del informe se recomienda colocar».

**Alcance de este documento.** El informe Word de 122 páginas no está en el repositorio, así que esto
**no** evalúa su redacción. Para cada competencia indica:

- qué **evidencia verificable existe hoy** en el repositorio;
- qué **hallazgo** (fortaleza o brecha) se desprende de ella;
- qué **mejora** falta;
- en qué **sección del informe** (numeración de `03_ESTRUCTURA_INFORME_S14.md`) se recomienda colocarla.

El reporte final lo redacta el equipo, cruzando esta matriz con el texto del informe.

---

## Competencias transversales

### 1. Conocimientos de Ingeniería

| | |
|---|---|
| **Evidencia** | TF-IDF y coseno (`indice_hibrido_lexico.py:75-136`); regresión logística con validación cruzada k = 5 e IC 95 % por bootstrap (`metricas/metricas_ml_final.md`); τ formulado como optimización con restricción («maximizar la cobertura sujeto a FP = 0», barrido en `metricas/evidencias/barrido_tau.csv`); cota exacta de Clopper-Pearson; BM25 como línea base; energía calculada como integral de la potencia medida (`medir_latencia_energia.py`) |
| **Hallazgos** | **Fortaleza:** cada concepto matemático está aplicado y medido, no solo citado, y se verificó en una muestra independiente (F, 107; 0 FP). **Brecha:** no hay reglas fonológicas ni morfológicas del quechua en el código; si el informe las menciona como aplicadas, es una afirmación sin respaldo |
| **Mejora** | Presentar τ como problema de optimización con su gráfico; tabla área → concepto → `ruta:línea` (`informe_final/insumos.md` §II); declarar la fonología como limitación |
| **Sección** | **II. Conocimientos de ingeniería** (tabla y matriz AG-I07) y 8.8 |

### 2. Medioambiente y Sostenibilidad

| | |
|---|---|
| **Evidencia** | Potencia de la GPU **medida**: 44,2 J por respuesta y 0,07 J por abstención (`metricas/evidencias/latencia_local_qwen_gpu.json`); APK de 22,6 MB que funciona sin red; keep-alive rechazado por consumo (PR #22, ≈ 90 de 100 CU-h de Neon) |
| **Hallazgos** | **Fortaleza:** el dato energético está medido, no estimado, y muestra que abstenerse cuesta casi 0. **Brecha:** el ML no añade abstenciones en el conjunto de evaluación (corte 0,25), así que no se le puede atribuir ahorro energético. Falta la energía de la nube (Render, Neon, Gemini) |
| **Mejora** | Estimar el CO₂e por modo (local, nube y teléfono) con fuentes publicadas, separado de lo medido; vincular el proyecto a un ODS (4 o 10) con un indicador; redactar el plan de sostenibilidad (operación sin conexión en zonas sin cobertura) |
| **Sección** | **III. Ingeniero y sociedad** (justificación ambiental y sostenibilidad); resumen ejecutivo (ODS) |

### 3. El Ingeniero y la Sociedad

| | |
|---|---|
| **Evidencia** | Tabla de privacidad por modo (`articulo/insumos_pmv3.md` §2); datos que salen a la nube por campo y tabla (`icacit/datos_nube.md`); alcance declarado («no es autoridad lingüística»); principios CARE y la salvaguarda de abstención (0 FP en el dispositivo y en la nube); acontecimientos tecnológicos con fecha y commit (`informe_final/insumos.md` §III) |
| **Hallazgos** | **Fortaleza:** la app declara siempre si la consulta salió del teléfono. **Brecha 1:** el informe anterior afirmaba «la consulta nunca sale del dispositivo»; solo es cierto sin conexión. **Brecha 2:** licencias de las fuentes «pendiente de verificar (ADR-015)» (H-16, visible en la pestaña Fuentes). **Brecha 3:** sin validación de hablantes de la comunidad |
| **Mejora** | Corregir la afirmación de privacidad; escribir un párrafo legal de la operación en la nube (Gemini, Neon en EE. UU.); completar las licencias; anotar las lecciones para la práctica profesional |
| **Sección** | **III** (marco legal, salud y seguridad, interesados) y **IX. Lecciones aprendidas** |

### 4. Gestión de Proyectos

| | |
|---|---|
| **Evidencia** | Trello exportado: sprints S1 21/09–12/10 (7 HU), S2 12/10–06/11 (4), S13 09/11–13/11 (7 tareas), S3 06/11–14/12 (4 HU) (`icacit/avance_sprints.csv`); burndown (`icacit/burndown_sprints.png`); 14 cambios gestionados con decisión y evidencia (`icacit/cambios.md`); commits y PR por semana e integrante (`avance_*.csv`); bitácora del PMV3; 27 PR más 6 de esta entrega |
| **Hallazgos** | **Fortaleza:** la trazabilidad del cambio (de denso a léxico, retiro de Gemini 2.5, keep-alive rechazado) está documentada con PR y fecha. **Brecha 1:** WIP distinto entre `docs/05_KANBAN.md` (1) y Trello (3). **Brecha 2:** participación desigual en las herramientas: Yeferson no tiene commits en `main` (28 acciones en Trello) y James tiene 14 acciones en Trello (23 commits y 4 PR antes de esta entrega). **Brecha 3:** las HU del PMV3 siguen en el Product Backlog de Trello aunque están hechas en el emulador |
| **Mejora** | Mover las HU-10.x y HU-11 en Trello (`kanban/tarjetas_pmv3.md`); unificar el WIP; Gantt ejecutado hasta el PMV3; costo real frente a la línea base; declarar quién hizo qué, incluido el uso de asistentes de IA |
| **Sección** | **VII. Gestión del proyecto** (7.3 Scrum, 7.4 Kanban, 7.5 Gantt, 7.9 indicadores, **7.10 Gestión de cambios**) |

## Competencias específicas

### 5. Diseño y Desarrollo de Soluciones

| | |
|---|---|
| **Evidencia** | Arquitectura hexagonal verificada por pruebas (4/4) y UML v1.1 contrastados con el código (`docs_ingenieria_inversa/`); app en dos modos con un solo puerto y tres adaptadores (ADR-038); paridad del índice móvil y el backend byte a byte; 416 pytest, 48 Vitest y 45 Flutter; CI en Ubuntu; FURPS+ 7,6 y OWASP 82 (`docs_auditoria/08`); restricción → decisión → verificación en ADR-019 a ADR-038 |
| **Hallazgos** | **Fortaleza:** las decisiones de diseño se validaron con datos. Por ejemplo, BM25 frente a E4 mostró que la capa de lema aporta el 100 % (B3 §3), y la auditoría delta encontró un defecto real (APK sin INTERNET) antes de entregar. **Brecha:** la medición en el teléfono físico ARM64 está pendiente; las cifras del PMV3 son de emulador |
| **Mejora** | Incluir la vista de despliegue (`poster/figuras/despliegue_poster.png`) y la de componentes; medir en el teléfono físico; añadir la tabla de requisitos con el valor medido en los tres entornos |
| **Sección** | **VI. Diseño de ingeniería** (6.1 a 6.4) y **VIII** (8.7 PMV3, 8.9 FURPS+/OWASP, 8.10 ingeniería inversa) |

### 6. Análisis de Problemas

| | |
|---|---|
| **Evidencia** | Problema y PoC (Documentos 0 y 6): denso 0,65 frente a léxico 1,00 en recall@5; árbol de problemas y cinco porqués (`docs/diagramas/v_5porques.py`); trazabilidad problema → HU → prueba (Gherkin en `docs/03`); diagnóstico del arranque en frío (62–72 s) con su solución en dos capas (aviso y respaldo sin conexión) |
| **Hallazgos** | **Fortaleza:** el análisis cambió el diseño, de denso a léxico y del modelo en el teléfono al compositor determinista, a partir de mediciones. **Brecha:** las restricciones del problema siguen redactadas para el modo «solo local»; con el PMV3 deben separarse por modo (en línea o sin conexión) |
| **Mejora** | Reescribir 1.2 con restricciones por modo; agregar el OE del PMV3 con su métrica; mantener la trazabilidad problema → objetivo → requisito → prueba |
| **Sección** | **I. Análisis de problemas** (1.2 y 1.4) |

### 7. Uso de Herramientas Modernas

| | |
|---|---|
| **Evidencia** | Herramientas con su versión real y el PMV en que entran (`icacit/herramientas.md`, `poster/herramientas_por_pmv.md`); CI con ruff, Bandit, pip-audit, oxlint, `npm audit` y Vitest; Playwright para capturas y para probar la CSP; emulador de Android Studio con arnés de integración; Flutter, Render, Neon, Gemini y Ollama |
| **Hallazgos** | **Fortaleza:** cada herramienta tiene un resultado medido asociado. **Brecha 1:** faltan las capturas de los paneles de Render y Neon (cuentas de otro integrante). **Brecha 2:** no hay ZAP contra la nube ni escaneo activo (solo pasivo local) |
| **Mejora** | Una captura por herramienta, sin secretos; criterio de selección de cada una; declarar el uso de asistentes de IA y su límite (revisión humana) |
| **Sección** | **V. Uso de herramientas modernas** (tabla con versión, uso, resultado y limitación) y IV (técnicas) |

---

## Resumen para el anexo C

| Competencia | Nivel de evidencia hoy | Lo más urgente | Sección |
|---|---|---|---|
| Conocimientos de Ingeniería | Alto | Tabla con `ruta:línea` y τ como optimización | II |
| Medioambiente y Sostenibilidad | Medio | CO₂e por modo, ODS con indicador | III |
| El Ingeniero y la Sociedad | Medio | Corregir la privacidad por modo; licencias (H-16) | III, IX |
| Gestión de Proyectos | Alto | Mover el PMV3 en Trello; unificar el WIP; Gantt ejecutado | VII |
| Diseño y Desarrollo de Soluciones | Alto | Medir en el teléfono físico | VI, VIII |
| Análisis de Problemas | Alto | Restricciones por modo y OE del PMV3 | I |
| Uso de Herramientas Modernas | Medio-alto | Capturas de Render y Neon | V |
