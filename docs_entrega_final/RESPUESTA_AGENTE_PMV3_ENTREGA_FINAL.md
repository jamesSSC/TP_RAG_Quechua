# Respuesta del agente · PMV3 y evidencias de la entrega final

Índice de todo lo producido, ordenado según `03_ESTRUCTURA_INFORME_S14.md` (secciones I a X y anexos
A a I).

- **Hecho por:** el agente de James Saenz (Lead Backend & AI), 19–20/11/2026. Actualizado el 24/11/2026
  con la ronda 2 de arreglos (`06_PROMPT_JAMES_ARREGLOS_PENDIENTES.md`, P1 a P8).
- **Fork:** `jamesSSC/TP_RAG_Quechua`. App: `jamesSSC/quechua-wanka-movil`.
- **Estados:** **hecho** · **parcial** (falta algo que se indica) · **sin evidencia** (no se pudo medir y se
  dice por qué).

## 1. Bloques, ramas y estado

| Bloque | Rama · commit | Archivos principales | Estado |
|---|---|---|---|
| B0 · App en dos modos | App `feat/pmv3-dos-modos` (`e7005b5`…`48f5c63`); documentación `feat/pmv3-app-movil` (`4f75b02`) | `lib/` de la app, ADR-038, `docs/03 §7.1`, `docs/18_REPORTE_PMV3.md`, `docs/evidencias/pmv3/` | **Hecho en emulador**; parcial en el teléfono físico |
| B1 · Ingeniería inversa | `docs/ingenieria-inversa` (`999ea06`) | `docs_ingenieria_inversa/` | **Hecho** (PNG de los UML no regenerados; `.puml` verificados) |
| B2 · Auditoría delta | `docs/auditoria-delta-pmv3` (`cf3960c`) | `docs_auditoria/08_auditoria_delta_pmv3.md` | **Hecho** |
| B3 · Métricas de ML y rendimiento | `docs/metricas-ml-final` (`2ed44b9`) | `docs_entrega_final/metricas/` | **Hecho**; la latencia en la nube con N ≥ 30 queda sin evidencia (sin `TOKEN_PRUEBAS`) |
| B4 · Prueba con usuarios | `docs/entrega-final` | `docs_entrega_final/pruebas_usuarios/` | **Materiales hechos**; la prueba la hace el equipo |
| B5 · Guion del video | `docs/entrega-final` | `docs_entrega_final/video_u4/guion.md` | **Hecho**; duración por confirmar (8 o 20 min) |
| B6 · Insumos del informe | `docs/entrega-final` | `docs_entrega_final/informe_final/insumos.md` | **Hecho**; capturas de Render y Neon sin evidencia (cuentas) |
| B7 · Cifras oficiales | `docs/entrega-final` | `docs_entrega_final/cifras_oficiales.md` | **Hecho** |
| B8 · Insumos del artículo | `docs/entrega-final` | `docs_entrega_final/articulo/insumos_pmv3.md` | **Hecho** |
| B9 · Kanban | `docs/entrega-final` | `docs_entrega_final/kanban/tarjetas_pmv3.md` | **Hecho** (lo aplica Omar) |
| B10 · ICACIT | `docs/entrega-final` | `docs_entrega_final/icacit/` (matriz de las 7 competencias, energía, cambios, sprints de Trello, burndown) | **Hecho** |
| B11 · Logo | `feat/logo-proyecto` (`df6cf5e`) y app `b3f4d64` | `docs_entrega_final/logo/` | **Hecho**; falta la captura en la nube tras desplegar |
| B12 · Póster | `docs/entrega-final` | `docs_entrega_final/poster/` | **Hecho**; falta el QR del video |
| B13 · Arreglos rápidos | `fix/s14-arreglos-rapidos` (`54385b0`, `d23098a`, `d43a553`) | `docs_entrega_final/calidad/arreglos_rapidos.md`, `docs_ingenieria_inversa/evidencias/{antes,despues}/` | **Hecho**; los ID H-03 y H-05 a H-08 hay que cotejarlos con el reporte v1.1 |

**PR de la primera ronda:** #28 (B0), #29 (B11), #30 (B13), #31 (B2), #32 (B1), #33 (entrega final) y #34 (B3).
Todos **fusionados** en `main` el 20/11 (`4448478`).

