# 03 · Historias de usuario (INVEST + Gherkin)

> Historias del Documento 0 (Tabla 6), refinadas con los parámetros medidos en el Documento 6 y
> comprobadas contra INVEST. Los criterios de aceptación están en **Gherkin en español** y son la base de
> las pruebas de aceptación: cada bloque `gherkin` de este archivo se copia tal cual a
> `tests/aceptacion/<ID>.feature`.
>
> Mantenido por: **archivista** · El programador **no** modifica criterios: si un criterio es
> inviable, lo reporta al orquestador · Última revisión: 2026-09-24 · Versión 1.1

---

## 1. Convenciones

### 1.1 Formato de historia

```
Como <rol concreto>
Quiero <capacidad>
Para <beneficio verificable>
```

### 1.2 Lista de comprobación INVEST

| Letra | Pregunta que debe responder «sí» | Qué se hace si no |
|---|---|---|
| **I**ndependiente | ¿Puede entregarse sin esperar a otra historia del mismo sprint? | Se declara la dependencia y se ordena el sprint. |
| **N**egociable | ¿El «cómo» queda abierto al plan técnico? | Se retiran detalles de implementación de la historia. |
| **V**aliosa | ¿Aporta algo observable a una persona usuaria o habilita algo que sí lo aporta? | Se convierte en historia técnica (HT). |
| **E**stimable | ¿Se entiende lo suficiente para estimarla? | Se hace una espiga (*spike*) acotada. |
| **S**mall (pequeña) | ¿Cabe en la mitad de un sprint o menos? | Se divide con sufijo (`HU-08.1`). |
| **T**esteable | ¿Tiene criterios Gherkin verificables? | No entra en «Listo». |

### 1.3 Reglas del Gherkin del proyecto

- Primera línea de cada `.feature`: `# language: es`. Palabras clave: `Característica`, `Antecedentes`,
  `Escenario`, `Esquema del escenario`, `Ejemplos`, `Dado`, `Cuando`, `Entonces`, `Y`, `Pero`.
- Cada historia tiene **al menos un escenario de éxito y uno de error o de límite** (Documento 0, §3.2).
- **Las formas quechuas de los ejemplos proceden literalmente del corpus** (ver `01_CONTEXTO_GENERAL.md`
  §9). Está prohibido escribir una forma quechua que no figure en un fragmento indexado, también en las
  pruebas.
- Etiquetas: `@HU-xx` (trazabilidad), `@PMV1`/`@PMV2`/`@PMV3`, `@salvaguarda` (se ejecuta en **todas**
  las ramas, DoD-4), `@arnes` (usa el arnés de evaluación), `@lento` (fuera del ciclo rápido), `@manual`
  (requiere persona o dispositivo).
- Herramienta sugerida: `pytest-bdd`. Antes de fijarla, el programador verifica que la versión elegida
  admite `# language: es`; si no, se usa `behave`, que sí lo admite. Decisión registrable como ADR menor.

### 1.4 Definición de Listo (DoR) — propuesta para validar en la revisión del sprint 1

Una historia pasa a **Listo** solo si: (1) cumple INVEST o tiene su excepción declarada; (2) tiene
criterios Gherkin; (3) sus requisitos están en `02_REQUERIMIENTOS.md`; (4) sus dependencias están
resueltas o planificadas antes; (5) existe `docs/specs/<ID>/spec.md` aprobado por el usuario; (6) está
estimada.

### 1.5 Definición de Terminado (Documento 4, Tabla 13)

| N.º | Criterio | Cuándo |
|---|---|---|
| DoD-1 | Funcionalidad implementada y ejecutable de principio a fin, sin intervención manual. | Antes de la revisión |
| DoD-2 | Todos los escenarios Gherkin de la historia pasan y el resultado queda registrado. | Antes de la revisión |
| DoD-3 | Ninguna respuesta sin documento y página; la procedencia OCR se advierte. | Cada incremento del flujo de consulta |
| **DoD-4** | **Ante una consulta sin respaldo, se declara la ausencia y no se genera forma alguna.** | **Todos los incrementos, sin excepción** |
| DoD-5 | Sin dependencia de servicios externos ni transmisión de la consulta. | Cada incremento |
| DoD-6 | Tiempo de respuesta medido y contrastado con el umbral de la plataforma. | Cierre de cada PMV |
| DoD-7 | Todo documento del corpus con fuente, fecha de extracción y licencia. | En la ingesta |
| DoD-8 | Código integrado en el repositorio; entorno reconstruible desde la especificación de dependencias. | Antes de la revisión |
| DoD-9 | Documentación SDD y serie documental actualizadas. | Cierre de cada sprint |
| DoD-10 | Revisión cruzada por alguien distinto del autor. En este modelo: **auditor + aprobación humana del PR**. | Antes de la revisión |

---

## 2. Índice de historias

