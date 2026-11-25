// REF-08 (ADR-041): «¿Quiso escribir…?» tras una abstención; consulta de nuevo solo si se elige.
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import Respuesta from "./componentes/Respuesta";

const ABSTENCION = {
  consulta_id: undefined,
  texto: "No dispongo de respaldo documental para esa consulta en el corpus indexado.",
  abstenida: true,
  respaldo: [],
  aviso: "Consulta sobre fuentes publicadas.",
  similitud_maxima: 0.2,
  umbral: 0.48,
  latencia_ms: 9,
  sugerencias: [
    { termino: "zorro", consulta: "¿cómo se dice zorro en quechua wanka?" },
    { termino: "oro", consulta: "¿cómo se dice oro en quechua wanka?" },
  ],
};

afterEach(cleanup);

describe("REF-08 · ¿quiso escribir…?", () => {
  it("en una abstención propone los lemas y consulta la elegida", () => {
    const onConsultar = vi.fn();
    render(<Respuesta resultado={ABSTENCION} onConsultar={onConsultar} />);
    expect(screen.getByText("¿Quiso escribir…?")).toBeInTheDocument();
    expect(screen.getByText(/ni cambia formas en quechua/)).toBeInTheDocument();
    expect(onConsultar).not.toHaveBeenCalled(); // no corrige por su cuenta
    fireEvent.click(screen.getByRole("button", { name: "zorro" }));
    expect(onConsultar).toHaveBeenCalledWith("¿cómo se dice zorro en quechua wanka?");
  });

  it("la abstención se mantiene: sigue el mensaje de ausencia, sin forma ni fuente", () => {
    render(<Respuesta resultado={ABSTENCION} onConsultar={vi.fn()} />);
    expect(screen.getByText(ABSTENCION.texto)).toHaveClass("respuesta__ausencia");
    expect(screen.queryByText("Fuente consultada")).not.toBeInTheDocument();
  });

  it("sin sugerencias no muestra nada", () => {
    render(<Respuesta resultado={{ ...ABSTENCION, sugerencias: [] }} onConsultar={vi.fn()} />);
    expect(screen.queryByTestId("sugerencias")).not.toBeInTheDocument();
  });
});
