# 08 · Auditoría delta FURPS+/OWASP del PMV3

| Dato | Valor |
|---|---|
| Fecha | 2026-11-20 |
| Alcance | Solo lo que agregó el PMV3 y los arreglos de la S14: app móvil en dos modos (`quechua-wanka-movil`, rama `feat/pmv3-dos-modos`), cabeceras del sitio estático, CI y dependencias. Lo ya auditado en la S13 (01 a 07) no se repite |
| Ramas auditadas | App: `feat/pmv3-dos-modos` (`e7005b5`…`48f5c63`). Backend y web: `fix/s14-arreglos-rapidos` (`54385b0`), `feat/logo-proyecto` (`df6cf5e`), `feat/pmv3-app-movil` (`4f75b02`) |
| Criterios | Los mismos de la S13: FURPS+ como media de 6 dimensiones (0–10) y OWASP Top 10 como suma de 10 categorías (0–10 cada una, máximo 100) |
| Contra la nube | Solo `GET /api/estado`, `GET /api/vivo`, `GET /api/analitica/demanda`, `curl -sI` y un `POST` sin cuerpo ni token (401). Las 6 consultas de la app están anotadas en `docs/evidencias/pmv3/BITACORA.md` |

Igual que en la S13, el dictamen tiene dos planos. Lo que se puntúa es **la rama**. En la nube los
cambios de la S14 (CSP del sitio estático) aparecen recién cuando `main` se despliegue.

## 1. Superficie nueva del PMV3

| Elemento | Qué añade | Comprobación |
|---|---|---|
| Endpoints | **Ninguno nuevo.** La app consume los públicos de lectura (`POST /api/consultas`, `POST /api/predicciones`, `GET /api/modelos`, `GET /api/fuentes`, `GET /api/estado`) | `test/seguridad_test.dart`: los únicos POST de la app son esos dos |
| Tokens en la app | Ninguno: ni `ADMIN_TOKEN` ni `TOKEN_PRUEBAS` ni claves | `test/seguridad_test.dart` falla si aparecen en `lib/` |
| Permisos Android | `INTERNET` (tras D-01) | `aapt dump permissions` del APK release |
| Almacenamiento local | SQLite con el historial (consulta, respuesta, si hubo respaldo, similitud, hora, modo) y dos preferencias (modo y tamaño de letra) | `historial_sqlite.dart`. Sin datos personales |
| Red | HTTPS hacia `quechua-api.onrender.com` por defecto. En release, Android bloquea el tráfico en claro (`targetSdk` ≥ 28, sin `usesCleartextTraffic`) | Manifiesto y `--dart-define=API_URL` |
| Dependencias | `http`, `sqflite`, `path` (ya estaban). Nueva: `flutter_launcher_icons` (**solo desarrollo**, genera el ícono) | `pubspec.yaml` |

## 2. Hallazgos nuevos

| ID | Categoría | Severidad | Hallazgo | Estado |
|---|---|---|---|---|
| **PMV3-D01** | FURPS R / OWASP A05 | **Alta** (funcional) | El `AndroidManifest.xml` principal no declaraba `android.permission.INTERNET` (solo debug y profile). En el APK release el modo en línea nunca conectaba y la app caía siempre al corpus local | **Corregido** en `48f5c63`. `aapt`: antes sin permiso, después con él. Release en el emulador: «En línea · nube» con los datos de `/api/estado`. Evidencia: `evidencias/delta_pmv3/PMV3-D01_*` |
| **PMV3-D02** | OWASP A02 / privacidad | Baja | `allowBackup` por defecto (`true`): la copia de seguridad de Android podía sacar del teléfono el historial, cuando la interfaz dice «se almacenan solo en este teléfono» | **Corregido** en `48f5c63` (`allowBackup=false`, `fullBackupContent=false`) |
| PMV3-D03 | OWASP A09 / integridad de la analítica | Media | Las consultas de la app a la nube cuentan como `usuario` (HU-09), porque la app no puede llevar el token de pruebas | **Aceptado y documentado** (ADR-038). Las 6 consultas de prueba están identificadas en la bitácora para rotularlas como `humo` |
| PMV3-D04 | OWASP A02 | Baja | El historial SQLite no está cifrado. Queda en el almacenamiento privado de la app (sandbox) y no contiene datos personales | **Aceptado** |
| PMV3-D05 | OWASP A02 | Baja | Sin *certificate pinning* hacia Render | **Aceptado** (dominio gestionado por Render y Cloudflare; el pinning rompería la app al rotar certificados) |
| PMV3-D06 | OWASP A06 | Baja | `sqflite` 2.4.4 (hay 2.4.6) y `cupertino_icons` 1.0.9 (hay 2.0.0) desactualizados. No hay avisos de seguridad publicados para esas versiones en la salida de `flutter pub outdated` | **Mantenimiento**: actualizar en el próximo ciclo |
| PMV3-D07 | FURPS F | Informativo | En línea y sin conexión no son idénticos: sin conexión no hay predictor ML (RN-06) ni Gemini; decide τ = 0,48 con el compositor determinista. La salvaguarda se conserva (0 FP en C en el dispositivo) | **Documentado** (ADR-038 y la interfaz lo dice) |
| **S14-01** | OWASP A04 / A01 (interfaz) | Media | Mientras `/api/estado` no respondía (arranque en frío de Render, ~1 min) o si fallaba, la web mostraba desbloqueadas «Fuentes del corpus» e «Incorporar documentos» y pedía `/api/historial`: `protegida = Boolean(estado?.escritura_protegida)` valía `false` con `estado = null`. La API seguía rechazando las escrituras sin token (401, ADR-035), así que no se expusieron datos | **Corregido** en la rama `fix/web-bloqueo-por-defecto`: la web bloquea por defecto y solo desbloquea con `escritura_protegida === false` confirmado por la API o con el token validado. Vitest `BloqueoPorDefecto.s14.test.jsx` (5 casos). Playwright con `/api/estado` retrasado 20 s y caído. Evidencia: `evidencias/antes/S14-01_antes_*`, `evidencias/despues/S14-01_despues_*`. La app móvil no tiene el patrón: no administra nada y no pide `/api/historial` (`asistente_nube.dart`) |

