# B4 · Prueba con usuarios finales

Atiende el **indicador 9** de la lista de cotejo U4 (6 puntos), la sección 8.11 del informe y el
anexo B. La guía pide `./docs`; se usó `./docs_entrega_final` para no mezclarla con la documentación
SDD de `docs/`.

**La prueba la hace el equipo con personas reales.** Aquí solo están los materiales: no hay ningún
resultado medido.

| Archivo | Para qué |
|---|---|
| `protocolo.md` | Objetivo, perfil de los participantes, 7 tareas (una por HU principal y por PMV), métricas y desarrollo de la sesión |
| `consentimiento.md` | Consentimiento informado, uno por participante |
| `cuestionario_SUS.md` | Las 10 preguntas SUS y cómo se calcula el puntaje |
| `acta_plantilla.md` | Acta de la reunión con participantes, resultados, retroalimentación, acuerdos y firmas |
| `resultados_plantilla.csv` | Cabecera para volcar los datos (una fila por participante) |
| `analizar_resultados.py` | `python analizar_resultados.py resultados.csv` → SUS, éxito, tiempos y errores (solo biblioteca estándar) |
