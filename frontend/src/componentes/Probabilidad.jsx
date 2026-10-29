// Barra de probabilidad estimada por un modelo predictivo, con la marca del corte de operacion.
export default function Probabilidad({ etiqueta, valor, corte, testId }) {
  if (typeof valor !== "number") return null;
  const porcentaje = Math.round(valor * 1000) / 10;
  const alta = typeof corte === "number" ? valor >= corte : valor >= 0.5;
  return (
    <div className="probabilidad" data-testid={testId}>
      <div className="probabilidad__cabecera">
        <span>{etiqueta}</span>
        <strong className={alta ? "probabilidad__valor--alta" : "probabilidad__valor--baja"}>
          {porcentaje.toLocaleString("es-PE")} %
        </strong>
      </div>
      <div
        className="barra barra--ml"
        role="meter"
        aria-label={etiqueta}
        aria-valuemin={0}
        aria-valuemax={1}
        aria-valuenow={valor}
      >
        <div
          className={`barra__relleno ${alta ? "" : "barra__relleno--baja"}`}
          style={{ width: `${Math.min(100, porcentaje)}%` }}
        />
        {typeof corte === "number" && (
          <div className="barra__umbral" style={{ left: `${corte * 100}%` }} title={`corte ${corte}`} />
        )}
      </div>
    </div>
  );
}