## 3. Herramientas

| Herramienta | Resultado | Antes (S13) |
|---|---|---|
| `pip-audit -r requirements.txt` | **No known vulnerabilities found** | 0 |
| `npm audit` | **0 vulnerabilidades** (tras `npm audit fix` en la S14) | 3 altas (OW-14) |
| `flutter pub outdated` | 2 dependencias directas con versión nueva menor; sin avisos de seguridad | — |
| `ruff check src tests` | Sin errores (era 1, B905) | 1 |
| `bandit -q -r src -ll` | 0 de severidad media o alta (3 bajas) | No estaba en la CI |
| `flutter analyze` | Sin avisos | — |
| CSP del sitio estático | Build de producción servido con las cabeceras de `render.yaml`: **0 violaciones** | Sin CSP (OW-10) |

## 4. Puntajes

### FURPS+ (media de 6 dimensiones)

| Dimensión | S13 | PMV3 | Motivo |
|---|---|---|---|
| F | 8,0 | 8,25 | App en dos modos con consulta, abstención, pasajes, predicción ML y fuentes. HU-10.x verificadas en emulador; teléfono físico pendiente |
| U | 7,75 | 8,0 | A−/A/A+ y botones de 48 px o más en la app; aviso de arranque en frío con el mismo texto que la web; modo siempre visible |
| R | 6,75 | 7,0 | Con la nube caída o dormida la app sigue respondiendo (respaldo medido: 20 ms en modo avión); prueba de recuperación real en la CI (H-02). Resta: arranque en frío de Render de 62–72 s |
| P | 6,5 | 6,5 | Sin cambio: la latencia en línea desde la app con N ≥ 30 sigue sin medir (requiere `TOKEN_PRUEBAS`) |
| S | 9,25 | 9,5 | README y `.env.example` al día, `NIVEL_LOG`, nombre correcto del repositorio, corpus reconstruible |
| + | 6,25 | 6,5 | ruff, Bandit y `npm audit` en la CI |
| **Media** | **7,4** | **7,6** | (8,25 + 8,0 + 7,0 + 6,5 + 9,5 + 6,5) / 6 = 7,625 |

### OWASP Top 10 (suma, máximo 100)

| Categoría | S13 | PMV3 | Motivo |
|---|---|---|---|
| A01 Broken Access Control | 7 | 7 | La app no administra (prueba). OW-03 sigue parcial: la analítica es pública, aunque hoy vacía (`suficiente: false`) |
| A02 Cryptographic Failures | 10 | 10 | HTTPS en release; D-02 corregido; D-04 y D-05 aceptados |
| A03 Injection | 9 | 9 | Sin cambios |
| A04 Insecure Design | 6,5 | 6,5 | OW-08 aceptado (ADR-037); 429 probado de punta a punta desde la app sin reintentos |
| A05 Security Misconfiguration | 6 | 7,5 | OW-10 (CSP del sitio estático) implementado en la rama; D-01 corregido. Sigue OW-12 (OpenAPI pública) |
| A06 Vulnerable Components | 6,5 | 8 | OW-14 implementado (`npm audit` 3 → 0 y en la CI); `pip-audit` 0; D-06 menor |
| A07 Authentication Failures | 9 | 9 | Sin cambios |
| A08 Integrity Failures | 6,5 | 6,5 | OW-17 sin cuarentena (evaluado en B13: aceptar con rotación de tokens) |
| A09 Logging and Monitoring | 8,5 | 8,5 | Nivel de registro configurable (H-09); D-03 documentado |
| A10 SSRF | 10 | 10 | Sin cambios |
| **Total** | **79,0** | **82,0** | |

## 5. Correcciones al informe S13

En `docs_auditoria/` no aparecen los errores señalados (se comprobó con `grep`): están en el informe en
Word. La tabla con cada corrección y su fuente (`config.py:93`, `api.js:8`, `06_…:146`,
`02_plan_furps.md:32`) está en `docs_entrega_final/calidad/arreglos_rapidos.md`, grupo 4.

## 6. Dictamen

- **Rama:** favorable. Lo que bloqueaba (D-01) ya está corregido y verificado en un APK release.
- **Nube:** los controles de la S13 están desplegados (`/api/historial` y la ingesta devuelven 401 sin
  token; `/api/estado` informa `escritura_protegida: true`). La CSP del sitio estático y los cambios
  de la S14 llegarán cuando se fusione y despliegue `main`; ese despliegue es una acción manual de quien
  tenga la cuenta de Render.
- **Pendiente:** mediciones en el teléfono físico (ARM64) y latencia en línea con N ≥ 30 con
  `TOKEN_PRUEBAS`.
