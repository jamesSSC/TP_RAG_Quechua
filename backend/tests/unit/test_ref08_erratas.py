"""REF-08 (ADR-041): tolerancia a erratas en la consulta en español, nunca en formas quechuas.

El sistema propone «¿quiso escribir…?» tras una abstención y no cambia nada más: la abstención,
τ, RN-06 y la respuesta quedan igual.
"""

import pytest

from adapters.out.recuperacion.indice_hibrido_lexico import IndiceHibridoLexico
from domain.entities.fragmento import Fragmento, TipoFragmento
from domain.services.sugerencia_errata import distancia, parece_quechua, sugerir
from domain.value_objects.procedencia import Procedencia

LEMAS = {"zorro": 2, "oro": 5, "perro": 3, "cerro": 1, "mujer": 4, "corazon": 2, "arco iris": 1}
VOCABULARIO = {"atuq", "allqu", "caza", "zorro", "perro"}


@pytest.mark.parametrize(
    ("a", "b", "esperada"),
    [("zoro", "zorro", 1), ("mujr", "mujer", 1), ("perrro", "perro", 1), ("ozrro", "zorro", 1),
     ("criptomoneda", "corazon", 3)],
)
def test_distancia_con_transposiciones(a, b, esperada):
    assert distancia(a, b, tope=2) == min(esperada, 3)


def test_sugiere_lemas_castellanos_a_una_letra():
    assert sugerir("zoro", LEMAS, VOCABULARIO)[0] == "zorro"  # misma primera letra antes que «oro»
    assert sugerir("mujr", LEMAS, VOCABULARIO) == ["mujer"]
    assert sugerir("perrro", LEMAS, VOCABULARIO)[:2] == ["perro", "cerro"]


@pytest.mark.parametrize(
    "termino",
    [
        "zorro",  # ya es lema
        "caza",  # palabra del corpus: no es una errata
        "atuk",  # ortografía quechua (k)
        "wasi",  # ortografía quechua (w)
        "qasa",  # q sin u: quechua
        "allqu",  # forma quechua presente en el corpus
        "oso",  # demasiado corta
        "criptomoneda",  # nada cerca: se abstiene sin sugerencia
        "arco iris",  # solo términos de una palabra
    ],
)
def test_no_sugiere(termino):
    assert sugerir(termino, LEMAS, VOCABULARIO) == []


def test_nunca_propone_una_forma_quechua():
    """Las propuestas salen solo de los lemas castellanos, no del cuerpo de las entradas."""
    indice = IndiceHibridoLexico()
    indice.indexar(
        [
            Fragmento(
                id="z",
                texto="ZORRO: Atuq.",
                procedencia=Procedencia("dic.pdf", 37),
                tipo=TipoFragmento.LEXICOGRAFICO,
            ),
            Fragmento(
                id="p",
                texto="PERRO: Allqu.",
                procedencia=Procedencia("dic.pdf", 40),
                tipo=TipoFragmento.LEXICOGRAFICO,
            ),
        ]
    )
    assert indice.lemas_parecidos("¿cómo se dice zoro?") == ["zorro"]
    # «atuqq» está a una letra de la forma quechua «atuq», pero no se corrige hacia ella.
    assert indice.lemas_parecidos("¿qué significa atuqq?") == []
    assert indice.lemas_parecidos("¿cómo se dice perr?") == ["perro"]


def test_parece_quechua():
    assert parece_quechua("atuq") and parece_quechua("wasi") and parece_quechua("kay")
    assert not parece_quechua("queso") and not parece_quechua("zorro")


# --- De punta a punta en el caso de uso: la propuesta no cambia la decisión --------------------


def _caso_de_uso():
    from adapters.out.generacion.generador_literal import GeneradorLiteral
    from adapters.out.idioma.detector_idioma_heuristico import DetectorIdiomaHeuristico
    from application.use_cases.consultar_corpus import ConsultarCorpusUseCase
    from domain.services.evaluador_confianza import EvaluadorConfianza

    indice = IndiceHibridoLexico()
    indice.indexar(
        [
            Fragmento(
                id=f"e{i}",
                texto=texto,
                procedencia=Procedencia("dic.pdf", i),
                tipo=TipoFragmento.LEXICOGRAFICO,
            )
            for i, texto in enumerate(
                ["ZORRO: Atuq.", "PERRO: Allqu.", "MUJER: Warmi.", "CASA: Wasi."], start=1
            )
        ]
    )
    return ConsultarCorpusUseCase(
        indice, GeneradorLiteral(), EvaluadorConfianza(0.48), DetectorIdiomaHeuristico()
    )


@pytest.mark.salvaguarda
def test_con_errata_se_abstiene_igual_y_propone_la_consulta_corregida():
    caso = _caso_de_uso()
    r = caso.ejecutar("¿cómo se dice zoro en quechua wanka?")
    assert r.abstenida and r.respaldo == []
    assert r.sugerencias[0] == {
        "termino": "zorro",
        "consulta": "¿cómo se dice zorro en quechua wanka?",
    }
    # Seguir la propuesta es otra consulta, que pasa por τ y el lema como cualquiera.
    corregida = caso.ejecutar(r.sugerencias[0]["consulta"])
    assert not corregida.abstenida
    assert corregida.respaldo[0].procedencia.pagina == 1


@pytest.mark.salvaguarda
@pytest.mark.parametrize(
    "consulta",
    [
        "¿cómo se dice zorro en quechua wanka?",  # respondida: nada que proponer
        "¿cómo se dice criptomoneda en quechua wanka?",  # fuera de cobertura y sin vecinos
        "¿qué significa atuqq?",  # quechua: nunca se corrige
        "how do you say fox",  # en inglés no se proponen lemas castellanos
    ],
)
def test_sin_sugerencias(consulta):
    assert _caso_de_uso().ejecutar(consulta).sugerencias == []
