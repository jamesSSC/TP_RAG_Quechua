# Dailies sugeridas del PMV3

Textos para que **cada integrante los publique desde su propia cuenta** (Trello o el canal del equipo).
El agente no los publica. Aquí solo están los de James, sacados de la bitácora. Los de Omar y Yeferson
los escribe cada uno.

## James Saenz · 19/11/2026

- **Ayer:** revisión del paquete del PMV3 y de la entrega final. El fork estaba 36 commits detrás:
  sincronizado con `8088193`.
- **Hoy:**
  - limpieza de Neon (H-14), con 3 605 fragmentos y 8 documentos verificados antes del `COMMIT`;
  - app en dos modos (ADR-038): en línea contra la API y sin conexión con el corpus local;
  - paleta y logo de la web; 45 pruebas de Flutter;
  - arnés de 248 consultas en el emulador: 0 FP.
- **Bloqueos:** sin acceso a Render, así que no hay `TOKEN_PRUEBAS` ni reinicio manual. Las consultas de
  prueba de la app cuentan como `usuario`; se limitaron a 6 y quedaron anotadas.

## James Saenz · 20/11/2026

- **Ayer:**
  - capturas del PMV3 (en línea, modo avión, selector, letra máxima, 429 real);
  - arreglos rápidos de la S14 (CSP del sitio estático, `npm audit` 0, ruff, Bandit y `npm audit` en
    la CI, corpus mínimo, H-09 y H-10);
  - logo en la web.
- **Hoy:**
  - métricas finales de ML (IC 95 %, τ en una muestra independiente, BM25 frente al híbrido);
  - latencia y energía con Qwen en GPU;
  - auditoría delta: se encontró y corrigió que el APK release no tenía permiso de INTERNET;
  - ingeniería inversa e insumos del informe, del artículo y del póster.
- **Bloqueos:**
  - el teléfono físico no estaba conectado para medir;
  - falta abrir los PR hacia el repositorio del equipo.