| ID | Título | Épica | Tema | PMV | Sprint | Prior. | Estado |
|---|---|---|---|---|---|---|---|
| HU-01 | Cargar documentos con procedencia | E-01 | Gestión del corpus | 1 | 1 | Alta | Backlog |
| HU-02 | Segmentar e indexar el corpus | E-02 | Gestión del corpus | 1 | 1 | Alta | Backlog |
| HU-03 | Consultar una palabra en quechua wanka | E-03 | Consulta asistida | 1 | 2 | Alta | Backlog |
| HU-04 | Consultar contenido cultural | E-04 | Consulta asistida | 1 | 2 | Media | Backlog |
| HU-05 | Recibir la respuesta en mi idioma | E-05 | Consulta asistida | 1 | 2 | Media* | Backlog |
| HU-06 | Saber cuándo no hay información documentada | E-06 | Confiabilidad | 1 | 2 | Alta | Backlog |
| HU-07 | Ver documento y página de cada respuesta | E-07 | Confiabilidad | 1 | 2 | Alta | Backlog |
| HU-08.1 | Anticipar si hay respaldo antes de generar | E-08 | Analítica predictiva | 2 | 3 | Alta | Backlog |
| HU-08.2 | Ajustar el umbral con la experiencia acumulada | E-08 | Analítica predictiva | 2 | 3 | Alta | Backlog |
| HU-09 | Saber qué material conviene incorporar | E-09 | Analítica predictiva | 2 | 3 | Media | Backlog |
| HU-10.1 | Consultar desde el teléfono sin conexión | E-10 | Despliegue móvil | 3 | 4 (Trello: S3) | Alta | Hecha en emulador (dos modos, ADR-038); teléfono físico pendiente |
| HU-10.2 | Misma salvaguarda en el teléfono | E-10 | Despliegue móvil | 3 | 4 (Trello: S3) | Alta | Hecha: 0 FP en C en el dispositivo (emulador); teléfono físico pendiente |
| HU-10.3 | Instalación que no queda a medias | E-10 | Despliegue móvil | 3 | 4 (Trello: S3) | Alta | Hecha: APK arm64 22,6 MB, Release v1.1.0; instalación en teléfono físico pendiente |
| HU-11 | Interfaz simple y legible | E-11 | Despliegue móvil | 3 | 4 (Trello: S3) | Media | Hecha (A−/A/A+, objetivos ≥ 48 px); Accessibility Scanner en teléfono físico pendiente |
| HT-00 | Repositorio, integración continua y entorno de agentes | — | Habilitador | 1 | 1 | Alta | Listo |
| HT-01 | Arnés de evaluación reproducible | — | Habilitador | 1 | 1 | Alta | Backlog |
| HT-02 | Conjunto de evaluación externo (docentes de EIB) | — | Habilitador | 1 | 1–2 | Alta | Backlog |
| HT-03 | Traducción de la consulta y recalibración de τ | — | Habilitador | 1 | 2 | Alta | Backlog |
| HT-04 | Servicio local y interfaz de escritorio | — | Habilitador | 1 | 2 | Alta | Backlog |
| HT-05 | Artefactos móviles y equivalencia entre plataformas | — | Habilitador | 2 | 3 | Alta | Backlog |
| HT-06 | Medición de rendimiento y recursos | — | Habilitador | 1, 3 | 2, 4 | Alta | Backlog |
| HT-07 | Evaluar bge-m3 como complemento de la recuperación | — | Espiga | 1 | 2 | Baja | Backlog |
| HT-08 | Servidor MCP de desarrollo (solo lectura) | — | Habilitador | 1 | 1–2 | Media | Backlog |

Estado de HU-10.x y HU-11 al 24/11/2026: ver `18_REPORTE_PMV3.md` (fichas por historia) y
`docs_entrega_final/RESPUESTA_AGENTE_PMV3_ENTREGA_FINAL.md` §4. En Trello el PMV3 es el **Sprint 3
(06/11–13/12)**; en el plan de `04_SPRINTS.md` figura como Sprint 4 (ver su §1.4).

\* Ver la tensión de prioridad de RF-04 en `02_REQUERIMIENTOS.md` §2 y ADR-008.

**Cambios respecto del Documento 0 por INVEST:** HU-08 se divide en HU-08.1 (RF-14) y HU-08.2 (RF-15)
porque juntas no caben en medio sprint y se prueban de forma distinta; HU-10 se divide en tres porque
agrupaba ejecución, salvaguarda e instalación. Se añaden historias técnicas (HT) para el trabajo que no
entrega valor directo a una persona usuaria pero lo habilita; las HT no se disfrazan de historias de
usuario.

---

## 3. Tema: Gestión del corpus documental

### HU-01 · Cargar documentos con procedencia

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-01 Ingesta y documentación de fuentes | PMV1 · S1 | Alta | RF-01, RF-13, RNF-11, RD-01, RD-02 | HT-00 | Por estimar |

**Como** integrante del equipo **quiero** cargar los documentos oficiales del corpus de quechua wanka y
registrar su procedencia **para** construir la base documental del sistema con trazabilidad verificable.

**INVEST:** I ✓ · N ✓ · V ✓ (habilita toda consulta) · E ✓ (existe `ingest2.py`) · S ✓ · T ✓

```gherkin
# language: es
@HU-01 @PMV1
Característica: Ingesta documental con procedencia registrada
  Como integrante del equipo
  Quiero cargar los documentos del corpus registrando su procedencia
  Para construir una base documental con trazabilidad verificable

  Antecedentes:
    Dado un manifiesto del corpus con fuente, fecha de extracción y licencia por documento

  Escenario: Documento válido con capa de texto
    Dado el PDF "293274822-diccionario-quechua-Wanka-docx.pdf" registrado en el manifiesto
    Cuando ejecuto la ingesta
    Entonces cada fragmento producido tiene "documento", "pagina", "texto", "tipo" y "procedencia"
    Y la procedencia de sus páginas con texto es "capa de texto"
    Y el fragmento "ZORRO: Atuq." queda asociado a la página 37

  Escenario: Documento sin capa de texto
    Dado un PDF registrado en el manifiesto cuyas páginas son imágenes escaneadas
    Cuando ejecuto la ingesta
    Entonces el sistema aplica reconocimiento óptico de caracteres a esas páginas
    Y marca sus fragmentos con procedencia "reconocimiento óptico"

  Escenario: Capa de reconocimiento óptico fragmentada
    Dado una página cuya longitud media de línea es inferior a 12 caracteres
    Cuando ejecuto la ingesta
    Entonces las líneas se recomponen antes de segmentar

  Escenario: Documento sin entrada en el manifiesto
    Dado un PDF que no figura en el manifiesto del corpus
    Cuando ejecuto la ingesta
    Entonces el documento se rechaza con un mensaje que indica la falta de procedencia
    Y no se genera ningún fragmento a partir de él
```

