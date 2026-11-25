# Bitácora del PMV3

Registro cronológico de decisiones, incidentes, mediciones y comandos del PMV3. Horas en UTC (el
emulador registra en UTC; en Perú son 5 h menos). Fuente de las dailies, de la cascada del sprint y del
registro de cambios (7.10 del informe).

## 2026-11-19 / 2026-11-20 · James Saenz (Lead Backend & AI)

| Hora UTC | Tipo | Qué | Evidencia |
|---|---|---|---|
| 19/11 23:30 | Preparación | Fork `jamesSSC/TP_RAG_Quechua` sincronizado con `omarpiero/TP_RAG_Quechua@8088193` (estaba 36 commits detrás). Clon local en `F:\App Quechua Final\tp-rag-quechua` | `git log -1` = `8088193` |
| 19/11 23:35 | Preparación | Repositorio móvil: fork `jamesSSC/quechua-wanka-movil` desde `DalgomXD-byte/quechua-wanka-movil@3c6e976`; rama `feat/pmv3-dos-modos` | — |
| 19/11 23:40 | Acción manual (James) | Limpieza de Neon (H-14, guía 02): borrados los 2 PDF de prueba en transacción; verificación previa al `COMMIT`: **3 605 fragmentos, 8 documentos** | Captura de la consola de Neon (James) |
| 19/11 23:45 | Incidente | No hay acceso a la consola de Render (es de otro integrante). Sin `TOKEN_PRUEBAS` ni reinicio manual del servicio. `GET /api/estado` seguía en 3 607 fragmentos en memoria hasta el siguiente arranque | — |
| 20/11 00:30 | Decisión | ADR-038: la app cumple `AsistentePort` con `AsistenteConmutado` (nube principal + corpus local de respaldo) | `docs/07_DECISIONES.md` |
| 20/11 00:36 | Medición | Primera consulta en línea desde la app con Render dormido: 19,4 s hasta responder (el estado inicial ya había pasado al corpus local a los 20 s) | `adb logcat \| grep MEDICION` |
| 20/11 00:38 | Incidente | El emulador no tenía espacio para reinstalar el APK de depuración (158 MB). Se desinstaló solo la app del proyecto y se pasó a compilar `--profile` para x86_64 (33 MB) | — |
| 20/11 00:39 | Defecto corregido | La tarjeta de respuesta salía en blanco: Flutter no pinta un borde redondeado con lados de distinto color. Marco uniforme y franja recortada | commit `e7005b5` |
| 20/11 00:45 | Pruebas | 45 pruebas de Flutter en verde; `flutter analyze` sin avisos | `movil/HU-10_movil_flutter_test.txt` |
| 20/11 00:46 | Logo | Ícono adaptativo con el logo aprobado (fondo `#8A5A2B`) | `docs_entrega_final/logo/` |
| 20/11 00:47 | Verificación HT-05 | El índice que exporta hoy `exportar_indice_movil.py` es idéntico byte a byte al de la app (10/10 archivos) y `generar_paridad_dart.py` produce el mismo `paridad_esperada.json` | `movil/HT-05_movil_paridad_indice.txt` |
| 20/11 00:48 | Medición | Arnés de 248 consultas en el emulador, sin conexión: A 120/120, B 60/60, D 40/40, **C 0 FP**; P50 0,80 ms, P95 2,71 ms | `movil/HU-10.2_movil_arnes_248_resumen.png` |
| 20/11 00:50–00:51 | Capturas en línea | Consultas reales a la nube desde la app: `zorro`, `criptomoneda`, `que es el sufijo ablativo`; más `POST /api/predicciones` (no se registra) | `movil/HU-*_en_linea_*.png` |
| 20/11 00:51–00:53 | Capturas sin conexión | Modo avión (`cmd connectivity airplane-mode enable`): cambio automático, abstención, fuentes, predicción no disponible, letra máxima | `movil/HU-*_modo_avion_*.png` |
| 20/11 00:53 | Medición | Arranque en frío (`am start -W`, 5 corridas): 682–788 ms; carga del índice 140–175 ms. PSS 137,8 MB | `movil/HU-10.3_movil_mediciones_emulador.txt` |
| 20/11 00:54 | Medición | APK release: arm64-v8a 22,6 MB · armeabi-v7a 20,2 MB · x86_64 24,0 MB | ídem |
| 20/11 00:59 | Verificación H-14 en la nube | Tras el arranque en frío de las 00:36 la API recargó el corpus desde Neon: `GET /api/estado` = **3 605 fragmentos, 8 documentos**. Sin reinicio manual. `consultas_por_origen.usuario` pasó de 43 (19/11 23:45) a **49**: exactamente las 6 consultas de la tabla de abajo | `nube/H-14_nube_estado_tras_limpieza.txt` |
| 20/11 00:55 | Prueba del 429 | Backend del equipo en local (`ENTORNO=staging`, `LIMITE_CONSULTAS_POR_MINUTO=2`) y la app apuntando a él (`--dart-define=API_URL=http://10.0.2.2:8765`): 429 real, mensaje del servidor, cuenta atrás y **un solo 429** en el registro, sin reintentos | `movil/HU-10_movil_429_*.png`, `movil/HU-10_movil_429_registro_backend_local.txt` |

