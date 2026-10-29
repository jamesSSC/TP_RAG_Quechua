"""Pruebas de humo y de carga contra la API publicada en la nube (Guia 11, §3.8 del encargo).

Humo: C-01, C-02, C-03, C-05, C-07 (vacia y >300), HU-04 (pasajes), /api/predicciones (cubierta y
fuera de cobertura), /api/analitica/demanda, /api/historial y el CRUD de /api/fuentes. El primer
intento de cada caso se mide aparte (arranque en frio del plan gratuito de Render) y despues se
repite 5 veces para P50 y P95.

Carga (--carga N): N consultas en lotes con espera, rotuladas `carga` (HU-09). Mide transacciones
por segundo, P50/P95, errores y filas por origen que informa la API.

Para que las consultas se registren como `humo` o `carga` y no como demanda real, se envia
TOKEN_PRUEBAS (variable de entorno; el mismo valor que en Render). El token no se imprime.

Uso, desde backend/:
    set TOKEN_PRUEBAS=...   (PowerShell: $env:TOKEN_PRUEBAS="...")
    python scripts/humo_nube.py https://quechua-api.onrender.com
    python scripts/humo_nube.py https://quechua-api.onrender.com --carga 500
Salida: docs/evidencias/nube/humo_<fecha>.json (y carga_<fecha>.json).
"""

import argparse
import json
import os
import statistics
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import httpx

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "docs" / "evidencias" / "nube"
REPETICIONES = 5

CASOS_CONSULTA = [
    ("C-01", "HU-03/HU-07", "¿cómo se dice zorro en quechua wanka?", {"abstenida": False}),
    ("C-03", "HU-05", "how do you say fox in Wanka Quechua?", {"abstenida": False}),
    ("C-02", "HU-06", "¿cómo se dice criptomoneda en quechua wanka?", {"abstenida": True}),
    (
        "HU-04",
        "HU-04/RF-15",
        "¿Qué sufijo se usa para marcar localización espacial o temporal?",
        {"abstenida": True, "pasajes": True},
    ),
    (
        "C-05",
        "HU-06",
        "¿Cuál es el procedimiento para renovar un pasaporte?",
        {"abstenida": True},
    ),
    ("C-07-vacia", "Validacion", "", {"estado": 422}),
    ("C-07-larga", "Validacion", "a" * 301, {"estado": 422}),
]

PREDICCIONES = [
    ("HU-08.1-cubierta", "¿cómo se dice zorro en quechua wanka?"),
    ("HU-08.1-fuera", "¿cómo se dice criptomoneda en quechua wanka?"),
]

CONSULTAS_CARGA = [
    "¿cómo se dice zorro en quechua wanka?",
    "¿cómo se dice perro en quechua wanka?",
    "¿cómo se dice agua en quechua wanka?",
    "how do you say fox in Wanka Quechua?",
    "¿cómo se dice criptomoneda en quechua wanka?",
    "¿Qué sufijo se usa para marcar localización espacial o temporal?",
]


def _percentil(valores: list[float], p: float) -> float | None:
    if not valores:
        return None
    ordenados = sorted(valores)
    k = (len(ordenados) - 1) * p
    i = int(k)
    j = min(i + 1, len(ordenados) - 1)
    return round(ordenados[i] + (ordenados[j] - ordenados[i]) * (k - i), 1)


def _medir(cliente: httpx.Client, metodo: str, ruta: str, **kw):
    t0 = time.perf_counter()
    r = cliente.request(metodo, ruta, **kw)
    return r, round((time.perf_counter() - t0) * 1000, 1)


def _resumen_consulta(r: httpx.Response) -> dict:
    if r.status_code != 200:
        return {"estado": r.status_code}
    d = r.json()
    resumen = {
        "estado": 200,
        "abstenida": d.get("abstenida"),
        "texto": d.get("texto", "")[:160],
        "via_respaldo": d.get("via_respaldo"),
        "similitud_maxima": d.get("similitud_maxima"),
        "probabilidad_cobertura": d.get("probabilidad_cobertura"),
        "probabilidad_pasajes": d.get("probabilidad_pasajes"),
        "redactado_por": d.get("redactado_por"),
        "motivo_redaccion": d.get("motivo_redaccion"),
        "latencia_servidor_ms": d.get("latencia_ms"),
        "pasajes": len(d.get("pasajes", [])),
    }
    if d.get("respaldo"):
        resumen["cita"] = f"{d['respaldo'][0]['documento']}, p. {d['respaldo'][0]['pagina']}"
    return resumen


