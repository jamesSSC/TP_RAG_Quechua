# B9 · Tarjetas del Kanban del PMV3 (Trello)

Textos listos para crear o actualizar las tarjetas en Trello. **Las aplica Omar desde su cuenta**: el
agente no entra a Trello. Atiende el indicador 4 (Kanban) y el anexo E del informe.

- **Fechas:** sacadas de los commits (hora de Perú, UTC−5). Lo que no sale de Git dice «por confirmar».
- **Enlaces raw:** fijados al commit del fork de James (`jamesSSC`), que existe hoy. Cuando se fusionen
  los PR, pueden cambiarse por los de `omarpiero/TP_RAG_Quechua` con el commit de la fusión.
- **Base de los enlaces:**
  - Web y documentación (`R`): `https://raw.githubusercontent.com/jamesSSC/TP_RAG_Quechua`
  - App (`M`): `https://raw.githubusercontent.com/jamesSSC/quechua-wanka-movil`

| Responsable por rol | |
|---|---|
| Omar Terbullino | Scrum Master, QA y DevOps |
| James Saenz | Lead Backend & AI |
| Yeferson Serpa | Lead Frontend |

---

## HU-10.1 · Consultar desde el teléfono (en línea y sin conexión)

- **PMV:** PMV3 · Sprint 3 · **Responsable:** James Saenz.
- **Inicio:** 2026-11-19 · **Fin:** 2026-11-19 (commit `e7005b5`, 19:44).
- **Checklist:**
  - [x] Modo en línea contra la API desplegada (consulta, cita, abstención, pasajes, ML, fuentes).
  - [x] Modo sin conexión con el índice exportado y el compositor determinista.
  - [x] Cambio automático (sin red, sin respuesta en 20 s o 5xx) y selector manual.
  - [x] Modo visible siempre; cada respuesta dice de qué modo vino.
  - [x] Aviso de arranque en frío a los 4 s (como la web).
  - [x] 429 sin reintentos, con cuenta atrás.
  - [ ] Medición en el teléfono físico.
- **PR / commit:** app `jamesSSC/quechua-wanka-movil` rama `feat/pmv3-dos-modos` (`e7005b5`, `48f5c63`) ·
  documentación rama `feat/pmv3-app-movil` (`4f75b02`). PR: por abrir.
- **Capturas** (antes → después):
  - Antes: `R/df6cf5e/docs_entrega_final/logo/B11_movil_antes_app_paleta_verde.png` (solo sin conexión,
    sin modo visible).
  - Después:
    - `R/4f75b02/docs/evidencias/pmv3/movil/HU-10.1_movil_en_linea_respuesta_con_cita.png`
    - `R/4f75b02/docs/evidencias/pmv3/movil/HU-10.1_movil_modo_avion_cambio_automatico.png`
    - `R/4f75b02/docs/evidencias/pmv3/movil/HU-10_movil_429_limite_sin_reintento.png`
- **Lista destino:** DONE (en emulador). Lo del teléfono físico va a la tarjeta de deuda.

## HU-10.2 · Misma salvaguarda en el teléfono

- **PMV:** PMV3 · **Responsable:** James Saenz · **Inicio y fin:** 2026-11-19 (`ccb4e29`, 19:49).
- **Checklist:**
  - [x] 248 consultas en el dispositivo sin red: A, B y D con recall@5 = 1,000.
  - [x] **0 FP en C**.
  - [x] «criptomoneda» se abstiene en línea y en modo avión.
- **Capturas:**
  - `R/4f75b02/docs/evidencias/pmv3/movil/HU-10.2_movil_arnes_248_resumen.png`
  - `R/4f75b02/docs/evidencias/pmv3/movil/HU-10.2_movil_modo_avion_abstencion_criptomoneda.png`
- **Lista destino:** DONE.

## HU-10.3 · Instalación que no queda a medias

- **PMV:** PMV3 · **Responsable:** James Saenz · **Inicio y fin:** 2026-11-19 (`48f5c63`, 21:01).
- **Checklist:**
  - [x] APK release arm64 de 22,6 MB, frente al límite de 1,2 GB.
  - [x] Sin descarga de modelo: se instala completo o no se instala.
  - [x] Permiso de INTERNET en el release (PMV3-D01).
  - [ ] Prueba en el teléfono físico.
