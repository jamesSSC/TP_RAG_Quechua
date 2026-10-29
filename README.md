# Asistente de consulta del quechua wanka

Producto Mínimo Viable de un asistente conversacional con generación aumentada por
recuperación sobre el corpus documental publicado del quechua wanka de Junín.

Toda respuesta cita el documento y la página que la sustentan, y el sistema declara
explícitamente la ausencia de información en lugar de proponer una forma no documentada.

Este repositorio contiene la **versión de escritorio**: servicio, interfaz web, base de
datos e ingesta documental. La aplicación móvil, que resuelve la consulta en el propio
dispositivo y sin red, vive en
[quechua-wanka-movil](https://github.com/DalgomXD-byte/quechua-wanka-movil) y empaqueta
los artefactos que aquí se generan con `scripts/exportar_indice_movil.py`.

## Arquitectura

Arquitectura hexagonal (puertos y adaptadores). La correspondencia con la estructura
exigida por la consigna es directa; los nombres siguen la convención de Python:

```
backend/
├── domain/                     -> /domain
│   ├── entities/               -> entities
│   ├── value_objects/          -> valueObjects
│   └── ports/                  -> ports (interfaces)
├── application/                -> /application
│   ├── use_cases/              -> useCases
│   └── services/               -> services
└── infrastructure/             -> /infrastructure
    └── adapters/               -> adapters
        ├── input/              -> input (controllers)
        └── output/             -> output (DB, APIs)
```

El núcleo de dominio no conoce ninguna tecnología concreta: solo los puertos. Sustituir
PostgreSQL por SQLite, u Ollama por un motor de inferencia embebido, afecta únicamente al
adaptador correspondiente y se resuelve en `infrastructure/contenedor.py`.

| Puerto | Adaptador actual | Adaptador previsto en el incremento móvil |
|---|---|---|
| `IndiceRecuperacionPort` | Índice híbrido léxico en memoria | El mismo, con índice preconstruido |
| `GeneradorTextoPort` | Ollama por HTTP (Qwen3.5-4B) | llama.cpp embebido (Qwen3.5-0.8B) |
| `TraductorPort` | Ollama por HTTP | llama.cpp embebido |
| `ExtraccionDocumentalPort` | pypdf | No aplica: el corpus viaja preindexado |
| `RepositorioCorpusPort` | Archivo JSONL | SQLite |
| `RepositorioFuentesPort` | PostgreSQL | SQLite |
| `RepositorioConsultasPort` | PostgreSQL | SQLite |
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

## Reparto de roles

| Rol | Responsabilidad en este proyecto | Componentes |
|---|---|---|
| Arquitecto de software | Estructura hexagonal, definición de los puertos y decisiones de sustitución entre incrementos | `domain/ports/`, `infrastructure/contenedor.py` |
| Desarrollador back-end | Casos de uso, reglas de abstención y controladores REST | `application/`, `infrastructure/adapters/input/` |
| Desarrollador front-end | Interfaz de consulta, gestión de fuentes e ingesta documental | `frontend/src/` |
| Desarrollador de base de datos | Modelo relacional, repositorios y persistencia del historial | `infrastructure/adapters/output/persistencia/` |
| Desarrollador de integración | Integración con el servicio de inferencia y el traductor | `infrastructure/adapters/output/ollama_*.py` |

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
