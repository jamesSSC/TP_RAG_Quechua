# B2 · BUG-01: persistencia de PDF en el ejecutable

Prueba manual con el `.exe` recompilado (29/10/2026, copia en una carpeta temporal fuera del repositorio).

- Reconstrucción: `npm run build` → copia a `backend/interfaz` → PyInstaller con `QuechuaWankaWeb.spec`.
- Tamaño del `.exe`: 109 131 367 bytes (104,1 MiB; antes 106 910 041 bytes en el `.exe` del 2026-10-01).
- Documento incorporado: copia **renombrada** (`copia-prueba-bug01.pdf`) de un PDF ya registrado del corpus
  (`293274822-diccionario-quechua-Wanka-docx.pdf`). Se renombró porque el identificador de fragmento depende del
  nombre del archivo; con el nombre original todos los fragmentos ya estaban en el corpus y no habría nada nuevo.
- Secuencia: arranque en frío (se crea `datos/` y se copia el corpus base) → `POST /api/corpus/documentos` → cierre →
  reapertura → listado de documentos y fuentes → consulta de prueba.

| Medida | Resultado |
|---|---|
| Arranque en frío hasta `GET /api/estado` = 200 | 43,72 s (incluye la copia del corpus base, la descompresión del `.exe` y la comprobación de Ollama) |
| Arranque en caliente | 2,06 s |
| Fragmentos antes / después de incorporar | 3 605 / 5 965 (2 360 nuevos) |
| Tras reabrir | 5 965 fragmentos; 9 documentos (antes 8); documento y fuente listados |
| Consulta tras reabrir | 200; el respaldo incluye el documento incorporado |
| `consistencia` en `/api/estado` | `ok`, sin avisos, en las tres lecturas |
| Archivos en `datos/` | `fragmentos_v3.jsonl`, `documentos/copia-prueba-bug01.pdf`, `documentos/manifiesto.json` |

Hallazgo adicional: el `.exe` construido desde `main` no arrancaba (`ModuleNotFoundError:
application.ports.in.predecir_consulta_port`) porque el `.spec` no declaraba los módulos del PMV2. Se añadieron al
`hiddenimports` (`predecir_consulta_port`, `analizar_demanda_port`, `prediccion_controller`).

Limpieza: se borró la `quechua_wanka.db` de `backend/dist`; la prueba corrió en una carpeta temporal y no dejó `datos/`.
