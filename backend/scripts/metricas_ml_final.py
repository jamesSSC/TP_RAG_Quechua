"""B3 · Metricas finales de ML y de la salvaguarda para la entrega U4 (indicador 10).

Reutiliza exactamente los datos y las caracteristicas de `entrenar_predictores.py` (415 consultas
etiquetadas, 11 rasgos, semilla 2026) y calcula lo que el informe pide y el PMV2 no dejo:

1. Los dos predictores (cobertura RF-14 y pasajes RF-15): validacion cruzada estratificada k = 5
   con media y desviacion por particion; matriz de confusion, precision, exhaustividad, F1, ROC-AUC
   y Brier sobre las predicciones fuera de particion; IC 95 % por bootstrap (1 000 remuestreos).
2. El umbral tau: barrido de cobertura y falsos positivos (tau como "maximizar la cobertura sujeto a
   FP = 0") y su comprobacion en una muestra que NO se uso para calibrarlo (F: 107 preguntas fuera de
   cobertura de negativas_prosa.json).
3. Linea base BM25 frente al hibrido lexico (recall@5, MRR@10 y cobertura con 0 FP).
4. Figuras PNG (curvas ROC, matrices de confusion, barrido de tau).

Uso:  python scripts/metricas_ml_final.py [carpeta_salida]
Necesita backend/data/fragmentos_v3.jsonl (reconstruible con scripts/reconstruir_corpus.py).
"""

import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts"))

import entrenar_predictores as ep  # noqa: E402

from adapters.out.recuperacion.indice_hibrido_lexico import IndiceHibridoLexico  # noqa: E402
from adapters.out.traduccion.traductor_tabla import TraductorTabla  # noqa: E402
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase  # noqa: E402
from domain.services.depurador_consulta import DepuradorConsulta  # noqa: E402
from domain.services.evaluador_confianza import EvaluadorConfianza  # noqa: E402

SEMILLA = ep.SEMILLA
REMUESTREOS = 1000
CORTES = {"cobertura": 0.25, "pasajes": 0.50}  # cortes de operacion vigentes (config.py)
TAU = 0.48
PALETA = {
    "acento": "#8A5A2B",
    "aviso": "#86581A",
    "tinta": "#1C1A17",
    "suave": "#5D574F",
    "borde": "#DED5C7",
}


# ----------------------------------------------------------------------------- utilidades
def r4(x):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), 4)


def metricas_corte(y, prob, corte):
    pred = (prob >= corte).astype(int)
    vn, fp, fn, vp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "auc_roc": r4(roc_auc_score(y, prob)) if len(set(y)) > 1 else None,
        "precision": r4(precision_score(y, pred, zero_division=0)),
        "exhaustividad": r4(recall_score(y, pred, zero_division=0)),
        "especificidad": r4(vn / (vn + fp) if (vn + fp) else 0.0),
        "f1": r4(f1_score(y, pred, zero_division=0)),
        "brier": r4(brier_score_loss(y, prob)),
        "matriz_confusion": {"vp": int(vp), "fp": int(fp), "vn": int(vn), "fn": int(fn)},
    }


def clopper_pearson_superior(k, n, conf=0.95):
    """Cota superior exacta (dos colas) de una proporcion. Con k = 0: 1 - (alfa/2)^(1/n)."""
    from scipy.stats import beta

    if k == n:
        return 1.0
    return float(beta.ppf(1 - (1 - conf) / 2, k + 1, n - k))


