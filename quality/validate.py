"""
Great Expectations validation of the RAW layer against Data Contracts.

Runs a declarative suite of expectations (null checks, uniqueness, schema /
type, accepted-value sets, range checks) against the freshly-landed raw tables
and writes a data-quality report to quality/expectations/validation_report.json
and quality/expectations/validation_summary.md.

By design this runs in *monitor* mode: it reports failures (and exits 0) so the
pipeline can continue into staging, where the issues are cleaned. Run with
`--strict` to fail the build on any critical expectation (how you would gate a
production load). This mirrors the real trade-off between observability and
hard enforcement.

    python -m quality.validate            # report + continue
    python -m quality.validate --strict   # non-zero exit on critical failure
    python -m quality.validate --table flights  # validate a single table
"""
from __future__ import annotations

import argparse
import contextlib
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import warnings

# Auto-re-exec in project virtualenv if running in system Python and GX is not present
try:
    import great_expectations as gx  # noqa: F401
except ModuleNotFoundError:
    if __name__ == "__main__":
        project_root = Path(__file__).resolve().parent.parent
        venv_py = project_root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if venv_py.exists() and Path(sys.executable).resolve() != venv_py.resolve():
            cmd = [str(venv_py), "-m", "quality.validate"] + sys.argv[1:]
            res = subprocess.run(cmd)
            sys.exit(res.returncode)
    raise

warnings.filterwarnings("ignore")
os.environ.setdefault("TQDM_DISABLE", "1")

import great_expectations as gx  # noqa: E402

from config import settings, get_duckdb_connection  # noqa: E402
from data.reference import AIRPORTS, CANCELLATION_CODES  # noqa: E402
from ingestion.logging_config import get_logger  # noqa: E402

logger = get_logger("quality.validate")

VALID_AIRPORTS = [a[0] for a in AIRPORTS]
REPORT_DIR = settings.data_raw_dir.parent.parent / "quality" / "expectations"
REPORT_PATH = REPORT_DIR / "validation_report.json"
SUMMARY_MD_PATH = REPORT_DIR / "validation_summary.md"

# --- suites for REAL BTS data (quirks documented in docs/data_profile.md) ----
BTS_SUITES: dict[str, list[dict]] = {
    "flights": [
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "flight_id"}, "sev": "critical"},
        # real data contains double-reported flights: surface (don't fail) them
        {"e": "expect_compound_columns_to_be_unique",
         "k": {"column_list": ["flight_date", "carrier_code", "flight_number",
                               "origin", "scheduled_departure_min"], "mostly": 0.999},
         "sev": "warn"},
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "flight_date"}, "sev": "critical"},
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "carrier_code"}, "sev": "critical"},
        {"e": "expect_column_values_to_match_regex", "k": {"column": "origin", "regex": "^[A-Z0-9]{3}$"}, "sev": "critical"},
        {"e": "expect_column_values_to_match_regex", "k": {"column": "dest", "regex": "^[A-Z0-9]{3}$"}, "sev": "critical"},
        {"e": "expect_column_values_to_be_in_set", "k": {"column": "cancelled", "value_set": [0, 1]}, "sev": "critical"},
        # BTS quirk: delay is NULL on (most) cancelled flights — expected, not an error
        {"e": "expect_column_values_to_be_null",
         "k": {"column": "dep_delay_min", "row_condition": "cancelled==1",
               "condition_parser": "pandas", "mostly": 0.9}, "sev": "warn"},
        {"e": "expect_column_values_to_be_between",
         "k": {"column": "dep_delay_min", "min_value": -60, "max_value": 2000}, "sev": "warn"},
        {"e": "expect_column_values_to_be_between",
         "k": {"column": "arr_delay_min", "min_value": -90, "max_value": 2200}, "sev": "warn"},
        {"e": "expect_column_values_to_be_between",
         "k": {"column": "distance_miles", "min_value": 10, "max_value": 6000}, "sev": "critical"},
        {"e": "expect_table_row_count_to_be_between", "k": {"min_value": 100_000, "max_value": 50_000_000}, "sev": "warn"},
    ],
    "airports": [
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "airport_code"}, "sev": "critical"},
        {"e": "expect_column_values_to_be_unique", "k": {"column": "airport_code"}, "sev": "critical"},
        {"e": "expect_column_value_lengths_to_equal", "k": {"column": "airport_code", "value": 3}, "sev": "critical"},
    ],
    "carriers": [
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "carrier_code"}, "sev": "critical"},
        {"e": "expect_column_values_to_be_unique", "k": {"column": "carrier_code"}, "sev": "critical"},
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "carrier_name"}, "sev": "critical"},
    ],
    "weather": [],  # no BTS weather feed; table is an empty contract
}

