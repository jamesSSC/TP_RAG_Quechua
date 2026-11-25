"""B3 y B10 · Latencia de extremo a extremo (P50/P95) y energia de la GPU por consulta, en local.

Recorre las 248 consultas de evaluacion_v2.json (N >= 30, ninguna inventada) contra la API local
y, si se pide, registra en paralelo la potencia de la GPU con
`nvidia-smi --query-gpu=timestamp,power.draw --format=csv -lms 100`.

La energia de cada consulta es la integral de la potencia medida durante su intervalo [t0, t1]
menos la potencia en reposo (mediana de 10 s sin carga) por la duracion: es la energia que la
consulta anade, no la del equipo entero. Se informa por respuesta y por abstencion.

Uso:
    python scripts/medir_latencia_energia.py http://127.0.0.1:8000 SALIDA [--energia] [--etiqueta X]

Contra la nube (HU-09): las consultas se marcan con `--origen humo` (cabeceras X-Token-Pruebas y
X-Origen-Consultas; el token se lee de la variable TOKEN_PRUEBAS o de backend/.env y no se imprime)
y se espacian con `--por-minuto 20`, para no registrar demanda falsa ni forzar el limite:
    python scripts/medir_latencia_energia.py https://quechua-api.onrender.com SALIDA         --origen humo --por-minuto 20 --etiqueta nube_gemini
Ademas del tiempo, informa el arnes: recall@5 (oro en el respaldo) en A, B y D y FP en C.
"""

import os

import csv
import json
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx

RAIZ = Path(__file__).resolve().parents[1]


class MedidorGpu:
    def __init__(self):
        self.muestras: list[tuple[float, float]] = []
        self._proc = None
        self._hilo = None

    def iniciar(self):
        self._proc = subprocess.Popen(
            [
                "nvidia-smi",
                "--query-gpu=power.draw",
                "--format=csv,noheader,nounits",
                "-lms",
                "100",
            ],
            stdout=subprocess.PIPE,
            text=True,
        )
        self._hilo = threading.Thread(target=self._leer, daemon=True)
        self._hilo.start()

    def _leer(self):
        for linea in self._proc.stdout:
            try:
                self.muestras.append((time.perf_counter(), float(linea.strip())))
            except ValueError:
                continue

    def detener(self):
        if self._proc:
            self._proc.terminate()

    def energia_j(self, t0, t1, reposo_w):
        tramo = [(t, p) for t, p in self.muestras if t0 <= t <= t1]
        if len(tramo) < 2:
            potencia = next((p for t, p in reversed(self.muestras) if t <= t1), reposo_w)
            return max(0.0, (potencia - reposo_w) * (t1 - t0)), potencia
        e = 0.0
        for (ta, pa), (tb, pb) in zip(tramo, tramo[1:], strict=False):
            e += ((pa + pb) / 2 - reposo_w) * (tb - ta)
        return max(0.0, e), statistics.mean(p for _, p in tramo)


def percentil(valores, p):
    v = sorted(valores)
    return v[min(len(v) - 1, round((len(v) - 1) * p))]


def token_pruebas() -> str:
    if os.environ.get("TOKEN_PRUEBAS"):
        return os.environ["TOKEN_PRUEBAS"]
    env = RAIZ / ".env"
    if env.exists():
        for linea in env.read_text(encoding="utf-8").splitlines():
            if linea.startswith("TOKEN_PRUEBAS="):
                return linea.split("=", 1)[1].strip()
    return ""