# ------------------------------------------------------------------ 1. predictores con IC 95 %
def evaluar_predictor(nombre, X, y, corte):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)
    por_particion = {m: [] for m in ("regresion_logistica", "bosque_aleatorio")}
    oof = {m: np.zeros(len(y)) for m in por_particion}
    for k, (ent, pru) in enumerate(cv.split(X, y), start=1):
        for m in por_particion:
            modelo = ep.candidatos()[m].fit(X[ent], y[ent])
            p = modelo.predict_proba(X[pru])[:, 1]
            oof[m][pru] = p
            fila = metricas_corte(y[pru], p, corte)
            fila.pop("matriz_confusion")
            fila["particion"] = k
            fila["n"] = int(len(pru))
            por_particion[m].append(fila)

    resumen = {}
    for m, filas in por_particion.items():
        claves = ["auc_roc", "precision", "exhaustividad", "especificidad", "f1", "brier"]
        resumen[m] = {
            c: {
                "media": r4(np.mean([f[c] for f in filas])),
                "desv": r4(np.std([f[c] for f in filas], ddof=1)),
            }
            for c in claves
        }

    p = oof["regresion_logistica"]
    rng = np.random.default_rng(SEMILLA)
    boot = {"auc_roc": [], "f1": [], "brier": []}
    for _ in range(REMUESTREOS):
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx])) < 2:
            continue
        boot["auc_roc"].append(roc_auc_score(y[idx], p[idx]))
        boot["f1"].append(f1_score(y[idx], (p[idx] >= corte).astype(int), zero_division=0))
        boot["brier"].append(brier_score_loss(y[idx], p[idx]))
    ic = {c: [r4(np.percentile(v, 2.5)), r4(np.percentile(v, 97.5))] for c, v in boot.items()}

    fpr, tpr, _ = roc_curve(y, p)
    return {
        "tarea": nombre,
        "n": int(len(y)),
        "positivos": int(y.sum()),
        "corte_operacion": corte,
        "fuera_de_particion_corte_operacion": metricas_corte(y, p, corte),
        "fuera_de_particion_corte_05": metricas_corte(y, p, 0.5),
        "validacion_cruzada_media_desv": resumen,
        "por_particion_regresion_logistica": por_particion["regresion_logistica"],
        "ic95_bootstrap": {"remuestreos": len(boot["auc_roc"]), **ic},
        "roc": {"fpr": fpr.tolist(), "tpr": tpr.tolist()},
    }, oof


# ---------------------------------------------------------------------- 2. barrido de tau
def barrido_tau(indice, conjunto_v2, negativas_f):
    traductor = TraductorTabla(ep.configuracion.ruta_tabla_traduccion)

    def caso(tau):
        return ConsultarCorpusUseCase(
            indice=indice,
            generador=ep.GeneradorLiteral(),
            evaluador=EvaluadorConfianza(umbral=tau),
            detector_idioma=ep.DetectorIdiomaHeuristico(),
            traductor=traductor,
            k=ep.configuracion.fragmentos_recuperados,
        )

    filas = []
    for tau in [round(t, 2) for t in np.arange(0.05, 0.96, 0.01)]:
        uc = caso(tau)
        resp = {e["id"]: not uc.ejecutar(e["consulta"]).abstenida for e in conjunto_v2}
        pos = [e for e in conjunto_v2 if e["subconjunto"][0] in "ABD"]
        neg = [e for e in conjunto_v2 if e["subconjunto"][0] == "C"]
        filas.append(
            {
                "tau": tau,
                "cobertura_ABD": r4(sum(resp[e["id"]] for e in pos) / len(pos)),
                "fp_C": sum(resp[e["id"]] for e in neg),
            }
        )
    factibles = [f for f in filas if f["fp_C"] == 0]
    optimo = max(factibles, key=lambda f: (f["cobertura_ABD"], -f["tau"])) if factibles else None
    tau_min_fp0 = min(f["tau"] for f in factibles) if factibles else None

    # Muestra independiente: F (negativas de prosa) no se uso para calibrar tau.
    uc = caso(TAU)
    afirmadas = [e["id"] for e in negativas_f if not uc.ejecutar(e["consulta"]).abstenida]
    n_f = len(negativas_f)
    c_neg = [e for e in conjunto_v2 if e["subconjunto"][0] == "C"]
    fp_c = sum(not uc.ejecutar(e["consulta"]).abstenida for e in c_neg)
    return filas, {
        "formulacion": "tau* = argmax_tau cobertura(A,B,D)  sujeto a  FP(C) = 0",
        "tau_vigente": TAU,
        "tau_minimo_con_fp0": tau_min_fp0,
        "optimo": optimo,
        "fila_tau_vigente": next(f for f in filas if f["tau"] == TAU),
        "calibracion_C": {
            "n": len(c_neg),
            "fp": fp_c,
            "cota_sup_95_clopper_pearson": r4(clopper_pearson_superior(fp_c, len(c_neg))),
        },
        "muestra_independiente_F": {
            "origen": "negativas_prosa.json (107 preguntas de gramatica sobre otras lenguas); "
            "no intervino en la calibracion de tau",
            "n": n_f,
            "fp_respuesta_afirmada": len(afirmadas),
            "ids_fp": afirmadas,
            "cota_sup_95_clopper_pearson": r4(clopper_pearson_superior(len(afirmadas), n_f)),
        },
    }


