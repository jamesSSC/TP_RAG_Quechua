import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import Respuesta from "./componentes/Respuesta";

const DOC = "293274822-diccionario-quechua-Wanka-docx.pdf";

const respaldoZorro = {
  fragmento_id: "35d5d6d6b8a4",
  texto: "ZORRO: Atuq.",
  documento: DOC,
  pagina: 37,
  puntuacion: 0.3,
  similitud: 0.3,
  derivado_ocr: false,
  coincidencia_lema: true,
  rotulo: null,
};

const respuestaBase = {
  consulta_id: "c1",
  texto: "ZORRO: Atuq.",
  abstenida: false,
  idioma: "es",
  similitud_maxima: 0.3,
  aviso: "Consulta sobre fuentes publicadas.",
  respaldo: [respaldoZorro],
  consulta_traducida: null,
  pasajes: [],
  via_respaldo: "lema",
  umbral: 0.48,
  latencia_ms: 1234.5,
  lecturas_traduccion: [],
  traduccion_usada: null,
  generador_invocado: true,
  aviso_generacion: null,
};

function json(cuerpo, estado = 200) {
  return Promise.resolve({
    ok: estado < 400,
    status: estado,
    json: () => Promise.resolve(cuerpo),
  });
}

function instalarFetch(manejadorConsulta, historial = []) {
  const falso = vi.fn((url, opciones = {}) => {
    const metodo = opciones.method ?? "GET";
    if (url.endsWith("/api/estado")) {
      return json({
        fragmentos_indexados: 3605,
        umbral_abstencion: 0.48,
        generador_disponible: true,
        base_datos_disponible: true,
        modelo: "qwen3.5:4b",
      });
    }
    if (url.endsWith("/api/historial") && metodo === "GET") return json(historial);
    if (url.endsWith("/api/historial") && metodo === "DELETE") {
      historial.length = 0;
      return Promise.resolve({ ok: true, status: 204, json: () => Promise.resolve(null) });
    }
    if (url.endsWith("/api/consultas")) return manejadorConsulta(opciones);
    return json({}, 404);
  });
  vi.stubGlobal("fetch", falso);
  return falso;
}

const llamadasAConsultas = (falso) =>
  falso.mock.calls.filter(([url]) => url.endsWith("/api/consultas"));

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("tamaño del texto", () => {
  it("A+, A− y Restablecer cambian el tamaño y los extremos se deshabilitan", async () => {
    instalarFetch(() => json(respuestaBase));
    const { container } = render(<App />);
    const raiz = () => container.querySelector(".aplicacion");
    const menos = screen.getByRole("button", { name: /reducir tamaño del texto/i });
    const mas = screen.getByRole("button", { name: /aumentar tamaño del texto/i });
    const reset = screen.getByRole("button", { name: /restablecer tamaño del texto/i });

    expect(raiz()).toHaveClass("aplicacion--normal");
    expect(reset).toBeDisabled();

    fireEvent.click(menos);
    expect(raiz()).toHaveClass("aplicacion--pequeno");
    expect(menos).toBeDisabled();

    fireEvent.click(mas);
    fireEvent.click(mas);
    fireEvent.click(mas);
    expect(raiz()).toHaveClass("aplicacion--mayor");
    expect(mas).toBeDisabled();
    expect(window.localStorage.getItem("tamano_texto")).toBe("mayor");

    fireEvent.click(reset);
    expect(raiz()).toHaveClass("aplicacion--normal");
    expect(window.localStorage.getItem("tamano_texto")).toBe("normal");
    await waitFor(() => expect(screen.getByText(/fragmentos indexados/)).toBeInTheDocument());
  });

  it("recupera la preferencia guardada y no falla si el almacenamiento está bloqueado", async () => {
    window.localStorage.setItem("tamano_texto", "grande");
    instalarFetch(() => json(respuestaBase));
    const { container, unmount } = render(<App />);
    expect(container.querySelector(".aplicacion")).toHaveClass("aplicacion--grande");
    unmount();

    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("bloqueado");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("bloqueado");
    });
    const otro = render(<App />);
    expect(otro.container.querySelector(".aplicacion")).toHaveClass("aplicacion--normal");
    fireEvent.click(screen.getByRole("button", { name: /aumentar tamaño del texto/i }));
    expect(otro.container.querySelector(".aplicacion")).toHaveClass("aplicacion--grande");
    await waitFor(() => expect(screen.getByText(/fragmentos indexados/)).toBeInTheDocument());
  });
});

