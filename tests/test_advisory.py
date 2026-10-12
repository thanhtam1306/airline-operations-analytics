"""
Unit tests for Context-Aware Advisory & Grounding Engine (Phase 6.2).
Validates tri-layer grounding (Warehouse + ML + Regulatory), minute-by-minute
actionable dispatch plans, financial cost-of-delay calculations, dynamic SOP
binding, What-If operational simulations, and API endpoints.
"""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from ml.advisory import (
    COST_OF_DELAY_PER_MIN_USD,
    TARMAC_FINE_PER_PAX_USD,
    DispatchAdvisory,
    FinancialExposure,
    FlightContext,
    PredictionContext,
    TimelineAction,
    format_advisory_markdown,
    generate_dispatch_advisory,
    lookup_flight_advisory,
    simulate_what_if,
)
from ml.api import app

ART = Path(__file__).resolve().parents[1] / "ml" / "artifacts"

pytestmark = pytest.mark.skipif(
    not (ART / "metrics.json").exists(),
    reason="model artifacts not trained — run: make train",
)


@pytest.fixture(scope="module")
def api_client():
    return TestClient(app)


# =============================================================================
# 1. ADVISORY GENERATION & TRI-LAYER GROUNDING
# =============================================================================

def test_generate_dispatch_advisory_direct_params():
    """Verify advisory generation with direct operational parameters."""
    adv = generate_dispatch_advisory(
        carrier_code="AA",
        origin="ATL",
        dest="DFW",
        dep_hour=17,
        flight_date="2025-02-14",
    )
    assert isinstance(adv, DispatchAdvisory)
    assert adv.advisory_id.startswith("ADV-AA-")
    assert adv.flight_context.carrier_code == "AA"
    assert adv.flight_context.origin == "ATL"
    assert adv.flight_context.dest == "DFW"
    assert adv.flight_context.dep_hour == 17

    # Layer 1: Warehouse / Operational Grounding
    ctx = adv.flight_context
    assert ctx.origin_city == "Atlanta"
    assert ctx.dest_city == "Dallas/Fort Worth" or "Dallas" in ctx.dest_city
    assert ctx.carrier_type == "legacy"
    assert ctx.distance_miles > 500
    assert ctx.distance_bucket in ("short", "medium", "long")
    assert ctx.scheduled_departures_hour >= 1
    assert "evening peak bank" in ctx.dep_window_label.lower() or "chiều tối" in ctx.dep_window_label.lower()


    # Layer 2: Machine Learning Prediction Context
    pred = adv.prediction_context
    assert 0.0 <= pred.delay_probability <= 1.0
    assert pred.risk_band in ("NORMAL", "ELEVATED", "HIGH")
    assert pred.operating_threshold > 0.0
    assert pred.lift_at_10 >= 1.0
    assert pred.projected_delay_min >= 0
    assert len(pred.top_risk_factors) >= 1

    # Layer 3: Regulatory Compliance Grounding
    legal = adv.regulatory_compliance
    assert "US DOT Title 14 CFR" in legal["regulatory_framework"]
    assert legal["compliance_status"] in ("HIGH_COMPLIANCE_RISK", "MONITORING_REQUIRED", "COMPLIANT_ON_TIME")
    assert len(legal["legal_evaluations"]) >= 1


def test_generate_dispatch_advisory_by_warehouse_flight_id():
    """Verify lookup directly by flight_id from pre-scored warehouse mart."""
    adv = generate_dispatch_advisory(flight_id=4568)
    assert isinstance(adv, DispatchAdvisory)
    assert adv.flight_context.carrier_code == "UA"
    assert adv.flight_context.origin == "LAS"
    assert adv.flight_context.dest == "BOS"
    assert adv.prediction_context.delay_probability > 0.0
    assert adv.prediction_context.risk_band == "HIGH"
    assert adv.financial_exposure.base_delay_cost_usd > 0


def test_lookup_flight_advisory_helper():
    """Test lookup_flight_advisory helper function."""
    adv = lookup_flight_advisory(4568)
    assert adv is not None
    assert adv.flight_context.origin == "LAS"

    # Non-existent flight_id returns default synthesized advisory
    adv_unknown = lookup_flight_advisory(99999999)
    assert adv_unknown is not None
    assert adv_unknown.flight_context.carrier_code == "AA"


# =============================================================================
# 2. FINANCIAL EXPOSURE & COST OF DELAY TESTS
# =============================================================================

