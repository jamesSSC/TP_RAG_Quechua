import { mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const aqui = dirname(fileURLToPath(import.meta.url));
export const CAPTURAS = resolve(aqui, "..", "..", "docs", "evidencias", "cierre_u3", "capturas");
export const CORPUS_PDF = resolve(aqui, "..", "..", "corpus", "pdf");
mkdirSync(CAPTURAS, { recursive: true });

// Captura del viewport (1366x768). Solo la página: no sale ninguna ruta ni dato del sistema.
export async function capturar(page, nombre, localizador) {
  if (localizador) await localizador.first().scrollIntoViewIfNeeded();
  await page.screenshot({ path: join(CAPTURAS, `${nombre}.png`) });
}

// Envia la consulta y espera a que la API responda y la interfaz termine de pintarla.
export async function consultar(page, texto) {
  await page.getByLabel("Escriba su consulta en español o inglés").fill(texto);
  const [respuesta] = await Promise.all([
    page.waitForResponse(
      (r) => r.url().endsWith("/api/consultas") && r.request().method() === "POST",
    ),
    page.locator("button.caja__boton").click(),
  ]);
  await page.locator("button.caja__boton").waitFor();
  return respuesta;
}

export const pestana = (page, nombre) => page.getByRole("button", { name: nombre, exact: true });
