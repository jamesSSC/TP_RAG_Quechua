"""PMV1 + PMV2 · Prueba con data masiva: ejecuta entre 500 y 1000 transacciones de consulta
contra el sistema completo, tal como lo cablea el contenedor (indice, traduccion, regla del
umbral, predictores del PMV2 y base de datos), y deja la evidencia en CSV y JSON.

Composicion de la carga (semilla fija 2026, reproducible):
  1. Las 415 consultas etiquetadas del proyecto (A, B, C, D, E y F).
  2. Consultas derivadas del propio corpus hasta completar N: por cada lema del diccionario
     elegido al azar, una de tres formulaciones en espanol, y para una parte de ellos la
     formulacion inglesa con la traduccion de la tabla ES->EN.

Declaracion: las consultas del punto 2 se generan a partir del corpus indexado, de modo que
NO son consultas de usuarios reales ni sirven para medir la calidad (eso lo hacen el arnes y
la validacion cruzada). Sirven para lo que exige la prueba de data masiva: volumen, latencia
bajo carga, persistencia de cada transaccion y alimentar la analitica de HU-09.

Uso, desde backend/:
    python scripts/generar_transacciones.py [N=800] [carpeta_evidencias]
Base de datos: la de la configuracion (SQLite por defecto; BASE_DATOS=postgres para usar los
procedimientos almacenados). Se recomienda RUTA_SQLITE=<archivo nuevo> para no mezclar con el
historial de uso.
"""

import csv
import json
import random
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts"))

from entrenar_predictores import cargar_conjunto  # noqa: E402

from infrastructure.config import configuracion  # noqa: E402
from domain.value_objects.origen_consulta import OrigenConsulta  # noqa: E402
from infrastructure.contenedor import Contenedor  # noqa: E402

SEMILLA = 2026
PLANTILLAS_ES = [
    "¿cómo se dice {t} en quechua wanka?",
    "necesito el término wanka para referirme a {t}",
    "estoy buscando la palabra que designa {t} en la variedad wanka",
]
PLANTILLA_EN = "how do you say {t} in Wanka Quechua?"


def carga(n: int, contenedor: Contenedor) -> list[dict]:
    rng = random.Random(SEMILLA)
    filas = [
        {"origen": f["particion"], "consulta": f["consulta"], "etiqueta": f["etiqueta"]}
        for f in cargar_conjunto()
    ]
    tabla_es_en = json.loads(
        (RAIZ / "data" / "traduccion_es_en.json").read_text(encoding="utf-8")
    )
    lemas = sorted(
        lema for lema in contenedor.indice._lemario if lema.isalpha() and len(lema) > 2
    )
    rng.shuffle(lemas)
    for lema in lemas:
        if len(filas) >= n:
            break
        en = tabla_es_en.get(lema)
        if en and rng.random() < 0.25:
            termino = en[0] if isinstance(en, list) else en
            filas.append({"origen": "lema_en", "consulta": PLANTILLA_EN.format(t=termino)})
        else:
            plantilla = rng.choice(PLANTILLAS_ES)
            filas.append({"origen": "lema_es", "consulta": plantilla.format(t=lema)})
    rng.shuffle(filas)
    return filas[:n]


def percentil(valores: list[float], q: float) -> float:
    ordenados = sorted(valores)
    return ordenados[min(len(ordenados) - 1, int(q * (len(ordenados) - 1)))]


def main(n: int, salida: Path) -> None:
    salida.mkdir(parents=True, exist_ok=True)
    # HU-09: lo que esta corrida registra es sintetico y se rotula como `carga`.
    contenedor = Contenedor(generador="literal", origen=OrigenConsulta.CARGA)
    uc = contenedor.consultar_corpus
    filas = carga(n, contenedor)
    print(f"[CARGA] {len(filas)} transacciones · base de datos: {configuracion.base_datos}")

    registros, t0 = [], time.perf_counter()
    for i, fila in enumerate(filas, start=1):
        r = uc.ejecutar(fila["consulta"])
        registros.append(
            {
                "n": i,
                "origen": fila["origen"],
                "consulta": fila["consulta"],
                "etiqueta": fila.get("etiqueta", ""),
                "decision": "responde"
                if not r.abstenida
                else ("abstiene_con_pasajes" if r.pasajes else "abstiene"),
                "via": r.via_respaldo or "",
                "similitud_maxima": round(r.similitud_maxima, 4),
                "p_cobertura": "" if r.probabilidad_cobertura is None
                else round(r.probabilidad_cobertura, 4),
                "p_pasajes": "" if r.probabilidad_pasajes is None
                else round(r.probabilidad_pasajes, 4),
                "abstencion_por_predictor": int(r.abstencion_por_predictor),
                "documento": r.respaldo[0].procedencia.documento if r.respaldo else "",
                "pagina": r.respaldo[0].procedencia.pagina if r.respaldo else "",
                "latencia_ms": r.latencia_ms,
            }
        )
        if i % 100 == 0:
            print(f"  {i} transacciones")
    duracion = time.perf_counter() - t0

    with (salida / "transacciones.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(registros[0]))
        w.writeheader()
        w.writerows(registros)

    latencias = [r["latencia_ms"] for r in registros]
    por_origen: dict[str, dict[str, int]] = {}
    for r in registros:
        d = por_origen.setdefault(r["origen"], {})
        d[r["decision"]] = d.get(r["decision"], 0) + 1
    etiquetadas = [r for r in registros if r["etiqueta"] != ""]
    fp = sum(1 for r in etiquetadas if r["etiqueta"] == 0 and r["decision"] == "responde")
    lema_es = [r for r in registros if r["origen"] == "lema_es"]
    resumen = {
        "transacciones": len(registros),
        "base_datos": configuracion.base_datos,
        "duracion_s": round(duracion, 2),
        "transacciones_por_segundo": round(len(registros) / duracion, 1),
        "latencia_ms": {
            "media": round(statistics.mean(latencias), 2),
            "p50": round(percentil(latencias, 0.50), 2),
            "p95": round(percentil(latencias, 0.95), 2),
            "max": round(max(latencias), 2),
        },
        "por_origen": por_origen,
        "falsos_positivos_en_negativas_etiquetadas": fp,
        "respondidas_lema_es": f"{sum(r['decision'] == 'responde' for r in lema_es)}/{len(lema_es)}",
        "abstenciones_por_predictor": sum(r["abstencion_por_predictor"] for r in registros),
        "estadisticas_base_datos": contenedor.repositorio_consultas.estadisticas()
        if contenedor.repositorio_consultas
        else None,
        "generador": "literal (sin Ollama): mide recuperacion, prediccion y persistencia",
    }
    (salida / "resumen_transacciones.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    print(json.dumps(resumen, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 800
    carpeta = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ.parent / "docs" / "evidencias" / "pmv2"
    main(total, carpeta)
