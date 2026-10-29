// Pantalla de estado inicial (B14): lo que el sistema tiene disponible al arrancar. Lee /api/estado.
// Sin Ollama la aplicacion sigue funcionando: responde con el fragmento literal y lo avisa.
function Indicador({ nombre, ok, detalle, testId }) {
  return (
    <li className={`estado__item ${ok ? "estado__item--ok" : "estado__item--aviso"}`} data-testid={testId}>
      <span className="estado__marca" aria-hidden="true">
        {ok ? "✔" : "⚠"}
      </span>
      <span className="estado__nombre">{nombre}</span>
      <span className="estado__detalle">{detalle}</span>
    </li>
  );
}

export default function EstadoInicial({ estado }) {
  if (!estado) {
    return (
      <section className="estado" aria-label="Estado del sistema" data-testid="estado-inicial">
        <output className="estado__aviso" data-testid="estado-sin-servicio">
          Sin conexión con el servicio local. Compruebe que la aplicación esté en marcha.
        </output>
      </section>
    );
  }
  const hayOllama = Boolean(estado.generador_disponible);
  // En la nube (ADR-032) no hay Ollama: redacta Gemini o el extractivo sin modelo.
  const enLaNube = estado.generador === "gemini" || estado.generador === "extractivo";
  const nombreGenerador = estado.generador === "gemini" ? "Gemini" : "Extractivo";
  return (
    <section className="estado" aria-label="Estado del sistema" data-testid="estado-inicial">
      <h2 className="estado__titulo">Estado del sistema</h2>
      <ul className="estado__lista">
        {enLaNube ? (
          <Indicador
            testId="estado-generador"
            nombre="Redacción"
            ok={hayOllama}
            detalle={
              hayOllama
                ? `${nombreGenerador} configurado`
                : "sin clave: fragmento literal citado"
            }
          />
        ) : (
          <Indicador
            testId="estado-ollama"
            nombre="Ollama"
            ok={hayOllama}
            detalle={hayOllama ? "responde" : "no responde"}
          />
        )}
        <Indicador
          testId="estado-modelo"
          nombre="Modelo"
          ok={hayOllama}
          detalle={estado.modelo}
        />
        <Indicador
          testId="estado-corpus"
          nombre="Corpus"
          ok={estado.fragmentos_indexados > 0}
          detalle={`${Number(estado.fragmentos_indexados).toLocaleString("es-PE")} fragmentos en el corpus`}
        />
        <Indicador
          testId="estado-base"
          nombre="Base de datos"
          ok={Boolean(estado.base_datos_disponible)}
          detalle={estado.base_datos_disponible ? "conectada" : "sin base: no se guarda el historial"}
        />
      </ul>
      {!hayOllama && !enLaNube && (
        <output className="estado__aviso" data-testid="aviso-sin-ollama">
          Ollama no responde: las respuestas muestran el fragmento literal con su documento y página,
          sin redacción. Para activar la redacción inicie Ollama y descargue el modelo {estado.modelo}.
        </output>
      )}
    </section>
  );
}
