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
| `llenar_acta.py` | Escribe la sección 6 (tablas 6.1 y 6.2) en una copia del **acta en Word de Omar** (`Acta_Prueba_Usuarios_Finales.docx`) a partir del mismo CSV. Requiere `python-docx` |

## Flujo con el acta en Word (24/11)

El acta oficial es el Word que preparó Omar, que trae los anexos 1 a 4 por participante. Las tareas
T1 a T7 y el SUS son los mismos de este kit.

1. **Antes de la sesión:**
   - despertar la web;
   - anotar en el acta el commit que muestra el pie de la web («versión: API … · web …», PR #37);
   - anotar la versión del APK: v1.1.0, de la [Release](https://github.com/DalgomXD-byte/quechua-wanka-movil/releases/tag/v1.1.0).
2. **Por participante:**
   - consentimiento (anexo 1);
   - hoja de registro (anexo 2);
   - SUS (anexo 3);
   - hora de inicio y de fin, que sirven para identificar sus consultas en la base (HU-09).
3. **Después:**
   - pasar las hojas a `resultados.csv`, con el formato de `resultados_plantilla.csv`;
   - correr `python llenar_acta.py resultados.csv Acta_Prueba_Usuarios_Finales.docx Acta_llena.docx`;
   - completar a mano la retroalimentación, los problemas (UF-0x), los acuerdos, las firmas y las fotos.

Los datos y los nombres de los participantes **no se suben** al repositorio: solo el acta firmada va al
anexo B del informe.
