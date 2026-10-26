"""Precalcula datos para la web: entrada tabular → Parquet + JSON estáticos.

Uso: python data_build.py <entrada.(csv|parquet|json)> <dir de salida> [--sql "SELECT ..."]

Patrón del stack: Python hace el trabajo pesado en build; el navegador solo
filtra/pinta. Si DuckDB está instalado se usa (con --sql opcional sobre la
tabla `datos`); si no, cae a pandas puro. El JSON es para gráficas pequeñas
(<~5 MB); el Parquet para DuckDB-WASM en dashboards.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def leer(entrada: Path):
    import pandas as pd

    if not entrada.exists():
        sys.exit(f"ERROR: no existe {entrada}")
    if entrada.suffix == ".csv":
        df = pd.read_csv(entrada, encoding="utf-8")
    elif entrada.suffix == ".parquet":
        df = pd.read_parquet(entrada)
    elif entrada.suffix == ".json":
        df = pd.read_json(entrada, encoding="utf-8")
    else:
        sys.exit(f"ERROR: formato no soportado: {entrada.suffix}")
    if df.empty:
        sys.exit("ERROR: la entrada está vacía.")
    log.info("Entrada: %d filas × %d columnas", *df.shape)
    return df


def transformar(df, sql: str | None):
    if not sql:
        return df
    try:
        import duckdb
    except ImportError:
        sys.exit("ERROR: --sql requiere DuckDB (pip install duckdb).")
    con = duckdb.connect()
    con.register("datos", df)
    out = con.execute(sql).df()
    log.info("SQL aplicado: %d filas × %d columnas", *out.shape)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("entrada", type=Path)
    ap.add_argument("salida", type=Path)
    ap.add_argument("--sql", help="Query DuckDB sobre la tabla `datos`")
    args = ap.parse_args()

    df = transformar(leer(args.entrada), args.sql)
    args.salida.mkdir(parents=True, exist_ok=True)
    base = args.salida / args.entrada.stem
    df.to_parquet(f"{base}.parquet", index=False)
    Path(f"{base}.json").write_text(
        json.dumps(df.to_dict(orient="records"), ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    kb_p = Path(f"{base}.parquet").stat().st_size / 1024
    kb_j = Path(f"{base}.json").stat().st_size / 1024
    log.info("Escrito: %s.parquet (%.0f KB) y .json (%.0f KB)", base, kb_p, kb_j)
    if kb_j > 5000:
        log.warning(
            "El JSON supera 5 MB: usa el Parquet con DuckDB-WASM y borra el JSON."
        )


if __name__ == "__main__":
    main()
