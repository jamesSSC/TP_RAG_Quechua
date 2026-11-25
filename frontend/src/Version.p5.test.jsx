// P5 (ronda 2): el pie muestra el commit desplegado de la API (/api/estado.version) y el de la web.
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const ESTADO = {
  fragmentos_indexados: 3605,
  documentos_corpus: 8,
  umbral_abstencion: 0.48,
  generador_disponible: true,
  base_datos_disponible: true,
  modelo: "gemini-3.5-flash-lite",
  escritura_protegida: true,
  entorno: "staging",
  motor_base_datos: "postgresql",
  origen_corpus: "postgres",
  generador: "gemini",
  predictores_disponibles: true,
};
const json = (c) => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(c) });
const simular = (estado) =>
  vi.stubGlobal("fetch", vi.fn((url) => (url.endsWith("/api/estado") ? json(estado) : json([]))));

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("P5 · versión desplegada en el pie", () => {
  it("en la nube muestra el commit de la API y el de la web", async () => {
    simular({ ...ESTADO, version: "4448478" });
    render(<App />);
    const version = await screen.findByTestId("pie-version");
    expect(version).toHaveTextContent("versión: API 4448478");
    expect(version).toHaveTextContent(/web local/); // en las pruebas no hay RENDER_GIT_COMMIT
  });

  it("en local muestra «local»", async () => {
    simular({ ...ESTADO, entorno: "local", escritura_protegida: false, version: "local" });
    render(<App />);
    expect(await screen.findByTestId("pie-version")).toHaveTextContent("versión: API local");
  });

  it("una API anterior sin el campo no rompe el pie", async () => {
    simular(ESTADO);
    render(<App />);
    expect(await screen.findByTestId("pie-version")).toHaveTextContent("API sin dato");
  });
});
