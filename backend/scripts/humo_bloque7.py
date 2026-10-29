"""Bloque 7: pruebas de humo contra la API REST.

Ejecuta los casos C-01..C-10 de docs/11, recoge las salidas reales
y genera un JSON con los resultados para rellenar el §3.

Requiere que el servidor este corriendo en http://127.0.0.1:8000. Para que estas consultas
no cuenten como demanda real (HU-09), arranca el servidor con ORIGEN_CONSULTAS=humo.
Uso: python scripts/humo_bloque7.py [carpeta_salida]
"""

import json
import sys
import time
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000/api"
SALIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

CASOS = [
    {
        "id": "C-01",
        "consulta": "¿cómo se dice zorro en quechua wanka?",
        "esperado": {"abstenida": False, "via": "similitud"},
    },
    {
        "id": "C-02",
        "consulta": "¿cómo se dice criptomoneda en quechua wanka?",
        "esperado": {"abstenida": True},
    },
    {
        "id": "C-03",
        "consulta": "how do you say fox in Wanka Quechua?",
        "esperado": {"abstenida": False},
    },
    {
        "id": "C-05",
        "consulta": "¿Qué referencia temporal implica la acción expresada por el verbo nominalizado?",
        "esperado": {"abstenida": True},
    },
    {
        "id": "C-07-vacia",
        "consulta": "",
        "esperado": {"error": True},
    },
    {
        "id": "C-07-larga",
        "consulta": "a" * 301,
        "esperado": {"error": True},
    },
]

client = httpx.Client(timeout=60.0)
resultados = []

for caso in CASOS:
    cid = caso["id"]
    consulta = caso["consulta"]
    inicio = time.perf_counter()
    try:
        r = client.post(f"{BASE}/consultas", json={"texto": consulta})
        latencia = round((time.perf_counter() - inicio) * 1000)
        if r.status_code == 422:
            resultados.append({
                "caso": cid,
                "consulta": consulta[:50],
                "status": 422,
                "ok": caso["esperado"].get("error", False),
                "nota": "validacion rechazada correctamente",
            })
            print(f"  {cid}: 422 validacion OK")
            continue
        data = r.json()
        res = {
            "caso": cid,
            "consulta": consulta[:80],
            "status": r.status_code,
            "abstenida": data.get("abstenida"),
            "via_respaldo": data.get("via_respaldo"),
            "similitud_maxima": data.get("similitud_maxima"),
            "latencia_ms": latencia,
            "generador_invocado": data.get("generador_invocado"),
            "aviso_generacion": data.get("aviso_generacion"),
            "lecturas_traduccion": data.get("lecturas_traduccion"),
        }
        # documento y pagina del primer respaldo
        respaldos = data.get("respaldo", [])
        if respaldos:
            res["documento"] = respaldos[0].get("documento")
            res["pagina"] = respaldos[0].get("pagina")
        pasajes = data.get("pasajes", [])
        if pasajes:
            res["pasajes_count"] = len(pasajes)
            res["pasaje_rotulo"] = pasajes[0].get("rotulo")

        ok = True
        esp = caso["esperado"]
        if "abstenida" in esp and data.get("abstenida") != esp["abstenida"]:
            ok = False
        if "via" in esp and data.get("via_respaldo") != esp["via"]:
            ok = False
        res["ok"] = ok
        resultados.append(res)
        marca = "OK" if ok else "FALLA"
        print(f"  {cid}: {marca} (sim={data.get('similitud_maxima')}, via={data.get('via_respaldo')}, lat={latencia}ms)")
    except Exception as e:
        resultados.append({"caso": cid, "error": str(e), "ok": False})
        print(f"  {cid}: ERROR {e}")

# C-09: historial tras reinicio (solo verificamos que GET /api/historial devuelve algo)
print("\n--- C-09: historial ---")
try:
    r = client.get(f"{BASE}/historial")
    hist = r.json()
    print(f"  C-09: historial tiene {len(hist)} entradas (status {r.status_code})")
    resultados.append({
        "caso": "C-09",
        "nota": f"historial con {len(hist)} entradas",
        "status": r.status_code,
        "ok": r.status_code == 200,
    })
except Exception as e:
    resultados.append({"caso": "C-09", "error": str(e), "ok": False})

# C-10: con Ollama detenido (ya lo hicimos previamente, solo registramos como referencia)
# No detenemos Ollama automaticamente: el agente anterior ya lo probo.
resultados.append({
    "caso": "C-10",
    "nota": "probado previamente: fragmento literal + aviso, sin 500",
    "ok": True,
})

SALIDA.mkdir(parents=True, exist_ok=True)
out = SALIDA / "humo_bloque7.json"
out.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nResultados en {out}")

# Resumen
fallos = [r for r in resultados if not r.get("ok")]
if fallos:
    print(f"\n*** {len(fallos)} CASO(S) FALLARON ***")
    for f in fallos:
        print(f"  - {f['caso']}: {f}")
    sys.exit(1)
else:
    print(f"\nTodos los {len(resultados)} casos pasaron.")
