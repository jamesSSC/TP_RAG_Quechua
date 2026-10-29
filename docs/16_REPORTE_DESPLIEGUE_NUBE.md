# 16 · Reporte de despliegue en la nube (Guía de laboratorio 11)

> Fecha: 2026-10-29 · Entorno: **staging** · Ejecutado desde una PC compartida de la universidad.
> Corpus de staging: **corpus reconstruido, no v3**. Se regeneró con `reparar_ocr.py` a partir de
> `fragmentos_v2.jsonl` (3 605 fragmentos, 8 documentos; SHA-256 del v3 reconstruido
> `d6200ed9…e47470a`).

## 1. URL públicas

| Recurso | URL |
|---|---|
| Frontend (static site) | <https://quechua-web.onrender.com> |
| API | <https://quechua-api.onrender.com> |
| Documentación interactiva | <https://quechua-api.onrender.com/docs> |
| Repositorio | <https://github.com/omarpiero/TP_RAG_Quechua> |
| PR del despliegue | [#17](https://github.com/omarpiero/TP_RAG_Quechua/pull/17) (código), [#18](https://github.com/omarpiero/TP_RAG_Quechua/pull/18) (modelo de Gemini) |
| Commit de partida | `9ca0361` (PR #3 a #16 fusionados) |
| Commit desplegado | `5a4ad44` (fusión del PR #18), con la CI en verde: [ejecución 40964359312](https://github.com/omarpiero/TP_RAG_Quechua/actions/runs/40964359312) |

No se usa `localhost`, `127.0.0.1` ni túneles: todas las pruebas de las §3 y §4 van contra las URL
públicas con HTTPS.

## 2. Topología

| Capa hexagonal | Dónde vive en la nube |
|---|---|
| `domain`, `application` | Render, web service `quechua-api` (plan free, región Virginia), el mismo proceso Python 3.12 |
| `adapters/in` (REST, FastAPI) | Render `quechua-api`, `uvicorn --host 0.0.0.0 --port $PORT` (ADR-030) |
| `adapters/out` | Persistencia y corpus: **Neon PostgreSQL** (plan free, AWS us-east-1, base `neondb`, conexión con *pooling*). Redacción: **API de Gemini** (Google AI Studio, plan gratuito). Modelos ML: archivos `joblib` dentro del servicio |
| `infrastructure` | `contenedor.py` elige los adaptadores por variables de entorno. `render.yaml` define el Blueprint |
| Interfaz React | Render, static site `quechua-web` (CDN de Render), con reescritura de rutas de la SPA |
| CI/CD | GitHub Actions (`.github/workflows/ci.yml`). Render despliega `main` cuando la CI pasa (`autoDeployTrigger: checksPass`) |

**Variables de entorno de `quechua-api`** (solo los nombres):
- `PYTHON_VERSION`, `ENTORNO`, `BASE_DATOS`, `CORPUS_ORIGEN`, `GENERADOR`, `GEMINI_MODELO`, `TRADUCTOR`, `UMBRAL_ABSTENCION`, `CORS_ORIGENES`;
- secretas: `DATABASE_URL`, `GEMINI_API_KEY` y `TOKEN_PRUEBAS`.

**`quechua-web`:** `NODE_VERSION` y `VITE_API_URL`.

**Adaptadores que cambian entre E1 (local) y la nube:**

| Puerto | E1 (local) | Nube (staging) |
|---|---|---|
| `RepositorioCorpusPort` | `CorpusJsonl` (archivo) | `RepositorioCorpusPostgres` (tabla `fragmentos` en Neon), ADR-031 |
| `RepositorioConsultasPort` / `RepositorioFuentesPort` | SQLite | PostgreSQL en Neon, con procedimientos almacenados |
| `GeneradorTextoPort` | Ollama + Qwen 3.5 4B (GPU), extractivo verificado (ADR-028) | **Gemini 3.5 Flash-Lite**, extractivo verificado (ADR-028/032). Sin clave, con 429, error o 15 s: fragmento literal citado |
| `TraductorPort` | Tabla | Tabla (sin cambio: Gemini no traduce) |
| Almacén de PDF | Disco | Ninguno: los PDF persisten como fragmentos en Neon |

RN-06 y τ = 0,48 no cambian (`/api/estado` → `umbral_abstencion: 0.48`).

## 3. Matriz de pruebas en la nube

Evidencia: `docs/evidencias/nube/humo_2026-10-29_2219.json` (origen `humo`, 5 repeticiones por caso
tras un primer intento aparte). Las latencias de C-01/C-03 de esa corrida corresponden a
**Gemini 3.8 Flash**, que agotaba los 15 s (ver §4.3). Con **Flash-Lite**, el modelo final, las
afirmativas tardan alrededor de 1 s (`gemini_flash_lite_2026-10-29.txt`).

| Caso | Historia | Given / When / Then | Entrada | Obtenido en la nube | P50 / P95 | Estado |
|---|---|---|---|---|---|---|
| C-01 | HU-03 / HU-07 | Dado el corpus en Neon, cuando se consulta un término documentado, entonces responde con cita | «¿cómo se dice zorro en quechua wanka?» | Flash-Lite: «En quechua wanka, «zorro» se dice Atuq.», `redactado_por: gemini`. Cita: diccionario, p. 37, similitud 0,6095, P(cobertura) 0,9995 | 1,09 s (Flash-Lite) · 15,4 / 15,6 s (3.8 Flash, respaldo) | APROBADO |
| C-03 | HU-05 | Consulta en inglés, traducida por la tabla | «how do you say fox in Wanka Quechua?» | «In Wanka Quechua, «zorro» is Atuq.» (gemini), p. 37 | 0,86 s (Flash-Lite) | APROBADO |
| C-02 | HU-06 | Término ausente: abstención explícita, sin llamar a Gemini | «¿cómo se dice criptomoneda en quechua wanka?» | Abstención; no propone forma | 0,15 / 0,17 s | APROBADO |
| HU-04 | HU-04 / RF-15 | Pregunta de prosa: pasajes rotulados «no es una respuesta» | «¿Qué sufijo se usa para marcar localización espacial o temporal?» | Abstención con pasajes de la gramática | 0,20 / 0,21 s | APROBADO |
| C-05 | HU-06 | Fuera de dominio | «¿Cuál es el procedimiento para renovar un pasaporte?» | Abstención | 0,20 / 0,21 s | APROBADO |
| C-07 | Validación | Vacía y de 301 caracteres | `""`, `"a"×301` | HTTP 422 en ambas | 0,12–0,13 s | APROBADO |
| RF-11 | Historial | `GET /api/historial` | — | 200, con las consultas de la sesión | 0,15 s | APROBADO |
| HU-01 | CRUD de fuentes | Crear, listar, editar, borrar y comprobar 404 | Fuente de prueba | 201 · 200 · 200 · 204 · 404 | ≈ 0,15 s cada paso | APROBADO |
| HU-02 | Incorporar PDF que persista tras redespliegue | Subir PDF → *Manual Deploy* → consultar | PDF de prueba | **Pendiente (U8)**: lo ejecuta el usuario en la interfaz | — | PENDIENTE |
| HU-08.1 | Cobertura | Consulta cubierta y fuera de cobertura | zorro / criptomoneda | Cubierta: similitud 0,61, margen 0,40. Fuera: similitud 0,05 | 0,20 / 0,29 s · 0,14 / 0,20 s | APROBADO |
| RF-15 | Pasajes | Prosa cubierta / no cubierta | sufijo / pasaporte | Pasajes ofrecidos / sin pasajes | ver HU-04 y C-05 | APROBADO |
| HU-09 | Analítica | Real: insuficiencia. Con sintéticas: demostración rotulada | `GET /api/analitica/demanda` | Real: «Historial insuficiente: hay 10 consultas» (mínimo 100). Con sintéticas: 554 consultas, `base_demostracion: true` y aviso en la interfaz | 0,19 / 0,21 s | APROBADO |
| Procedimientos | Neon | `fn_resumen_demanda()` | SQL Editor de Neon | Instalados: 5 funciones y 2 procedimientos (§5). Captura U7 del usuario | — | APROBADO |

**Salvaguarda observada en la nube:**
- Con Flash-Lite, en «agua» el verificador de la ADR-028 rechazó la extracción de Gemini. Se mostró el fragmento literal con el motivo «verificador: forma o glosa ausentes del fragmento».
- Con 3.8 Flash, un HTTP 503 y varios tiempos agotados terminaron igual: fragmento literal citado y motivo visible. Ninguna forma quechua salió de Gemini sin estar en el fragmento.

## 4. Métricas en la nube

### 4.1 API

| Medida | Valor | Fuente |
|---|---|---|
| Arranque en frío del plan free | **Pendiente**: medir con `humo_nube.py` tras 15 min sin tráfico (el servicio estaba despierto: `/api/estado` respondió en 0,24 s) | — |
| `/api/estado` | 0,24 s, primer intento con el servicio despierto | `humo_*.json` |
| Consultas que se abstienen | P50 0,15–0,20 s | `humo_*.json` |
| Consultas afirmativas con Gemini Flash-Lite | 0,81–1,09 s en el servidor (5 consultas) | `gemini_flash_lite_2026-10-29.txt` |
| Predicción ML (`/api/predicciones`) | P50 0,14–0,20 s · P95 0,20–0,29 s | `humo_*.json` |
| Analítica, historial, modelos | P50 0,12–0,21 s | `humo_*.json` |
| Memoria en Render | **Pendiente (U10)**. Referencia local: pico de 217 MB con el corpus completo, frente a 512 MB del plan free | `pc_universidad/P08_memoria_local.txt` |

### 4.2 Carga (500 consultas, origen `carga`)

| Medida | Valor |
|---|---|
| Consultas / errores | 500 / **0** (todas HTTP 200) |
| Lotes | 25 consultas + 2 s de espera |
| Duración | 265,7 s |
| Transacciones por segundo | 2,22 sin contar las esperas · 1,88 contándolas |
| Latencia | P50 484 ms · P95 624 ms · media 451 ms |
| Filas en Neon tras la carga | `carga` 500 · `humo` 2 · `usuario` 6 |

Durante la carga, Gemini devolvía 404: el modelo `gemini-2.5-flash` ya no existe, y se corrigió en
el PR #18. La carga mide por tanto la API y Neon con el respaldo extractivo, sin gastar la cuota
gratuita de Gemini. Evidencia: `docs/evidencias/nube/carga_2026-10-29_2210.json`.

### 4.3 Gemini en la nube frente a Qwen local (ADR-032)

Regla v2 de `medir_fidelidad.py`, aplicada sobre las 120 primeras consultas del subconjunto A.

| Medida | Qwen 3.5 4B local (B11, cierre U3) | Gemini 3.5 Flash-Lite (nube) |
|---|---|---|
| Respuestas con contradicción potencial de la glosa | 0 / 109 (0,0 %) | 0 / 90 (0,0 %) |
| Respuestas sustituidas por el fragmento literal | 11 / 120 (9,2 %) | 30 / 120 (25,0 %): 10 por el verificador (8,3 %) y 20 por cuota agotada (429) |
| Latencia P50 / P95 | 2 594 / 2 681 ms (GPU RTX 4060) | 772 / 1 017 ms (servidor; media 736 ms) |
| Errores 429 | No aplica | 20 / 120 (16,7 %), con 2 s de pausa entre consultas |

Fuentes:
- Qwen: `docs/evidencias/cierre_u3/b11_fidelidad/despues_v2_verificador_por_entrada/resumen.json`. En el repositorio no se encontró el rótulo «M-23»; esta es la medición equivalente.
- Gemini: `docs/evidencias/nube/gemini_fidelidad_*.json`.

Lectura: con la misma regla, Gemini no introdujo contradicciones; el verificador rechazó una
proporción parecida a la de Qwen (10 de 100 respuestas sin 429, frente a 11 de 120). Los 429 son
el límite por minuto del plan gratuito: con más pausa entre consultas desaparecerían, pero no se
repitió la medición para no gastar cuota. Muestra: las 120 consultas completas.

**Gemini 3.8 Flash** (el primer modelo probado) en el plan gratuito: de unas 14 llamadas, 1 redactó
(10,9 s), 1 devolvió HTTP 503 y el resto agotó los 15 s. Se cambió a **Flash-Lite** por latencia y
cuota. `gemini-2.5-flash` devolvía 404 porque fue retirado.

### 4.4 Newman (colección Postman con el entorno de la nube)

15 peticiones y 39 aserciones, **0 fallos**. Evidencia:
`docs/evidencias/nube/newman_2026-10-29.{txt,json}`.

La primera corrida tuvo 5 fallos por un defecto del archivo de entorno, no de la API: la variable
`fuente_id` vacía tapaba la variable de la colección. Se corrigió y se borró la fuente de prueba que
había quedado.

### 4.5 CI

GitHub Actions, en verde en `e296c1d` y `5a4ad44`:
- backend: pytest con un PostgreSQL de servicio (incluye las pruebas de integración del corpus y de los procedimientos) y pip-audit;
- frontend: vitest y build.

Las pruebas que necesitan el corpus se omiten por marcador.

## 5. Base de datos (Neon)

| Momento | `fragmentos` | `fuentes` | `consultas` |
|---|---|---|---|
| Tras el *seeding* (`sembrar_nube.py`) | 3 605 | 8 | 0 |
| Segunda ejecución del *seeding* (idempotencia) | +0 | +0 | — |
| Tras humo, Newman y carga | 3 605 | 8 | 554 (`carga` 500, `humo` 44, `usuario` 10) |
| Tras la medición de Gemini (120 consultas `humo`) | 3 605 | 8 | 670 (`carga` 500, `humo` 160, `usuario` 10) |

Fragmentos por documento: 2 351 · 24 · 2 · 204 · 32 · 71 · 119 · 802
(`fn_fragmentos_por_documento()`).

**Rutinas instaladas:**
- procedimientos: `sp_registrar_consulta` y `sp_borrar_historial`;
- funciones: `fn_resumen_demanda`, `fn_respaldo_por_documento`, `fn_demanda_insatisfecha`, `fn_conteo_por_origen` y `fn_fragmentos_por_documento`.

Las 10 consultas de origen `usuario` vienen de Newman (6) y de las capturas automáticas de
Playwright (4): ninguna de las dos herramientas envía el token de pruebas.

## 6. Pruebas en la PC de la universidad

| Prueba | Sin corpus (como en la CI) | Con el corpus reconstruido |
|---|---|---|
| pytest | 323 pasan, 4 omitidas, **10 errores** (línea base de `main`) → 354 pasan, 16 omitidas, 0 errores (rama nube) | 333 → 365 pasan, 6 omitidas |
| Arnés, τ = 0,48 | — | VP 180 · FP 0 · VN 28 · FN 0 → precisión 1,0, recall 1,0 |
| vitest / build | 30 → 34 pasan / correcto | — |
| pip-audit | sin vulnerabilidades conocidas | — |

El arnés coincide con la línea base congelada del PMV2: 0 falsos positivos en C con τ = 0,48.
Evidencia: `docs/evidencias/nube/pc_universidad/P01…P18` (registros de texto y PNG).

## 7. Capturas

**Del agente:**
- automáticas con Playwright contra la URL pública: `docs/evidencias/nube/capturas_agente/00…08_*.png` (estado, zorro, fox, criptomoneda, sufijo, validación, predicción, fuentes e incorporar);
- de los pasos en la PC (registros convertidos en PNG): `docs/evidencias/nube/pc_universidad/`;
- de pantalla completa de cada paso: `D:\Quechua\capturas_pasos\`, fuera de Git porque muestran la sesión del usuario.

**Del usuario** (carpeta `capturas_nube`, con la barra de direcciones visible):

| # | Captura | Estado |
|---|---|---|
| U0 | PR fusionado y checks en verde | Hecho por el usuario (PR #17 y #18 fusionados): falta confirmar que el archivo existe |
| U1 | Panel de Neon con el proyecto | Falta confirmar |
| U3 / U3b | Blueprint de Render / clave en AI Studio | Falta confirmar |
| U4 | Logs «Your service is live» | Falta confirmar |
| U6 / U7 | Neon › Tables y SQL Editor | Tablas listas según el usuario |
| U8 | Casos de la §3 en la web pública, incluido HU-02 | **Pendiente** |
| U9 | Neon › `consultas` con filas nuevas | **Pendiente** |
| U10 | Render › Logs y Metrics (memoria) | **Pendiente** |
| U11 | GitHub › Actions y árbol `backend/src` | **Pendiente** |

## 8. Limitaciones declaradas

- **Redacción con Gemini en la nube** (ADR-032):
  - depende de la cuota gratuita, que es baja y variable;
  - envía el texto de la consulta y los fragmentos a Google, sin datos personales; la interfaz lo avisa;
  - sin clave, con 429, error o 15 s se usa el fragmento literal citado;
  - el modelo Flash más reciente (3.8) no respondió a tiempo en el plan gratuito.
- **Plan gratuito de Render:** se suspende tras 15 minutos sin uso; la primera petición sufre un arranque en frío de unos 50 s.
- **PDF incorporados:** persisten como fragmentos en Neon, no como archivos (disco efímero).
- **Historial en la nube:** es compartido por todos los visitantes (una sola base), y «Borrar historial» lo borra para todos. Aceptable en staging; no lo sería en producción sin autenticación.
- **Licencias del corpus:** pendientes de verificar. Las fuentes sembradas dicen «Pendiente de verificar (ADR-015)».
- **Corpus reconstruido:** no es el v3 original. `evaluacion_prosa.json` no se pudo regenerar (necesita Ollama), así que no hay métricas de prosa nuevas.
- **Equipo:** 3 personas para los 5 roles de la guía.

## 9. Incidencias y cómo se resolvieron

| Incidencia | Resolución |
|---|---|
| `uv venv --python 3.12` falló: la PC no permite crear el enlace de versión menor | Se usó directamente el Python 3.12.16 que descargó uv (`python -m venv`) |
| No estaban `fragmentos_v3.jsonl` ni `evaluacion_prosa.json` | Con aprobación del usuario se regeneró v3 desde v2 con `reparar_ocr.py`. La evaluación de prosa no se regenera porque necesita el LLM |
| Push denegado (403) al repositorio de omarpiero | Fork `jamesSSC/TP_RAG_Quechua` y PR hacia `omarpiero:main` |
| CI roja en Linux (vitest): una prueba nueva simulaba una respuesta incompleta | Respuesta simulada completa (`7e5df02`) |
| Primer despliegue de `quechua-api` fallido | Arrancó antes del *seeding*: con la base vacía el índice no se construye. Se sembró Neon y se volvió a desplegar |
| `.env` con `DATEBASE_URL` (error de escritura) | Se corrigió solo el nombre de la variable, sin leer su valor |
| Gemini 404 (`gemini-2.5-flash` retirado) | PR #18: `gemini-3.8-flash` con `thinkingLevel: low` (3.8 rechaza `minimal`) |
| Gemini 3.8 Flash agotaba 15 s o devolvía 503 | `GEMINI_MODELO=gemini-3.5-flash-lite`: unos 1 s por consulta |
| Newman: 5 fallos por `fuente_id` vacío en el entorno | Se quitó la variable del entorno y se borró la fuente de prueba que quedó |
| La interfaz decía «Ollama responde» y «solo en este equipo» en la nube | Textos condicionados al entorno (rama `docs/reporte-nube`) |
| `TOKEN_PRUEBAS` pegado en el chat | Se usó solo como variable de entorno; **regenerarlo en Render** al terminar |
