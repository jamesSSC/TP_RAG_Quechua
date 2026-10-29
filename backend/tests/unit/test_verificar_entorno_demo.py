"""P0-B7: cada comprobacion del verificador, con el entorno simulado (presente / ausente)."""

import importlib.util
import sys
from pathlib import Path

import pytest

RUTA = Path(__file__).resolve().parents[2] / "scripts" / "verificar_entorno_demo.py"
spec = importlib.util.spec_from_file_location("verificar_entorno_demo", RUTA)
v = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v  # los dataclass lo necesitan
spec.loader.exec_module(v)


def test_python_antiguo_es_critico():
    assert not v.comprobar_python((3, 11)).ok
    assert v.comprobar_python((3, 12)).ok


def test_dependencias_ausentes_se_nombran():
    r = v.comprobar_dependencias(("a", "b"), buscar=lambda n: None if n == "b" else object())
    assert not r.ok and r.critico and "b" in r.detalle and "a," not in r.detalle
    assert v.comprobar_dependencias(("a",), buscar=lambda n: object()).ok


def test_archivo_presente_y_ausente(tmp_path):
    (tmp_path / "x.bin").write_bytes(b"1")
    assert v.comprobar_archivo("x", tmp_path / "x.bin").ok
    r = v.comprobar_archivo("y", tmp_path / "no.bin", ayuda="hagalo")
    assert not r.ok and r.critico and "hagalo" in r.detalle
    assert not v.comprobar_archivo("z", tmp_path / "no.bin", critico=False).critico


def test_datos_fuera_de_git_distinguen_criticos_de_avisos(tmp_path):
    (tmp_path / "evaluacion_v2.json").write_text("[]")
    (tmp_path / "traduccion_en_es.json").write_text("{}")
    corpus = tmp_path / "fragmentos_v3.jsonl"
    resultados = v.comprobar_datos_fuera_de_git(tmp_path, corpus)
    por_nombre = {r.nombre: r for r in resultados}
    assert not por_nombre["Corpus segmentado (fuera de Git)"].ok
    assert por_nombre["Corpus segmentado (fuera de Git)"].critico
    prosa = por_nombre["Evaluacion de prosa (fuera de Git)"]
    assert not prosa.ok and not prosa.critico and prosa.simbolo == "⚠"


def _joblib_falso(tmp_path, nombre, contenido=b"x" * 1000):
    (tmp_path / nombre).write_bytes(contenido)


def test_modelos_ausentes_son_criticos(tmp_path):
    _joblib_falso(tmp_path, "cobertura.joblib")
    cob, pas = v.comprobar_modelos(tmp_path, cargar=lambda ruta: object())
    assert cob.ok and not pas.ok and pas.critico


def test_modelo_vacio_o_truncado_da_error(tmp_path):
    _joblib_falso(tmp_path, "cobertura.joblib", b"")
    _joblib_falso(tmp_path, "relevancia_pasajes.joblib", b"abc")
    cob, pas = v.comprobar_modelos(tmp_path, cargar=lambda ruta: object())
    assert not cob.ok and cob.critico and "vacio" in cob.detalle
    assert not pas.ok and "truncado" in pas.detalle


def test_modelo_corrupto_que_no_carga_da_error(tmp_path):
    _joblib_falso(tmp_path, "cobertura.joblib")
    _joblib_falso(tmp_path, "relevancia_pasajes.joblib")

    def corrupto(ruta):
        raise ValueError("pickle roto")

    cob, pas = v.comprobar_modelos(tmp_path, cargar=corrupto)
    assert not cob.ok and cob.critico and "no se puede cargar" in cob.detalle
    assert "pickle roto" not in cob.detalle


def test_los_modelos_reales_del_repositorio_cargan():
    carpeta = Path(__file__).resolve().parents[2] / "modelos"
    assert all(r.ok for r in v.comprobar_modelos(carpeta)), "modelos versionados invalidos"


def _etiquetas(*nombres):
    return lambda url: {"models": [{"name": n} for n in nombres]}


def test_ollama_con_el_modelo_y_precalentado():
    llamado = []
    r = v.comprobar_ollama(
        "http://x", "qwen3.5:4b", _etiquetas("qwen3.5:4b"), lambda: llamado.append(1) or True
    )
    assert [x.ok for x in r] == [True, True] and llamado == [1]