### 1.1 Ronda 2 (24/11): arreglos pedidos por Omar antes del video

| Punto | Qué | PR · rama | Estado |
|---|---|---|---|
| P1 | La web bloquea la gestión por defecto mientras la nube arranca o si `/api/estado` falla (hallazgo S14-01, A04/A01) | #35 · `fix/web-bloqueo-por-defecto` | Abierto; Vitest 53. Falta la captura en la nube tras desplegar |
| — | Matriz ICACIT (B10) y cifras de la nube del 20/11, que habían quedado fuera de `main` | #36 · `docs/icacit-y-cifras-nube` | Abierto |
| P5 | Commit desplegado en `/api/estado.version` y en el pie de la web | #37 · `feat/version-desplegada` | Abierto. Faltan las capturas en la nube (logo, cabeceras y versión) |
| P2 | App en `mobile/` con su historial; QR a la Release | #38 · `feat/app-movil-en-mobile` | Abierto. Repositorio de la app: PR #1 **fusionado** y **Release v1.1.0** publicada con los APK y su SHA-256 |
| P4 | Gemini con tiempo máximo de 10 s, un reintento ante 503 y registro por llamada (ADR-039) | #39 · `fix/latencia-gemini` | Abierto. Faltan el diagnóstico con los logs de Render y la nueva medición |
| P8 | REF-05 (variables en la web), REF-07 («¿le sirvió?», ADR-040) y REF-08 (erratas en español, ADR-041) | #40 · `feat/p8-ref-05-07-08` | Abierto; pytest 459, Vitest 57 |
| P7 | Documentos y cifras al día | `docs/p7-documentos-al-dia` | Este PR. Las cifras del teléfono y de la nube nueva quedan «por medir» |
| P3 | Pruebas en el teléfono físico | — | **Pendiente** (lo último, con el teléfono de James) |
| P6 | Acciones manuales en Neon y Render | — | **Pendiente**: las hace James, sin el agente |

Orden de fusión recomendado: #35 → #37 → #38 → #39 → #40 → #36 → P7. Varios PR añaden una entrada al
final de la bitácora o del registro de ADR, así que pueden pedir resolver conflictos triviales.

## 2. Evidencias por sección del informe

### Preliminares

- **Resumen y abstract (ind. 2):** cifras en `cifras_oficiales.md` (C-15, C-16, C-19, C-20, C-22, C-26 y
  C-29 a C-30).

### I. Análisis de problemas

- 1.2 Restricciones **por modo**: ADR-038 (`docs/07_DECISIONES.md`) y la tabla de privacidad por modo
  (`articulo/insumos_pmv3.md` §2).
- 1.4 OE del PMV3: `docs/03_HISTORIAS_USUARIO.md` §7 y §7.1.

### II. Conocimientos de ingeniería

- `informe_final/insumos.md` §II: tabla con `ruta:línea`.
- τ como optimización: `metricas/metricas_ml_final.md` §2 y `metricas/evidencias/barrido_tau.png`.
- Bootstrap: ídem §1.
- Energía medida: `metricas/metricas_ml_final.md` §5 e `icacit/README.md` §1.

### III. Ingeniero y sociedad

- Energía por modo: `icacit/README.md` §1. La estimación de CO₂e con fuentes publicadas la hace Omar.
- Párrafo de la nube: `icacit/datos_nube.md`.
- Acontecimientos tecnológicos: `informe_final/insumos.md` §III.

### IV. Metodología

- Aportes del PMV3:
  - el índice móvil sigue siendo idéntico al del backend (HT-05);
  - la capa de lema, no la función de puntuación, aporta el 100 % (B3 §3);
  - el APK release sin INTERNET (D-01).

### V. Herramientas modernas

- `informe_final/insumos.md` §V e `icacit/herramientas.md`.
- Capturas:
  - CI: `docs_ingenieria_inversa/evidencias/despues/H-08_despues_ci_ubuntu_run.png` (rama de los arreglos);
  - Playwright: `logo/`;
  - Flutter y emulador: `docs/evidencias/pmv3/movil/`;
  - **Render y Neon: sin evidencia** (cuentas de otro integrante).

