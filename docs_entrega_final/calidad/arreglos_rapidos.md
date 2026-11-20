# B13 · Arreglos rápidos de calidad, con capturas de antes y después

Atiende el bloque B13 del paquete de la entrega final: indicador 8 de la lista de cotejo U4 y
secciones 8.9/8.10 del informe. La guía pide `./docs`; se usó `./docs_entrega_final` para no mezclarla
con la documentación SDD de `docs/`.

- **Rama:** `fix/s14-arreglos-rapidos`. **Commit:** `54385b0`. **Base:** `8088193`.
- **Capturas:** en `docs_ingenieria_inversa/evidencias/{antes,despues}/`, cada `.txt` con su `.png`
  (tema claro, letra de 16 px, comando y hora UTC en la cabecera).

> **Aviso sobre los identificadores.** El reporte de ingeniería inversa v1.1, que define los 17
> hallazgos, no está en el repositorio ni en el paquete. La tabla del paquete agrupa
> H-03 y H-05 a H-08 en el grupo 1 y describe la captura de cada arreglo, pero no dice qué ID
> corresponde a cuál. La asignación de abajo es la más probable según esa descripción. **Debe
> cotejarse con el reporte v1.1 antes de pasarla al informe.**

## Tabla

| ID | Arreglo | PR | Commit | Antes | Después | Verificación (comando → resultado) |
|---|---|---|---|---|---|---|
| H-03 | `.env.example` con las variables de la nube, sin valores (`ENTORNO`, `CORPUS_ORIGEN`, `DATABASE_URL`, `GENERADOR`, `GEMINI_*`, `CORS_ORIGENES`, `ADMIN_TOKEN`, `TOKEN_PRUEBAS`, límites, `TRADUCTOR`, `NIVEL_LOG`) | por abrir | `54385b0` | `antes/H-03_antes_env_example_sin_nube.png` | `despues/H-03_despues_env_example_con_nube.png` | `grep -nE "ENTORNO\|DATABASE_URL\|…" backend/.env.example` → 0 líneas antes, 11 después |
| H-05 | `npm audit fix` (vite, undici, source-map-js) | por abrir | `54385b0` | `antes/H-05_antes_npm_audit_3_altas.png` | `despues/H-05_despues_npm_audit_0.png` | `npm audit` → 3 altas → **0**; `vitest` 46/46 y `vite build` correcto tras el cambio |
| H-06 | README al día: Python 3.12 obligatorio, árbol real `backend/src/`, adaptadores actuales, nube (URL), app en dos modos y enlaces a `docs_auditoria/`, `docs_ingenieria_inversa/` y `docs_entrega_final/` | por abrir | `54385b0` | `antes/H-06_antes_readme.png` | `despues/H-06_despues_readme.png` | `grep` de esas cadenas → antes solo «la convención de Python» (1 línea, no relacionada); después 10 líneas |
| H-07 | Sitio estático con `Content-Security-Policy`, `Referrer-Policy` y `Permissions-Policy` (`render.yaml`). Corresponde a OW-10 / RM-06, que la auditoría final dejó «no implementada» | por abrir | `54385b0` | `antes/H-07_antes_sitio_estatico_sin_csp.png` (`curl -sI` real del sitio) | `despues/H-07_despues_sitio_estatico_con_csp.png` | Build de producción servido con las cabeceras de `render.yaml` y abierto con Playwright → **0 violaciones de CSP**. En Render se ve tras el despliegue de `main` (acción de quien tenga la cuenta) |
| H-08 | CI con `ruff check src tests`, `bandit -q -r src -ll` y `npm audit --audit-level=high`. Corresponde a OW-14 / RM-07, que tampoco estaba implementada | por abrir | `54385b0` | `antes/H-08_antes_ci_sin_ruff_ni_npm_audit.png`, `antes/H-08_antes_ruff_bandit_local.png` | `despues/H-08_despues_ci_con_ruff_bandit_npm_audit.png` | ruff: 1 error (B905) → **0**; Bandit: 0 de severidad media o alta (3 bajas); `bandit` añadido a `requirements-dev.txt` |
| H-02 | Corpus mínimo versionado (`backend/data/corpus_minimo.jsonl`, 295 fragmentos literales), guion `scripts/reconstruir_corpus.py` desde el índice móvil y prueba de recuperación real en la CI | por abrir | `54385b0` | `antes/H-02_antes_clon_limpio_sin_corpus.png` (406 aprobadas, 16 omitidas; sin guion) | `despues/H-02_despues_corpus_minimo_y_reconstruccion.png` | Reconstrucción: 3 605 fragmentos, **idénticos como datos** al `fragmentos_v3.jsonl` de referencia (solo cambia CRLF por LF). Prueba: A 20/20 con oro en el top-5, **C 0 FP**, `zorro` → p. 37 |
| H-01 | «Python 3.12 obligatorio» en el README (además de `render.yaml` y la CI) | por abrir | `54385b0` | `antes/H-06_antes_readme.png` | `despues/H-06_despues_readme.png` | `grep "Python 3.12" README.md` → 1 línea |
| H-09 | `RepositorioFuentesPostgres` → `RepositorioFuentesSqlalchemy` (se usa también con SQLite). Nivel del registro configurable (`NIVEL_LOG`) y visible en cada línea | por abrir | `54385b0` | `antes/H-09_antes_nombre_logs_y_traductor.png` | `despues/H-09_despues_nombre_logs_y_traductor.png` | `pytest test_arreglos_s14.py` → 7/7 |
| H-10 | `/api/estado.modelo` informa «ninguno (extractivo)» cuando no redacta un modelo; con Ollama o Gemini, el suyo | por abrir | `54385b0` | `antes/H-10_antes_estado_modelo_qwen_con_extractivo.png` y `docs_entrega_final/logo/B11_web_local_antes_sin_logo.png` («Modelo qwen3.5:4b» con redacción extractiva) | `despues/H-10_despues_estado_modelo_extractivo.png` | `curl /api/estado` → `"modelo": "ninguno (extractivo)"` |
| B1 (nuevo) | `TRADUCTOR` de `render.yaml` se ignoraba: ahora la configuración lo lee (`tabla` u `ollama`; otro valor impide arrancar) | por abrir | `54385b0` | `antes/H-09_antes_nombre_logs_y_traductor.png` (sin campo en `config.py`) | registro `[TRADUCTOR] tabla` en `despues/H-09_…` | pruebas `test_traductor_*` (3) |
| B1 (nuevo) | `ADMIN_TOKEN` declarado en `render.yaml` solo como `sync: false`, sin valor | por abrir | `54385b0` | — | `despues/H-07_despues_sitio_estatico_con_csp.png` (grep de `render.yaml`) | YAML válido; no se tocó Render |

