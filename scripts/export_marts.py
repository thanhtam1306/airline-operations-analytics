"""
Export the analytics marts to Parquet so BI tools without a DuckDB connector
(e.g. Power BI Desktop) can import them.

    python scripts/export_marts.py
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

# Auto-re-exec in project virtualenv if running in system Python and pandas/duckdb is not present
try:
    import pandas  # noqa: F401
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[1]
    venv_py = project_root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if venv_py.exists() and Path(sys.executable).resolve() != venv_py.resolve():
        cmd = [str(venv_py), str(Path(__file__).resolve())] + sys.argv[1:]
        res = subprocess.run(cmd)
        sys.exit(res.returncode)
    raise

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import duckdb

from config import settings

EXPORT_DIR = Path(__file__).resolve().parents[1] / "dashboards" / "powerbi" / "export"
MARTS = [
    "fact_flights", "fact_flight_delays", "dim_airport", "dim_airline",
    "dim_date", "route_performance", "delay_trends", "cancellations",
    "operational_kpis",
]


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    if settings.warehouse == "postgres":
        import pandas as pd
        from config import get_postgres_engine

        engine = get_postgres_engine()
        for table in MARTS:
            out = EXPORT_DIR / f"{table}.parquet"
            df = pd.read_sql(f"SELECT * FROM marts.{table}", con=engine)
            df.to_parquet(out, index=False)
            print(f"exported marts.{table:<20} rows={len(df):>8,} -> {out.name}")
        print(f"\nAll marts exported from PostgreSQL to {EXPORT_DIR}")
        return

    con = duckdb.connect(str(settings.duckdb_path), read_only=True)
    try:
        for table in MARTS:
            out = EXPORT_DIR / f"{table}.parquet"
            con.execute(f"COPY marts.{table} TO '{out}' (FORMAT PARQUET)")
            n = con.sql(f"SELECT COUNT(*) FROM marts.{table}").fetchone()[0]
            print(f"exported marts.{table:<20} rows={n:>8,} -> {out.name}")
    finally:
        con.close()
    print(f"\nAll marts exported to {EXPORT_DIR}")


if __name__ == "__main__":
    main()
