import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

// B11: logo del proyecto en el encabezado (a la izquierda del título) y como favicon.
describe("logo del proyecto", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("el encabezado muestra el logo con su texto alternativo, antes del título", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new TypeError("sin red en la prueba"))),
    );
    render(<App />);

    const logo = screen.getByRole("img", {
      name: "Logo del asistente de consulta del quechua wanka",
    });
    const titulo = screen.getByRole("heading", {
      level: 1,
      name: "Asistente de consulta del quechua wanka",
    });
    expect(logo).toBeInTheDocument();
    // El logo precede al título en el orden del documento.
    expect(logo.compareDocumentPosition(titulo) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(logo.closest("header")).toBe(titulo.closest("header"));
  });

  it("index.html declara el favicon SVG, los PNG y el apple-touch-icon", () => {
    const html = readFileSync(resolve(__dirname, "..", "index.html"), "utf8");
    expect(html).toContain('href="/favicon.svg"');
    expect(html).toContain('sizes="32x32" href="/favicon-32.png"');
    expect(html).toContain('sizes="192x192" href="/icono-192.png"');
    expect(html).toContain('sizes="512x512" href="/icono-512.png"');
    expect(html).toContain('rel="apple-touch-icon"');
  });
});
