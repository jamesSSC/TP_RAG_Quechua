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

---

# Corrección tras la auditoría del PR #13 (verificador endurecido y regla v2)

**Fallo (mayor, salvaguarda):** `VerificadorFormaLiteral` comparaba por subcadena y aceptaba una forma truncada, el lema castellano como forma, formas de entradas
distintas y el par cruzado forma de una entrada + glosa de otra. **Corrección:** `domain/services/entradas_lexicas.py` (única definición de `PATRON_LEMA`, compartida
con el índice) segmenta el fragmento en entradas; el verificador exige que la glosa sea el lema de una entrada y que cada forma sea un token completo o una secuencia
completa de tokens del cuerpo de **esa** entrada, distinta del lema; solo se normalizan mayúsculas y espacios (las letras quechuas se comparan literales) y la plantilla se
compone con la forma tal como está en el fragmento. Si algo falla, se muestra el fragmento literal. 4 pruebas `@salvaguarda` de dominio (una por caso, más variantes) y 5 del generador.

**Regla v2** (`regla_declarada.md`, declarada antes de medir; la v1 se conserva): palabras de contenido desde 3 letras, negaciones ajenas, y las respuestas que son el fragmento literal se cuentan aparte.

Medición con la regla v2 sobre las mismas 120 consultas de A, Qwen real en GPU, base temporal (`antes_v2/`, `despues_v2/`):

| Medida | Redacción libre (antes) | Extractiva con verificador endurecido (después) |
|---|---|---|
| Respuestas evaluadas (redacción del modelo o plantilla) | 120 | 109 |
| Fragmento literal mostrado (verificador descartó) | 0 | 11 |
| Contradicción potencial (v2) | 13/120 = 10,8 % | 0/109 = 0,0 % |
| Extracciones aceptadas / descartadas | — | 109 / 11 |
| Cortadas (`done_reason == length`) | 0 | 0 |
| Latencia P95 | 2 793 ms | 2 681 ms |

El verificador endurecido descarta 11 de 120 extracciones (9,2 %, frente a 2 con el original): el coste de la fidelidad es mostrar el fragmento literal en ese 9 %. Con la v1 las cifras
(`antes_regla_v1/`, `despues_regla_v1_verificador_original/`) fueron 6,7 % y 1,7 %; la v2 marca más (10,8 % en libre) porque es más conservadora, no porque el modelo haya empeorado.
