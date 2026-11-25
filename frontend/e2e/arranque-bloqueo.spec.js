// S14-01 · la gestión no debe verse desbloqueada mientras la nube arranca ni si /api/estado falla.
// Salida: docs_auditoria/evidencias/<FASE>/S14-01_<FASE>_*.png. Ver playwright.arranque.config.js.
import { mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

const FASE = process.env.FASE === "antes" ? "antes" : "despues";
const aqui = dirname(fileURLToPath(import.meta.url));
const salida = resolve(aqui, "..", "..", "docs_auditoria", "evidencias", FASE);
mkdirSync(salida, { recursive: true });

const ESTADO_NUBE = {
  fragmentos_indexados: 3605,
  documentos_corpus: 8,
  umbral_abstencion: 0.48,
  generador_disponible: true,
  base_datos_disponible: true,
  modelo: "gemini-3.5-flash-lite",
  entorno: "staging",
  generador: "gemini",
  motor_base_datos: "postgresql",
  origen_corpus: "artefacto",
  predictores_disponibles: true,
  escritura_protegida: true,
};
const RETRASO_ESTADO_MS = 20_000;

// Simula la API: /api/estado según el caso; el resto responde vacío y anota lo que se pidió.
async function simularApi(page, { estado }) {
  const pedidas = [];
  await page.route("**/api/**", async (ruta) => {
    const url = ruta.request().url();
    pedidas.push(url);
    if (url.endsWith("/api/estado")) {
      if (estado === "falla") return ruta.abort("connectionrefused");
      await new Promise((r) => setTimeout(r, RETRASO_ESTADO_MS));
      return ruta.fulfill({ json: ESTADO_NUBE }).catch(() => {});
    }
    return ruta.fulfill({ json: [] });
  });
  return pedidas;
}

const captura = (page, nombre) =>
  page.screenshot({ path: join(salida, `S14-01_${FASE}_${nombre}.png`), fullPage: true });

test("arranque en frío: la gestión no aparece mientras /api/estado no responde", async ({ page }) => {
  const pedidas = await simularApi(page, { estado: "lento" });
  await page.goto("/");
  await page.getByRole("button", { name: "Fuentes del corpus" }).click();
  await page.waitForTimeout(1500);
  await captura(
    page,
    FASE === "antes" ? "gestion_desbloqueada_en_arranque" : "gestion_bloqueada_en_arranque",
  );
  if (FASE === "despues") {
    await expect(page.getByTestId("gestion-pendiente")).toContainText("Conectando con el servicio");
    await expect(page.getByText("Registrar nueva fuente")).toHaveCount(0);
    await page.getByRole("button", { name: "Incorporar documentos" }).click();
    await expect(page.getByTestId("gestion-pendiente")).toBeVisible();
    expect(pedidas.some((u) => u.includes("/api/historial"))).toBe(false);
  }
});

test("/api/estado falla: la gestión queda bloqueada y se puede reintentar", async ({ page }) => {
  await simularApi(page, { estado: "falla" });
  await page.goto("/");
  await page.getByRole("button", { name: "Fuentes del corpus" }).click();
  await page.waitForTimeout(1500);
  await captura(
    page,
    FASE === "antes" ? "estado_fallido_desbloqueado" : "estado_fallido_bloqueado",
  );
  if (FASE === "despues") {
    await expect(page.getByTestId("gestion-pendiente")).toContainText("No se pudo confirmar");
    await expect(page.getByRole("button", { name: "Reintentar" })).toBeVisible();
    await expect(page.getByText("Registrar nueva fuente")).toHaveCount(0);
  }
});
