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

## 2026-11-24 · P5: versión desplegada en `/api/estado` y en el pie de la web

`/api/estado` informa `version`: los 7 primeros caracteres de `RENDER_GIT_COMMIT`, que Render define en
cada despliegue, o `"local"`. El pie de la web muestra «versión: API <commit> · web <commit>». La web
toma su commit al compilarse (`vite.config.js`, `__VERSION_WEB__`), porque el sitio estático y la API
se despliegan por separado y pueden quedar en commits distintos. pytest 430 + 4 (todas en verde);
Vitest + 3. Pendiente tras desplegar `main`: capturas en la nube (logo, cabeceras con
`curl -sI`, `/api/estado` con 3 605 fragmentos, 8 documentos y el commit).
