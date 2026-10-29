import { useEffect, useState } from "react";

import { obtenerDemanda, obtenerModelos, predecir } from "../api";
import Probabilidad from "./Probabilidad";

const EJEMPLOS = [
  "¿cómo se dice zorro en quechua wanka?",
  "¿cómo se dice criptomoneda en quechua wanka?",
  "¿Para qué sirven los sufijos en la gramática?",
  "¿Cómo se conjugan los verbos en la forma negativa del presente?",
];

const NOMBRES_CARACTERISTICAS = {
  similitud_maxima: "Similitud máxima",
  margen_top1_top2: "Margen 1.º − 2.º",
  similitud_media_top5: "Similitud media top-5",
  dispersion_top5: "Dispersión top-5",
  similitud_prosa_maxima: "Similitud prosa máx.",
  similitud_prosa_media_top3: "Similitud prosa media",
  palabras_compartidas_prosa: "Palabras compartidas",
  proporcion_compartida_prosa: "Proporción compartida",
  terminos_consulta: "Términos de la consulta",
  proporcion_fuera_vocabulario: "Fuera de vocabulario",
  coincidencia_lema: "Coincidencia de lema",
};

const NOMBRES_MODELOS = {
  regresion_logistica: "Regresión logística (elegido)",
  bosque_aleatorio: "Bosque aleatorio",
  linea_base_mayoritaria: "Línea base: clase mayoritaria",
  regla_umbral_pmv1: "Regla del PMV1 (umbral τ + lema)",
  regla_palabras_pmv1: "Regla del PMV1 (2 palabras compartidas)",
};

const pct = (v) =>
  typeof v === "number" ? `${(Math.round(v * 1000) / 10).toLocaleString("es-PE")} %` : "—";
const num = (v, d = 3) => (typeof v === "number" ? v.toFixed(d) : "—");

function CurvaRoc({ roc, auc }) {
  if (!roc?.fpr?.length) return null;
  const puntos = roc.fpr.map((x, i) => `${(x * 180).toFixed(1)},${(180 - roc.tpr[i] * 180).toFixed(1)}`);
  return (
    <figure className="roc">
      <svg viewBox="-28 -8 216 216" role="img" aria-label={`Curva ROC, AUC ${num(auc)}`}>
        <rect x="0" y="0" width="180" height="180" className="roc__marco" />
        <line x1="0" y1="180" x2="180" y2="0" className="roc__diagonal" />
        <polyline points={puntos.join(" ")} className="roc__curva" />
        <text x="90" y="204" textAnchor="middle" className="roc__eje">Tasa de falsos positivos</text>
        <text x="-14" y="90" textAnchor="middle" transform="rotate(-90 -14 90)" className="roc__eje">
          Sensibilidad
        </text>
      </svg>
      <figcaption>ROC en validación cruzada · AUC {num(auc)}</figcaption>
    </figure>
  );
}

function MatrizConfusion({ m }) {
  if (!m) return null;
  return (
    <table className="matriz" aria-label="Matriz de confusión">
      <thead>
        <tr>
          <th />
          <th>Predice sí</th>
          <th>Predice no</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Real sí</th>
          <td className="matriz__acierto">{m.vp}</td>
          <td>{m.fn}</td>
        </tr>
        <tr>
          <th>Real no</th>
          <td>{m.fp}</td>
          <td className="matriz__acierto">{m.vn}</td>
        </tr>
      </tbody>
    </table>
  );
}

