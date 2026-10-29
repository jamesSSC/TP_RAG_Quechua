import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import EstadoInicial from "./componentes/EstadoInicial";

const estado = {
  fragmentos_indexados: 3605,
  umbral_abstencion: 0.48,
  generador_disponible: true,
  base_datos_disponible: true,
  modelo: "qwen3.5:4b",
};

describe("pantalla de estado inicial", () => {
  afterEach(cleanup);

  it("muestra Ollama, modelo, corpus y base cuando todo esta disponible", () => {
    render(<EstadoInicial estado={estado} />);
    expect(screen.getByTestId("estado-ollama").textContent).toContain("responde");
    expect(screen.getByTestId("estado-modelo").textContent).toContain("qwen3.5:4b");
    expect(screen.getByTestId("estado-corpus").textContent).toMatch(/3[.,\s]?605 fragmentos/);
    expect(screen.getByTestId("estado-base").textContent).toContain("conectada");
    expect(screen.queryByTestId("aviso-sin-ollama")).toBeNull();
  });

  it("sin Ollama avisa y explica que se responde con el fragmento literal", () => {
    render(<EstadoInicial estado={{ ...estado, generador_disponible: false }} />);
    expect(screen.getByTestId("estado-ollama").textContent).toContain("no responde");
    const aviso = screen.getByTestId("aviso-sin-ollama");
    expect(aviso.textContent).toMatch(/fragmento literal/);
    expect(aviso.textContent).toContain("qwen3.5:4b");
  });

  it("sin base de datos lo dice", () => {
    render(<EstadoInicial estado={{ ...estado, base_datos_disponible: false }} />);
    expect(screen.getByTestId("estado-base").textContent).toMatch(/sin base/);
  });

  it("sin conexion con el servicio lo dice", () => {
    render(<EstadoInicial estado={null} />);
    expect(screen.getByTestId("estado-sin-servicio")).toBeTruthy();
  });
});
