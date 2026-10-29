import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import PanelPrediccion from "./componentes/PanelPrediccion";
import Respuesta from "./componentes/Respuesta";

const modelo = (clave) => ({
  clave,
  disponible: true,
  nombre: clave === "cobertura" ? "Predictor de cobertura documental" : "Predictor de relevancia",
  historia: "HU-08.1",
  requisito: "RF-14",
  algoritmo: "Regresion logistica",
  n_entrenamiento: 415,
  corte_operacion: 0.25,
  validacion_cruzada: {
    auc_roc: 0.9961,
    f1: 0.9635,
    precision: 0.9851,
    sensibilidad: 0.9429,
    especificidad: 0.9704,
    exactitud: 0.9518,
    matriz_confusion: { vp: 264, fp: 4, vn: 131, fn: 16 },
  },
  comparacion: { regresion_logistica: { auc_roc: 0.9961, f1: 0.9635, especificidad: 0.97 } },
  roc: { fpr: [0, 0.1, 1], tpr: [0, 0.9, 1] },
});

function json(cuerpo) {
  return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(cuerpo) });
}

function instalar() {
  globalThis.fetch = vi.fn((url) => {
    if (url.endsWith("/api/modelos")) return json([modelo("cobertura"), modelo("pasajes")]);
    if (url.includes("/api/analitica/demanda"))
      return json({
        suficiente: true,
        estadisticas: { total: 800, abstenidas: 186, respaldo_por_documento: { "dic.pdf": 606 } },
        terminos_distintos_no_cubiertos: 1,
        prioridades: [
          {
            termino: "criptomoneda",
            consultas: 1,
            probabilidad_cobertura_media: 0.0001,
            demanda_insatisfecha: 1,
            diagnostico: "ampliar el corpus",
          },
        ],
      });
    if (url.endsWith("/api/predicciones"))
      return json({
        texto: "zorro",
        caracteristicas: { similitud_maxima: 0.61 },
        cobertura: { probabilidad: 0.9995, corte: 0.25, decision: "con respaldo probable" },
        pasajes: { probabilidad: 0.03, corte: 0.5, decision: "retirar pasajes" },
      });
    return json({});
  });
}

describe("PMV2 · panel de predicción", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("muestra las métricas de los dos modelos y la demanda", async () => {
    instalar();
    render(<PanelPrediccion />);
    expect(await screen.findByTestId("modelo-cobertura")).toBeTruthy();
    expect(screen.getByTestId("modelo-pasajes")).toBeTruthy();
    expect(screen.getAllByText("0.996").length).toBeGreaterThan(0);
    expect(await screen.findByText("criptomoneda")).toBeTruthy();
  });

  it("predice al pulsar un ejemplo y muestra las dos probabilidades", async () => {
    instalar();
    render(<PanelPrediccion />);
    fireEvent.click(screen.getByText("¿cómo se dice zorro en quechua wanka?"));
    await waitFor(() => expect(screen.getByTestId("p-cobertura")).toBeTruthy());
    expect(screen.getByTestId("p-pasajes")).toBeTruthy();
    expect(screen.getByText("con respaldo probable")).toBeTruthy();
  });

  it("la respuesta muestra la predicción y avisa si el modelo forzó la abstención", () => {
    render(
      <Respuesta
        resultado={{
          consulta_id: "c",
          texto: "El modelo predictivo estima...",
          abstenida: true,
          idioma: "es",
          similitud_maxima: 0.5,
          aviso: "alcance",
          respaldo: [],
          pasajes: [],
          umbral: 0.48,
          latencia_ms: 10,
          lecturas_traduccion: [],
          probabilidad_cobertura: 0.1,
          abstencion_por_predictor: true,
        }}
      />,
    );
    expect(screen.getByTestId("prediccion-ml")).toBeTruthy();
    expect(screen.getByText(/RN-06/)).toBeTruthy();
  });
});
