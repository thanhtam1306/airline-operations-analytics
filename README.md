# Production-Grade Airline Data Platform & Operations Console

This README provides complete instructions for setting up the environment, executing the end-to-end data engineering and machine learning pipeline, and interacting with analytical dashboards and operations consoles.

---

## 1. Overview

**Airline Data Platform** is an enterprise-grade, production-ready data engineering and operational analytics platform. The system ingests large-scale airline operational data—supporting both real-world US Department of Transportation (US DOT BTS) datasets containing over **3.45 million flight records** and automated synthetic data feeds.

The end-to-end architecture covers data ingestion, Great Expectations data contract validation, Kimball star-schema dimensional modeling via dbt across multiple data warehouses (**DuckDB, PostgreSQL, and Snowflake**), a 5-model Machine Learning tournament for flight delay prediction, and real-time operational decision support through the **SkyOps Operations Console** and an audited 4-page **Power BI** semantic model.

The primary objective is to empower Operations Control Centers (OCC), flight dispatchers, and data analysts to detect delay root causes, prevent cascading turnaround delays, enforce international aviation regulatory compliance, and optimize fleet performance with data-driven precision.

---

## 2. Tech Stack & Libraries

- **Programming Language:** Python 3.10+
- **Execution & Development:** Visual Studio Code, Jupyter Notebook (`.ipynb`), CLI / Makefile
- **Data Ingestion & Processing:** `pandas`, `numpy`, `pyarrow`, `duckdb`, `psycopg2-binary`, `snowflake-connector-python`
- **Data Modeling & Warehousing:** `dbt-core` (v1.9), `dbt-duckdb`, `dbt-postgres`, `dbt-snowflake`
- **Data Quality & Governance:** `great-expectations` (v0.18), custom 100% row-level reconciliation engine
- **Workflow Orchestration:** Apache Airflow, Python orchestration runners
- **Machine Learning & Analytics:** `scikit-learn`, `lightgbm`, `xgboost`, `catboost`, `joblib`, `scipy`
- **API & Serving Framework:** `fastapi`, `uvicorn`, `pydantic` (v2)
- **Business Intelligence & Dashboards:** Microsoft Power BI Desktop (`.pbix`, DAX), Streamlit
- **Automated Reporting:** `python-pptx` (automated 16:9 executive presentation deck generation), automated HTML reports

---

## 3. Data Processing & Analytical Workflow

The end-to-end data pipeline follows this robust ELT and ML workflow:

```text
Flight Data Sources (US DOT BTS 3.45M CSVs / Synthetic Generator)
      |
      v
Data Ingestion Engine & Audit Logging (ingestion/)
      |
      v
Data Quality Contracts & Gateway (Great Expectations)
      |
      v
Data Warehousing Layer (DuckDB / PostgreSQL / Snowflake)
      |
      v
dbt Dimensional Modeling (Staging -> Dims & Facts -> Analytics Marts)
      |
      v
Data Reconciliation & Integrity Audit (100% Row Accounting)
      |
      v
ML Feature Store & Tournament (5 Competing Algorithms, Temporal Split)
      |
      v
Aviation Regulatory & Advisory Engine (FAA / DOT Compliance Rules)
      |
      v
FastAPI Real-Time Serving + OCC Operations Console + Power BI Dashboard
```

---

## 4. Key Highlights & Achievements

- **Dual Ingestion Scale:** Ingests **3,453,795 real US DOT BTS flight records** (~1.5 GB CSVs) in ~25 seconds, with seamless fallback to automated synthetic demo feeds.
- **Multi-Warehouse Architecture:** Runs locally on embedded DuckDB with zero cloud cost, connects directly to enterprise PostgreSQL, or switches to cloud Snowflake via a single `.env` toggle.
- **dbt Star Schema Modeling:** **56/56 models and schema tests pass green in 3.34 seconds** (Kimball star schema: staging, dimensions, facts, and ML feature tables).
- **Automated Data Quality Gateway:** Enforces schema and statistical expectations via Great Expectations (`monitor` and `strict` modes), accompanied by an automated reconciliation audit ensuring 100% row accounting.
- **5-Model ML Delay Tournament:** Evaluates Logistic Regression (baseline), LightGBM, CatBoost, XGBoost, and a Soft-Voting Ensemble using temporal train/validation/test splits, threshold optimization, and SHAP feature importance.
- **Aviation Regulatory Compliance Engine:** Grounded in US Federal Aviation Regulations (14 CFR § 259.4 tarmac delay limit, FAR Part 117 crew flight duty period, 14 CFR § 260.6 cash refunds, FAA \$101.18/min operating cost benchmark) and Vietnam Circular 19/2023/TT-BGTVT.
- **Audited 4-Page Power BI Suite:** Fully structured across the 4 stages of Gartner Analytics Maturity (Descriptive → Diagnostic → Bottleneck Deep-Dive → Predictive Governance) with 50+ DAX measures.
- **Operations Decision Support Console:** Real-time OCC flight dispatch console featuring a 40-topic domain knowledge base, What-If turnaround intervention simulator, 1-click PowerPoint (.pptx) export, and flight risk lookups.
- **Comprehensive Test Coverage:** **115/115 automated unit and integration tests passing 100% green**.

