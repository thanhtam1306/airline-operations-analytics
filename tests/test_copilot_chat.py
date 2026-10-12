"""
Unit tests for Conversational OCC Copilot Q&A & Web Serving API (Phase 6.3 & 6.4).
Validates hybrid chatbot engine (offline grounding & fallback), flight context injection,
What-If simulation in chat, prompt chips, 40-item catalog API, and 3-tab web UI.
"""
import pytest
from fastapi.testclient import TestClient

from ml.api import app
from ml.chat import (
    ChatMessage,
    ChatResponse,
    ask_copilot,
    get_copilot_quick_prompts,
)
from ml.copilot import (
    KNOWLEDGE_TERMS,
    SOP_CHECKLISTS,
)


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# =============================================================================
# 1. CORE COPILOT Q&A LOGIC TESTS (PHASE 6.3)
# =============================================================================

def test_ask_copilot_greeting_and_help():
    """Verify friendly greeting, capabilities overview, and suggested questions."""
    res = ask_copilot("Xin chào, bạn có thể giúp gì cho tôi?")
    assert isinstance(res, ChatResponse)
    assert res.source == "offline_knowledge_engine"
    assert "copilot_greeting" in res.matched_terms
    assert "OCC Decision & Knowledge Copilot" in res.reply
    assert len(res.suggested_questions) >= 4
    assert len(res.grounding_citations) >= 1


def test_ask_copilot_aviation_metric_concept():
    """Verify domain concept explanation for FDP and Tarmac Delay."""
    # Test FDP
    res_fdp = ask_copilot("FDP là gì và quy tắc của nó như thế nào?")
    assert res_fdp.source == "offline_knowledge_engine"
    assert "fdp" in res_fdp.matched_terms
    assert "Flight Duty Period" in res_fdp.reply
    assert any("117" in c for c in res_fdp.grounding_citations)
    assert len(res_fdp.suggested_questions) >= 2

    # Test Tarmac Delay
    res_tarmac = ask_copilot("Quy định Tarmac Delay 180 phút")
    assert res_tarmac.source == "offline_knowledge_engine"
    assert "tarmac_delay" in res_tarmac.matched_terms
    assert "37,377" in res_tarmac.reply or "259.4" in res_tarmac.reply


def test_ask_copilot_ml_metric_concept():
    """Verify explanation of ML metrics and formulas."""
    res = ask_copilot("Giải thích chỉ số Lift @ 10% và Optimal Threshold")
    assert res.source == "offline_knowledge_engine"
    assert "lift_at_10" in res.matched_terms or "optimal_threshold" in res.matched_terms
    assert len(res.suggested_questions) >= 2


def test_ask_copilot_sop_checklist():
    """Verify SOP retrieval and step-by-step guidance."""
    res = ask_copilot("Cho tôi xem toàn văn quy trình sop_tarmac_clockwork_emergency")
    assert res.source == "offline_knowledge_engine"
    assert "sop_tarmac_clockwork_emergency" in res.matched_terms
    assert "MỐC PHÚT 120" in res.reply
    assert "POINT OF NO RETURN" in res.reply
    assert len(res.grounding_citations) >= 1


def test_ask_copilot_what_if_simulation_without_flight():
    """Verify general What-If toolkit overview when no flight context is set."""
    res = ask_copilot("Có những phương án can thiệp điều hành nào trong What-If?")
    assert res.source == "offline_knowledge_engine"
    assert "what_if_simulation" in res.matched_terms
    assert "reschedule_hour" in res.reply
    assert "crew_standby" in res.reply
    assert "airborne_speedup" in res.reply
    assert "tail_swap" in res.reply


def test_ask_copilot_what_if_simulation_with_flight():
    """Verify quantitative ROI calculation when What-If is triggered for a specific flight."""
    res = ask_copilot("Mô phỏng đổi giờ bay sang 10:00 sáng", flight_id=4568)
    assert res.source == "offline_knowledge_engine"
    assert "what_if_simulation" in res.matched_terms
    assert "Kết Quả Mô Phỏng Can Thiệp" in res.reply
    assert "UA4554" in res.reply or "UA" in res.reply
    assert "Xác suất trễ ban đầu" in res.reply


