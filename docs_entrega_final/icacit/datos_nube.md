# Datos que salen en la nube (Sociedad, S-01)

Sin secretos. Todo se lee del repositorio (commit `8088193`), sin entrar a ningún panel.

## Qué se envía a Gemini

Fuente: `backend/src/adapters/out/generacion/gemini_generador.py:81-100`.

- Un único mensaje `user` con: la instrucción fija, los **textos de los fragmentos recuperados**
  (`[Fragmento i] texto`) y el **texto de la consulta**.
- **No se envía:** identificador de sesión, IP, historial ni ningún dato personal.
- La clave de Gemini va en la cabecera de la petición y no se registra. Si la aporta el usuario
  (BYOK, ADR-032), solo vive en la memoria de la pestaña.
- **Solo en el modo en la nube**, y solo cuando hay respaldo: las abstenciones no invocan el modelo.
  En el escritorio redacta Ollama, en el propio equipo. En la app sin conexión no sale nada.

## Qué se guarda en Neon y en qué tabla

Fuente: `backend/src/adapters/out/persistencia/modelos.py`.

| Tabla | Columnas |
|---|---|
| `consultas` | id, texto de la consulta, idioma, texto traducido, momento, texto de la respuesta, abstenida, similitud máxima, vía de respaldo, probabilidad de cobertura, probabilidad de pasajes, abstención por predictor, pasajes ofrecidos, latencia en ms, **origen** (`usuario`, `carga`, `arnes`, `humo`) |
| `respaldos` | id, id de la consulta, id del fragmento, documento, página, texto del fragmento, puntuación, derivado de OCR |
| `fuentes` | Registro de las 8 fuentes: título, entidad, licenciamiento, fecha de extracción, archivo, páginas |
| `fragmentos` | Corpus (3 605), cuando `CORPUS_ORIGEN=postgres` |

No se guarda ningún dato personal. La bitácora de seguridad solo registra un seudónimo SHA-256
truncado de la IP (`backend/src/infrastructure/seguridad_nube.py`, `seudonimo`), y no lo guarda en Neon.

## Región

- **Render:** `region: virginia` (`render.yaml:16`, comentario «cerca de Neon (AWS us-east-1)»).
- **Neon:** AWS **us-east-1** (`docs/16_REPORTE_DESPLIEGUE_NUBE.md:29`). Confirmación en el panel:
  **por confirmar con James** (guía 02, paso 6). No se entró a ningún panel.