## Consultas a la nube con origen `usuario` generadas por estas pruebas (HU-09)

La app no puede llevar `TOKEN_PRUEBAS` (ADR-038), así que sus consultas a la nube se registran como
`usuario`. Para no fabricar demanda se limitaron a lo imprescindible para las capturas. Son estas, todas
el 20/11/2026 (UTC); conviene rotularlas `humo` si el equipo decide relabelar (guía 02, paso 4):

| Hora UTC aprox. | Consulta | Para qué |
|---|---|---|
| 00:37 | `zorro` | primera prueba en línea (Render despertando) |
| 00:38 | `zorro` | prueba tras corregir la tarjeta en blanco |
| 00:39 | `zorro` | ídem, APK reinstalado |
| 00:50 | `zorro` | captura HU-10.1 en línea |
| 00:50 | `criptomoneda` | captura HU-10.2 en línea |
| 00:50 | `que es el sufijo ablativo` | captura HU-04 en línea |

## Pendiente

- Mediciones en el **teléfono físico** de James (ARM64): no se hicieron en esta sesión. Las cifras del
  emulador (x86_64 sobre una PC con RTX 4060) **no** sirven para declarar RNF-01/02/04 en el teléfono.
- Latencia en línea desde la app con N ≥ 30: requiere `TOKEN_PRUEBAS` para no registrar 30 consultas
  como demanda real. Sin acceso a Render, **por medir**.
- Aviso de arranque en frío capturado contra Render dormido: se intenta cuando el servicio vuelva a
  suspenderse (15 min sin tráfico).

## Incidente · 2026-11-20, 02:23–02:26 UTC · 31 consultas de prueba registradas como `usuario`

Al medir la latencia en la nube con `TOKEN_PRUEBAS` se usó el origen `arnes`, pero la API solo admite
`humo` y `carga` (`backend/src/infrastructure/seguridad.py:58`, `ORIGENES_DE_PRUEBA`). El token se había
comprobado con `humo` (humo 270 → 271), pero no con `arnes`. Resultado: **31 consultas** quedaron con
`origen = 'usuario'`: la de calentamiento («zorro») más las 30 primeras de `evaluacion_v2.json`
(A001 a A030). Se detuvo en cuanto `usuario` pasó de 50 a 79 (cerró en 81). El guion ya rechaza
cualquier origen distinto de `humo` y `carga`.

**Corrección (acción manual de James en la consola de Neon, en transacción, sin borrar nada):**

```sql
BEGIN;
SELECT COUNT(*) FROM consultas
WHERE origen = 'usuario'
  AND momento BETWEEN '2026-11-20 02:23:00+00' AND '2026-11-20 02:26:30+00';
-- Debe dar 31. Si da otro número, ROLLBACK y revisar.
UPDATE consultas SET origen = 'humo'
WHERE origen = 'usuario'
  AND momento BETWEEN '2026-11-20 02:23:00+00' AND '2026-11-20 02:26:30+00';
COMMIT;   -- o ROLLBACK si la verificación no dio 31
```

Las 6 consultas de la app del 20/11, 00:37–00:51 UTC (tabla de arriba), se pueden rotular igual si el
equipo lo decide.

## 2026-11-24 · S14-01: la web bloquea la gestión por defecto (ronda 2 de arreglos)

