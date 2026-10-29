"""ADR-032 · Fidelidad de Gemini en la nube, comparable con B11 (Qwen local, cierre U3).

Mismas consultas (las N primeras del subconjunto A de evaluacion_v2.json) y misma regla v2
(`evaluar_fidelidad` de medir_fidelidad.py), pero contra la API publicada: mide lo que ve el
usuario de la nube, incluidos los rechazos del verificador, los 429 de la cuota gratuita y los
tiempos agotados. Las consultas se registran como `humo` (TOKEN_PRUEBAS). La evidencia solo
lleva ids y banderas: nunca la redaccion ni el fragmento.

Uso, desde backend/:
    $env:TOKEN_PRUEBAS="..."; python scripts/medir_gemini_nube.py https://quechua-api.onrender.com
"""

import argparse
import json
import os
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from medir_fidelidad import evaluar_fidelidad  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ.parent / "docs" / "evidencias" / "nube"


def _percentil(valores, p):
    if not valores:
        return None
    v = sorted(valores)
    return v[int(p * (len(v) - 1))]


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("url_api")
    argumentos.add_argument("--n", type=int, default=120)
    argumentos.add_argument("--espera", type=float, default=2.0, help="segundos entre consultas")
    args = argumentos.parse_args()

    consultas = [
        e
        for e in json.loads((RAIZ / "data" / "evaluacion_v2.json").read_text(encoding="utf-8"))
        if e["subconjunto"].startswith("A")
    ][: args.n]
    cabeceras = {"X-Origen-Consultas": "humo"}
    if os.environ.get("TOKEN_PRUEBAS"):
        cabeceras["X-Token-Pruebas"] = os.environ["TOKEN_PRUEBAS"]

    filas = []
    with httpx.Client(base_url=args.url_api.rstrip("/"), headers=cabeceras, timeout=90) as c:
        estado = c.get("/api/estado").json()
        for i, e in enumerate(consultas, 1):
            t0 = time.perf_counter()
            r = c.post("/api/consultas", json={"texto": e["consulta"]})
            ms = round((time.perf_counter() - t0) * 1000)
            fila = {"id": e["id"], "http": r.status_code, "latencia_cliente_ms": ms}
            if r.status_code == 200:
                d = r.json()
                fila.update(
                    {
                        "abstenida": d["abstenida"],
                        "latencia_servidor_ms": d.get("latencia_ms"),
                        "redactado_por": d.get("redactado_por"),
                        "motivo": d.get("motivo_redaccion"),
                    }
                )
                if not d["abstenida"] and d.get("redactado_por") == "gemini":
                    fragmentos = [f["texto"] for f in d["respaldo"]]
                    fila.update(evaluar_fidelidad(d["texto"], e["consulta"], fragmentos))
            filas.append(fila)
            if i % 20 == 0:
                print(f"[GEMINI] {i}/{len(consultas)}", flush=True)
            time.sleep(args.espera)

    afirmativas = [f for f in filas if f.get("abstenida") is False]
    por_gemini = [f for f in afirmativas if f.get("redactado_por") == "gemini"]
    motivos: dict[str, int] = {}
    for f in afirmativas:
        if f.get("redactado_por") != "gemini":
            clave = (f.get("motivo") or "sin motivo").split(" (")[0]
            motivos[clave] = motivos.get(clave, 0) + 1
    latencias = [f["latencia_servidor_ms"] for f in afirmativas if f.get("latencia_servidor_ms")]
    resumen = {
        "url_api": args.url_api,
        "momento_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "modelo": estado.get("modelo"),
        "regla": "v2 (medir_fidelidad.evaluar_fidelidad)",
        "consultas": len(filas),
        "afirmativas": len(afirmativas),
        "redactadas_por_gemini": len(por_gemini),
        "contradiccion_potencial": sum(f["contradiccion_potencial"] for f in por_gemini),
        "contradiccion_potencial_pct": round(
            100 * sum(f["contradiccion_potencial"] for f in por_gemini) / max(1, len(por_gemini)), 1
        ),
        "sustituidas_por_fragmento_literal": len(afirmativas) - len(por_gemini),
        "sustituidas_pct": round(
            100 * (len(afirmativas) - len(por_gemini)) / max(1, len(afirmativas)), 1
        ),
        "motivos_de_sustitucion": motivos,
        "errores_429": sum(1 for f in afirmativas if "429" in (f.get("motivo") or "")),
        "latencia_servidor_ms": {
            "p50": _percentil(latencias, 0.5),
            "p95": _percentil(latencias, 0.95),
            "media": round(statistics.fmean(latencias)) if latencias else None,
        },
        "errores_http": sum(1 for f in filas if f["http"] != 200),
    }
    SALIDA.mkdir(parents=True, exist_ok=True)
    marca = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    (SALIDA / f"gemini_fidelidad_{marca}.json").write_text(
        json.dumps({"resumen": resumen, "por_consulta": filas}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
