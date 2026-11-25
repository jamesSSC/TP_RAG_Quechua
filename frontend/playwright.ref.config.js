// Ronda 2 (P8) · evidencias de antes y después de REF-05, REF-07 y REF-08 contra la API LOCAL real
// (no se toca la nube). Requiere la API levantada aparte en 127.0.0.1:8010:
//   cd backend; .venv\Scripts\python -m uvicorn infrastructure.main:app --app-dir src --port 8010
//   $env:FASE="antes"; npx playwright test -c playwright.ref.config.js -g REF-05
import { defineConfig } from "@playwright/test";

const PUERTO = 5190;

export default defineConfig({
  testDir: "./e2e",
  testMatch: /ref\.evidencias\.spec\.js/,
  workers: 1,
  timeout: 120_000,
  expect: { timeout: 60_000 },
  reporter: [["list"]],
  use: { baseURL: `http://127.0.0.1:${PUERTO}`, viewport: { width: 1366, height: 900 }, locale: "es-PE" },
  webServer: {
    command: `npm run dev -- --host 127.0.0.1 --port ${PUERTO} --strictPort`,
    url: `http://127.0.0.1:${PUERTO}`,
    timeout: 60_000,
    reuseExistingServer: false,
    env: { VITE_PROXY: "http://127.0.0.1:8010" },
  },
});