Omar observó en la nube que, durante el arranque en frío (~1 min), «Fuentes del corpus» e «Incorporar
documentos» aparecían con los formularios activos hasta que `/api/estado` respondía. Causa en
`frontend/src/App.jsx`: `protegida = Boolean(estado?.escritura_protegida)` era `false` con
`estado = null`, el `.catch` dejaba `estado = null` para siempre si la API fallaba, y
`!datos?.escritura_protegida` pedía `/api/historial` también con `datos` indefinido. La API seguía
devolviendo 401 a las escrituras sin token: fallo de diseño de la interfaz, no exposición de datos.

- Reproducido sin tocar la nube: web compilada con una API remota simulada y `vite preview`;
  Playwright intercepta `/api/estado` y lo retrasa 20 s o lo hace fallar
  (`frontend/playwright.arranque.config.js`). Capturas de antes y después en
  `docs_auditoria/evidencias/{antes,despues}/S14-01_*`.
- Arreglo en `fix/web-bloqueo-por-defecto`; Vitest 48 → 53 (todas en verde).
- App móvil revisada: no tiene el patrón (no administra nada ni pide `/api/historial`).
- Pendiente: captura en la nube durante un arranque en frío real, después de fusionar y desplegar.

## 2026-11-24 · P5: versión desplegada en `/api/estado` y en el pie de la web

`/api/estado` informa `version`: los 7 primeros caracteres de `RENDER_GIT_COMMIT`, que Render define en
cada despliegue, o `"local"`. El pie de la web muestra «versión: API <commit> · web <commit>». La web
toma su commit al compilarse (`vite.config.js`, `__VERSION_WEB__`), porque el sitio estático y la API
se despliegan por separado y pueden quedar en commits distintos. pytest 430 + 4 (todas en verde);
Vitest + 3. Pendiente tras desplegar `main`: capturas en la nube (logo, cabeceras con
`curl -sI`, `/api/estado` con 3 605 fragmentos, 8 documentos y el commit).

## 2026-11-24 · P2: la app en el repositorio oficial

- PR #1 en `DalgomXD-byte/quechua-wanka-movil`: `feat/pmv3-dos-modos` → `master` (fast-forward de
  6 commits sobre `3c6e976`). `flutter analyze`: sin avisos. `flutter test`: 45/45.
- La app también queda en `mobile/` de este repositorio, traída con `git subtree add` (conserva los
  14 commits de su historial), como pidió Omar. `flutter analyze` y `flutter test` también pasan
  desde `mobile/`.
