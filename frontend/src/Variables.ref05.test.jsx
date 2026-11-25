// REF-05 (ronda 2): la web muestra, como la app, el valor de cada variable y su peso en el modelo
// de cobertura (coeficiente estandarizado de /api/modelos), ordenadas por la magnitud del peso.
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import PanelPrediccion from "./componentes/PanelPrediccion";

const json = (c) => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(c) });

const COEFICIENTES = {
  similitud_maxima: 1.0218,
  proporcion_fuera_vocabulario: -1.8264,
  coincidencia_lema: 1.5836,
};

function instalar({ conCoeficientes = true } = {}) {
  vi.stubGlobal(
    "fetch",
    vi.fn((url) => {
      if (url.endsWith("/api/modelos"))
        return json([
          {
            clave: "cobertura",
            disponible: false,
            ...(conCoeficientes ? { coeficientes: COEFICIENTES } : {}),
          },
          { clave: "pasajes", disponible: false },
        ]);
      if (url.endsWith("/api/predicciones"))
        return json({
          texto: "zorro",
          caracteristicas: {
            similitud_maxima: 0.6123,
            proporcion_fuera_vocabulario: 0,
            coincidencia_lema: 1,
          },
          cobertura: { probabilidad: 0.99, corte: 0.25, decision: "con respaldo probable" },
          pasajes: { probabilidad: 0.03, corte: 0.5, decision: "retirar pasajes" },
        });
      return json({ suficiente: false, estadisticas: {}, por_origen: {} });
    }),
  );
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("REF-05 · variables del modelo de cobertura en la web", () => {
  it("muestra valor y peso de cada variable, de mayor a menor peso, con su signo", async () => {
    instalar();
    render(<PanelPrediccion />);
    fireEvent.click(screen.getByText("¿cómo se dice zorro en quechua wanka?"));
    const tabla = await screen.findByTestId("tabla-variables");
    const filas = within(tabla).getAllByRole("row").slice(1);
    expect(filas.map((f) => within(f).getAllByRole("cell")[0].textContent)).toEqual([
      "Fuera de vocabulario",
      "Coincidencia de lema",
      "Similitud máxima",
    ]);
    expect(within(filas[0]).getByTestId("peso")).toHaveTextContent("−1,83");
    expect(within(filas[1]).getByTestId("peso")).toHaveTextContent("+1,58");
    expect(within(filas[2]).getAllByRole("cell")[1]).toHaveTextContent("0,612");
    expect(tabla).toHaveTextContent(/un peso positivo empuja hacia «hay respaldo»/);
  });

  it("sin coeficientes en /api/modelos muestra los valores y un guion en el peso", async () => {
    instalar({ conCoeficientes: false });
    render(<PanelPrediccion />);
    fireEvent.click(screen.getByText("¿cómo se dice zorro en quechua wanka?"));
    const tabla = await screen.findByTestId("tabla-variables");
    expect(within(tabla).queryAllByTestId("peso")).toHaveLength(0);
    expect(within(tabla).getAllByRole("row")).toHaveLength(4);
  });
});
