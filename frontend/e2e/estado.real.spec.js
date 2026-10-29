// B14: la pantalla de estado inicial muestra Ollama, modelo, corpus y base.
import { expect, test } from "@playwright/test";

import { capturar } from "./ayudas.js";

test("Estado inicial · todo disponible", async ({ page }) => {
  await page.goto("/");
  const estado = page.getByTestId("estado-inicial");
  await expect(estado).toBeVisible();
  await expect(page.getByTestId("estado-ollama")).toContainText("responde");
  await expect(page.getByTestId("estado-modelo")).toContainText("qwen3.5:4b");
  await expect(page.getByTestId("estado-corpus")).toContainText("fragmentos en el corpus");
  await expect(page.getByTestId("estado-base")).toContainText("conectada");
  await expect(page.getByTestId("aviso-sin-ollama")).toHaveCount(0);
  await capturar(page, "B14_estado_inicial_todo_disponible");
});