function TarjetaModelo({ modelo }) {
  const cv = modelo.validacion_cruzada ?? {};
  return (
    <article className="modelo" data-testid={`modelo-${modelo.clave}`}>
      <header className="modelo__cabecera">
        <h3 className="modelo__titulo">
          {modelo.clave === "cobertura" ? "Predicción 1" : "Predicción 2"} · {modelo.nombre}
        </h3>
        <p className="modelo__meta">
          {modelo.historia} · {modelo.requisito} · {modelo.algoritmo} · {modelo.n_entrenamiento}{" "}
          consultas etiquetadas · corte de operación {modelo.corte_operacion}
        </p>
      </header>
      {!modelo.disponible ? (
        <p className="modelo__aviso">Modelo no disponible: ejecute scripts/entrenar_predictores.py.</p>
      ) : (
        <>
          <div className="cifras">
            <div className="cifra"><span>AUC-ROC</span><strong>{num(cv.auc_roc)}</strong></div>
            <div className="cifra"><span>F1</span><strong>{num(cv.f1)}</strong></div>
            <div className="cifra"><span>Precisión</span><strong>{pct(cv.precision)}</strong></div>
            <div className="cifra"><span>Sensibilidad</span><strong>{pct(cv.sensibilidad)}</strong></div>
            <div className="cifra"><span>Especificidad</span><strong>{pct(cv.especificidad)}</strong></div>
            <div className="cifra"><span>Exactitud</span><strong>{pct(cv.exactitud)}</strong></div>
          </div>
          <div className="modelo__graficos">
            <CurvaRoc roc={modelo.roc} auc={cv.auc_roc} />
            <div>
              <p className="modelo__subtitulo">Matriz de confusión (corte 0,5)</p>
              <MatrizConfusion m={cv.matriz_confusion} />
            </div>
          </div>
          {modelo.comparacion && (
            <table className="tabla" aria-label="Comparación de modelos">
              <thead>
                <tr>
                  <th>Modelo (validación cruzada 5 particiones)</th>
                  <th>AUC</th>
                  <th>F1</th>
                  <th>Especificidad</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(modelo.comparacion).map(([clave, m]) => (
                  <tr key={clave}>
                    <td>{NOMBRES_MODELOS[clave] ?? clave}</td>
                    <td>{num(m.auc_roc)}</td>
                    <td>{num(m.f1)}</td>
                    <td>{pct(m.especificidad)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {modelo.regla_mas_modelo && (
            <p className="modelo__nota">
              Regla del PMV1 + modelo (corte {modelo.regla_mas_modelo.corte}): pasajes mostrados
              ante preguntas cubiertas {pct(modelo.regla_mas_modelo.cobertura_E)} · ante preguntas
              fuera de cobertura {pct(modelo.regla_mas_modelo.falsos_positivos_F)} (la regla sola:{" "}
              {pct(modelo.comparacion?.regla_palabras_pmv1?.sensibilidad)} y{" "}
              {pct(1 - (modelo.comparacion?.regla_palabras_pmv1?.especificidad ?? 1))}).
            </p>
          )}
        </>
      )}
    </article>
  );
}

const NOMBRES_ORIGEN = {
  usuario: "usuario (demanda real)",
  carga: "carga (sintética)",
  arnes: "arnés (sintética)",
  humo: "humo (sintética)",
};

const NOMBRES_IDIOMA = { es: "español", en: "inglés" };

function Demanda({ demanda, sinteticas, onSinteticas }) {
  if (!demanda) return null;
  const e = demanda.estadisticas ?? {};
  const documentos = Object.entries(e.respaldo_por_documento ?? {});
  const maxDoc = Math.max(1, ...documentos.map(([, n]) => n));
  return (
    <section className="demanda" data-testid="demanda">
      <h2 className="panel__titulo">Analítica de demanda (HU-09)</h2>
      {demanda.modo === "demostracion" && (
        <p className="aviso-demostracion" role="status" data-testid="aviso-demostracion">
          {demanda.aviso}
        </p>
      )}
      <ul className="origenes" aria-label="Consultas por origen" data-testid="por-origen">
        {Object.entries(demanda.por_origen ?? {}).map(([origen, n]) => (
          <li key={origen}>
            {NOMBRES_ORIGEN[origen] ?? origen}: <strong>{n}</strong>
          </li>
        ))}
      </ul>
      <label className="origenes__control">
        <input
          type="checkbox"
          checked={sinteticas}
          onChange={(e) => onSinteticas(e.target.checked)}
        />{" "}
        Ver demostración con las consultas de prueba (no es demanda real)
      </label>
      <div className="cifras">
        <div className="cifra"><span>Consultas registradas</span><strong>{e.total ?? 0}</strong></div>
        <div className="cifra"><span>Abstenciones</span><strong>{e.abstenidas ?? 0}</strong></div>
        <div className="cifra">
          <span>P(cobertura) media</span><strong>{pct(e.probabilidad_cobertura_media)}</strong>
        </div>
        <div className="cifra">
          <span>Latencia p95</span><strong>{num(e.latencia_p95_ms, 1)} ms</strong>
        </div>
      </div>
      <div className="distribuciones">
        <ul className="origenes" aria-label="Consultas por idioma" data-testid="por-idioma">
          <li>Por idioma:</li>
          {Object.entries(e.por_idioma ?? {}).map(([idioma, n]) => (
            <li key={idioma}>
              {NOMBRES_IDIOMA[idioma] ?? idioma}: <strong>{n}</strong>
            </li>
          ))}
        </ul>
        <ul className="origenes" aria-label="Consultas por vía de respaldo" data-testid="por-via">
          <li>Por vía:</li>
          {Object.entries(e.por_via ?? {}).map(([via, n]) => (
            <li key={via}>
              {via}: <strong>{n}</strong>
            </li>
          ))}
        </ul>
      </div>
      {!demanda.suficiente ? (
        <p className="modelo__aviso" role="status">{demanda.mensaje}</p>
      ) : (
        <>
          <p className="modelo__subtitulo">Documento que respalda las respuestas</p>
          <ul className="barras">
            {documentos.map(([doc, n]) => (
              <li key={doc}>
                <span className="barras__nombre">{doc}</span>
                <span className="barras__pista">
                  <span className="barras__relleno" style={{ width: `${(n / maxDoc) * 100}%` }} />
                </span>
                <span className="barras__valor">{n}</span>
              </li>
            ))}
          </ul>
          <p className="modelo__subtitulo">
            Prioridades para ampliar el corpus ({demanda.terminos_distintos_no_cubiertos} términos
            sin cobertura)
          </p>
          <table className="tabla" aria-label="Demanda insatisfecha">
            <thead>
              <tr>
                <th>Término consultado</th>
                <th>Consultas</th>
                <th>P(cobertura)</th>
                <th>Demanda insatisfecha</th>
                <th>Diagnóstico</th>
              </tr>
            </thead>
            <tbody>
              {demanda.prioridades.map((p) => (
                <tr key={p.termino}>
                  <td>{p.termino}</td>
                  <td>{p.consultas}</td>
                  <td>{pct(p.probabilidad_cobertura_media)}</td>
                  <td>{num(p.demanda_insatisfecha, 2)}</td>
                  <td>{p.diagnostico}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  );
}

export default function PanelPrediccion() {
  const [texto, setTexto] = useState("");
  const [prediccion, setPrediccion] = useState(null);
  const [modelos, setModelos] = useState([]);
  const [demanda, setDemanda] = useState(null);
  const [sinteticas, setSinteticas] = useState(false);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  const cargarDemanda = (incluir) =>
    obtenerDemanda(15, incluir).then(setDemanda).catch(() => setDemanda(null));

  const cargar = () => {
    obtenerModelos().then(setModelos).catch((e) => setError(e.message));
    cargarDemanda(sinteticas);
  };

  const alternarSinteticas = (incluir) => {
    setSinteticas(incluir);
    cargarDemanda(incluir);
  };

  useEffect(cargar, []);

  const lanzar = async (consulta) => {
    const limpio = consulta.trim();
    if (!limpio) return;
    setTexto(limpio);
    setCargando(true);
    setError(null);
    try {
      setPrediccion(await predecir(limpio));
    } catch (e) {
      setError(e.message);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="panel">
      <section className="caja">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            lanzar(texto);
          }}
        >
          <label className="caja__etiqueta" htmlFor="consulta-ml">
            Probar los modelos predictivos con una consulta
          </label>
          <div className="caja__fila">
            <input
              id="consulta-ml"
              className="caja__entrada"
              value={texto}
              maxLength={300}
              onChange={(e) => setTexto(e.target.value)}
              placeholder="Escribe una consulta en español o inglés"
            />
            <button className="caja__boton" type="submit" disabled={cargando || !texto.trim()}>
              Predecir
            </button>
          </div>
        </form>
        <div className="caja__ejemplos">
          <span className="caja__ejemplos-titulo">Ejemplos:</span>
          {EJEMPLOS.map((ej) => (
            <button key={ej} type="button" className="caja__ejemplo" onClick={() => lanzar(ej)}>
              {ej}
            </button>
          ))}
        </div>
      </section>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {prediccion && (
        <section className="respuesta" data-testid="resultado-prediccion">
          <h2 className="respuesta__titulo">Predicción para «{prediccion.texto}»</h2>
          <Probabilidad
            etiqueta="Predicción 1 · probabilidad de respaldo documental"
            valor={prediccion.cobertura?.probabilidad}
            corte={prediccion.cobertura?.corte}
            testId="p-cobertura"
          />
          <p className="indicadores__linea">
            {prediccion.cobertura?.decision}
            {prediccion.cobertura?.bloquearia_respuesta &&
              " · por debajo del corte: el sistema se abstendría aunque la similitud lo permitiera"}
          </p>
          <Probabilidad
            etiqueta="Predicción 2 · probabilidad de que los pasajes de prosa traten la pregunta"
            valor={prediccion.pasajes?.probabilidad}
            corte={prediccion.pasajes?.corte}
            testId="p-pasajes"
          />
          <p className="indicadores__linea">{prediccion.pasajes?.decision}</p>
          <details className="caracteristicas">
            <summary>Características que recibió el modelo</summary>
            <table className="tabla">
              <tbody>
                {Object.entries(prediccion.caracteristicas ?? {}).map(([k, v]) => (
                  <tr key={k}>
                    <td>{NOMBRES_CARACTERISTICAS[k] ?? k}</td>
                    <td>{num(v, 4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </details>
        </section>
      )}

      <section>
        <h2 className="panel__titulo">Modelos de aprendizaje automático</h2>
        {modelos.map((m) => (
          <TarjetaModelo key={m.clave} modelo={m} />
        ))}
      </section>

      <Demanda demanda={demanda} sinteticas={sinteticas} onSinteticas={alternarSinteticas} />
      <button type="button" className="boton" onClick={cargar}>
        Actualizar métricas y demanda
      </button>
    </div>
  );
}
