"""PMV2 · Entrena y valida los dos modelos predictivos (HU-08.1 / RF-14 y HU-04 / RF-15).

Modelo 1 · Cobertura documental. Estima la probabilidad de que el corpus respalde la
consulta. Se entrena con las 415 consultas etiquetadas del proyecto:
  - con respaldo:  A (120), B (60), D (40) de evaluacion_v2.json y E (60) de evaluacion_prosa.json
  - sin respaldo:  C (28) de evaluacion_v2.json y F (107) de negativas_prosa.json

Modelo 2 · Relevancia de los pasajes de prosa. Estima si los pasajes que el sistema ofrece al
abstenerse tratan de verdad la pregunta. Se entrena con E (60, si) frente a F (107, no).

Las caracteristicas salen del mismo caso de uso que atiende la consulta real
(ConsultarCorpusUseCase.caracteristicas), de modo que entrenar y predecir hacen las mismas
cuentas. Validacion cruzada estratificada de 5 particiones con semilla fija (2026); las
cifras que se reportan son las de validacion, nunca las de entrenamiento.

Uso, desde backend/:  python scripts/entrenar_predictores.py [carpeta_evidencias]
Genera:  modelos/cobertura.joblib, modelos/relevancia_pasajes.joblib, modelos/metricas.json
         y en la carpeta de evidencias: caracteristicas.csv, predicciones_cv.csv, metricas.json
"""

import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from adapters.out.documentos.corpus_jsonl import cargar_fragmentos  # noqa: E402
from adapters.out.generacion.generador_literal import GeneradorLiteral  # noqa: E402
from adapters.out.idioma.detector_idioma_heuristico import (  # noqa: E402
    DetectorIdiomaHeuristico,
)
from adapters.out.recuperacion.indice_hibrido_lexico import (  # noqa: E402
    IndiceHibridoLexico,
)
from adapters.out.traduccion.traductor_tabla import TraductorTabla  # noqa: E402
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase  # noqa: E402
from domain.services.caracteristicas_consulta import NOMBRES  # noqa: E402
from domain.services.evaluador_confianza import EvaluadorConfianza  # noqa: E402
from infrastructure.config import configuracion  # noqa: E402

DATOS = RAIZ / "data"
# QW_MODELOS_SALIDA permite entrenar sin tocar los modelos versionados (scripts/demo/04).
MODELOS = Path(os.environ.get("QW_MODELOS_SALIDA") or RAIZ / "modelos")
SEMILLA = 2026
CON_RESPALDO = {"A", "B", "D", "E"}
REJILLA = [round(float(x), 2) for x in np.arange(0.05, 0.96, 0.05)]


def cargar_conjunto() -> list[dict]:
    filas = []
    for archivo in ("evaluacion_v2.json", "evaluacion_prosa.json", "negativas_prosa.json"):
        for e in json.loads((DATOS / archivo).read_text(encoding="utf-8")):
            particion = e["subconjunto"][0]
            filas.append(
                {
                    "id": e["id"],
                    "particion": particion,
                    "consulta": e["consulta"],
                    "etiqueta": 1 if particion in CON_RESPALDO else 0,
                }
            )
    return filas


def caso_de_uso() -> ConsultarCorpusUseCase:
    indice = IndiceHibridoLexico()
    indice.indexar(cargar_fragmentos(configuracion.ruta_corpus))
    return ConsultarCorpusUseCase(
        indice=indice,
        generador=GeneradorLiteral(),
        evaluador=EvaluadorConfianza(umbral=configuracion.umbral_abstencion),
        detector_idioma=DetectorIdiomaHeuristico(),
        traductor=TraductorTabla(configuracion.ruta_tabla_traduccion),
        k=configuracion.fragmentos_recuperados,
    )


def candidatos() -> dict:
    return {
        "regresion_logistica": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=SEMILLA),
        ),
        "bosque_aleatorio": RandomForestClassifier(
            n_estimators=300, min_samples_leaf=2, class_weight="balanced", random_state=SEMILLA
        ),
        "linea_base_mayoritaria": DummyClassifier(strategy="most_frequent"),
    }


def metricas(y, prob, corte=0.5) -> dict:
    pred = (prob >= corte).astype(int)
    vn, fp, fn, vp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "n": int(len(y)),
        "auc_roc": round(float(roc_auc_score(y, prob)), 4) if len(set(y)) > 1 else None,
        "exactitud": round(float(accuracy_score(y, pred)), 4),
        "precision": round(float(precision_score(y, pred, zero_division=0)), 4),
        "sensibilidad": round(float(recall_score(y, pred, zero_division=0)), 4),
        "especificidad": round(float(vn / (vn + fp)) if (vn + fp) else 0.0, 4),
        "f1": round(float(f1_score(y, pred, zero_division=0)), 4),
        "matriz_confusion": {"vp": int(vp), "fp": int(fp), "vn": int(vn), "fn": int(fn)},
        "corte": corte,
    }


