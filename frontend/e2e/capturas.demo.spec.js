// HU-09 con la base de demostración (copia de backend/carga.db, consultas sintéticas rotuladas).
import { expect, test } from "@playwright/test";

import { capturar, pestana } from "./ayudas.js";

test("HU-09 · demostración rotulada con la base de carga", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("base-demostracion")).toBeVisible();
  await capturar(page, "HU-09_cabecera_avisa_base_de_demostracion");

  await pestana(page, "Predicción ML").click();
  const demanda = page.getByTestId("demanda");
  await expect(demanda).toContainText(/insuficiente/i); // por defecto: solo demanda real
  await capturar(page, "HU-09_por_defecto_no_cuenta_las_sinteticas", demanda);

  await page.getByLabel(/Ver demostración/).check();
  const aviso = page.getByTestId("aviso-demostracion");
  await expect(aviso).toContainText("no es demanda real");
  await expect(page.getByTestId("por-idioma")).toContainText("español");
  await expect(page.getByTestId("por-via")).toBeVisible();
  await capturar(page, "HU-09_demostracion_rotulada_con_la_base_de_carga", aviso);
  await capturar(
    page,
    "HU-09_demostracion_priorizacion",
    page.getByRole("table", { name: "Demanda insatisfecha" }),
  );
});
