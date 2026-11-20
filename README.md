# Asistente de consulta del quechua wanka

Producto Mínimo Viable de un asistente conversacional con generación aumentada por
recuperación sobre el corpus documental publicado del quechua wanka de Junín.

Toda respuesta cita el documento y la página que la sustentan, y el sistema declara
explícitamente la ausencia de información en lugar de proponer una forma no documentada.

Este repositorio contiene el **servicio, la interfaz web, la base de datos y la ingesta
documental**, desplegados también en la nube:

- Web: <https://quechua-web.onrender.com>
- API: <https://quechua-api.onrender.com> (`/docs`, `/api/estado`, `/api/vivo`)
- Base: Neon PostgreSQL (AWS us-east-1). Redacción en la nube: Gemini 3.5 Flash-Lite.

La aplicación móvil (PMV3, ADR-038) vive en
[quechua-wanka-movil](https://github.com/DalgomXD-byte/quechua-wanka-movil). Tiene dos modos:

- **En línea:** cliente de esta API.
- **Sin conexión:** resuelve en el teléfono con los artefactos que aquí se generan con
  `backend/scripts/exportar_indice_movil.py`.

**Requisitos: Python 3.12 (obligatorio, el mismo que fija `render.yaml` y la CI) y Node 22.**

El corpus procesado (`backend/data/fragmentos_v3.jsonl`) no se versiona (ADR-015). Sin él, el
backend arranca, pero las pruebas que lo necesitan se omiten (ver `docs/INSTALACION.md`).

## Arquitectura

Arquitectura hexagonal (puertos y adaptadores). La correspondencia con la estructura
exigida por la consigna es directa; los nombres siguen la convención de Python:

```
backend/src/
├── domain/                     -> /domain
│   ├── entities/               -> entities
│   ├── value_objects/          -> valueObjects
│   └── services/               -> reglas de dominio (evaluador de confianza, verificador literal)
├── application/                -> /application
│   ├── ports/in/  ports/out/   -> ports (7 de entrada, 10 de salida)
│   └── use_cases/              -> useCases (8 casos de uso)
├── adapters/
│   ├── in/rest/  in/cli/       -> input (6 controladores REST y la CLI)
│   └── out/                    -> output (BD, índice, generadores, predictores, traducción)
└── infrastructure/             -> /infrastructure (configuración, contenedor, main, seguridad)
```

El núcleo de dominio no conoce ninguna tecnología concreta: solo los puertos. Sustituir
PostgreSQL por SQLite, u Ollama por un motor de inferencia embebido, afecta únicamente al
adaptador correspondiente y se resuelve en `infrastructure/contenedor.py`.

| Puerto | Adaptadores (local / nube) | En la app móvil sin conexión |
|---|---|---|
| `IndiceRecuperacionPort` | `IndiceHibridoLexico` en memoria | El mismo índice exportado (paridad byte a byte) |
| `GeneradorTextoPort` | Ollama (local) · Gemini (nube) · extractivo y literal (sin modelo) | Compositor determinista (ADR-026) |
| `TraductorPort` | `TraductorTabla` (defecto, `TRADUCTOR=tabla`) · `OllamaTraductor` (`TRADUCTOR=ollama`) | La misma tabla |
| `PredictorPort` | `PredictorSklearn` ×2 (PMV2) | No (se declara en la interfaz) |
| `ExtraccionDocumentalPort` | pypdf | No aplica: el corpus viaja preindexado |
| `RepositorioCorpusPort` | `CorpusJsonl` (local) · `RepositorioCorpusPostgres` (Neon) | Índice exportado |
| `RepositorioFuentesPort` | `RepositorioFuentesSqlalchemy` (SQLite o PostgreSQL) | En línea, de la API |
| `RepositorioConsultasPort` | SQLAlchemy (SQLite) · PostgreSQL con procedimientos | SQLite del teléfono |
| `DetectorIdiomaPort` | Heurístico por palabras funcionales | El mismo |

## Historias de usuario implementadas

| Historia | Descripción | Endpoint | Vista |
|---|---|---|---|
| HU-01 | Registro de fuentes con procedencia y licenciamiento | `/api/fuentes` (CRUD) | Fuentes del corpus |
| HU-01 / HU-02 | Ingesta de PDF, segmentación e indexación | `POST /api/corpus/documentos` | Incorporar documentos |
| HU-03 | Consulta léxica español/inglés | `POST /api/consultas` | Consultar |
| HU-05 | Multilingüismo con traducción previa | Integrada en la consulta | Consultar |
| HU-06 | Salvaguarda antialucinación | Integrada en la consulta | Consultar |
| HU-07 | Trazabilidad documental | Campo `respaldo` de la respuesta | Consultar |
| RF-11 | Historial de sesión | `GET /api/historial` | Consultar |
| RF-13 | Reconstrucción del índice | `POST /api/corpus/reindexar` | Incorporar documentos |
| REF-01 | Prueba de vida para el ping programado, sin tocar la base (ADR-034) | `GET /api/vivo` | — |

## Reparto de roles

| Rol | Responsabilidad en este proyecto | Componentes |
|---|---|---|
| Arquitecto de software | Estructura hexagonal, definición de los puertos y decisiones de sustitución entre incrementos | `backend/src/application/ports/`, `backend/src/infrastructure/contenedor.py` |
| Desarrollador back-end | Casos de uso, reglas de abstención y controladores REST | `backend/src/application/use_cases/`, `backend/src/adapters/in/` |
| Desarrollador front-end | Interfaz de consulta, gestión de fuentes e ingesta documental | `frontend/src/` |
| Desarrollador de base de datos | Modelo relacional, repositorios y persistencia del historial | `backend/src/adapters/out/persistencia/`, `backend/db/postgres/` |
| Desarrollador de integración | Integración con Ollama, Gemini, el traductor y los predictores | `backend/src/adapters/out/{generacion,traduccion,prediccion}/` |

## Resultados medidos

Medidos sobre el corpus real (3605 fragmentos) y el conjunto de evaluación de 248
consultas. Reproducibles con `scripts/calibrar_umbral.py`.

| Métrica | Valor |
|---|---|
| recall@5 (español, subconjuntos A y B) | 1.000 |
| recall@5 (inglés, subconjunto D) | 0.950 con traducción previa · 0.175 sin ella |
| Consultas en inglés atendidas | 90 % con traducción previa · 2,5 % sin ella |
| MRR@10 | 0.992 |
| Latencia de recuperación | 1.7 ms (media) |
| Umbral de abstención calibrado | 0.48 |
| Falsos positivos fuera de cobertura | 0 de 28 |
| Consultas atendibles conservadas | 100 % |
| Latencia de respuesta completa | 3.5 s, incluida la primera consulta |
| Ejecución del modelo | 100 % en GPU (3.1 GB de los 8 GB disponibles) |

Tres desviaciones respecto de la prueba de concepto, todas documentadas en el código:

1. **Umbral 0.48 en lugar de 0.41.** El Documento 6 no fija la fórmula exacta de las
   estrategias E2 y E3; aquí ambas se calculan como coseno sobre TF-IDF. El punto de
   operación se recalibró conforme al procedimiento que el propio documento establece, y
   el resultado mejora al publicado: 100 % de recall conservado frente al 85,6 %.
2. **Capa determinista de coincidencia de lema.** Un término muy frecuente en el corpus
   recibe un IDF bajo, de modo que su propia entrada de diccionario puede quedar por
   debajo del umbral (caso medido: «perro», 0,271). Cuando el término consultado coincide
   exactamente con el lema de una entrada lexicográfica se considera respaldo documental
   sin pasar por el umbral. No puede producir falsos positivos, porque solo se activa si la
   entrada existe literalmente en el corpus.

3. **Se traduce el término depurado, no la pregunta completa.** El experimento E7 preveía
   traducir la consulta antes de recuperar, y la prueba de concepto dejó el requisito RF-04
   pendiente de recalibrar el umbral porque la mitad de las consultas traducidas seguía
   quedando por debajo de la frontera. Medido aquí, la causa es que traducir la pregunta
   entera devuelve también su fraseo en español («cómo se dice X en quechua de Wanka»), que
   reintroduce las palabras que la depuración existe para eliminar. Traduciendo únicamente
   el término ya depurado, las consultas atendidas en inglés pasan del 40 % al 90 % **sin
   modificar el umbral**, de modo que la recalibración prevista en la condición C-4 no
   resulta necesaria.

## PMV2 · Predicción con aprendizaje automático

Dos casos de uso de predicción, integrados en la arquitectura hexagonal mediante el puerto
`PredictorPort` (adaptador `PredictorSklearn`) y expuestos en la pestaña **Predicción ML** y
en cada respuesta:

| Predicción | Historia | Qué estima | Validación cruzada (5 particiones, semilla 2026) |
|---|---|---|---|
| 1 · Cobertura documental | HU-08.1 / RF-14 | Probabilidad de que el corpus respalde la consulta | 415 consultas: AUC 0,996 · F1 0,964 · especificidad 97 % |
| 2 · Relevancia de pasajes | HU-04 / RF-15 | Probabilidad de que los pasajes de prosa traten la pregunta | 167 consultas: AUC 0,980 · pasajes ante preguntas no cubiertas 45,8 % → 9,3 % |

Los modelos solo pueden **añadir** abstenciones o retirar pasajes (RN-06); `scripts/evaluar_pmv2.py`
lo verifica. HU-09 (`GET /api/analitica/demanda`) ordena la demanda insatisfecha ponderada por
el modelo de cobertura. Con `BASE_DATOS=postgres` el historial se escribe y se agrega con
procedimientos almacenados (`backend/db/postgres/procedimientos.sql`).

```bash
python scripts/entrenar_predictores.py      # entrena, valida y guarda modelos/*.joblib
python scripts/evaluar_pmv2.py              # no regresión RN-06
RUTA_SQLITE=carga.db python scripts/generar_transacciones.py 800   # prueba de data masiva
```

Endpoints nuevos: `POST /api/predicciones`, `GET /api/modelos`, `GET /api/analitica/demanda`.
Evidencias en `docs/evidencias/pmv2/`.

## Puesta en marcha y verificación

- Instalación completa del entorno: [docs/INSTALACION.md](docs/INSTALACION.md)
- Colección de Postman con los quince endpoints y sus comprobaciones automáticas:
  [docs/Asistente_Quechua_Wanka.postman_collection.json](docs/Asistente_Quechua_Wanka.postman_collection.json)
- Guion de la demostración: [docs/GUION_DEMO.md](docs/GUION_DEMO.md)
- Batería de pruebas: `pytest tests/` desde `backend/`

## Documentación de la entrega

| Carpeta | Qué contiene | Guía del docente |
|---|---|---|
| [`docs/`](docs/) | Documentación SDD: especificaciones, historias, ADR, sprints y evidencias de desarrollo | — |
| [`docs_auditoria/`](docs_auditoria/) | Auditoría FURPS+ y OWASP (S13) y delta del PMV3 | Guía de calidad (S13) |
| [`docs_ingenieria_inversa/`](docs_ingenieria_inversa/) | Ingeniería inversa: fases, UML v1.1, hallazgos y evidencias antes/después | Guía de ingeniería inversa |
| [`docs_entrega_final/`](docs_entrega_final/) | Métricas, pruebas con usuarios, video, insumos del informe y del artículo, cifras oficiales, Kanban, ICACIT, logo y póster | Lista de cotejo U4 e informe final |

Las guías piden `./docs`; se usan carpetas propias para no mezclarlas con la documentación SDD.

## Alcance declarado

Herramienta de consulta sobre fuentes ya publicadas y validadas. No sustituye la validación
por hablantes de la comunidad ni se constituye en autoridad lingüística sobre la variedad
wanka. Ninguna forma quechua mostrada por el sistema es redactada por el modelo: todas
proceden literalmente de los documentos indexados y se citan con su fuente.

### Limitaciones reconocidas de este incremento

- **HU-04, consulta de contenido cultural, no está evaluada.** El material en prosa se
  indexa y se recupera, pero no existe un conjunto de referencia con pasajes anotados que
  permita medir su desempeño, y construirlo exige criterio lingüístico externo al equipo.
- **El generador puede interpretar de más.** El umbral impide que el sistema invente una
  forma quechua, pero no que el modelo atribuya un significado que el fragmento no declara.
  Se detectó sobre «PERRO: Allqu, ashuti. (perrito) Pichi, uña allqu.», donde el modelo leyó
  *uña* como la palabra castellana en lugar del morfema quechua. La instrucción se endureció
  para prohibir el análisis de morfemas y la deducción por parecido con el castellano, pero
  el riesgo no queda eliminado, solo reducido.
- **Las cifras de los subconjuntos A y B son un límite superior.** El conjunto de evaluación
  deriva del propio corpus indexado, de modo que sobrestima el desempeño en uso real. Un
  conjunto verdaderamente independiente exigiría consultas formuladas por docentes de
  Educación Intercultural Bilingüe o por hablantes de la variedad.
- **El despliegue móvil (PMV3) no forma parte de este incremento.** La analítica predictiva
  (PMV2) sí: ver la sección anterior.
