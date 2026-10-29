import { useEffect, useState } from "react";

import { borrarHistorial, consultar, obtenerEstado, obtenerHistorial } from "./api";
import CajaConsulta from "./componentes/CajaConsulta";
import GestionCorpus from "./componentes/GestionCorpus";
import GestionFuentes from "./componentes/GestionFuentes";
import Historial from "./componentes/Historial";
import PanelPrediccion from "./componentes/PanelPrediccion";
import Respuesta from "./componentes/Respuesta";
import TamanoTexto from "./componentes/TamanoTexto";
import { guardarTamano, leerTamano, TAMANOS } from "./tamanoTexto";
import "./App.css";

export default function App() {
  const [vista, setVista] = useState("consulta");
  const [resultado, setResultado] = useState(null);
  const [historial, setHistorial] = useState({ entradas: [], disponible: true });
  const [estado, setEstado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [ultimaConsulta, setUltimaConsulta] = useState(null);
  const [tamano, setTamano] = useState(leerTamano);

  const cambiarTamano = (indice) => {
    const acotado = Math.min(TAMANOS.length - 1, Math.max(0, indice));
    setTamano(acotado);
    guardarTamano(acotado);
  };

  const cargarHistorial = () =>
    obtenerHistorial()
      .then((entradas) => setHistorial({ entradas, disponible: true }))
      .catch(() => setHistorial({ entradas: [], disponible: false }));

  useEffect(() => {
    obtenerEstado()
      .then(setEstado)
      .catch(() => setEstado(null));
    cargarHistorial();
  }, []);

  const lanzarConsulta = async (texto) => {
    setCargando(true);
    setError(null);
    setUltimaConsulta(texto);
    try {
      const respuesta = await consultar(texto);
      setResultado(respuesta);
      await cargarHistorial();
    } catch (e) {
      setError(e.message);
      setResultado(null);
    } finally {
      setCargando(false);
    }
  };

  const borrar = async () => {
    try {
      await borrarHistorial();
    } finally {
      await cargarHistorial();
    }
  };

  return (
    <div className={`aplicacion aplicacion--${TAMANOS[tamano]}`}>
      <header className="cabecera">
        <div>
          <h1 className="cabecera__titulo">Asistente de consulta del quechua wanka</h1>
          <p className="cabecera__subtitulo">
            Consulta sobre el corpus documental publicado de la variedad wanka de Junín
          </p>
        </div>
        <TamanoTexto indice={tamano} onCambiar={cambiarTamano} />
      </header>

      {estado?.base_demostracion && (
        <p className="aviso-demostracion" role="status" data-testid="base-demostracion">
          Base de demostración: la mayoría de las consultas guardadas son generadas por pruebas, no
          demanda real.
        </p>
      )}

      <nav className="pestanas">
        <button
          className={`pestana ${vista === "consulta" ? "pestana--activa" : ""}`}
          onClick={() => setVista("consulta")}
        >
          Consultar
        </button>
        <button
          className={`pestana ${vista === "fuentes" ? "pestana--activa" : ""}`}
          onClick={() => setVista("fuentes")}
        >
          Fuentes del corpus
        </button>
        <button
          className={`pestana ${vista === "corpus" ? "pestana--activa" : ""}`}
          onClick={() => setVista("corpus")}
        >
          Incorporar documentos
        </button>
        <button
          className={`pestana ${vista === "prediccion" ? "pestana--activa" : ""}`}
          onClick={() => setVista("prediccion")}
        >
          Predicción ML
        </button>
      </nav>

      <main className="contenido">
        {vista === "consulta" ? (
          <>
            <CajaConsulta onConsultar={lanzarConsulta} cargando={cargando} />

            {error && (
              <div className="error" role="alert">
                <p className="error__mensaje">{error}</p>
                <button
                  type="button"
                  className="error__reintentar"
                  onClick={() => lanzarConsulta(ultimaConsulta)}
                  disabled={cargando || !ultimaConsulta}
                >
                  Reintentar
                </button>
              </div>
            )}
            {cargando && (
              <p className="cargando" role="status">
                <span className="giro" aria-hidden="true" /> Buscando en el corpus…
              </p>
            )}

            <Respuesta resultado={resultado} />
            <Historial
              entradas={historial.entradas}
              disponible={historial.disponible}
              onBorrar={borrar}
            />
          </>
        ) : vista === "prediccion" ? (
          <PanelPrediccion />
        ) : vista === "fuentes" ? (
          <GestionFuentes />
        ) : (
          <GestionCorpus />
        )}
      </main>

      <footer className="pie">
        {estado ? (
          <span>
            {estado.fragmentos_indexados.toLocaleString("es-PE")} fragmentos indexados ·
            umbral de abstención {estado.umbral_abstencion} · modelo {estado.modelo} ·
            {estado.predictores_disponibles ? " predictores ML activos ·" : ""}
            procesamiento local
          </span>
        ) : (
          <span>Sin conexión con el servicio local</span>
        )}
      </footer>
    </div>
  );
}
