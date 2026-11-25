// REF-07 (ADR-040): «¿Le sirvió esta respuesta?» envía solo el id de la consulta y sí/no.
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import Respuesta from "./componentes/Respuesta";

const RESULTADO = {
  consulta_id: "11111111-2222-3333-4444-555555555555",
  texto: "En quechua wanka, «zorro» se dice Atuq.",
  abstenida: false,
  respaldo: [],
  aviso: "Consulta sobre fuentes publicadas.",
  similitud_maxima: 0.61,
  umbral: 0.48,
  latencia_ms: 12,
  via_respaldo: "similitud",
};
const responder = (status, cuerpo = {}) =>
  Promise.resolve({ ok: status < 400, status, json: () => Promise.resolve(cuerpo) });

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("REF-07 · ¿le sirvió esta respuesta?", () => {
  it("envía solo el id de la consulta y sí/no, y agradece", async () => {
    const falso = vi.fn(() => responder(201, { registrada: true }));
    vi.stubGlobal("fetch", falso);
    render(<Respuesta resultado={RESULTADO} />);
    fireEvent.click(screen.getByRole("button", { name: "No" }));
    expect(await screen.findByText(/Gracias: su valoración se registró/)).toBeInTheDocument();
    const [url, opciones] = falso.mock.calls[0];
    expect(url).toMatch(/\/api\/valoraciones$/);
    expect(JSON.parse(opciones.body)).toEqual({ consulta_id: RESULTADO.consulta_id, util: false });
    expect(screen.queryByRole("button", { name: "Sí" })).not.toBeInTheDocument();
  });

  it("si ya estaba valorada lo dice sin error", async () => {
    vi.stubGlobal("fetch", vi.fn(() => responder(409, { detail: "Esta respuesta ya fue valorada" })));
    render(<Respuesta resultado={RESULTADO} />);
    fireEvent.click(screen.getByRole("button", { name: "Sí" }));
    expect(await screen.findByText("Esta respuesta ya fue valorada.")).toBeInTheDocument();
  });

  it("si falla, avisa y deja volver a intentar; la respuesta no cambia", async () => {
    vi.stubGlobal("fetch", vi.fn(() => responder(503, { detail: "sin base" })));
    render(<Respuesta resultado={RESULTADO} />);
    fireEvent.click(screen.getByRole("button", { name: "Sí" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo registrar");
    expect(screen.getByRole("button", { name: "Sí" })).toBeEnabled();
    expect(screen.getByText(RESULTADO.texto)).toBeInTheDocument();
  });

  it("sin id de consulta no se ofrece", () => {
    render(<Respuesta resultado={{ ...RESULTADO, consulta_id: undefined }} />);
    expect(screen.queryByTestId("valoracion")).not.toBeInTheDocument();
  });
});