def main(base, salida: Path, energia: bool, etiqueta: str, origen=None, por_minuto=0):
    salida.mkdir(parents=True, exist_ok=True)
    consultas = json.loads((RAIZ / "data" / "evaluacion_v2.json").read_text(encoding="utf-8"))
    cabeceras = {}
    if origen:
        # La API solo acepta estos origenes (seguridad.py, ORIGENES_DE_PRUEBA); cualquier otro
        # se registra como `usuario`, es decir, como demanda real. Ocurrio el 20/11 con "arnes".
        if origen not in {"humo", "carga"}:
            sys.exit(f"Origen '{origen}' no admitido por la API: usar humo o carga.")
        token = token_pruebas()
        if not token:
            sys.exit("Falta TOKEN_PRUEBAS: sin el, las consultas contarian como demanda real.")
        cabeceras = {"X-Token-Pruebas": token, "X-Origen-Consultas": origen}
    cliente = httpx.Client(timeout=180.0, headers=cabeceras)
    pausa = 60.0 / por_minuto if por_minuto else 0.0
    estado = cliente.get(f"{base}/api/estado").json()

    gpu = MedidorGpu() if energia else None
    reposo = None
    if gpu:
        gpu.iniciar()
        time.sleep(10)
        reposo = statistics.median(p for _, p in gpu.muestras)

    # Calentamiento: la primera consulta carga el modelo en VRAM y no es representativa.
    t = time.perf_counter()
    cliente.post(f"{base}/api/consultas", json={"texto": "zorro"})
    calentamiento_ms = (time.perf_counter() - t) * 1000

    filas = []
    for e in consultas:
        if pausa:
            time.sleep(pausa)
        t0 = time.perf_counter()
        r = cliente.post(f"{base}/api/consultas", json={"texto": e["consulta"]})
        t1 = time.perf_counter()
        d = r.json()
        fila = {
            "id": e["id"],
            "subconjunto": e["subconjunto"][0],
            "http": r.status_code,
            "abstenida": d.get("abstenida"),
            "generador_invocado": d.get("generador_invocado"),
            "redactado_por": d.get("redactado_por"),
            # P4 (diagnostico): por que respondio el respaldo (429, 503, tiempo agotado o
            # verificador). Lo devuelve la API; no contiene la clave ni datos personales.
            "motivo_redaccion": d.get("motivo_redaccion") or "",
            "total_ms": round((t1 - t0) * 1000, 2),
            "servidor_ms": d.get("latencia_ms"),
            "oro_en_top5": bool(
                set(e["oro"]) & {f["fragmento_id"] for f in (d.get("respaldo") or [])[:5]}
            )
            if e["oro"]
            else None,
        }
        if gpu:
            ej, pmedia = gpu.energia_j(t0, t1, reposo)
            fila["energia_j"] = round(ej, 3)
            fila["potencia_media_w"] = round(pmedia, 2)
        filas.append(fila)
    if gpu:
        gpu.detener()

    with (salida / f"latencia_{etiqueta}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)

    def resumen(sub):
        tot = [f["total_ms"] for f in sub]
        r = {
            "n": len(sub),
            "p50_ms": round(percentil(tot, 0.5), 1),
            "p95_ms": round(percentil(tot, 0.95), 1),
            "max_ms": round(max(tot), 1),
            "media_ms": round(statistics.mean(tot), 1),
        }
        if gpu:
            ens = [f["energia_j"] for f in sub]
            r.update(
                {
                    "energia_media_j": round(statistics.mean(ens), 2),
                    "energia_p50_j": round(percentil(ens, 0.5), 2),
                    "energia_total_j": round(sum(ens), 1),
                }
            )
        return r

    respondidas = [f for f in filas if f["abstenida"] is False]
    abstenidas = [f for f in filas if f["abstenida"] is True]
    res = {
        "etiqueta": etiqueta,
        "api": base,
        "generador": estado.get("generador"),
        "modelo": estado.get("modelo"),
        "fragmentos": estado.get("fragmentos_indexados"),
        "calentamiento_ms": round(calentamiento_ms, 1),
        "todas": resumen(filas),
        "respuestas": resumen(respondidas) if respondidas else None,
        "abstenciones": resumen(abstenidas) if abstenidas else None,
        "errores_http": sum(f["http"] != 200 for f in filas),
        "origen": origen or "usuario (API local)",
        "arnes": {
            sub: {
                "n": len(g := [f for f in filas if f["subconjunto"] == sub]),
                "respondidas": sum(f["abstenida"] is False for f in g),
                **(
                    {"falsos_positivos": sum(f["abstenida"] is False for f in g)}
                    if sub == "C"
                    else {"recall@5": round(sum(bool(f["oro_en_top5"]) for f in g) / len(g), 4)}
                ),
            }
            for sub in "ABCD"
        },
        "potencia_reposo_w": round(reposo, 2) if reposo is not None else None,
        "fecha_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (salida / f"latencia_{etiqueta}.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    args = sys.argv[1:]
    etiqueta = args[args.index("--etiqueta") + 1] if "--etiqueta" in args else "local"
    origen = args[args.index("--origen") + 1] if "--origen" in args else None
    por_minuto = int(args[args.index("--por-minuto") + 1]) if "--por-minuto" in args else 0
    main(args[0], Path(args[1]), "--energia" in args, etiqueta, origen, por_minuto)