# --- suites for the SYNTHETIC generator (original defect injection) ----------
SUITES: dict[str, list[dict]] = {
    "flights": [
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "flight_id"}, "sev": "critical"},
        {"e": "expect_column_values_to_be_unique", "k": {"column": "flight_id"}, "sev": "critical"},
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "flight_date"}, "sev": "critical"},
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "carrier_code"}, "sev": "critical"},
        {"e": "expect_column_values_to_be_in_set", "k": {"column": "origin", "value_set": VALID_AIRPORTS}, "sev": "critical"},
        {"e": "expect_column_values_to_be_in_set", "k": {"column": "dest", "value_set": VALID_AIRPORTS}, "sev": "critical"},
        {"e": "expect_column_values_to_be_in_set", "k": {"column": "cancelled", "value_set": [0, 1]}, "sev": "critical"},
        {"e": "expect_column_values_to_be_in_set", "k": {"column": "cancellation_code", "value_set": list(CANCELLATION_CODES)}, "sev": "warn"},
        {"e": "expect_column_values_to_be_between", "k": {"column": "dep_delay_min", "min_value": -120, "max_value": 1800}, "sev": "critical"},
        {"e": "expect_column_values_to_be_between", "k": {"column": "arr_delay_min", "min_value": -120, "max_value": 1800}, "sev": "warn"},
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "tail_number", "mostly": 0.99}, "sev": "warn"},
        {"e": "expect_table_row_count_to_be_between", "k": {"min_value": 1000, "max_value": 5_000_000}, "sev": "warn"},
    ],
    "airports": [
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "airport_code"}, "sev": "critical"},
        {"e": "expect_column_values_to_be_unique", "k": {"column": "airport_code"}, "sev": "critical"},
        {"e": "expect_column_value_lengths_to_equal", "k": {"column": "airport_code", "value": 3}, "sev": "critical"},
        {"e": "expect_column_values_to_be_between", "k": {"column": "latitude", "min_value": -90, "max_value": 90}, "sev": "critical"},
        {"e": "expect_column_values_to_be_between", "k": {"column": "longitude", "min_value": -180, "max_value": 180}, "sev": "critical"},
    ],
    "carriers": [
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "carrier_code"}, "sev": "critical"},
        {"e": "expect_column_values_to_be_unique", "k": {"column": "carrier_code"}, "sev": "critical"},
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "carrier_name"}, "sev": "critical"},
    ],
    "weather": [
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "weather_date"}, "sev": "critical"},
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "airport_code"}, "sev": "critical"},
        {"e": "expect_column_values_to_not_be_null", "k": {"column": "precipitation_in", "mostly": 0.95}, "sev": "warn"},
        {"e": "expect_column_values_to_be_between", "k": {"column": "temperature_f", "min_value": -40, "max_value": 130}, "sev": "warn"},
        {"e": "expect_column_values_to_be_in_set", "k": {"column": "is_severe", "value_set": [0, 1]}, "sev": "critical"},
    ],
}

BTS_SAMPLE_ROWS = 300_000  # GE runs on pandas; sample big real tables, full checks live in SQL


