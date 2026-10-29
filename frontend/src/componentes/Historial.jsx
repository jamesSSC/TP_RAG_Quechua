function etiquetaDeEstado(entrada) {
  if (entrada.abstenida) return "sin respaldo";
  if (entrada.via_respaldo === "lema") return "respondida · entrada exacta";
  return "respondida";
}

export default function Historial({ entradas, disponible = true, onBorrar, borrando = false }) {
  const confirmarBorrado = () => {
    if (window.confirm("¿Borrar todo el historial de consultas de este equipo?")) onBorrar();
  };

  return (
    <section className="historial">
      <div className="historial__cabecera">
        <h2 className="historial__titulo">Historial de consultas</h2>
        {entradas.length > 0 && (
          <button
            type="button"
            className="historial__borrar"
            onClick={confirmarBorrado}
            disabled={borrando}
          >
            Borrar historial
          </button>
        )}
      </div>

      <p className="historial__privacidad">
        No se guardan datos personales; las consultas se almacenan solo en este equipo y puedes
        borrarlas.
      </p>

      {!disponible && (
        <p className="historial__vacio">El historial no está disponible en este momento.</p>
      )}
      {disponible && entradas.length === 0 && (
        <p className="historial__vacio">Todavía no hay consultas guardadas.</p>
      )}
      {disponible && entradas.length > 0 && (
        <ul className="historial__lista">
          {entradas.map((entrada, indice) => (
            <li key={`${entrada.momento ?? ""}-${indice}`} className="historial__item">
              <span
                className={`historial__marca ${
                  entrada.abstenida ? "historial__marca--abstenida" : ""
                }`}
                aria-hidden="true"
              />
              <span className="historial__consulta">{entrada.consulta}</span>
              <span className="historial__estado">
                {etiquetaDeEstado(entrada)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