def test_financial_exposure_cost_of_delay_standard():
    """Verify quantitative FAA/A4A $101.18/minute calculation."""
    adv = generate_dispatch_advisory(
        carrier_code="DL",
        origin="ORD",
        dest="LAX",
        dep_hour=18,
    )
    fin = adv.financial_exposure
    assert fin.cost_per_minute_usd == COST_OF_DELAY_PER_MIN_USD
    expected_direct_cost = round(fin.projected_delay_min * COST_OF_DELAY_PER_MIN_USD, 2)
    assert fin.base_delay_cost_usd == expected_direct_cost
    assert fin.total_potential_exposure_usd >= fin.base_delay_cost_usd
    assert fin.estimated_passengers >= 100


def test_tarmac_delay_penalty_exposure_trigger():
    """Verify tarmac delay exposure ($37,377/pax) is quantified for high risk scenarios."""
    adv = generate_dispatch_advisory(
        carrier_code="AA",
        origin="ATL",
        dest="DFW",
        dep_hour=17,
        custom_delay_prob=0.85,  # Force extreme high risk
    )
    fin = adv.financial_exposure
    assert adv.prediction_context.risk_band == "HIGH"
    assert fin.tarmac_penalty_exposure_usd > 0
    assert fin.proactive_mitigation_savings_usd > 0


# =============================================================================
# 3. TIMELINE ACTIONS & MINUTE-BY-MINUTE DISPATCH PLAN
# =============================================================================

def test_timeline_actions_structure():
    """Verify timeline action plan covers all 5 chronological operational gates."""
    adv = generate_dispatch_advisory(carrier_code="UA", origin="ORD", dest="SFO", dep_hour=17)
    actions = adv.timeline_actions
    assert len(actions) == 5

    phase_codes = [a.phase_code for a in actions]
    assert phase_codes == ["T-120", "T-60", "T-15", "T-0", "EN-ROUTE"]

    # Roles assigned
    roles = {a.responsible_role for a in actions}
    assert "OCC Flight Dispatcher" in roles
    assert "Station Manager & Ramp Supervisor" in roles
    assert "Captain (PIC) & ATC Coordinator" in roles

    # Guidance and critical decision texts exist
    for a in actions:
        assert len(a.operational_guidance) > 20
        assert len(a.critical_decision) > 10
        assert a.priority in ("CRITICAL", "HIGH", "MEDIUM", "LOW")


# =============================================================================
# 4. SOP DYNAMIC BINDING
# =============================================================================

def test_sop_dynamic_binding_high_risk():
    """Verify high-risk flights automatically bind relevant emergency SOPs."""
    adv = generate_dispatch_advisory(
        carrier_code="AA",
        origin="ATL",
        dest="DFW",
        dep_hour=19,
        custom_delay_prob=0.75,
    )
    sops = adv.recommended_sops
    assert len(sops) >= 2
    sop_ids = [s.get("sop_id") for s in sops]
    assert "sop_tarmac_clockwork_emergency" in sop_ids
    assert "sop_crew_timeout_replacement" in sop_ids
    for s in sops:
        assert "binding_reason" in s
        assert len(s.get("steps", [])) >= 3


# =============================================================================
# 5. WHAT-IF OPERATIONAL DISPATCH SIMULATION
# =============================================================================

def test_what_if_reschedule_hour():
    """Verify rescheduling departure hour simulates reduced risk and calculated savings."""
    adv = generate_dispatch_advisory(carrier_code="AA", origin="ATL", dest="DFW", dep_hour=18)
    sim = simulate_what_if(adv, "reschedule_hour", {"new_dep_hour": 10})
    assert sim["scenario_type"] == "reschedule_hour"
    assert "baseline" in sim
    assert "simulated_outcome" in sim
    outcome = sim["simulated_outcome"]
    assert "new_delay_probability" in outcome
    assert "new_risk_band" in outcome
    assert "cost_saved_usd" in outcome
    assert "roi_verdict" in outcome


def test_what_if_crew_standby():
    """Verify calling in standby crew eliminates Part 117 risk and calculates net savings."""
    adv = generate_dispatch_advisory(carrier_code="UA", origin="LAS", dest="BOS", dep_hour=19)
    sim = simulate_what_if(adv, "crew_standby")
    assert sim["scenario_type"] == "crew_standby"
    outcome = sim["simulated_outcome"]
    assert outcome["crew_duty_compliance"] == "100% TUÂN THỦ (FAR Part 117)"
    assert outcome["cancellation_risk"] == "TRIỆT TIÊU HOÀN TOÀN (0%)"
    assert outcome["net_financial_savings_usd"] > 0


