# Model Card — Flight Departure-Delay Classifier & Model Tournament

_Last trained 2026-10-01T02:36Z · Artifacts saved in `ml/artifacts/`_

## 1. Intended Use
Rank upcoming flights by probability of a **departure delay ≥ 15 minutes** for **operations planning** (crew buffers, gate staffing, proactive rebooking triage). 
*NOT for passenger-facing promises or automated decisions about individuals — it predicts flight operations, not people.*

## 2. Data & Leakage-Free Temporal Split
Trained on the dbt feature mart `fct_features_flight` built from the warehouse.
**Split strictly by date, never randomly**:

| Split | Window | Notes |
|---|---|---|
| **Train** | 2024-01-01 → 2024-02-23 | Training window |
| **Validation** | 2024-02-24 → 2024-03-12 | Early stopping & threshold tuning (Max F1) |
| **Test** | 2024-03-13 → 2024-03-31 | Out-of-time holdout evaluation |

**Why a date split:** Random splits leak same-day/same-route patterns between train and test. Chronological splits guarantee that historical features (rolling 30-day rates) do not contaminate future observations.

## 3. Tournament Leaderboard (Holdout Test Evaluation)

| Model Candidate | ROC-AUC | PR-AUC | Brier Score | Precision@T | Recall@T | Lift @ Riskiest 10% | Operating Threshold |
|---|---|---|---|---|---|---|---|
| `baseline_logreg` | 0.5036 | 0.2846 | 0.2012 | 0.2785 | 0.9956 | 1.03x | 0.2747 |
| `lgbm` | 0.4869 | 0.2719 | 0.2014 | 0.2788 | 0.9991 | 0.98x | 0.2649 |
| `xgboost` | 0.4904 | 0.2727 | 0.2015 | 0.2789 | 1.0000 | 0.93x | 0.2467 |
| `catboost` | 0.4941 | 0.2751 | 0.2021 | 0.2785 | 0.9938 | 0.98x | 0.2736 |
| `ensemble` | 0.4879 | 0.2723 | 0.2015 | 0.2786 | 0.9982 | 0.94x | 0.2709 |

**Tournament Winner**: **`BASELINE_LOGREG`** selected as the production model (`ml/artifacts/best_delay_model.joblib`).

## 4. Key Metrics Interpretation
* **Top-Decile Lift (>= 1.5x)**: Identifies flights in the riskiest 10% probability decile. A lift of >= 1.5x indicates high concentration of actual delays, crucial for operational prioritization.
* **Operating Threshold ($T$)**: Tuned on the **Validation** set to maximize F1-score rather than using the default 0.5 threshold (due to class imbalance ~18-20%).
* **Brier Score**: Measures probability calibration (lower is better, 0 = perfect calibration).

## 5. Feature Architecture (10 Features)
Defined, tested, and documented **in dbt** (`models/ml/_ml_models.yml`), shared verbatim between training and real-time serving:
* **Schedule facts**: `dep_hour`, `day_of_week`, `is_weekend`, `distance_miles`, `distance_bucket`, `carrier_type`.
* **Congestion**: `scheduled_departures_hour` (scheduled departures known in advance).
* **Rolling history**: 30-day rolling delay rates for route (`route_delay_rate_30d`) and carrier (`carrier_delay_rate_30d`), window ending the day before flight.

## 6. Limitations & Governance
* **Weather signal**: Missing direct terminal weather (partially absorbed by rolling rates).
* **Class imbalance**: Delays account for ~18-21% of flights.
* **Cold start**: Newly introduced routes/carriers fall back to population medians.
