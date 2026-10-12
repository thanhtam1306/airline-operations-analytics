"""
Export Machine Learning & Regulatory Governance data to Parquet for Power BI Desktop.

Outputs:
1. dashboards/powerbi/export/ml_tournament_metrics.parquet
   - Model tournament leaderboard metrics (Baseline, LightGBM, XGBoost, CatBoost, Ensemble)
2. dashboards/powerbi/export/fct_flight_regulatory_predictions.parquet
   - Model predictions on flight feature dataset joined with Star Schema keys
   - Evaluated against US DOT / FAA / CAAV regulatory rules down to Article & Clause

Usage:
    python scripts/export_ml_powerbi.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

# Ensure root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import duckdb
import joblib
import numpy as np
import pandas as pd

from config import get_postgres_engine, settings

EXPORT_DIR = PROJECT_ROOT / "dashboards" / "powerbi" / "export"
ART_DIR = PROJECT_ROOT / "ml" / "artifacts"


def export_tournament_metrics() -> pd.DataFrame:
    """Read ml/artifacts/metrics.json and format into tabular Parquet."""
    metrics_path = ART_DIR / "metrics.json"
    if not metrics_path.exists():
        raise FileNotFoundError(f"Missing {metrics_path}. Please run: python ml/train.py --model tournament")

    raw_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    winner_name = raw_metrics.get("best_model", {}).get("winner", "baseline_logreg")

    display_names = {
        "baseline_logreg": "1. Logistic Regression (Baseline)",
        "lgbm": "2. LightGBM GBDT",
        "xgboost": "3. XGBoost Classifier",
        "catboost": "4. CatBoost Classifier",
        "ensemble": "5. Soft-Voting Ensemble",
    }

    rows = []
    for model_key in ["baseline_logreg", "lgbm", "xgboost", "catboost", "ensemble"]:
        if model_key not in raw_metrics:
            continue
        data = raw_metrics[model_key]
        val = data.get("val", {})
        test = data.get("test", {})
        feats = data.get("features", [])

        rows.append({
            "model_key": model_key,
            "model_name": display_names.get(model_key, model_key),
            "model_type": data.get("model_type", "MLModel"),
            "is_winner": (model_key == winner_name),
            "features_count": len(feats),
            "val_auc": float(val.get("auc", 0.0)),
            "val_avg_precision": float(val.get("avg_precision", 0.0)),
            "val_brier_score": float(val.get("brier", 0.0)),
            "val_threshold": float(val.get("threshold", 0.25)),
            "val_precision": float(val.get("precision@t", 0.0)),
            "val_recall": float(val.get("recall@t", 0.0)),
            "val_lift_top10pct": float(val.get("lift@top10pct", 1.0)),
            "test_auc": float(test.get("auc", 0.0)),
            "test_avg_precision": float(test.get("avg_precision", 0.0)),
            "test_brier_score": float(test.get("brier", 0.0)),
            "test_threshold": float(test.get("threshold", 0.25)),
            "test_precision": float(test.get("precision@t", 0.0)),
            "test_recall": float(test.get("recall@t", 0.0)),
            "test_lift_top10pct": float(test.get("lift@top10pct", 1.0)),
            "n_test_samples": int(test.get("n", 0)),
        })

    df = pd.DataFrame(rows)
    out_path = EXPORT_DIR / "ml_tournament_metrics.parquet"
    df.to_parquet(out_path, index=False)
    print(f"Exported {len(df)} models to {out_path.name}")
    return df


def export_regulatory_predictions() -> pd.DataFrame:
    """
    Score flight features using best model and evaluate aviation regulatory compliance.
    Includes foreign keys for Star Schema integration in Power BI.
    """
    query = """
        SELECT 
            feat.flight_id,
            feat.flight_date,
            feat.carrier_code,
            feat.origin_airport,
            feat.dest_airport,
            feat.dep_hour,
            feat.day_of_week,
            feat.month,
            feat.is_weekend,
            feat.distance_miles,
            feat.distance_bucket,
            feat.carrier_type,
            feat.scheduled_departures_hour,
            feat.route_delay_rate_30d,
            feat.route_flights_30d,
            feat.carrier_delay_rate_30d,
            f.date_key,
            f.origin_airport_key,
            f.dest_airport_key,
            f.airline_key,
            f.flight_number,
            f.tail_number,
            f.is_cancelled,
            f.is_delayed,
            f.arr_delay_min,
            f.dep_delay_min
        FROM fct_features_flight feat
        JOIN marts.fact_flights f ON feat.flight_id = f.flight_id
    """

    if settings.warehouse == "postgres":
        eng = get_postgres_engine()
        # In postgres, tables might be in marts or raw
        try:
            df = pd.read_sql(query, eng)
        except Exception:
            con = duckdb.connect(str(settings.duckdb_path), read_only=True)
            try:
                df = con.sql(query).df()
            finally:
                con.close()
    else:
        con = duckdb.connect(str(settings.duckdb_path), read_only=True)
        try:
            df = con.sql(query).df()
        finally:
            con.close()

    # Load Model and Metrics
    model_path = ART_DIR / "best_delay_model.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Missing {model_path}. Please run: python ml/train.py --model tournament")
    
    clf = joblib.load(model_path)
    metrics_path = ART_DIR / "metrics.json"
    raw_metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    winner = raw_metrics.get("best_model", {}).get("winner", "baseline_logreg")
    val_threshold = float(raw_metrics.get(winner, {}).get("val", {}).get("threshold", 0.2747))

    # Feature preparation for inference
    if hasattr(clf, "feature_names_in_"):
        expected_features = list(clf.feature_names_in_)
    elif hasattr(clf, "feature_names_"):
        expected_features = list(clf.feature_names_)
    else:
        expected_features = [
            "dep_hour", "route_delay_rate_30d", "carrier_delay_rate_30d",
            "scheduled_departures_hour", "distance_miles"
        ]

    # Predict probabilities
    X = df[expected_features].copy()
    probs = clf.predict_proba(X)[:, 1]
    df["delay_probability"] = np.round(probs, 4)

    # In operational airline dispatch, realistic OCC bands prioritize the top risk tiers:
    # High Risk: Top ~30% highest delay probability (p >= 0.2900 or 70th percentile)
    # Elevated Risk: Middle tier requiring passenger updates and monitoring (0.2850 <= p < 0.2900)
    # Normal Risk: Lower tier operating within safe standard corridor (p < 0.2850)
    high_thr = 0.2900
    elev_thr = 0.2850
    df["operating_threshold"] = high_thr

    p_series = df["delay_probability"]
    df["risk_band"] = np.where(
        p_series >= high_thr, "High",
        np.where(p_series >= elev_thr, "Elevated", "Normal")
    )
    df["is_predicted_delayed"] = df["risk_band"] == "High"

    # Vectorized Regulatory Compliance & Mandate Mapping
    # Rule 1: Normal Safe Corridor (14 CFR § 121.593)
    is_normal = df["risk_band"] == "Normal"
    # Rule 2: Elevated Monitoring (14 CFR § 259.8(a)(1))
    is_elevated = df["risk_band"] == "Elevated"
    # Rule 3: High Risk Rules
    is_high = df["risk_band"] == "High"

    # Tarmac Delay Rule: High Risk AND (congestion >= 8 OR evening peak 16-20h)
    is_congested = (df["scheduled_departures_hour"] >= 8) | (df["dep_hour"].isin([16, 17, 18, 19, 20]))
    df["is_tarmac_risk"] = is_high & is_congested

    # Crew Duty Time-Out Rule (FAR Part 117): High Risk AND (night/late evening >= 17h or <= 5h)
    is_late_or_early = (df["dep_hour"] >= 17) | (df["dep_hour"] <= 5)
    df["is_crew_duty_risk"] = is_high & is_late_or_early

    # Legacy Missed Connections Rebooking Mandate (14 CFR § 259.5(b)(8))
    is_legacy = df["carrier_type"].str.contains("Legacy", case=False, na=False) | df["carrier_code"].isin(["AA", "DL", "UA", "AS"])
    df["is_rebooking_mandate"] = is_high & is_legacy

    # LCC Cash Refund Mandate (14 CFR § 260.6)
    is_lcc = df["carrier_type"].str.contains("Low-Cost", case=False, na=False) | df["carrier_code"].isin(["WN", "B6", "F9", "NK", "G4", "HA"])
    df["is_cash_refund_mandate"] = is_high & is_lcc

    # Chronically Delayed Route Risk (14 CFR § 234.11): High Risk AND route_delay_rate_30d >= 0.30
    df["is_chronic_route_risk"] = is_high & (df["route_delay_rate_30d"] >= 0.30)

    # Base assignments: Normal Safe Corridor
    df["primary_legal_code"] = "14 CFR § 121.593 (Standard Corridor)"
    df["primary_regulatory_agency"] = "FAA (Federal Aviation Admin)"
    df["primary_legal_citation"] = "Điều 121.593 - Dispatch Release Hành lang an toàn"
    df["statutory_penalty_potential_usd"] = 0.0
    df["max_penalty_exposure_usd"] = 0.0
    df["mandatory_occ_action"] = "OCC DISPATCH: Cho phép đẩy lùi (Push-back) đúng lịch, khai thác bình thường."
    df["vietnam_legal_equivalent"] = "Luật Hàng không Dân dụng VN Điều 158 Khoản 1 Điểm a"

    # Assign Elevated (Monitoring Alert)
    m_elevated = is_elevated
    df.loc[m_elevated, "primary_legal_code"] = "14 CFR § 259.8(a)(1)"
    df.loc[m_elevated, "primary_regulatory_agency"] = "US DOT (Office of Aviation Consumer Protection)"
    df.loc[m_elevated, "primary_legal_citation"] = "Điều 259.8(a)(1) - Cập nhật thông tin trễ chuyến mỗi 30 phút"
    df.loc[m_elevated, "mandatory_occ_action"] = "OCC/PAX SERVICE: Cập nhật FIDS và gửi thông báo SMS trước cho hành khách."
    df.loc[m_elevated, "vietnam_legal_equivalent"] = "Thông tư 19/2023/TT-BGTVT Điều 8 Khoản 1 Điểm a"

    # Assign Rebooking (Legacy high risk)
    m_rebook = is_high & is_legacy
    df.loc[m_rebook, "primary_legal_code"] = "14 CFR § 259.5(b)(8)"
    df.loc[m_rebook, "primary_regulatory_agency"] = "US DOT"
    df.loc[m_rebook, "primary_legal_citation"] = "Điều 259.5(b)(8) - Nghĩa vụ bảo vệ khách nối chuyến (Interline Rebooking)"
    df.loc[m_rebook, "mandatory_occ_action"] = "OCC/REBOOKING: Lọc khách MCT < 45 phút, tự động bảo lưu chỗ trên chuyến bay kế tiếp."
    df.loc[m_rebook, "vietnam_legal_equivalent"] = "Thông tư 19/2023/TT-BGTVT Điều 8 Khoản 2 Điểm b"

    # Assign Refund (LCC high risk)
    m_refund = is_high & is_lcc
    df.loc[m_refund, "primary_legal_code"] = "14 CFR § 260.6(a)(1)"
    df.loc[m_refund, "primary_regulatory_agency"] = "US DOT"
    df.loc[m_refund, "primary_legal_citation"] = "Điều 260.6(a)(1) - Hoàn trả 100% tiền mặt tự động khi chậm từ 3 giờ"
    df.loc[m_refund, "mandatory_occ_action"] = "FINANCE/TICKETING: Kích hoạt quy trình hoàn tiền mặt 100%, không ép nhận voucher bay."
    df.loc[m_refund, "vietnam_legal_equivalent"] = "Thông tư 19/2023/TT-BGTVT Điều 8 Khoản 2 Điểm c"

    # Assign Chronic Route (High delay rate)
    m_chronic = df["is_chronic_route_risk"]
    df.loc[m_chronic, "primary_legal_code"] = "14 CFR § 234.11"
    df.loc[m_chronic, "primary_regulatory_agency"] = "US DOT BTS"
    df.loc[m_chronic, "primary_legal_citation"] = "Điều 234.11 - Kiểm toán đặc biệt đường bay chậm kinh niên"
    df.loc[m_chronic, "mandatory_occ_action"] = "NETWORK PLANNING: Bổ sung 20 phút đệm quay đầu trong mùa bay tới tránh bị thu hồi slot."
    df.loc[m_chronic, "vietnam_legal_equivalent"] = "Thông tư 81/2014/TT-BGTVT Điều 25"

    # Assign Crew Duty Risk (Evening/Night flights)
    m_crew = df["is_crew_duty_risk"]
    df.loc[m_crew, "primary_legal_code"] = "FAR Part 117 § 117.11 & § 117.19"
    df.loc[m_crew, "primary_regulatory_agency"] = "FAA (Flight Standards Service)"
    df.loc[m_crew, "primary_legal_citation"] = "FAR Part 117 § 117.11(a) - Giới hạn giờ làm nhiệm vụ bay (FDP)"
    df.loc[m_crew, "mandatory_occ_action"] = "CREW DISPATCH: Rà soát quỹ giờ FDP, kích hoạt ngay Standby Crew dự bị tại sân bay khởi hành."
    df.loc[m_crew, "vietnam_legal_equivalent"] = "Quy chế An toàn Hàng không VAR Part 12"

    # Assign Tarmac Delay Risk (Highest Severity: Congested Hubs + Evening)
    m_tarmac = df["is_tarmac_risk"]
    df.loc[m_tarmac, "primary_legal_code"] = "14 CFR § 259.4(b)(1)"
    df.loc[m_tarmac, "primary_regulatory_agency"] = "US DOT"
    df.loc[m_tarmac, "primary_legal_citation"] = "Điều 259.4(b)(1) - Giới hạn kẹt đường lăn Tarmac Delay > 3 giờ"
    df.loc[m_tarmac, "statutory_penalty_potential_usd"] = 37377.0
    # Average narrow-body aircraft passenger load = 180 seats
    df.loc[m_tarmac, "max_penalty_exposure_usd"] = 37377.0 * 180.0
    df.loc[m_tarmac, "mandatory_occ_action"] = "OCC GATE HOLD: Giữ máy bay tại cửa (Gate Hold), TUYỆT ĐỐI KHÔNG đẩy lùi ra đường lăn khi chưa có slot ATC."
    df.loc[m_tarmac, "vietnam_legal_equivalent"] = "Thông tư 19/2023/TT-BGTVT Điều 8 Khoản 2 Điểm a & NĐ 162/2018/NĐ-CP Điều 24"

    # Calculate Total Regulations Triggered per flight
    df["total_regulations_triggered"] = (
        is_normal.astype(int) +
        is_elevated.astype(int) +
        df["is_tarmac_risk"].astype(int) +
        df["is_crew_duty_risk"].astype(int) +
        df["is_rebooking_mandate"].astype(int) +
        df["is_cash_refund_mandate"].astype(int) +
        df["is_chronic_route_risk"].astype(int)
    )

    # Route display column
    df["route"] = df["origin_airport"] + " -> " + df["dest_airport"]

    # Select and order columns for Power BI consumption
    cols_to_export = [
        "flight_id", "date_key", "origin_airport_key", "dest_airport_key", "airline_key",
        "flight_date", "carrier_code", "flight_number", "tail_number",
        "origin_airport", "dest_airport", "route", "dep_hour", "distance_miles",
        "distance_bucket", "carrier_type", "scheduled_departures_hour",
        "route_delay_rate_30d", "carrier_delay_rate_30d",
        "delay_probability", "operating_threshold", "risk_band", "is_predicted_delayed",
        "is_tarmac_risk", "is_crew_duty_risk", "is_rebooking_mandate",
        "is_cash_refund_mandate", "is_chronic_route_risk",
        "primary_legal_code", "primary_regulatory_agency", "primary_legal_citation",
        "statutory_penalty_potential_usd", "max_penalty_exposure_usd",
        "mandatory_occ_action", "vietnam_legal_equivalent",
        "total_regulations_triggered",
        "is_cancelled", "is_delayed", "dep_delay_min", "arr_delay_min"
    ]

    export_df = df[cols_to_export]
    out_path = EXPORT_DIR / "fct_flight_regulatory_predictions.parquet"
    export_df.to_parquet(out_path, index=False)
    print(f"Exported {len(export_df):,} scored flights to {out_path.name}")
    print(f"  - High Risk Flights: {export_df['is_predicted_delayed'].sum():,} ({export_df['is_predicted_delayed'].mean()*100:.1f}%)")
    print(f"  - Elevated Risk Flights: {(export_df['risk_band'] == 'Elevated').sum():,} ({(export_df['risk_band'] == 'Elevated').mean()*100:.1f}%)")
    print(f"  - Normal Safe Flights: {(export_df['risk_band'] == 'Normal').sum():,} ({(export_df['risk_band'] == 'Normal').mean()*100:.1f}%)")
    print(f"  - Tarmac Delay Risks: {export_df['is_tarmac_risk'].sum():,}")
    print(f"  - Crew Duty Risks: {export_df['is_crew_duty_risk'].sum():,}")
    print(f"  - Cash Refund Mandates: {export_df['is_cash_refund_mandate'].sum():,}")
    print(f"  - Max Potential Penalty Exposure: ${export_df['max_penalty_exposure_usd'].sum():,.0f} USD")
    return export_df


def main():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 70)
    print("EXPORTING POWER BI ADVANCED ML & REGULATORY GOVERNANCE MARTS")
    print("=" * 70)
    export_tournament_metrics()
    export_regulatory_predictions()
    print("=" * 70)
    print("All ML & Regulatory Parquet files successfully exported!")


if __name__ == "__main__":
    main()
