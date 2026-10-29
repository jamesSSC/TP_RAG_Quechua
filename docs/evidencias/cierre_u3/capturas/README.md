# Capturas por historia (P0-B6)

Generadas por `npm run test:e2e` (Playwright, Chromium, 1366×768) desde `frontend/`. Cada corrida levanta tres APIs locales
(127.0.0.1) con bases aisladas: una copia de `backend/quechua_wanka.db` (la base real no se modifica), una copia de
`backend/carga.db` (consultas sintéticas, HU-09) y una base vacía con Ollama inalcanzable (C-10).

- HU-02 usa una **copia renombrada de un PDF ya registrado en el corpus** (el diccionario de 37 páginas); no hay un PDF de prueba con licencia propia.
- Las consultas de prosa (HU-04, RF-15) son preguntas propias que no figuran en ningún conjunto de evaluación.
- Las capturas muestran los fragmentos citados con su documento y página, que es la función del producto; ninguna muestra preguntas de
  `evaluacion_prosa.json` ni rutas del sistema (revisadas una por una; el historial visible y las 15 prioridades de HU-09 se compararon con ese conjunto).

**Resultado de la corrida:** 15 pruebas E2E aprobadas de 15 (1,3 min), incluida PF-18 (consulta → documento y página → historial → borrar).
