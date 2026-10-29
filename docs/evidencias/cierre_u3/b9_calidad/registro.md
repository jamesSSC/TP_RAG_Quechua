# B9 · calidad estática y seguridad

| Medida | Antes | Después |
|---|---|---|
| `ConsultarCorpusUseCase._resolver` (radon cc) | E (32) | B (6); los pasos extraídos están entre A (1) y B (8) |
| Complejidad media del backend (radon cc -a) | A (2,53) | A (2,47) |
| Bandit (src) | 0 altos, 0 medios, 1 bajo | 0 altos, 0 medios, 1 bajo |
| Arnés de 248 (`arnes_por_consulta.csv`, `barrido_umbral.csv`) | línea base | byte a byte igual |
| `evaluar_pmv2` | RN-06 true, FP en C 0 | RN-06 true, FP en C 0 |

SonarQube Community local (`omarpiero_rag-quechua-wanka`, rama `refactor/resolver-complejidad`, `sonar.json`): bugs 0, vulnerabilidades 0,
hotspots 0, code smells 83 (3 críticos), duplicación 0,7 %, cobertura de Python 77,6 %, puerta de calidad ERROR por 44 violaciones nuevas
(todas code smells; solo se registran, no se corrigen aquí).

**OWASP ZAP: pendiente.** ZAP 2.17 arranca en modo daemon pero su complemento de red falla en este entorno con
«Unexpected failure opening I/O selector» (Java NIO no puede abrir el selector bajo las restricciones del entorno de ejecución), de modo que no
llega a escuchar. No se desactivó la restricción. Mientras no se pueda escanear, se añadió por prudencia un middleware de cabeceras de seguridad
(`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, CSP sin terceros para la interfaz,
`Cache-Control: no-store` en `/api`) con sus pruebas; la interfaz servida por el backend carga bajo esa CSP sin errores de consola.
Esto NO es el resultado de un escaneo: el antes/después de ZAP queda por medir.
