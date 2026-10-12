"""
Unit tests for Aviation & ML Knowledge Engine (ml/copilot.py) - Enterprise Suite (40 items).
Validates domain glossary (18 aviation terms), mathematical metrics (14 ML metrics),
and 8 SOP checklists, search ranking, and Markdown formatting.
"""
import pytest

from ml.copilot import (
    KNOWLEDGE_TERMS,
    SOP_CHECKLISTS,
    explain_term,
    format_catalog_markdown,
    format_sop_markdown,
    format_term_card_markdown,
    get_knowledge_base,
    get_sop_checklist,
    get_sop_checklists,
    list_terms,
    lookup_term,
    search_knowledge,
    strip_accents,
    tokenize,
)


# =============================================================================
# 1. KNOWLEDGE BASE INTEGRITY TESTS (32 TERMS + 8 SOPS = 40 ITEMS)
# =============================================================================

def test_knowledge_base_total_count():
    kb = get_knowledge_base()
    sops = get_sop_checklists()
    assert len(kb) == 32, f"Knowledge base must contain exactly 32 terms, found {len(kb)}"
    assert len(sops) == 8, f"SOP checklists must contain exactly 8 SOPs, found {len(sops)}"
    assert len(kb) + len(sops) == 40, "Total enterprise knowledge items must equal 40"


def test_required_18_aviation_terms_present():
    """Verify all 18 mandatory aviation domain metrics exist."""
    required = [
        "fdp",
        "tarmac_delay",
        "otp",
        "d0_d15",
        "taxi_out_in",
        "turnaround_time",
        "block_time_air_time",
        "schedule_padding",
        "makeup_time",
        "cascading_delay",
        "hub_congestion",
        "ground_stop",
        "gdp_edct",
        "airport_slot_8020",
        "curfew",
        "diversion",
        "ferry_flight",
        "cost_of_delay",
    ]
    assert len(required) == 18
    for term_id in required:
        assert term_id in KNOWLEDGE_TERMS, f"Missing required aviation term: {term_id}"
        term = KNOWLEDGE_TERMS[term_id]
        assert term.category == "aviation_metrics"
        assert len(term.definition_vi) > 20
        assert len(term.business_significance) > 20
        assert len(term.calculation_or_rule) > 10
        assert len(term.operational_impact) > 10
        assert len(term.keywords) >= 3


def test_required_14_ml_metrics_present():
    """Verify all 14 mandatory ML metrics exist."""
    required = [
        "delay_probability",
        "risk_band",
        "optimal_threshold",
        "roc_auc",
        "pr_auc",
        "lift_at_10",
        "brier_score",
        "precision_score",
        "recall_sensitivity",
        "f1_fbeta_score",
        "confusion_matrix_cost",
        "feature_importance_shap",
        "data_drift_psi",
        "temporal_split_leakage",
    ]
    assert len(required) == 14
    for term_id in required:
        assert term_id in KNOWLEDGE_TERMS, f"Missing required ML metric: {term_id}"
        term = KNOWLEDGE_TERMS[term_id]
        assert term.category == "ml_metrics"
        assert len(term.calculation_or_rule) > 10
        assert len(term.keywords) >= 3


def test_list_terms_and_category_filtering():
    all_terms = list_terms()
    assert len(all_terms) == 32

    aviation_terms = list_terms(category="aviation_metrics")
    assert len(aviation_terms) == 18
    assert all(t["category"] == "aviation_metrics" for t in aviation_terms)

    ml_terms = list_terms(category="ml_metrics")
    assert len(ml_terms) == 14
    assert all(t["category"] == "ml_metrics" for t in ml_terms)


# =============================================================================
# 2. SOP CHECKLIST TESTS (8 SOPS)
# =============================================================================

def test_all_8_sop_checklists_integrity():
    """Verify all 8 mandatory SOP checklists exist with structured steps."""
    expected_sops = [
        "sop_delay_incident",
        "sop_crew_timeout_replacement",
        "sop_priority_slot_request",
        "sop_passenger_refund_care",
        "sop_aircraft_aog_swap",
        "sop_flight_diversion",
        "sop_tarmac_clockwork_emergency",
        "sop_cancellation_consolidation",
    ]
    assert len(expected_sops) == 8
    all_sops = get_sop_checklists()
    for sop_id in expected_sops:
        assert sop_id in all_sops, f"Missing mandatory SOP: {sop_id}"
        sop = all_sops[sop_id]
        assert len(sop.steps) >= 4, f"SOP {sop_id} should have at least 4 steps"
        assert len(sop.target_roles) >= 1
        assert len(sop.contingency_fallback) > 10

        # Validate step sequencing
        for i, step in enumerate(sop.steps, start=1):
            assert step.step_number == i
            assert len(step.action_vi) > 10
            assert len(step.responsible_role) > 2
            assert len(step.timeframe) > 2
            assert len(step.verification_criteria) > 5


