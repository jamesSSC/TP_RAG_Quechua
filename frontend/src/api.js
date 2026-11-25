// URL de la API: solo desde VITE_API_URL. Vacia (o sin definir) = rutas relativas al mismo
// origen, que es como el ejecutable sirve la interfaz; en desarrollo Vite redirige /api.
const BASE = import.meta.env.VITE_API_URL ?? "";
export const URL_API = BASE || "mismo origen";
// La version web habla con una API remota (Render); el escritorio, con la del propio equipo.
export const API_REMOTA = BASE !== "";
// REF-02 (ADR-033): pasado este tiempo sin respuesta, la interfaz avisa de la espera.
export const AVISO_ESPERA_MS = 4000;

// BYOK (ADR-032): clave de Gemini del propio usuario. Solo en memoria de esta pestaña: sin
// localStorage ni cookies; se pierde al recargar. Viaja en la cabecera X-Gemini-Key por HTTPS.
let claveGemini = "";
export const fijarClaveGemini = (clave) => {
  claveGemini = (clave ?? "").trim();
};
export const hayClaveGemini = () => claveGemini !== "";
// S13 · ADR-035: token de administracion, tambien solo en memoria (nunca en el bundle ni en
// localStorage). Solo se envia si el administrador lo escribio en la pestaña correspondiente.
let tokenAdmin = "";
export const fijarTokenAdmin = (token) => {
  tokenAdmin = (token ?? "").trim();
};
export const hayTokenAdmin = () => tokenAdmin !== "";
const cabecerasClave = () => ({
  ...(claveGemini ? { "X-Gemini-Key": claveGemini } : {}),
  ...(tokenAdmin ? { "X-Admin-Token": tokenAdmin } : {}),
});

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
      headers: { "Content-Type": "application/json", ...cabecerasClave() },
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
      API_REMOTA
        ? "No se pudo conectar con el servicio en la nube. Si estuvo sin uso, puede tardar " +
            "hasta un minuto en activarse: vuelve a intentarlo."
        : "No se pudo conectar con el servicio local. Comprueba que esté en marcha.",
      "red",
    );
  } finally {
    clearTimeout(temporizador);
  }
  if (!respuesta.ok) {
    const detalle = await respuesta.json().catch(() => ({}));
    // Un 422 con detalle de texto (p. ej. una fuente sin licenciamiento) se muestra tal cual;
    // el de la validacion del cuerpo (lista de errores) es el de la consulta (M-03).
    if (respuesta.status === 422 && typeof detalle.detail !== "string") {
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

// REF-07 (ADR-040): «¿te sirvió?». Solo el id de la consulta y sí/no.
export const valorar = (consultaId, util) =>
  pedir("/api/valoraciones", {
    method: "POST",
    body: JSON.stringify({ consulta_id: consultaId, util }),
  });

export const obtenerHistorial = () => pedir("/api/historial");

// S13 · ADR-035: antes de desbloquear la gestion, el token se comprueba contra el servidor con una
// lectura protegida e inocua (`GET /api/historial?limite=1`). Si la API lo rechaza (401/403), se
// descarta y la interfaz sigue en solo lectura. La autorizacion real sigue siendo la del servidor.
export async function verificarTokenAdmin(token) {
  fijarTokenAdmin(token);
  try {
    await pedir("/api/historial?limite=1");
    return true;
  } catch (e) {
    fijarTokenAdmin("");
    throw e;
  }
}

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
    headers: cabecerasClave(),
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
