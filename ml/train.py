"""
Flight departure-delay model training (label: dep_delay >= 15 min).

Honest-workflow rules:
  * Split BY DATE, never randomly: random splits leak same-day/same-route
    information between train and test and flatter every metric.
  * Baseline FIRST (logistic regression, 5 features) and reported permanently.
  * Multi-model tournament & ensembling:
      - Logistic Regression (Baseline)
      - LightGBM Classifier (Fast GBDT)
      - XGBoost Classifier (Regularized GBDT)
      - CatBoost Classifier (Native Categorical GBDT)
      - Soft-Voting Ensemble (Combines all 3 tree models)
  * `month` is excluded from model inputs to prevent unseen-category extrapolation.

Commands:
    python ml/train.py --model baseline
    python ml/train.py --model lgbm
    python ml/train.py --model xgboost
    python ml/train.py --model catboost
    python ml/train.py --model ensemble
    python ml/train.py --model tournament   # Runs all, builds leaderboard & model card

Artifacts -> ml/artifacts/ (models, metrics.json, serving lookups)
Plots     -> docs/img/ml_feature_importance.png
Card      -> docs/model_card.md
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import duckdb
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             precision_score, recall_score, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from config import get_postgres_engine, settings
from ml.ensemble import SoftVotingEnsemble

ART = Path(__file__).resolve().parent / "artifacts"
IMG = Path(__file__).resolve().parents[1] / "docs" / "img"
CARD = Path(__file__).resolve().parents[1] / "docs" / "model_card.md"

SPLITS_BTS = {
    "train": ("2024-02-01", "2024-05-31"),
    "val":   ("2024-06-01", "2024-06-30"),
    "test":  ("2025-01-01", "2025-01-31"),
}

BASELINE_FEATURES = ["dep_hour", "route_delay_rate_30d", "carrier_delay_rate_30d",
                     "scheduled_departures_hour", "distance_miles"]
NUMERIC_FEATURES = BASELINE_FEATURES + ["route_flights_30d", "day_of_week"]
CATEGORICAL_FEATURES = ["distance_bucket", "carrier_type", "is_weekend"]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
LABEL = "is_delayed_dep"


def load_frame() -> pd.DataFrame:
    """Load feature matrix from active warehouse (PostgreSQL or DuckDB)."""
    cols = f"flight_date, {LABEL}, {', '.join(ALL_FEATURES)}"
    
    if settings.warehouse == "postgres":
        eng = get_postgres_engine()
        # Check both raw and marts schemas
        try:
            df = pd.read_sql(f"select {cols} from marts.fct_features_flight", eng)
        except Exception:
            df = pd.read_sql(f"select {cols} from raw.fct_features_flight", eng)
    else:
        con = duckdb.connect(str(settings.duckdb_path), read_only=True)
        try:
            try:
                df = con.sql(f"select {cols} from marts.fct_features_flight").df()
            except Exception:
                try:
                    df = con.sql(f"select {cols} from main.fct_features_flight").df()
                except Exception:
                    df = con.sql(f"select {cols} from fct_features_flight").df()
        finally:
            con.close()

    df["flight_date"] = pd.to_datetime(df["flight_date"])
    for c in ["distance_bucket", "carrier_type"]:
        df[c] = df[c].astype("category")
    df["is_weekend"] = df["is_weekend"].astype(int)
    df[LABEL] = df[LABEL].astype(int)
    return df


def split(df: pd.DataFrame):
    """
    Split data by flight_date (chronological, leakage-free).
    If large multi-month/BTS dataset is detected, use BTS 6-month holdout split.
    Otherwise, split chronologically: 60% Train, 20% Val, 20% Test.
    """
    min_date = df["flight_date"].min()
    max_date = df["flight_date"].max()
    span_days = (max_date - min_date).days

    if span_days >= 180 and max_date.year > min_date.year:
        out = {}
        for name, (a, b) in SPLITS_BTS.items():
            m = (df["flight_date"] >= a) & (df["flight_date"] <= b)
            out[name] = df.loc[m]
        return out["train"], out["val"], out["test"], SPLITS_BTS

    # Chronological temporal split for synthetic / quarterly data
    dates = np.sort(df["flight_date"].unique())
    n = len(dates)
    i_val = max(1, int(n * 0.60))
    i_test = max(i_val + 1, int(n * 0.80))

    t_train = (dates[0], dates[i_val - 1])
    t_val = (dates[i_val], dates[i_test - 1])
    t_test = (dates[i_test], dates[-1])

    split_meta = {
        "train": (pd.Timestamp(t_train[0]).strftime("%Y-%m-%d"), pd.Timestamp(t_train[1]).strftime("%Y-%m-%d")),
        "val":   (pd.Timestamp(t_val[0]).strftime("%Y-%m-%d"), pd.Timestamp(t_val[1]).strftime("%Y-%m-%d")),
        "test":  (pd.Timestamp(t_test[0]).strftime("%Y-%m-%d"), pd.Timestamp(t_test[1]).strftime("%Y-%m-%d")),
    }

    train = df[(df["flight_date"] >= t_train[0]) & (df["flight_date"] <= t_train[1])]
    val = df[(df["flight_date"] >= t_val[0]) & (df["flight_date"] <= t_val[1])]
    test = df[(df["flight_date"] >= t_test[0]) & (df["flight_date"] <= t_test[1])]
    return train, val, test, split_meta


def pick_threshold(y_val, p_val) -> float:
    """Choose operating threshold on VALIDATION (max F1)."""
    from sklearn.metrics import precision_recall_curve

    prec, rec, thr = precision_recall_curve(y_val, p_val)
    f1 = 2 * prec[:-1] * rec[:-1] / np.clip(prec[:-1] + rec[:-1], 1e-9, None)
    return float(thr[int(np.argmax(f1))])


def evaluate(y_true, p, threshold: float) -> dict:
    yhat = (p >= threshold).astype(int)
    k = max(1, len(p) // 10)
    top_idx = np.argsort(p)[-k:]
    y_arr = np.asarray(y_true)
    base = float(np.mean(y_arr))
    prec_top = float(np.mean(y_arr[top_idx]))
    return {
        "auc": round(float(roc_auc_score(y_true, p)), 4),
        "avg_precision": round(float(average_precision_score(y_true, p)), 4),
        "brier": round(float(brier_score_loss(y_true, p)), 4),
        "precision@t": round(float(precision_score(y_true, yhat, zero_division=0)), 4),
        "recall@t": round(float(recall_score(y_true, yhat, zero_division=0)), 4),
        "threshold": round(threshold, 4),
        "precision@top10pct": round(prec_top, 4),
        "lift@top10pct": round(prec_top / max(base, 1e-9), 2),
        "base_rate": round(base, 4),
        "n": int(len(y_true)),
    }


def _update_metrics(key: str, payload: dict) -> dict:
    ART.mkdir(parents=True, exist_ok=True)
    path = ART / "metrics.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    data[key] = payload
    data["updated_at"] = datetime.utcnow().isoformat()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def train_baseline(df: pd.DataFrame, return_model: bool = False):
    print("--- Training Baseline: Logistic Regression ---")
    train, val, test, _ = split(df)
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("clf", LogisticRegression(max_iter=1000, n_jobs=-1, random_state=42))])
    pipe.fit(train[BASELINE_FEATURES], train[LABEL])
    p_val = pipe.predict_proba(val[BASELINE_FEATURES])[:, 1]
    thr = pick_threshold(val[LABEL], p_val)
    res = {
        "val": evaluate(val[LABEL], p_val, thr),
        "test": evaluate(test[LABEL], pipe.predict_proba(test[BASELINE_FEATURES])[:, 1], thr),
        "features": BASELINE_FEATURES,
        "model_type": "LogisticRegression",
    }
    joblib.dump(pipe, ART / "baseline_logreg.joblib")
    _update_metrics("baseline_logreg", res)
    print("Baseline test metrics:", json.dumps(res["test"], indent=2))
    if return_model:
        return pipe, res
    return res


def train_lgbm(df: pd.DataFrame, return_model: bool = False):
    import lightgbm as lgb
    print("--- Training LightGBM Classifier ---")
    train, val, test, _ = split(df)
    clf = lgb.LGBMClassifier(
        n_estimators=500, learning_rate=0.06, num_leaves=31,
        subsample=0.8, colsample_bytree=0.8, n_jobs=4, random_state=42,
    )
    clf.fit(
        train[ALL_FEATURES], train[LABEL],
        eval_set=[(val[ALL_FEATURES], val[LABEL])],
        eval_metric="auc",
        callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(0)]
    )
    p_val = clf.predict_proba(val[ALL_FEATURES])[:, 1]
    thr = pick_threshold(val[LABEL], p_val)
    res = {
        "val": evaluate(val[LABEL], p_val, thr),
        "test": evaluate(test[LABEL], clf.predict_proba(test[ALL_FEATURES])[:, 1], thr),
        "features": ALL_FEATURES,
        "best_iteration": int(clf.best_iteration_ or 0),
        "model_type": "LightGBM",
    }
    joblib.dump(clf, ART / "lgbm_delay.joblib")
    _update_metrics("lgbm", res)
    print("LightGBM test metrics:", json.dumps(res["test"], indent=2))
    _plot_importance(clf, "LightGBM")
    if return_model:
        return clf, res
    return res


def train_xgboost(df: pd.DataFrame, return_model: bool = False):
    import xgboost as xgb
    print("--- Training XGBoost Classifier ---")
    train, val, test, _ = split(df)
    clf = xgb.XGBClassifier(
        n_estimators=400, learning_rate=0.06, max_depth=6,
        subsample=0.8, colsample_bytree=0.8, enable_categorical=True,
        eval_metric="logloss", early_stopping_rounds=30, n_jobs=4, random_state=42,
    )
    clf.fit(
        train[ALL_FEATURES], train[LABEL],
        eval_set=[(val[ALL_FEATURES], val[LABEL])],
        verbose=False,
    )
    p_val = clf.predict_proba(val[ALL_FEATURES])[:, 1]
    thr = pick_threshold(val[LABEL], p_val)
    res = {
        "val": evaluate(val[LABEL], p_val, thr),
        "test": evaluate(test[LABEL], clf.predict_proba(test[ALL_FEATURES])[:, 1], thr),
        "features": ALL_FEATURES,
        "best_iteration": int(clf.best_iteration or 0),
        "model_type": "XGBoost",
    }
    joblib.dump(clf, ART / "xgboost_delay.joblib")
    _update_metrics("xgboost", res)
    print("XGBoost test metrics:", json.dumps(res["test"], indent=2))
    if return_model:
        return clf, res
    return res


def train_catboost(df: pd.DataFrame, return_model: bool = False):
    import catboost as cb
    print("--- Training CatBoost Classifier ---")
    train, val, test, _ = split(df)
    cat_cols = ["distance_bucket", "carrier_type"]
    clf = cb.CatBoostClassifier(
        iterations=400, learning_rate=0.06, depth=6,
        cat_features=cat_cols, eval_metric="Logloss",
        early_stopping_rounds=30, verbose=0, random_seed=42,
    )
    clf.fit(
        train[ALL_FEATURES], train[LABEL],
        eval_set=(val[ALL_FEATURES], val[LABEL]),
        verbose=False,
    )
    p_val = clf.predict_proba(val[ALL_FEATURES])[:, 1]
    thr = pick_threshold(val[LABEL], p_val)
    res = {
        "val": evaluate(val[LABEL], p_val, thr),
        "test": evaluate(test[LABEL], clf.predict_proba(test[ALL_FEATURES])[:, 1], thr),
        "features": ALL_FEATURES,
        "best_iteration": int(clf.get_best_iteration() or 0),
        "model_type": "CatBoost",
    }
    joblib.dump(clf, ART / "catboost_delay.joblib")
    _update_metrics("catboost", res)
    print("CatBoost test metrics:", json.dumps(res["test"], indent=2))
    if return_model:
        return clf, res
    return res


def train_ensemble(df: pd.DataFrame, trained_models: dict | None = None, return_model: bool = False):
    print("--- Training Soft-Voting Ensemble (LightGBM + CatBoost + XGBoost) ---")
    train, val, test, _ = split(df)
    
    if trained_models is None:
        m_lgb, _ = train_lgbm(df, return_model=True)
        m_cat, _ = train_catboost(df, return_model=True)
        m_xgb, _ = train_xgboost(df, return_model=True)
        models = {"lgbm": m_lgb, "catboost": m_cat, "xgboost": m_xgb}
    else:
        models = trained_models

    ensemble = SoftVotingEnsemble(models=models)
    p_val = ensemble.predict_proba(val[ALL_FEATURES])[:, 1]
    thr = pick_threshold(val[LABEL], p_val)
    res = {
        "val": evaluate(val[LABEL], p_val, thr),
        "test": evaluate(test[LABEL], ensemble.predict_proba(test[ALL_FEATURES])[:, 1], thr),
        "features": ALL_FEATURES,
        "weights": ensemble.weights,
        "model_type": "SoftVotingEnsemble",
    }
    joblib.dump(ensemble, ART / "ensemble_delay.joblib")
    _update_metrics("ensemble", res)
    print("Ensemble test metrics:", json.dumps(res["test"], indent=2))
    if return_model:
        return ensemble, res
    return res


def run_tournament(df: pd.DataFrame) -> None:
    """Run full tournament across all candidate models, rank, and save best model."""
    print("==================================================================")
    print("       [TOURNAMENT] FLIGHT DELAY MODEL TOURNAMENT & ENSEMBLING    ")
    print("==================================================================")
    
    _, _, _, split_meta = split(df)
    print(f"Dataset split: Train {split_meta['train']} | Val {split_meta['val']} | Test {split_meta['test']}")

    # 1. Train individual models
    pipe_base, res_base = train_baseline(df, return_model=True)
    m_lgb, res_lgb = train_lgbm(df, return_model=True)
    m_xgb, res_xgb = train_xgboost(df, return_model=True)
    m_cat, res_cat = train_catboost(df, return_model=True)

    # 2. Train ensemble
    models_dict = {"lgbm": m_lgb, "catboost": m_cat, "xgboost": m_xgb}
    m_ens, res_ens = train_ensemble(df, trained_models=models_dict, return_model=True)

    candidates = {
        "baseline_logreg": (pipe_base, res_base),
        "lgbm": (m_lgb, res_lgb),
        "xgboost": (m_xgb, res_xgb),
        "catboost": (m_cat, res_cat),
        "ensemble": (m_ens, res_ens),
    }

    # 3. Print Leaderboard Table
    print("\n" + "=" * 90)
    print(f"{'Model Name':<20} | {'ROC-AUC':<8} | {'PR-AUC':<8} | {'Brier':<8} | {'Recall@T':<8} | {'Lift@10%':<8} | {'Threshold':<8}")
    print("-" * 90)
    
    ranked = sorted(candidates.items(), key=lambda x: (x[1][1]["test"]["auc"], x[1][1]["test"]["lift@top10pct"]), reverse=True)
    for name, (_, r) in ranked:
        t = r["test"]
        print(f"{name:<20} | {t['auc']:<8.4f} | {t['avg_precision']:<8.4f} | {t['brier']:<8.4f} | {t['recall@t']:<8.4f} | {t['lift@top10pct']:<8.2f} | {t['threshold']:<8.4f}")
    print("=" * 90)

    winner_name, (winner_model, winner_res) = ranked[0]
    print(f"\n>>> TOURNAMENT WINNER: [{winner_name.upper()}] with Test AUC = {winner_res['test']['auc']:.4f} and Lift@10% = {winner_res['test']['lift@top10pct']}x")

    # Persist as best model for API serving
    joblib.dump(winner_model, ART / "best_delay_model.joblib")
    _update_metrics("best_model", {"winner": winner_name, "metrics": winner_res["test"]})

    # Export lookups and model card
    _export_serving_lookups()
    metrics = json.loads((ART / "metrics.json").read_text(encoding="utf-8"))
    _write_model_card(metrics, split_meta)
    print("\nTournament complete! Artifacts, lookups, and Model Card saved successfully.")


def _plot_importance(clf, model_name: str = "LightGBM") -> None:
    try:
        import matplotlib
        # Avoid forcing Agg backend if running in interactive notebook/ipykernel
        if "ipykernel" not in sys.modules and not matplotlib.get_backend().startswith("module://"):
            try:
                matplotlib.use("Agg")
            except Exception:
                pass
        import matplotlib.pyplot as plt

        IMG.mkdir(parents=True, exist_ok=True)
        if hasattr(clf, "feature_importances_"):
            imp = pd.Series(clf.feature_importances_, index=ALL_FEATURES).sort_values()
        elif hasattr(clf, "get_feature_importance"):
            imp = pd.Series(clf.get_feature_importance(), index=ALL_FEATURES).sort_values()
        else:
            return

        fig, ax = plt.subplots(figsize=(8, 5))
        imp.plot.barh(ax=ax, color="#2a9d8f")
        ax.set_title(f"{model_name} Feature Importance (splits)", fontweight="bold")
        fig.tight_layout()
        fig.savefig(IMG / "ml_feature_importance.png", dpi=120)
        plt.close(fig)
        print(f"wrote {IMG / 'ml_feature_importance.png'}")
    except Exception as e:
        print(f"Warning: could not plot feature importance: {e}")


def _export_serving_lookups() -> None:
    """Export latest rolling rates per route/carrier + congestion medians for the API."""
    print("Exporting serving lookup tables...")
    query = """
        select origin_airport, dest_airport, carrier_code, flight_date, dep_hour,
               route_delay_rate_30d, route_flights_30d, distance_miles,
               carrier_type, carrier_delay_rate_30d, scheduled_departures_hour
        from marts.fct_features_flight
    """
    if settings.warehouse == "postgres":
        eng = get_postgres_engine()
        try:
            df = pd.read_sql(query, eng)
        except Exception:
            df = pd.read_sql(query.replace("marts.", "raw."), eng)
    else:
        con = duckdb.connect(str(settings.duckdb_path), read_only=True)
        try:
            try:
                df = con.sql(query).df()
            except Exception:
                df = con.sql(query.replace("marts.", "")).df()
        finally:
            con.close()

    df["flight_date"] = pd.to_datetime(df["flight_date"])
    ART.mkdir(parents=True, exist_ok=True)

    # 1. Route lookup
    routes = (
        df.sort_values("flight_date", ascending=False)
        .groupby(["origin_airport", "dest_airport"])
        .first()
        .reset_index()[["origin_airport", "dest_airport", "route_delay_rate_30d", "route_flights_30d", "distance_miles"]]
    )
    routes.to_parquet(ART / "route_lookup.parquet")

    # 2. Carrier lookup
    carriers = (
        df.sort_values("flight_date", ascending=False)
        .groupby("carrier_code")
        .first()
        .reset_index()[["carrier_code", "carrier_type", "carrier_delay_rate_30d"]]
    )
    carriers.to_parquet(ART / "carrier_lookup.parquet")

    # 3. Congestion lookup
    congestion = (
        df.groupby(["origin_airport", "dep_hour"])["scheduled_departures_hour"]
        .median()
        .round()
        .astype(int)
        .reset_index()
    )
    congestion.to_parquet(ART / "congestion_lookup.parquet")
    print(f"Exported {len(routes):,} routes, {len(carriers)} carriers, {len(congestion):,} congestion lookups.")


def _write_model_card(metrics: dict, split_meta: dict) -> None:
    updated_at = metrics.get("updated_at", datetime.utcnow().isoformat())[:16]
    best_info = metrics.get("best_model", {})
    winner = best_info.get("winner", "lgbm").upper()

    rows_leaderboard = []
    for k in ["baseline_logreg", "lgbm", "xgboost", "catboost", "ensemble"]:
        if k in metrics:
            m = metrics[k]["test"]
            rows_leaderboard.append(
                f"| `{k}` | {m['auc']:.4f} | {m['avg_precision']:.4f} | {m['brier']:.4f} | "
                f"{m['precision@t']:.4f} | {m['recall@t']:.4f} | {m['lift@top10pct']:.2f}x | {m['threshold']:.4f} |"
            )
    leaderboard_md = "\n".join(rows_leaderboard)

    CARD.write_text(f"""# Model Card — Flight Departure-Delay Classifier & Model Tournament

