// Pruebas E2E y capturas por historia (P0-B6). Levanta tres APIs locales (127.0.0.1) con bases
// aisladas y tres servidores Vite que apuntan a cada una:
//   real        8000 / 5173  copia de backend/quechua_wanka.db (la base real no se modifica)
//   demo        8001 / 5174  copia de backend/carga.db (consultas sinteticas, ver scripts/demo/02)
//   sin-ollama  8002 / 5175  base vacia y Ollama inalcanzable (caso C-10)
import { copyFileSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig } from "@playwright/test";

const aqui = dirname(fileURLToPath(import.meta.url));
const backend = resolve(aqui, "..", "backend");
const tmp = join(aqui, "e2e", ".tmp");
const python = process.env.QW_PYTHON ?? join(backend, ".venv", "Scripts", "python.exe");

// Bases y carpetas de datos temporales: cada corrida parte de cero y nunca toca las reales.
// Este archivo se carga tambien en cada worker: la preparacion se hace una sola vez.
const dbReal = join(backend, "quechua_wanka.db");
const dbCarga = join(backend, "carga.db");
if (!process.env.QW_E2E_PREPARADO) {
  rmSync(tmp, { recursive: true, force: true });
  mkdirSync(tmp, { recursive: true });
  if (existsSync(dbReal)) copyFileSync(dbReal, join(tmp, "real.db"));
  if (!existsSync(dbCarga)) {
    throw new Error("Falta backend/carga.db: genérela con scripts/demo/02_carga_sqlite.ps1");
  }
  copyFileSync(dbCarga, join(tmp, "carga.db"));
  process.env.QW_E2E_PREPARADO = "1";
}

const api = (puerto, base, extra = {}) => ({
  command: `"${python}" -m uvicorn infrastructure.main:app --app-dir src --host 127.0.0.1 --port ${puerto}`,
  cwd: backend,
  url: `http://127.0.0.1:${puerto}/api/estado`,
  timeout: 180_000,
  reuseExistingServer: false,
  env: {
    BASE_DATOS: "sqlite",
    RUTA_SQLITE: join(tmp, base),
    CARPETA_DATOS: join(tmp, `datos_${puerto}`),
    PYTHONIOENCODING: "utf-8",
    ...extra,
  },
});
const web = (puerto, apiPuerto) => ({
  command: `npm run dev -- --host 127.0.0.1 --port ${puerto} --strictPort`,
  cwd: aqui,
  url: `http://127.0.0.1:${puerto}`,
  timeout: 60_000,
  reuseExistingServer: false,
  env: { VITE_PROXY: `http://127.0.0.1:${apiPuerto}` },
});

export default defineConfig({
  testDir: "./e2e",
  outputDir: join(tmp, "resultados"),
  workers: 1,
  fullyParallel: false,
  timeout: 180_000,
  expect: { timeout: 60_000 },
  reporter: [["list"]],
  use: { viewport: { width: 1366, height: 768 }, locale: "es-PE", trace: "off" },
  projects: [
    { name: "real", testMatch: /real\.spec\.js/, use: { baseURL: "http://127.0.0.1:5173" } },
    { name: "demo", testMatch: /demo\.spec\.js/, use: { baseURL: "http://127.0.0.1:5174" } },
    {
      name: "sin-ollama",
      testMatch: /sin-ollama\.spec\.js/,
      use: { baseURL: "http://127.0.0.1:5175" },
    },
  ],
  webServer: [
    api(8000, "real.db"),
    api(8001, "carga.db"),
    // Puerto 9 (descartar): nadie escucha, Ollama queda inalcanzable.
    api(8002, "vacia.db", { OLLAMA_URL: "http://127.0.0.1:9" }),
    web(5173, 8000),
    web(5174, 8001),
    web(5175, 8002),
  ],
});