def _cumple(resumen: dict, esperado: dict) -> bool:
    if "estado" in esperado:
        return resumen["estado"] == esperado["estado"]
    if resumen["estado"] != 200 or resumen["abstenida"] != esperado["abstenida"]:
        return False
    if esperado.get("pasajes"):
        return resumen["pasajes"] > 0
    return True


def humo(cliente: httpx.Client) -> dict:
    resultado: dict = {"casos": [], "endpoints": {}}

    r, ms = _medir(cliente, "GET", "/api/estado")
    resultado["arranque_en_frio_ms"] = ms
    resultado["estado"] = r.json() if r.status_code == 200 else {"estado": r.status_code}
    print(f"[HUMO] /api/estado primer intento {ms} ms (incluye arranque en frio si dormia)")

    for cid, historia, texto, esperado in CASOS_CONSULTA:
        r, primero = _medir(cliente, "POST", "/api/consultas", json={"texto": texto})
        resumen = _resumen_consulta(r)
        tiempos = [
            _medir(cliente, "POST", "/api/consultas", json={"texto": texto})[1]
            for _ in range(REPETICIONES)
        ]
        caso = {
            "id": cid,
            "historia": historia,
            "entrada": texto if len(texto) <= 80 else f"{texto[:20]}... ({len(texto)} caracteres)",
            "esperado": esperado,
            "obtenido": resumen,
            "primer_intento_ms": primero,
            "p50_ms": _percentil(tiempos, 0.5),
            "p95_ms": _percentil(tiempos, 0.95),
            "estado": "APROBADO" if _cumple(resumen, esperado) else "RECHAZADO",
        }
        resultado["casos"].append(caso)
        print(f"[HUMO] {cid:12s} {caso['estado']:9s} p50={caso['p50_ms']} ms  {resumen}")

    for cid, texto in PREDICCIONES:
        r, primero = _medir(cliente, "POST", "/api/predicciones", json={"texto": texto})
        tiempos = [
            _medir(cliente, "POST", "/api/predicciones", json={"texto": texto})[1]
            for _ in range(REPETICIONES)
        ]
        caso = {
            "id": cid,
            "historia": "HU-08.1",
            "entrada": texto,
            "obtenido": r.json() if r.status_code == 200 else {"estado": r.status_code},
            "primer_intento_ms": primero,
            "p50_ms": _percentil(tiempos, 0.5),
            "p95_ms": _percentil(tiempos, 0.95),
            "estado": "APROBADO" if r.status_code == 200 else "RECHAZADO",
        }
        resultado["casos"].append(caso)
        print(f"[HUMO] {cid:16s} {caso['estado']} {caso['obtenido']}")

    for nombre, ruta in [
        ("historial", "/api/historial"),
        ("demanda", "/api/analitica/demanda?top=15"),
        ("demanda_con_sinteticas", "/api/analitica/demanda?top=15&incluir_sinteticas=true"),
        ("modelos", "/api/modelos"),
    ]:
        r, primero = _medir(cliente, "GET", ruta)
        tiempos = [_medir(cliente, "GET", ruta)[1] for _ in range(REPETICIONES)]
        cuerpo = r.json() if r.status_code == 200 else None
        resultado["endpoints"][nombre] = {
            "estado": r.status_code,
            "primer_intento_ms": primero,
            "p50_ms": _percentil(tiempos, 0.5),
            "p95_ms": _percentil(tiempos, 0.95),
            "muestra": (cuerpo[:3] if isinstance(cuerpo, list) else cuerpo),
        }
        print(f"[HUMO] GET {ruta} -> {r.status_code} p50={_percentil(tiempos, 0.5)} ms")

    resultado["crud_fuentes"] = crud_fuentes(cliente)
    return resultado