def validar(nombre_tarea: str, X, y, cv) -> tuple[dict, dict]:
    resultados, probabilidades = {}, {}
    for nombre, modelo in candidatos().items():
        prob = cross_val_predict(modelo, X, y, cv=cv, method="predict_proba")[:, 1]
        probabilidades[nombre] = prob
        resultados[nombre] = metricas(y, prob)
        print(f"[{nombre_tarea}] {nombre:24s} {resultados[nombre]}")
    return resultados, probabilidades


def curva(y, prob) -> dict:
    fpr, tpr, _ = roc_curve(y, prob)
    return {"fpr": [round(float(v), 4) for v in fpr], "tpr": [round(float(v), 4) for v in tpr]}


def guardar_modelo(ruta: Path, modelo, metadatos: dict) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"estimador": modelo, "caracteristicas": list(NOMBRES), "metadatos": metadatos}, ruta
    )


def coeficientes(modelo) -> dict:
    reg = modelo.named_steps["logisticregression"]
    return {n: round(float(c), 4) for n, c in zip(NOMBRES, reg.coef_[0], strict=True)}


def main(salida: Path) -> None:
    salida.mkdir(parents=True, exist_ok=True)
    conjunto = cargar_conjunto()
    uc = caso_de_uso()

    print(f"[DATOS] {len(conjunto)} consultas etiquetadas; extrayendo caracteristicas...")
    X, decisiones = [], []
    for fila in conjunto:
        X.append(uc.caracteristicas(fila["consulta"]).como_vector())
        r = uc.ejecutar(fila["consulta"])
        decisiones.append(
            {"responde": not r.abstenida, "pasajes": len(r.pasajes), "via": r.via_respaldo}
        )
    X = np.array(X)
    y = np.array([f["etiqueta"] for f in conjunto])
    particiones = np.array([f["particion"] for f in conjunto])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)

    with (salida / "caracteristicas.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "particion", "etiqueta", *NOMBRES])
        for fila, x in zip(conjunto, X, strict=True):
            w.writerow([fila["id"], fila["particion"], fila["etiqueta"], *[round(v, 6) for v in x]])

    # ---------------- Modelo 1: cobertura documental (RF-14) ----------------
    res_cob, prob_cob = validar("cobertura", X, y, cv)
    p1 = prob_cob["regresion_logistica"]
    regla_umbral = np.array([1 if d["responde"] else 0 for d in decisiones])
    linea_base_regla = metricas(y, regla_umbral.astype(float))
    por_particion = {
        p: {
            "n": int((particiones == p).sum()),
            "prob_media": round(float(p1[particiones == p].mean()), 4),
            "aciertos_corte_05": int(
                ((p1[particiones == p] >= 0.5) == (y[particiones == p] == 1)).sum()
            ),
        }
        for p in "ABCDEF"
    }
    # Compuerta RN-06: el predictor solo puede abstenerse donde el umbral responde.
    compuerta = []
    for corte in REJILLA:
        retiradas = int(((regla_umbral == 1) & (p1 < corte)).sum())
        fp_tras = int(((regla_umbral == 1) & (p1 >= corte) & (y == 0)).sum())
        compuerta.append({"corte": corte, "respuestas_retiradas": retiradas, "fp": fp_tras})
    corte_cobertura = max(
        [c["corte"] for c in compuerta if c["respuestas_retiradas"] == 0], default=0.0
    )

    # ---------------- Modelo 2: relevancia de pasajes (RF-15) ----------------
    prosa = np.isin(particiones, ["E", "F"])
    Xp, yp = X[prosa], y[prosa]
    res_pas, prob_pas = validar("pasajes", Xp, yp, cv)
    p2 = prob_pas["regresion_logistica"]
    regla_pasajes = np.array(
        [1 if d["pasajes"] > 0 else 0 for d, m in zip(decisiones, prosa, strict=True) if m]
    )
    linea_base_pasajes = metricas(yp, regla_pasajes.astype(float))
    combinada = []
    for corte in REJILLA:
        muestra = (regla_pasajes == 1) & (p2 >= corte)
        combinada.append(
            {
                "corte": corte,
                "cobertura_E": round(float(muestra[yp == 1].mean()), 4),
                "falsos_positivos_F": round(float(muestra[yp == 0].mean()), 4),
                "f1": round(float(f1_score(yp, muestra.astype(int))), 4),
            }
        )
    mejor = max(combinada, key=lambda c: (c["f1"], c["corte"]))
    corte_pasajes = mejor["corte"]

    # ---------------- Entrenamiento final y artefactos ----------------
    fecha = datetime.now(timezone.utc).isoformat(timespec="seconds")
    final_cob = candidatos()["regresion_logistica"].fit(X, y)
    final_pas = candidatos()["regresion_logistica"].fit(Xp, yp)
    meta_cob = {
        "nombre": "Predictor de cobertura documental",
        "historia": "HU-08.1",
        "requisito": "RF-14",
        "algoritmo": "Regresion logistica (scikit-learn), caracteristicas estandarizadas",
        "entrenado": fecha,
        "n_entrenamiento": int(len(y)),
        "corte_operacion": corte_cobertura,
        "validacion_cruzada": res_cob["regresion_logistica"],
        "coeficientes": coeficientes(final_cob),
        "comparacion": {
            "regresion_logistica": res_cob["regresion_logistica"],
            "bosque_aleatorio": res_cob["bosque_aleatorio"],
            "linea_base_mayoritaria": res_cob["linea_base_mayoritaria"],
            "regla_umbral_pmv1": linea_base_regla,
        },
        "por_particion": por_particion,
        "roc": curva(y, p1),
    }
    meta_pas = {
        "nombre": "Predictor de relevancia de pasajes",
        "historia": "HU-04",
        "requisito": "RF-15",
        "algoritmo": "Regresion logistica (scikit-learn), caracteristicas estandarizadas",
        "entrenado": fecha,
        "n_entrenamiento": int(len(yp)),
        "corte_operacion": corte_pasajes,
        "validacion_cruzada": res_pas["regresion_logistica"],
        "coeficientes": coeficientes(final_pas),
        "comparacion": {
            "regresion_logistica": res_pas["regresion_logistica"],
            "bosque_aleatorio": res_pas["bosque_aleatorio"],
            "linea_base_mayoritaria": res_pas["linea_base_mayoritaria"],
            "regla_palabras_pmv1": linea_base_pasajes,
        },
        "regla_mas_modelo": mejor,
        "roc": curva(yp, p2),
    }
    guardar_modelo(MODELOS / "cobertura.joblib", final_cob, meta_cob)
    guardar_modelo(MODELOS / "relevancia_pasajes.joblib", final_pas, meta_pas)

    informe = {
        "fecha": fecha,
        "semilla": SEMILLA,
        "corpus": configuracion.ruta_corpus.name,
        "umbral_tau": configuracion.umbral_abstencion,
        "caracteristicas": list(NOMBRES),
        "cobertura": {
            "metadatos": meta_cob,
            "comparacion_cv": res_cob,
            "linea_base_regla_umbral": linea_base_regla,
            "por_particion": por_particion,
            "compuerta_rn06": compuerta,
            "roc": curva(y, p1),
        },
        "pasajes": {
            "metadatos": meta_pas,
            "comparacion_cv": res_pas,
            "linea_base_regla_palabras": linea_base_pasajes,
            "regla_mas_modelo": combinada,
            "punto_elegido": mejor,
            "roc": curva(yp, p2),
        },
    }
    texto = json.dumps(informe, ensure_ascii=False, indent=2)
    (MODELOS / "metricas.json").write_text(texto, encoding="utf-8")
    (salida / "metricas.json").write_text(texto, encoding="utf-8")

    with (salida / "predicciones_cv.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "id",
                "particion",
                "etiqueta",
                "responde_umbral",
                "pasajes_regla",
                "p_cobertura_cv",
                "p_pasajes_cv",
            ]
        )
        j = 0
        for i, fila in enumerate(conjunto):
            pp = ""
            if prosa[i]:
                pp = round(float(p2[j]), 4)
                j += 1
            w.writerow(
                [
                    fila["id"],
                    fila["particion"],
                    fila["etiqueta"],
                    regla_umbral[i],
                    decisiones[i]["pasajes"],
                    round(float(p1[i]), 4),
                    pp,
                ]
            )

    print(f"[COBERTURA] corte de operacion {corte_cobertura} (0 respuestas retiradas en CV)")
    print(f"[PASAJES]   linea base regla: {linea_base_pasajes}")
    print(f"[PASAJES]   regla + modelo:   {mejor}")
    print(f"[SALIDA]    {MODELOS} y {salida}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ.parent / "docs" / "evidencias" / "pmv2")