# --------------------------------------------------------------- 3. BM25 frente al hibrido
class Bm25:
    def __init__(self, textos, k1=1.5, b=0.75):
        self.docs = [t.split() for t in textos]
        self.k1, self.b = k1, b
        self.largo = np.array([len(d) for d in self.docs], dtype=float)
        self.media = self.largo.mean()
        self.tf = [Counter(d) for d in self.docs]
        df = Counter(t for d in self.docs for t in set(d))
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def puntuar(self, consulta):
        q = consulta.split()
        s = np.zeros(len(self.docs))
        for i, tf in enumerate(self.tf):
            den_base = self.k1 * (1 - self.b + self.b * self.largo[i] / self.media)
            for t in q:
                f = tf.get(t)
                if f:
                    s[i] += self.idf[t] * f * (self.k1 + 1) / (f + den_base)
        return s


def bm25_frente_hibrido(fragmentos, indice, conjunto_v2):
    import re

    dep = DepuradorConsulta()
    tok = re.compile(r"(?u)\b\w+\b")

    def norm(t):
        return " ".join(tok.findall(dep.normalizar(t)))

    bm = Bm25([norm(f.texto) for f in fragmentos])
    ids = [f.id for f in fragmentos]
    traductor = TraductorTabla(ep.configuracion.ruta_tabla_traduccion)

    def variantes(e):
        depurada = dep.depurar(e["consulta"])
        if e["subconjunto"][0] == "D":
            return [depurada, *traductor.candidatas(depurada, aproximar=True)]
        return [depurada]

    res = {"bm25": {}, "hibrido_E4": {}}
    maximos = {"bm25": {}, "hibrido_E4": {}}
    for e in conjunto_v2:
        for nombre in res:
            mejor = None
            for v in variantes(e):
                s = bm.puntuar(norm(v)) if nombre == "bm25" else indice.puntuar(v)
                mejor = s if mejor is None else np.maximum(mejor, s)
            orden = np.argsort(-mejor)[:10]
            maximos[nombre][e["id"]] = float(mejor.max())
            if e["subconjunto"][0] == "C":
                continue
            oro = set(e["oro"])
            top = [ids[i] for i in orden]
            sub = e["subconjunto"][0]
            d = res[nombre].setdefault(sub, {"n": 0, "recall5": 0, "rr": 0.0})
            d["n"] += 1
            d["recall5"] += int(bool(oro & set(top[:5])))
            d["rr"] += next((1 / (k + 1) for k, t in enumerate(top) if t in oro), 0.0)

    salida = {}
    for nombre, por_sub in res.items():
        c_max = max(maximos[nombre][e["id"]] for e in conjunto_v2 if e["subconjunto"][0] == "C")
        pos = [e for e in conjunto_v2 if e["subconjunto"][0] in "ABD"]
        cubiertas = sum(maximos[nombre][e["id"]] > c_max for e in pos)
        salida[nombre] = {
            **{
                s: {
                    "n": d["n"],
                    "recall@5": r4(d["recall5"] / d["n"]),
                    "mrr@10": r4(d["rr"] / d["n"]),
                }
                for s, d in sorted(por_sub.items())
            },
            "umbral_minimo_con_0_fp_en_C": r4(c_max),
            "cobertura_ABD_con_0_fp": r4(cubiertas / len(pos)),
            "nota": "BM25 Okapi (k1 1,5; b 0,75) sobre las mismas variantes de consulta (traduccion en D); sin la capa de lema"
            if nombre == "bm25"
            else "puntuacion E4 (palabras + n-gramas 3-5) sobre las mismas variantes; sin la capa de lema",
        }
    return salida


