# Auditoría de calidad (FURPS+) y seguridad (OWASP Top 10) · S13

Entregables de la *Guía para la evaluación, mejora y validación de la calidad y seguridad de software
mediante FURPS+ y OWASP Top 10 utilizando agentes de IA* del docente, aplicada a la versión web del
Asistente de consulta del quechua wanka (<https://quechua-web.onrender.com> y
<https://quechua-api.onrender.com>).

> La guía pide `./docs`; se usó `./docs_auditoria` para no mezclarla con la documentación del proyecto en `docs/`.

Los pasos de auditoría (1, 4, 5, 8 y 9) los ejecutaron subagentes independientes que recibieron el prompt
del docente tal cual y no modificaron código. Los pasos de planificación y aplicación (2, 3, 6 y 7) los
ejecutó el agente principal. Las decisiones de diseño que resultaron constan como ADR-033 a ADR-037 en
[`../docs/07_DECISIONES.md`](../docs/07_DECISIONES.md).

## Los nueve pasos

| Paso | Agente (prompt del docente) | Archivo | PR |
|---|---|---|---|
| 1 | Auditor FURPS+ | [01_auditoria_furps.md](01_auditoria_furps.md) | [#23](https://github.com/omarpiero/TP_RAG_Quechua/pull/23) |
| 2 | Planificador FURPS+ | [02_plan_furps.md](02_plan_furps.md) | [#23](https://github.com/omarpiero/TP_RAG_Quechua/pull/23) |
| 3 | Aplicación del plan FURPS+ (agente principal) | Código, pruebas y [evidencias](evidencias/despues/) | [#23](https://github.com/omarpiero/TP_RAG_Quechua/pull/23) |
| 4 | Auditor de implementación FURPS+ | [03_auditoria_implementacion_furps.md](03_auditoria_implementacion_furps.md) | [#23](https://github.com/omarpiero/TP_RAG_Quechua/pull/23) |
| 5 | Auditor OWASP Top 10 | [04_auditoria_owasp.md](04_auditoria_owasp.md) | [#24](https://github.com/omarpiero/TP_RAG_Quechua/pull/24) |
| 6 | Planificador OWASP Top 10 | [05_plan_owasp.md](05_plan_owasp.md) | [#24](https://github.com/omarpiero/TP_RAG_Quechua/pull/24) |
| 7 | Aplicación del plan OWASP (agente principal) | Código, pruebas y [evidencias](evidencias/despues/) | [#24](https://github.com/omarpiero/TP_RAG_Quechua/pull/24) y [#26](https://github.com/omarpiero/TP_RAG_Quechua/pull/26) (validación del token en la interfaz, NV-06) |
| 8 | Auditor de implementación OWASP | [06_auditoria_implementacion_owasp.md](06_auditoria_implementacion_owasp.md) | [#24](https://github.com/omarpiero/TP_RAG_Quechua/pull/24) |
| 9 | Auditor final integral, con adenda de la verificación en la nube | [07_auditoria_final.md](07_auditoria_final.md) | [#24](https://github.com/omarpiero/TP_RAG_Quechua/pull/24) y [#25](https://github.com/omarpiero/TP_RAG_Quechua/pull/25) |
| 10 | Auditoría delta del PMV3 (app móvil en dos modos y arreglos de la S14) | [08_auditoria_delta_pmv3.md](08_auditoria_delta_pmv3.md) | rama `docs/auditoria-delta-pmv3` |

## Estructura de `evidencias/`

```
evidencias/
├── antes/          capturas previas a los cambios (nube y código de cada hallazgo crítico o alto)
│   └── salidas/    salidas de terminal: pytest, Vitest, E2E, Newman, arnés de 248 consultas, demostraciones locales
├── despues/        capturas tras cada fase, en local (aviso de arranque en frío, 401/403/429, solo lectura)
│   └── salidas/    las mismas baterías, después de la fase 1 y de la fase 2
├── nube/           paso 9: verificación en la nube tras fusionar (401/403, consulta pública, CI en verde)
│   └── salidas/    salidas de los curl contra la nube (tokens enmascarados)
└── herramientas/   capturar.mjs (capturas con la URL visible) y proxy_lento.mjs (simula el arranque en frío)
```

Nombres de archivo: `<paso>_<categoría>_<qué_se_ve>.png`, por ejemplo
`04_A01_delete_historial_sin_auth_codigo.png`.

## Resultados

| Marco | Antes | Después | Fuente |
|---|---|---|---|
| FURPS+ (global, 0–10) | 6,9 | 7,4 | [01](01_auditoria_furps.md) → [03](03_auditoria_implementacion_furps.md) |
| OWASP Top 10 (0–100) | 61,0 (con un crítico: no apto para exposición pública) | 79,0 (sin críticos) | [04](04_auditoria_owasp.md) → [06](06_auditoria_implementacion_owasp.md) |

**Dictamen final ([07](07_auditoria_final.md)): apto para producción con observaciones.** Quedó verificado
en la nube tras la fusión y la definición de `ADMIN_TOKEN`. Las observaciones y los riesgos residuales
(CSP del sitio estático, `npm audit` en dependencias de desarrollo, límite de peticiones en memoria,
cuarentena de documentos y keep-alive del PR #22) se detallan en el propio dictamen.

En toda la auditoría se respetó la salvaguarda del sistema: τ = 0,48, RN-06 y el verificador de forma
literal (ADR-028) no se modificaron. El arnés de 248 consultas dio resultados idénticos byte a byte
antes y después de cada fase.
