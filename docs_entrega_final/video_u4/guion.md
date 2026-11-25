# B5 · Guion del video U4 por episodios

Atiende el **indicador 7** de la lista de cotejo U4: «demostración con 7 operaciones del funcionamiento
del software con el primer, segundo y tercer producto mínimo viable, cada uno con ML, a través del
video de software con episodios». También alimenta el anexo D del informe. La guía pide `./docs`; se
usó `./docs_entrega_final` para no mezclarla con la documentación SDD de `docs/`.

> **Duración: conflicto que confirmar con el docente.** La consigna anterior dice «no más de
> 8 minutos» y la consigna ICACIT, «no más de 20 minutos». Este guion propone **≈ 15 min**, con el
> tiempo de cada episodio. Si el docente confirma 8 min, la columna «versión 8 min» indica qué recortar.

**Reglas de grabación.**
- Datos reales del corpus. Ninguna forma quechua se dice ni se escribe a mano: se lee la pantalla.
- No se muestran secretos ni los paneles de Render o Neon con credenciales.
- Despertar la nube 5 min antes (abrir la web y esperar el estado). Si aparece el aviso de arranque en
  frío, se aprovecha para explicarlo.
- Un solo narrador por episodio, con el rol del informe.

| # | Episodio | Narra | ≈ 15 min | Versión 8 min |
|---|---|---|---|---|
| 1 | Título e integrantes | Omar Terbullino (Scrum Master, QA) | 0:30 | 0:20 |
| 2 | Problema, objetivos y solución por PMV | Omar Terbullino | 1:30 | 0:50 |
| 3 | Arquitectura de software y tecnológica, con herramientas | James Saenz (Lead Backend & AI) | 2:00 | 1:00 |
| 4 | PMV1 por HU, con ML | Yeferson Serpa (Lead Frontend) | 3:00 | 1:40 |
| 5 | PMV2 por HU, con ML | James Saenz | 2:30 | 1:30 |
| 6 | PMV3 por HU, con ML: app en línea y sin conexión | James Saenz | 3:30 | 1:50 |
| 7 | GitHub: hexagonal de la HU principal | Yeferson Serpa | 2:00 | 0:50 |
| | **Total** | | **15:00** | **8:00** |

---

## Episodio 1 · Título e integrantes (0:30)

- Pantalla: logo del proyecto (`assets/marca/logo_contorno_1024.png`) y título «Asistente de consulta
  del quechua wanka».
- Texto: «Taller de Proyectos de Ingeniería 1 · Universidad Continental · NRC 30170 · Docente Guevara
  Jiménez».
- Integrantes con su rol: Terbullino, O. (Scrum Master, arquitecto, QA y DevOps) · Saenz, J. (Lead
  Backend & AI) · Serpa, Y. (Lead Frontend).

## Episodio 2 · Problema, objetivos y solución por PMV (1:30)

1. Problema: el corpus del quechua wanka está disperso en PDF y un asistente genérico inventa formas.
   Dato: vitalidad de la lengua y 0 de 50 estudios con RAG (tomar las cifras del informe, sección I).
2. Objetivo general y OE1 a OE3, uno por PMV.
3. Solución por PMV:
   - **PMV1:** consulta con cita y abstención (τ = 0,48);
   - **PMV2:** dos predictores ML y la nube;
   - **PMV3:** app móvil en línea y sin conexión.
4. Alcance: «herramienta de consulta sobre fuentes publicadas; no es una autoridad lingüística».

## Episodio 3 · Arquitectura de software y tecnológica (2:00)

1. **Hexagonal:** mostrar `docs_ingenieria_inversa/uml/ii_03_componentes.png`. Dominio y aplicación en el
   centro; 7 puertos de entrada y 10 de salida; adaptadores (REST, SQLAlchemy, índice, Gemini u Ollama,
   predictores, traductor).
2. **Despliegue:** navegador → Render (`quechua-web` estático y `quechua-api` FastAPI) → Neon PostgreSQL
   (AWS us-east-1) y Gemini; teléfono → API en la nube o corpus local (ADR-038).
3. **Herramientas**, una línea cada una:
   - Python 3.12, FastAPI, scikit-learn, SQLAlchemy;
   - React 19 y Vite;
   - Flutter 3.44;
   - PostgreSQL/Neon y Render;
   - Gemini 3.5 Flash-Lite y Ollama (Qwen3.5 4B);
   - GitHub Actions, Trello y Postman.

## Episodio 4 · PMV1 por HU, con ML (3:00) — web en la nube

| Op. | HU | Acción en pantalla | Resultado esperado (leer de la pantalla) | ML visible |
|---|---|---|---|---|
| 1 | HU-03 | Consultar «zorro» | Forma con documento y **página 37** | Probabilidad de respaldo alta |
| 2 | HU-07 | Desplegar «Fuente consultada» | Fragmento literal y similitud frente a τ | ídem |
| 3 | HU-06 | Consultar «criptomoneda» | «Sin respaldo documental», ninguna forma | Probabilidad baja |
| 4 | HU-05 | Consultar «how do you say water» | Forma con fuente; aviso de que se buscó en español | Probabilidad |
| 5 | HU-05 | Consultar «love» (palabra inglesa suelta) | Respuesta con su fuente | Probabilidad |
| 6 | HU-03 | Consultar «perro» (lema bajo el umbral) | «Respaldo: entrada exacta del diccionario» | Probabilidad |
| 7 | RF-11 | Ver el historial de la sesión | Las consultas anteriores con su estado | — |

