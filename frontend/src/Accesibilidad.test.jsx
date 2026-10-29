import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import GestionCorpus from "./componentes/GestionCorpus";
import GestionFuentes from "./componentes/GestionFuentes";
import TamanoTexto from "./componentes/TamanoTexto";

function fallar() {
  vi.stubGlobal(
    "fetch",
    vi.fn(() => Promise.resolve({ ok: false, status: 500, json: () => Promise.resolve({}) })),
  );
}

describe("accesibilidad de formularios", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("el error de Fuentes se anuncia y se asocia al formulario con aria-describedby", async () => {
    fallar();
    const { container } = render(<GestionFuentes />);
    const alerta = await screen.findByRole("alert");
    expect(alerta.id).toBe("error-fuentes");
    expect(container.querySelector("form").getAttribute("aria-describedby")).toBe("error-fuentes");
  });

  it("el error de Incorporar documentos se asocia igual", async () => {
    fallar();
    const { container } = render(<GestionCorpus />);
    const alerta = await screen.findByRole("alert");
    expect(container.querySelector("form").getAttribute("aria-describedby")).toBe(alerta.id);
  });

  it("sin error el formulario no apunta a nada", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve([]) })),
    );
    const { container } = render(<GestionFuentes />);
    await screen.findByText(/Todavía no hay fuentes/);
    expect(container.querySelector("form").hasAttribute("aria-describedby")).toBe(false);
  });

  it("el nombre accesible de los botones de tamaño contiene su texto visible", () => {
    render(<TamanoTexto indice={1} onCambiar={() => {}} />);
    for (const boton of screen.getAllByRole("button")) {
      const visible = boton.textContent.trim();
      expect(boton.getAttribute("aria-label").startsWith(visible)).toBe(true);
    }
  });
});