- **Capturas:**
  - `R/4f75b02/docs/evidencias/pmv3/movil/HU-10.3_movil_mediciones_emulador.png`
  - Después de D-01: `docs_auditoria/evidencias/delta_pmv3/PMV3-D01_despues_release_en_linea.png`
    (rama `docs/auditoria-delta-pmv3`).
- **Lista destino:** DONE (emulador). Lo del teléfono físico va a la deuda.

## HU-11 · Interfaz simple y legible

- **PMV:** PMV3 · **Responsable:** Yeferson Serpa (revisión de interfaz) con James Saenz ·
  **Inicio y fin:** 2026-11-19 (`e7005b5`).
- **Checklist:**
  - [x] Consulta en 2 interacciones.
  - [x] A−/A/A+ como en la web; con la letra al máximo se lee todo.
  - [x] Botones de 48 px o más (prueba de widget).
  - [ ] Accessibility Scanner en el teléfono.
- **Captura:** `R/4f75b02/docs/evidencias/pmv3/movil/HU-11_movil_letra_maxima_forma_fuente_y_aviso.png`.
- **Lista destino:** DONE (falta el escáner en el teléfono, que va a la deuda).

## HT-05 · Artefactos móviles y equivalencia entre plataformas

- **Responsable:** James Saenz · **Inicio y fin:** 2026-11-19.
- **Checklist:**
  - [x] Índice exportado hoy idéntico al de la app (10/10 archivos).
  - [x] Paridad Dart 5/5.
- **Captura:** `R/4f75b02/docs/evidencias/pmv3/movil/HT-05_movil_paridad_indice.png`.
- **Lista destino:** DONE.

---

## Bloques de la entrega final

| Tarjeta | Responsable | Inicio–fin | Rama · commit | Evidencia principal | Lista |
|---|---|---|---|---|---|
| B0 · App en dos modos | James | 19/11 | `feat/pmv3-dos-modos` · `48f5c63` | `docs/18_REPORTE_PMV3.md` | DONE |
| B1 · Ingeniería inversa en GitHub | Omar (revisa) / James | 19/11–20/11 | `docs/ingenieria-inversa` | `docs_ingenieria_inversa/ingenieria_inversa.md` | En revisión |
| B2 · Auditoría delta FURPS+/OWASP | Omar (QA) / James | 20/11 | `docs/auditoria-delta-pmv3` | `docs_auditoria/08_auditoria_delta_pmv3.md` | En revisión |
| B3 · Métricas de ML y rendimiento | James | 20/11 | `docs/metricas-ml-final` | `docs_entrega_final/metricas/metricas_ml_final.md` | En revisión |
| B4 · Prueba con usuarios (materiales) | Omar | 20/11 | `docs/entrega-final` | `docs_entrega_final/pruebas_usuarios/` | **Bloqueado**: lo hace el equipo con personas |
| B5 · Guion del video | Omar | 20/11 | `docs/entrega-final` | `docs_entrega_final/video_u4/guion.md` | Por grabar (duración por confirmar) |
| B6 · Insumos del informe | James | 20/11 | `docs/entrega-final` | `docs_entrega_final/informe_final/insumos.md` | En revisión |
| B7 · Cifras oficiales | Omar (QA) | 20/11 | `docs/entrega-final` | `docs_entrega_final/cifras_oficiales.md` | En revisión |
| B8 · Insumos del artículo | James | 20/11 | `docs/entrega-final` | `docs_entrega_final/articulo/insumos_pmv3.md` | En revisión |
| B10 · Evidencias ICACIT | James | 20/11 | `docs/entrega-final` | `docs_entrega_final/icacit/` | En revisión |
| B11 · Logo en la web y la app | Yeferson (web) / James (app) | 19/11 | `feat/logo-proyecto` · `df6cf5e`; app `b3f4d64` | `docs_entrega_final/logo/` | DONE (falta la captura en la nube tras desplegar) |
| B12 · Insumos del póster | Omar | 20/11 | `docs/entrega-final` | `docs_entrega_final/poster/` | En revisión |
| B13 · Arreglos rápidos | James | 19/11 | `fix/s14-arreglos-rapidos` · `54385b0` | `docs_entrega_final/calidad/arreglos_rapidos.md` | En revisión |

