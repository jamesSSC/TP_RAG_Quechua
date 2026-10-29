"""Carga HTTP de POST /api/consultas con Locust (P1-B10).

Mide la API, no la GPU: el servidor debe arrancarse con GENERADOR=literal y ORIGEN_CONSULTAS=carga,
sobre una base aparte (las consultas quedan rotuladas `carga` y no cuentan como demanda real).
Las consultas son las de evaluacion_v2.json (versionado); no se fabrica ninguna.

    locust -f scripts/carga/locustfile.py --headless -u 5 -r 5 -t 60s --host http://127.0.0.1:8003
"""

import json
import random
from pathlib import Path

from locust import HttpUser, constant, task

DATOS = Path(__file__).resolve().parents[2] / "data" / "evaluacion_v2.json"
CONSULTAS = [e["consulta"] for e in json.loads(DATOS.read_text(encoding="utf-8"))]
random.seed(2026)


class UsuarioLocal(HttpUser):
    # Sin tiempo de espera: bucle cerrado, mide el maximo que sostiene la API con N usuarios.
    wait_time = constant(0)

    @task
    def consultar(self):
        with self.client.post(
            "/api/consultas",
            json={"texto": random.choice(CONSULTAS)},
            name="POST /api/consultas",
            catch_response=True,
        ) as r:
            if r.status_code != 200:
                r.failure(f"HTTP {r.status_code}")
