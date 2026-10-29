// Capturas automaticas de respaldo contra la URL PUBLICA de la nube (Guia 11, §3.9). No levanta
// ningun servidor local: URL_WEB es el static site de Render.
//   $env:URL_WEB="https://quechua-web.onrender.com"; npx playwright test -c playwright.nube.config.js
// Las capturas con la barra de direcciones visible las toma el usuario (docs/despliegue/PASOS_USUARIO.md).
import { defineConfig } from "@playwright/test";

const url = process.env.URL_WEB ?? "";
if (!/^https:\/\//.test(url)) {
  throw new Error("Defina URL_WEB con la URL https del frontend publicado (no localhost).");
}

export default defineConfig({
  testDir: "./e2e",
  testMatch: /capturas\.nube\.spec\.js/,
  workers: 1,
  // El plan gratuito de Render duerme tras 15 min: la primera carga puede tardar ~50 s.
  timeout: 180_000,
  expect: { timeout: 90_000 },
  reporter: [["list"]],
  use: {
    baseURL: url,
    viewport: { width: 1366, height: 900 },
    locale: "es-PE",
  },
});
