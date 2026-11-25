// Ronda 2 (P8) · capturas de antes y después contra la API local real. Salida:
// docs_entrega_final/calidad/evidencias_ref/<FASE>/REF-0x_<FASE>_*.png
import { mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

const FASE = process.env.FASE === "antes" ? "antes" : "despues";
const aqui = dirname(fileURLToPath(import.meta.url));
const salida = resolve(aqui, "..", "..", "docs_entrega_final", "calidad", "evidencias_ref", FASE);
mkdirSync(salida, { recursive: true });
const ruta = (nombre) => join(salida, `${nombre.replace("FASE", FASE)}.png`);

test("REF-05 variables del modelo de cobertura", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Predicción ML" }).click();
  await page.getByText("¿cómo se dice zorro en quechua wanka?").click();
  const resultado = page.getByTestId("resultado-prediccion");
  await expect(page.getByTestId("p-cobertura")).toBeVisible();
  const resumen = resultado.locator("summary");
  if (await resumen.count()) await resumen.click(); // antes: la tabla estaba plegada
  await resultado.screenshot({ path: ruta("REF-05_FASE_variables_prediccion_web") });
});
