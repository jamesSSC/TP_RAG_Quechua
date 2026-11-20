# B11 · Logo del proyecto en la web y en la app

Atiende el bloque B11 del paquete de la entrega final (indicador 8 de la lista de cotejo U4: producto
final con evidencias). La guía pide `./docs`; se usó `./docs_entrega_final` para no mezclarla con la
documentación SDD de `docs/`.

Logo aprobado por el equipo el 19/11/2026, en `assets/marca/` (SVG y PNG de 1024 px, versiones
icono y contorno). Paleta de la web: `#FAF7F2`, `#F0EBE2`, `#8A5A2B`, `#86581A`, `#1C1A17`,
`#5D574F`, `#DED5C7`; coincide con las variables de `frontend/src/index.css` (sin diferencias).

| Captura | Qué se ve |
|---|---|
| `B11_web_local_antes_sin_logo.png` | Web local antes: título sin logo |
| `B11_web_local_despues_con_logo.png` | Web local después: logo a la izquierda del título |
| `B11_web_local_despues_movil_390.png` | Web local después, ancho de teléfono (390 px) |
| `B11_web_nube_antes_sin_logo.png` | Web en Render antes (solo se abrió la página, sin consultar) |
| `B11_movil_antes_app_paleta_verde.png` | App antes: paleta verde, sin logo |
| `B11_movil_despues_app_paleta_web.png` | App después: paleta y logo de la web |
| `B11_movil_antes_cajon_icono_verde.png` | Cajón de apps antes: ícono verde anterior |
| `B11_movil_despues_cajon_icono_logo.png` | Cajón de apps después: ícono adaptativo con el logo |

**Pendiente:** la captura «después» de la web en la nube. Render despliega desde `main` del repositorio
del equipo: se toma cuando este PR esté fusionado y desplegado.

Verificación: `npx vitest run` (48 pruebas, incluida `src/Cabecera.logo.test.jsx`) y `npx vite build`.
En la app: `flutter test` (45) y el ícono generado con `flutter_launcher_icons`.