def test_get_sop_checklist_lookup():
    sop = get_sop_checklist("sop_aircraft_aog_swap")
    assert sop is not None
    assert sop["sop_id"] == "sop_aircraft_aog_swap"
    assert "SOP-OCC-MAINT-05" in sop["title_vi"]

    # Fuzzy/case insensitive lookup
    sop_fuzzy = get_sop_checklist("DIVERSION")
    assert sop_fuzzy is not None
    assert sop_fuzzy["sop_id"] == "sop_flight_diversion"

    sop_tarmac = get_sop_checklist("clockwork")
    assert sop_tarmac is not None
    assert sop_tarmac["sop_id"] == "sop_tarmac_clockwork_emergency"

    assert get_sop_checklist("non_existent_sop") is None


# =============================================================================
# 3. LOOKUP & TEXT PROCESSING TESTS
# =============================================================================

def test_strip_accents_and_tokenize():
    text = "Giờ Giới Nghiêm Tiếng Ồn Sân Bay"
    cleaned = strip_accents(text)
    assert cleaned == "gio gioi nghiem tieng on san bay"

    tokens = tokenize("PR-AUC & Brier Score with PSI > 0.25")
    assert "auc" in tokens
    assert "brier" in tokens
    assert "score" in tokens
    assert "psi" in tokens


def test_lookup_term_exact_and_acronym():
    # Exact term_id
    t1 = lookup_term("curfew")
    assert t1 is not None
    assert t1["term_id"] == "curfew"

    # Acronym match
    t2 = lookup_term("PR-AUC")
    assert t2 is not None
    assert t2["term_id"] == "pr_auc"

    # Alias / keyword match
    t3 = lookup_term("don ve sinh")
    assert t3 is not None
    assert t3["term_id"] == "turnaround_time"

    # Unknown term
    assert lookup_term("random_unknown_token_xyz") is None


# =============================================================================
# 4. SEARCH KNOWLEDGE & EXPLAIN TESTS
# =============================================================================

def test_search_knowledge_ranking():
    # Search for turn around time
    results = search_knowledge("thoi gian quay dau tau bay", top_k=3)
    assert len(results) >= 1
    assert results[0]["term_id"] == "turnaround_time"

    # Search for data drift
    drift_results = search_knowledge("data drift population stability index psi", top_k=3)
    assert len(drift_results) >= 1
    assert drift_results[0]["term_id"] == "data_drift_psi"

    # Search for diversion SOP
    div_results = search_knowledge("quy trinh chuyen huong ha canh san bay du bi", top_k=3)
    assert len(div_results) >= 1
    sop_ids = [r.get("sop_id") or r.get("term_id") for r in div_results]
    assert "sop_flight_diversion" in sop_ids or "diversion" in sop_ids


def test_explain_term_flow():
    # Exact lookup
    exp1 = explain_term("D0")
    assert exp1["status"] == "exact_match"
    assert "markdown" in exp1
    assert "### 📘" in exp1["markdown"]

    # Search fallback hit for new SOP
    exp2 = explain_term("quy trinh doi tau bay khi bi hong AOG")
    assert exp2["status"] in ("exact_match", "search_hit")
    assert "markdown" in exp2

    # Not found
    exp3 = explain_term("từ_khoá_hoàn_toàn_không_liên_quan_999999")
    assert exp3["status"] == "not_found"
    assert "available_topics" in exp3
    assert len(exp3["available_topics"]) == 32


# =============================================================================
# 5. MARKDOWN FORMATTING TESTS
# =============================================================================

def test_formatters():
    term = lookup_term("cost_of_delay")
    term_md = format_term_card_markdown(term)
    assert "### 📘" in term_md
    assert "101.18 USD" in term_md

    sop = get_sop_checklist("sop_tarmac_clockwork_emergency")
    sop_md = format_sop_markdown(sop)
    assert "### 📋" in sop_md
    assert "MỐC PHÚT 120" in sop_md
    assert "POINT OF NO RETURN" in sop_md

    catalog_md = format_catalog_markdown()
    assert "# 📚 TỪ ĐIỂN TRI THỨC" in catalog_md
    assert "40 ITEMS" in catalog_md
    assert "18 mục" in catalog_md
    assert "14 mục" in catalog_md
    assert "8 SOPs" in catalog_md


# =============================================================================
# 6. ADVISORY ENGINE RE-EXPORT TESTS (PHASE 6.2)
# =============================================================================

def test_copilot_advisory_reexports():
    """Verify that copilot exposes Phase 6.2 advisory engine functions seamlessly."""
    from ml.copilot import (
        DispatchAdvisory,
        format_advisory_markdown,
        generate_dispatch_advisory,
        lookup_flight_advisory,
        simulate_what_if,
    )
    adv = generate_dispatch_advisory(carrier_code="AA", origin="ATL", dest="DFW", dep_hour=17)
    assert isinstance(adv, DispatchAdvisory)
    assert adv.advisory_id.startswith("ADV-AA-")
    md = format_advisory_markdown(adv)
    assert "BẢN KHUYẾN NGHỊ ĐIỀU HÀNH TÁC NGHIỆP OCC" in md

    # What-if from copilot namespace
    sim = simulate_what_if(adv, "crew_standby")
    assert sim["scenario_type"] == "crew_standby"

