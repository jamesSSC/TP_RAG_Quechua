# 04 · Plan de sprints por PMV

> Calendario, objetivos, compromiso y resultados de cada sprint. Las historias **entran** al tablero
> (`05_KANBAN.md`) desde aquí en el Sprint Planning y **salen** en la Sprint Review; cada movimiento se
> anota con fecha en ambos archivos.
>
> Mantenido por: **archivista** · Las fechas y los resultados solo se modifican con evidencia · Última
> revisión: 2026-11-24 · Versión 1.2 (§1.4: ejecución real según Trello)

---

## 1. Marco (Documento 4)

- **Scrum** con cuatro sprints de **tres semanas**, cerrando en frontera de PMV, y **límite de trabajo en
  curso** tomado de Kanban.
- **Punto de control** a mitad de cada sprint.
- **Alcance:** el plazo es inamovible; si hace falta, se posponen o reducen historias de prioridad media
  (HU-04, HU-05, HU-09, HU-11), nunca las de prioridad alta.
- **DoD-4** (salvaguarda) se verifica en todos los incrementos.
- **Resultados:** se registran «por registrar» hasta que exista una medición.

### 1.1 Calendario — confirmado el 2026-09-24

El usuario confirmó que **la semana del 2026-09-21 es la semana 1 del desarrollo del PMV1**. La
preparación del entorno (HT-00) no es una iteración aparte: se ejecuta **dentro del sprint 1** y consume
parte de su capacidad, lo que se tiene en cuenta en el compromiso del §3.

| Semana | Del | Al | Sprint |
|---|---|---|---|
| 1 | 2026-09-21 | 2026-09-27 | Sprint 1 · arranque y HT-00 |
| 2 | 2026-09-28 | 2026-10-04 | Sprint 1 |
| 3 | 2026-10-05 | 2026-10-11 | Sprint 1 |
| 4 | 2026-10-12 | 2026-10-18 | Sprint 2 |
| 5 | 2026-10-19 | 2026-10-25 | Sprint 2 |
| 6 | 2026-10-26 | 2026-11-01 | Sprint 2 · **Hito 1** |
| 7 | 2026-11-02 | 2026-11-08 | Sprint 3 |
| 8 | 2026-11-09 | 2026-11-15 | Sprint 3 |
| 9 | 2026-11-16 | 2026-11-22 | Sprint 3 · **Hito 2** |
| 10 | 2026-11-23 | 2026-11-29 | Sprint 4 |
| 11 | 2026-11-30 | 2026-12-06 | Sprint 4 |
| 12 | 2026-12-07 | 2026-12-13 | Sprint 4 · **Hito 3** |

### 1.2 Resumen

| Sprint | Fechas | PMV | Objetivo | Estado |
|---|---|---|---|---|
| Sprint 1 | 2026-09-21 → 2026-10-11 | PMV1 | Entorno operativo; corpus indexado y consultable, con procedencia y arnés de evaluación | Cerrado (ver §1.4) |
| Sprint 2 | 2026-10-12 → 2026-11-01 | PMV1 | Flujo de consulta completo con traducción, trazabilidad y abstención · Hito 1 | Cerrado (ver §1.4) |
| Sprint 3 | 2026-11-02 → 2026-11-22 | PMV2 | Analítica predictiva y artefactos móviles equivalentes · Hito 2 | Cerrado (ver §1.4) |
| Sprint 4 | 2026-11-23 → 2026-12-13 | PMV3 | Aplicación móvil sin conexión validada en dispositivo · Hito 3 | En curso: en Trello es el **Sprint 3, 06/11 → 13/12** (§1.4) |

### 1.4 Ejecución real según Trello (alineado el 2026-11-24)

El plan de arriba tenía cuatro sprints de tres semanas. En el tablero de Trello (exportado el 20/11: 68
tarjetas y 498 acciones, `docs_entrega_final/icacit/avance_sprints.csv`) el trabajo quedó en **tres
sprints**, más uno corto de calidad y seguridad (S13). Las fechas oficiales del informe son las de Trello:

