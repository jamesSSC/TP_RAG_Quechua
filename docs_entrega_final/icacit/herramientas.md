# Herramientas con su versión real (H-01, H-02)

Versiones leídas del entorno el 19–20/11/2026 (`pip freeze` del entorno de medición, `package.json`,
`pubspec.yaml`, `flutter --version` y los workflows de CI).

| Herramienta | Versión | PMV en que entra | Uso | Captura |
|---|---|---|---|---|
| Python | 3.12 (obligatorio; `render.yaml`, CI) | PMV1 | Backend y guiones | Terminal (`docs_ingenieria_inversa/evidencias/`) |
| FastAPI / uvicorn | 0.162.0 / 0.34.0 | PMV1 | API REST hexagonal | Swagger en `/docs` (por capturar con el backend en marcha) |
| scikit-learn | 1.6.0 | PMV1 (TF-IDF) y PMV2 (predictores) | Índice y regresión logística | Figuras de `../metricas/evidencias/` |
| SQLAlchemy / psycopg | 2.0.36 / 3.2.3 | PMV1–PMV2 | Persistencia SQLite y PostgreSQL | — |
| pypdf | 6.21.4 | PMV1 | Ingesta de PDF | — |
| numpy / joblib | 2.2.1 / 1.6.0 | PMV2 | Modelos | — |
| pytest / ruff / bandit / pip-audit | 9.2.0 / 0.17.6 / 1.9.4 / ver CI | PMV1–S14 | Pruebas y calidad | `H-08_despues_ci_ubuntu_run.png` |
| matplotlib | 3.11.2 | Entrega final | Figuras de métricas | `../metricas/evidencias/*.png` |
| React + Vite | ver `frontend/package.json` (React 19, Vite 8.3.x) | PMV1 | Web | `../logo/B11_web_local_despues_con_logo.png` |
| Vitest / Playwright / oxlint | 5.0.3 / 1.64.1 / ver `package.json` | PMV1–S13 | Pruebas de la web, capturas, lint | `../logo/` |
| Flutter / Dart | 3.44.9 / 3.12 | PMV3 | App en dos modos | `docs/evidencias/pmv3/movil/` |
| Android Studio (emulador) | Pixel 9 Pro, API 37 | PMV3 | Pruebas del teléfono | `docs/evidencias/pmv3/movil/` |
| Ollama + Qwen3.5 4B | `qwen3.5:4b` | PMV1 | Redacción local | `../metricas/evidencias/latencia_local_qwen_gpu.json` |
| Gemini | 3.5 Flash-Lite | PMV2 (nube) | Redacción en la nube | — |
| PostgreSQL / Neon | 16 en la CI / Neon (plan gratuito) | PMV2 | Base en la nube | **Por capturar** (cuenta de James; sin la cadena de conexión) |
| Render | plan gratuito | PMV2 | Despliegue | **Por capturar** (cuenta de otro integrante) |
| GitHub / GitHub Actions | — | Todos | Repositorio y CI | `H-08_despues_ci_ubuntu_run.png` |
| Trello | — | Todos | Kanban | Lo captura Omar |
| Postman / Newman | Newman 6 | PMV1–PMV2 | Pruebas de endpoints | `docs/Asistente_Quechua_Wanka.postman_collection.json` |
| Claude Code (asistente de IA) | — | Todos | Programación asistida y redacción de evidencias, bajo revisión humana | Declarar en el informe (quién hizo qué) |