**Notas para el plan técnico.** Promover `poc/ingest2.py` a adaptador de `ExtraccionDocumentalPort`
(pypdf + Tesseract). El OCR es higiene: la PoC midió que aporta un 0,45 % del texto. Las tarjetas con
relatos no tienen texto impreso; emparejar cada ilustración con el texto de su página contigua **sin
generar descripciones con IA** (sería generación sin respaldo).

---

### HU-02 · Segmentar e indexar el corpus

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-02 Segmentación e indexación vectorial | PMV1 · S1 | Alta | RF-02, RF-05, RF-13, RNF-12 | HU-01 | Por estimar |

**Como** integrante del equipo **quiero** segmentar e indexar el corpus extraído **para** que el sistema
pueda recuperar fragmentos por similitud.

**INVEST:** I ✗ (depende de HU-01, se ordena en el sprint) · N ✓ · V ✓ · E ✓ · S ✓ · T ✓

```gherkin
# language: es
@HU-02 @PMV1
Característica: Segmentación por tipo documental e indexación reconstruible
  Como integrante del equipo
  Quiero segmentar e indexar el corpus
  Para que el sistema recupere fragmentos por similitud

  Escenario: Una entrada de diccionario es un fragmento
    Dado el texto extraído de un documento de tipo "lexicografico"
    Cuando ejecuto la segmentación
    Entonces "ZORRO: Atuq." constituye un fragmento independiente
    Y ningún fragmento lexicográfico contiene más de una entrada

  Escenario: La prosa se segmenta por párrafo
    Dado el texto extraído de un documento de tipo "prosa"
    Cuando ejecuto la segmentación
    Entonces los fragmentos tienen en torno a 650 caracteres
    Y ningún fragmento corta un párrafo por la mitad salvo que el párrafo exceda ese tamaño

  Escenario: Indexación reproducible con un comando
    Dado el corpus de referencia de ocho documentos
    Cuando ejecuto el comando de reconstrucción del índice
    Entonces el índice reporta el número de fragmentos indexados
    Y el número coincide con el de la ejecución anterior sobre el mismo corpus

  Escenario: Reindexación sin duplicados
    Dado un índice ya construido
    Cuando incorporo un documento nuevo al manifiesto y reconstruyo el índice
    Entonces el índice incluye los fragmentos nuevos
    Y ningún fragmento existente aparece duplicado

  Escenario: Identificadores compatibles con la prueba de concepto
    Dado el corpus de referencia con los nombres de archivo del manifiesto
    Cuando ejecuto la indexación
    Entonces el fragmento "ZORRO: Atuq." de la página 37 tiene el identificador "35d5d6d6b8a4"
    Y todos los identificadores citados como referencia en el conjunto de evaluación existen en el índice
```

**Notas.** Referencia medida: 3 605 fragmentos (2 470 lexicográficos, 1 135 de prosa). Segmentar el
material lexicográfico en bloques uniformes hunde la cobertura en el punto de operación (ADR-007). El
`id` es `md5("<archivo>|<página>|<índice>")[:12]`, como en la PoC, para que el conjunto de evaluación
siga siendo válido (ADR-018); los nombres de archivo los fija `corpus/MANIFIESTO.yaml`.

---

## 4. Tema: Consulta asistida del corpus

### HU-03 · Consultar una palabra en quechua wanka

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-03 Consulta léxica | PMV1 · S2 | Alta | RF-03, RF-05, RF-06, RF-09, RF-11 | HU-02, HT-01, HT-04 | Por estimar |

**Como** estudiante o docente de Educación Intercultural Bilingüe **quiero** consultar la equivalencia de
una palabra del español en quechua wanka **para** incorporarla a mi práctica pedagógica.

**INVEST:** I ✓ (sobre el índice del S1) · N ✓ · V ✓ · E ✓ · S ✓ · T ✓

```gherkin
# language: es
@HU-03 @PMV1
Característica: Consulta léxica con respaldo documental
  Como estudiante o docente de EIB
  Quiero consultar la equivalencia de una palabra en quechua wanka
  Para incorporarla a mi práctica pedagógica

  Antecedentes:
    Dado el índice del corpus de referencia
    Y el umbral de abstención leído de la configuración (vigente 0,48, ADR-020)

  Esquema del escenario: Término presente en el corpus
    Cuando consulto "¿cómo se dice <palabra> en quechua wanka?"
    Entonces la similitud del mejor fragmento es mayor o igual que el umbral
    Y la respuesta muestra la forma "<forma>" copiada literalmente del fragmento "<fragmento>"
    Y la respuesta cita el documento "293274822-diccionario-quechua-Wanka-docx.pdf" y la página <pagina>

    Ejemplos:
      | palabra  | forma    | fragmento           | pagina |
      | zorro    | Atuq     | ZORRO: Atuq.        | 37     |
      | cóncavo  | Puklu    | CÓNCAVO: Puklu.     | 9      |
      | confesar | Kunfisay | CONFESAR: Kunfisay. | 9      |

  @salvaguarda
  Escenario: Término ausente del corpus
    Cuando consulto "¿cómo se dice criptomoneda en quechua wanka?"
    Entonces el sistema declara que no dispone de respaldo documental
    Y la respuesta no contiene ninguna forma en quechua
    Y el modelo generador no es invocado

  Escenario: Consulta vacía o demasiado larga
    Cuando envío una consulta vacía o de más de 300 caracteres
    Entonces el sistema muestra un mensaje de validación
    Y no ejecuta la recuperación

  Escenario: El historial conserva la sesión
    Dado que realicé dos consultas en la sesión activa
    Cuando reviso el historial
    Entonces aparecen ambas consultas con sus respuestas y fuentes
```

