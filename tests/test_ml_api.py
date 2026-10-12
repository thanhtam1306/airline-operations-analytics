"""API tests for the delay-risk service and multi-model tournament."""
from pathlib import Path

import pandas as pd
import pytest

ART = Path(__file__).resolve().parents[1] / "ml" / "artifacts"

pytestmark = pytest.mark.skipif(
    not (ART / "metrics.json").exists(),
    reason="model artifacts not trained — run: make train",
)


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from ml.api import app

    return TestClient(app)


def test_health(client):
    j = client.get("/health").json()
    assert j["status"] == "ok"
    assert j["routes_known"] > 100
    assert "tournament_winner" in j
    assert "model_type" in j


def test_models_endpoint(client):
    r = client.get("/models")
    assert r.status_code == 200
    data = r.json()
    assert "available_models" in data
    assert "tournament_leaderboard" in data
    assert len(data["available_models"]) >= 3


def test_predict_known_route_default_best(client):
    j = client.post("/predict", json={
        "carrier_code": "AA", "origin": "ATL", "dest": "DFW",
        "flight_date": "2025-02-14", "dep_hour": 17}).json()
    assert 0.0 <= j["delay_probability"] <= 1.0
    assert j["risk_band"] in ("normal", "elevated", "high")
    assert j["features_used"]["carrier_type"]
    assert "model" in j
    assert "regulatory_compliance" in j
    comp = j["regulatory_compliance"]
    assert comp["compliance_status"] in ("HIGH_COMPLIANCE_RISK", "MONITORING_REQUIRED", "COMPLIANT")
    assert len(comp["legal_evaluations"]) >= 1


def test_regulatory_compliance_clauses_and_penalties(client):
    """Verify that predictions cite exact legal articles, clauses, subsections and statutory penalties."""
    r = client.post("/predict", json={
        "carrier_code": "AA", "origin": "ATL", "dest": "DFW",
        "flight_date": "2025-02-14", "dep_hour": 17})
    assert r.status_code == 200
    comp = r.json()["regulatory_compliance"]
    
    assert "legal_evaluations" in comp
    assert comp["total_regulations_evaluated"] >= 2
    
    # Check that each evaluated regulation has exact Điều, Khoản, Điểm and statutory penalties
    for alert in comp["legal_evaluations"]:
        assert "legal_code" in alert
        assert "citation" in alert
        assert any(k in alert["citation"] for k in ("Điều", "Khoản", "Điểm", "Part", "§"))
        assert "statutory_text" in alert and len(alert["statutory_text"]) > 20
        assert "statutory_penalty" in alert and len(alert["statutory_penalty"]) > 10
        assert "mandatory_action" in alert and len(alert["mandatory_action"]) > 10
        assert "vietnam_equivalent" in alert
        
        # Verify subsection granularity exists
        if "subsections" in alert:
            for sub in alert["subsections"]:
                assert "item" in sub and "requirement" in sub
        assert "trigger_reason" in alert


def test_situational_regulatory_matching(client):
    """Verify that legal rules dynamically match the flight's specific conditions."""
    # 1. Normal morning flight (low risk) -> Only standard corridor, NO tarmac delay or crew timeout
    r_norm = client.post("/predict", json={
        "carrier_code": "DL", "origin": "DFW", "dest": "ORD",
        "flight_date": "2025-02-14", "dep_hour": 7})
    assert r_norm.status_code == 200
    comp_norm = r_norm.json()["regulatory_compliance"]
    codes_norm = [a["legal_code"] for a in comp_norm["legal_evaluations"]]
    if r_norm.json()["risk_band"] == "normal":
        assert "14 CFR § 121.593 & § 121.597" in codes_norm
        assert not any("259.4" in c for c in codes_norm)  # No tarmac delay rule for low risk morning flight




