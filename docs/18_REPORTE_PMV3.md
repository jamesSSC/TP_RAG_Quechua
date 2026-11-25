# Reporte del PMV3 · App móvil en dos modos

> Responsable: James Saenz Castro (Lead Backend & AI). Fecha: 20/11/2026.
> Decisión de arquitectura: ADR-038. Criterios: `03_HISTORIAS_USUARIO.md` §7 y §7.1.
> Bitácora: `evidencias/pmv3/BITACORA.md`. Evidencias: `evidencias/pmv3/{movil,nube}/`.

## 1. Metadatos

| Dato | Valor |
|---|---|
| Repositorio de la app | `mobile/` de este repositorio (con su historial, `git subtree`) y `DalgomXD-byte/quechua-wanka-movil` (`master`, PR #1 desde `feat/pmv3-dos-modos`) |
| APK release | [Release v1.1.0](https://github.com/DalgomXD-byte/quechua-wanka-movil/releases/tag/v1.1.0): `QuechuaWanka-1.1.0-arm64.apk`, SHA-256 `2acd0b56ea9c2d0b68479d2b4895d2d2710164882058655134fdf8f4c7146790` |
| Commits de la app | `e7005b5` (dos modos), `b3f4d64` (ícono), `ccb4e29` (arnés en el dispositivo) |
| Backend de referencia | `omarpiero/TP_RAG_Quechua@8088193` |
| Flutter / Dart | Flutter 3.44.9 (stable) |
| Dispositivo de prueba | Emulador Android Studio `sdk_gphone16k_x86_64` (perfil Pixel 9 Pro), Android 17 (API 37) |
| Teléfono físico | **Sin medir** en esta entrega (ver §5) |
| API en la nube | `https://quechua-api.onrender.com` (Render, entorno `staging`, Neon, Gemini 3.5 Flash-Lite) |

## 2. Qué se construyó

La app tiene un único puerto, `AsistentePort`, y tres adaptadores:

- `AsistenteNube`: consume la API desplegada con los mismos endpoints públicos que la web
  (`POST /api/consultas`, `POST /api/predicciones`, `GET /api/modelos`, `GET /api/fuentes`,
  `GET /api/estado`). No envía ningún token.
- `AsistenteLocal`: el modo sin conexión que ya existía (índice exportado, tabla EN→ES, compositor
  determinista). Su lógica no cambió.
- `AsistenteConmutado`: elige entre los dos. Es el que inyecta el contenedor.

En la interfaz:

- El modo activo se ve siempre en la cabecera y cada respuesta dice de qué modo vino.
- La cita principal (documento y página) es visible sin desplegar nada.
- Bloque de predicción ML en línea. Sin conexión, la app dice que el teléfono no ejecuta los modelos.
- Pestañas Consultar, Fuentes y Predicción ML. No hay funciones de administración.
- A−/A/A+ con los mismos factores que la web (0,9 · 1 · 1,15 · 1,35) y botones de 48 px o más.
- Aviso de arranque en frío con el mismo texto y umbral (4 s) que la web.
- Manejo del 429 sin reintentos, con cuenta atrás de `Retry-After`.
- Paleta y logo de la web (B11).

## 3. Métricas (P3)

| ID | Métrica | Valor | Unidad | Comando | Evidencia | Commit | Entorno |
|---|---|---|---|---|---|---|---|
| P3-01 | Pruebas de Flutter (unitarias, widget, adaptador, conmutador, seguridad, paridad) | 45/45 | pruebas | `flutter test` | `movil/HU-10_movil_flutter_test.txt` | `ccb4e29` | PC |
| P3-02 | Avisos del analizador | 0 | avisos | `flutter analyze` | `movil/HU-10_movil_flutter_analyze.txt` | `ccb4e29` | PC |
| P3-03 | Recall@5 sin conexión, A / B / D | 1,000 / 1,000 / 1,000 | proporción | arnés en el dispositivo | `movil/HU-10.2_movil_arnes_248_resumen.png` | `ccb4e29` | emulador |
| P3-04 | Falsos positivos en C sin conexión | 0 de 28 | consultas | ídem | ídem | `ccb4e29` | emulador |
| P3-05 | Latencia por consulta sin conexión (N = 248), P50 / P95 | 0,80 / 2,71 | ms | ídem | ídem | `ccb4e29` | emulador (depuración) |
| P3-06 | Carga del índice en el arranque | 140–175 | ms | `adb logcat \| grep MEDICION` | `movil/HU-10.3_movil_mediciones_emulador.txt` | `ccb4e29` | emulador (profile) |
| P3-07 | Arranque en frío de la app (5 corridas) | 682–788 | ms | `adb shell am start -W` | ídem | `ccb4e29` | emulador (profile) |
| P3-08 | Memoria PSS tras una consulta | 137,8 | MB | `adb shell dumpsys meminfo` | ídem | `ccb4e29` | emulador (profile) |
| P3-09 | APK release arm64-v8a / armeabi-v7a / x86_64 | 22,6 / 20,2 / 24,0 | MB | `flutter build apk --release --split-per-abi` | ídem | `ccb4e29` | PC |
| P3-10 | Índice incorporado (`assets/indice`) | 12 | MB | `du -sh` | ídem | `ccb4e29` | PC |
| P3-11 | Paridad del índice app ↔ backend | 10/10 archivos idénticos (sha256) | archivos | `exportar_indice_movil.py` + `sha256sum` | `movil/HT-05_movil_paridad_indice.txt` | `8088193` / `ccb4e29` | PC |
| P3-12 | Consulta en modo avión, de la pulsación a la respuesta (`zorro`) | 20 | ms | `MEDICION total_ms` | `movil/HU-10.1_movil_modo_avion_cambio_automatico.png` | `ccb4e29` | emulador (profile) |
| P3-13 | Consulta en línea, nube despierta (`zorro`), de la pulsación a la respuesta | 822–987 | ms | `MEDICION total_ms` (3 consultas) | `BITACORA.md` | `ccb4e29` | emulador → Render |
| P3-14 | Primera consulta en línea con Render dormido | 19 406 | ms | `MEDICION total_ms` | `BITACORA.md` | `ccb4e29` | emulador → Render |
| P3-15 | Reintentos automáticos tras un 429 | 0 | peticiones | registro del backend local | `movil/HU-10_movil_429_registro_backend_local.txt` | `ccb4e29` | emulador → backend local |

**Lo que no se midió y por qué.**
- Latencia en línea con N ≥ 30: haría falta `TOKEN_PRUEBAS` para que esas consultas no cuenten como
  demanda real (HU-09), y no hay acceso a Render. **Por medir.**
- Todo lo del teléfono físico ARM64: **por medir**.

## 4. Comparación entre entornos

| Aspecto | Web local | Nube (Render) | Teléfono, en línea | Teléfono, sin conexión |
|---|---|---|---|---|
| Quién responde | backend local | backend en Render | backend en Render | `AsistenteLocal` en el teléfono |
| Redacción | Ollama o extractivo | Gemini 3.5 Flash-Lite | Gemini (de la nube) | compositor determinista |
| Predicción ML | sí | sí | sí (se muestra) | no (se dice explícitamente) |
| Umbral τ | 0,48 | 0,48 | 0,48 | 0,48 |
| ¿Sale la consulta del dispositivo? | no | sí | sí | **no** |
| Abstención en C | 0 FP (arnés del backend) | — | — | **0 FP (medido en el emulador)** |
| Respuesta a `zorro` | — | Atuq, p. 37 | Atuq, p. 37 | Atuq, p. 37 |

## 5. Ficha por historia

### HU-10.1 · Consultar desde el teléfono (en línea y sin conexión)

- **Como** usuario del valle del Mantaro, **quiero** consultar desde el teléfono con o sin internet,
  **para** acceder al corpus donde la lengua se habla.
- **Gherkin:** §7 (modo avión) y §7.1 (dos modos, cambio automático, selector, arranque en frío, 429).
- **Pasos:** abrir la app, consultar `zorro` con red; activar el modo avión y repetirla; elegir modo
  en el selector.
- **Resultado:**

  | Entorno | Resultado |
  |---|---|
  | Local | 45 pruebas con doble de la API, incluidas las del conmutador |
  | Nube | `zorro` → Atuq, p. 37, «Respondido en línea · nube», 822–987 ms |
  | Teléfono | Emulador. En modo avión, cambio automático a «Sin conexión · corpus local» en 20 ms; mismo resultado. Teléfono físico sin medir |

- **Estado:** hecha en emulador. Queda pendiente la medición en el teléfono físico.
- **Capturas** (con su pie sugerido):
  - `HU-10.1_movil_en_linea_respuesta_con_cita.png`: «Consulta en línea: forma literal, documento,
    página y predicción ML».
  - `HU-10.1_movil_modo_avion_cambio_automatico.png`: «En modo avión la app pasa sola al corpus del
    teléfono y lo declara».
  - `HU-10_movil_selector_manual_de_modo.png`: «Selector manual de modo».
  - `HU-10_movil_429_limite_sin_reintento.png`: «Límite de la nube: mensaje y espera, sin reintentos».
- **Decisiones:** ADR-038. Espera de 20 s en automático, porque Render tarda 62–72 s en despertar y el
  teléfono tiene la respuesta en milisegundos.

### HU-10.2 · Misma salvaguarda en el teléfono

- **Como** usuario, **quiero** que el teléfono se abstenga igual que el escritorio, **para** no recibir
  formas inventadas.
- **Resultado:**
  - Arnés de 248 consultas en el emulador sin red: **0 FP en C** y recall@5 = 1,000 en A, B y D.
  - `criptomoneda` se abstiene en línea (similitud 0,050, P(respaldo) 0,0 %) y en modo avión.
- **Estado:** hecha (emulador).
- **Capturas:**
  - `HU-10.2_movil_arnes_248_resumen.png`
  - `HU-10.2_movil_en_linea_abstencion_criptomoneda.png`
  - `HU-10.2_movil_modo_avion_abstencion_criptomoneda.png`
- **Nota:** en línea el predictor puede añadir abstenciones (RN-06); sin conexión no hay predictor.
  Las dos vías conservan la salvaguarda, pero no son idénticas.

### HU-10.3 · Instalación que no queda a medias

- **Resultado:**
  - APK release arm64 de 22,6 MB, frente al límite de 1,2 GB.
  - No hay modelo que descargar: la app se instala completa o no se instala.
- **Estado:** hecha en cuanto al tamaño. El escenario «almacenamiento insuficiente» lo resuelve el
  instalador de Android (en el emulador se vio `INSTALL_FAILED_INSUFFICIENT_STORAGE`, sin instalación
  parcial). Medición en el teléfono físico: pendiente.

### HU-11 · Interfaz simple y legible

- **Resultado:**
  - Consulta en 2 interacciones: tocar un ejemplo o escribir y pulsar Consultar.
  - Con la letra al máximo (A+ ×2) se leen la forma, la fuente y el aviso, sin recortes. Lo comprueba
    una prueba de widget y la captura.
  - Botones de 48 px o más (prueba).
- **Captura:** `HU-11_movil_letra_maxima_forma_fuente_y_aviso.png`.
- **Pendiente:** Accessibility Scanner en el teléfono.

### HT-05 · Artefactos móviles y equivalencia entre plataformas

- **Resultado:**
  - El índice que exporta hoy el backend del equipo (`8088193`) es idéntico byte a byte al que lleva
    la app (10/10 archivos).
  - `generar_paridad_dart.py` produce el mismo `paridad_esperada.json`.
  - Las 5 pruebas de paridad de Dart pasan.
- **Evidencia:** `HT-05_movil_paridad_indice.png`.

### HU-01, HU-04 y HU-08.1 en la app (solo lectura)

- **Fuentes:**
  - En línea: registro de la nube con entidad y licencia.
  - Sin conexión: documentos del índice, con páginas y fragmentos.
- **Pasajes:** `que es el sufijo ablativo` → «Sin respuesta confirmada» con el pasaje de la p. 133,
  rotulado «no es una respuesta».
- **Predicción ML:** pestaña con las dos probabilidades, la decisión y las 11 variables con su peso
  (coeficiente estandarizado del modelo de cobertura, de `GET /api/modelos`).
  - Es el peso de la variable en el modelo, **no** su contribución exacta a la consulta: la API no expone
    el estandarizador.

## 6. Deuda que queda

1. Mediciones en el teléfono físico de James (latencia en modo avión, arranque, memoria, Accessibility
   Scanner).
2. Latencia en línea con N ≥ 30 desde la app (requiere `TOKEN_PRUEBAS`).
3. Captura del aviso de arranque en frío contra Render dormido. El comportamiento lo cubre una prueba
   de widget.
4. La contribución exacta de cada variable por consulta requeriría que la API exponga la media y la
   desviación del estandarizador. Hoy se muestran los coeficientes.
5. Rotular como `humo` las 6 consultas de prueba de la app que quedaron como `usuario` (decisión del
   equipo; ver la bitácora).
