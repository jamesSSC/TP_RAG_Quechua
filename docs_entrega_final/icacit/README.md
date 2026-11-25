# B10 · Evidencias para el reporte de cumplimiento ICACIT

Atiende la consigna `S14. Evaluación de evidencias de ICACIT.docx`: un reporte de cumplimiento de 7
competencias (Conocimientos de Ingeniería, Medioambiente y Sostenibilidad, El Ingeniero y la Sociedad,
Gestión de Proyectos, Diseño y Desarrollo de Soluciones, Análisis de Problemas y Uso de Herramientas
Modernas), con hallazgos y mejoras por atributo y la sección del informe donde va cada uno.

**Matriz por competencia: `matriz_competencias.md`.** Los 6 puntos del bloque B10 están abajo. La guía pide `./docs`; se usó `./docs_entrega_final`.

Cada cifra viene con el comando que la produjo.

## 1. Energía (medioambiente y ciencias naturales)

- **Medido:** potencia real de la GPU (RTX 4060 Ti) con `nvidia-smi` cada 100 ms durante **248**
  consultas locales con Qwen3.5 4B.
  - Reposo: 19,7 W.
  - **Respuesta: 44,2 J** de media (n = 220).
  - **Abstención: 0,07 J** (n = 28).
  - Comando: `python scripts/medir_latencia_energia.py http://127.0.0.1:8000 … --energia`.
  - Datos: `../metricas/evidencias/latencia_local_qwen_gpu.{json,csv}`.
- **Abstenciones del ML sobre el conjunto de pruebas: 0 %** con el corte vigente 0,25. El modelo no
  retiró ninguna respuesta (`backend/modelos/metricas.json → compuerta_rn06`), así que **el ML no
  ahorra energía en este conjunto**. El ahorro viene de las abstenciones por τ: 28 × ≈ 44 J ≈ 1,24 kJ
  por pasada del conjunto.
- **Nube y móvil:** solo hay datos medidos de latencia y tamaño (`../metricas/metricas_ml_final.md` §4).
  La estimación de la energía de Render, Neon y Gemini con fuentes publicadas la hace Omar.

## 2. Optimización y simulación (conocimientos)

- τ formulado como «maximizar la cobertura sujeto a FP = 0».
  - Barrido en `../metricas/evidencias/barrido_tau.csv` y figura `barrido_tau.png`.
  - τ factible mínimo 0,47; vigente 0,48.
- Bootstrap de 1 000 remuestreos del AUC con su IC 95 %, y cota exacta de la tasa de FP:
  `../metricas/metricas_ml_final.md` §1 y §2 (no se duplica).

## 3. Registro de cambios (gestión, G-01)

`cambios.md`.

## 4. Control del avance (gestión, G-02)

Los datos de Git (`main` = `8088193`) están en:

- `avance_commits_por_semana.csv`
- `avance_pr.csv` (27 PR con fecha de creación y de fusión)
- `avance_commits.png` (barras por integrante y flujo acumulado)

| Semana ISO | Omar Terbullino | James Saenz | Yeferson Serpa | Total |
|---|---|---|---|---|
| 2026-S39 | 1 | 16 | 0 | 17 |
| 2026-S40 | 15 | 0 | 0 | 15 |
| 2026-S44 | 75 | 7 | 0 | 82 |
| 2026-S46 | 23 | 0 | 0 | 23 |

- **Observación:** Yeferson Serpa no figura como autor de commits en `main`. Si trabajó en ramas
  propias, en Trello o en diseño, conviene declararlo en el informe con su propia evidencia.
- **Fuera de este conteo:** los commits de esta entrega (19–20/11, ramas de James aún sin fusionar).
- **HU cerradas por sprint y duración de cada sprint** (del tablero de Trello exportado el 20/11; 68
  tarjetas y 498 acciones). Datos en `avance_sprints.csv` y gráfico en `burndown_sprints.png`:

  | Sprint | Fechas (Trello) | Días | Ítems | En DONE |
  |---|---|---|---|---|
  | Sprint 1 · PMV1 | 21/09 – 12/10 | 21 | HU-01 a HU-07 | 7/7 |
  | Sprint 2 · PMV2 + nube | 12/10 – 06/11 | 25 | HU-08.1, HU-08.2, HU-09, RF-15 | 4/4 |
  | Sprint S13 · calidad y seguridad | 09/11 – 13/11 | 4 | RM-01 a RM-04, M-01 a M-08 y entregables 01–07 | 7 (RM-05 a RM-08 parciales, en QA-TESTING) |
  | Sprint 3 · PMV3 | 06/11 – 14/12 | 38 | HU-10.1 a HU-10.3, HU-11 | 0 en Trello. Hechas en el emulador el 19–20/11: moverlas con `../kanban/tarjetas_pmv3.md` |

- **Acciones en Trello por semana e integrante:** `avance_trello_por_semana.csv`. Totales: Omar 453,
  Yeferson 28 y James 14.
- **Discrepancia:** Trello fija **WIP = 3** («una tarjeta por integrante») y `docs/05_KANBAN.md:20` dice
  WIP 1. Hay que unificarlo en el informe (ver `../cifras_oficiales.md`, C-07).

## 5. Herramientas (H-01, H-02)

`herramientas.md`: lista con la versión real de cada herramienta y la captura disponible de cada una.

## 6. Datos que salen en la nube (sociedad, S-01)

`datos_nube.md`.
