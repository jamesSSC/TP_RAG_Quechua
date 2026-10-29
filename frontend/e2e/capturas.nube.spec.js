// Capturas de respaldo de la matriz §6 contra la nube. Salida:
// docs/evidencias/nube/capturas_agente/<n>_<caso>.png (pagina completa, con el pie de entorno).
import { mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

const aqui = dirname(fileURLToPath(import.meta.url));
const salida = resolve(aqui, "..", "..", "docs", "evidencias", "nube", "capturas_agente");
mkdirSync(salida, { recursive: true });

const CONSULTAS = [
  ["01_HU-03_zorro", "¿cómo se dice zorro en quechua wanka?"],
  ["02_HU-05_fox", "how do you say fox in Wanka Quechua?"],
  ["03_HU-06_criptomoneda", "¿cómo se dice criptomoneda en quechua wanka?"],
  ["04_HU-04_sufijo", "¿Qué sufijo se usa para marcar localización espacial o temporal?"],
];

async function abrir(page) {
  await page.goto("/");
  await expect(page.getByTestId("pie-entorno")).toBeVisible();
}

test("00 estado inicial con pie de entorno", async ({ page }) => {
  await abrir(page);
  await page.screenshot({ path: join(salida, "00_estado_staging.png"), fullPage: true });
});

for (const [nombre, texto] of CONSULTAS) {
  test(nombre, async ({ page }) => {
    await abrir(page);
    await page.getByLabel(/Escriba su consulta/).fill(texto);
    await page.getByLabel(/Escriba su consulta/).press("Enter");
    await expect(page.locator(".respuesta")).toBeVisible();
    await page.screenshot({ path: join(salida, `${nombre}.png`), fullPage: true });
  });
}

test("05 validacion consulta larga", async ({ page }) => {
  await abrir(page);
  await page.getByLabel(/Escriba su consulta/).fill("a".repeat(301));
  await page.getByLabel(/Escriba su consulta/).press("Enter");
  await page.screenshot({ path: join(salida, "05_validacion_301.png"), fullPage: true });
});

for (const [nombre, pestana] of [
  ["06_PMV2_prediccion", "Predicción ML"],
  ["07_HU-01_fuentes", "Fuentes del corpus"],
  ["08_HU-02_incorporar", "Incorporar documentos"],
]) {
  test(nombre, async ({ page }) => {
    await abrir(page);
    await page.getByRole("button", { name: pestana }).click();
    await page.waitForLoadState("networkidle");
    await page.screenshot({ path: join(salida, `${nombre}.png`), fullPage: true });
  });
}
