# Protocolo de la prueba con usuarios finales

Atiende el **indicador 9** de la lista de cotejo U4 (6 puntos): «prueba con usuarios finales a
través de la retroalimentación y acta de reunión». Va en la sección **8.11** del informe y en el
**anexo B**.

> El agente solo preparó estos materiales. **La prueba la hace el equipo con personas reales.**
> Ningún resultado de este documento está medido todavía.

## 1. Objetivo

Comprobar si docentes y estudiantes de Educación Intercultural Bilingüe (EIB) pueden usar el asistente
(web y app) para tres cosas: obtener la forma documentada de una palabra con su fuente, reconocer
cuándo el sistema no tiene respaldo, y entender la diferencia entre el modo en línea y el modo sin
conexión. Se mide el éxito de cada tarea, el tiempo, los errores y la usabilidad percibida (SUS).

## 2. Participantes

- **Perfil:** docentes o estudiantes de EIB, o de carreras afines (educación, lingüística), del
  valle del Mantaro si es posible. Mayores de edad. Sin vínculo con el equipo.
- **Cantidad:** de 5 a 8. Con 5 participantes ya aparecen la mayoría de los problemas de usabilidad;
  el SUS se reporta con la media y el rango, sin generalizarlo.
- **Exclusión:** integrantes del equipo y personas que hayan visto la demo del curso.
- **Consentimiento:** firmado antes de empezar (`consentimiento.md`). No se registra el nombre en los
  datos: cada persona es P01, P02, etc.

## 3. Materiales y entorno

| Elemento | Detalle |
|---|---|
| Web | <https://quechua-web.onrender.com>. **Despertarla 5 min antes:** abrir la página y esperar al estado |
| App | APK release arm64 en un teléfono Android del equipo, en modo **automático** |
| Registro | Cronómetro y esta hoja por participante. Opcional: grabación de la pantalla, con consentimiento |
| Cuestionario | `cuestionario_SUS.md` (10 preguntas, escala de 1 a 5) |
| Datos | `resultados_plantilla.csv` → `analizar_resultados.py` |

**Aviso importante sobre HU-09:** las consultas que hagan los participantes en la nube se registran
como demanda real (`origen = usuario`), y eso es correcto: son usuarios reales. Anoten la fecha y la
hora de inicio y fin de la sesión en el acta. Así, si después se analiza la demanda, se sabe qué
consultas vinieron de la prueba.

## 4. Tareas (una por HU principal y por PMV)

La consulta sugerida está entre comillas. El participante la escribe o elige a su manera; no se le
dicta la respuesta. Todas las formas esperadas salen del corpus: el moderador **no** debe decirlas.

| # | PMV | HU | Tarea que se lee al participante | Éxito si… | Tiempo máx. |
|---|---|---|---|---|---|
| T1 | PMV1 | HU-03, HU-07 | «En la web, averigüe cómo se dice *zorro* en quechua wanka y en qué documento y página aparece.» | Lee la forma y dice el documento y la **página 37** | 2 min |
| T2 | PMV1 | HU-06 | «Ahora pregunte por *criptomoneda*. ¿Qué le responde el sistema? ¿Le da una palabra?» | Explica que el sistema **no tiene respaldo** y no inventa una forma | 2 min |
| T3 | PMV1 | HU-05 | «Pregunte en inglés: *how do you say water*.» | Obtiene una forma con su fuente y nota que se buscó en español | 2 min |
| T4 | PMV2 | HU-08.1 | «En la pestaña Predicción ML, pruebe *zorro* y *criptomoneda*. ¿Qué cree que significa la probabilidad?» | Relaciona la probabilidad alta o baja con «hay o no hay respaldo» | 3 min |
| T5 | PMV2 | HU-04 | «Pregunte *¿para qué sirven los sufijos en la gramática?* ¿Qué le muestra el sistema?» | Reconoce que son **pasajes** citados, «no una respuesta» | 3 min |
| T6 | PMV3 | HU-10.1 | «En el teléfono, consulte *perro*. Luego active el modo avión y repita la consulta.» | Obtiene respuesta en los dos casos y señala que el indicador cambió a «Sin conexión» | 3 min |
| T7 | PMV3 | HU-11 | «Agrande la letra al máximo y lea la fuente de la última respuesta.» | Usa A+ y lee la fuente sin ayuda | 1 min |

Orden: T1 → T7. Antes de T6 el moderador comprueba que el teléfono tenga red.

## 5. Desarrollo de la sesión (20–25 min por persona)

1. Bienvenida, explicación y firma del consentimiento (3 min).
2. Pregunta inicial: experiencia con el quechua y con diccionarios digitales (1 min).
3. Tareas T1 a T7 en voz alta («piense en voz alta»). El moderador no ayuda. Si a los 2 intentos la
   persona se bloquea, se anota «con ayuda» y se pasa a la siguiente (15 min).
4. Cuestionario SUS (3 min).
5. Preguntas abiertas (3 min):
   - ¿Qué fue lo más útil?
   - ¿Qué le confundió?
   - ¿Le parece correcto que el sistema diga «no tengo respaldo» en lugar de inventar?
   - ¿Usaría la app sin conexión? ¿Dónde?

## 6. Métricas

| Métrica | Cómo se registra | Cómo se reporta |
|---|---|---|
| Éxito de la tarea | 1 = sin ayuda · 0,5 = con ayuda · 0 = no lo logró | % por tarea y global |
| Tiempo | Segundos desde que se lee la tarea hasta que el participante dice «listo» | Mediana y rango por tarea |
| Errores | Número de acciones equivocadas (pestaña errónea, consulta mal escrita que obliga a repetir) | Total por tarea |
| SUS | 10 respuestas de 1 a 5 → puntaje de 0 a 100 | Media, desviación y rango; referencia 68 = promedio |
| Comentarios | Literales | Agrupados por tema en el acta |

## 7. Después de la sesión

1. Volcar los datos en `resultados_plantilla.csv` (una fila por participante).
2. `python analizar_resultados.py resultados.csv` → tabla y resumen para el informe.
3. Completar `acta_plantilla.md` con las firmas y adjuntarla al anexo B.
4. Registrar los problemas detectados como tarjetas de deuda o mejora en Trello.
