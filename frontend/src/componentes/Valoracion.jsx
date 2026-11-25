// REF-07 (ADR-040): «¿te sirvió esta respuesta?». Solo envía el id de la consulta y sí/no: ningún
// texto libre ni dato personal. Una valoración por respuesta; no cambia la respuesta ni τ.
import { useState } from "react";

import { valorar } from "../api";

export default function Valoracion({ consultaId }) {
  const [estado, setEstado] = useState("pendiente"); // pendiente | enviando | hecha | error
  const [mensaje, setMensaje] = useState("");

  if (!consultaId) return null;

  const enviar = async (util) => {
    setEstado("enviando");
    try {
      await valorar(consultaId, util);
      setEstado("hecha");
      setMensaje("Gracias: su valoración se registró sin datos personales.");
    } catch (e) {
      if (e?.estado === 409) {
        setEstado("hecha");
        setMensaje("Esta respuesta ya fue valorada.");
        return;
      }
      setEstado("error");
      setMensaje("No se pudo registrar la valoración. La respuesta no cambia.");
    }
  };

  return (
    <div className="valoracion" data-testid="valoracion">
      {estado === "hecha" ? (
        <output>{mensaje}</output>
      ) : (
        <>
          <span className="valoracion__pregunta" id={`valorar-${consultaId}`}>
            ¿Le sirvió esta respuesta?
          </span>
          <div role="group" aria-labelledby={`valorar-${consultaId}`} className="valoracion__botones">
            <button
              type="button"
              className="valoracion__boton"
              disabled={estado === "enviando"}
              onClick={() => enviar(true)}
            >
              Sí
            </button>
            <button
              type="button"
              className="valoracion__boton"
              disabled={estado === "enviando"}
              onClick={() => enviar(false)}
            >
              No
            </button>
          </div>
          {estado === "error" && (
            <p className="valoracion__error" role="alert">
              {mensaje}
            </p>
          )}
        </>
      )}
    </div>
  );
}
