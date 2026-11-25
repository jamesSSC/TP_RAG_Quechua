// S13 · fase 1 (FURPS+): aviso de arranque en frio (M-01, REF-02, ADR-033), mensajes propios de
// la version web (M-03) y pestana activa anunciada (M-07).
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const ESTADO = {
  fragmentos_indexados: 3605,
  umbral_abstencion: 0.48,
  generador_disponible: true,
  base_datos_disponible: true,
  modelo: "qwen3.5:4b",
  escritura_protegida: false,
};

const json = (cuerpo, estado = 200) =>
  Promise.resolve({ ok: estado < 400, status: estado, json: () => Promise.resolve(cuerpo) });

function instalarFetch(manejadorEstado) {
  const falso = vi.fn((url) => {
    if (url.endsWith("/api/estado")) return manejadorEstado();
    if (url.endsWith("/api/historial")) return json([]);
    return json({});
  });
  vi.stubGlobal("fetch", falso);
  return falso;
}

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
  vi.resetModules();
});

describe("aviso de arranque en frío (REF-02)", () => {
  it("aparece si /api/estado tarda más de 4 s y no antes", async () => {
    vi.useFakeTimers();
    instalarFetch(() => new Promise(() => {})); // la API no responde todavía
    render(<App />);
    expect(screen.getByTestId("estado-conectando")).toBeInTheDocument();

    await act(async () => vi.advanceTimersByTime(3900));
    expect(screen.queryByTestId("aviso-arranque")).not.toBeInTheDocument();

    await act(async () => vi.advanceTimersByTime(200));
    const aviso = screen.getByTestId("aviso-arranque");
    expect(aviso).toHaveTextContent(/tardando más de lo habitual/); // API local en Vitest
    expect(aviso.tagName).toBe("OUTPUT"); // role="status" implícito: lo anuncia el lector
  });

  it("no aparece si el servicio responde enseguida", async () => {
    vi.useFakeTimers();
    instalarFetch(() => json(ESTADO));
    render(<App />);
    await act(async () => vi.advanceTimersByTime(5000));
    expect(screen.queryByTestId("aviso-arranque")).not.toBeInTheDocument();
    expect(screen.getByTestId("estado-inicial")).toHaveTextContent("Estado del sistema");
  });

  it("desaparece en cuanto el servicio responde", async () => {
    vi.useFakeTimers();
    let responder;
    instalarFetch(() => new Promise((r) => (responder = r)));
    render(<App />);
    await act(async () => vi.advanceTimersByTime(4100));
    expect(screen.getByTestId("aviso-arranque")).toBeInTheDocument();
    await act(async () => responder({ ok: true, status: 200, json: () => Promise.resolve(ESTADO) }));
    expect(screen.queryByTestId("aviso-arranque")).not.toBeInTheDocument();
  });
});

describe("estado sin servicio", () => {
  it("ofrece Reintentar y vuelve a pedir el estado", async () => {
    let intento = 0;
    const falso = instalarFetch(() => {
      intento += 1;
      return intento === 1 ? Promise.reject(new TypeError("Failed to fetch")) : json(ESTADO);
    });
    render(<App />);
    expect(await screen.findByTestId("estado-sin-servicio")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Reintentar conexión" }));
    expect(await screen.findByText("Estado del sistema")).toBeInTheDocument();
    expect(falso.mock.calls.filter(([u]) => u.endsWith("/api/estado"))).toHaveLength(2);
  });
});

describe("mensajes de la versión web (M-03)", () => {
  it("con API remota, el error de red habla de la nube y no del servicio local", async () => {
    vi.stubEnv("VITE_API_URL", "https://api.ejemplo.test");
    vi.stubGlobal("fetch", vi.fn(() => Promise.reject(new TypeError("Failed to fetch"))));
    const api = await import("./api");
    expect(api.API_REMOTA).toBe(true);
    await expect(api.obtenerEstado()).rejects.toThrow(/servicio en la nube/);
    await expect(api.obtenerEstado()).rejects.not.toThrow(/servicio local/);
  });

  it("en local se conserva el mensaje de escritorio", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.reject(new TypeError("Failed to fetch"))));
    const api = await import("./api");
    expect(api.API_REMOTA).toBe(false);
    await expect(api.obtenerEstado()).rejects.toThrow(/servicio local/);
  });

  it("un 422 con detalle de texto muestra ese detalle", async () => {
    vi.stubGlobal("fetch", vi.fn(() => json({ detail: "El licenciamiento es obligatorio" }, 422)));
    const api = await import("./api");
    await expect(api.listarFuentes()).rejects.toThrow("El licenciamiento es obligatorio");
  });

  it("un 422 de validación de la consulta conserva el mensaje de 1 a 300 caracteres", async () => {
    vi.stubGlobal("fetch", vi.fn(() => json({ detail: [{ loc: ["body", "texto"] }] }, 422)));
    const api = await import("./api");
    await expect(api.consultar("")).rejects.toThrow(/entre 1 y 300 caracteres/);
  });
});

describe("pestañas (M-07)", () => {
  it("la pestaña activa se anuncia con aria-current", async () => {
    instalarFetch(() => json(ESTADO));
    render(<App />);
    const nav = within(document.querySelector("nav.pestanas"));
    const consultar = nav.getByRole("button", { name: "Consultar" });
    expect(consultar).toHaveAttribute("aria-current", "page");
    fireEvent.click(nav.getByRole("button", { name: "Predicción ML" }));
    expect(consultar).not.toHaveAttribute("aria-current");
    expect(nav.getByRole("button", { name: "Predicción ML" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });
});
