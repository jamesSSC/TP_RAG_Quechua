// La interfaz que sirve el propio backend (con su CSP sin 'unsafe-inline') no provoca violaciones.
// Se prueba contra backend/interfaz (build de Vite), no contra el servidor de desarrollo.
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

const interfaz = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "backend", "interfaz", "index.html");

test("CSP · la interfaz servida por el backend no viola su política", async ({ page }) => {
  test.skip(!existsSync(interfaz), "backend/interfaz no existe: ejecute npm run build y copie dist");

  const violaciones = [];
  const consola = [];
  await page.addInitScript(() => {
    window.__violacionesCSP = [];
    document.addEventListener("securitypolicyviolation", (e) =>
      window.__violacionesCSP.push(`${e.violatedDirective} ${e.blockedURI}`),
    );
  });
  page.on("console", (m) => {
    if (/content security policy|refused to/i.test(m.text())) consola.push(m.text());
  });

  const respuesta = await page.goto("http://127.0.0.1:8000/");
  const csp = respuesta.headers()["content-security-policy"] ?? "";
  expect(csp).toContain("style-src 'self';");
  expect(csp).not.toContain("unsafe-inline");

  // Recorre la interfaz, incluidas las barras y medidores que usan `style` por CSSOM.
  await expect(page.getByText(/fragmentos indexados/)).toBeVisible();
  await page.getByLabel("Escriba su consulta en español o inglés").fill("¿cómo se dice zorro en quechua wanka?");
  await page.locator("button.caja__boton").click();
  await expect(page.locator(".respaldo__origen").first()).toBeVisible();
  await page.getByRole("button", { name: "Predicción ML", exact: true }).click();
  await expect(page.getByTestId("modelo-cobertura")).toBeVisible();
  await page.getByRole("button", { name: "Fuentes del corpus", exact: true }).click();
  await page.getByRole("button", { name: "Incorporar documentos", exact: true }).click();

  violaciones.push(...(await page.evaluate(() => window.__violacionesCSP)));
  expect(violaciones, "eventos securitypolicyviolation").toEqual([]);
  expect(consola, "mensajes de CSP en la consola").toEqual([]);
});
