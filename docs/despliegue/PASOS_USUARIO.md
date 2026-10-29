# Despliegue en la nube · pasos del usuario (Guía de laboratorio 11)

Estos pasos los hace **una persona del equipo en el navegador**: el agente no crea cuentas ni
inicia sesión. Los secretos (cadena de conexión de Neon, clave de Gemini, token de pruebas) se
pegan **solo** en los paneles de Neon y Render o en `backend\.env`, **nunca** en el chat ni en
Git.

**Capturas:** carpeta `capturas_nube`, nombre `U<n>_<descripcion>.png`, pantalla completa y
**con la barra de direcciones visible** (Windows: Win + Shift + S → Guardar). Antes de capturar
un panel con secretos, comprueba que los valores estén ocultos.

| # | Paso | Captura |
|---|---|---|
| U0 | Revisar y fusionar el PR `feat/despliegue-nube` con la CI en verde | PR fusionado y checks en verde |
| U1 | **Neon** (<https://console.neon.tech>): entrar con GitHub → *New project* `quechua-wanka`, región **AWS us-east-1** → *Connect* → activar **Connection pooling** → copiar la *connection string* | Panel de Neon con el proyecto y la base `neondb` |
| U2 | Pegar esa cadena **solo** en `backend\.env` como `DATABASE_URL=...` (no en el chat). Avisar al agente: «ya está en el .env» | — |
| U3 | **Render** (<https://dashboard.render.com>): entrar con GitHub → *New* → *Blueprint* → repositorio `omarpiero/TP_RAG_Quechua` → en `quechua-api` pegar `DATABASE_URL` (la misma cadena) → *Apply* | Blueprint con los 2 servicios y las variables (valores ocultos) |
| U3b | **Google AI Studio** (<https://aistudio.google.com/apikey>): entrar con una cuenta de Google → *Create API key* → pegarla **solo** en Render › `quechua-api` › *Environment* como `GEMINI_API_KEY` → *Save* | Panel de AI Studio con la clave creada (valor oculto) |
| U4 | Esperar al despliegue de los dos servicios | Logs de build del API con «Your service is live» y del static site |
| U5 | Copiar las dos URL públicas (`https://…onrender.com`) y pasárselas al agente. Si no son `quechua-api` / `quechua-web`, el agente actualiza `CORS_ORIGENES` y `VITE_API_URL`. Copiar también `TOKEN_PRUEBAS` (Render › `quechua-api` › *Environment*, lo generó el Blueprint) y pegarlo **solo** en la terminal cuando el agente lo pida como variable de entorno | — |
| U6 | **Neon › Tables**, después del *seeding* | Tablas `fragmentos` (conteo), `fuentes` y `consultas` |
| U7 | **Neon › SQL Editor:** `SELECT * FROM fn_resumen_demanda();` y `SELECT * FROM fn_fragmentos_por_documento();` y la lista de rutinas: `SELECT proname, prokind FROM pg_proc WHERE proname LIKE 'sp\_%' OR proname LIKE 'fn\_%';` | Resultado de cada consulta |
| U8 | En la URL pública del frontend, los casos de la matriz (§6 del encargo): zorro, *fox*, criptomoneda, sufijo, vacía, >300, historial, fuentes, incorporar PDF, predicción | Una captura por caso, con entrada, resultado y el pie «Entorno: staging · API: …» |
| U9 | Volver a **Neon › Tables › `consultas`** | Filas nuevas con fecha, idioma, vía y probabilidades |
| U10 | **Render › `quechua-api` › Logs** y **Metrics** | `POST /api/consultas 200` con latencia; memoria usada |
| U11 | **GitHub › Actions** y el árbol `backend/src` | CI en verde; carpetas `domain`, `application`, `adapters`, `infrastructure` |

## HU-02 · persistencia del PDF tras un redespliegue

1. En la interfaz pública, *Incorporar documentos* → subir un PDF pequeño de prueba.
2. Render › `quechua-api` › *Manual Deploy* → *Deploy latest commit*.
3. Al terminar, consultar un término del PDF: debe seguir respondiendo (los fragmentos están en
   Neon). El archivo PDF en sí **no** persiste: el disco de Render es efímero (limitación
   declarada).

## Al terminar en la PC compartida (obligatorio)

- Borrar `backend\.env`, `backend\data\fragmentos_v2.jsonl` y `backend\data\fragmentos_v3.jsonl`
  (el agente lo hace después de confirmar el *seeding*).
- Cerrar sesión en GitHub, Render, Neon y Google AI Studio en el navegador.
- Si Git guardó credenciales: Administrador de credenciales de Windows → *Credenciales de
  Windows* → borrar las de `git:https://github.com`.