| Sprint (Trello) | Fechas | PMV | Ítems | Estado |
|---|---|---|---|---|
| Sprint 1 · PMV1 | 2026-09-21 → 2026-10-12 | PMV1 | HU-01 a HU-07 | Cerrado: 7/7 en DONE |
| Sprint 2 · PMV2 + nube | 2026-10-12 → 2026-11-06 | PMV2 | HU-08.1, HU-08.2, HU-09, RF-15 | Cerrado: 4/4 en DONE |
| Sprint S13 · calidad y seguridad | 2026-11-09 → 2026-11-13 | — | RM-01 a RM-04, M-01 a M-08, entregables 01–07 | Cerrado (RM-05 a RM-08 parciales) |
| **Sprint 3 · PMV3** | **2026-11-06 → 2026-12-13** | PMV3 | HU-10.1, HU-10.2, HU-10.3, HU-11 | En curso: las 4 HU hechas en el emulador el 19–20/11; faltan el teléfono físico y la prueba con usuarios |

El export de Trello termina el Sprint 3 el 14/12. El cierre se fija en el **13/12**, el día del Hito 3,
que es la fecha acordada en el equipo. El PMV3 está registrado en §6 como «Sprint 4», el nombre del
plan original.

### 1.3 Ceremonias adaptadas al trabajo con agentes

| Ceremonia | Cuándo | Quién | Salida |
|---|---|---|---|
| Sprint Planning | Lunes de la semana 1 del sprint | Usuario + orquestador | Compromiso del sprint; specs a redactar; el archivista mueve tarjetas a «Listo» |
| Sesión de trabajo | Cada sesión de Claude Code | Orquestador + subagentes | Tarjetas movidas; entrada en el registro de §7 |
| Punto de control | Jueves de la semana 2 | Usuario + orquestador | Riesgo del compromiso; repriorización si hace falta |
| Sprint Review | Domingo de la semana 3 | Usuario + orquestador | Demostración, DoD verificada, resultados medidos |
| Retrospectiva | Tras la revisión | Usuario + orquestador | ≥ 1 acción de mejora para el sprint siguiente (también sobre las instrucciones de los agentes) |

---

## 2. Arranque del sprint 1 (semana 1) · HT-00

**Objetivo.** Que un PR de prueba recorra el circuito completo: especificación → rama → pruebas →
auditoría → revisión humana → fusión → actualización del tablero.

| Tarea | Responsable | Estado |
|---|---|---|
| Crear `SDD_RAG_Quechua/docs` con la documentación base | Orquestador | Hecho (2026-09-24) |
| Decidir calendario, SonarQube, repositorio y servidor MCP | Usuario | Hecho (2026-09-24) |
| `CLAUDE.md`, `.claude/agents/*`, `.claude/settings.json`, `.mcp.json`, `.gitignore`, `sonar-project.properties` | Orquestador | Hecho (2026-09-24) |
| Copia del corpus en `corpus/pdf/` con `MANIFIESTO.yaml` y del material de la PoC en `referencia_poc/` | Orquestador | Hecho (2026-09-24) |
| Revisar y aprobar la documentación y la configuración | **Usuario** | Pendiente |
| Completar en el manifiesto las licencias y fuentes «por registrar» | **Usuario** | Pendiente |
| Crear el repositorio privado en GitHub y hacer el primer commit de esta carpeta | **Usuario** (o programador con `gh`) | Pendiente |
| Crear tokens de SonarQube Cloud y local; definir las variables de entorno | **Usuario** | Pendiente |
| Esqueleto hexagonal con `uv`, prueba de arquitectura y comandos del `CLAUDE.md` §9 | Programador | Pendiente |
| Integración continua: `ruff`, `mypy`, `pytest --cov`, `pip-audit`, análisis de SonarQube Cloud | Programador + auditor | Pendiente |
| PR de prueba de extremo a extremo | Todos | Pendiente |
| Solicitar consultas a docentes de EIB (HT-02) | **Usuario** | Pendiente |

