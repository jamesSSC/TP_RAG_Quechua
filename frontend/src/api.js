// URL de la API: solo desde VITE_API_URL. Vacia (o sin definir) = rutas relativas al mismo
// origen, que es como el ejecutable sirve la interfaz; en desarrollo Vite redirige /api.
const BASE = import.meta.env.VITE_API_URL ?? "";

// La primera consulta con el modelo en CPU puede tardar decenas de segundos.
export const TIEMPO_MAXIMO_MS = 180000;

export class ErrorApi extends Error {
  constructor(mensaje, tipo, estado) {
    super(mensaje);
    this.tipo = tipo; // "red" | "tiempo" | "validacion" | "servicio"
    this.estado = estado;
  }
}

async function pedir(ruta, opciones = {}) {
  const control = new AbortController();
  const temporizador = setTimeout(() => control.abort(), TIEMPO_MAXIMO_MS);
  let respuesta;
  try {
    respuesta = await fetch(`${BASE}${ruta}`, {
      headers: { "Content-Type": "application/json" },
      signal: control.signal,
      ...opciones,
    });
  } catch (e) {
    if (e?.name === "AbortError") {
      throw new ErrorApi(
        "La consulta tardó demasiado en responder. Inténtalo de nuevo.",
        "tiempo",
      );
    }
    throw new ErrorApi(
      "No se pudo conectar con el servicio local. Comprueba que esté en marcha.",
      "red",
    );
  } finally {
    clearTimeout(temporizador);
  }
  if (!respuesta.ok) {
    const detalle = await respuesta.json().catch(() => ({}));
    if (respuesta.status === 422) {
      throw new ErrorApi(
        "La consulta no es válida: escribe entre 1 y 300 caracteres.",
        "validacion",
        422,
      );
    }
    throw new ErrorApi(
      typeof detalle.detail === "string"
        ? detalle.detail
        : `El servicio devolvió un error (${respuesta.status}).`,
      "servicio",
      respuesta.status,
    );
  }
  return respuesta.status === 204 ? null : respuesta.json();
}

export const consultar = (texto) =>
  pedir("/api/consultas", { method: "POST", body: JSON.stringify({ texto }) });

export const obtenerEstado = () => pedir("/api/estado");

export const obtenerHistorial = () => pedir("/api/historial");

export const borrarHistorial = () => pedir("/api/historial", { method: "DELETE" });

export const listarFuentes = () => pedir("/api/fuentes");

export const crearFuente = (fuente) =>
  pedir("/api/fuentes", { method: "POST", body: JSON.stringify(fuente) });

export const actualizarFuente = (id, fuente) =>
  pedir(`/api/fuentes/${id}`, { method: "PUT", body: JSON.stringify(fuente) });

export const eliminarFuente = (id) =>
  pedir(`/api/fuentes/${id}`, { method: "DELETE" });

export const listarDocumentos = () => pedir("/api/corpus/documentos");

export const reindexar = () =>
  pedir("/api/corpus/reindexar", { method: "POST" });

export async function ingestarDocumento(datos) {
  const cuerpo = new FormData();
  Object.entries(datos).forEach(([clave, valor]) => cuerpo.append(clave, valor));

  // Sin Content-Type explicito: el navegador anade el boundary de multipart.
  const respuesta = await fetch(`${BASE}/api/corpus/documentos`, {
    method: "POST",
    body: cuerpo,
  });
  if (!respuesta.ok) {
    const detalle = await respuesta.json().catch(() => ({}));
    throw new Error(detalle.detail ?? `Error ${respuesta.status}`);
  }
  return respuesta.json();
}

// PMV2 · casos de uso de prediccion (HU-08.1, HU-04) y analitica de demanda (HU-09).
export const predecir = (texto) =>
  pedir("/api/predicciones", { method: "POST", body: JSON.stringify({ texto }) });

export const obtenerModelos = () => pedir("/api/modelos");

export const obtenerDemanda = (top = 15, incluirSinteticas = false) =>
  pedir(`/api/analitica/demanda?top=${top}${incluirSinteticas ? "&incluir_sinteticas=true" : ""}`);
