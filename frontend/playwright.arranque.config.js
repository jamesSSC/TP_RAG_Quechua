// S14-01 · evidencia de antes/después del bloqueo por defecto durante el arranque en frío.
// Compila la web como si fuera la de la nube (VITE_API_URL remota) y la sirve con `vite preview`.
// La API no existe: la prueba intercepta cada /api/* con page.route y retrasa /api/estado 20 s
// para simular el arranque en frío de Render, o lo hace fallar.
//   $env:FASE="antes"   ; npx playwright test -c playwright.arranque.config.js
//   $env:FASE="despues" ; npx playwright test -c playwright.arranque.config.js
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig } from "@playwright/test";

const aqui = dirname(fileURLToPath(import.meta.url));
const salidaBuild = join(aqui, "e2e", ".tmp", "dist-arranque");
const PUERTO = 4179;

export default defineConfig({
  testDir: "./e2e",
  testMatch: /arranque-bloqueo\.spec\.js/,
  outputDir: join(aqui, "e2e", ".tmp", "resultados-arranque"),
  workers: 1,
  timeout: 90_000,
  reporter: [["list"]],
  use: {
    baseURL: `http://127.0.0.1:${PUERTO}`,
    viewport: { width: 1366, height: 768 },
    locale: "es-PE",
  },
  webServer: {
    command:
      `npx vite build --outDir "${salidaBuild}" --emptyOutDir && ` +
      `npx vite preview --outDir "${salidaBuild}" --host 127.0.0.1 --port ${PUERTO} --strictPort`,
    cwd: aqui,
    url: `http://127.0.0.1:${PUERTO}`,
    timeout: 120_000,
    reuseExistingServer: false,
    // Dominio reservado (.invalid): nunca resuelve, todo pasa por page.route.
    env: { VITE_API_URL: "https://api-simulada.invalid" },
  },
});
