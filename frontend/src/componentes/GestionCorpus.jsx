import { useEffect, useState } from "react";

import { ingestarDocumento, listarDocumentos, reindexar } from "../api";

const VACIO = {
  titulo: "",
  entidad_publicadora: "",
  licenciamiento: "",
  tipo: "lexicografico",
};

export default function GestionCorpus() {
  const [corpus, setCorpus] = useState({ documentos: [], total_fragmentos: 0 });
  const [formulario, setFormulario] = useState(VACIO);
  const [archivo, setArchivo] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);
  const [trabajando, setTrabajando] = useState(false);

  const recargar = () => {
    listarDocumentos().then(setCorpus).catch((e) => setError(e.message));
  };

  useEffect(recargar, []);

  const cambiar = (campo) => (evento) =>
    setFormulario((previo) => ({ ...previo, [campo]: evento.target.value }));

  const subir = async (evento) => {
    evento.preventDefault();
    if (!archivo) return;
    setTrabajando(true);
    setError(null);
    setResultado(null);
    try {
      const salida = await ingestarDocumento({ ...formulario, archivo });
      setResultado(salida);
      setFormulario(VACIO);
      setArchivo(null);
      evento.target.reset();
      recargar();
    } catch (e) {
      setError(e.message);
    } finally {
      setTrabajando(false);
    }
  };

  const reconstruir = async () => {
    setTrabajando(true);
    setError(null);
    try {
      setCorpus(await reindexar());
    } catch (e) {
      setError(e.message);
    } finally {
      setTrabajando(false);
    }
  };

  return (
    <section className="fuentes">
      <h2 className="fuentes__titulo">Corpus documental</h2>
      <p className="fuentes__intro">
        Al incorporar un documento se extrae su texto conservando la página de origen, se
        segmenta según su tipo y se reconstruye el índice. El material lexicográfico se
        segmenta por entrada y el de prosa por bloques: esa distinción es la que más pesa
        en la calidad de la recuperación.
      </p>

      {error && (
        <p id="error-corpus" role="alert" className="error">
          {error}
        </p>
      )}

      <form
        className="formulario"
        onSubmit={subir}
        aria-describedby={error ? "error-corpus" : undefined}
      >
        <h3 className="formulario__titulo">Incorporar documento</h3>

        <div className="formulario__rejilla">
          <label className="campo campo--ancho">
            <span>Archivo PDF</span>
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setArchivo(e.target.files[0] ?? null)}
              required
            />
          </label>

          <label className="campo campo--ancho">
            <span>Título</span>
            <input value={formulario.titulo} onChange={cambiar("titulo")} required />
          </label>

          <label className="campo">
            <span>Entidad publicadora</span>
            <input
              value={formulario.entidad_publicadora}
              onChange={cambiar("entidad_publicadora")}
              required
            />
          </label>

          <label className="campo">
            <span>Licenciamiento</span>
            <input
              value={formulario.licenciamiento}
              onChange={cambiar("licenciamiento")}
              required
            />
          </label>

          <label className="campo campo--ancho">
            <span>Tipo de material</span>
            <select value={formulario.tipo} onChange={cambiar("tipo")}>
              <option value="lexicografico">
                Lexicográfico — diccionario, se segmenta por entrada
              </option>
              <option value="prosa">
                Prosa — relatos, gramática, se segmenta por bloques
              </option>
            </select>
          </label>
        </div>

        <div className="formulario__acciones">
          <button type="submit" className="boton boton--principal" disabled={trabajando}>
            {trabajando ? "Procesando…" : "Incorporar al corpus"}
          </button>
          <button type="button" className="boton" onClick={reconstruir} disabled={trabajando}>
            Reconstruir índice
          </button>
        </div>
      </form>

      {resultado && (
        <div className="ingesta">
          <h3 className="ingesta__titulo">{resultado.titulo}</h3>
          <p className="ingesta__dato">
            {resultado.paginas_con_texto} de {resultado.paginas_totales} páginas con capa de
            texto ({(resultado.cobertura_extraccion * 100).toFixed(1)} %)
          </p>
          <p className="ingesta__dato">
            {resultado.fragmentos_generados} fragmentos generados ·{" "}
            {resultado.fragmentos_nuevos} incorporados · {resultado.total_indexado} en el
            índice
          </p>
          {resultado.aviso && <p className="ingesta__aviso">{resultado.aviso}</p>}
        </div>
      )}

      <h3 className="fuentes__titulo">
        Documentos indexados ({corpus.total_fragmentos.toLocaleString("es-PE")} fragmentos)
      </h3>
      <ul className="fuentes__lista">
        {corpus.documentos.map((documento) => (
          <li key={documento} className="fuente">
            <div className="fuente__datos">
              <p className="fuente__meta fuente__meta--principal">{documento}</p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