# ---------------------------------------------------------------------------- 4. figuras
def figuras(salida, preds, barrido, ancho_poster=False):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    dpi = 300 if ancho_poster else 150
    sufijo = "_poster" if ancho_poster else ""
    plt.rcParams.update(
        {
            "font.size": 12,
            "axes.edgecolor": PALETA["tinta"],
            "axes.labelcolor": PALETA["tinta"],
            "xtick.color": PALETA["tinta"],
            "ytick.color": PALETA["tinta"],
        }
    )

    fig, ax = plt.subplots(figsize=(10.5 if ancho_poster else 6, 10.5 if ancho_poster else 6))
    estilos = {"cobertura": "-", "pasajes": "--"}
    for nombre, r in preds.items():
        auc = r["fuera_de_particion_corte_operacion"]["auc_roc"]
        lo, hi = r["ic95_bootstrap"]["auc_roc"]
        ax.plot(
            r["roc"]["fpr"],
            r["roc"]["tpr"],
            estilos[nombre],
            color=PALETA["acento"],
            lw=2.5,
            label=f"Predicción {'1 · cobertura' if nombre == 'cobertura' else '2 · pasajes'}"
            f"  AUC {auc:.3f} (IC95 {lo:.3f}–{hi:.3f})",
        )
    ax.plot([0, 1], [0, 1], ":", color=PALETA["suave"], lw=1)
    ax.set_xlabel("Tasa de falsos positivos")
    ax.set_ylabel("Sensibilidad")
    ax.set_title("Curvas ROC (validación cruzada estratificada k = 5)")
    ax.legend(
        loc="lower right",
        bbox_to_anchor=(1.0, 0.12),
        frameon=True,
        facecolor="white",
        edgecolor=PALETA["borde"],
    )
    fig.tight_layout()
    fig.savefig(salida / f"roc_predictores{sufijo}.png", dpi=dpi, facecolor="white")
    plt.close(fig)

    for nombre, r in preds.items():
        m = r["fuera_de_particion_corte_operacion"]["matriz_confusion"]
        fig, ax = plt.subplots(figsize=(5, 4.4))
        datos = [[m["vp"], m["fn"]], [m["fp"], m["vn"]]]
        ax.imshow([[1, 0], [0, 1]], cmap=matplotlib.colors.ListedColormap(["#FFFFFF", "#F5EDE2"]))
        for i in range(2):
            for j in range(2):
                ax.text(
                    j,
                    i,
                    str(datos[i][j]),
                    ha="center",
                    va="center",
                    fontsize=20,
                    color=PALETA["tinta"],
                )
        ax.set_xticks([0, 1], ["Predice sí", "Predice no"])
        ax.set_yticks([0, 1], ["Real sí", "Real no"])
        for s in ax.spines.values():
            s.set_edgecolor(PALETA["borde"])
        ax.set_title(
            f"{'Cobertura' if nombre == 'cobertura' else 'Pasajes'} · corte {r['corte_operacion']}"
        )
        fig.tight_layout()
        fig.savefig(salida / f"matriz_{nombre}{sufijo}.png", dpi=dpi, facecolor="white")
        plt.close(fig)

    fig, ax1 = plt.subplots(figsize=(10.5 if ancho_poster else 7, 7 if ancho_poster else 4.5))
    taus = [f["tau"] for f in barrido]
    ax1.plot(
        taus,
        [f["cobertura_ABD"] for f in barrido],
        color=PALETA["acento"],
        lw=2.5,
        label="Cobertura A+B+D",
    )
    ax1.set_xlabel("Umbral τ")
    ax1.set_ylabel("Cobertura (consultas con respaldo respondidas)")
    ax1.set_ylim(0, 1.02)
    ax2 = ax1.twinx()
    ax2.step(
        taus,
        [f["fp_C"] for f in barrido],
        where="mid",
        color=PALETA["aviso"],
        lw=1.8,
        ls="--",
        label="Falsos positivos en C",
    )
    ax2.set_ylabel("Falsos positivos en C (de 28)")
    ax1.axvline(TAU, color=PALETA["tinta"], lw=1)
    ax1.text(TAU + 0.01, 0.05, "τ = 0,48", color=PALETA["tinta"])
    lineas = ax1.get_legend_handles_labels()[0] + ax2.get_legend_handles_labels()[0]
    ax1.legend(lineas, [ln.get_label() for ln in lineas], loc="center right", frameon=False)
    ax1.set_title("Barrido de τ: maximizar la cobertura sujeto a FP = 0")
    fig.tight_layout()
    fig.savefig(salida / f"barrido_tau{sufijo}.png", dpi=dpi, facecolor="white")
    plt.close(fig)


