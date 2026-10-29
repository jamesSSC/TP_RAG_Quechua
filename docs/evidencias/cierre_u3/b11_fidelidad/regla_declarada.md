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

---

# Regla v2 (declarada antes de volver a medir; la v1 de arriba se conserva)

Motivo: la auditoría del PR #13 mostró que `VerificadorFormaLiteral` aceptaba por subcadena (formas truncadas, el lema como forma, formas de otra
entrada y pares cruzados), y que la regla v1 era demasiado permisiva con palabras cortas y con negaciones. La v2 es **más conservadora** (marca más):

1. **Palabras de contenido desde 3 letras** (v1: 4): una palabra de 3 o más letras, no funcional ni metalingüística, que no figura en la glosa ni en la consulta
   (mismo criterio de raíz de 5 caracteres) marca contradicción potencial.
2. **Negación:** las palabras «no», «nunca», «jamás», «sin», «ni» y «tampoco» en la redacción que no estén en la consulta ni en la glosa marcan contradicción
   potencial (una negación que el diccionario no dice invierte el sentido).
3. Una respuesta que **es el fragmento literal** (porque el verificador descartó la extracción o el servicio no redactó) no es una redacción del modelo: no se
   evalúa y se cuenta aparte (`fragmentos_literales`). Así el porcentaje mide solo lo que el modelo escribió o lo que la plantilla compuso.
4. Se mide con la v2 **las dos variantes** sobre las mismas 120 consultas de A y Qwen real: `antes_v2` (redacción libre) y `despues_v2` (extractiva con el
   verificador endurecido), y se registran extracciones aceptadas y descartadas.

Los resultados con la v1 (`antes/`, `despues/`) se conservan; `despues/` se obtuvo con el verificador original (por subcadena).
