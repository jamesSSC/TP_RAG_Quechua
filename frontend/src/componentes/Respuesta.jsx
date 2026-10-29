import Probabilidad from "./Probabilidad";

function Indicadores({ resultado }) {
  const { similitud_maxima, umbral, latencia_ms, via_respaldo, abstenida } = resultado;
  const tau = typeof umbral === "number" ? umbral : null;
  const porcentaje = Math.min(100, Math.max(0, similitud_maxima * 100));

  let via = null;
  if (!abstenida && via_respaldo === "lema") {
    via = "Respaldo: entrada exacta del diccionario";
  } else if (!abstenida && via_respaldo === "similitud") {
    via = "Respaldo: similitud ≥ τ";
  }

  return (
    <div className="indicadores">
      <div
        className="barra"
        role="meter"
        aria-label="Similitud frente al umbral τ"
        aria-valuemin={0}
        aria-valuemax={1}
        aria-valuenow={similitud_maxima}
      >
        <div className="barra__relleno" style={{ width: `${porcentaje}%` }} />
        {tau !== null && (
          <div
            className="barra__umbral"
            data-testid="marca-tau"
            style={{ left: `${tau * 100}%` }}
            title={`τ = ${tau}`}
          />
        )}
      </div>
      <p className="indicadores__linea">
        Similitud {similitud_maxima.toFixed(3)}
        {tau !== null && ` · τ = ${tau}`}
        {typeof latencia_ms === "number" && (
          <>
            {" "}
            · <span data-testid="latencia">Latencia: {Math.round(latencia_ms)} ms</span>
          </>
        )}
      </p>
      {via && (
        <p className="indicadores__via" data-testid="via-respaldo">
          {via}
          {via_respaldo === "lema" && tau !== null && (
            <>
              {" "}
              (la similitud {similitud_maxima.toFixed(3)} queda bajo τ = {tau})
            </>
          )}
        </p>
      )}
    </div>
  );
}

function Traduccion({ lecturas, usada }) {
  if (lecturas.length === 0 && !usada) return null;
  return (
    <div className="respuesta__traduccion">
      <p>
        La consulta se tradujo al español para buscar en el corpus. El término en quechua se
        toma literal del fragmento, sin traducir.
      </p>
      {lecturas.length > 0 && (
        <>
          <p className="respuesta__traduccion-titulo">Lecturas consideradas:</p>
          <ul className="lecturas">
            {lecturas.map((lectura) => (
              <li key={lectura} className={lectura === usada ? "lecturas__usada" : ""}>
                {lectura}
                {lectura === usada && " — usada"}
              </li>
            ))}
          </ul>
        </>
      )}
      {usada && lecturas.length === 0 && (
        <p>
          Lectura usada: <strong>{usada}</strong>
        </p>
      )}
    </div>
  );
}

// PMV2: lo que estimaron los modelos predictivos para esta consulta (HU-08.1 y HU-04).
function PrediccionMl({ resultado }) {
  const {
    probabilidad_cobertura: pCob,
    probabilidad_pasajes: pPas,
    abstencion_por_predictor: porPredictor,
  } = resultado;
  if (typeof pCob !== "number" && typeof pPas !== "number") return null;
  return (
    <div className="prediccion-ml" data-testid="prediccion-ml">
      <p className="prediccion-ml__titulo">Predicción del modelo (aprendizaje automático)</p>
      <Probabilidad etiqueta="Probabilidad de respaldo documental" valor={pCob} />
      {porPredictor && (
        <p className="prediccion-ml__nota">
          La similitud permitía responder, pero el modelo estimó una probabilidad de respaldo
          por debajo del corte y el sistema se abstuvo (RN-06: el modelo solo añade
          abstenciones).
        </p>
      )}
      <Probabilidad
        etiqueta="Probabilidad de que los pasajes traten la pregunta"
        valor={pPas}
        corte={0.5}
      />
    </div>
  );
}

export default function Respuesta({ resultado }) {
  if (!resultado) return null;

  const {
    abstenida,
    texto,
    respaldo = [],
    aviso,
    pasajes = [],
    lecturas_traduccion: lecturas = [],
    traduccion_usada: usada,
    consulta_traducida: traducida,
    aviso_generacion: avisoGeneracion,
  } = resultado;

  const hayPasajes = pasajes.length > 0;

  return (
    <section
      className={`respuesta ${abstenida ? "respuesta--abstenida" : ""}`}
      aria-live="polite"
    >
      <h2 className="respuesta__titulo">
        {abstenida
          ? hayPasajes
            ? "Sin respuesta confirmada"
            : "Sin respaldo documental"
          : "Respuesta"}
      </h2>

      <Traduccion lecturas={lecturas} usada={usada ?? traducida} />

      {avisoGeneracion && (
        <p className="respuesta__aviso-generacion" role="status">
          {avisoGeneracion}
        </p>
      )}

      {/* En una abstencion solo hay un mensaje de ausencia: ninguna forma destacada. */}
      <p className={abstenida ? "respuesta__ausencia" : "respuesta__texto"}>{texto}</p>

      {!abstenida && respaldo.length > 0 && (
        <div className="respaldo">
          <h3 className="respaldo__titulo">Fuente consultada</h3>
          {respaldo.map((f) => (
            <article key={f.fragmento_id} className="respaldo__item">
              <blockquote className="respaldo__cita">{f.texto}</blockquote>
              <p className="respaldo__origen">
                {f.documento} — página {f.pagina}
              </p>
              <p className="respaldo__metricas">
                Similitud {(f.similitud ?? f.puntuacion).toFixed(3)}
                {f.coincidencia_lema && " · entrada exacta del diccionario"}
              </p>
              {f.derivado_ocr && (
                <p className="respaldo__aviso-ocr">
                  Texto derivado por reconocimiento óptico: puede contener errores de
                  transcripción.
                </p>
              )}
            </article>
          ))}
        </div>
      )}

      {abstenida && hayPasajes && (
        <div className="pasajes">
          <h3 className="pasajes__titulo">Pasajes relacionados — no es una respuesta</h3>
          <p className="pasajes__nota">
            El sistema no afirma que respondan a la consulta: el material se entrega literal
            y citado para que lo juzgue quien consulta.
          </p>
          {pasajes.map((f) => (
            <article key={f.fragmento_id} className="pasajes__item">
              <p className="pasajes__cita">{f.texto}</p>
              <p className="pasajes__origen">
                {f.documento} — página {f.pagina}
              </p>
            </article>
          ))}
        </div>
      )}

      <Indicadores resultado={resultado} />

      <PrediccionMl resultado={resultado} />

      <footer className="respuesta__pie">
        <p className="respuesta__aviso">{aviso}</p>
      </footer>
    </section>
  );
}