def test_what_if_airborne_speedup():
    """Verify increasing Cost Index for airborne make-up time."""
    adv = generate_dispatch_advisory(carrier_code="DL", origin="ATL", dest="LAX", dep_hour=17)
    sim = simulate_what_if(adv, "airborne_speedup")
    assert sim["scenario_type"] == "airborne_speedup"
    outcome = sim["simulated_outcome"]
    assert outcome["airborne_minutes_recovered"] > 0
    assert outcome["net_savings_usd"] > 0


def test_what_if_tail_swap():
    """Verify tail swap cuts domino cascading delay."""
    adv = generate_dispatch_advisory(carrier_code="AA", origin="ORD", dest="DFW", dep_hour=18)
    sim = simulate_what_if(adv, "tail_swap")
    assert sim["scenario_type"] == "tail_swap"
    outcome = sim["simulated_outcome"]
    assert outcome["domino_delay_eliminated_min"] > 0


# =============================================================================
# 6. SERIALIZATION & MARKDOWN FORMATTING
# =============================================================================

def test_dispatch_advisory_serialization():
    """Verify advisory can be cleanly serialized to dictionary with JSON-native types."""
    adv = generate_dispatch_advisory(carrier_code="AA", origin="ATL", dest="DFW", dep_hour=17)
    d = adv.to_dict()
    assert isinstance(d, dict)
    assert isinstance(d["flight_context"]["dep_hour"], int)
    assert isinstance(d["prediction_context"]["delay_probability"], float)
    assert isinstance(d["financial_exposure"]["total_potential_exposure_usd"], float)


def test_format_advisory_markdown():
    """Verify rich Markdown report rendering."""
    adv = generate_dispatch_advisory(carrier_code="AA", origin="ATL", dest="DFW", dep_hour=17)
    md = format_advisory_markdown(adv)
    assert "# " in md
    assert "BẢN KHUYẾN NGHỊ ĐIỀU HÀNH TÁC NGHIỆP OCC" in md
    assert "## 1. Tóm Tắt Tác Nghiệp Cấp Cao" in md
    assert "## 2. Thông Tin Chuyến Bay & Bối Cảnh Vận Hành" in md
    assert "## 3. Dự Báo AI & Phân Tích Thiệt Hại Tài Chính" in md
    assert "101.18" in md
    assert "## 4. Thẩm Định Pháp Lý & Chế Tài Quản Lý Nhà Nước" in md
    assert "## 5. Bản Kế Hoạch Điều Hành Tác Nghiệp Từng Phút" in md
    assert "## 6. Danh Mục Quy Trình Thao Tác Chuẩn SOP Kích Hoạt" in md


# =============================================================================
# 7. FASTAPI SERVING ENDPOINTS
# =============================================================================

def test_api_advisory_endpoint(api_client):
    """Test POST /copilot/advisory endpoint."""
    res = api_client.post("/copilot/advisory", json={
        "carrier_code": "AA",
        "origin": "ATL",
        "dest": "DFW",
        "dep_hour": 17,
        "flight_date": "2025-02-14",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["advisory_id"].startswith("ADV-AA-")
    assert "flight_context" in data
    assert "prediction_context" in data
    assert "financial_exposure" in data
    assert "regulatory_compliance" in data
    assert "timeline_actions" in data
    assert "recommended_sops" in data
    assert "markdown_report" in data
    assert len(data["timeline_actions"]) == 5


def test_api_advisory_endpoint_by_flight_id(api_client):
    """Test POST /copilot/advisory with flight_id."""
    res = api_client.post("/copilot/advisory", json={"flight_id": 4568})
    assert res.status_code == 200
    data = res.json()
    assert data["flight_context"]["carrier_code"] == "UA"
    assert data["flight_context"]["origin"] == "LAS"
    assert data["flight_context"]["dest"] == "BOS"


def test_api_simulate_endpoint(api_client):
    """Test POST /copilot/simulate endpoint."""
    res = api_client.post("/copilot/simulate", json={
        "carrier_code": "AA",
        "origin": "ATL",
        "dest": "DFW",
        "dep_hour": 17,
        "scenario_type": "crew_standby",
    })
    assert res.status_code == 200
    sim_data = res.json()
    assert sim_data["scenario_type"] == "crew_standby"
    assert sim_data["simulated_outcome"]["crew_duty_compliance"] == "100% TUÂN THỦ (FAR Part 117)"
