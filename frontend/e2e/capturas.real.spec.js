// Capturas por historia con datos reales (copia de la base real). Corre en orden: las capturas del
// historial y de la analitica se toman antes de que PF-18 borre el historial.
import { readFileSync } from "node:fs";
import { join } from "node:path";

import { expect, test } from "@playwright/test";

import { capturar, consultar, CORPUS_PDF, pestana } from "./ayudas.js";

test.describe.configure({ mode: "serial" });

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText(/fragmentos indexados/)).toBeVisible();
});

test("HU-01 · registrar, editar y eliminar una fuente (CRUD)", async ({ page }) => {
  await pestana(page, "Fuentes del corpus").click();
  await page.getByLabel("Título", { exact: true }).fill("Fuente de prueba E2E");
  await page.getByLabel("Entidad publicadora").fill("Prueba local");
  await page.getByLabel("Licenciamiento").fill("Uso interno de prueba");
  await page.getByLabel("Nombre del archivo").fill("prueba-e2e.pdf");
  await page.getByLabel("Fecha de extracción").fill("2026-10-29");
  await page.getByLabel("Páginas totales").fill("10");
  await page.getByLabel("Páginas con texto").fill("9");
  await capturar(page, "HU-01_fuentes_formulario");
  await page.getByRole("button", { name: "Registrar fuente" }).click();
  const fila = page.locator("li.fuente", { hasText: "Fuente de prueba E2E" });
  await expect(fila).toBeVisible();

  await fila.getByRole("button", { name: "Editar" }).click();
  await page.getByLabel("Páginas con texto").fill("10");
  await page.getByRole("button", { name: "Guardar cambios" }).click();
  await expect(fila).toContainText("10/10 páginas con texto");
  await capturar(page, "HU-01_fuentes_lista_con_fuente_editada", fila);

  await fila.getByRole("button", { name: "Eliminar" }).click();
  await expect(fila).toHaveCount(0);
});

test("HU-03 y HU-07 · una palabra con documento y página", async ({ page }) => {
  const r = await consultar(page, "¿cómo se dice zorro en quechua wanka?");
  expect(r.status()).toBe(200);
  await expect(page.locator(".respaldo__origen").first()).toContainText(/\.pdf — página \d+/);
  await capturar(page, "HU-03_consulta_de_una_palabra");
  await capturar(
    page,
    "HU-07_documento_y_pagina_de_la_respuesta",
    page.locator(".respaldo__origen"),
  );
});

test("HU-04 · contenido cultural", async ({ page }) => {
  await consultar(page, "¿Qué relatos hablan del zorro?");
  await capturar(page, "HU-04_consulta_de_contenido_cultural");
});

test("HU-05 · consulta en inglés", async ({ page }) => {
  await consultar(page, "how do you say fox in Wanka Quechua?");
  await capturar(page, "HU-05_consulta_en_ingles_con_traduccion_de_la_consulta");
  await expect(page.locator(".respaldo__origen").first()).toContainText(/\.pdf — página \d+/);
  await capturar(page, "HU-05_documento_y_pagina_de_la_respuesta_en_ingles", page.locator(".respaldo__origen"));
});

test("HU-06 · sin respaldo no hay respuesta", async ({ page }) => {
  await consultar(page, "¿cómo se dice criptomoneda en quechua wanka?");
  await expect(
    page.getByRole("heading", { level: 2, name: /Sin respaldo|Sin respuesta/ }),
  ).toBeVisible();
  await capturar(page, "HU-06_abstencion_sin_respaldo_documental");
});

test("HU-08.1 · probabilidad de respaldo antes de generar", async ({ page }) => {
  await consultar(page, "¿cómo se dice zorro en quechua wanka?");
  await expect(page.getByTestId("prediccion-ml")).toBeVisible();
  await capturar(
    page,
    "HU-08.1_bloque_de_probabilidad_en_la_respuesta",
    page.getByTestId("prediccion-ml"),
  );
  await pestana(page, "Predicción ML").click();
  await expect(page.getByTestId("modelo-cobertura")).toBeVisible();
  await capturar(page, "HU-08.1_pestana_prediccion_ml");
});

test("RF-15 · pasajes con la segunda probabilidad", async ({ page }) => {
  // Pregunta propia de gramática (no pertenece a ningún conjunto de evaluación).
  await consultar(page, "¿Cómo se forma el plural en los sustantivos?");
  await expect(page.getByText(/no es una respuesta/).first()).toBeVisible();
  await capturar(page, "RF-15_pasajes_de_prosa_rotulados", page.getByText(/no es una respuesta/));
  await expect(page.locator(".pasajes__origen").first()).toContainText(/\.pdf — página \d+/);
  await capturar(page, "RF-15_pasaje_con_documento_y_pagina", page.locator(".pasajes__origen"));
  await capturar(page, "RF-15_probabilidad_de_los_pasajes", page.getByTestId("prediccion-ml"));
});

