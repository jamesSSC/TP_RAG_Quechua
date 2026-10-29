# B11 · significados alterados y respuestas cortadas

Medición: 120 consultas de la partición A, caso de uso en proceso, Qwen3.5-4B real en GPU, base temporal. Regla en `regla_declarada.md`
(escrita antes de medir). Solo ids y banderas; nada de redacciones ni fragmentos.

| Medida | Antes (redacción libre) | Después (ADR-028, extractiva verificada) |
|---|---|---|
| Contradicción potencial (cota superior) | 8/120 = 6,7 % | 2/120 = 1,7 % (ambas son el fragmento literal tras descartar la extracción) |
| Extracciones aceptadas / descartadas | — | 118 / 2 |
| Respuestas cortadas (`done_reason == "length"`) | 0/120 | 0/120 |
| Tokens máximos generados | 32 | 31 |
| Latencia P95 | 2 805 ms | 2 672 ms |

**Corte.** No se observó ningún corte (máximo 32 tokens frente al límite de 300). Causa posible confirmada en el código: el adaptador ignoraba
`done_reason`; una respuesta que topara con `num_predict: 300` se habría entregado recortada. Ni los DTO de salida ni el CSS de `.respuesta__texto`
recortan (sin `[:N]`, `max-height`, `overflow` ni `line-clamp`; Vitest lo comprueba con 120 frases). Corrección: con `length` se reintenta con 900 tokens y, si
vuelve a toparse, se descarta y el caso de uso muestra el fragmento literal con su aviso.

**Fidelidad.** Entre las 8 marcadas antes había una alteración real de formas quechuas (el modelo reescribió dos formas de una entrada) y un lema castellano
mal copiado; el resto eran redacciones con palabras ajenas al fragmento. Mitigación (ADR-028, por registrar): el modelo solo extrae `{forma, glosa}`,
`VerificadorFormaLiteral` (dominio) exige la forma exacta y la glosa literal en el fragmento y la frase la compone una plantilla; si no se verifica,
se muestra el fragmento literal. Las 2 marcadas después son esos fragmentos literales (la regla las cuenta porque contienen texto del propio diccionario): 0 frases del modelo con palabras ajenas.
Modo configurable con `MODO_REDACCION=extractiva|libre` (por defecto extractiva).