def crud_fuentes(cliente: httpx.Client) -> dict:
    fuente = {
        "titulo": "Fuente de prueba de humo (nube)",
        "entidad_publicadora": "Prueba automatizada",
        "licenciamiento": "No aplica: registro temporal de prueba",
        "fecha_extraccion": date.today().isoformat(),
        "nombre_archivo": f"humo_{int(time.time())}.pdf",
    }
    pasos = {}
    r, ms = _medir(cliente, "POST", "/api/fuentes", json=fuente)
    pasos["crear"] = {"estado": r.status_code, "ms": ms}
    if r.status_code != 201:
        print(f"[HUMO] CRUD fuentes: crear -> {r.status_code}")
        return {"pasos": pasos, "estado": "RECHAZADO"}
    fid = r.json()["id"]
    r, ms = _medir(cliente, "GET", "/api/fuentes")
    pasos["listar"] = {"estado": r.status_code, "ms": ms, "total": len(r.json())}
    r, ms = _medir(cliente, "PUT", f"/api/fuentes/{fid}", json={**fuente, "paginas_totales": 3})
    pasos["actualizar"] = {"estado": r.status_code, "ms": ms}
    r, ms = _medir(cliente, "DELETE", f"/api/fuentes/{fid}")
    pasos["eliminar"] = {"estado": r.status_code, "ms": ms}
    r, _ = _medir(cliente, "GET", f"/api/fuentes/{fid}")
    pasos["tras_eliminar"] = {"estado": r.status_code}
    esperado = {
        "crear": 201,
        "listar": 200,
        "actualizar": 200,
        "eliminar": 204,
        "tras_eliminar": 404,
    }
    ok = all(pasos[k]["estado"] == v for k, v in esperado.items())
    print(f"[HUMO] CRUD fuentes {'APROBADO' if ok else 'RECHAZADO'} {pasos}")
    return {"pasos": pasos, "estado": "APROBADO" if ok else "RECHAZADO"}


def carga(cliente: httpx.Client, total: int, lote: int, espera: float) -> dict:
    latencias, errores, codigos = [], 0, {}
    t0 = time.perf_counter()
    for i in range(total):
        texto = CONSULTAS_CARGA[i % len(CONSULTAS_CARGA)]
        try:
            r, ms = _medir(cliente, "POST", "/api/consultas", json={"texto": texto})
            codigos[r.status_code] = codigos.get(r.status_code, 0) + 1
            if r.status_code == 200:
                latencias.append(ms)
            else:
                errores += 1
        except httpx.HTTPError as exc:
            errores += 1
            codigos[type(exc).__name__] = codigos.get(type(exc).__name__, 0) + 1
        if (i + 1) % lote == 0:
            print(f"[CARGA] {i + 1}/{total}  errores={errores}")
            time.sleep(espera)
    duracion = time.perf_counter() - t0
    estado = cliente.get("/api/estado").json()
    return {
        "consultas": total,
        "lote": lote,
        "espera_entre_lotes_s": espera,
        "duracion_s": round(duracion, 1),
        "tps_incluyendo_esperas": round(total / duracion, 2),
        "tps_sin_esperas": round(len(latencias) / (sum(latencias) / 1000), 2)
        if latencias
        else None,
        "p50_ms": _percentil(latencias, 0.5),
        "p95_ms": _percentil(latencias, 0.95),
        "media_ms": round(statistics.fmean(latencias), 1) if latencias else None,
        "errores": errores,
        "codigos": {str(k): v for k, v in codigos.items()},
        "consultas_por_origen_tras_la_carga": estado.get("consultas_por_origen"),
        "base_demostracion": estado.get("base_demostracion"),
    }


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("url_api")
    argumentos.add_argument("--carga", type=int, default=0, help="consultas de carga (p. ej. 500)")
    argumentos.add_argument("--lote", type=int, default=25)
    argumentos.add_argument("--espera", type=float, default=2.0)
    argumentos.add_argument("--salida", type=Path, default=SALIDA)
    args = argumentos.parse_args()

    url = args.url_api.rstrip("/")
    if any(h in url for h in ("localhost", "127.0.0.1", "ngrok")):
        print("[HUMO] la Guia 11 exige la URL publica de la nube", file=sys.stderr)
        return 2
    token = os.environ.get("TOKEN_PRUEBAS", "")
    if not token:
        print("[HUMO] aviso: sin TOKEN_PRUEBAS las consultas se registran como `usuario`")
    args.salida.mkdir(parents=True, exist_ok=True)
    marca = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")

    def cliente(origen: str) -> httpx.Client:
        cabeceras = {"X-Origen-Consultas": origen}
        if token:
            cabeceras["X-Token-Pruebas"] = token
        return httpx.Client(base_url=url, headers=cabeceras, timeout=120.0)

    comun = {"url_api": url, "momento_utc": marca, "token_pruebas_usado": bool(token)}
    if args.carga:
        with cliente("carga") as c:
            datos = {**comun, **carga(c, args.carga, args.lote, args.espera)}
        destino = args.salida / f"carga_{marca}.json"
    else:
        with cliente("humo") as c:
            datos = {**comun, **humo(c)}
        rechazados = [c["id"] for c in datos["casos"] if c["estado"] != "APROBADO"]
        if datos["crud_fuentes"]["estado"] != "APROBADO":
            rechazados.append("CRUD-fuentes")
        datos["rechazados"] = rechazados
        destino = args.salida / f"humo_{marca}.json"
    destino.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[HUMO] escrito {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