### VI. Diseño de ingeniería

- 6.1 HU del PMV3 con Gherkin: `docs/03 §7.1`. Flujo de pantallas de la app:
  `docs/evidencias/pmv3/movil/HU-*.png`.
- 6.2 BD: `informe_final/insumos.md` §VI (`docs/diagramas/er.dot`; SQLite del teléfono; 7 rutinas).
- 6.3 Arquitectura:
  - `docs_ingenieria_inversa/uml/` (componentes, secuencia, clases, casos de uso);
  - despliegue: `poster/figuras/despliegue_poster.png`.

### VII. Gestión del proyecto

- 7.4 Kanban: `kanban/tarjetas_pmv3.md`.
- 7.9 Indicadores: `icacit/avance_commits.png` y los CSV.
- **7.10 Gestión de cambios:** `icacit/cambios.md`.
- Dailies: `docs/evidencias/pmv3/DAILIES_EQUIPO.md` (rama `feat/pmv3-app-movil`).
- Bitácora: `docs/evidencias/pmv3/BITACORA.md`.

### VIII. Pruebas, resultados y discusión

- **8.5 Otra plataforma:** `informe_final/insumos.md` §VIII (Windows, Ubuntu en la CI y Android x86_64).
- **8.7 PMV3:**
  - `docs/18_REPORTE_PMV3.md` (métricas P3-01 a P3-15, una ficha por historia y la comparación entre
    local, nube y teléfono);
  - capturas en `docs/evidencias/pmv3/movil/`.
- **8.8 Métricas de ML y rendimiento:** `metricas/metricas_ml_final.md` (validación cruzada, IC 95 %, τ en
  una muestra independiente, P50/P95, BM25 frente al híbrido).
- **8.9 FURPS+/OWASP:** `docs_auditoria/08_auditoria_delta_pmv3.md` (7,4 → 7,6 y 79 → 82).
- **8.10 Ingeniería inversa:** `docs_ingenieria_inversa/ingenieria_inversa.md`, con antes y después en
  `calidad/arreglos_rapidos.md`.
- **8.11 Usuarios:** `pruebas_usuarios/`. **Sin evidencia** hasta que se haga la prueba.
- 8.12 Discusión: el hallazgo BM25 frente a E4 en `articulo/insumos_pmv3.md` §1.

### IX y X. Lecciones y conclusiones

- Insumos:
  - la bitácora (incidentes: tarjeta en blanco, espacio del emulador, D-01);
  - `cifras_oficiales.md`.

### Anexos

| Anexo | Evidencia | Estado |
|---|---|---|
| A. Experto | Informe U3 | Ya estaba |
| B. Usuarios | `pruebas_usuarios/acta_plantilla.md` | Pendiente: la hace el equipo |
| C. Matriz ICACIT | `icacit/matriz_competencias.md` | Hecho (el equipo redacta el reporte a partir de ella) |
| D. Video | `video_u4/guion.md` | Por grabar |
| E. Kanban | `kanban/tarjetas_pmv3.md` | Lo aplica Omar |
| F. Repositorio | README raíz con enlaces a `docs_auditoria/`, `docs_ingenieria_inversa/` y `docs_entrega_final/` (rama de los arreglos) | Hecho |
| G. Enlaces | `poster/figuras/qr_*.png` | Falta el QR del video |
| H. Póster | `poster/` | Insumos hechos |
| I. Endpoints | Sin endpoints nuevos en el PMV3 (la app usa los públicos) | Sin cambios |

## 3. Las 15 cifras más importantes

1. App: **0 FP** en C y recall@5 **1,000** en A, B y D, con las 248 consultas **en el dispositivo y sin red**.
2. τ: **0 FP también en la muestra independiente F (107)**; cota del 95 % 3,4 %.
3. Predictor 1: **AUC 0,996** (IC 95 % 0,993–0,999).
4. Predictor 2: **AUC 0,980** (IC 95 % 0,964–0,993).
5. Latencia local con Qwen 4B en GPU: **P50 2 744 ms**, P95 2 830 ms (N = 220).
6. Sin conexión en el dispositivo: **P50 0,80 ms**, P95 2,71 ms.
7. Energía de GPU: **44,2 J por respuesta** y **0,07 J por abstención**.
8. APK release arm64: **22,6 MB**, frente a un presupuesto de 1,2 GB.
9. Índice móvil **idéntico byte a byte** al del backend (10/10 archivos).
10. Pruebas en `main`: **426** pytest (con corpus) · **48** Vitest · **45** Flutter. Con la ronda 2: 459 pytest
    y 57 Vitest en la rama de P8.
