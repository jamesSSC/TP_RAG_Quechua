# B14 · arranque del ejecutable

- **Pantalla de estado inicial:** sección «Estado del sistema» en la vista Consultar (sin cambiar las pestañas) que lee `/api/estado`: Ollama, modelo, corpus y base.
  Con Ollama detenido muestra el aviso «las respuestas muestran el fragmento literal con su documento y página, sin redacción» y la aplicación sigue funcionando
  (generador literal por el fallback del caso de uso). Vitest (4), E2E (2 capturas `B14_*`) y prueba de backend sin Ollama.
- **`.exe` recompilado** (PyInstaller, con la interfaz y el backend actuales):

| Medida | Resultado |
|---|---|
| Tamaño del `.exe` | 109 152 471 bytes (104,1 MiB; B2: 109 131 367) |
| Arranque en frío hasta `GET /api/estado` = 200 | 43,61 s (copia del corpus base, descompresión, comprobación de Ollama) |
| Arranque en caliente | 2,06 s |
| Persistencia (BUG-01) en carpeta temporal | 3 605 → 5 965 fragmentos al incorporar una copia renombrada de un PDF ya registrado; tras cerrar y reabrir siguen 5 965, 9 documentos, documento y fuente listados, `consistencia` ok |
| Sin Ollama (`OLLAMA_URL` hacia un puerto muerto) | arranca (43,6 s en frío), `generador_disponible: false`, consulta 200 con documento y página, aviso de generación y la respuesta es el fragmento literal |

Las pruebas se hicieron en carpetas temporales fuera del repositorio; `backend/dist` solo contiene el `.exe` (ni `datos/` ni `.db`), y la base real no se tocó.