test("HU-09 · insuficiencia con la base real", async ({ page }) => {
  await pestana(page, "Predicción ML").click();
  await expect(page.getByTestId("demanda")).toContainText(/insuficiente/i);
  await capturar(page, "HU-09_insuficiencia_con_la_base_real", page.getByTestId("demanda"));
});

test("Historial · consultas guardadas (RF-11)", async ({ page }) => {
  await expect(page.locator(".historial__item").first()).toBeVisible();
  await capturar(page, "RF-11_historial_de_consultas", page.locator(".historial"));
});

test("Validación · consulta vacía y demasiado larga no llegan a la API", async ({ page }) => {
  let llamadas = 0;
  page.on("request", (r) => {
    if (r.url().endsWith("/api/consultas") && r.method() === "POST") llamadas += 1;
  });
  await page.locator("button.caja__boton").click();
  await expect(page.locator("#consulta-aviso")).not.toBeEmpty();
  await capturar(page, "validacion_consulta_vacia_en_la_interfaz");
  await page.getByLabel("Escriba su consulta en español o inglés").fill("a".repeat(301));
  await page.locator("button.caja__boton").click();
  await capturar(page, "validacion_consulta_demasiado_larga_en_la_interfaz");
  expect(llamadas).toBe(0);
});

test("Validación 422 y Swagger · la API rechaza una consulta inválida", async ({ page }) => {
  await page.goto("http://127.0.0.1:8000/docs");
  // La documentacion interactiva carga su interfaz desde un CDN: se espera a que pinte las operaciones.
  const cargo = await page
    .locator(".swagger-ui .opblock")
    .first()
    .waitFor({ timeout: 30_000 })
    .then(() => true)
    .catch(() => false);

  if (cargo) {
    await expect(page.getByText("LOADING", { exact: true })).toHaveCount(0);
    await capturar(page, "Swagger_documentacion_de_la_API");
    await page.locator("[id^='operations-'][id*='api_consultas_post']").first().click();
    await page.getByRole("button", { name: "Try it out" }).click();
    await page.locator("textarea.body-param__text").fill('{"texto": ""}');
    await page.getByRole("button", { name: "Execute" }).click();
    await expect(
      page.locator(".live-responses-table td.response-col_status:not(.col_header)").first(),
    ).toHaveText("422", { timeout: 30_000 });
    await capturar(
      page,
      "validacion_422_respuesta_de_la_API_en_Swagger",
      page.locator(".live-responses-table"),
    );
    return;
  }

  // Sin CDN: el esquema OpenAPI formateado hace de documentacion y el 422 se pide por la API.
  const esquema = await (await page.request.get("http://127.0.0.1:8000/openapi.json")).json();
  await page.setContent(
    `<pre style="font:14px monospace;padding:16px">${JSON.stringify(
      { info: esquema.info, rutas: Object.keys(esquema.paths) },
      null,
      2,
    )}</pre>`,
  );
  await capturar(page, "Swagger_documentacion_de_la_API");
  const r = await page.request.post("http://127.0.0.1:8000/api/consultas", { data: { texto: "" } });
  expect(r.status()).toBe(422);
  await page.setContent(`<pre style="font:14px monospace;padding:16px">422\n${await r.text()}</pre>`);
  await capturar(page, "validacion_422_respuesta_de_la_API_en_Swagger");
});

test("HU-02 · incorporar un PDF ya registrado en el corpus y reindexar", async ({ page }) => {
  // Se usa una COPIA RENOMBRADA de un PDF del corpus ya registrado en MANIFIESTO.yaml
  // (el diccionario de 37 paginas): el identificador de fragmento depende del nombre.
  const pdf = readFileSync(join(CORPUS_PDF, "293274822-diccionario-quechua-Wanka-docx.pdf"));
  await pestana(page, "Incorporar documentos").click();
  await page.locator('input[type="file"]').setInputFiles({
    name: "copia-e2e-hu02.pdf",
    mimeType: "application/pdf",
    buffer: pdf,
  });
  await page.getByLabel("Título", { exact: true }).fill("Copia de prueba E2E (PDF ya registrado)");
  await page.getByLabel("Entidad publicadora").fill("Prueba local");
  await page.getByLabel("Licenciamiento").fill("Uso interno de prueba");
  await page.getByRole("button", { name: "Incorporar al corpus" }).click();
  await expect(page.locator(".ingesta")).toContainText("incorporados");
  await capturar(page, "HU-02_incorporar_pdf_resultado", page.locator(".ingesta"));

  await page.getByRole("button", { name: "Reconstruir índice" }).click();
  await expect(page.getByText("copia-e2e-hu02.pdf")).toBeVisible();
  await capturar(
    page,
    "HU-02_documentos_indexados_tras_reindexar",
    page.getByText("copia-e2e-hu02.pdf"),
  );
});