---

## 5. Dashboards & Visual Outputs

### Power BI Analytics Suite
The primary Power BI report file is located at:
```text
dashboards/powerbi/Dashboard.pbix
```

The underlying parquet export source used to refresh the Power BI model:
```text
dashboards/powerbi/export/*.parquet
```

The Power BI model follows the 4-page Gartner Analytics Maturity framework:
1. **Page 1: Executive Operations Overview (Descriptive Analytics)**
   - On-Time Performance (A14 OTP %), completion rate, direct delay cost exposure (\$101.18/min), and carrier market share.
2. **Page 2: Delay Root-Cause & Domino Propagation (Diagnostic Analytics)**
   - BTS 5-factor delay breakdown (Carrier, Weather, NAS, Security, Late Aircraft) and cascading turnaround delay analysis.
3. **Page 3: Hub Bottlenecks & Route Economics (Diagnostic Deep-Dive)**
   - Hub congestion matrix (DFW, ORD, ATL, JFK, DEN), taxi-out duration spikes (35–48 min), and evening departure banks.
4. **Page 4: Predictive Delay Risk & Regulatory Governance (Predictive & Prescriptive)**
   - ML tournament performance metrics (Holdout Test AUC 0.741+, Lift @ 10% 2.37x, Brier score), tarmac delay exposure, and embedded OCC Operations Console iframe.

### Model Feature Importance & Performance Preview:

![Feature Importance](<docs/img/ml_feature_importance.png>)

### Interactive Web Dashboards:
- **OCC Operations Console & API:** `http://localhost:8000` (or `http://skyops.local:8000`)
- **Embedded Operations Console for BI:** `http://localhost:8000/embed/chat?page=1`
- **Streamlit Operational Dashboard:** `http://localhost:8501`
- **FastAPI Interactive Swagger Docs:** `http://localhost:8000/docs`

---

## 6. Environment Requirements

Ensure the host machine satisfies the following prerequisites:

- **Python:** Version 3.10 or higher.
- **Visual Studio Code:** Recommended IDE with Python and Jupyter extensions.
- **Microsoft Power BI Desktop:** Required to open and refresh `dashboards/powerbi/Dashboard.pbix`.
- **Operating System:** Windows, macOS, or Linux.
- **Docker & Docker Compose (Optional):** Required only if running containerized Apache Airflow and PostgreSQL services.

All required Python dependencies are listed in `requirements.txt`.

---

## 7. Directory Structure

```text
airline-data-platform/
|
|-- airflow/                 # Apache Airflow DAGs and orchestration configuration
|   |-- dags/
|   |   `-- airline_pipeline_dag.py
|
|-- config/                  # Multi-warehouse database configuration (DuckDB, Postgres, Snowflake)
|   |-- config.py
|   `-- __init__.py
|
|-- data/                    # Data storage layer
|   |-- raw/                 # Raw BTS and synthetic CSV/parquet files
|   `-- clean/               # Cleaned datasets
|
|-- dashboards/              # Visual reporting layer
|   |-- powerbi/             # Power BI model (.pbix, measures.dax, export scripts, PBIR)
|   |   |-- Dashboard.pbix
|   |   |-- measures.dax
|   |   |-- PAGE_4_DESIGN.md
|   |   `-- export/
|   `-- streamlit_app.py     # 4-state Streamlit operational dashboard
|
|-- dbt/airline_dwh/         # dbt dimensional modeling project
|   |-- dbt_project.yml
|   |-- profiles.yml
|   `-- models/
|       |-- staging/         # stg_flights, stg_airports, stg_weather
|       |-- marts/           # dim_date, dim_aircraft, fact_flights, route_performance
|       `-- ml/              # fct_features_flight (feature store)
|
|-- docs/                    # Technical documentation, Model Cards, architectural diagrams
|   |-- model_card.md
|   |-- USER_GUIDE.md
|   `-- img/
|
|-- ingestion/               # Idempotent extract & load engine with audit logging
|   |-- load.py
|   |-- run_ingestion.py
|   `-- generate_synthetic.py
|
|-- ml/                      # Machine Learning tournament, API, and dispatch advisory engine
|   |-- advisory.py          # 3-layer grounding advisory & What-If simulator
|   |-- api.py               # FastAPI real-time serving endpoints
|   |-- chat.py              # Operational query routing engine
|   |-- copilot.py           # Aviation domain knowledge base & SOP checklists
|   |-- ensemble.py          # Soft-voting ensemble classifier
|   |-- regulatory_engine.py # Aviation regulatory compliance & penalty rules
|   |-- slide_generator.py   # PowerPoint (.pptx) & HTML slide deck generator
|   |-- train.py             # Tournament training pipeline across 5 algorithms
|   |-- web_ui.py            # Responsive OCC Cockpit & console interface
|   `-- artifacts/           # Trained models (.joblib), lookups (.parquet), and metrics.json
|
|-- quality/                 # Data Quality & Governance layer
|   |-- validate.py          # Great Expectations validation runner
|   |-- reconciliation.py   # Source-to-target 100% row-level reconciliation
|   |-- contracts/           # Data contract schemas (JSON)
|   `-- expectations/        # Great Expectations suites and summary reports
|
|-- scripts/                 # Parquet export utilities, setup scripts, and SSL tools
|   |-- export_marts.py
|   |-- export_ml_powerbi.py
|   `-- run_demo.py
|
|-- tests/                   # Automated pytest suite (115/115 tests passing)
|   |-- test_ml_api.py
|   |-- test_advisory.py
|   |-- test_copilot.py      # OCC advisory test suite
|   `-- test_data_contracts.py
|
|-- .env.example             # Environment variable template
|-- Makefile                 # CLI entrypoint commands
|-- README.md                # Project documentation
|-- requirements.txt         # Production Python dependencies
`-- START_SKYOPS.bat         # 1-click Windows launcher for OCC Console
```

