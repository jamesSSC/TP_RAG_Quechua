# B12 · paridad del índice móvil (HU-08.3)

Reexportación con `exportar_indice_movil.py` a `backend/artefactos_movil/` (fuera de Git) y validación con `validar_indice_movil.py` sobre las 248 consultas
del conjunto de evaluación, tras los cambios de rutas, origen, índice atómico y redacción. Ningún script falló.

| Medida | Informe (ADR-019) | Ahora |
|---|---|---|
| Diferencia máxima absoluta | 2,5 × 10⁻⁸ | 2,533 × 10⁻⁸ (umbral < 1 × 10⁻⁶) |
| Desajustes en el top-5 | 0 | 0 (top-5 idéntico: sí) |
| Tamaño del índice | 11,85 MB | 11,67 MB |

Resultado: EQUIVALENTE. HU-08.3 sigue en QA hasta validarse en un dispositivo físico (no se midió en dispositivo).
