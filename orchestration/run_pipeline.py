"""
Local, no-Docker pipeline runner.

Executes the full automated flow in order and prints a timed summary:

    generate -> ingest -> validate (GE) -> dbt build -> reconcile -> export marts

This is the same sequence the Airflow DAG runs; keeping a plain-Python runner
means the project is demonstrable on any laptop without standing up Airflow.

    python -m orchestration.run_pipeline
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import time

# Auto-re-exec in project virtualenv if running in system Python and duckdb/dbt is not present
try:
    import duckdb  # noqa: F401
    import dbt  # noqa: F401
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[1]
    venv_py = project_root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if venv_py.exists() and Path(sys.executable).resolve() != venv_py.resolve():
        cmd = [str(venv_py), "-m", "orchestration.run_pipeline"] + sys.argv[1:]
        res = subprocess.run(cmd)
        sys.exit(res.returncode)
    raise

from config import settings, PROJECT_ROOT
from ingestion.logging_config import get_logger

logger = get_logger("orchestration")

DBT_DIR = PROJECT_ROOT / "dbt" / "airline_dwh"


def _last_source() -> str | None:
    """Which DATA_SOURCE last built this warehouse (None on first build)."""
    if settings.warehouse == "postgres":
        try:
            from config import get_postgres_engine
            from sqlalchemy import text
            engine = get_postgres_engine()
            with engine.connect() as con:
                con.execute(text(
                    f"CREATE TABLE IF NOT EXISTS {settings.raw_schema}._pipeline_meta "
                    f"(key VARCHAR PRIMARY KEY, value VARCHAR)"
                ))
                con.commit()
                row = con.execute(text(
                    f"SELECT value FROM {settings.raw_schema}._pipeline_meta WHERE key = 'last_source'"
                )).fetchone()
                return row[0] if row else None
        except Exception as exc:
            logger.debug("could not query last_source in postgres: %s", exc)
            return None

    try:
        import duckdb
        con = duckdb.connect(str(settings.duckdb_path))
        con.execute("CREATE TABLE IF NOT EXISTS main._pipeline_meta "
                    "(key VARCHAR PRIMARY KEY, value VARCHAR)")
        row = con.execute(
            "SELECT value FROM main._pipeline_meta WHERE key = 'last_source'"
        ).fetchone()
        con.close()
        return row[0] if row else None
    except Exception as exc:
        logger.debug("could not query last_source in duckdb: %s", exc)
        return None


def _record_source() -> None:
    """Persist current DATA_SOURCE to prevent dirty mixed builds across modes."""
    if settings.warehouse == "postgres":
        try:
            from config import get_postgres_engine
            from sqlalchemy import text
            engine = get_postgres_engine()
            with engine.connect() as con:
                con.execute(text(
                    f"CREATE TABLE IF NOT EXISTS {settings.raw_schema}._pipeline_meta "
                    f"(key VARCHAR PRIMARY KEY, value VARCHAR)"
                ))
                con.execute(text(
                    f"INSERT INTO {settings.raw_schema}._pipeline_meta (key, value) VALUES ('last_source', :src) "
                    f"ON CONFLICT (key) DO UPDATE SET value = :src"
                ), {"src": settings.data_source})
                con.commit()
        except Exception as exc:
            logger.warning("could not record last_source in postgres: %s", exc)
        return

    try:
        import duckdb
        con = duckdb.connect(str(settings.duckdb_path))
        con.execute("CREATE TABLE IF NOT EXISTS main._pipeline_meta "
                    "(key VARCHAR PRIMARY KEY, value VARCHAR)")
        con.execute("INSERT OR REPLACE INTO main._pipeline_meta VALUES ('last_source', ?)",
                    [settings.data_source])
        con.close()
    except Exception as exc:
        logger.warning("could not record last_source in duckdb: %s", exc)


def _get_dbt_target() -> str:
    """Resolve dbt target profile dynamically from warehouse settings."""
    wh = settings.warehouse.lower()
    if wh == "postgres":
        return "postgres"
    if wh == "snowflake":
        return "snowflake"
    return "local"


def _run_dbt() -> int:
    env = os.environ.copy()
    target = _get_dbt_target()
    env["DBT_TARGET"] = target
    env.setdefault("DBT_DUCKDB_PATH", str(settings.duckdb_path))

    cmd = [
        sys.executable, "-m", "dbt.cli.main", "build",
        "--profiles-dir", ".",
        "--target", target,
    ]

    # SOURCE GUARD: incremental models must never mix rows from different
    # sources. If this warehouse was last built from a different DATA_SOURCE
    # (e.g. bts -> synthetic), force a full refresh so facts and dimensions are
    # rebuilt consistently instead of appending across sources.
    last = _last_source()
    if last is not None and last != settings.data_source:
        logger.warning("source changed since last build (%s -> %s): forcing --full-refresh",
                       last, settings.data_source)
        cmd.append("--full-refresh")

    logger.info("running dbt build with target='%s' ...", target)
    proc = subprocess.run(cmd, cwd=DBT_DIR, env=env)
    if proc.returncode == 0:
        _record_source()
    return proc.returncode


def _run_export_marts() -> int:
    """Export analytics marts to Parquet for Power BI and external BI consumption."""
    from scripts.export_marts import main as export_marts
    logger.info("exporting marts to Parquet (warehouse=%s) ...", settings.warehouse)
    export_marts()
    return 0


def main() -> int:
    from data.generate_data import main as generate
    from ingestion.run_ingestion import run as ingest
    from quality.validate import run as validate
    from quality.reconciliation import run as reconcile

    stages = [
        ("generate", lambda: (generate(), 0)[1]),
        ("ingest", lambda: (ingest(), 0)[1]),
        ("validate (GE)", lambda: validate(strict=False)),  # monitor mode
        ("dbt build", _run_dbt),
        ("reconcile", reconcile),
        ("export marts", _run_export_marts),
    ]
    if settings.data_source == "bts":
        # real data: nothing to generate — the BTS files ARE the source
        stages = stages[1:]

    dbt_target = _get_dbt_target()
    logger.info("################ PIPELINE START (source=%s, warehouse=%s, dbt_target=%s) ################",
                settings.data_source, settings.warehouse, dbt_target)
    
    total_start = time.time()
    results, failed = [], False
    for name, fn in stages:
        t0 = time.time()
        try:
            rc = fn() or 0
        except Exception as exc:  # noqa: BLE001
            logger.exception("stage '%s' crashed: %s", name, exc)
            rc = 1
        elapsed = time.time() - t0
        status = "OK" if rc == 0 else "FAIL"
        results.append((name, status, f"{elapsed:5.1f}s"))
        logger.info(">>> stage '%s' finished: %s (%.1fs)", name, status, elapsed)
        if rc != 0 and name in ("dbt build", "reconcile"):  # hard-stop stages
            failed = True
            break

    total_elapsed = time.time() - total_start

    logger.info("################ PIPELINE SUMMARY ################")
    logger.info("  %-18s | %-6s | %-10s", "Stage", "Status", "Duration")
    logger.info("  " + "-" * 40)
    for name, status, elapsed in results:
        logger.info("  %-18s | %-6s | %-10s", name, status, elapsed)
    logger.info("  " + "-" * 40)
    logger.info("  Total Duration: %.2fs", total_elapsed)
    logger.info("################ %s ################", "FAILED" if failed else "SUCCESS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