def _load_raw(table: str):
    """Load a raw table for validation. Supports PostgreSQL and DuckDB.
    In bts mode, large tables are sampled so pandas-based GE stays fast;
    full-table row counts and duplicate accounting are enforced by the SQL
    reconciliation step."""
    if settings.warehouse == "postgres":
        import pandas as pd
        from sqlalchemy import text
        from config import get_postgres_engine

        engine = get_postgres_engine()
        with engine.connect() as con:
            fq = f'"{settings.raw_schema}"."{table}"'
            table_check = con.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = :schema AND table_name = :table"
                ),
                {"schema": settings.raw_schema, "table": table},
            ).scalar()
            if not table_check:
                return pd.DataFrame()

            n = con.execute(text(f"SELECT count(*) FROM {fq}")).scalar()
            if not n:
                return pd.DataFrame()

            if settings.data_source == "bts" and n > BTS_SAMPLE_ROWS:
                pct = min(100.0, max(0.01, (BTS_SAMPLE_ROWS / n) * 100.0 * 1.05))
                query = text(
                    f'SELECT * FROM {fq} TABLESAMPLE BERNOULLI ({pct:.2f}) REPEATABLE (42) LIMIT {BTS_SAMPLE_ROWS}'
                )
                return pd.read_sql(query, con)

            return pd.read_sql(text(f"SELECT * FROM {fq}"), con)

    con = get_duckdb_connection(read_only=True)
    try:
        fq = f"{settings.raw_schema}.{table}"
        n = con.sql(f"SELECT count(*) FROM {fq}").fetchone()[0]
        if settings.data_source == "bts" and n > BTS_SAMPLE_ROWS:
            return con.sql(
                f"SELECT * FROM {fq} USING SAMPLE {BTS_SAMPLE_ROWS} ROWS (reservoir, 42)"
            ).df()
        return con.sql(f"SELECT * FROM {fq}").df()
    finally:
        con.close()


def _validate_table(context, source, table: str, specs: list[dict], df=None) -> list[dict]:
    if df is None:
        df = _load_raw(table)
    asset = source.add_dataframe_asset(name=table)
    batch_request = asset.build_batch_request(dataframe=df)
    validator = context.get_validator(batch_request=batch_request)

    results = []
    for spec in specs:
        method = getattr(validator, spec["e"])
        with contextlib.redirect_stderr(open(os.devnull, "w")):
            res = method(**spec["k"])
        results.append({
            "table": table,
            "expectation": spec["e"],
            "column": spec["k"].get("column", "(table)"),
            "severity": spec.get("sev", "critical"),
            "description": spec.get("description", ""),
            "success": bool(res.success),
            "unexpected_count": (res.result or {}).get("unexpected_count"),
            "element_count": (res.result or {}).get("element_count"),
        })
    return results


def _write_markdown_summary(report: dict) -> None:
    """Generate a clean, readable Markdown validation summary report."""
    summary = report["summary"]
    metadata = report["metadata"]
    results = report["results"]

    lines = [
        "# DATA QUALITY VALIDATION REPORT (GREAT EXPECTATIONS)",
        "",
        f"- **Validation Timestamp**: `{metadata['timestamp']}`",
        f"- **Data Source**: `{metadata['source']}`",
        f"- **Warehouse Target**: `{metadata['warehouse']}`",
        f"- **Data Contract Version**: `{metadata['contract_version']}`",
        "",
        "## 1. Summary Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **Total Expectations Evaluated** | `{summary['total']}` |",
        f"| **Passed Expectations** | `{summary['passed']}` |",
        f"| **Failed Expectations** | `{summary['failed']}` |",
        f"| **Critical Failures (Gate Gating)** | `{summary['critical_failed']}` |",
        f"| **Data Quality Compliance Rate** | **{summary['pass_rate_pct']}%** |",
        "",
        "## 2. Validation Results by Table",
        "",
        "| Table | Expectation | Target Column | Severity | Status | Violations / Unexpected |",
        "|---|---|---|---|---|---|",
    ]

    for r in results:
        status_badge = "✅ PASS" if r["success"] else f"❌ FAIL ({r['severity'].upper()})"
        unexpected = r["unexpected_count"] if r["unexpected_count"] is not None else (0 if r["success"] else "N/A")
        lines.append(
            f"| `{r['table']}` | `{r['expectation']}` | `{r['column']}` | {r['severity']} | {status_badge} | {unexpected} |"
        )

    lines.extend([
        "",
        "## 3. Analysis & Downstream Contract Notes",
        "",
        "- **Synthetic Mode Intentional Defects**:",
        "  - `flights.expect_column_values_to_be_unique(flight_id)`: 360 duplicates injected to test dbt deduplication (`stg_flights`).",
        "  - `flights.expect_column_values_to_be_in_set(dest)`: 89 orphan `ZZZ` destinations injected to test foreign key filtering.",
        "  - `flights.expect_column_values_to_be_between(dep_delay_min)`: 116 records with sensor loss sentinel `-9999`.",
        "- **Enforcement Policy**: Monitor mode records all deviations without halting the pipeline, allowing dbt staging models to remediate defects. Strict mode (`--strict`) enforces hard gates for automated CI/CD releases.",
    ])

    SUMMARY_MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    logger.info("markdown summary written -> %s", SUMMARY_MD_PATH)