**Notas.** El fragmento `CASA: Wasi.CASADO: Walmiyuq.` es un **falso negativo conocido** (dos entradas
fusionadas por la extracción): sirve de prueba de regresión para la ingesta, no para bajar τ.

---

### HU-04 · Consultar contenido cultural

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-04 Consulta de contenido cultural | PMV1 · S2 | Media | RF-06, RF-10 | HU-03, **RD-05** | Por estimar |

**Como** investigador o estudiante **quiero** consultar relatos, saberes y expresiones contenidos en el
corpus **para** acceder a material cultural documentado sin revisar los PDF uno por uno.

**INVEST:** I ✗ (**depende de RD-05, un conjunto anotado por humanos que hoy no existe**) · N ✓ · V ✓ ·
E ~ (el umbral de «baja relevancia» está por medir) · S ✓ · T ✓ condicionado a RD-05.
**Excepción declarada:** si RD-05 no está disponible al cierre del sprint 2, la historia se entrega
funcional pero se declara **no evaluada**, conforme al Documento 6.

```gherkin
# language: es
@HU-04 @PMV1
Característica: Consulta de contenido cultural con fuentes citadas
  Como investigador o estudiante
  Quiero consultar relatos, saberes y expresiones del corpus
  Para acceder a material cultural documentado

  Escenario: Consulta temática con respaldo
    Dado una consulta del conjunto de referencia cultural con pasajes anotados
    Cuando el sistema recupera fragmentos con similitud mayor o igual que el umbral
    Entonces elabora una respuesta explicativa a partir de esos fragmentos
    Y cita el documento y la página de cada fragmento utilizado
    Y toda forma quechua de la respuesta figura literalmente en alguno de ellos

  Escenario: Consulta ambigua o demasiado general
    Dado una consulta cuyos fragmentos recuperados tienen baja relevancia y puntuaciones muy próximas entre sí
    Cuando el sistema procesa la consulta
    Entonces solicita una precisión en lugar de responder

  @salvaguarda
  Escenario: Práctica cultural ausente del corpus
    Dado una consulta cultural del dominio andino que no figura en el corpus
    Cuando la similitud máxima es inferior al umbral
    Entonces el sistema declara la ausencia de información
```

**Notas.** «Baja relevancia» se define en el plan técnico (p. ej., margen entre el primer y el quinto
resultado) y se calibra con el arnés: **por medir**. El tercer escenario cubre el caso adverso difícil
que la PoC no probó (consultas cercanas al dominio pero ausentes).

---

### HU-05 · Recibir la respuesta en mi idioma

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-05 Multilingüismo | PMV1 · S2 | Media (ver ADR-008) | RF-04, RNF-08, RN-05 | HU-03, HT-03 | Por estimar |

**Como** usuario angloparlante **quiero** que el sistema responda en el idioma en que formulo la consulta
**para** comprender la respuesta sin traducción adicional.

**INVEST:** I ✓ (tras HT-03) · N ✓ · V ✓ · E ✓ (medido en el cuaderno integral) · S ✓ · T ✓

```gherkin
# language: es
@HU-05 @PMV1
Característica: Consulta en inglés con traducción previa de la consulta
  Como usuario angloparlante
  Quiero recibir la respuesta en inglés
  Para comprenderla sin traducción adicional

  Escenario: Consulta en inglés con respaldo documental
    Cuando consulto "how do you say concave in Wanka Quechua?"
    Entonces el sistema detecta el idioma inglés
    Y traduce la consulta al español antes de recuperar
    Y recupera con la consulta original y con la traducida conservando la mejor puntuación
    Y la respuesta se redacta en inglés
    Y la forma "Puklu" se muestra literalmente, sin traducir, con el documento y la página 9

  Escenario: La traducción queda registrada en la trazabilidad
    Cuando consulto en inglés
    Entonces la respuesta muestra los términos en español con los que se buscó

  @salvaguarda
  Escenario: Consulta en inglés sin respaldo
    Cuando consulto "how do you say cryptocurrency in Wanka Quechua?"
    Entonces el sistema declara en inglés que no dispone de respaldo documental
    Y la respuesta no contiene ninguna forma en quechua

  Escenario: Idioma no soportado
    Cuando formulo la consulta en un idioma distinto del español o el inglés
    Entonces el sistema informa que solo admite consultas en español o en inglés

  @arnes
  Escenario: Criterio de cierre sobre el subconjunto D
    Dado el umbral recalibrado tras incorporar la traducción
    Cuando ejecuto el arnés sobre las particiones C y D
    Entonces recall@5 en D es mayor o igual que 0,80
    Y el número de falsos positivos en C es 0
```

**Notas.** Medido con un traductor específico: recall@5 en D 0,175 → 0,875, pero **solo 20 de 40**
consultas superan τ = 0,41. En la línea base v2 la traducción la hace una **tabla de lemas** calculada en
tiempo de compilación (ADR-023), que muestra todas las lecturas; el resultado en D es un **techo** mientras
las consultas de D deriven de los mismos lemas. Falta un conjunto de consultas en inglés independiente.

---

## 5. Tema: Confiabilidad y trazabilidad

### HU-06 · Saber cuándo no hay información documentada

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-06 Salvaguarda antialucinación | PMV1 · S2 | Alta | RF-08, RN-01, RN-04, RN-08 | HU-02, HT-01 | Por estimar |

**Como** usuario **quiero** que el sistema declare explícitamente cuándo no dispone de información
documentada **para** no incorporar a mi práctica una forma lingüística inventada.

**INVEST:** I ✓ · N ✓ · V ✓ (es el valor diferencial del producto) · E ✓ · S ✓ · T ✓