def test_ask_copilot_flight_risk_diagnosis():
    """Verify end-to-end flight risk diagnosis with delay probability, costs, and laws."""
    res = ask_copilot("Phân tích tổng quan và đánh giá rủi ro chuyến bay này", flight_id=4568)
    assert res.source == "offline_knowledge_engine"
    assert "flight_UA_4554" in res.matched_terms
    assert "Phân Tích & Khuyến Nghị Tác Nghiệp" in res.reply
    assert "Chi phí trễ vận hành FAA" in res.reply or "Chi phí trễ" in res.reply
    assert "101.18" in res.reply
    assert len(res.grounding_citations) >= 1
    assert len(res.suggested_questions) >= 3


def test_ask_copilot_fallback_search():
    """Verify smart keyword fallback when an unfamiliar query is submitted."""
    res = ask_copilot("qwerty asdfgh zxcvbn 9999")
    assert res.source == "offline_knowledge_engine"
    assert "Tôi không tìm thấy thuật ngữ" in res.reply
    assert len(res.suggested_questions) >= 3




# =============================================================================
# 2. FASTAPI COPILOT SERVING ENDPOINT TESTS (PHASE 6.4)
# =============================================================================

def test_api_copilot_prompts(client):
    """Verify /copilot/prompts returns categorized starter prompts."""
    r = client.get("/copilot/prompts")
    assert r.status_code == 200
    data = r.json()
    assert "prompts" in data
    assert len(data["prompts"]) >= 5
    for p in data["prompts"]:
        assert "category" in p and "prompt" in p


def test_api_copilot_catalog(client):
    """Verify /copilot/catalog returns all 40 items (terms and SOPs)."""
    r = client.get("/copilot/catalog")
    assert r.status_code == 200
    data = r.json()
    assert data["total_items"] == 40
    assert data["aviation_terms_count"] == 18
    assert data["ml_terms_count"] == 14
    assert data["sops_count"] == 8
    assert len(data["terms"]) == 32
    assert len(data["sops"]) == 8


def test_api_copilot_chat_general(client):
    """Verify POST /copilot/chat for general Q&A."""
    payload = {
        "message": "FDP là gì?",
        "model_provider": "offline",
    }
    r = client.post("/copilot/chat", json=payload)
    assert r.status_code == 200
    d = r.json()
    assert d["source"] == "offline_knowledge_engine"
    assert "fdp" in d["matched_terms"]
    assert "Flight Duty Period" in d["reply"]
    assert len(d["grounding_citations"]) >= 1
    assert len(d["suggested_questions"]) >= 1


def test_api_copilot_chat_with_flight_id(client):
    """Verify POST /copilot/chat with flight_id runs grounded analysis."""
    payload = {
        "message": "Chuyến bay này có nguy cơ vi phạm luật gì?",
        "flight_id": 4568,
        "model_provider": "offline",
    }
    r = client.post("/copilot/chat", json=payload)
    assert r.status_code == 200
    d = r.json()
    assert d["source"] == "offline_knowledge_engine"
    assert "flight_UA_4554" in d["matched_terms"]
    assert "Thẩm Định Pháp Lý & Chế Tài Xử Phạt" in d["reply"]
    assert d["flight_context"] is not None
    assert d["flight_context"]["carrier_code"] == "UA"


def test_api_copilot_chat_what_if_intervention(client):
    """Verify POST /copilot/chat with What-If intervention simulation."""
    payload = {
        "message": "Mô phỏng kích hoạt tổ bay dự bị Standby Crew",
        "flight_id": 4568,
        "model_provider": "offline",
    }
    r = client.post("/copilot/chat", json=payload)
    assert r.status_code == 200
    d = r.json()
    assert "what_if_simulation" in d["matched_terms"]
    assert "CREW_STANDBY" in d["reply"]


