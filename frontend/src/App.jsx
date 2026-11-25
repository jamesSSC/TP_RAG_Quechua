import { useEffect, useState } from "react";

import {
  API_REMOTA,
  AVISO_ESPERA_MS,
  borrarHistorial,
  consultar,
  obtenerEstado,
  hayTokenAdmin,
  obtenerHistorial,
  URL_API,
} from "./api";
import AccesoAdministracion from "./componentes/AccesoAdministracion";
import ConfiguracionNube from "./componentes/ConfiguracionNube";
import CajaConsulta from "./componentes/CajaConsulta";
import EstadoInicial from "./componentes/EstadoInicial";
import GestionCorpus from "./componentes/GestionCorpus";
import GestionFuentes from "./componentes/GestionFuentes";
import Historial from "./componentes/Historial";
import PanelPrediccion from "./componentes/PanelPrediccion";
import Respuesta from "./componentes/Respuesta";
import TamanoTexto from "./componentes/TamanoTexto";
import { guardarTamano, leerTamano, TAMANOS } from "./tamanoTexto";
import logo from "./assets/logo_contorno.svg";
import "./App.css";

const PESTANAS = [
  { id: "consulta", texto: "Consultar" },
  { id: "fuentes", texto: "Fuentes del corpus" },
  { id: "corpus", texto: "Incorporar documentos" },
  { id: "prediccion", texto: "Predicción ML" },
];

function Pestanas({ vista, onCambiar }) {
  return (
    <nav className="pestanas">
      {PESTANAS.map(({ id, texto }) => (
        <button
          key={id}
          className={`pestana ${vista === id ? "pestana--activa" : ""}`}
          aria-current={vista === id ? "page" : undefined}
          onClick={() => onCambiar(id)}
        >
          {texto}
        </button>
      ))}
    </nav>
  );
}

// REF-02 (ADR-033): verdadero cuando `activo` lleva mas de AVISO_ESPERA_MS sin resolverse.
function useEsperaLarga(activo) {
  const [larga, setLarga] = useState(false);
  useEffect(() => {
    if (!activo) return undefined;
    const temporizador = setTimeout(() => setLarga(true), AVISO_ESPERA_MS);
    return () => {
      clearTimeout(temporizador);
      setLarga(false);
    };
  }, [activo]);
  return activo && larga;
}

function AvisoEspera({ visible }) {
  if (!visible) return null;
  return (
    <output className="aviso-arranque" data-testid="aviso-arranque">
      {API_REMOTA
        ? "El servicio en la nube se está activando tras un periodo sin uso (plan gratuito). " +
          "La primera respuesta puede tardar hasta un minuto; no hace falta recargar la página."
        : "La respuesta está tardando más de lo habitual: el modelo puede estar cargándose. " +
          "Espere, por favor."}
    </output>
  );
}

function PieEstado({ estado, conectando }) {
  if (!estado) {
    if (conectando) return <span>Conectando con el servicio…</span>;
    return (
      <span>Sin conexión con el servicio {API_REMOTA ? "en la nube" : "local"}</span>
    );
  }
  if (estado.entorno && estado.entorno !== "local") {
    return (
      <span data-testid="pie-entorno">
        Entorno: {estado.entorno} · API: {URL_API} · base {estado.motor_base_datos} · corpus{" "}
        {estado.origen_corpus} ({estado.fragmentos_indexados.toLocaleString("es-PE")}{" "}
        fragmentos, {estado.documentos_corpus} documentos) · redacción {estado.generador}
        {estado.generador === "gemini" ? ` (${estado.modelo})` : ""} · modelos ML{" "}
        {estado.predictores_disponibles ? "cargados" : "no cargados"} · umbral{" "}
        {estado.umbral_abstencion}
      </span>
    );
  }
  return (
    <span>
      {estado.fragmentos_indexados.toLocaleString("es-PE")} fragmentos indexados ·
      umbral de abstención {estado.umbral_abstencion} · modelo {estado.modelo} ·
      {estado.predictores_disponibles ? " predictores ML activos ·" : ""}
      procesamiento local
    </span>
  );
}