---

## 8. Input Data

The platform natively supports two data input channels:

1. **Synthetic Demo Data (Default):**
   - Automatically generated via `ingestion/generate_synthetic.py`.
   - Produces realistic flights, airports, and weather records modeled with high peak congestion, seasonal weather spikes, and tail-number turnaround links.

2. **US DOT Bureau of Transportation Statistics (BTS) Real Data:**
   - Raw monthly flight performance CSV files placed in `data/raw/` (e.g., `T_ONTIME_REPORTING_*.csv`).
   - Supplemental lookup tables:
     - `data/raw/airports.csv` (ICAO/IATA coordinates, hub classifications).
     - `data/raw/weather.csv` (Hourly airport weather observations: METAR, precipitation, wind speed, visibility).

> **Note:** Raw CSV and Parquet files in `data/raw/` are automatically processed and ignored by version control to avoid repository bloat.

---

## 9. Installation & Getting Started

Open your terminal at the root directory of the project:

1. **Create a virtual environment:**

```bash
python -m venv .venv
```

2. **Activate the virtual environment:**

On Windows:
```powershell
.venv\Scripts\activate
```

On macOS / Linux:
```bash
source .venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

Copy the template file:
```bash
cp .env.example .env
```
*(The default configuration operates out-of-the-box using local DuckDB without requiring external credentials).*

5. **Launch in Visual Studio Code:**

```bash
code .
```

---

## 10. Pipeline Execution Order

To execute the entire data engineering, quality check, modeling, and serving lifecycle in sequential order, run:

1. **Data Ingestion:**
   ```bash
   python -m ingestion.run_ingestion
   ```
   *Ingests raw CSV/synthetic datasets into the raw data warehouse layer with audit logs.*

2. **Data Quality Validation (Great Expectations):**
   ```bash
   python -m quality.validate
   ```
   *Validates schemas, null constraints, and value ranges against pre-defined data contracts.*

3. **dbt Transformation & Modeling:**
   ```bash
   cd dbt/airline_dwh
   dbt run --profiles-dir .
   dbt test --profiles-dir .
   cd ../..
   ```
   *Builds staging views, Kimball dimensions, fact tables, and the ML feature store.*

4. **Source-to-Target Reconciliation:**
   ```bash
   python -m quality.reconciliation
   ```
   *Executes 100% row-level reconciliation between raw ingestion and dbt dimensional marts.*

5. **Machine Learning Tournament:**
   ```bash
   python -m ml.train
   ```
   *Trains 5 algorithms with temporal splits, optimizes decision thresholds, and exports artifacts to `ml/artifacts/`.*

6. **Power BI Marts Export:**
   ```bash
   python -m scripts.export_marts
   ```
   *Exports modeled dbt tables into high-performance Parquet format for Power BI ingestion.*

7. **Automated End-to-End Orchestration:**
   Alternatively, execute the complete pipeline in one single command:
   ```bash
   python -m orchestration.run_pipeline
   # or using Makefile:
   make pipeline
   ```

8. **Automated Test Suite Verification:**
   ```bash
   pytest -q
   ```
   *Runs all 115 test cases across ingestion, dbt models, API endpoints, advisory logic, and contracts.*

---

## 11. Output Deliverables & Artifacts

Upon completion of the pipeline, the following artifacts are generated:

- `warehouse/airline.duckdb`: Local analytical data warehouse containing raw, staging, and marts tables.
- `quality/expectations/validation_report.json`: Great Expectations data contract audit report.
- `quality/expectations/validation_summary.md`: Human-readable markdown summary of data contract validation.
- `ml/artifacts/`:
  - `best_delay_model.joblib`: Serialized tournament winner model.
  - `lgbm_delay.joblib`, `xgboost_delay.joblib`, `catboost_delay.joblib`: Competing model binaries.
  - `ensemble_delay.joblib`: Calibrated Soft-Voting Ensemble model.
  - `metrics.json`: Full tournament performance evaluation scorecard (AUC, Brier score, Lift @ 10%, F1, precision, recall).
  - `carrier_lookup.parquet`, `route_lookup.parquet`, `congestion_lookup.parquet`: Feature store lookup tables.
- `dashboards/powerbi/export/`: Parquet tables optimized for Power BI DirectQuery / Import modes.
- `dashboards/powerbi/Dashboard.pbix`: Production-ready Power BI reporting file.

---

## 12. Opening Dashboards & Operational Consoles

### 1. Launching SkyOps Operations Console & Serving API
You can start the operational dispatch platform using either method:

- **Windows 1-Click Launcher:** Double-click `START_SKYOPS.bat` (opens `http://skyops.local:8000` automatically).
- **Command Line:**
  ```bash
  python -m uvicorn ml.api:app --reload --host 0.0.0.0 --port 8000
  # or:
  make skyops
  ```