**Criterio de salida.** HT-00 terminada, a más tardar el domingo 2026-09-27; si se extiende, reduce el
margen del sprint 1 y se registra en §8.

---

## 3. Sprint 1 · PMV1 — 2026-09-21 → 2026-10-11

**Objetivo (Documento 4).** Disponer de un corpus indexado y consultable por similitud, con la
procedencia de cada fuente registrada.

| Compromiso | Prior. | Épica | Criterio de cierre |
|---|---|---|---|
| HT-00 Repositorio, CI y entorno de agentes | Alta | — | Un PR de prueba recorre todo el circuito |
| HU-01 Ingesta con procedencia | Alta | E-01 | Todo documento con manifiesto; OCR marcado; capas rotas recompuestas |
| HU-02 Segmentación e indexación | Alta | E-02 | Índice reconstruible con un comando; segmentación por tipo; sin duplicados |
| HT-01 Arnés de evaluación | Alta | — | Reproduce la línea base: recall@5 1,000 en A y B; 0 FP en C con el τ vigente (ADR-020) |
| HT-02 Conjunto externo (inicio) | Alta | — | Procedimiento y formato listos; consultas recibidas o solicitud cursada |
| Núcleo: normalización y depuración de la consulta | Alta | — | Prueba de arquitectura: el núcleo no importa bibliotecas de terceros |

**Punto de control:** jueves 2026-10-01. **Revisión:** domingo 2026-10-11.

**Hallazgo previsible (Documento 4, Tabla 18):** cobertura temática desigual → acotar el alcance temático
y declararlo.

| Resultado | Valor medido | Medio de verificación |
|---|---|---|
| Fragmentos indexados | por registrar | salida del comando de indexación |
| recall@5 A / B / D (línea base) | por registrar | informe del arnés |
| Falsos positivos en C con τ vigente | **0** de 28 con τ 0,48 (código base, `fragmentos_v3`, 2026-10-01) | `docs/evidencias/2026-10-01_base-integrante_pc-rtx4060/resumen_arnes.json` (`fp_en_C`) |
| Documentos con manifiesto completo | por registrar | validación de la ingesta |

---

## 4. Sprint 2 · PMV1 — 2026-10-12 → 2026-11-01 · **Hito 1**

**Objetivo.** Completar el flujo de consulta con generación contextualizada, traducción de la consulta,
trazabilidad de la fuente y umbral de abstención; aplicación de escritorio y web operativa.

| Compromiso | Prior. | Épica | Criterio de cierre |
|---|---|---|---|
| HU-06 Salvaguarda de abstención | Alta | E-06 | 0 FP en C; generador no invocado si S < τ; τ en configuración |
| HU-07 Trazabilidad | Alta | E-07 | 100 % de respuestas con documento y página; advertencia OCR |
| HU-03 Consulta léxica | Alta | E-03 | Escenarios Gherkin en verde; forma quechua literal |
| HT-04 Servicio local e interfaz | Alta | — | FastAPI en `127.0.0.1`; interfaz React endurecida (ADR-025) |
| HT-03 Traducción y recalibración de τ | Alta | — | τ recalibrado con A, B, C, D (y E si existe) |
| HU-05 Respuesta en el idioma de la consulta | Media | E-05 | recall@5 ≥ 0,80 en D con 0 FP en C |
| HU-04 Contenido cultural | Media | E-04 | Funcional; evaluada solo si existe RD-05 |
| HT-06 Medición escritorio | Alta | — | P95 ≤ 8 s; VRAM ≤ 8 GB |
| HT-07 Espiga bge-m3 | Baja | — | Informe comparativo en el arnés |

**Orden interno obligatorio:** HU-06 y HU-07 antes que HU-03; HT-03 antes que HU-05. Si el sprint se
estrecha, se reduce HU-04 y después HU-05 (prioridad media), nunca HU-06 ni HU-07.

**Criterios del Hito 1 (go/no-go hacia el PMV2):**