11. FURPS+ **7,4 → 7,6** · OWASP **79 → 82** (en la rama).
12. `npm audit` **3 altas → 0**; `pip-audit` **0**.
13. Conteos de pruebas cuadrados: sin corpus **406/16**; con corpus **416/6** (el 408/14 no se reproduce).
14. Nube tras H-14: **3 605 fragmentos y 8 documentos**.
15. BM25 frente a E4 sin capa de lema: cobertura con 0 FP del **95,5 % frente al 93,2 %**. El 100 % del
    sistema lo aporta la capa de lema.

## 4. Estado de cada historia del PMV3

| HU | Estado |
|---|---|
| HU-10.1 | Hecha en emulador (en línea, modo avión, cambio automático, selector, 429). Teléfono físico pendiente (P3) |
| HU-10.2 | Hecha: 0 FP en el dispositivo (emulador). Teléfono físico pendiente (P3) |
| HU-10.3 | Hecha: 22,6 MB e INTERNET en el release; **Release v1.1.0 publicada**. Instalación en teléfono físico pendiente (P3) |
| HU-11 | Hecha. Falta Accessibility Scanner en el teléfono (P3) |
| HT-05 | Hecha |
| REF-05, REF-07, REF-08 | **Hechas** en la web (PR #40; ADR-040 y ADR-041) |
| REF-03 | No abordada |

Sprint: en Trello el PMV3 es el **Sprint 3 (06/11–13/12)**; ver `docs/04_SPRINTS.md` §1.4.

## 5. Lo que requiere intervención humana

1. **Prueba con usuarios** (B4, 6 puntos): protocolo, consentimientos, SUS y acta firmada. El acta oficial es
   el Word de Omar. `pruebas_usuarios/llenar_acta.py` escribe en ella las tablas 6.1 y 6.2 desde el CSV.
2. **Grabar el video** (B5) y confirmar la duración con el docente.
3. **Dailies:** cada integrante publica los suyos. Los de James están sugeridos en
   `docs/evidencias/pmv3/DAILIES_EQUIPO.md`.
4. **Decidir** OW-03, OW-08 y OW-17 (recomendación en `calidad/arreglos_rapidos.md`, grupo 5).
5. **Consultas mal rotuladas en Neon:** las 6 de la app (bitácora) y las de la grabación del 05/11 y la
   S13 (guía 02, paso 4).
6. **Render** (quien tenga la cuenta):
   - regenerar `ADMIN_TOKEN` y `TOKEN_PRUEBAS` (P6);
   - desplegar `main` cuando se fusionen los PR;
   - capturar la CSP y el logo en la nube;
   - si existe `GEMINI_TIMEOUT` puesta a mano, borrarla o ponerla en 10 (ADR-039).
7. **Teléfono físico de James (P3):** mediciones, arnés sin red, instalación y Accessibility Scanner.
8. **Cotejar con el reporte v1.1** los ID H-03, H-05 a H-08, H-04, H-11 a H-13 y H-15.
9. **Fusionar los PR #35 a #40 y el de P7** en el orden de §1.1 (Omar revisa y fusiona).
10. **Después del despliegue** (lo hace el agente):
    - medir la nube con N ≥ 30 en dos franjas (C-24);
    - capturar S14-01 durante un arranque en frío real;
    - capturar las cabeceras y la versión (P5).

## 6. Comprobación de rutas

`docs/` solo recibió lo que permite la regla de rutas: las evidencias de desarrollo del PMV3
(`docs/evidencias/pmv3/`), el reporte `docs/18_REPORTE_PMV3.md` que pide el prompt 00, el ADR nuevo
(ADR-038) y los criterios de `docs/03` §7.1 que pide B0. En `docs/` no se modificó nada más.