**Suite completa tras los arreglos:** `pytest` → 416 aprobadas y 16 omitidas (antes 406 y 16; las 10
nuevas son de estos arreglos). `ruff check src tests` → sin errores.

**Sobre el corpus mínimo y ADR-015:** el corpus completo no se versiona aquí, pero el mismo texto ya es
público en `assets/indice/fragmentos.json` del repositorio móvil. Ni el corpus mínimo ni el guion
amplían esa exposición.

## Grupo 4 · Errores del informe S13

En `docs_auditoria/` estos errores **no aparecen**: se comprobó con `grep`. `05_plan_owasp.md:62`
ya dice 60/min para predicciones y `02_plan_furps.md:64` y `03_…:67` dicen 4 s. Están en el
**informe S13 (Word)**, que no está en el repositorio. Correcciones que se deben aplicar allí:

| Dice | Debe decir | Fuente |
|---|---|---|
| Límite de `/api/predicciones` 20/min | **60/min** | `backend/src/infrastructure/config.py:93` |
| Aviso de arranque en frío a los 5 s | **4 s** | `frontend/src/api.js:8` (`AVISO_ESPERA_MS = 4000`) |
| RM-08 «Implementada» (Tabla 6) | **Parcial** | `docs_auditoria/06_auditoria_implementacion_owasp.md:146` («RM-05, RM-07 y RM-08 están parcialmente aplicados») |
| 72,65 s atribuido al paso 1 | Es el arranque en frío medido en la **línea base** de la fase 1 (FURPS+), no el paso 1 | `docs_auditoria/02_plan_furps.md:32` |
| Cita a `RESPUESTA_AGENTE_S13.md` | El archivo no está en el repositorio: **quitar la cita** o subirlo | `git ls-files \| grep RESPUESTA_AGENTE` → vacío |

Además, con este PR quedan implementadas **OW-10** (CSP del sitio estático) y **OW-14** (`npm audit`
en la CI), que `07_auditoria_final.md:99-100` registraba como no implementadas.

## Grupo 5 · Riesgos residuales OWASP (evaluación; no se implementó nada)

| Riesgo | Estado hoy (comprobado) | Costo de corregir | Riesgo residual | Recomendación |
|---|---|---|---|---|
| **OW-03** · Consultas de todos legibles | `GET /api/historial` en la nube → **401** sin token (ADR-036). `GET /api/analitica/demanda` es público, pero hoy devuelve `prioridades: []` porque la demanda real no alcanza el mínimo (`suficiente: false`) | Bajo: exigir el token también en la analítica, o publicar solo términos con k ≥ 5 consultas distintas (2–3 h con pruebas) | Bajo: la analítica agrega términos sin identidad ni hora | **Aceptar** para la U4 y anotar el umbral de k-anonimato como mejora |
| **OW-08** · Sin límite de peticiones | Implementado (ADR-037): 20/min consultas, 60/min predicciones, 429 con `Retry-After`. Probado de punta a punta desde la app (`docs/evidencias/pmv3/movil/HU-10_movil_429_*`) | Medio, si se quisiera un límite compartido entre procesos (Redis) | Bajo: contador en memoria que se pierde al reiniciar; detrás de un NAT el límite se comparte | **Aceptar** (un solo proceso en Render) |
| **OW-17** · Corpus sin cuarentena ni autoría | Ingesta sin token → **401** en la nube (ADR-035): solo el administrador incorpora. No hay estado «en revisión» ni registro de quién incorporó | Medio: campo de estado en `fuentes`, filtro del índice a las aprobadas, autor y fecha en la ingesta y pruebas (≈ 1 día) | Medio-bajo: depende de que el token no se filtre (se recomienda rotarlo, guía 02 paso 7) | **Aceptar con condición**: rotar `ADMIN_TOKEN` y `TOKEN_PRUEBAS`. Cuarentena como trabajo futuro |

Las comprobaciones contra la nube fueron inocuas: un `GET` y un `POST` sin cuerpo ni token, que el
middleware rechaza con 401 antes de llegar al caso de uso.
