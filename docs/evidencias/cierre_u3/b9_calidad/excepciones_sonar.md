# Excepciones de SonarQube aceptadas (puerta de calidad)

La puerta de calidad estaba en ERROR por 44 violaciones nuevas (todas code smells). Se corrigieron las reales y se aceptaron en Sonar
(`do_transition` → `accept`, con comentario) las que son estilo en pruebas o decisiones de diseño. Estado final de la puerta: **OK**.

**Corregidas (sin cambio de comportamiento):** S3776 ×2 (`analizar_demanda`, `verificar_consistencia_datos`), S8572 ×2 (`logging.exception`),
S3358 ×9 (condicionales anidadas, Python y JSX), S6819 ×7 (`<output>` en lugar de `role="status"`), S7776 (`Set`), S1192 (constante) y S5779
(sin `assert` dentro de `try/except`).

| Regla | Cantidad | Justificación |
|---|---|---|
| python:S9073 | 35 | Aserción compuesta en pruebas: cada `assert a and b` verifica una sola propiedad del caso; partirla duplica el contexto sin añadir cobertura. Estilo en pruebas. |
| python:S5778 | 2 | El bloque `pytest.raises` contiene la construcción del objeto y la llamada que debe fallar; forman un único caso. Estilo en pruebas. |
| python:S107 | 1 | `ConsultarCorpusUseCase` recibe sus 14 colaboradores por inyección desde el contenedor (hexagonal); un objeto de parámetros no aporta valor ahora. Se evalúa en el PMV3. |
| javascript:S9020 | 1 | Estilo en una prueba de la interfaz: `waitFor` + `getByText` es equivalente a `findByText`. |
| javascript:S6819 | 1 | El `<meter>` nativo no admite la barra con la marca del umbral τ del diseño; `role="meter"` con `aria-valuenow/min/max` es accesible. |