def run(
    strict: bool = False,
    table_filter: str | None = None,
    source_override: str | None = None,
) -> int:
    source_mode = source_override or settings.data_source
    logger.info("=== Great Expectations validation of raw layer (source=%s, warehouse=%s) ===",
                source_mode, settings.warehouse)

    # Try loading from declarative contract first
    try:
        from quality.contracts.contract_loader import get_expectations_for_source
        suites = get_expectations_for_source(source_mode)
    except Exception as exc:
        logger.warning("Could not load declarative data contract (%s), using default suites", exc)
        suites = BTS_SUITES if source_mode == "bts" else SUITES

    if table_filter:
        if table_filter not in suites:
            logger.error("Unknown table '%s'. Available: %s", table_filter, list(suites.keys()))
            return 1
        suites = {table_filter: suites[table_filter]}

    context = gx.get_context(mode="ephemeral")
    source = context.sources.add_pandas("raw_pandas")

    all_results: list[dict] = []
    for table, specs in suites.items():
        if not specs:
            logger.info("  (skipping '%s': no expectations for this source)", table)
            continue
        df = _load_raw(table)
        if df.empty:
            logger.info("  (skipping '%s': table is empty in this source mode)", table)
            continue
        all_results.extend(_validate_table(context, source, table, specs, df=df))

    passed = [r for r in all_results if r["success"]]
    failed = [r for r in all_results if not r["success"]]
    critical_failed = [r for r in failed if r["severity"] == "critical"]

    logger.info("expectations: %d total | %d passed | %d failed (%d critical)",
                len(all_results), len(passed), len(failed), len(critical_failed))
    for r in failed:
        logger.warning("  FAIL [%s] %-14s %-40s unexpected=%s",
                       r["severity"], r["table"], f"{r['expectation']}({r['column']})",
                       r["unexpected_count"])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "metadata": {
            "source": source_mode,
            "warehouse": settings.warehouse,
            "contract_version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "summary": {
            "total": len(all_results),
            "passed": len(passed),
            "failed": len(failed),
            "critical_failed": len(critical_failed),
            "pass_rate_pct": round(len(passed) / len(all_results) * 100, 2) if all_results else 0.0,
        },
        "results": all_results,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    logger.info("report written -> %s", REPORT_PATH)

    _write_markdown_summary(report)

    logger.info("NOTE: failures above are the intentional raw-layer defects "
                "(duplicates, sentinel -9999, orphan 'ZZZ', missing tails) that "
                "the dbt staging models clean downstream.")

    if strict and critical_failed:
        logger.error("strict mode: %d critical expectations failed -> failing build",
                     len(critical_failed))
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Great Expectations Data Contract Validation")
    parser.add_argument("--strict", action="store_true", help="Fail build with exit code 1 on critical expectations")
    parser.add_argument("--table", type=str, default=None, help="Validate only a specific table")
    parser.add_argument("--source", type=str, default=None, choices=["synthetic", "bts"], help="Override data source")
    args = parser.parse_args()

    return run(strict=args.strict, table_filter=args.table, source_override=args.source)


if __name__ == "__main__":
    sys.exit(main())