@pytest.mark.parametrize("model_name", ["lgbm", "xgboost", "catboost", "ensemble", "baseline"])
def test_predict_specific_model_architectures(client, model_name):
    # Only test if artifact exists
    from ml.api import MODEL_FILES
    if not (ART / MODEL_FILES[model_name]).exists():
        pytest.skip(f"Model artifact for {model_name} not found")

    r = client.post(f"/predict?model={model_name}", json={
        "carrier_code": "AA", "origin": "ATL", "dest": "DFW",
        "flight_date": "2025-02-14", "dep_hour": 17})
    assert r.status_code == 200
    j = r.json()
    assert 0.0 <= j["delay_probability"] <= 1.0
    assert j["risk_band"] in ("normal", "elevated", "high")


def test_predict_unknown_route_cold_start(client):
    j = client.post("/predict", json={
        "carrier_code": "DL", "origin": "XNA", "dest": "OGG",
        "flight_date": "2025-03-01", "dep_hour": 6}).json()
    assert 0.0 <= j["delay_probability"] <= 1.0  # falls back to zero-history features


def test_unknown_carrier_422(client):
    r = client.post("/predict", json={
        "carrier_code": "ZZ", "origin": "ATL", "dest": "DFW",
        "flight_date": "2025-02-14", "dep_hour": 17})
    assert r.status_code == 422


def test_validation_bad_hour(client):
    r = client.post("/predict", json={
        "carrier_code": "AA", "origin": "ATL", "dest": "DFW",
        "flight_date": "2025-02-14", "dep_hour": 99})
    assert r.status_code == 422


def test_invalid_model_name_400(client):
    r = client.post("/predict?model=non_existent_model", json={
        "carrier_code": "AA", "origin": "ATL", "dest": "DFW",
        "flight_date": "2025-02-14", "dep_hour": 17})
    assert r.status_code == 400


def test_powerbi_ml_tournament_parquet_export():
    p = Path("dashboards/powerbi/export/ml_tournament_metrics.parquet")
    assert p.exists(), "ml_tournament_metrics.parquet should exist"
    df = pd.read_parquet(p)
    assert len(df) == 5, f"Expected 5 tournament models, found {len(df)}"
    assert "test_auc" in df.columns
    assert "is_winner" in df.columns
    assert df["is_winner"].sum() == 1


def test_powerbi_regulatory_predictions_parquet_export():
    p = Path("dashboards/powerbi/export/fct_flight_regulatory_predictions.parquet")
    assert p.exists(), "fct_flight_regulatory_predictions.parquet should exist"
    df = pd.read_parquet(p)
    assert len(df) > 0, "fct_flight_regulatory_predictions should have rows"
    expected_cols = [
        "flight_id", "date_key", "origin_airport_key", "dest_airport_key", "airline_key",
        "delay_probability", "risk_band", "is_predicted_delayed",
        "is_tarmac_risk", "is_crew_duty_risk", "is_cash_refund_mandate",
        "primary_legal_code", "mandatory_occ_action"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing column {col}"
    assert set(df["risk_band"].unique()).issubset({"Normal", "Elevated", "High"})


def test_export_slide_pptx(client):
    r = client.get("/copilot/export-slide/pptx?carrier_code=AA&origin=ATL&dest=DFW&flight_date=2025-02-14&dep_hour=17")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    assert len(r.content) > 10000
    assert "SkyOps_Executive_Slide" in r.headers["content-disposition"]


def test_export_slide_deck_html(client):
    r = client.get("/copilot/slide-deck?carrier_code=AA&origin=ATL&dest=DFW&flight_date=2025-02-14&dep_hour=17")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "SkyOps Slide Deck" in r.text
    assert "14 CFR § 259.4" in r.text


def test_export_slide_markdown(client):
    r = client.get("/copilot/export-slide/markdown?carrier_code=AA&origin=ATL&dest=DFW&flight_date=2025-02-14&dep_hour=17")
    assert r.status_code == 200
    assert "text/markdown" in r.headers["content-type"]
    assert "marp: true" in r.text

