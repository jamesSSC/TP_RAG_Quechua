// S14-01: lo que muestran «Fuentes del corpus» e «Incorporar documentos» mientras la API no confirmó
// el modo de escritura (arranque en frío de la nube) o si /api/estado falló. Sin formularios ni
// botones de gestión: la web bloquea por defecto y desbloquea solo con confirmación explícita.
export default function GestionPendiente({ conectando, onReintentar }) {
  return (
    <section className="solo-lectura" data-testid="gestion-pendiente">
      <h2>Gestión del corpus</h2>
      {conectando ? (
        <output>
          <span className="giro" aria-hidden="true" /> Conectando con el servicio… la gestión se
          habilita cuando la API confirma el modo.
        </output>
      ) : (
        <>
          <p role="alert">
            No se pudo confirmar el modo del servicio; la gestión queda bloqueada.
          </p>
          <button type="button" className="error__reintentar" onClick={onReintentar}>
            Reintentar
          </button>
        </>
      )}
    </section>
  );
}