```gherkin
# language: es
@HU-06 @PMV1 @salvaguarda
Característica: Salvaguarda de abstención
  Como usuario
  Quiero saber cuándo el sistema no tiene respaldo documental
  Para no incorporar formas lingüísticas inventadas

  Antecedentes:
    Dado el umbral de abstención leído de la configuración versionada

  Escenario: Abstención correcta
    Dado una consulta cuya similitud máxima es inferior al umbral
    Cuando el sistema la procesa
    Entonces muestra el mensaje de ausencia de información
    Y no invoca al modelo generador
    Y registra la consulta como no cubierta

  Escenario: Frontera exacta del umbral
    Dado una consulta cuya similitud máxima es exactamente igual al umbral
    Cuando el sistema la procesa
    Entonces responde citando la fuente

  Escenario: Toda respuesta lleva el aviso de alcance
    Cuando el sistema emite cualquier respuesta
    Entonces se muestra el aviso de que es una consulta sobre fuentes documentales y no una validación por hablantes de la comunidad

  @arnes
  Escenario: Cero falsos positivos en la partición C
    Cuando ejecuto el arnés sobre las 28 consultas fuera de cobertura
    Entonces el número de falsos positivos es 0
    Y el recall sobre A y B en ese umbral se reporta por separado

  Escenario: El umbral no está escrito en el código
    Cuando cambio el umbral en la configuración
    Entonces el comportamiento cambia sin modificar el código fuente

  # ADR-021 (propuesta): segunda vía de respaldo
  Escenario: Coincidencia exacta de lema por debajo del umbral
    Dado una consulta cuyo término depurado es exactamente el lema de una entrada del diccionario
    Y cuya similitud máxima es inferior al umbral
    Cuando el sistema la procesa
    Entonces responde citando la entrada, el documento y la página
    Y la interfaz indica «respaldo: entrada exacta del diccionario»

  # ADR-022: tercer caso de RF-08
  Escenario: Material de prosa sin respaldo afirmable
    Dado una consulta sin respaldo cuyos pasajes de prosa comparten al menos dos palabras de contenido con ella
    Cuando el sistema la procesa
    Entonces declara la ausencia de información
    Y ofrece los pasajes literales y citados rotulados «no es una respuesta»
    Y la consulta se cuenta como abstención
```

**Notas.** PoC: τ = 0,41 (0 FP, 28/28, recall 0,856, F1 0,922). Implementación: τ = 0,48 (0 FP, 92,8 % atendibles; ADR-020), a re-medir en M3. El punto de mayor F1 (0,25) se
descarta por producir un falso positivo. Esta característica completa se ejecuta en **todas** las ramas.

---

### HU-07 · Ver documento y página de cada respuesta

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-07 Trazabilidad documental | PMV1 · S2 | Alta | RF-07, RNF-08, RN-03 | HU-03 | Por estimar |

**Como** docente **quiero** ver el documento y la página de los que proviene cada respuesta **para**
poder verificarla en la fuente original.

**INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓

```gherkin
# language: es
@HU-07 @PMV1
Característica: Trazabilidad documental de cada respuesta
  Como docente
  Quiero ver la fuente de cada respuesta
  Para verificarla en el documento original

  Escenario: Fuente disponible
    Cuando recibo una respuesta del sistema
    Entonces aparecen el nombre del documento, la página y el fragmento literal utilizados

  Escenario: Fragmento derivado de reconocimiento óptico
    Dado un fragmento con procedencia "reconocimiento óptico"
    Cuando se muestra la respuesta
    Entonces el sistema advierte que el texto puede contener errores de transcripción

  Escenario: Respuesta sin procedencia completa
    Dado un fragmento al que le falta el documento o la página
    Cuando el sistema compone la respuesta
    Entonces no la muestra
    Y registra un error de integridad del índice
```

---

## 6. Tema: Analítica predictiva (PMV2)

> Condición común: los modelos predictivos **solo pueden añadir abstenciones** (RN-06). Nunca convierten
> una abstención de τ en respuesta. Requieren el registro de consultas (RD-03), sujeto a ADR-013.

### HU-08.1 · Anticipar si hay respaldo antes de generar

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-08 Predicción de cobertura y de riesgo | PMV2 · S3 | Alta | RF-14, RN-06, RD-03 | Hito 1, ADR-013 | Por estimar |

**Como** integrante del equipo **quiero** que el sistema estime la probabilidad de responder con respaldo
antes de invocar al generador **para** evitar respuestas no documentadas y reducir el cómputo innecesario.

**INVEST:** I ✓ · N ✓ · V ✓ · E ~ (depende del volumen del registro) · S ✓ (tras la división) · T ✓

```gherkin
# language: es
@HU-08.1 @PMV2
Característica: Predicción de cobertura antes de generar
  Como integrante del equipo
  Quiero estimar si la consulta tiene respaldo antes de generar
  Para evitar respuestas sin respaldo y cómputo innecesario

  Escenario: Cobertura suficiente
    Dado una consulta con similitud mayor o igual que el umbral
    Y una probabilidad de cobertura estimada superior al umbral del clasificador
    Cuando se procesa la consulta
    Entonces el sistema procede a la generación
    Y registra la predicción junto con el resultado real

  Escenario: Cobertura insuficiente
    Dado una probabilidad de cobertura estimada inferior al umbral del clasificador
    Cuando se procesa la consulta
    Entonces el sistema se abstiene sin invocar al modelo generador
    Y registra el caso para el reentrenamiento

  @salvaguarda
  Escenario: El predictor no anula la regla del umbral
    Dado una consulta con similitud inferior a τ
    Y una probabilidad de cobertura estimada alta
    Cuando se procesa la consulta
    Entonces el sistema se abstiene

  @arnes
  Escenario: Criterio de cierre
    Cuando comparo en validación cruzada τ solo frente a τ con predictor
    Entonces la combinación no produce más falsos positivos que τ solo
    Y el resultado se reporta aunque la mejora sea nula
```

---