describe("validación de la consulta", () => {
  it("una consulta vacía no llama a la API", async () => {
    const falso = instalarFetch(() => json(respuestaBase));
    render(<App />);
    fireEvent.submit(screen.getByLabelText(/Escriba su consulta/));
    expect(await screen.findByRole("alert")).toHaveTextContent(/Escribe una consulta/);
    expect(llamadasAConsultas(falso)).toHaveLength(0);
  });

  it("más de 300 caracteres no llama a la API y el contador lo muestra", async () => {
    const falso = instalarFetch(() => json(respuestaBase));
    render(<App />);
    const entrada = screen.getByLabelText(/Escriba su consulta/);
    fireEvent.change(entrada, { target: { value: "a".repeat(301) } });
    expect(screen.getByText("301 / 300 caracteres")).toBeInTheDocument();
    fireEvent.submit(entrada);
    expect(await screen.findByText(/supera los 300 caracteres/)).toBeInTheDocument();
    expect(llamadasAConsultas(falso)).toHaveLength(0);
  });

  it("una consulta válida se envía con Enter (submit del formulario)", async () => {
    const falso = instalarFetch(() => json(respuestaBase));
    render(<App />);
    const entrada = screen.getByLabelText(/Escriba su consulta/);
    fireEvent.change(entrada, { target: { value: "¿cómo se dice zorro en quechua wanka?" } });
    fireEvent.submit(entrada);
    expect(await screen.findByText(/Fuente consultada/)).toBeInTheDocument();
    expect(llamadasAConsultas(falso)).toHaveLength(1);
  });
});

describe("estados de la consulta", () => {
  it("muestra el error en español con Reintentar y reintenta", async () => {
    let intento = 0;
    const falso = instalarFetch(() => {
      intento += 1;
      return intento === 1 ? Promise.reject(new TypeError("Failed to fetch")) : json(respuestaBase);
    });
    render(<App />);
    fireEvent.change(screen.getByLabelText(/Escriba su consulta/), {
      target: { value: "zorro" },
    });
    fireEvent.click(document.querySelector(".caja__boton"));

    const alerta = await screen.findByText(/No se pudo conectar con el servicio local/);
    expect(alerta).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Reintentar" }));

    expect(await screen.findByText(/Fuente consultada/)).toBeInTheDocument();
    expect(llamadasAConsultas(falso)).toHaveLength(2);
    expect(screen.queryByRole("button", { name: "Reintentar" })).not.toBeInTheDocument();
  });

  it("deshabilita el botón y muestra «Consultando…» mientras espera", async () => {
    let resolver;
    instalarFetch(() => new Promise((r) => (resolver = r)));
    render(<App />);
    fireEvent.change(screen.getByLabelText(/Escriba su consulta/), { target: { value: "zorro" } });
    fireEvent.click(document.querySelector(".caja__boton"));
    const boton = await screen.findByRole("button", { name: /Consultando…/ });
    expect(boton).toBeDisabled();
    resolver({ ok: true, status: 200, json: () => Promise.resolve(respuestaBase) });
    await screen.findByText(/Fuente consultada/);
  });
});

describe("historial", () => {
  it("se recarga tras cada consulta, avisa de privacidad y se borra con confirmación", async () => {
    const historial = [
      {
        consulta: "zorro",
        respuesta: "x",
        abstenida: false,
        similitud_maxima: 0.6,
        via_respaldo: "similitud",
        momento: "2026-10-01T10:00:00",
      },
    ];
    const falso = instalarFetch(() => json(respuestaBase), historial);
    render(<App />);
    expect(await screen.findByText("zorro")).toBeInTheDocument();
    expect(screen.getByText(/No se guardan datos personales/)).toBeInTheDocument();

    vi.spyOn(window, "confirm").mockReturnValue(true);
    fireEvent.click(screen.getByRole("button", { name: "Borrar historial" }));
    await waitFor(() =>
      expect(
        falso.mock.calls.some(([u, o]) => u.endsWith("/api/historial") && o?.method === "DELETE"),
      ).toBe(true),
    );
    expect(await screen.findByText(/Todavía no hay consultas guardadas/)).toBeInTheDocument();
  });
});

