import hashlib
import re

from domain.entities.documento_extraido import DocumentoExtraido
from domain.entities.fragmento import Fragmento, TipoFragmento
from domain.value_objects.procedencia import Procedencia

# Inicio de una entrada de diccionario: lema en mayusculas seguido de dos puntos.
INICIO_ENTRADA = re.compile(r"(?=(?:^|\s)([A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s\-]{1,40}:))")

TAMANO_BLOQUE = 900
SOLAPE = 120


class Segmentador:
    """Divide el texto extraido segun el tipo de documento.

    Esta es la decision de ingenieria con mas peso en el resultado del sistema. El
    experimento E6 de la prueba de concepto midio que aislar cada entrada del diccionario en
    su propio fragmento, en lugar de trocear el material en bloques uniformes, eleva el
    recall en el punto de operacion del 48,3 % al 85,6 % y triplica la ventana util del
    umbral. Ninguna biblioteca de recuperacion lo resuelve por defecto."""

    def segmentar(
        self, documento: DocumentoExtraido, tipo: TipoFragmento, derivado_ocr: bool = False
    ) -> list[Fragmento]:
        fragmentos = []
        for pagina in documento.paginas:
            if not pagina.tiene_texto:
                continue
            procedencia = Procedencia(
                documento=documento.nombre_archivo,
                pagina=pagina.numero,
                derivado_ocr=derivado_ocr,
            )
            textos = (
                self._por_entrada(pagina.texto)
                if tipo is TipoFragmento.LEXICOGRAFICO
                else self._por_bloques(pagina.texto)
            )
            for texto in textos:
                fragmentos.append(
                    Fragmento(
                        id=self._identificador(documento.nombre_archivo, pagina.numero, texto),
                        texto=texto,
                        procedencia=procedencia,
                        tipo=tipo,
                    )
                )
        return fragmentos

    @staticmethod
    def _por_entrada(texto: str) -> list[str]:
        cortes = [m.start() for m in INICIO_ENTRADA.finditer(texto)]
        if not cortes:
            return Segmentador._por_bloques(texto)

        limites = cortes + [len(texto)]
        entradas = []
        for inicio, fin in zip(limites, limites[1:], strict=False):
            entrada = texto[inicio:fin].strip()
            if entrada:
                entradas.append(entrada)
        return entradas

    @staticmethod
    def _por_bloques(texto: str) -> list[str]:
        limpio = re.sub(r"\s+", " ", texto).strip()
        if len(limpio) <= TAMANO_BLOQUE:
            return [limpio] if limpio else []

        bloques = []
        inicio = 0
        while inicio < len(limpio):
            fin = min(inicio + TAMANO_BLOQUE, len(limpio))
            if fin < len(limpio):
                # Se corta en el ultimo punto o espacio del bloque para no partir palabras.
                corte = max(limpio.rfind(". ", inicio, fin), limpio.rfind(" ", inicio, fin))
                if corte > inicio:
                    fin = corte + 1
            bloque = limpio[inicio:fin].strip()
            if bloque:
                bloques.append(bloque)
            if fin >= len(limpio):
                break
            inicio = max(fin - SOLAPE, inicio + 1)
        return bloques

    @staticmethod
    def _identificador(documento: str, pagina: int, texto: str) -> str:
        semilla = f"{documento}|{pagina}|{texto}".encode()
        return hashlib.sha256(semilla).hexdigest()[:12]
