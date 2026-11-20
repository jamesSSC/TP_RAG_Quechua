# rama fix/s14-arreglos-rapidos (sin commit aun; ver PR)
$ grep -nE "Python 3.12|quechua-api|docs_auditoria|docs_entrega|docs_ingenieria|backend/src" README.md
13:- API: <https://quechua-api.onrender.com> (`/docs`, `/api/estado`, `/api/vivo`)
23:**Requisitos: Python 3.12 (obligatorio, el mismo que fija `render.yaml` y la CI) y Node 22.**
34:backend/src/
82:| Arquitecto de software | Estructura hexagonal, definición de los puertos y decisiones de sustitución entre incrementos | `backend/src/application/ports/`, `backend/src/infrastructure/contenedor.py` |
83:| Desarrollador back-end | Casos de uso, reglas de abstención y controladores REST | `backend/src/application/use_cases/`, `backend/src/adapters/in/` |
85:| Desarrollador de base de datos | Modelo relacional, repositorios y persistencia del historial | `backend/src/adapters/out/persistencia/`, `backend/db/postgres/` |
86:| Desarrollador de integración | Integración con Ollama, Gemini, el traductor y los predictores | `backend/src/adapters/out/{generacion,traduccion,prediccion}/` |
167:| [`docs_auditoria/`](docs_auditoria/) | Auditoría FURPS+ y OWASP (S13) y delta del PMV3 | Guía de calidad (S13) |
168:| [`docs_ingenieria_inversa/`](docs_ingenieria_inversa/) | Ingeniería inversa: fases, UML v1.1, hallazgos y evidencias antes/después | Guía de ingeniería inversa |
169:| [`docs_entrega_final/`](docs_entrega_final/) | Métricas, pruebas con usuarios, video, insumos del informe y del artículo, cifras oficiales, Kanban, ICACIT, logo y póster | Lista de cotejo U4 e informe final |