Una tarjeta por hallazgo corregido (para el informe 8.9 y como portada, la captura «después»):

| Tarjeta | Captura de portada (`docs_ingenieria_inversa/evidencias/despues/`) |
|---|---|
| H-02 Corpus mínimo y reconstrucción | `H-02_despues_corpus_minimo_y_reconstruccion.png` |
| H-03 `.env.example` de la nube | `H-03_despues_env_example_con_nube.png` |
| H-05 `npm audit` 3 → 0 | `H-05_despues_npm_audit_0.png` |
| H-06 README | `H-06_despues_readme.png` |
| H-07 CSP del sitio estático | `H-07_despues_sitio_estatico_con_csp.png` |
| H-08 ruff, Bandit y `npm audit` en la CI | `H-08_despues_ci_con_ruff_bandit_npm_audit.png` |
| H-09 Nombre del repositorio y nivel de logs | `H-09_despues_nombre_logs_y_traductor.png` |
| H-10 Modelo en `/api/estado` | `H-10_despues_estado_modelo_extractivo.png` |
| S14-01 Gestión bloqueada por defecto en el arranque en frío | `docs_auditoria/evidencias/despues/S14-01_despues_gestion_bloqueada_en_arranque.png` |
| PMV3-D01 INTERNET en el release | `docs_auditoria/evidencias/delta_pmv3/PMV3-D01_despues_release_con_internet.png` |

## S14-01 · La web bloquea la gestión mientras la nube arranca

- **PMV:** PMV3 · Sprint 3 · **Responsable:** James Saenz · **Revisó:** Omar Terbullino (QA).
- **Inicio y fin:** 2026-11-24.
- **Checklist:**
  - [x] Bloqueo por defecto: solo `escritura_protegida === false` confirmado o el token validado desbloquean.
  - [x] Aviso neutro «Conectando con el servicio…» mientras `/api/estado` no responde.
  - [x] Si `/api/estado` falla: «No se pudo confirmar el modo del servicio» y Reintentar.
  - [x] Sin `/api/historial` ni «Borrar historial» del servidor hasta confirmar el modo.
  - [x] Modo local sin cambios.
  - [x] Revisión de la app móvil: no tiene el patrón.
  - [x] Captura en la nube durante un arranque en frío real (25/11, `8d8969d`): gestión bloqueada a los 6,4 s; «Modo solo lectura» al responder la API (56,3 s).
- **PR / rama:** `fix/web-bloqueo-por-defecto`. PR: por abrir.
- **Capturas:** antes `docs_auditoria/evidencias/antes/S14-01_antes_gestion_desbloqueada_en_arranque.png` →
  después `docs_auditoria/evidencias/despues/S14-01_despues_gestion_bloqueada_en_arranque.png`.
- **Lista destino:** DONE al fusionar (la captura en la nube queda como verificación).

## Deuda técnica (una tarjeta, lista «Deuda»)

1. Mediciones en el **teléfono físico** de James (ARM64): latencia en modo avión, arranque, memoria y
   Accessibility Scanner (HU-10.1, 10.3, 11). Motivo: sin dispositivo conectado en esta sesión.
2. Latencia en línea con N ≥ 30 desde la app y la nube. Motivo: requiere `TOKEN_PRUEBAS`, porque sin él
   las consultas cuentan como demanda real.
3. Desplegar `main` en Render y capturar la CSP del sitio estático y el logo en la nube. Motivo: acción
   manual de quien tenga la cuenta.
4. Regenerar los PNG de los UML con PlantUML. Los `.puml` se verificaron contra el código y no cambiaron.
5. Rotular como `humo` las 6 consultas de prueba de la app (bitácora del PMV3).
6. Cuarentena del corpus (OW-17) y k-anonimato de la analítica (OW-03): trabajo futuro.
7. Fechas del Sprint 3 confirmadas con el tablero (06/11 – 14/12). Las HU-10.x y HU-11 siguen en **Product Backlog**: moverlas a DONE con estas tarjetas.