## Episodio 5 · PMV2 por HU, con ML (2:30) — web en la nube

| Op. | HU | Acción | Resultado esperado | ML |
|---|---|---|---|---|
| 1 | HU-08.1 | Pestaña Predicción ML: ejemplo «zorro» | Predicción 1 alta, sobre el corte 0,25 | **Predicción 1** |
| 2 | HU-08.1 | Ejemplo «criptomoneda» | Predicción 1 bajo el corte: «se abstendría» | **Predicción 1** |
| 3 | HU-04 | Ejemplo «¿Para qué sirven los sufijos en la gramática?» | Predicción 2 sobre 0,50: «mostrar pasajes» | **Predicción 2** |
| 4 | HU-04 | En Consultar, la misma pregunta | Pasajes citados, «no es una respuesta» | Predicción 2 en la respuesta |
| 5 | HU-08.1 | Bajar a «Modelos»: AUC, F1, matriz y ROC | AUC 0,996 (cobertura) y 0,980 (pasajes) | Métricas |
| 6 | HU-09 | Analítica de demanda | Consultas por origen; aviso de demostración | Demanda ponderada por el modelo |
| 7 | HU-01 | Fuentes del corpus (solo lectura sin token) | 8 documentos; gestión bloqueada sin token | — |

## Episodio 6 · PMV3 por HU, con ML (3:30) — teléfono

Grabar la pantalla del teléfono (o del emulador) con la barra de estado visible.

| Op. | HU | Acción | Resultado esperado | ML |
|---|---|---|---|---|
| 1 | HU-10.1 | Abrir la app con red | Cabecera «En línea · nube», 3 605 fragmentos y 8 documentos | — |
| 2 | HU-10.1 | Tocar el ejemplo «zorro» | Forma, **página 37**, «Respondido en línea · nube» | **Predicción 1** en la tarjeta |
| 3 | HU-08.1 | Pestaña Predicción ML: ejemplo «criptomoneda» | Las dos probabilidades y las variables con su peso | **Predicción 1 y 2** |
| 4 | HU-10.1 | Activar el **modo avión** y repetir «zorro» | Pasa sola a «Sin conexión · corpus local» y lo explica | Bloque ML: «no disponible sin conexión» |
| 5 | HU-10.2 | En modo avión, «criptomoneda» | «Sin respaldo documental», ninguna forma | — |
| 6 | HU-10.1 | Selector de modo → «Solo sin conexión» | Indicador fijo; nada sale del teléfono | — |
| 7 | HU-11 | A+ hasta el máximo | Forma, fuente y aviso legibles | — |

Cierre del episodio: el arnés de 248 consultas corrió en el dispositivo con 0 falsos positivos
(`docs/evidencias/pmv3/movil/HU-10.2_movil_arnes_248_resumen.png`).

## Episodio 7 · GitHub: hexagonal de la HU principal (2:00)

HU-03/HU-07, consulta con cita, recorriendo el código en GitHub:

1. **Controlador:** `backend/src/adapters/in/rest/consultas_controller.py` (`POST /api/consultas`).
2. **Puerto de entrada:** `backend/src/application/ports/in/consultar_corpus_port.py`.
3. **Caso de uso:** `backend/src/application/use_cases/consultar_corpus.py` (`ejecutar`).
4. **Dominio:** `backend/src/domain/services/evaluador_confianza.py` (τ y lema) y
   `domain/entities/respuesta.py` (RN-03: sin abstención, respaldo ≥ 1).
5. **Adaptadores de salida:** `adapters/out/recuperacion/indice_hibrido_lexico.py`,
   `adapters/out/generacion/gemini_generador.py`, `adapters/out/prediccion/predictor_sklearn.py`.
6. **Composición:** `backend/src/infrastructure/contenedor.py`. En la app, `mobile/lib/infraestructura/contenedor.dart`:
   el mismo puerto cumplido por la nube o por el teléfono.
7. **La app en el mismo repositorio:** carpeta `mobile/` (traída con su historial) y la
   [Release v1.1.0](https://github.com/DalgomXD-byte/quechua-wanka-movil/releases/tag/v1.1.0) con el
   APK y su SHA-256; es el destino del QR del póster.

## Lista de tomas

| Toma | Episodio | Pantalla | Entorno | Consulta | Narra |
|---|---|---|---|---|---|
| T01 | 1 | Logo y título | Diapositiva | — | Omar |
| T02 | 2 | Diapositivas del problema y objetivos | Diapositiva | — | Omar |
| T03 | 3 | UML de componentes y de despliegue | Diapositiva | — | James |
| T04 | 4 | Web, pestaña Consultar | Nube | zorro, criptomoneda, how do you say water, love, perro | Yeferson |
| T05 | 4 | Web, historial | Nube | — | Yeferson |
| T06 | 5 | Web, pestaña Predicción ML | Nube | zorro, criptomoneda, sufijos | James |
| T07 | 5 | Web, Analítica y Fuentes | Nube | — | James |
| T08 | 6 | App con red | Teléfono | zorro, criptomoneda | James |
| T09 | 6 | App en modo avión | Teléfono | zorro, criptomoneda | James |
| T10 | 6 | Selector de modo y A+ | Teléfono | — | James |
| T11 | 7 | Repositorio en GitHub | Navegador | — | Yeferson |

**Nota sobre HU-09:** las consultas que se hagan al grabar cuentan como demanda real. Anoten la fecha y
la hora de la grabación para poder rotularlas como `humo` si el equipo lo decide (guía 02, paso 4).
