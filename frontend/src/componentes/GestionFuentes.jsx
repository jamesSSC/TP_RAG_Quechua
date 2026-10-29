import { useEffect, useState } from "react";

import {
  actualizarFuente,
  crearFuente,
  eliminarFuente,
  listarFuentes,
} from "../api";

const VACIA = {
  titulo: "",
  entidad_publicadora: "",
  licenciamiento: "",
  fecha_extraccion: new Date().toISOString().slice(0, 10),
  nombre_archivo: "",
  paginas_totales: 0,
  paginas_con_texto: 0,
  derivado_ocr: false,
};

const NUMERICOS = new Set(["paginas_totales", "paginas_con_texto"]);

export default function GestionFuentes() {
  const [fuentes, setFuentes] = useState([]);
  const [formulario, setFormulario] = useState(VACIA);
  const [editando, setEditando] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(true);

  const recargar = () => {
    setCargando(true);
    listarFuentes()
      .then(setFuentes)
      .catch((e) => setError(e.message))
      .finally(() => setCargando(false));
  };

  useEffect(recargar, []);

  const cambiar = (campo) => (evento) => {
    let valor = evento.target.value;
    if (NUMERICOS.has(campo)) valor = Number(valor);
    else if (campo === "derivado_ocr") valor = evento.target.checked;
    setFormulario((previo) => ({ ...previo, [campo]: valor }));
  };

  const cancelar = () => {
    setFormulario(VACIA);
    setEditando(null);
    setError(null);
  };

  const guardar = async (evento) => {
    evento.preventDefault();
    setError(null);
    try {
      if (editando) await actualizarFuente(editando, formulario);
      else await crearFuente(formulario);
      cancelar();
      recargar();
    } catch (e) {
      setError(e.message);
    }
  };

  const editar = (fuente) => {
    const { id, cobertura_extraccion, ...datos } = fuente;
    setFormulario(datos);
    setEditando(id);
    setError(null);
  };

  const borrar = async (id) => {
    setError(null);
    try {
      await eliminarFuente(id);
      if (editando === id) cancelar();
      recargar();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <section className="fuentes">
      <h2 className="fuentes__titulo">Fuentes del corpus</h2>
      <p className="fuentes__intro">
        Cada documento indexado queda registrado con su procedencia, su fecha de extracción
        y sus condiciones de licenciamiento. Una fuente sin licenciamiento declarado no se
        acepta.
      </p>

      {error && <p className="error">{error}</p>}

      <form className="formulario" onSubmit={guardar}>
        <h3 className="formulario__titulo">
          {editando ? "Editar fuente" : "Registrar nueva fuente"}
        </h3>

        <div className="formulario__rejilla">
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
            <span>Nombre del archivo</span>
            <input
              value={formulario.nombre_archivo}
              onChange={cambiar("nombre_archivo")}
              required
            />
          </label>

          <label className="campo">
            <span>Fecha de extracción</span>
            <input
              type="date"
              value={formulario.fecha_extraccion}
              onChange={cambiar("fecha_extraccion")}
              required
            />
          </label>

          <label className="campo">
            <span>Páginas totales</span>
            <input
              type="number"
              min="0"
              value={formulario.paginas_totales}
              onChange={cambiar("paginas_totales")}
            />
          </label>

          <label className="campo">
            <span>Páginas con texto</span>
            <input
              type="number"
              min="0"
              value={formulario.paginas_con_texto}
              onChange={cambiar("paginas_con_texto")}
            />
          </label>

          <label className="campo campo--casilla">
            <input
              type="checkbox"
              checked={formulario.derivado_ocr}
              onChange={cambiar("derivado_ocr")}
            />
            <span>Texto derivado de OCR</span>
          </label>
        </div>

        <div className="formulario__acciones">
          <button type="submit" className="boton boton--principal">
            {editando ? "Guardar cambios" : "Registrar fuente"}
          </button>
          {editando && (
            <button type="button" className="boton" onClick={cancelar}>
              Cancelar
            </button>
          )}
        </div>
      </form>

      {cargando && <p className="cargando">Cargando fuentes…</p>}
      {!cargando && fuentes.length === 0 && (
        <p className="fuentes__vacio">Todavía no hay fuentes registradas.</p>
      )}
      {!cargando && fuentes.length > 0 && (
        <ul className="fuentes__lista">
          {fuentes.map((f) => (
            <li key={f.id} className="fuente">
              <div className="fuente__datos">
                <h4 className="fuente__titulo">{f.titulo}</h4>
                <p className="fuente__meta">
                  {f.entidad_publicadora} · {f.licenciamiento}
                </p>
                <p className="fuente__meta">
                  {f.nombre_archivo} · extraído el {f.fecha_extraccion} ·{" "}
                  {f.paginas_con_texto}/{f.paginas_totales} páginas con texto
                  {f.paginas_totales > 0 &&
                    ` (${(f.cobertura_extraccion * 100).toFixed(1)} %)`}
                  {f.derivado_ocr && " · OCR"}
                </p>
              </div>
              <div className="fuente__acciones">
                <button className="boton" onClick={() => editar(f)}>
                  Editar
                </button>
                <button className="boton boton--peligro" onClick={() => borrar(f.id)}>
                  Eliminar
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
