"""
Unit tests for Data Contracts and Great Expectations validation gateway.
"""
from __future__ import annotations

import json
from pathlib import Path

from quality.contracts.contract_loader import (
    DEFAULT_CONTRACT_PATH,
    get_expectations_for_source,
    load_raw_data_contract,
)
from quality.validate import run as run_validation, REPORT_PATH, SUMMARY_MD_PATH


def test_load_raw_data_contract_structure():
    """Verify raw_data_contract.yaml loads and has valid contract metadata."""
    assert DEFAULT_CONTRACT_PATH.exists(), f"Contract file missing at {DEFAULT_CONTRACT_PATH}"
    contract = load_raw_data_contract()
    assert contract["version"] == "1.0.0"
    assert contract["layer"] == "raw"
    assert "contracts" in contract

    tables = ["flights", "airports", "carriers", "weather"]
    for table in tables:
        assert table in contract["contracts"], f"Table {table} missing from data contract"
        assert "columns" in contract["contracts"][table]
        assert "grain" in contract["contracts"][table]
        assert "expectations" in contract["contracts"][table]


def test_get_expectations_resolution():
    """Verify reference mapping correctly resolves airport and cancellation codes."""
    suites = get_expectations_for_source("synthetic")
    assert "flights" in suites
    assert "airports" in suites
    assert "carriers" in suites
    assert "weather" in suites

    # Check origin airport reference was resolved to a non-empty list
    flight_specs = suites["flights"]
    origin_spec = next(s for s in flight_specs if s["k"].get("column") == "origin")
    assert "value_set" in origin_spec["k"]
    assert len(origin_spec["k"]["value_set"]) >= 40
    assert "ATL" in origin_spec["k"]["value_set"]

    # Check cancellation codes reference resolved
    canc_spec = next(s for s in flight_specs if s["k"].get("column") == "cancellation_code")
    assert set(canc_spec["k"]["value_set"]) == {"A", "B", "C", "D"}


def test_bts_suites_definition():
    """Verify BTS suites load properly and handle empty weather contract."""
    suites = get_expectations_for_source("bts")
    assert len(suites["flights"]) > 0
    assert len(suites["airports"]) > 0
    assert len(suites["carriers"]) > 0
    assert suites["weather"] == []


def test_validation_execution_monitor_mode():
    """Verify validation runs in monitor mode and outputs both JSON and Markdown reports."""
    exit_code = run_validation(strict=False, table_filter="airports")
    assert exit_code == 0

    assert REPORT_PATH.exists()
    assert SUMMARY_MD_PATH.exists()

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert "metadata" in report
    assert "summary" in report
    assert report["summary"]["total"] >= 5
    assert report["summary"]["passed"] == report["summary"]["total"]

    summary_text = SUMMARY_MD_PATH.read_text(encoding="utf-8")
    assert "DATA QUALITY VALIDATION REPORT" in summary_text
    assert "airports" in summary_text