| Criterio | Meta | Resultado |
|---|---|---|
| recall@5 en A y B | ≥ 0,80 | por registrar |
| recall@5 en D (con traducción) | ≥ 0,80 | por registrar |
| recall en la partición externa E | se reporta por separado | por registrar |
| Falsos positivos en C | **0** | por registrar |
| Respuestas con documento y página | 100 % | por registrar |
| Tiempo de respuesta P95 en escritorio | ≤ 8 s | por registrar |
| Pico de VRAM | ≤ 8 GB | por registrar |

**Hallazgo previsible:** volumen documental distinto del previsto → activar la respuesta a R-01 antes de
iniciar el sprint 3.

---

## 5. Sprint 3 · PMV2 — 2026-11-02 → 2026-11-22 · **Hito 2**

**Objetivo.** Incorporar la analítica predictiva y generar los artefactos ejecutables en dispositivo,
con equivalencia comprobada.

**Decisiones previas obligatorias:** ADR-012 (estrategia de recuperación en el móvil) y ADR-013 (registro
de consultas frente a RNF-06) deben estar **aceptadas** en el Sprint Planning.

| Compromiso | Prior. | Épica | Criterio de cierre |
|---|---|---|---|
| HT-05 Artefactos móviles y equivalencia | Alta | — | Índice exportado + paridad (hechos en la revisión 2; verificar en M13) |
| HU-08.1 Predicción de cobertura | Alta | E-08 | No más FP que τ solo en validación cruzada |
| HU-08.2 Umbral adaptativo | Alta | E-08 | Nunca por debajo del τ sin FP; resultado negativo reportable |
| HU-09 Priorización del corpus | Media | E-09 | Informe con ≥ 100 consultas o declaración de insuficiencia |

**Criterio de paso del Hito 2 (Documento 4):** no es que los modelos predictivos rindan mucho, sino que
la **equivalencia entre plataformas** quede comprobada. Si no se sostiene, el sprint 4 se reorienta a
resolverla antes de construir la interfaz.

| Resultado | Valor medido | Medio de verificación |
|---|---|---|
| Error de las tres predicciones | por registrar | validación cruzada |
| Umbral fijo frente a adaptativo | por registrar | arnés |
| Fidelidad de lectura de modelos candidatos | 4B 5/5; 2B 3/5; 0,8B fallos graves (5 casos) | anexo Doc. 5, tabla B |
| Paridad escritorio ↔ móvil | 2,5 × 10⁻⁸ máx.; top-5 idéntico (declarado) | validador de paridad |
| Tamaño del paquete | 21,5 MB (declarado) | artefacto ARM64 |

---

## 6. Sprint 4 · PMV3 — 2026-11-23 → 2026-12-13 · **Hito 3** (en Trello: Sprint 3, 2026-11-06 → 2026-12-13)

**Objetivo.** Integrar los artefactos en la aplicación móvil y validarla en un dispositivo de gama media.

| Compromiso | Prior. | Épica | Criterio de cierre |
|---|---|---|---|
| HU-10.1 Consulta sin conexión | Alta | E-10 | Modo avión; ≤ 15 s; recuperación ≤ 100 ms |
| HU-10.2 Salvaguarda en el teléfono | Alta | E-10 | 0 FP en C ejecutado en el dispositivo |
| HU-10.3 Instalación | Alta | E-10 | Paquete ≤ 1,2 GB o sustitución activada |
| HU-11 Interfaz accesible | Media | E-11 | ≤ 3 interacciones; tipografía ampliable |
| HT-06 Medición en dispositivo | Alta | — | Mínimos **verificados** declarados |

**Hito 3:** no decide si se continúa, sino qué se declara alcanzado y qué queda como trabajo futuro.

