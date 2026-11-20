# Ingeniería inversa del asistente de consulta del quechua wanka

Salida final de la guía de ingeniería inversa del docente (bloque B1 del paquete de la entrega final,
indicador 8 de la lista de cotejo U4, sección 8.10 del informe). La guía dice `docs/ingenieria_inversa.md`;
va en `docs_ingenieria_inversa/` para no mezclarla con la documentación SDD de `docs/`.

- **Objeto analizado:** `omarpiero/TP_RAG_Quechua@8088193` (`main`, PR #27) y la app
  `quechua-wanka-movil`.
- **Base:** el reporte de ingeniería inversa v1.1 (19/11/2026, 17 hallazgos), resumido en la sección 8.9
  del informe.
- **Qué añade este documento:** las evidencias de terminal (que eran la carencia principal del reporte),
  la verificación de los UML contra el código, los conteos de pruebas cuadrados y el estado de cada
  hallazgo.

> El reporte v1.1 no está en el repositorio. Los nombres de las fases de abajo siguen el orden habitual de
> la guía (inventario → estructura → arquitectura → diseño → datos → comportamiento → hallazgos) y
> **deben cotejarse con los títulos exactos de la guía** antes de pasarlos al informe.

## Fase 1 · Inventario y contexto

| Dato | Valor | Evidencia |
|---|---|---|
| Commits en `main` | 137 | `evidencias/fase_inventario/inventario.png` |
| PR | 26 fusionados, 1 abierto (#22, keep-alive, que no se fusiona) | ídem |
| Backend `src` | domain 20 archivos / 830 líneas · application 30 / 1 287 · adapters 39 / 2 353 · infrastructure 7 / 894 | ídem |
| Pruebas del backend | 56 archivos / 5 014 líneas | ídem |
| Frontend `src` | 27 archivos / 3 774 líneas | ídem |
| Dependencias directas | backend 13; frontend 2 de ejecución y 12 de desarrollo | ídem |

## Fase 2 · Estructura

Árbol real: `backend/src/{domain, application/{ports/in, ports/out, use_cases}, adapters/{in, out},
infrastructure}`. El README anterior mostraba otra estructura (`backend/domain/…`); se corrigió
(H-06, rama `fix/s14-arreglos-rapidos`).

## Fase 3 · Arquitectura

| Elemento | Conteo verificado |
|---|---|
| Middleware ASGI | 7 |
| Controladores REST | 6 |
| Casos de uso | 8 |
| Puertos de entrada / de salida | 7 / 10 |
| Archivos de adaptadores de salida | 17 |
| Pruebas de arquitectura | 4/4 en verde: el dominio solo usa la biblioteca estándar; la aplicación no importa adaptadores; ni el dominio ni la aplicación conocen PostgreSQL ni SQLAlchemy |

- **Evidencia:** `evidencias/fase_arquitectura/arquitectura.png`.
- **UML:** `uml/ii_03_componentes.puml` (interfaces con lollipop y `<<use>>`).

## Fase 4 · Diseño (UML v1.1)

Los 4 diagramas corregidos están en `uml/`, en `.puml`, `.png` y `.svg`:

- `ii_01_clases`;
- `ii_02_secuencia` (`alt` con `else` y un `opt`);
- `ii_03_componentes`;
- `ii_04_casos_uso` (`<<extend>>` de «Declarar ausencia» a «Consultar»).

**Verificación contra el código** (`evidencias/fase_diseno/verificacion_uml.png`):

- Las 10 clases del diagrama de clases existen, con todos sus atributos y métodos.
- Los 18 puertos, adaptadores y servicios de los diagramas de secuencia y de componentes existen con
  ese nombre.
- **Los `.puml` no requieren corrección.**

**PNG:** los PNG y SVG son los entregados con la v1.1, generados de esos mismos `.puml`. No se
regeneraron en esta sesión porque PlantUML no está instalado en el equipo. Como los `.puml` no
cambiaron, las imágenes siguen siendo fieles. Para regenerarlas: `plantuml -tpng -tsvg uml/*.puml`.

## Fase 5 · Datos

- Tablas del servidor: `FuenteORM`, `ConsultaORM` y `RespaldoORM`.
- Rutinas: **7** (2 procedimientos y 5 funciones), en `backend/db/postgres/procedimientos.sql` y
  `esquema.sql`.
- Corpus: fuera de Git (ADR-015). Se reconstruye de forma exacta desde el índice móvil con
  `scripts/reconstruir_corpus.py` (H-02).
- **Evidencia:** `evidencias/fase_datos/datos.png`.

## Fase 6 · Comportamiento y pruebas (conteos cuadrados)

El reporte daba «406/16 sin corpus y 408/14 con corpus». Ejecutadas las variantes en `8088193`
(`evidencias/fase_pruebas/pytest_variantes.png`):

| Variante | Aprobadas | Omitidas | Motivos de omisión |
|---|---|---|---|
| Sin corpus (clon limpio) | **406** | **16** | 8 sin `fragmentos_v2`, 2 sin `fragmentos_v3`, 6 sin PostgreSQL |
| Solo `fragmentos_v3` | 406 | 16 | 10 sin `fragmentos_v2`, 6 sin PostgreSQL |
| Solo `fragmentos_v2` | 414 | 8 | 2 sin `fragmentos_v3`, 6 sin PostgreSQL |
| **Con corpus** (`v2` + `v3`, sin PostgreSQL) | **416** | **6** | 6 sin PostgreSQL |

**Cifra única por variante:** sin corpus **406/16**; con corpus **416/6**. El «408/14» del reporte no
se reproduce con ninguna combinación de datos y debe sustituirse. Con los arreglos de la S14 (rama
`fix/s14-arreglos-rapidos`) la suite pasa a 416/16 sin corpus: 10 pruebas nuevas, entre ellas la de
recuperación real sobre el corpus mínimo versionado, que ya corre en la CI.

## Fase 7 · Hallazgos

| ID | Prioridad | Hallazgo | Estado | Dónde |
|---|---|---|---|---|
| H-01 | — | Versión de Python no declarada como obligatoria | **Corregido** (README: Python 3.12 obligatorio) | `fix/s14-arreglos-rapidos` |
| H-02 | P1 | Un clon limpio no reproduce las pruebas ni las métricas que necesitan el corpus | **Corregido**: corpus mínimo, `reconstruir_corpus.py` y prueba en la CI | ídem |
| H-03 | — | `.env.example` sin las variables de la nube (*) | **Corregido** | ídem |
| H-05 | — | 3 vulnerabilidades altas en `npm audit` (*) | **Corregido** (0) | ídem |
| H-06 | P1 | README desactualizado (*) | **Corregido** | ídem |
| H-07 | — | Sitio estático sin CSP (*) | **Corregido en la rama**; visible en la nube al desplegar | ídem |
| H-08 | — | CI sin ruff ni `npm audit` (*) | **Corregido**; CI en verde en Ubuntu | ídem |
| H-09 | — | `RepositorioFuentesPostgres` mal nombrado; registros sin nivel | **Corregido** | ídem |
| H-10 | — | `/api/estado.modelo` muestra Qwen con el redactor extractivo | **Corregido** | ídem |
| H-14 | — | 2 PDF de prueba en Neon (3 607 fragmentos y 10 documentos) | **Corregido** (acción manual de James, 19/11). La nube ya informa 3 605 y 8 | `docs/evidencias/pmv3/nube/H-14_nube_estado_tras_limpieza.txt` |
| H-16 | — | Licencias de las fuentes | Pendiente: documental, lo completa el equipo | — |
| H-17 | P1 | El móvil no tiene predictor de ML | **Resuelto por diseño** (ADR-038): en línea la app muestra el ML de la nube; sin conexión lo declara no disponible | `feat/pmv3-dos-modos` |
| H-04, H-11, H-12, H-13, H-15 | H-11 y H-12 son P1 | Descripción en el reporte v1.1, que no está en el repositorio | **Por cotejar con el reporte** | — |
| **H-18** (nuevo) | — | `TRADUCTOR` de `render.yaml` se ignoraba | **Corregido** | `fix/s14-arreglos-rapidos` |
| **H-19** (nuevo) | — | `ADMIN_TOKEN` no declarado en `render.yaml` | **Corregido**: solo `sync: false`, sin valor; no se tocó Render | ídem |
| **H-20** (nuevo) | — | El reporte cita md5, pero el hash que se usa es **sha256** (ej.: `seguridad_nube.py`, `seudonimo`; los hashes del corpus) | **Corregir el texto del reporte** | — |
| **H-21** (nuevo) | Alta | El APK release no declaraba INTERNET (PMV3-D01) | **Corregido** | `feat/pmv3-dos-modos` (`48f5c63`) |

(*) La correspondencia entre estos IDs y sus arreglos se dedujo de la tabla B13 del paquete; **hay que
cotejarla con el reporte v1.1.** Detalle y capturas antes/después: `docs_entrega_final/calidad/arreglos_rapidos.md`
y `evidencias/{antes,despues}/`.

## Adenda S14

La rama `fix/s14-riesgos-residuales` y `docs_auditoria/08` que citaba la adenda **no existían** en el
remoto (verificado con `gh api` el 19/11). Los arreglos se **rehicieron** en `fix/s14-arreglos-rapidos`,
y la auditoría delta del PMV3 ocupa ahora `docs_auditoria/08_auditoria_delta_pmv3.md` (rama
`docs/auditoria-delta-pmv3`). La adenda debe citar esas ramas en lugar de las anteriores, y decir
«pendiente» en lo que no esté fusionado en `main`.
