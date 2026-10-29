// Configuración de la nube (ADR-032): «Usar mi propia clave de Gemini». La clave vive solo en
// la memoria de la pestaña (api.js); no se guarda en localStorage ni se muestra de nuevo.
import { useState } from "react";

import { fijarClaveGemini, hayClaveGemini } from "../api";

export default function ConfiguracionNube() {
  const [borrador, setBorrador] = useState("");
  const [activa, setActiva] = useState(hayClaveGemini);

  const usar = (evento) => {
    evento.preventDefault();
    fijarClaveGemini(borrador);
    setBorrador("");
    setActiva(hayClaveGemini());
  };

  const quitar = () => {
    fijarClaveGemini("");
    setActiva(false);
  };

  return (
    <details className="configuracion-nube">
      <summary>Configuración</summary>
      <form onSubmit={usar} className="configuracion-nube__formulario">
        <label htmlFor="clave-gemini">Usar mi propia clave de Gemini</label>
        <input
          id="clave-gemini"
          type="password"
          autoComplete="off"
          spellCheck={false}
          value={borrador}
          onChange={(e) => setBorrador(e.target.value)}
          placeholder={activa ? "Clave propia en uso" : "Pega tu clave de Google AI Studio"}
        />
        <button type="submit" disabled={!borrador.trim()}>
          Usar esta clave
        </button>
        {activa && (
          <button type="button" onClick={quitar}>
            Quitar mi clave
          </button>
        )}
      </form>
      <p className="configuracion-nube__nota">
        La clave se guarda solo en la memoria de esta pestaña y se envía por HTTPS en cada
        consulta. El servidor no la registra ni la almacena. Sin clave propia se usa la del
        servicio o, si no hay, el fragmento literal citado.
      </p>
    </details>
  );
}
