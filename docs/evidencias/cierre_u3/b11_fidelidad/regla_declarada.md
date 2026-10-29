# Regla de fidelidad, declarada antes de medir (P1-B11)

- **Glosa en español** del fragmento: el lema castellano (lo que precede a los dos puntos de cada entrada). **Formas quechuas**: lo que sigue a
  los dos puntos. La separación es mecánica; ninguna forma se escribe ni se corrige.
- **Contradicción potencial:** la redacción en español, una vez quitadas las formas quechuas del fragmento, contiene al menos una palabra
  de contenido (4 o más letras, ni funcional ni metalingüística) que no figura en la glosa ni en la consulta. «Figura» = coincide por
  sus 5 primeros caracteres, para tolerar flexiones (zorro/zorros).
- Es una **cota superior conservadora del riesgo** (marca para revisar, no prueba un error); sobrestima, no subestima.
- **Cortada:** `done_reason == "length"` en la respuesta de Ollama.
- Muestra: las 120 consultas de la partición A, a través del caso de uso en proceso, con Qwen3.5-4B real en la GPU, base temporal.
- La evidencia solo lleva ids y banderas: ni la redacción ni el fragmento.
