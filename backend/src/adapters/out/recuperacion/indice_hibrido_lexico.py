import re
from collections import defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from application.ports.out.indice_recuperacion_port import IndiceRecuperacionPort
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.services.depurador_consulta import DepuradorConsulta
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud

# Lema de una entrada lexicografica: la parte en mayusculas que precede a los dos puntos,
# como en "PERRO: Allqu, ashuti." Un mismo fragmento puede contener mas de una entrada.
PATRON_LEMA = re.compile(r"([A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s\-]*?)\s*:")


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
        self._vec_palabras = TfidfVectorizer(
            analyzer="word", token_pattern=r"(?u)\b\w+\b"
        )
        self._vec_caracteres = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
        self._fragmentos: list[Fragmento] = []
        self._matriz_palabras = None
        self._matriz_caracteres = None
        self._lemario: dict[str, list[int]] = {}

    def indexar(self, fragmentos: list[Fragmento]) -> int:
        if not fragmentos:
            raise ValueError("No se puede construir un indice vacio")
        self._fragmentos = list(fragmentos)
        textos = [self._depurador.normalizar(f.texto) for f in self._fragmentos]
        self._matriz_palabras = self._vec_palabras.fit_transform(textos)
        self._matriz_caracteres = self._vec_caracteres.fit_transform(textos)
        self._lemario = self._construir_lemario()
        return len(self._fragmentos)

    def _construir_lemario(self) -> dict[str, list[int]]:
        lemario: dict[str, list[int]] = defaultdict(list)
        for posicion, fragmento in enumerate(self._fragmentos):
            if fragmento.tipo is not TipoFragmento.LEXICOGRAFICO:
                continue
            for lema in PATRON_LEMA.findall(fragmento.texto):
                normalizado = self._depurador.normalizar(lema).strip()
                if normalizado:
                    lemario[normalizado].append(posicion)
        return dict(lemario)

    def recuperar(self, consulta: str, k: int = 5) -> list[FragmentoRecuperado]:
        if self._matriz_palabras is None:
            raise RuntimeError("El indice no ha sido construido; invoque indexar() primero")

        puntuaciones = self.puntuar(consulta)
        k = min(k, len(self._fragmentos))
        mejores = np.argpartition(-puntuaciones, k - 1)[:k]
        mejores = mejores[np.argsort(-puntuaciones[mejores])]

        por_lema = self._lemario.get(self._depurador.depurar(consulta), [])
        # Las entradas cuyo lema coincide encabezan el resultado aunque su similitud quede
        # por debajo del umbral: un termino frecuente en el corpus recibe un IDF bajo y su
        # propia entrada de diccionario puede no alcanzarlo (caso medido: "perro", 0,271).
        orden = list(dict.fromkeys(list(por_lema) + [int(i) for i in mejores]))[:k]

        return [
            FragmentoRecuperado(
                fragmento=self._fragmentos[i],
                puntuacion=PuntuacionSimilitud(float(puntuaciones[i])),
                coincidencia_lema=i in por_lema,
            )
            for i in orden
        ]

    def puntuar(self, consulta: str) -> np.ndarray:
        """Puntuacion E4 de la consulta frente a todo el indice. Expuesto aparte de
        recuperar() porque el barrido de calibracion del umbral necesita el vector completo."""
        depurada = self._depurador.depurar(consulta)
        vector_palabras = self._vec_palabras.transform([depurada])
        vector_caracteres = self._vec_caracteres.transform([depurada])

        # TfidfVectorizer normaliza L2 por defecto, de modo que el producto punto es el coseno.
        similitud_palabras = (self._matriz_palabras @ vector_palabras.T).toarray().ravel()
        similitud_caracteres = (
            (self._matriz_caracteres @ vector_caracteres.T).toarray().ravel()
        )
        return np.clip((similitud_palabras + similitud_caracteres) / 2.0, 0.0, 1.0)

    def total_indexado(self) -> int:
        return len(self._fragmentos)

    def recuperar_prosa(self, consulta: str, k: int = 3) -> list[FragmentoRecuperado]:
        if self._matriz_palabras is None:
            raise RuntimeError("El indice no ha sido construido; invoque indexar() primero")

        posiciones = [
            i
            for i, f in enumerate(self._fragmentos)
            if f.tipo is not TipoFragmento.LEXICOGRAFICO
        ]
        if not posiciones:
            return []

        puntuaciones = self.puntuar(consulta)
        posiciones.sort(key=lambda i: -puntuaciones[i])
        return [
            FragmentoRecuperado(
                fragmento=self._fragmentos[i],
                puntuacion=PuntuacionSimilitud(float(puntuaciones[i])),
                coincidencia_lema=False,
            )
            for i in posiciones[:k]
        ]

    def proporcion_fuera_de_vocabulario(self, consulta: str) -> float:
        terminos = re.findall(r"\w+", self._depurador.depurar(consulta))
        if not terminos or self._matriz_palabras is None:
            return 0.0
        vocabulario = self._vec_palabras.vocabulary_
        return sum(t not in vocabulario for t in terminos) / len(terminos)

    def es_lema(self, termino: str) -> bool:
        return self._depurador.depurar(termino) in self._lemario