### HU-08.2 · Ajustar el umbral con la experiencia acumulada

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-08 Predicción de cobertura y de riesgo | PMV2 · S3 | Alta | RF-15, RN-04, RN-06 | HU-08.1 | Por estimar |

**Como** integrante del equipo **quiero** que el umbral se ajuste a partir de las decisiones registradas
**para** que no permanezca fijado a un valor arbitrario.

**INVEST:** I ✗ (tras HU-08.1) · N ✓ · V ✓ · E ~ · S ✓ · T ✓

```gherkin
# language: es
@HU-08.2 @PMV2 @salvaguarda
Característica: Umbral adaptativo con suelo de seguridad
  Como integrante del equipo
  Quiero ajustar el umbral con los datos registrados
  Para no depender de un valor fijo arbitrario

  Escenario: Ajuste dentro del margen seguro
    Dado un umbral calibrado sin falsos positivos
    Cuando el ajuste adaptativo propone un nuevo umbral
    Entonces el nuevo umbral no es inferior al último umbral sin falsos positivos calibrado con el arnés
    Y la partición C sigue produciendo 0 falsos positivos

  Escenario: El ajuste no mejora al umbral fijo
    Cuando el umbral adaptativo no mejora la decisión del umbral fijo en validación cruzada
    Entonces se conserva el umbral fijo
    Y el resultado negativo se registra como hallazgo
```

---

### HU-09 · Saber qué material conviene incorporar

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-09 Priorización predictiva del corpus | PMV2 · S3 | Media | RF-16, RD-03 | ADR-013 | Por estimar |

**Como** integrante del equipo **quiero** conocer qué campos semánticos concentran la demanda
insatisfecha **para** priorizar qué documentos incorporar en la siguiente iteración.

**INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓. **Riesgo declarado:** en doce semanas el registro real
puede no alcanzar 100 consultas; en ese caso el comportamiento correcto es el del segundo escenario, y
**no se fabrican consultas para alcanzar el mínimo** en el informe.

```gherkin
# language: es
@HU-09 @PMV2
Característica: Priorización del corpus por demanda insatisfecha
  Como integrante del equipo
  Quiero saber qué campos semánticos concentran la demanda insatisfecha
  Para priorizar la ampliación del corpus

  Escenario: Historial suficiente
    Dado un registro de al menos 100 consultas reales
    Cuando solicito el informe de priorización
    Entonces el sistema presenta los campos semánticos ordenados por demanda insatisfecha proyectada

  Escenario: Historial insuficiente
    Dado un registro con menos de 100 consultas
    Cuando solicito el informe
    Entonces el sistema indica que el historial es insuficiente
    Y no emite proyecciones
```

---

## 7. Tema: Despliegue móvil offline (PMV3)

### HU-10.1 · Consultar desde el teléfono sin conexión

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-10 Operación sin conexión | PMV3 · S4 | Alta | RNF-01, RNF-02, RNF-03, RNF-04 | HT-05, Hito 2 | Por estimar |

**Como** usuario de una zona rural del valle del Mantaro sin cobertura **quiero** consultar el asistente
desde mi teléfono sin internet **para** acceder al corpus donde la lengua se habla.

**INVEST:** I ✗ (requiere los artefactos del PMV2) · N ✓ · V ✓ · E ~ (por dispositivo) · S ✓ · T ✓

```gherkin
# language: es
@HU-10.1 @PMV3 @manual
Característica: Consulta sin conexión en el dispositivo
  Como usuario sin cobertura de red
  Quiero consultar desde el teléfono
  Para acceder al corpus en el territorio

  Escenario: Consulta en modo avión
    Dado la aplicación instalada con el modelo y el índice incorporados
    Y el dispositivo en modo avión
    Cuando consulto "¿cómo se dice zorro en quechua wanka?"
    Entonces la respuesta muestra "Atuq" con el documento y la página 37
    Y el tiempo total no supera 15 segundos
    Y la búsqueda en el índice no supera 100 milisegundos
```

### HU-10.2 · Misma salvaguarda en el teléfono

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-10 Operación sin conexión | PMV3 · S4 | Alta | RF-08, RN-01, DoD-4 | HT-05 | Por estimar |

**Como** usuario **quiero** que el teléfono se abstenga igual que el escritorio **para** no recibir
formas inventadas en ninguna plataforma.

```gherkin
# language: es
@HU-10.2 @PMV3 @salvaguarda @arnes
Característica: Equivalencia de la abstención entre plataformas
  Escenario: Cero falsos positivos en el dispositivo
    Dado el umbral calibrado para la estrategia de recuperación del móvil
    Cuando ejecuto en el dispositivo las 28 consultas de la partición C
    Entonces el número de falsos positivos es 0

  Escenario: Consulta sin respaldo en el teléfono
    Cuando consulto "¿cómo se dice criptomoneda en quechua wanka?" en modo avión
    Entonces la aplicación declara que no dispone de respaldo documental
    Y no muestra ninguna forma en quechua
```

### HU-10.3 · Instalación que no queda a medias

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-10 Operación sin conexión | PMV3 · S4 | Alta | RNF-04, RNF-05 | HU-10.1 | Por estimar |

**Como** usuario con un teléfono de gama media **quiero** saber si la aplicación cabe antes de
instalarla **para** no quedarme con una instalación incompleta.

```gherkin
# language: es
@HU-10.3 @PMV3 @manual
Característica: Instalación con verificación de espacio
  Escenario: Paquete dentro del límite
    Cuando compilo el paquete de instalación con modelo e índice
    Entonces su tamaño no supera 1,2 GB

  Escenario: Almacenamiento insuficiente
    Dado un dispositivo sin el espacio requerido
    Cuando intento instalar o preparar los recursos de la aplicación
    Entonces se informa el espacio necesario
    Y no queda una instalación incompleta
```