def main(salida: Path):
    salida.mkdir(parents=True, exist_ok=True)
    conjunto = ep.cargar_conjunto()
    uc = ep.caso_de_uso()
    X = np.array([uc.caracteristicas(f["consulta"]).como_vector() for f in conjunto])
    y = np.array([f["etiqueta"] for f in conjunto])
    part = np.array([f["particion"] for f in conjunto])
    prosa = np.isin(part, ["E", "F"])

    preds = {}
    preds["cobertura"], _ = evaluar_predictor("cobertura", X, y, CORTES["cobertura"])
    preds["pasajes"], _ = evaluar_predictor("pasajes", X[prosa], y[prosa], CORTES["pasajes"])

    datos = ep.DATOS
    v2 = json.loads((datos / "evaluacion_v2.json").read_text(encoding="utf-8"))
    negativas = json.loads((datos / "negativas_prosa.json").read_text(encoding="utf-8"))
    fragmentos = ep.cargar_fragmentos(ep.configuracion.ruta_corpus)
    indice = IndiceHibridoLexico()
    indice.indexar(fragmentos)

    barrido, resumen_tau = barrido_tau(indice, v2, negativas)
    linea_base = bm25_frente_hibrido(fragmentos, indice, v2)

    with (salida / "barrido_tau.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["tau", "cobertura_ABD", "fp_C"])
        w.writeheader()
        w.writerows(barrido)
    with (salida / "cv_por_particion.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "predictor",
                "particion",
                "n",
                "auc_roc",
                "precision",
                "exhaustividad",
                "especificidad",
                "f1",
                "brier",
            ]
        )
        for nombre, r in preds.items():
            for fila in r["por_particion_regresion_logistica"]:
                w.writerow(
                    [
                        nombre,
                        fila["particion"],
                        fila["n"],
                        fila["auc_roc"],
                        fila["precision"],
                        fila["exhaustividad"],
                        fila["especificidad"],
                        fila["f1"],
                        fila["brier"],
                    ]
                )

    resultado = {
        "semilla": SEMILLA,
        "remuestreos_bootstrap": REMUESTREOS,
        "corpus": "fragmentos_v3.jsonl (3605)",
        "predictores": {
            k: {kk: vv for kk, vv in v.items() if kk != "roc"} for k, v in preds.items()
        },
        "tau": resumen_tau,
        "bm25_frente_hibrido": linea_base,
    }
    (salida / "metricas_ml_final.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    figuras(salida, preds, barrido)
    figuras(salida, preds, barrido, ancho_poster=True)
    print(
        json.dumps(
            {
                "cobertura": preds["cobertura"]["fuera_de_particion_corte_operacion"],
                "cobertura_ic95": preds["cobertura"]["ic95_bootstrap"],
                "pasajes": preds["pasajes"]["fuera_de_particion_corte_operacion"],
                "pasajes_ic95": preds["pasajes"]["ic95_bootstrap"],
                "tau": {k: v for k, v in resumen_tau.items() if k != "muestra_independiente_F"},
                "F": resumen_tau["muestra_independiente_F"],
                "bm25_frente_hibrido": linea_base,
            },
            ensure_ascii=False,
            indent=1,
        )
    )


if __name__ == "__main__":
    main(
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else RAIZ.parent / "docs_entrega_final" / "metricas" / "evidencias"
    )
