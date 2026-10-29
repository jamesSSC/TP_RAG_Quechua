"""Siembra la base de la nube (Neon) con el corpus y sus fuentes. Idempotente.

Lee DATABASE_URL de backend/.env (o del entorno); la cadena nunca se imprime. Aplica las tablas
de los modelos, `db/postgres/esquema.sql` y `db/postgres/procedimientos.sql`, carga los
fragmentos con su procedencia y registra una fuente por documento. Volver a ejecutarlo no
duplica nada: los fragmentos y las fuentes tienen identificador fijo.

Las fuentes se registran con la procedencia que consta en el corpus (documento, paginas, OCR);
entidad publicadora y licencia quedan como «pendiente de verificar» (ADR-015): no se inventan.

Uso, desde backend/:
    python scripts/sembrar_nube.py [ruta_fragmentos.jsonl] [--rotulo "corpus reconstruido, no v3"]
"""

import argparse
import hashlib
import sys
import uuid
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import create_engine, text  # noqa: E402

from adapters.out.documentos.corpus_jsonl import cargar_fragmentos  # noqa: E402
from adapters.out.persistencia.repositorio_corpus_postgres import (  # noqa: E402
    RepositorioCorpusPostgres,
    instalar_todo,
)
from infrastructure.config import configuracion, normalizar_database_url  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
ESPACIO_FUENTES = uuid.UUID("6f1c2a52-6a7e-4c1e-9d0b-6b8f1e2a0c31")
PENDIENTE = "Pendiente de verificar (ADR-015)"


def _fuentes(fragmentos) -> list[dict]:
    por_documento = defaultdict(list)
    for f in fragmentos:
        por_documento[f.procedencia.documento].append(f)
    return [
        {
            "id": str(uuid.uuid5(ESPACIO_FUENTES, documento)),
            "titulo": Path(documento).stem[:300],
            "entidad": PENDIENTE,
            "licencia": PENDIENTE,
            "fecha": date.today(),
            "archivo": documento,
            "paginas": max(f.procedencia.pagina for f in grupo),
            "con_texto": len({f.procedencia.pagina for f in grupo}),
            "ocr": any(f.procedencia.derivado_ocr for f in grupo),
        }
        for documento, grupo in sorted(por_documento.items())
    ]


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument(
        "corpus", nargs="?", type=Path, default=RAIZ / "data" / "fragmentos_v3.jsonl"
    )
    argumentos.add_argument("--rotulo", default="", help="rotulo del corpus para el informe")
    args = argumentos.parse_args()

    if not configuracion.database_url:
        print("[SEMBRAR] falta DATABASE_URL en backend/.env o en el entorno", file=sys.stderr)
        return 2
    if not args.corpus.exists():
        print(f"[SEMBRAR] no existe {args.corpus}", file=sys.stderr)
        return 2

    fragmentos = cargar_fragmentos(args.corpus)
    sha = hashlib.sha256(args.corpus.read_bytes()).hexdigest()
    print(f"[SEMBRAR] corpus {args.corpus.name}: {len(fragmentos)} fragmentos, sha256 {sha}")
    if args.rotulo:
        print(f"[SEMBRAR] rotulo: {args.rotulo}")

    motor = create_engine(
        normalizar_database_url(configuracion.database_url),
        hide_parameters=True,
        pool_pre_ping=True,
        connect_args={"prepare_threshold": None},
    )
    instalar_todo(motor)
    print("[SEMBRAR] esquema y procedimientos instalados")

    repo = RepositorioCorpusPostgres(motor)
    nuevos = 0
    for inicio in range(0, len(fragmentos), 500):
        nuevos += repo.agregar(fragmentos[inicio : inicio + 500])
    print(f"[SEMBRAR] fragmentos nuevos: {nuevos}")

    fuentes = _fuentes(fragmentos)
    with motor.begin() as c:
        antes = c.execute(text("SELECT COUNT(*) FROM fuentes")).scalar_one()
        c.execute(
            text(
                "INSERT INTO fuentes (id, titulo, entidad_publicadora, licenciamiento, "
                "fecha_extraccion, nombre_archivo, paginas_totales, paginas_con_texto, "
                "derivado_ocr) VALUES (:id, :titulo, :entidad, :licencia, :fecha, :archivo, "
                ":paginas, :con_texto, :ocr) ON CONFLICT (id) DO NOTHING"
            ),
            fuentes,
        )
        despues = c.execute(text("SELECT COUNT(*) FROM fuentes")).scalar_one()
    print(f"[SEMBRAR] fuentes nuevas: {despues - antes}")

    with motor.connect() as c:
        total = c.execute(text("SELECT COUNT(*) FROM fragmentos")).scalar_one()
        documentos = c.execute(text("SELECT * FROM fn_fragmentos_por_documento()")).all()
        consultas = c.execute(text("SELECT COUNT(*) FROM consultas")).scalar_one()
        rutinas = c.execute(
            text(
                "SELECT p.proname, CASE p.prokind WHEN 'p' THEN 'PROCEDURE' ELSE 'FUNCTION' END "
                "FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
                "WHERE n.nspname = 'public' "
                "AND (p.proname LIKE 'sp\\_%' OR p.proname LIKE 'fn\\_%') "
                "ORDER BY 1"
            )
        ).all()
    print(f"[SEMBRAR] conteos: fragmentos={total} fuentes={despues} consultas={consultas}")
    for documento, n, paginas in documentos:
        print(f"    {n:5d} fragmentos  {paginas:4d} paginas  {documento}")
    print("[SEMBRAR] rutinas: " + ", ".join(f"{n} ({k})" for n, k in rutinas))
    motor.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(main())
