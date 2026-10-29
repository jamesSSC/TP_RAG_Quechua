"""PMV2 · Prueba de no regresion del caso de uso con los dos predictores activos.

Ejecuta el caso de uso completo, tal como lo cablea el contenedor (umbral + regla de lema +
predictor de cobertura + predictor de pasajes), sobre las 415 consultas etiquetadas y compara
con el mismo caso de uso sin predictores (PMV1). Comprueba RN-06: con los predictores activos,
el conjunto de respuestas es un subconjunto del obtenido sin ellos.

Las cifras de generalizacion de los modelos son las de validacion cruzada
(scripts/entrenar_predictores.py); esto es una verificacion de comportamiento del sistema.

Uso, desde backend/:  python scripts/evaluar_pmv2.py [carpeta_evidencias]
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts"))

from entrenar_predictores import cargar_conjunto, caso_de_uso  # noqa: E402

from adapters.out.prediccion.predictor_sklearn import PredictorSklearn  # noqa: E402
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase  # noqa: E402
from infrastructure.config import configuracion  # noqa: E402


def con_predictores(base: ConsultarCorpusUseCase) -> ConsultarCorpusUseCase:
    return ConsultarCorpusUseCase(
        indice=base._indice,
        generador=base._generador,
        evaluador=base._evaluador,
        detector_idioma=base._detector,
        traductor=base._traductor,
        k=base._k,
        predictor_cobertura=PredictorSklearn(configuracion.ruta_modelo_cobertura),
        predictor_pasajes=PredictorSklearn(configuracion.ruta_modelo_pasajes),
        probabilidad_minima_cobertura=configuracion.probabilidad_minima_cobertura,
        probabilidad_minima_pasajes=configuracion.probabilidad_minima_pasajes,
    )


def resumir(uc, conjunto) -> tuple[dict, set]:
    resumen = defaultdict(lambda: defaultdict(int))
    responde = set()
    for fila in conjunto:
        r = uc.ejecutar(fila["consulta"])
        p = resumen[fila["particion"]]
        p["n"] += 1
        if not r.abstenida:
            p["responde"] += 1
            responde.add(fila["id"])
        elif r.pasajes:
            p["abstiene_con_pasajes"] += 1
        else:
            p["abstiene"] += 1
        if r.abstencion_por_predictor:
            p["abstenciones_del_predictor"] += 1
    return {k: dict(v) for k, v in sorted(resumen.items())}, responde


def main(salida: Path) -> None:
    conjunto = cargar_conjunto()
    base = caso_de_uso()
    pmv1, resp1 = resumir(base, conjunto)
    pmv2, resp2 = resumir(con_predictores(base), conjunto)
    informe = {
        "pmv1_sin_predictores": pmv1,
        "pmv2_con_predictores": pmv2,
        "rn06_respuestas_pmv2_subconjunto_de_pmv1": resp2 <= resp1,
        "respuestas_retiradas_por_predictor": sorted(resp1 - resp2),
        "fp_C_pmv2": pmv2.get("C", {}).get("responde", 0),
        "pasajes_mostrados_F_pmv1": pmv1.get("F", {}).get("abstiene_con_pasajes", 0),
        "pasajes_mostrados_F_pmv2": pmv2.get("F", {}).get("abstiene_con_pasajes", 0),
        "pasajes_mostrados_E_pmv1": pmv1.get("E", {}).get("abstiene_con_pasajes", 0),
        "pasajes_mostrados_E_pmv2": pmv2.get("E", {}).get("abstiene_con_pasajes", 0),
    }
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "no_regresion_pmv2.json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(informe, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ.parent / "docs" / "evidencias" / "pmv2")
