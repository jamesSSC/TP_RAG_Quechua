// C-10: con Ollama inalcanzable (OLLAMA_URL hacia un puerto muerto) el sistema responde con el
// fragmento literal y un aviso; nunca un 500 ni una pantalla en blanco.
import { expect, test } from "@playwright/test";

import { capturar, consultar } from "./ayudas.js";

test("C-10 · Ollama detenido: fragmento literal con aviso, sin error 500", async ({ page }) => {
  await page.goto("/");
  // Pantalla de estado inicial (B14): avisa que Ollama no responde y que se usara el fragmento literal.
  await expect(page.getByTestId("aviso-sin-ollama")).toContainText("fragmento literal");
  await capturar(page, "B14_estado_inicial_sin_ollama_con_aviso");
  const respuesta = await consultar(page, "¿cómo se dice zorro en quechua wanka?");
  expect(respuesta.status()).toBe(200);
  await expect(page.locator(".respaldo__origen").first()).toContainText(/\.pdf — página \d+/);
  await expect(page.locator(".respuesta__aviso-generacion")).toBeVisible();
  await capturar(page, "C-10_ollama_detenido_fragmento_literal_con_aviso");
});
