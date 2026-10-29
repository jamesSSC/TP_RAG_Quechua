# B13 · accesibilidad de formularios (axe-core, WCAG 2 A/AA)

`npm run test:e2e` incluye `a11y.real.spec.js`: axe-core (`wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`) sobre las cuatro vistas con backend y datos
(Consultar con una respuesta, Fuentes del corpus, Incorporar documentos, Predicción ML) y una medición de objetivos táctiles (< 44 px). Sin texto de la página en la evidencia.

| Vista | Infracciones antes | Infracciones después | Objetivos < 44 px antes | después |
|---|---|---|---|---|
| Consultar | 1 | 0 | 8 | 0 |
| Fuentes del corpus | 1 | 0 | 11 | 0 |
| Incorporar documentos | 1 | 0 | 10 | 0 |
| Predicción ML | 2 | 0 | 9 | 0 |

Antes: `label-content-name-mismatch` (botones A−/A+: el nombre accesible no contenía el texto visible) y `color-contrast` (aviso ámbar sobre el papel, 4,4:1).
Cambios: nombres accesibles que empiezan por el texto visible, `aria-describedby` del formulario hacia su mensaje de error (`role="alert"`) en Fuentes e
Incorporar, `--abstencion` más oscuro (≥ 4,5:1), objetivos de 44 px en botones, campos y casilla. El foco visible ya existía (`:focus-visible`, 3 px). La estructura de pestañas no cambió.
Se regeneraron las capturas de B6 (20 pruebas E2E aprobadas de 20; Vitest 26/26).
