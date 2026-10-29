import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { fijarClaveGemini } from "./api";

const ESTADO_NUBE = {
  fragmentos_indexados: 3605,
  umbral_abstencion: 0.48,
  generador_disponible: true,
  base_datos_disponible: true,
  modelo: "gemini-flash",
  predictores_disponibles: true,
  consultas_por_origen: {},
  base_demostracion: false,
  entorno: "staging",
  motor_base_datos: "postgres",
  origen_corpus: "postgres",
  generador: "gemini",
  modelos_ml: { cobertura_hu08_1: true, pasajes_rf15: true },
  documentos_corpus: 8,
};

const RESPUESTA_ZORRO = {
  consulta_id: "c1",
  texto: "En quechua wanka, «ZORRO» se dice Atuq.",
  abstenida: false,
  idioma: "es",
  similitud_maxima: 0.6095,
  aviso: "Consulta sobre fuentes documentales publicadas.",
  respaldo: [
    {
      fragmento_id: "f1",
      texto: "ZORRO: Atuq.",
      documento: "diccionario.pdf",
      pagina: 37,
      puntuacion: 0.6095,
      similitud: 0.6095,
      derivado_ocr: false,
      coincidencia_lema: true,
    },
  ],
  pasajes: [],
  via_respaldo: "similitud",
  umbral: 0.48,
  latencia_ms: 12,
  lecturas_traduccion: [],
  generador_invocado: true,
  redactado_por: "gemini",
  motivo_redaccion: null,
};

function simularApi(estado) {
  const llamadas = [];
  globalThis.fetch = vi.fn(async (url, opciones = {}) => {
    llamadas.push({ url, opciones });
    const cuerpo = url.endsWith("/api/estado")
      ? estado
      : url.endsWith("/api/historial")
        ? []
        : url.endsWith("/api/consultas")
          ? RESPUESTA_ZORRO
          : {};
    return { ok: true, status: 200, json: async () => cuerpo };
  });
  return llamadas;
}

afterEach(() => {
  cleanup();
  fijarClaveGemini("");
  vi.restoreAllMocks();
});

describe("despliegue en la nube", () => {
  it("el pie muestra el entorno y la API, y el aviso de privacidad de Gemini", async () => {
    simularApi(ESTADO_NUBE);
    render(<App />);
    const pie = await screen.findByTestId("pie-entorno");
    expect(pie.textContent).toContain("Entorno: staging");
    expect(pie.textContent).toContain("API:");
    expect(pie.textContent).toContain("corpus postgres");
    expect(screen.getByTestId("aviso-privacidad").textContent).toContain("API de Google");
  });

  it("en local no aparece el pie de entorno ni el aviso", async () => {
    simularApi({ ...ESTADO_NUBE, entorno: "local", generador: "ollama" });
    render(<App />);
    await waitFor(() => expect(screen.queryByText(/fragmentos indexados/)).not.toBeNull());
    expect(screen.queryByTestId("pie-entorno")).toBeNull();
    expect(screen.queryByTestId("aviso-privacidad")).toBeNull();
  });

  it("la clave propia viaja en X-Gemini-Key y no se guarda en localStorage", async () => {
    const llamadas = simularApi(ESTADO_NUBE);
    const guardar = vi.spyOn(Storage.prototype, "setItem");
    render(<App />);
    await screen.findByTestId("pie-entorno");
    fireEvent.change(screen.getByLabelText("Usar mi propia clave de Gemini"), {
      target: { value: "clave-propia" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Usar esta clave" }));
    const entrada = screen.getByLabelText(/Escriba su consulta/);
    fireEvent.change(entrada, { target: { value: "zorro" } });
    fireEvent.submit(entrada.closest("form"));
    await waitFor(() =>
      expect(llamadas.some((l) => l.url.endsWith("/api/consultas"))).toBe(true),
    );
    const consulta = llamadas.find((l) => l.url.endsWith("/api/consultas"));
    expect(consulta.opciones.headers["X-Gemini-Key"]).toBe("clave-propia");
    expect(guardar.mock.calls.flat().join(" ")).not.toContain("clave-propia");
    expect((await screen.findByTestId("redactado-por")).textContent).toBe("Redactado por: Gemini");
  });
});

describe("textos de la nube", () => {
  it("no menciona Ollama ni 'este equipo' en staging", async () => {
    simularApi(ESTADO_NUBE);
    render(<App />);
    await screen.findByTestId("pie-entorno");
    expect(screen.getByTestId("estado-generador").textContent).toContain("Gemini configurado");
    expect(screen.queryByTestId("estado-ollama")).toBeNull();
    expect(screen.queryByTestId("aviso-sin-ollama")).toBeNull();
  });
});
