"""P1-B11 · Mide la fidelidad de la redaccion de Qwen frente a la glosa del fragmento literal.

Regla declarada ANTES de medir (docs/evidencias/cierre_u3/b11_fidelidad/regla_declarada.md):

  Glosa en espanol del fragmento = lo que precede a los dos puntos de cada entrada (el lema
  castellano). Formas quechuas = lo que sigue a los dos puntos. Una redaccion tiene
  CONTRADICCION POTENCIAL si, tras quitar las formas quechuas del fragmento, contiene al menos una
  palabra de contenido en espanol (4 o mas letras, no funcional ni metalinguistica) que NO figura
  en la glosa ni en la consulta. Una palabra "figura" si coincide con otra por sus primeros 5
  caracteres (o completa si es mas corta), lo que tolera flexiones. Es una cota superior
  conservadora del riesgo: marca a revisar, no prueba un error.

Ademas se cuentan las respuestas CORTADAS (done_reason == "length" de Ollama) y la latencia.
La evidencia solo lleva ids y banderas: nunca la redaccion ni el fragmento.

Uso, desde backend/ (con Ollama y qwen3.5:4b):
    python scripts/medir_fidelidad.py <carpeta_salida> [--n 120] [--mitigada]
"""

import json
import re
import statistics
import sys
import time
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

TOKEN = re.compile(r"[a-zñ]+")

# Palabras funcionales y metalinguisticas que cualquier redaccion correcta puede usar.
FUNCIONALES = set(
    """
    el la los las un una unos unas de del al en con por para como que se es son fue era ser
    esta este esto estos estas esa ese eso ello y o u e ni pero sino mas muy mismo misma lo
    le les su sus tu tus mi mis segun entre sobre desde hasta hacia donde cuando cual cuales
    quien quienes tambien solo solamente ademas asi aqui alli ahi si no ya aun todo toda
    todos todas cada otra otro otras otros dice dicen decir dijo significa significan
    significar corresponde corresponden equivale equivalen aparece aparecen figura figuran
    registra registran indica indican consta constan menciona recoge recogen ofrece ofrecen
    presenta presentan existe existen hay habia puede pueden forma formas palabra palabras
    termino terminos expresion voz vocablo entrada entradas diccionario documento fragmento
    fragmentos texto pagina fuente fuentes citado citada quechua wanka huanca junin variedad
    lengua idioma castellano espanol llama llaman llamado llamada denomina denominan nombre
    nombres literal literalmente exactamente directamente siguiente siguientes traduccion
    equivalente equivalentes sentido contexto uso usa usan utiliza utilizan
    """.split()
)


