from abc import ABC, abstractmethod

from domain.entities.fragmento import Fragmento, FragmentoRecuperado


class IndiceRecuperacionPort(ABC):
    """Sustituye al IndiceVectorialPort previsto en el Documento 0: la prueba de concepto
    determino que sobre este corpus la recuperacion lexica supera a la densa, de modo que
    el puerto se define sobre la operacion (recuperar) y no sobre la tecnica (vectorial)."""

    @abstractmethod
    def indexar(self, fragmentos: list[Fragmento]) -> int:
        """Construye el indice y devuelve el numero de fragmentos indexados."""

    @abstractmethod
    def recuperar(self, consulta: str, k: int = 5) -> list[FragmentoRecuperado]:
        """Devuelve los k fragmentos mas similares, ordenados de mayor a menor puntuacion."""

    @abstractmethod
    def total_indexado(self) -> int: ...

    @abstractmethod
    def es_lema(self, termino: str) -> bool:
        """El termino encabeza alguna entrada lexicografica del corpus.

        Permite distinguir una palabra espanola documentada de una inglesa suelta sin
        recurrir a la heuristica de palabras funcionales, que sobre un termino aislado
        no tiene ninguna marca que contar."""

    def recuperar_prosa(self, consulta: str, k: int = 3) -> list[FragmentoRecuperado]:
        """Los k pasajes de prosa mas similares, al margen de las entradas de diccionario.

        Se consulta por separado porque las entradas lexicograficas, al ser mucho mas
        cortas, copan siempre las primeras posiciones y un pasaje de gramatica nunca
        llegaria a mostrarse. No es abstracto: un indice que no distinga tipos puede no
        ofrecer prosa sin dejar de cumplir el puerto."""
        return []

    def proporcion_fuera_de_vocabulario(self, consulta: str) -> float:
        """Parte de los terminos de la consulta depurada que no aparece en ningun fragmento.

        Es una de las senales de los modelos predictivos del PMV2: "criptomoneda" no
        figura en el corpus y "perro" si. No es abstracto por la misma razon que
        recuperar_prosa: un indice que no la calcule devuelve 0 y el predictor la ignora."""
        return 0.0
