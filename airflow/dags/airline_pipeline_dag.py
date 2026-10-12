"""
Airflow DAG: airline_operations_pipeline

Orchestrates the daily automated batch pipeline:

    generate_data -> ingest_raw -> validate_raw (Great Expectations)
        -> dbt_build (staging -> dims/facts -> marts + tests)
        -> reconcile (source-to-target 100% accounting)
        -> export_marts (Parquet export for Power BI)

The Python stages import the project modules (the same code the local runner
uses); dbt runs as a BashOperator with dynamic --target matching the active
warehouse (PostgreSQL, DuckDB, or Snowflake). The project is mounted into the
Airflow containers at $PROJECT_DIR (see docker-compose.yml).
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

PROJECT_DIR = os.environ.get("PROJECT_DIR", "/opt/airflow/project")
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "depends_on_past": False,
}

# Dynamic warehouse & dbt target detection
WAREHOUSE = os.environ.get("WAREHOUSE", "postgres").lower()
DEFAULT_DBT_TARGET = (
    "postgres" if WAREHOUSE == "postgres"
    else ("snowflake" if WAREHOUSE == "snowflake" else "local")
)
DBT_TARGET = os.environ.get("DBT_TARGET", DEFAULT_DBT_TARGET)


# --- task callables (import inside to keep DAG parsing cheap) ----------------
def _generate(**_):
    from data.generate_data import main
    main()


def _ingest(**_):
    from ingestion.run_ingestion import run
    run()


def _validate(**_):
    from quality.validate import run
    # monitor mode: report defects but let the DAG continue into cleaning
    run(strict=False)


def _reconcile(**_):
    from quality.reconciliation import run
    if run() != 0:
        raise ValueError("Source-to-target reconciliation failed: unexplained row loss")


def _export_marts(**_):
    from scripts.export_marts import main
    main()


with DAG(
    dag_id="airline_operations_pipeline",
    description="End-to-end airline operations batch: ingest -> validate -> model -> reconcile -> export_marts",
    default_args=DEFAULT_ARGS,
    schedule="0 6 * * *",          # daily at 06:00
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["airline", "dbt", "great-expectations", "postgres", "duckdb", "powerbi"],
) as dag:

    generate_data = PythonOperator(
        task_id="generate_data",
        python_callable=_generate,
    )

    ingest_raw = PythonOperator(
        task_id="ingest_raw",
        python_callable=_ingest,
    )

    validate_raw = PythonOperator(
        task_id="validate_raw",
        python_callable=_validate,
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            f"cd {PROJECT_DIR}/dbt/airline_dwh && "
            f"DBT_TARGET={DBT_TARGET} "
            f"DBT_DUCKDB_PATH={PROJECT_DIR}/warehouse/airline.duckdb "
            f"dbt build --profiles-dir . --target {DBT_TARGET}"
        ),
    )

    reconcile = PythonOperator(
        task_id="reconcile",
        python_callable=_reconcile,
    )

    export_marts = PythonOperator(
        task_id="export_marts",
        python_callable=_export_marts,
    )

    # Automated 5-stage dependency chain:
    generate_data >> ingest_raw >> validate_raw >> dbt_build >> reconcile >> export_marts