| Resultado | Valor medido | Medio de verificación |
|---|---|---|
| Latencia de respuesta en dispositivo | 20 ms en modo avión (`zorro`, emulador); teléfono físico por medir | instrumentación (`18_REPORTE_PMV3.md`, P3-12) |
| Latencia de recuperación en dispositivo | P50 0,80 ms / P95 2,71 ms (N = 248, emulador); teléfono físico por medir | arnés en el dispositivo (P3-05) |
| Tamaño del paquete | 22,6 MB (APK release arm64), frente a 1,2 GB de límite | artefacto (P3-09); Release v1.1.0 |
| Requisitos mínimos verificados | por registrar en el teléfono físico | dispositivo de prueba |
| Prueba de usabilidad | por registrar | sesión con usuarios (acta del anexo B) |

---

## 7. Registro de entradas y salidas del tablero

El archivista añade una fila cada vez que una tarjeta cambia de columna. Formato: fecha ISO, tarjeta,
origen → destino, agente, evidencia (PR, informe, commit).

| Fecha | Tarjeta | Movimiento | Agente | Evidencia |
|---|---|---|---|---|
| 2026-09-24 | DOC-00 Documentación SDD base | En curso → En revisión humana | Orquestador | `docs/` creado |
| 2026-09-24 | DOC-01 CLAUDE.md, subagentes y configuración | En curso → En revisión humana | Orquestador | `CLAUDE.md`, `.claude/`, `.mcp.json` |
| 2026-09-24 | ADR-009/010/011/015 | Listo → Hecho | Usuario | Respuestas del usuario del 2026-09-24 |
| 2026-10-01 | CP-01 Línea base del arnés congelada | (nueva) → Hecho | Orquestador + programador | `docs/evidencias/2026-10-01_base-integrante_pc-rtx4060/` (`resumen_arnes.json`, `meta.json`, `junit.xml`; 40/40 pruebas, 248 consultas) |
| 2026-10-01 | CP-02 M16 preparado: lista y hoja | (nueva) → Hecho | Orquestador | `docs/evidencias/m16/` (`lista_m16.csv`, `kpi_asis.csv`, `README.md`) |
| 2026-10-01 | DEC-02 Decisiones del usuario (ADR-021 aceptada, τ 0,48 confirmado, D-6, docs/13 adoptado) | (nueva) → Hecho | Usuario | `07_DECISIONES.md` (ADR-020, ADR-021) · `13_BRECHAS_RUBRICA.md` |
| 2026-10-01 | PR-01 Estructura hexagonal | (nueva) → Listo | Archivista | `docs/specs/PR-01-estructura-hexagonal/spec.md` (Borrador, pendiente de aprobación) |
| 2026-10-01 | PR-02 Puertos de entrada y CLI | (nueva) → Listo | Archivista | `docs/specs/PR-02-puertos-entrada/spec.md` (Borrador, pendiente de aprobación) |
| 2026-10-01 | PR-03, PR-04, PR-06, PR-07, PR-08, PR-09, PR-10r, PR-11, GH-PRJ, M16-MED, DOC-11-3, PR-INTEG, ARB-PTO | (nuevas) → Backlog | Archivista | `13_BRECHAS_RUBRICA.md` §7 (lista P0) · `05_KANBAN.md` |

---

## 8. Registro de cambios del plan

| Fecha | Cambio | Motivo | Decisión |
|---|---|---|---|
| 2026-09-24 | Creación con fecha ancla supuesta 2026-09-28 | Calendario académico no confirmado | — |
| 2026-09-24 | Fecha ancla corregida a 2026-09-21; la Iteración 0 se integra en la semana 1 del sprint 1 | El usuario confirmó que esta es la primera semana del PMV1 | Usuario |
| 2026-10-01 | Cierre del PMV1: lista P0 de `13_BRECHAS_RUBRICA.md` §7 sustituye a la del prompt §5; fila de FP en C del §3 con la línea base; movimientos en §7 | Revisión de brechas frente a la rúbrica; línea base congelada | Usuario (vía orquestador) |
| 2026-11-24 | §1.4: ejecución real según Trello (tres sprints y S13; PMV3 = Sprint 3, 06/11–13/12); estados del §1.2 y resultados medidos del §6 | Alinear el plan con el tablero para el informe final | Ronda 2 de Omar (P7) |
