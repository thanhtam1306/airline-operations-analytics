# DATA QUALITY VALIDATION REPORT (GREAT EXPECTATIONS)

- **Validation Timestamp**: `2026-10-12T01:58:18.594619+00:00`
- **Data Source**: `synthetic`
- **Warehouse Target**: `postgres`
- **Data Contract Version**: `1.0.0`

## 1. Summary Metrics

| Metric | Value |
|---|---|
| **Total Expectations Evaluated** | `5` |
| **Passed Expectations** | `5` |
| **Failed Expectations** | `0` |
| **Critical Failures (Gate Gating)** | `0` |
| **Data Quality Compliance Rate** | **100.0%** |

## 2. Validation Results by Table

| Table | Expectation | Target Column | Severity | Status | Violations / Unexpected |
|---|---|---|---|---|---|
| `airports` | `expect_column_values_to_not_be_null` | `airport_code` | critical | ✅ PASS | 0 |
| `airports` | `expect_column_values_to_be_unique` | `airport_code` | critical | ✅ PASS | 0 |
| `airports` | `expect_column_value_lengths_to_equal` | `airport_code` | critical | ✅ PASS | 0 |
| `airports` | `expect_column_values_to_be_between` | `latitude` | critical | ✅ PASS | 0 |
| `airports` | `expect_column_values_to_be_between` | `longitude` | critical | ✅ PASS | 0 |

## 3. Analysis & Downstream Contract Notes

- **Synthetic Mode Intentional Defects**:
  - `flights.expect_column_values_to_be_unique(flight_id)`: 360 duplicates injected to test dbt deduplication (`stg_flights`).
  - `flights.expect_column_values_to_be_in_set(dest)`: 89 orphan `ZZZ` destinations injected to test foreign key filtering.
  - `flights.expect_column_values_to_be_between(dep_delay_min)`: 116 records with sensor loss sentinel `-9999`.
- **Enforcement Policy**: Monitor mode records all deviations without halting the pipeline, allowing dbt staging models to remediate defects. Strict mode (`--strict`) enforces hard gates for automated CI/CD releases.