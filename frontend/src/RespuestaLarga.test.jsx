import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import Respuesta from "./componentes/Respuesta";

const base = {
  consulta_id: "c",
  abstenida: false,
  idioma: "es",
  similitud_maxima: 0.6,
  aviso: "alcance",
  respaldo: [
    {
      fragmento_id: "f1",
      texto: "ZORRO: Atuq.",
      documento: "293274822-diccionario-quechua-Wanka-docx.pdf",
      pagina: 37,
      puntuacion: 0.61,
      similitud: 0.61,
      derivado_ocr: false,
    },
  ],
  pasajes: [],
  umbral: 0.48,
  latencia_ms: 10,
  lecturas_traduccion: [],
};

describe("respuestas largas", () => {
  afterEach(cleanup);

  it("se muestran completas, sin recortes, y con su documento y página", () => {
    const largo = Array.from({ length: 120 }, (_, i) => `frase${i}`).join(" ") + " FINAL";
    const { container } = render(<Respuesta resultado={{ ...base, texto: largo }} />);
    const parrafo = container.querySelector(".respuesta__texto");
    expect(parrafo.textContent).toBe(largo);
    expect(parrafo.textContent.endsWith("FINAL")).toBe(true);
    expect(screen.getByText(/página 37/)).toBeTruthy();
  });
});
