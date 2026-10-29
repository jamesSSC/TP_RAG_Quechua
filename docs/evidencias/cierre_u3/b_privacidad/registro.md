# BUG-03 · depuración de textos de `evaluacion_prosa.json` en archivos versionados

Conteo de coincidencias (preguntas y pasajes del conjunto, buscados en `docs/` y en todos los archivos versionados; sin imprimir el texto):
`conteo_antes.txt` (6 archivos, 212 coincidencias) → `conteo_despues.txt` (solo `docs/11_CASOS_VIDEO_Y_CAPTURAS.md`, 4 coincidencias, a cargo del archivista).

| Archivo | Cambio |
|---|---|
| `docs/evidencias/pmv2/transacciones.csv` y `.../postgres/transacciones.csv` | 60 filas de la partición E: la columna `consulta` pasa a `[prosa:<id>]` |
| `docs/evidencias/2026-10-01_ba74edb_pc-rtx4060/humo_bloque7.json` | caso C-05: la consulta pasa a `[prosa:P001]` |
| `backend/scripts/humo_bloque7.py` | caso C-05 usa una pregunta fuera del corpus, redactada para esto (esperado: abstención) |
| `frontend/src/componentes/PanelPrediccion.jsx` | ejemplo de prosa sustituido por una pregunta genérica propia |
| `docs/11_CASOS_VIDEO_Y_CAPTURAS.md` | **no se edita aquí**; líneas 27 y 77 (pregunta de la partición de prosa, id P001) |

No se reescribe el historial de Git: los textos anteriores siguen en commits antiguos (decisión del usuario).
Búsqueda adicional: ningún archivo versionado contiene el comienzo de fragmentos del corpus de 60 o más caracteres.