def _norm(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _tokens(texto: str) -> list[str]:
    return TOKEN.findall(_norm(texto))


def _raiz(token: str) -> str:
    return token[:5]


def separar_glosa_y_formas(fragmentos: list[str]) -> tuple[set[str], set[str]]:
    """Glosa (antes de ':') y formas quechuas (despues de ':') de las entradas del fragmento."""
    glosa: set[str] = set()
    formas: set[str] = set()
    for texto in fragmentos:
        for entrada in re.split(r"\n", texto):
            if ":" in entrada:
                lema, _, resto = entrada.partition(":")
                glosa.update(_tokens(lema))
                formas.update(_tokens(resto))
            else:
                glosa.update(_tokens(entrada))
    formas -= glosa  # una palabra que es a la vez lema y forma cuenta como glosa
    return glosa, formas


def evaluar_fidelidad(redaccion: str, consulta: str, fragmentos: list[str]) -> dict:
    """Devuelve banderas y conteos; nunca texto."""
    glosa, formas = separar_glosa_y_formas(fragmentos)
    permitidas = glosa | set(_tokens(consulta)) | FUNCIONALES
    raices = {_raiz(t) for t in permitidas}
    extranas = [
        t
        for t in _tokens(redaccion)
        if len(t) >= 4 and t not in formas and t not in permitidas and _raiz(t) not in raices
    ]
    return {
        "palabras_extranas": len(extranas),
        "contradiccion_potencial": bool(extranas),
        "forma_quechua_presente": any(t in formas for t in _tokens(redaccion)),
    }


# --- Medicion (necesita Ollama y el corpus) ---


def _instalar_espia_de_ollama(registro: list[dict]):
    import httpx

    original = httpx.post

    def espia(url, *args, **kwargs):
        respuesta = original(url, *args, **kwargs)
        if str(url).endswith("/api/generate") and kwargs.get("json", {}).get("prompt") != "ok":
            try:
                cuerpo = respuesta.json()
                registro.append(
                    {
                        "done_reason": cuerpo.get("done_reason"),
                        "eval_count": cuerpo.get("eval_count"),
                    }
                )
            except ValueError:
                registro.append({"done_reason": None, "eval_count": None})
        return respuesta

    httpx.post = espia


def main(salida: Path, n: int, mitigada: bool) -> None:
    import os
    import tempfile

    # Base temporal: nunca la real.
    os.environ["RUTA_SQLITE"] = str(Path(tempfile.mkdtemp(prefix="qw_fid_")) / "fidelidad.db")
    os.environ["ORIGEN_CONSULTAS"] = "arnes"
    from infrastructure.contenedor import Contenedor

    razones: list[dict] = []
    _instalar_espia_de_ollama(razones)
    c = Contenedor(generador="ollama")
    if not c.generador.disponible():
        raise SystemExit("Ollama o qwen3.5:4b no responden")
    c.generador.precalentar()

    consultas = [
        e
        for e in json.loads((RAIZ / "data" / "evaluacion_v2.json").read_text(encoding="utf-8"))
        if e["subconjunto"].startswith("A")
    ][:n]
    filas = []
    for e in consultas:
        antes = len(razones)
        t0 = time.perf_counter()
        r = c.consultar_corpus.ejecutar(e["consulta"])
        ms = (time.perf_counter() - t0) * 1000
        fila = {
            "id": e["id"],
            "abstenida": r.abstenida,
            "generador_invocado": r.generador_invocado,
            "aviso_generacion": bool(r.aviso_generacion),
            "latencia_ms": round(ms),
            "done_reason": razones[antes]["done_reason"] if len(razones) > antes else None,
            "tokens": razones[antes]["eval_count"] if len(razones) > antes else None,
        }
        if not r.abstenida and r.generador_invocado:
            fila.update(evaluar_fidelidad(r.texto, e["consulta"], [f.texto for f in r.respaldo]))
            fila["longitud_redaccion"] = len(r.texto)
            fila["es_fragmento_literal"] = r.texto.startswith(r.respaldo[0].texto)
        filas.append(fila)

    salida.mkdir(parents=True, exist_ok=True)
    con_modelo = [f for f in filas if "contradiccion_potencial" in f]
    lat = sorted(f["latencia_ms"] for f in filas)
    p95 = lat[int(0.95 * (len(lat) - 1))] if lat else None
    resumen = {
        "consultas": len(filas),
        "respuestas_redactadas": len(con_modelo),
        "con_aviso_de_generacion": sum(f["aviso_generacion"] for f in filas),
        "contradiccion_potencial": sum(f["contradiccion_potencial"] for f in con_modelo),
        "contradiccion_potencial_pct": round(
            100 * sum(f["contradiccion_potencial"] for f in con_modelo) / max(1, len(con_modelo)), 1
        ),
        "cortadas_done_reason_length": sum(1 for f in filas if f["done_reason"] == "length"),
        "cortadas_pct": round(
            100 * sum(1 for f in filas if f["done_reason"] == "length") / max(1, len(filas)), 1
        ),
        "tokens_maximos": max((f["tokens"] or 0) for f in filas),
        "latencia_ms": {
            "media": round(statistics.mean(lat)),
            "p50": lat[len(lat) // 2],
            "p95": p95,
            "max": lat[-1],
        },
        "mitigacion_adr_028": mitigada,
        "extracciones_aceptadas": getattr(c.generador, "aceptadas", None),
        "extracciones_descartadas": getattr(c.generador, "descartadas", None),
    }
    (salida / "fidelidad_por_consulta.json").write_text(
        json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (salida / "resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(resumen, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    carpeta = Path(sys.argv[1])
    cuantas = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 120
    main(carpeta, cuantas, "--mitigada" in sys.argv)
