"""PMV2 · adaptador del modelo de scikit-learn: carga, compatibilidad del vector y prediccion."""

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

from adapters.out.prediccion.predictor_sklearn import PredictorSklearn
from domain.services.caracteristicas_consulta import NOMBRES, extraer_caracteristicas


def _vector():
    return extraer_caracteristicas("zorro", ["zorro"], [], [], 0.0)


def test_sin_artefacto_el_predictor_no_esta_disponible(tmp_path):
    p = PredictorSklearn(tmp_path / "no_existe.joblib")
    assert not p.disponible()
    assert p.probabilidad(_vector()) is None


def test_artefacto_de_otro_vector_se_rechaza(tmp_path):
    ruta = tmp_path / "viejo.joblib"
    joblib.dump({"estimador": object(), "caracteristicas": ["otra"], "metadatos": {}}, ruta)
    assert not PredictorSklearn(ruta).disponible()


def test_artefacto_valido_devuelve_una_probabilidad(tmp_path):
    X = np.array([[0.0] * len(NOMBRES), [1.0] * len(NOMBRES)] * 5)
    y = np.array([0, 1] * 5)
    ruta = tmp_path / "m.joblib"
    joblib.dump(
        {
            "estimador": LogisticRegression().fit(X, y),
            "caracteristicas": list(NOMBRES),
            "metadatos": {"nombre": "prueba"},
        },
        ruta,
    )
    p = PredictorSklearn(ruta)
    assert p.disponible()
    assert 0.0 <= p.probabilidad(_vector()) <= 1.0
    assert p.metadatos()["nombre"] == "prueba"