export default function App() {
  const [vista, setVista] = useState("consulta");
  const [resultado, setResultado] = useState(null);
  const [historial, setHistorial] = useState({ entradas: [], disponible: true });
  const [estado, setEstado] = useState(null);
  // Mientras /api/estado no responde (arranque en frio de Render: 62-72 s medidos).
  const [conectando, setConectando] = useState(true);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [ultimaConsulta, setUltimaConsulta] = useState(null);
  const [tamano, setTamano] = useState(leerTamano);
  // S13 · ADR-036: en la nube el historial publico es el de esta pestaña (en memoria); el de la
  // base solo lo lee el administrador. En local sigue siendo el de la base (RF-11).
  const [historialSesion, setHistorialSesion] = useState([]);
  const [administrando, setAdministrando] = useState(hayTokenAdmin);
  const protegida = Boolean(estado?.escritura_protegida);

  const cambiarTamano = (indice) => {
    const acotado = Math.min(TAMANOS.length - 1, Math.max(0, indice));
    setTamano(acotado);
    guardarTamano(acotado);
  };

  const cargarHistorial = () =>
    obtenerHistorial()
      .then((entradas) => setHistorial({ entradas, disponible: true }))
      .catch(() => setHistorial({ entradas: [], disponible: false }));

  const cargarEstado = () =>
    obtenerEstado()
      .then((datos) => {
        setEstado(datos);
        return datos;
      })
      .catch(() => setEstado(null))
      .finally(() => setConectando(false));

  const reintentarEstado = () => {
    setConectando(true);
    cargarEstado().then((datos) => {
      if (!datos?.escritura_protegida) cargarHistorial();
    });
  };

  useEffect(() => {
    cargarEstado().then((datos) => {
      if (!datos?.escritura_protegida) cargarHistorial();
    });
  }, []);

  const esperaLarga = useEsperaLarga(conectando || cargando);

  const lanzarConsulta = async (texto) => {
    setCargando(true);
    setError(null);
    setUltimaConsulta(texto);
    try {
      const respuesta = await consultar(texto);
      setResultado(respuesta);
      if (protegida) {
        setHistorialSesion((previo) => [
          {
            consulta: texto,
            abstenida: respuesta.abstenida,
            via_respaldo: respuesta.via_respaldo,
            momento: new Date().toISOString(),
          },
          ...previo,
        ]);
      } else {
        await cargarHistorial();
      }
    } catch (e) {
      setError(e.message);
      setResultado(null);
    } finally {
      setCargando(false);
    }
  };

  const borrar = async () => {
    if (protegida) {
      setHistorialSesion([]);
      return;
    }
    try {
      await borrarHistorial();
    } finally {
      await cargarHistorial();
    }
  };

  const soloLectura = protegida && !administrando;
  const acceso = <AccesoAdministracion onAcceso={() => setAdministrando(true)} />;
  const otrasVistas = {
    prediccion: <PanelPrediccion />,
    fuentes: soloLectura ? acceso : <GestionFuentes />,
    corpus: soloLectura ? acceso : <GestionCorpus />,
  };

  return (
    <div className={`aplicacion aplicacion--${TAMANOS[tamano]}`}>
      <header className="cabecera">
        <div className="cabecera__marca">
          <img
            className="cabecera__logo"
            src={logo}
            alt="Logo del asistente de consulta del quechua wanka"
            width="56"
            height="56"
          />
          <div>
            <h1 className="cabecera__titulo">Asistente de consulta del quechua wanka</h1>
            <p className="cabecera__subtitulo">
              Consulta sobre el corpus documental publicado de la variedad wanka de Junín
            </p>
          </div>
        </div>
        <TamanoTexto indice={tamano} onCambiar={cambiarTamano} />
      </header>

      {estado?.generador === "gemini" && (
        <output className="aviso-privacidad" data-testid="aviso-privacidad">
          En la versión en la nube, el texto de la consulta y los fragmentos se envían a la API de
          Google para redactar; no se envían datos personales.
        </output>
      )}

      {estado?.base_demostracion && (
        <output className="aviso-demostracion" data-testid="base-demostracion">
          Base de demostración: la mayoría de las consultas guardadas son generadas por pruebas, no
          demanda real.
        </output>
      )}

      <AvisoEspera visible={esperaLarga} />

      <Pestanas vista={vista} onCambiar={setVista} />

      <main className="contenido">
        {vista === "consulta" ? (
          <>
            <EstadoInicial
              estado={estado}
              conectando={conectando}
              onReintentar={reintentarEstado}
            />
            {estado?.generador === "gemini" && <ConfiguracionNube />}
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
              <output className="cargando">
                <span className="giro" aria-hidden="true" /> Buscando en el corpus…
              </output>
            )}

            <Respuesta resultado={resultado} onConsultar={lanzarConsulta} />
            <Historial
              enLaNube={Boolean(estado?.entorno && estado.entorno !== "local")}
              porSesion={protegida}
              entradas={protegida ? historialSesion : historial.entradas}
              disponible={protegida || historial.disponible}
              onBorrar={borrar}
            />
          </>
        ) : (
          otrasVistas[vista]
        )}
      </main>

      <footer className="pie">
        <PieEstado estado={estado} conectando={conectando} />
      </footer>
    </div>
  );
}
