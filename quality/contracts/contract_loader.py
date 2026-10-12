"""
Contract Loader: parses and resolves declarative data contracts for Great Expectations.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from data.reference import AIRPORTS, CANCELLATION_CODES

CONTRACTS_DIR = Path(__file__).resolve().parent
DEFAULT_CONTRACT_PATH = CONTRACTS_DIR / "raw_data_contract.yaml"

REFERENCE_MAPPING: dict[str, list[Any]] = {
    "VALID_AIRPORTS": [a[0] for a in AIRPORTS],
    "CANCELLATION_CODES": list(CANCELLATION_CODES),
}


def load_raw_data_contract(path: Path | str | None = None) -> dict[str, Any]:
    """Load the YAML data contract file."""
    contract_file = Path(path) if path else DEFAULT_CONTRACT_PATH
    if not contract_file.exists():
        raise FileNotFoundError(f"Data contract file not found: {contract_file}")
    with open(contract_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_expectations_for_source(
    source_mode: str = "synthetic",
    contract_path: Path | str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Extract and resolve Great Expectations suites for all tables in a source mode.

    Resolves dynamic reference sets (e.g. valid airport codes, cancellation codes)
    into concrete expectation kwargs.
    """
    contract_data = load_raw_data_contract(contract_path)
    contracts = contract_data.get("contracts", {})
    suites: dict[str, list[dict[str, Any]]] = {}

    for table_name, table_spec in contracts.items():
        exp_specs = table_spec.get("expectations", {}).get(source_mode, [])
        table_suite: list[dict[str, Any]] = []

        for exp in exp_specs:
            kwargs = dict(exp.get("kwargs", {}))
            if "use_reference" in kwargs:
                ref_key = kwargs.pop("use_reference")
                if ref_key in REFERENCE_MAPPING:
                    kwargs["value_set"] = REFERENCE_MAPPING[ref_key]

            table_suite.append({
                "e": exp["expectation"],
                "k": kwargs,
                "sev": exp.get("severity", "critical"),
                "description": exp.get("description", ""),
            })

        suites[table_name] = table_suite

    return suites
