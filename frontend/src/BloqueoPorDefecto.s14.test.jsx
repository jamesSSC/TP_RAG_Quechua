// S14-01 (A04/A01): la gestión se bloquea por defecto y solo se desbloquea con confirmación
// explícita de la API (escritura_protegida === false) o con un token de administración validado.
// Antes, mientras /api/estado no respondía (arranque en frío de Render, ~1 min) o si fallaba, la
// web mostraba los formularios de gestión y pedía el historial del servidor.
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { fijarTokenAdmin } from "./api";
import App from "./App";

const ESTADO = {
  fragmentos_indexados: 3605,
  umbral_abstencion: 0.48,
  generador_disponible: true,
  base_datos_disponible: true,
  modelo: "gemini-3.5-flash-lite",
  entorno: "staging",
  generador: "extractivo",
};
const json = (c, s = 200) =>
  Promise.resolve({ ok: s < 400, status: s, json: () => Promise.resolve(c) });

// manejadorEstado decide qué pasa con /api/estado; el resto responde vacío.
function simularApi(manejadorEstado) {
  const falso = vi.fn((url) => {
    if (url.endsWith("/api/estado")) return manejadorEstado();
    return json([]);
  });
  vi.stubGlobal("fetch", falso);
  return falso;
}

const pedidasAlHistorial = (falso) =>
  falso.mock.calls.filter(([u]) => u.includes("/api/historial"));
const nav = () => within(document.querySelector("nav.pestanas"));
const irA = (pestana) => fireEvent.click(nav().getByRole("button", { name: pestana }));

afterEach(() => {
  cleanup();
  fijarTokenAdmin("");
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  vi.resetModules();
});

describe("S14-01 · bloqueo por defecto de la gestión", () => {
  it("con /api/estado pendiente no hay gestión, ni borrar todo, ni se pide /api/historial", async () => {
    const falso = simularApi(() => new Promise(() => {})); // nunca responde: arranque en frío
    render(<App />);

    irA("Fuentes del corpus");
    expect(screen.getByTestId("gestion-pendiente")).toHaveTextContent(
      /Conectando con el servicio… la gestión se habilita cuando la API confirma el modo/,
    );
    expect(screen.queryByText("Registrar nueva fuente")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Registrar fuente" })).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Token de administración")).not.toBeInTheDocument();

    irA("Incorporar documentos");
    expect(screen.getByTestId("gestion-pendiente")).toBeInTheDocument();
    expect(screen.queryByText("Corpus documental")).not.toBeInTheDocument();

    irA("Consultar");
    expect(screen.queryByRole("button", { name: "Borrar historial" })).not.toBeInTheDocument();
    expect(pedidasAlHistorial(falso)).toHaveLength(0);
  });

  it("si /api/estado falla queda todo bloqueado, con mensaje y Reintentar", async () => {
    let intento = 0;
    const falso = simularApi(() => {
      intento += 1;
      return intento === 1
        ? Promise.reject(new TypeError("Failed to fetch"))
        : json({ ...ESTADO, escritura_protegida: true });
    });
    render(<App />);

    irA("Fuentes del corpus");
    const bloqueo = await screen.findByText(
      "No se pudo confirmar el modo del servicio; la gestión queda bloqueada.",
    );
    expect(bloqueo).toBeInTheDocument();
    expect(screen.queryByText("Registrar nueva fuente")).not.toBeInTheDocument();
    expect(pedidasAlHistorial(falso)).toHaveLength(0);

    // Reintentar vuelve a pedir el estado; esta vez la API confirma el modo protegido.
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Reintentar" }));
    });
    expect(await screen.findByTestId("solo-lectura")).toHaveTextContent("Modo solo lectura");
    expect(falso.mock.calls.filter(([u]) => u.endsWith("/api/estado"))).toHaveLength(2);
    expect(pedidasAlHistorial(falso)).toHaveLength(0);
  });

  it("con escritura_protegida: true queda bloqueado y con un token válido se desbloquea", async () => {
    const falso = simularApi(() => json({ ...ESTADO, escritura_protegida: true }));
    render(<App />);
    await screen.findByText("Estado del sistema");

    irA("Fuentes del corpus");
    expect(screen.getByTestId("solo-lectura")).toBeInTheDocument();
    expect(screen.queryByText("Registrar nueva fuente")).not.toBeInTheDocument();
    expect(pedidasAlHistorial(falso)).toHaveLength(0);

    fireEvent.change(screen.getByLabelText("Token de administración"), {
      target: { value: "token-de-prueba" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Acceder" }));
    expect(await screen.findByText("Registrar nueva fuente")).toBeInTheDocument();
  });

  it("en local (escritura_protegida: false) la gestión se habilita como antes", async () => {
    const falso = simularApi(() => json({ ...ESTADO, entorno: "local", escritura_protegida: false }));
    render(<App />);
    await screen.findByText("Estado del sistema");
    expect(falso.mock.calls.some(([u]) => u.endsWith("/api/historial"))).toBe(true);

    irA("Fuentes del corpus");
    expect(screen.getByText("Registrar nueva fuente")).toBeInTheDocument();
    expect(screen.queryByTestId("gestion-pendiente")).not.toBeInTheDocument();
    expect(screen.queryByTestId("solo-lectura")).not.toBeInTheDocument();
  });

  it("una respuesta sin el campo escritura_protegida no desbloquea (solo vale false explícito)", async () => {
    simularApi(() => json({ ...ESTADO }));
    render(<App />);
    await screen.findByText("Estado del sistema");
    irA("Incorporar documentos");
    expect(screen.getByTestId("solo-lectura")).toBeInTheDocument();
    expect(screen.queryByText("Corpus documental")).not.toBeInTheDocument();
  });
});