Access points:
- **OCC Operations Console & Dispatch Tools:** `http://localhost:8000`
- **Embedded Operations Console for Power BI:** `http://localhost:8000/embed/chat?page=1`
- **Interactive OpenAPI Documentation:** `http://localhost:8000/docs`

### 2. Launching the Streamlit Analytical Dashboard
```bash
streamlit run dashboards/streamlit_app.py
# or:
make dashboard
```
Opens an interactive operational dashboard at `http://localhost:8501`.

### 3. Opening the Power BI Dashboard
1. Open `dashboards/powerbi/Dashboard.pbix` in Microsoft Power BI Desktop.
2. Confirm the underlying data points to `dashboards/powerbi/export/`.
3. Click **Refresh** on the Home ribbon to synchronize visualizations with newly modeled data.

---

## 13. Troubleshooting & Common Issues

- **DuckDB File Lock Error (`IOException: Could not set lock on file`):**
  DuckDB allows multiple concurrent readers but only one active writer process. Ensure background processes (such as a running FastAPI server or a previous Python script) are completed before executing `dbt run` or `ingestion`.
- **Missing Module / Package Not Found:**
  Ensure the virtual environment is activated and reinstall dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- **Power BI Data Source Path Mismatch:**
  If the repository directory is moved to another folder, open Power BI Desktop, navigate to **Transform Data > Data Source Settings**, and update the path to the local `dashboards/powerbi/export/` directory.
- **Port 8000 Already in Use:**
  Run the server on a different port:
  ```bash
  python -m uvicorn ml.api:app --port 8080
  ```

---

## 14. Important Notes & Production Guidelines

- **Strict Temporal Data Splitting:** In predictive ML training, the train/validation/test split is strictly partitioned along chronological time boundaries (`FlightDate`) to prevent future lookahead data leakage.
- **Decision Threshold Optimization:** The delay risk classifier utilizes an optimized decision threshold tuned for high recall rather than the default 0.5 probability cutoff, prioritizing early warning over false dismissals.
- **Zero Cloud Cost by Default:** The default configuration runs entirely on local DuckDB storage. To switch to enterprise PostgreSQL or cloud Snowflake, update the `WAREHOUSE_TYPE` environment variable in `.env`.
- **Decision-Support Scope:** Operations dispatch recommendations and predictive outputs serve as decision-support tools for dispatchers and do not override mandatory airline Operations Specifications (OpSpecs) or pilot-in-command final authority.

---

## 15. Authors & Contributors

- **Nguyễn Hoàng Thanh Tâm** — Data Analyst
- **Architecture & References:** Built upon enterprise airline data platform patterns and open-source foundations.

---

## 16. Purpose of Use & License

This project is built for operational data engineering, machine learning research, and airline dispatch analytics.

- **License:** Open-source under the Apache License 2.0 / MIT License.
- **Data Attributions:** Real flight statistics provided by the Bureau of Transportation Statistics (BTS), US Department of Transportation.

---

## 17. Contact & Support

- **Author:** Nguyễn Hoàng Thanh Tâm (Data Analyst)
- **Email:** [tamnguyen130620004@gmail.com](mailto:tamnguyen130620004@gmail.com)
- **Issues & Contributions:** Feel free to open an issue or pull request for bugs, feature suggestions, or aviation regulatory updates.
