import { INDICE_NORMAL, TAMANOS } from "../tamanoTexto";

export default function TamanoTexto({ indice, onCambiar }) {
  return (
    <div className="tamano" role="group" aria-label="Tamaño del texto">
      <button
        type="button"
        className="tamano__boton"
        aria-label="A−, reducir tamaño del texto"
        onClick={() => onCambiar(indice - 1)}
        disabled={indice <= 0}
      >
        A−
      </button>
      <button
        type="button"
        className="tamano__boton"
        aria-label="A, restablecer tamaño del texto"
        onClick={() => onCambiar(INDICE_NORMAL)}
        disabled={indice === INDICE_NORMAL}
      >
        A
      </button>
      <button
        type="button"
        className="tamano__boton"
        aria-label="A+, aumentar tamaño del texto"
        onClick={() => onCambiar(indice + 1)}
        disabled={indice >= TAMANOS.length - 1}
      >
        A+
      </button>
    </div>
  );
}