describe("respuesta", () => {
  it("por vía de lema rotula «entrada exacta del diccionario» con la similitud bajo τ", () => {
    render(<Respuesta resultado={respuestaBase} />);
    expect(screen.getByTestId("via-respaldo")).toHaveTextContent(
      "Respaldo: entrada exacta del diccionario",
    );
    expect(screen.getByTestId("via-respaldo")).toHaveTextContent(/queda bajo τ = 0.48/);
    expect(screen.getByText("ZORRO: Atuq.", { selector: "blockquote" })).toBeInTheDocument();
    expect(screen.getByText(`${DOC} — página 37`)).toBeInTheDocument();
    expect(screen.getByTestId("latencia")).toHaveTextContent("Latencia: 1235 ms");
    expect(screen.getByTestId("marca-tau").style.left).toBe("48%");
  });

  it("por vía de similitud rotula «similitud ≥ τ»", () => {
    render(
      <Respuesta resultado={{ ...respuestaBase, via_respaldo: "similitud", similitud_maxima: 0.61 }} />,
    );
    expect(screen.getByTestId("via-respaldo")).toHaveTextContent("Respaldo: similitud ≥ τ");
  });

  it("muestra el aviso de generación cuando el redactor no estuvo disponible", () => {
    render(
      <Respuesta
        resultado={{
          ...respuestaBase,
          aviso_generacion: "El servicio de redacción no está disponible; se muestra el fragmento literal.",
        }}
      />,
    );
    expect(screen.getByRole("status")).toHaveTextContent(/servicio de redacción no está disponible/);
  });

  it("en una abstención con pasajes los rotula «no es una respuesta» y no destaca ninguna forma", () => {
    const abstencion = {
      ...respuestaBase,
      abstenida: true,
      texto: "No tengo una respuesta confirmada para esa consulta.",
      respaldo: [],
      via_respaldo: null,
      similitud_maxima: 0.2,
      pasajes: [
        {
          ...respaldoZorro,
          fragmento_id: "p1",
          texto: "Texto de prosa de ejemplo sobre la gramática.",
          pagina: 12,
          coincidencia_lema: false,
          rotulo: "no es una respuesta",
        },
      ],
    };
    const { container } = render(<Respuesta resultado={abstencion} />);
    expect(
      screen.getByRole("heading", { name: "Pasajes relacionados — no es una respuesta" }),
    ).toBeInTheDocument();
    expect(screen.getByText(`${DOC} — página 12`)).toBeInTheDocument();
    expect(container.querySelector("blockquote")).toBeNull();
    expect(screen.queryByText(/Fuente consultada/)).not.toBeInTheDocument();
    expect(screen.queryByTestId("via-respaldo")).not.toBeInTheDocument();
  });

  it("en inglés muestra todas las lecturas y marca la usada", () => {
    render(
      <Respuesta
        resultado={{
          ...respuestaBase,
          idioma: "en",
          lecturas_traduccion: ["zorro", "zorra"],
          traduccion_usada: "zorro",
          consulta_traducida: "zorro",
        }}
      />,
    );
    const lista = screen.getByRole("list");
    expect(within(lista).getAllByRole("listitem")).toHaveLength(2);
    expect(within(lista).getByText("zorro — usada")).toBeInTheDocument();
    expect(within(lista).getByText("zorra")).toBeInTheDocument();
  });
});

describe("base de demostración (HU-09)", () => {
  const estado = (extra) =>
    vi.stubGlobal(
      "fetch",
      vi.fn((url) =>
        url.endsWith("/api/estado")
          ? json({
              fragmentos_indexados: 3605,
              umbral_abstencion: 0.48,
              generador_disponible: true,
              base_datos_disponible: true,
              modelo: "qwen3.5:4b",
              ...extra,
            })
          : json([]),
      ),
    );

  it("la cabecera avisa cuando la base es de demostración", async () => {
    estado({ base_demostracion: true, consultas_por_origen: { carga: 800 } });
    render(<App />);
    expect(await screen.findByTestId("base-demostracion")).toHaveTextContent(/demostración/);
  });

  it("no avisa con una base de demanda real", async () => {
    estado({ base_demostracion: false });
    render(<App />);
    await screen.findByText(/fragmentos indexados/);
    expect(screen.queryByTestId("base-demostracion")).toBeNull();
  });
});