def test_api_home_page_3_tabs(client):
    """Verify GET / serves the complete 3-tab Web UI."""
    r = client.get("/")
    assert r.status_code == 200
    html = r.text
    # Verify tab buttons and content containers
    assert "tab-advisory" in html
    assert "tab-chat" in html
    assert "tab-catalog" in html
    assert "chat-stream" in html
    assert "chat-input-field" in html
    assert "catalog-grid-container" in html
    assert "American Airlines" in html
    assert "Hartsfield-Jackson" in html


# =============================================================================
# 3. DATA ANALYST COPILOT SPECIALIZED Q&A TESTS
# =============================================================================

def test_ask_copilot_power_bi_4_pages():
    """Verify Data Analyst can query about the 4 Power BI report pages."""
    res = ask_copilot("Ý nghĩa các chỉ số trên 4 trang Power BI Dashboard là gì?")
    assert res.source == "offline_knowledge_engine"
    assert "power_bi_4_pages" in res.matched_terms
    assert "Trang 1: Tổng Quan Khai Thác Vận Hành" in res.reply
    assert "Trang 2: Phân Tích Nguyên Nhân Gốc Rễ" in res.reply
    assert "Trang 3: Điểm Nghẽn Siêu Trung Tâm" in res.reply
    assert "Trang 4: Dự Báo Rủi Ro AI" in res.reply
    assert "58.588 chuyến bay" in res.reply
    assert len(res.suggested_questions) >= 3


def test_ask_copilot_power_bi_page_4_visuals():
    """Verify detailed visual breakdown when user asks specifically about Page 4."""
    # Test exactly what user asked
    res = ask_copilot("giải thích các biểu đồ trên trang số 4 power bi dashboard")
    assert res.source == "offline_knowledge_engine"
    assert "power_bi_page_4" in res.matched_terms
    assert "Trang 4 Power BI: AI Predictive Risk & Regulatory Governance" in res.reply
    assert "Executive KPI Cards" in res.reply
    assert "19.333 chuyến bay" in res.reply or "19.333" in res.reply
    assert "14 CFR § 259.4" in res.reply
    assert "$75.76 Tỷ USD" in res.reply or "75.76" in res.reply
    assert "Biểu Đồ 1: Đấu Trường Đa Mô Hình" in res.reply
    assert "Biểu Đồ 2: Phân Bổ Rủi Ro Chế Tài Theo Hãng Bay" in res.reply
    assert "Biểu Đồ 3: Ma Trận Điểm Nghẽn Siêu Hub & Rủi Ro Tarmac" in res.reply
    assert "Biểu Đồ 4: Bảng Tác Nghiệp Thời Gian Thực Cho Điều Phái Bay" in res.reply
    assert len(res.suggested_questions) >= 3


def test_ask_copilot_power_bi_page_1_and_3_visuals():
    """Verify specific visual breakdown for Page 1 and Page 3."""
    res1 = ask_copilot("giải thích các biểu đồ trên trang số 1 power bi")
    assert res1.source == "offline_knowledge_engine"
    assert "power_bi_page_1" in res1.matched_terms
    assert "Trang 1 Power BI: Executive Operations Overview" in res1.reply

    res3 = ask_copilot("các biểu đồ trên trang 3 power bi có ý nghĩa gì?")
    assert res3.source == "offline_knowledge_engine"
    assert "power_bi_page_3" in res3.matched_terms
    assert "Trang 3 Power BI: Hub Bottlenecks & Route Performance" in res3.reply



def test_ask_copilot_root_cause_analysis():
    """Verify RCA queries for DFW hub bottlenecks and cascading delays."""
    # Test DFW Hub Bottleneck
    res_dfw = ask_copilot("Tại sao Hub DFW thường xuyên bị nghẽn nặng vào khung giờ tối?")
    assert res_dfw.source == "offline_knowledge_engine"
    assert "root_cause_analysis" in res_dfw.matched_terms
    assert "Dallas/Fort Worth" in res_dfw.reply or "DFW" in res_dfw.reply
    assert "American Airlines" in res_dfw.reply
    assert "Taxi-Out" in res_dfw.reply

    # Test Cascading Delays
    res_cascading = ask_copilot("Tại sao nguyên nhân Late Aircraft chiếm tới gần 40% tổng số phút trễ?")
    assert res_cascading.source == "offline_knowledge_engine"
    assert "Late Aircraft" in res_cascading.reply
    assert "domino" in res_cascading.reply.lower()