- Release `v1.1.0` (por publicar al fusionar el PR #1). Los APK no se suben al repositorio:
  - `QuechuaWanka-1.1.0-arm64.apk`, SHA-256 `2acd0b56ea9c2d0b68479d2b4895d2d2710164882058655134fdf8f4c7146790`;
  - `QuechuaWanka-1.1.0-arm32.apk`, SHA-256 `4dbb622c84c73851f28046a8d3ffebfb4d888596ec1b613e11c0c8c95d2bc934`.
- `qr_app_movil.png` regenerado: apunta a la Release. README, `docs/18` y el guion del video
  actualizados.

## 2026-11-24 · P4: mitigaciones de la latencia de la nube (ADR-039)

- `GEMINI_TIMEOUT`: 15 s → 10 s. Reintento único ante 503, dentro del mismo presupuesto. Registro
  `[GEMINI] modelo=… resultado=… ms=…` por llamada, sin la clave ni la consulta.
- pytest: 6 casos nuevos en `test_gemini_generador.py`; suite completa en verde.
- **Diagnóstico pendiente:** leer los logs de Render del 20/11 (429/503, duración por llamada) y la
  cuota en Google AI Studio. Requiere el acceso de James al panel; con este cambio desplegado, los
  logs ya muestran la duración de cada llamada.
- **Medición pendiente:** N ≥ 30 en dos franjas (mañana y noche, hora de Perú), origen `humo`,
  ≤ 20/min, después de desplegar. Luego C-24 en `cifras_oficiales.md`.
- Si en el panel de Render hay una variable `GEMINI_TIMEOUT` puesta a mano, tiene prioridad sobre el
  valor por defecto: hay que borrarla o ponerla en 10.

## 2026-11-24 · P8: REF-05, REF-07 y REF-08

- **REF-05:** la tabla de variables de la web es ahora igual a la de la app: valor y peso
  (coeficiente estandarizado). El MD pedía «coeficiente × valor», pero la app muestra el peso, porque
  la API no expone la media ni la desviación del estandarizador. Se igualó a la app para que coincidan
  en el video.
- **REF-07 (ADR-040):** «¿Le sirvió esta respuesta?». La tabla `valoraciones` la crea `create_all()` al
  arrancar, también en Neon, sin ejecutar SQL a mano. Pública en la nube con el límite de la consulta.
- **REF-08 (ADR-041):** «¿Quiso escribir…?» solo en abstenciones de consultas en español, desde el
  lemario castellano. Probado con el corpus real:
  - «zoro» → zorro y oro; «perrro» → perro; «mujr» → mujer;
  - «criptomoneda», «atuk» y el inglés no reciben sugerencias.
- Evidencias con la API local sobre una copia de `quechua_wanka.db`.
- pytest 459/6, Vitest 57.

## 2026-11-25 · Verificación en la nube tras desplegar `main` (`8d8969d`) y medición de P4 (mañana)

- **P5:**
  - `/api/estado` informa `version: 8d8969d`, 3 605 fragmentos, 8 documentos y `escritura_protegida: true`
    (`nube/P5_despues_nube_api_estado_version.{txt,png}`);
  - el pie de la web dice «versión: API 8d8969d · web 8d8969d», con el logo
    (`docs_entrega_final/logo/B11_web_nube_despues_con_logo.png`);
  - las cabeceras CSP, Referrer-Policy y Permissions-Policy están activas en el sitio estático
    (`docs_ingenieria_inversa/evidencias/despues/H-07_despues_nube_cabeceras.{txt,png}`). Render aplicó
    `render.yaml`: no hizo falta configurarlas a mano.
- **P1 (S14-01) con un arranque en frío real:** la API estuvo 16 min sin tráfico. Al abrir la web,
  «Fuentes del corpus» mostró a los 6,4 s el aviso neutro, sin formularios (0 controles). A los 56,3 s
  la API respondió y la pestaña pasó sola a «Modo solo lectura»
  (`docs_auditoria/evidencias/despues/S14-01_despues_nube_*`).
- **P4, franja de la mañana** (08:37–08:49 de Perú; 248 consultas, origen `humo`, 20/min):
  - comprobación previa del token: una consulta de control subió `humo` +1 y `usuario` +0. Sin ese
    control, un token inválido las habría contado como demanda real (el middleware no rechaza);
  - respuestas (N = 220): **P50 1 015 ms, P95 10 346 ms**; respaldo extractivo en 51 (23 %), 16 de ellas
    por tiempo agotado (10 s) y 35 rápidas (el verificador descartó la extracción);
  - abstenciones: P50 203 ms; arnés: recall@5 1,000 en A, B y D, **0 FP en C**, 0 errores HTTP;
  - frente al 20/11 (mediodía): P50 6 424 → 1 015 ms y P95 15 366 → 10 346 ms. La bajada del P95 es el
    efecto del tope de 10 s (ADR-039). La del P50 **no se atribuye al cambio**, porque el tope no actúa
    sobre las respuestas rápidas: probablemente refleja menos carga de Gemini a esa hora. La franja de
    la noche lo contrastará;
  - corrección de la cifra del 20/11: de las 55 respuestas por el respaldo, solo **18** agotaron los
    15 s; las otras 37 fueron rechazos rápidos del verificador.
  - Evidencia: `docs_entrega_final/metricas/evidencias/latencia_nube_gemini_adr039_manana.{json,csv}`.
- Pendiente: franja de la noche; diagnóstico de 429/503 con los logs de Render (acceso de James).


## 2026-11-25 · P4.1: diagnóstico desde el cliente (sin los logs de Render) y conteo de P6

**Diagnóstico de la latencia** (CSV del 20/11 y de esta mañana, consulta por consulta):

| Indicio | 20/11 (mediodía) | 25/11 (mañana) | Qué descarta o sugiere |
|---|---|---|---|
| Red cliente ↔ Render (`total_ms − servidor_ms`), P50 / P95 | 141 / 322 ms | 134 / 166 ms | **No es la red ni la región**: es menos del 3 % del tiempo |
| Llamadas a Gemini **aceptadas**, P50 / P95 | 6 086 / 9 533 ms (98 de 165 superan 5 s) | 834 / 2 736 ms (5 de 169 superan 5 s) | Mismo modelo, misma instrucción y mismo contexto: la lentitud está **en la llamada a Gemini** y varía con el momento |
| Respaldo «rápido» (verificador), P50 | 5 281 ms | 1 167 ms | Un 429 (cuota) falla en milisegundos; estos tardan lo que la llamada. **No hay indicio de cuota agotada** |
| Tiempo agotado: IDs y posición | 18, dispersos (solo A035 se repite al día siguiente) | 16, dispersos | **No depende de la consulta ni de la longitud del contexto**; son picos sueltos |

**Causa probable:** variabilidad de la latencia de Gemini 3.5 Flash-Lite (plan gratuito) según la carga
del momento, con razonamiento «low». No la explican la red, la región, la cuota ni la longitud de la
instrucción. **Falta confirmarlo:**
- con los logs de Render (`[GEMINI] … resultado=HTTP 429|503 ms=…`, que existen desde ADR-039) y la cuota
  en AI Studio, que son acceso de James;
- con la franja de la noche, que además guarda `motivo_redaccion` por consulta (cambio en
  `scripts/medir_latencia_energia.py`).

**P6 · consultas `usuario` reales:** **54**, según `fn_conteo_por_origen()` en Neon (servida por
`/api/estado`, 25/11). Si el equipo rotula como `humo` las 6 de la app del 20/11, quedan **48**. Esa es
la cifra de HU-09 para el informe. La consulta de control de hoy quedó como `humo` y no cambia la
cifra.

## 2026-11-25 · P4, segunda franja (media mañana) y corrección del diagnóstico

**Medición** (10:36–10:54 de Perú; 248 consultas, origen `humo` validado antes con una consulta de control;
20/min). Es la segunda franja que pide P4. Fue **solo dos horas después** de la primera: no es una franja
de noche.
- Respuestas (N = 220): **P50 997 ms, P95 5 304 ms**; abstenciones: P50 160 ms; 0 errores HTTP.
- Arnés: recall@5 1,000 en A, B y D; **0 FP en C**.
- Respaldo: 50 (22,7 %). Ahora con su motivo, porque el guion guarda `motivo_redaccion`:

| Motivo | n | `servidor_ms` (mediana) | Patrón |
|---|---|---|---|
| Verificador: la forma o la glosa no están en el fragmento | 21 | 830 | Disperso. Es la salvaguarda funcionando, no una falla |
| `cuota agotada (429)` | 16 | 348 | **12 de 16 al final** (consultas 225–247) |
| `error HTTP 503` (también falló el reintento de ADR-039) | 7 | 2 554 | Disperso |
| `tiempo agotado (10 s)` | 6 | 10 224 | Disperso |

**Corrección del diagnóstico de P4.1** (la entrada anterior decía «no hay indicio de cuota agotada»):
**sí hay 429.** La cuota del plan gratuito de Gemini se agota cuando hay muchas llamadas seguidas: esta
corrida era la tercera del día (unas 500 llamadas en unas 2 h), y los 429 se concentraron al final. Hay,
además, 503 sueltos (modelo saturado) y picos de latencia del propio Gemini que varían con el momento.
La red y la longitud de la instrucción siguen descartadas.

**Causas probables, por orden de peso:**
1. Latencia variable de Gemini 3.5 Flash-Lite según la carga (20/11: P50 de las llamadas aceptadas
   6,1 s; hoy, 0,8–0,9 s).
2. Límite de cuota del plan gratuito (429) bajo ráfagas como las de las mediciones. Un uso normal no
   llega a ese ritmo.
3. 503 sueltos y tiempos agotados (menos del 6 % de las respuestas).

**Implicación:** con el plan gratuito, la cifra depende del momento y de cuántas llamadas se hayan hecho
antes. No se contrata un plan de pago sin decisión del equipo (regla del MD). Los logs de Render
(`[GEMINI] … resultado=HTTP 429|503`) permitirían confirmar las cifras del 20/11, que no guardaron el
motivo.

Evidencia: `docs_entrega_final/metricas/evidencias/latencia_nube_gemini_adr039_franja2.{json,csv}`.
