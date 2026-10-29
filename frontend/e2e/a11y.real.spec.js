// Accesibilidad (WCAG 2 A/AA) con axe-core sobre las cuatro vistas, con backend y datos reales.
// Va primero (a < c): antes de los captures y de PF-18, que borra el historial.
// A11Y_FASE=antes solo registra; sin esa variable, 0 infracciones es obligatorio.
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import { consultar, pestana } from "./ayudas.js";

const SALIDA = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "docs", "evidencias", "cierre_u3", "b13_a11y");
const FASE = process.env.A11Y_FASE ?? "despues";
const ETIQUETAS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];
const resultado = {};

async function analizar(page, vista) {
  const r = await new AxeBuilder({ page }).withTags(ETIQUETAS).analyze();
  // Solo regla, impacto y selectores: ningun texto de la pagina.
  resultado[vista] = {
    infracciones: r.violations.length,
    nodos: r.violations.reduce((n, v) => n + v.nodes.length, 0),
    reglas: r.violations.map((v) => ({
      regla: v.id,
      impacto: v.impact,
      nodos: v.nodes.length,
      selectores: v.nodes.slice(0, 5).map((n) => n.target.join(" ")),
    })),
  };
  resultado[vista].objetivos_menores_44px = await objetivosPequenos(page);
  return r.violations;
}

// Objetivos tactiles: controles visibles de menos de 44 px de alto o de ancho (la casilla se mide por su etiqueta).
async function objetivosPequenos(page) {
  return page.evaluate(() => {
    const controles = [...document.querySelectorAll("button, select, input, a[href]")];
    const chicos = [];
    for (const el of controles) {
      const tipo = el.getAttribute("type");
      const medido = tipo === "checkbox" || tipo === "radio" ? (el.closest("label") ?? el) : el;
      const r = medido.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      if (r.width < 44 || r.height < 44) {
        chicos.push(`${el.tagName.toLowerCase()}.${el.className || "-"} ${Math.round(r.width)}x${Math.round(r.height)}`);
      }
    }
    return { cantidad: chicos.length, ejemplos: [...new Set(chicos)].slice(0, 8) };
  });
}

test.describe.configure({ mode: "serial" });

test("axe · Consultar con una respuesta", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText(/fragmentos indexados/)).toBeVisible();
  await consultar(page, "¿cómo se dice zorro en quechua wanka?");
  await expect(page.locator(".respaldo__origen").first()).toBeVisible();
  const v = await analizar(page, "consultar");
  if (FASE !== "antes") expect(v).toEqual([]);
  if (FASE !== "antes") expect(resultado.consultar.objetivos_menores_44px.cantidad).toBe(0);
});

test("axe · Fuentes del corpus", async ({ page }) => {
  await page.goto("/");
  await pestana(page, "Fuentes del corpus").click();
  await expect(page.getByLabel("Título", { exact: true })).toBeVisible();
  const v = await analizar(page, "fuentes");
  if (FASE !== "antes") expect(v).toEqual([]);
  if (FASE !== "antes") expect(resultado.fuentes.objetivos_menores_44px.cantidad).toBe(0);
});

test("axe · Incorporar documentos", async ({ page }) => {
  await page.goto("/");
  await pestana(page, "Incorporar documentos").click();
  await expect(page.getByRole("button", { name: "Incorporar al corpus" })).toBeVisible();
  const v = await analizar(page, "incorporar");
  if (FASE !== "antes") expect(v).toEqual([]);
  if (FASE !== "antes") expect(resultado.incorporar.objetivos_menores_44px.cantidad).toBe(0);
});

test("axe · Predicción ML", async ({ page }) => {
  await page.goto("/");
  await pestana(page, "Predicción ML").click();
  await expect(page.getByTestId("modelo-cobertura")).toBeVisible();
  await expect(page.getByTestId("demanda")).toBeVisible();
  const v = await analizar(page, "prediccion");
  if (FASE !== "antes") expect(v).toEqual([]);
  if (FASE !== "antes") expect(resultado.prediccion.objetivos_menores_44px.cantidad).toBe(0);
});

test.afterAll(() => {
  mkdirSync(SALIDA, { recursive: true });
  writeFileSync(join(SALIDA, `axe_${FASE}.json`), JSON.stringify(resultado, null, 2), "utf-8");
});