_Last trained {updated_at}Z · Artifacts saved in `ml/artifacts/`_

## 1. Intended Use
Rank upcoming flights by probability of a **departure delay ≥ 15 minutes** for **operations planning** (crew buffers, gate staffing, proactive rebooking triage). 
*NOT for passenger-facing promises or automated decisions about individuals — it predicts flight operations, not people.*

## 2. Data & Leakage-Free Temporal Split
Trained on the dbt feature mart `fct_features_flight` built from the warehouse.
**Split strictly by date, never randomly**:

| Split | Window | Notes |
|---|---|---|
| **Train** | {split_meta['train'][0]} → {split_meta['train'][1]} | Training window |
| **Validation** | {split_meta['val'][0]} → {split_meta['val'][1]} | Early stopping & threshold tuning (Max F1) |
| **Test** | {split_meta['test'][0]} → {split_meta['test'][1]} | Out-of-time holdout evaluation |

**Why a date split:** Random splits leak same-day/same-route patterns between train and test. Chronological splits guarantee that historical features (rolling 30-day rates) do not contaminate future observations.

## 3. Tournament Leaderboard (Holdout Test Evaluation)

| Model Candidate | ROC-AUC | PR-AUC | Brier Score | Precision@T | Recall@T | Lift @ Riskiest 10% | Operating Threshold |
|---|---|---|---|---|---|---|---|
{leaderboard_md}

