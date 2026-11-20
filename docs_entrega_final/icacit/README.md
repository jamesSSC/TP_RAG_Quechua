# B10 · Evidencias para el reporte de cumplimiento ICACIT

Atiende `Reporte_Cumplimiento_ICACIT_2025.pdf`. **Ese PDF no vino en el paquete**: este índice sigue los
6 puntos que enumera el bloque B10 del prompt. La guía pide `./docs`; se usó `./docs_entrega_final`.

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
- **HU cerradas por sprint y duración de cada sprint:** salen de Trello (`docs/04_SPRINTS.md` usa otra
  numeración). **Por confirmar** con el tablero; las fechas de Trello que da el paquete son S1 21/09–11/10,
  S2 12/10–05/11, S13 09/11–12/11 y S3 06/11–13/12.

## 5. Herramientas (H-01, H-02)

`herramientas.md`: lista con la versión real de cada herramienta y la captura disponible de cada una.

## 6. Datos que salen en la nube (sociedad, S-01)

`datos_nube.md`.
