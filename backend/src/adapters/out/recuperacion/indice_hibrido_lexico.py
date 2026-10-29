import re
from collections import defaultdict
from typing import NamedTuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from application.ports.out.indice_recuperacion_port import IndiceRecuperacionPort
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.services.depurador_consulta import DepuradorConsulta
from domain.services.entradas_lexicas import PATRON_LEMA
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud

SIN_INDICE = "El indice no ha sido construido; invoque indexar() primero"


class _Estado(NamedTuple):
    """Todo lo que define un indice construido. Se publica de una vez (una sola asignacion), de
    modo que una consulta que llega mientras se reconstruye ve el indice anterior completo o el
    nuevo completo, nunca una mezcla ni vectorizadores a medio ajustar."""

    fragmentos: list
    vec_palabras: TfidfVectorizer
    vec_caracteres: TfidfVectorizer
    matriz_palabras: object
    matriz_caracteres: object
    lemario: dict


class IndiceHibridoLexico(IndiceRecuperacionPort):
    """Estrategia E4 de la prueba de concepto: promedio con igual peso de la coincidencia
    de palabras completas (E2) y la de secuencias de 3 a 5 caracteres (E3), ambas medidas
    como coseno sobre representaciones TF-IDF.

    El promedio no es una eleccion de conveniencia. E3 nunca devuelve cero porque siempre
    hay algun fragmento con el que compartir trigramas, y ese ruido de fondo elevaria el
    umbral necesario para distinguir lo respaldado de lo que no lo esta; E2 arrastra esas
    coincidencias espurias hacia cero y ensancha la separacion entre ambos casos."""

    def __init__(self, depurador: DepuradorConsulta | None = None):
        self._depurador = depurador or DepuradorConsulta()
        self._estado: _Estado | None = None

    # Lectura del estado actual (los scripts de calibracion y de exportacion los usan).
    @property
    def _fragmentos(self) -> list[Fragmento]:
        return self._estado.fragmentos if self._estado else []

    @property
    def _lemario(self) -> dict[str, list[int]]:
        return self._estado.lemario if self._estado else {}

    @property
    def _vec_palabras(self) -> TfidfVectorizer | None:
        return self._estado.vec_palabras if self._estado else None

    @property
    def _vec_caracteres(self) -> TfidfVectorizer | None:
        return self._estado.vec_caracteres if self._estado else None

    @property
    def _matriz_palabras(self):
        return self._estado.matriz_palabras if self._estado else None

    @property
    def _matriz_caracteres(self):
        return self._estado.matriz_caracteres if self._estado else None

    def indexar(self, fragmentos: list[Fragmento]) -> int:
        if not fragmentos:
            raise ValueError("No se puede construir un indice vacio")
        lista = list(fragmentos)
        textos = [self._depurador.normalizar(f.texto) for f in lista]
        # Vectorizadores nuevos: los del indice en uso no se tocan mientras se construye otro.
        vec_palabras = TfidfVectorizer(analyzer="word", token_pattern=r"(?u)\b\w+\b")
        vec_caracteres = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
        matriz_palabras = vec_palabras.fit_transform(textos)
        matriz_caracteres = vec_caracteres.fit_transform(textos)
        lemario = self._construir_lemario(lista)
        self._estado = _Estado(
            lista, vec_palabras, vec_caracteres, matriz_palabras, matriz_caracteres, lemario
        )
        return len(lista)

    def _construir_lemario(self, fragmentos: list[Fragmento]) -> dict[str, list[int]]:
        lemario: dict[str, list[int]] = defaultdict(list)
        for posicion, fragmento in enumerate(fragmentos):
            if fragmento.tipo is not TipoFragmento.LEXICOGRAFICO:
                continue
            for lema in PATRON_LEMA.findall(fragmento.texto):
                normalizado = self._depurador.normalizar(lema).strip()
                if normalizado:
                    lemario[normalizado].append(posicion)
        return dict(lemario)

    def recuperar(self, consulta: str, k: int = 5) -> list[FragmentoRecuperado]:
        e = self._estado
        if e is None:
            raise RuntimeError(SIN_INDICE)

        puntuaciones = self._puntuar(e, consulta)
        k = min(k, len(e.fragmentos))
        mejores = np.argpartition(-puntuaciones, k - 1)[:k]
        mejores = mejores[np.argsort(-puntuaciones[mejores])]

        por_lema = e.lemario.get(self._depurador.depurar(consulta), [])
        # Las entradas cuyo lema coincide encabezan el resultado aunque su similitud quede
        # por debajo del umbral: un termino frecuente en el corpus recibe un IDF bajo y su
        # propia entrada de diccionario puede no alcanzarlo (caso medido: "perro", 0,271).
        orden = list(dict.fromkeys(list(por_lema) + [int(i) for i in mejores]))[:k]

        return [
            FragmentoRecuperado(
                fragmento=e.fragmentos[i],
                puntuacion=PuntuacionSimilitud(float(puntuaciones[i])),
                coincidencia_lema=i in por_lema,
            )
            for i in orden
        ]

    def puntuar(self, consulta: str) -> np.ndarray:
        """Puntuacion E4 de la consulta frente a todo el indice. Expuesto aparte de
        recuperar() porque el barrido de calibracion del umbral necesita el vector completo."""
        if self._estado is None:
            raise RuntimeError(SIN_INDICE)
        return self._puntuar(self._estado, consulta)

    def _puntuar(self, e: _Estado, consulta: str) -> np.ndarray:
        depurada = self._depurador.depurar(consulta)
        vector_palabras = e.vec_palabras.transform([depurada])
        vector_caracteres = e.vec_caracteres.transform([depurada])

        # TfidfVectorizer normaliza L2 por defecto, de modo que el producto punto es el coseno.
        similitud_palabras = (e.matriz_palabras @ vector_palabras.T).toarray().ravel()
        similitud_caracteres = (e.matriz_caracteres @ vector_caracteres.T).toarray().ravel()
        return np.clip((similitud_palabras + similitud_caracteres) / 2.0, 0.0, 1.0)

    def total_indexado(self) -> int:
        return len(self._fragmentos)

    def recuperar_prosa(self, consulta: str, k: int = 3) -> list[FragmentoRecuperado]:
        e = self._estado
        if e is None:
            raise RuntimeError(SIN_INDICE)

        posiciones = [
            i for i, f in enumerate(e.fragmentos) if f.tipo is not TipoFragmento.LEXICOGRAFICO
        ]
        if not posiciones:
            return []

        puntuaciones = self._puntuar(e, consulta)
        posiciones.sort(key=lambda i: -puntuaciones[i])
        return [
            FragmentoRecuperado(
                fragmento=e.fragmentos[i],
                puntuacion=PuntuacionSimilitud(float(puntuaciones[i])),
                coincidencia_lema=False,
            )
            for i in posiciones[:k]
        ]

    def proporcion_fuera_de_vocabulario(self, consulta: str) -> float:
        terminos = re.findall(r"\w+", self._depurador.depurar(consulta))
        e = self._estado
        if not terminos or e is None:
            return 0.0
        vocabulario = e.vec_palabras.vocabulary_
        return sum(t not in vocabulario for t in terminos) / len(terminos)

    def es_lema(self, termino: str) -> bool:
        return self._depurador.depurar(termino) in self._lemario