**Tournament Winner**: **`{winner}`** selected as the production model (`ml/artifacts/best_delay_model.joblib`).

## 4. Key Metrics Interpretation
* **Top-Decile Lift (>= 1.5x)**: Identifies flights in the riskiest 10% probability decile. A lift of >= 1.5x indicates high concentration of actual delays, crucial for operational prioritization.
* **Operating Threshold ($T$)**: Tuned on the **Validation** set to maximize F1-score rather than using the default 0.5 threshold (due to class imbalance ~18-20%).
* **Brier Score**: Measures probability calibration (lower is better, 0 = perfect calibration).

## 5. Feature Architecture ({len(ALL_FEATURES)} Features)
Defined, tested, and documented **in dbt** (`models/ml/_ml_models.yml`), shared verbatim between training and real-time serving:
* **Schedule facts**: `dep_hour`, `day_of_week`, `is_weekend`, `distance_miles`, `distance_bucket`, `carrier_type`.
* **Congestion**: `scheduled_departures_hour` (scheduled departures known in advance).
* **Rolling history**: 30-day rolling delay rates for route (`route_delay_rate_30d`) and carrier (`carrier_delay_rate_30d`), window ending the day before flight.

## 6. Limitations & Governance
* **Weather signal**: Missing direct terminal weather (partially absorbed by rolling rates).
* **Class imbalance**: Delays account for ~18-21% of flights.
* **Cold start**: Newly introduced routes/carriers fall back to population medians.
""", encoding="utf-8")
    print(f"wrote updated model card to {CARD}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--model",
        choices=["baseline", "lgbm", "xgboost", "catboost", "ensemble", "tournament"],
        default="tournament",
        help="Model architecture to train, or 'tournament' to evaluate and compare all.",
    )
    args = ap.parse_args()
    ART.mkdir(parents=True, exist_ok=True)
    
    frame = load_frame()
    print(f"Loaded {len(frame):,} rows from warehouse '{settings.warehouse}'")
    
    if args.model == "baseline":
        train_baseline(frame)
    elif args.model == "lgbm":
        train_lgbm(frame)
    elif args.model == "xgboost":
        train_xgboost(frame)
    elif args.model == "catboost":
        train_catboost(frame)
    elif args.model == "ensemble":
        train_ensemble(frame)
    elif args.model == "tournament":
        run_tournament(frame)
