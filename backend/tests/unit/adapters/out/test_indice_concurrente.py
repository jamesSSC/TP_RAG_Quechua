"""Una consulta que llega mientras se reconstruye el indice no debe fallar (hallazgo del E2E)."""

import threading

import pytest

from adapters.out.recuperacion.indice_hibrido_lexico import IndiceHibridoLexico
from domain.entities.fragmento import Fragmento, TipoFragmento
from domain.value_objects.procedencia import Procedencia

DOC = "293274822-diccionario-quechua-Wanka-docx.pdf"


def _corpus(sufijo: str, n: int = 400) -> list[Fragmento]:
    base = [
        Fragmento("zorro-37", "ZORRO: Atuq.", Procedencia(DOC, 37), TipoFragmento.LEXICOGRAFICO),
        Fragmento("puklu-9", "CÓNCAVO: Puklu.", Procedencia(DOC, 9), TipoFragmento.LEXICOGRAFICO),
    ]
    relleno = [
        Fragmento(
            f"{sufijo}-{i}",
            f"ENTRADA{sufijo}{i}: Texto de relleno {i}.",
            Procedencia(DOC, 1 + i % 30),
            TipoFragmento.LEXICOGRAFICO,
        )
        for i in range(n)
    ]
    return base + relleno


@pytest.mark.salvaguarda
def test_consultar_mientras_se_reindexa_nunca_falla_ni_cita_sin_documento():
    indice = IndiceHibridoLexico()
    indice.indexar(_corpus("a"))
    errores: list[Exception] = []
    sin_cita: list = []
    parar = threading.Event()

    def consultar():
        while not parar.is_set():
            try:
                recuperados = indice.recuperar("zorro", k=3)
                indice.recuperar_prosa("zorro")
                indice.es_lema("zorro")
                indice.proporcion_fuera_de_vocabulario("zorro")
            except Exception as exc:  # noqa: BLE001
                errores.append(exc)
                return
            sin_cita.extend(
                r
                for r in recuperados
                if not (r.fragmento.procedencia.documento and r.fragmento.procedencia.pagina)
            )

    hilos = [threading.Thread(target=consultar) for _ in range(4)]
    for h in hilos:
        h.start()
    for i in range(25):
        indice.indexar(_corpus("b" if i % 2 else "a", n=300 + i))
    parar.set()
    for h in hilos:
        h.join()
    assert errores == [], f"fallo durante la reconstruccion: {errores[:1]}"
    assert sin_cita == []


def test_el_estado_se_publica_de_una_vez():
    indice = IndiceHibridoLexico()
    indice.indexar(_corpus("a", n=10))
    antes = indice.total_indexado()
    indice.indexar(_corpus("b", n=50))
    assert indice.total_indexado() == antes + 40
    assert indice.es_lema("zorro")
