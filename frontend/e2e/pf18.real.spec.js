// PF-18: consulta -> respuesta con documento y página -> aparece en el historial -> borrar historial.
import { expect, test } from "@playwright/test";

import { consultar } from "./ayudas.js";

test("PF-18 · consulta, trazabilidad, historial y borrado", async ({ page }) => {
  await page.goto("/");
  const consulta = "¿cómo se dice zorro en quechua wanka?";

  const respuesta = await consultar(page, consulta);
  expect(respuesta.status()).toBe(200);

  // Respuesta con documento y página (RN-02).
  await expect(page.getByRole("heading", { level: 2, name: "Respuesta" })).toBeVisible();
  await expect(page.locator(".respaldo__origen").first()).toContainText(/\.pdf — página \d+/);

  // Aparece en el historial.
  await expect(page.locator(".historial__item", { hasText: consulta }).first()).toBeVisible();

  // Borrar el historial (con confirmación).
  page.once("dialog", (dialogo) => dialogo.accept());
  await page.getByRole("button", { name: "Borrar historial" }).click();
  await expect(page.getByText("Todavía no hay consultas guardadas.")).toBeVisible();
  await expect(page.locator(".historial__item")).toHaveCount(0);
});