def test_ask_copilot_dax_and_faa_costs():
    """Verify DAX measures explanation and FAA $101.18 cost benchmark."""
    res = ask_copilot("Giải thích công thức DAX tính Chi Phí Trễ và định mức FAA $101.18/phút.")
    assert res.source == "offline_knowledge_engine"
    assert "dax_formulas" in res.matched_terms
    assert "101.18" in res.reply
    assert "[Total Direct Delay Cost (USD)]" in res.reply
    assert "[OTP % (A14)]" in res.reply
    assert "Fuel Burn" in res.reply or "Nhiên liệu" in res.reply


def test_web_ui_data_analyst_copilot_lens(client):
    """Verify Web UI incorporates the Data Analyst Copilot perspective and slide exporter."""
    r = client.get("/")
    assert r.status_code == 200
    html = r.text

    # Tab 1: Flight & Financial Impact Analytics
    assert "Phân Tích Chuyên Sâu Chuyến Bay & Chi Phí" in html
    assert "Flight & Financial Impact Analytics" in html

    # Tab 2: Analytics Copilot Q&A
    assert "Trợ Lý Phân Tích Nghiệp Vụ" in html
    assert "Analytics Copilot Q&A" in html

    # Tab 3: Data Metric Dictionary
    assert "Từ Điển Chỉ Số & Quy Chuẩn" in html
    assert "Data Metric Dictionary" in html

    # Slide summary exporter button and JS function
    assert "exportSlideSummary" in html
    assert "Xuất Slide Insight" in html

    # DAX measures integration in catalog
    assert "DAX_MEASURES" in html
    assert "dax_measures" in html


def test_validate_claude_openai_deepseek_keys():
    """Verify validation functions for Claude, OpenAI, and DeepSeek with edge cases."""
    from ml.chat import validate_claude_key, validate_openai_key, validate_deepseek_key

    # Claude validations
    ok, msg = validate_claude_key("")
    assert ok is False
    assert "trống" in msg

    ok, msg = validate_claude_key("short")
    assert ok is False
    assert "quá ngắn" in msg

    # DeepSeek validations
    ok, msg = validate_deepseek_key("")
    assert ok is False
    assert "trống" in msg

    ok, msg = validate_deepseek_key("short")
    assert ok is False
    assert "quá ngắn" in msg

    # OpenAI validations
    ok, msg = validate_openai_key("")
    assert ok is False
    assert "trống" in msg

    ok, msg = validate_openai_key("invalid_prefix")
    assert ok is False
    assert "sk-" in msg


def test_ask_copilot_with_custom_provider_models(monkeypatch):
    """Verify ask_copilot delegates to proper provider adapters or gracefully falls back."""
    # 1. Fallback to offline when API call returns None
    res = ask_copilot("FDP là gì?", model_provider="claude", model_name="claude-3-7-sonnet-latest", api_key="sk-ant-testfakekey123456")
    assert res.source == "offline_knowledge_engine"
    assert "FDP" in res.reply

    # 2. Mock Claude API success
    from unittest.mock import MagicMock
    import urllib.request
    import json

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps({
        "content": [{"type": "text", "text": "Claude 3.7 Sonnet: Chuyến bay được phân tích với rủi ro thấp."}]
    }).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=20: mock_resp)

    res_claude = ask_copilot("Phân tích chuyến bay", model_provider="claude", model_name="claude-3-7-sonnet-latest", api_key="sk-ant-valid123456789")
    assert res_claude.source == "llm_claude"
    assert "Claude 3.7 Sonnet" in res_claude.reply

