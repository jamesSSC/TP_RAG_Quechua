# Registro de cambios del proyecto (Gestión, G-01)

Cambios reales sacados de Git, de los ADR y de los PR, sin fechas inventadas. Las fechas son las de
los commits, los PR o la cabecera de cada ADR; lo que no tiene fecha verificable dice «por confirmar».

| Fecha | Origen | Impacto | Decisión | Acción | Evidencia |
|---|---|---|---|---|---|
| 2026-09-24 (línea base v2) | PoC del Documento 6: el codificador denso rinde peor (recall@5 0,65 frente a 1,00) | Arquitectura de recuperación | Recuperación **léxica híbrida** en lugar de densa | ADR-019 y ADR-020; índice TF-IDF E4 | `docs/07_DECISIONES.md` (registro de cambios, 2026-09-24) |
| 2026-09-24 | Medición del techo de capacidad de los SLM ≤ 2B | Alcance del móvil | Sin modelo en el teléfono: compositor determinista | ADR-026 | ídem |
| 2026-10-01 | Términos frecuentes bajo τ («perro», 0,271) | Salvaguarda | Capa determinista de lema | ADR-021 aceptada con 5 condiciones | ídem, fila 2026-10-01 |
| Por confirmar (S1 21/09–11/10 y S2 12/10–05/11 en Trello) | Planificación | Sprints | **Un sprint por PMV** | `docs/04_SPRINTS.md` (numeración distinta a la de Trello) | Alinear con Trello |
| 2026-10-29 | Guía 11 (despliegue en la nube) | Infraestructura | Render + Neon + Gemini | ADR-030, 031 y 032; PR #17 | PR #17 (`jamesSSC`) |
| 2026-10-29 | `gemini-2.5-flash` retirado (404) | Redacción en la nube | Cambiar de modelo | PR **#18** → `gemini-3.8-flash` | `docs/16_REPORTE_DESPLIEGUE_NUBE.md:104,225` |
| 2026-10-29 | 3.8 Flash agotaba los 15 s del plan gratuito | Latencia en la nube | Gemini **3.5 Flash-Lite** | PR #19 (`e7476cd`) | `e7476cd` |
| 2026-11-04 | Revisión con el experto temático (REF-01 a REF-08) | Mejoras propuestas | Aceptar REF-02; evaluar REF-01 | ADR-033 y ADR-034 | Informe U3, anexo A |
| 2026-11-11 | REF-01: keep-alive para el arranque en frío | Consumo de Neon | **Rechazado**: consumiría ≈ 90 de las 100 CU-h | PR **#22** abierto, no se fusiona | PR #22; guía 02 §6 |
| 2026-11-12 | S13 FURPS+/OWASP | Seguridad y calidad | Token de administración, historial por sesión, límite por IP, HSTS | ADR-035 a ADR-037; PR #23 a #27 | `docs_auditoria/07_auditoria_final.md` |
| 2026-11-19 | Aclaración del alcance del PMV3 (B0) | App móvil | App **en dos modos**: nube principal y corpus local de respaldo | ADR-038 | `docs/07_DECISIONES.md`; `docs/18_REPORTE_PMV3.md` |
| 2026-11-19 | Ingeniería inversa v1.1 (17 hallazgos) | Calidad | Arreglos rápidos con antes y después | Rama `fix/s14-arreglos-rapidos` | `docs_entrega_final/calidad/arreglos_rapidos.md` |
| 2026-11-19 | H-14: 2 PDF de prueba en Neon | Cifras e IDF | Limpieza en transacción con respaldo | Acción manual de James | `docs/evidencias/pmv3/nube/H-14_nube_estado_tras_limpieza.txt` |
| 2026-11-20 | Auditoría delta: el APK release sin INTERNET | Funcionamiento del PMV3 | Corregir el manifiesto | App `48f5c63` | `docs_auditoria/08_auditoria_delta_pmv3.md` (D-01) |