**Nota.** Si el paquete supera 1,2 GB, se activa la sustitución prevista (Gemma 3 1B + MediaPipe) y se
registra como decisión; implica recalibrar τ.

---

### HU-11 · Interfaz simple y legible

| Épica | PMV · Sprint | Prioridad | Requisitos | Depende de | Estimación |
|---|---|---|---|---|---|
| E-11 Accesibilidad de la interfaz | PMV3 · S4 | Media | RNF-09, WCAG 2.1 | HU-10.1 | Por estimar |

**Como** usuario adulto mayor o con baja alfabetización digital **quiero** una interfaz simple **para**
consultar el asistente sin ayuda de terceros.

```gherkin
# language: es
@HU-11 @PMV3
Característica: Interfaz accesible
  Escenario: Consulta en tres interacciones
    Dado que abro la aplicación por primera vez
    Cuando formulo una consulta básica
    Entonces la completo en un máximo de tres interacciones sin instrucciones adicionales

  Escenario: Tipografía ampliable sin pérdida de contenido
    Dado que aumento el tamaño de la tipografía al máximo del sistema
    Cuando leo una respuesta
    Entonces se ven la forma quechua, la fuente y el aviso de alcance sin quedar recortados
```

### 7.1 Criterios del PMV3 en dos modos (ADR-038, aclaración B0)

La app tiene un modo **en línea** (principal: cliente de la API desplegada) y un modo **sin conexión**
(respaldo: índice exportado y compositor determinista). Estos escenarios amplían los de HU-10.1 a HU-11
sin sustituirlos; los de modo avión siguen vigentes tal cual.

```gherkin
# language: es
@HU-10.1 @PMV3 @dos-modos
Característica: Consulta desde el teléfono en los dos modos
  Escenario: Consulta en línea contra la nube
    Dado la aplicación en modo automático y el teléfono con red
    Cuando consulto "zorro"
    Entonces la respuesta muestra "Atuq" con el documento y la página 37
    Y la respuesta indica "Respondido en línea · nube"
    Y se muestra el bloque de predicción ML con la probabilidad de respaldo

  Escenario: Cambio automático al corpus del teléfono
    Dado la aplicación en modo automático
    Y el dispositivo en modo avión
    Cuando consulto "zorro"
    Entonces la respuesta muestra "Atuq" con el documento y la página 37
    Y la respuesta indica "Respondido sin conexión · corpus local"
    Y explica que no hubo conexión con la nube
    Y el indicador de la cabecera muestra "Sin conexión · corpus local"

  Escenario: La nube no responde a tiempo
    Dado la aplicación en modo automático
    Y la API sin responder durante 20 segundos
    Cuando consulto un término
    Entonces responde el corpus del teléfono y la respuesta lo declara

  Escenario: Selector manual
    Cuando elijo "Solo sin conexión" en el selector de modo
    Entonces ninguna consulta sale del teléfono
    Y la preferencia se conserva al volver a abrir la aplicación

@HU-10.1 @PMV3 @nube
Característica: Comportamiento ante la nube
  Escenario: Arranque en frío de Render
    Dado la API en la nube suspendida
    Cuando una consulta tarda más de 4 segundos
    Entonces se muestra el mismo aviso de arranque en frío que en la web

  Escenario: Límite de consultas
    Dado que la API responde 429 con Retry-After
    Cuando consulto
    Entonces se muestra el mensaje del servidor y la espera
    Y la aplicación no reintenta sola
    Y el botón "Reintentar" se habilita al cumplirse la espera

@HU-10.2 @PMV3 @salvaguarda @arnes
Característica: Misma salvaguarda en los dos modos
  Escenario: Cero falsos positivos sin conexión en el dispositivo
    Cuando ejecuto en el dispositivo las 248 consultas de evaluacion_v2.json en modo sin conexión
    Entonces los falsos positivos de la partición C son 0
    Y el recall@5 de A, B y D es 1,000

  Escenario: Abstención en los dos modos
    Cuando consulto "criptomoneda" en línea y en modo avión
    Entonces en ambos casos la aplicación declara que no dispone de respaldo documental
    Y no muestra ninguna forma en quechua

@HU-10.1 @PMV3 @seguridad
Característica: La app no administra
  Escenario: Sin token ni funciones de administración
    Dado el código fuente de la aplicación
    Entonces no contiene ADMIN_TOKEN, TOKEN_PRUEBAS ni la cabecera X-Admin-Token
    Y solo envía POST a /api/consultas y /api/predicciones

@HU-11 @PMV3
Característica: Interfaz legible en el teléfono
  Escenario: Tamaño de letra como en la web
    Cuando pulso "A+" hasta el máximo
    Entonces se leen la forma quechua, la fuente y el aviso de alcance sin recortes
    Y "A" restablece el tamaño normal

  Escenario: Botones táctiles grandes
    Entonces los botones A−, A, A+ y Consultar miden al menos 48 px de alto
```

---

## 8. Historias técnicas (habilitadores)

### HT-00 · Repositorio, integración continua y entorno de agentes — Sprint 1, semana 1

**Para** que los agentes construyan sobre una base común. **Ya hecho (2026-09-24):** `CLAUDE.md`,
`.claude/agents/*`, `.claude/settings.json`, `.mcp.json`, `.gitignore`, `.env.example`,
`sonar-project.properties`, `corpus/` con manifiesto y `referencia_poc/`. **Falta:** repositorio privado
en GitHub con `main` protegida; esqueleto hexagonal con `uv` y Python 3.12 (`src/rag_quechua/{dominio,
puertos,adaptadores,aplicacion,entrada}`, `tests/`); prueba de arquitectura; comandos de `CLAUDE.md` §9;
GitHub Actions con `ruff`, `mypy`, `pytest --cov` con umbrales, `pip-audit` y análisis de SonarQube Cloud
que importe `coverage.xml`; plantillas de PR e *issue*. **Hecho cuando** un PR de prueba recorre todo el
circuito y SonarQube Cloud comenta el PR.

