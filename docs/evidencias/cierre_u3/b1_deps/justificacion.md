# B1 · Dependencias con avisos de seguridad (BUG-02)

Avisos únicos (por identificador) según `pip-audit` el 2026-10-29. Los JSON completos están en esta carpeta.

| Paquete | Antes | Después | Avisos antes → después |
|---|---|---|---|
| pypdf | 5.1.0 | 6.21.4 | 60 → 0 |
| starlette (vía fastapi) | 0.41.3 | 1.10.0 (fijada) | 7 → 0 |
| fastapi | 0.115.6 | 0.162.0 | 0 → 0 |
| python-multipart | 0.0.20 | 0.0.32 | 6 → 0 |
| python-dotenv | 1.0.1 | 1.2.4 | 1 → 0 |
| pytest | 8.3.4 | 9.2.0 | 1 → 0 |

Total: 75 avisos únicos → 0 en `requirements.txt` y en `requirements-dev.txt`.

## Saltos de versión mayor (requieren ADR)
- pypdf 5 → 6 · starlette 0.x → 1.x · pytest 8 → 9.

## Avisos sin corrección o no aplicables
Ninguno: `pip-audit` informa «No known vulnerabilities found» en ambos archivos.

## Ajustes por la actualización
- `test_las_rutas_son_las_mismas_de_antes_del_refactor` leía `app.routes`; FastAPI 0.162 anida los routers incluidos.
  Ahora lee las rutas del esquema OpenAPI. Mismas 14 rutas esperadas; no cambia ninguna ruta de la API.
- `pytest` sigue fijado en `requirements.txt` (como antes) pero en 9.2.0; en dev queda `pytest>=9.0.3`.
- Las pruebas de PostgreSQL se corrieron contra la base `quechua_wanka_pruebas` (creada aparte, porque la
  fixture hace `drop_all`), no contra `quechua_wanka`.
