# B12 · Resultados por unidad del sílabo (cuadrantes del póster)

Las 3 a 5 cifras más fuertes de cada unidad, ordenadas según los ejes temáticos de
`ESPEC_POSTER_A0.md`. La fuente de cada cifra es `../cifras_oficiales.md` (código C-xx) u otra ruta
indicada. Una cifra **(cotejar)** viene del informe actual y no se volvió a medir en esta entrega: hay
que confirmarla antes de imprimir.

## U1 · Iniciación y planificación

Ejes: idea y alcance, requisitos, arquitectura, PMV, planificación y PoC.

| Cifra | Fuente |
|---|---|
| Arquitectura **hexagonal** elegida por factores ponderados: **4,65** sobre 5 | `docs/diagramas/v_tecnologica.py` (matriz ponderada) |
| PoC: híbrido léxico **recall@5 = 1,000** frente a denso 0,650 | Documento 6; `docs/07_DECISIONES.md` (ADR-019/020) |
| τ sin falsos positivos desde la PoC; hoy **τ = 0,48**, 0 FP en C y en F (107) | C-09, C-18 |
| 16 RF / 12 RNF y 11 épicas; plan en 3 PMV | **(cotejar)** `docs/02_REQUERIMIENTOS.md` |

Figura sugerida: `figuras/barrido_tau_poster.png`.

## U2 · Diseño y construcción (PMV1)

Ejes: interfaces y BD, costos, responsabilidades, hitos y PMV1.

| Cifra | Fuente |
|---|---|
| PMV1: recall@5 **1,000** en A y B; **0 FP** en C | C-15 |
| **100 %** de las respuestas con documento y página (RN-03 en el dominio) | `backend/src/domain/entities/respuesta.py`; UML `ii_01_clases` |
| Hexagonal: **17 puertos** (7 de entrada y 10 de salida), **8 casos de uso** y 4/4 pruebas de arquitectura | C-04, C-05 |
| Línea base de costos S/ 497,01 (presupuesto S/ 546,71) | **(cotejar)** informe U2 |
| Latencia local con Qwen 4B en GPU: **P50 2,74 s** (P95 2,83 s) | C-22 |

Figura sugerida: captura de una respuesta con cita (`../logo/B11_web_local_despues_con_logo.png`).

## U3 · Gestión del proyecto (PMV2)

Ejes: control de hitos, gestión de cambios y PMV2.

| Cifra | Fuente |
|---|---|
| Predictor 1 (cobertura): **AUC 0,996** (IC 95 % 0,993–0,999) | C-19 |
| Predictor 2 (pasajes): **AUC 0,980**; pasajes ante preguntas no cubiertas **45,8 % → 9,3 %** | C-20; README del repositorio (PMV2) |
| Despliegue en **Render + Neon** con 3 605 fragmentos y 8 documentos | C-08 |
| **14 cambios** gestionados, entre ellos: de denso a léxico, retiro de Gemini 2.5 (PR #18) y keep-alive rechazado (PR #22) | `../icacit/cambios.md` |

Figura sugerida: `figuras/roc_predictores_poster.png` o `figuras/despliegue_poster.png`.

## U4 · Aseguramiento de la calidad (PMV3)

Ejes: criterios de calidad, definición de pruebas, resultados e interpretación, y PMV3.

| Cifra | Fuente |
|---|---|
| **FURPS+ 6,9 → 7,4 → 7,6** · **OWASP 61 → 79 → 82** | C-29, C-30 |
| Pruebas: **416** pytest · **48** Vitest · **45** Flutter; CI en verde con ruff, Bandit y `npm audit` | C-12 a C-14 |
| PMV3 en el dispositivo, sin red: **248** consultas, **0 FP**, P50 **0,80 ms**; APK de **22,6 MB** | C-16, C-26, C-27 |
| Energía de GPU: **44 J** por respuesta frente a **0,07 J** por abstención | C-28 |
| SUS de la prueba con usuarios: **por medir** | `../pruebas_usuarios/` |

Figura sugerida: `figuras/histograma_latencias_poster.png` o la captura de la app en modo avión
(`docs/evidencias/pmv3/movil/HU-10.1_movil_modo_avion_cambio_automatico.png`).