### HT-01 · Arnés de evaluación reproducible — Sprint 1

```gherkin
# language: es
@HT-01 @PMV1 @arnes
Característica: Arnés de evaluación
  Escenario: Ejecución completa por particiones
    Dado el conjunto de evaluación versionado
    Cuando ejecuto el arnés con la configuración vigente
    Entonces obtengo recall@1, recall@5 y MRR@10 para A, B y D por separado
    Y la matriz de confusión con el recuento explícito de falsos positivos para C
    Y el resultado se guarda con la versión de corpus, segmentación, codificador y τ

  Escenario: Reproducción de la línea base de la prueba de concepto
    Cuando ejecuto el arnés con la estrategia híbrida léxica y el τ vigente
    Entonces recall@5 en A y B es 1,000
    Y los falsos positivos en C son 0
```

No usa exactitud (*accuracy*): las clases están desequilibradas 220 frente a 28.

### HT-02 · Conjunto de evaluación externo — Sprints 1 y 2 (**tarea humana**)

Consultas formuladas por docentes de EIB (RD-04), incorporadas como partición `E` y reportadas por
separado. Los agentes preparan el formato y el procedimiento; **no generan las consultas**. Ampliar
además C con consultas del dominio cultural ausentes del corpus. Si no se obtienen a tiempo, se declara
como limitación en el Hito 1.

### HT-03 · Traducción de la consulta y recalibración de τ — Sprint 2

```gherkin
# language: es
@HT-03 @PMV1 @arnes @salvaguarda
Característica: Traducción previa y recalibración
  Escenario: La traducción no toca el quechua
    Dado una consulta en inglés cuya respuesta tiene respaldo
    Cuando se traduce la consulta y se recupera
    Entonces la forma quechua de la salida es idéntica a la del fragmento recuperado

  Escenario: Recalibración tras incorporar la traducción
    Cuando barro el umbral con el arnés sobre A, B, C, D y E
    Entonces se registra el primer umbral sin falsos positivos
    Y se actualiza la configuración versionada con ese valor y su justificación
```

### HT-04 · Servicio local y interfaz de escritorio — Sprint 2

FastAPI escuchando solo en `127.0.0.1` (RS-01) y **React + Vite** como cliente de la API (ADR-025). La interfaz muestra:
consulta, respuesta, forma quechua, fragmento, documento, página, advertencia OCR, traducción usada y
aviso de alcance. Cubierta por los escenarios de HU-03, HU-06 y HU-07.

### HT-05 · Artefactos móviles y equivalencia entre plataformas — Sprint 3

**Línea base v2:** exportación del índice léxico a binarios planos por columnas, tabla EN→ES y compositor
determinista; sin modelo ni codificador en el dispositivo (ADR-019, ADR-026). **Criterio de paso del
Hito 2:** paridad aritmética entre motores (< 1 × 10⁻⁶, top-5 idéntico) — declarada cumplida en la revisión
2 y a verificar en M13. Una divergencia no resuelta reorienta el sprint 4 (Documento 4).

### HT-06 · Medición de rendimiento y recursos — Sprints 2 y 4

Percentil 95 del tiempo de respuesta, pico de VRAM, latencia de recuperación, tamaño del paquete.
Resultados en `04_SPRINTS.md` con su medio de verificación; nunca estimados.

### HT-07 · Evaluar bge-m3 como complemento — Sprint 2 (espiga, prioridad baja)

El Documento 5 eligió bge-m3 para escritorio, pero la PoC no lo midió. Se mide en el arnés como
complemento del híbrido léxico y solo se adopta si mejora sin romper la separación que sostiene τ.
Verificar antes si el adaptador vía Ollama expone la parte dispersa o solo la densa.

---

### HT-08 · Servidor MCP de desarrollo — Sprints 1 y 2 (ADR-017)

Adaptador de entrada con el SDK oficial de MCP para Python, transporte `stdio`, que llama a los mismos
casos de uso que FastAPI. Herramientas de **solo lectura**: `estado_indice` y `buscar_fragmentos`
(al cerrar HU-02), `ejecutar_arnes` (al cerrar HT-01), `consultar` y `verificar_salvaguarda` (al cerrar
HU-03 y HU-06). Se registra en `.mcp.json` cuando exista la primera herramienta. No forma parte del
producto (RS-08).

```gherkin
# language: es
@HT-08 @PMV1 @salvaguarda
Característica: Servidor MCP de desarrollo
  Escenario: Las herramientas reproducen el comportamiento del sistema
    Cuando un agente invoca "consultar" con "¿cómo se dice criptomoneda en quechua wanka?"
    Entonces la herramienta devuelve la declaración de ausencia de información
    Y no devuelve ninguna forma en quechua

  Escenario: Solo lectura
    Cuando se listan las herramientas del servidor
    Entonces ninguna modifica el índice, la configuración ni el corpus
```

---

## 9. Registro de cambios

| Fecha | Versión | Cambio | Decisión |
|---|---|---|---|
| 2026-09-24 | 1.0 | Creación; división de HU-08 y HU-10; historias técnicas HT-00…HT-07 | — |
| 2026-09-24 | 1.1 | HT-00 en la semana 1 del sprint 1; escenario de identificadores en HU-02; nueva HT-08 | ADR-017, ADR-018 |
| 2026-11-19 | 1.2 | §7.1: criterios Gherkin del PMV3 en dos modos (en línea y sin conexión) | ADR-038 |
| 2026-11-24 | 1.3 | Estado final de HU-10.1 a HU-10.3 y HU-11 en el índice; sprint alineado con Trello (S3, 06/11–13/12) | Ronda 2 (P7) |