def test_ollama_exige_exactamente_el_modelo_configurado():
    # Otra etiqueta de la misma familia NO sirve.
    r = v.comprobar_ollama("http://x", "qwen3.5:4b", _etiquetas("qwen3.5:9b", "qwen3.5:latest"))
    assert not r[0].ok and "qwen3.5:4b" in r[0].detalle
    assert v.comprobar_ollama("http://x", "qwen3.5:4b", _etiquetas("qwen3.5:4b"))[0].ok


def test_ollama_con_otro_modelo_configurado():
    assert v.comprobar_ollama("http://x", "otro:7b", _etiquetas("otro:7b"))[0].ok
    assert not v.comprobar_ollama("http://x", "otro:7b", _etiquetas("qwen3.5:4b"))[0].ok


def test_ollama_sin_etiqueta_acepta_latest():
    assert v.comprobar_ollama("http://x", "mistral", _etiquetas("mistral:latest"))[0].ok


def test_ollama_sin_el_modelo_es_critico_y_no_precalienta():
    llamado = []
    r = v.comprobar_ollama(
        "http://x", "qwen3.5:4b", _etiquetas("otro:7b"), lambda: llamado.append(1) or True
    )
    assert len(r) == 1 and not r[0].ok and "ollama pull" in r[0].detalle and llamado == []


def test_ollama_inalcanzable_es_critico():
    def falla(url):
        raise OSError("sin red")

    r = v.comprobar_ollama("http://x", "qwen3.5:4b", falla)
    assert not r[0].ok and r[0].critico and "ollama serve" in r[0].detalle


def test_precalentamiento_fallido_es_solo_aviso():
    r = v.comprobar_ollama("http://x", "qwen3.5:4b", _etiquetas("qwen3.5:4b"), lambda: False)
    assert not r[1].ok and not r[1].critico


def test_postgres_ok_y_caido():
    assert v.comprobar_postgres(lambda: "PostgreSQL 16").ok

    def cae():
        raise ConnectionError("clave: secreta")

    r = v.comprobar_postgres(cae)
    assert not r.ok and r.critico
    assert "secreta" not in r.detalle  # nunca se filtra el mensaje de la excepcion


def test_puertos_libres_o_ocupados():
    libres = v.comprobar_puertos(lambda p: False, False, lambda: 0)
    assert all(r.ok for r in libres) and len(libres) == 2
    ocupados = v.comprobar_puertos(lambda p: p == 8000, False, lambda: 0)
    assert [r.ok for r in ocupados] == [False, True]


def test_app_levantada_exige_estado_200():
    ok = v.comprobar_puertos(lambda p: True, True, lambda: 200)
    assert all(r.ok for r in ok)
    mal = v.comprobar_puertos(lambda p: False, True, lambda: 0)
    assert not mal[0].ok and mal[0].critico
    assert not mal[1].ok and not mal[1].critico


def test_frontend_compilado_arrancable_o_ausente(tmp_path):
    interfaz, frontend = tmp_path / "interfaz", tmp_path / "frontend"
    assert not v.comprobar_frontend(interfaz, frontend, lambda: True).ok
    (frontend / "node_modules").mkdir(parents=True)
    assert v.comprobar_frontend(interfaz, frontend, lambda: True).ok
    assert not v.comprobar_frontend(interfaz, frontend, lambda: False).ok  # sin npm
    interfaz.mkdir()
    (interfaz / "index.html").write_text("<html>")
    assert v.comprobar_frontend(interfaz, frontend, lambda: False).ok


def test_codigo_de_salida_distingue_criticos_de_avisos(capsys):
    bien = v.Resultado("a", True, "ok")
    aviso = v.Resultado("b", False, "meh", critico=False)
    mal = v.Resultado("c", False, "roto")
    assert v.imprimir_y_codigo([bien, aviso], 1.0) == 0
    assert v.imprimir_y_codigo([bien, aviso, mal], 1.0) == 1
    salida = capsys.readouterr().out
    assert "✔ a" in salida and "⚠ b" in salida and "✖ c" in salida
    assert "3 comprobaciones" in salida and "NO ESTA LISTO" in salida


@pytest.mark.parametrize("critico,simbolo", [(True, "✖"), (False, "⚠")])
def test_simbolos(critico, simbolo):
    assert v.Resultado("x", False, "d", critico).simbolo == simbolo
