"""
Unit tests for the 5 Web UI Copilot Enhancements:
1. Deep-link URL parameters support (?flight_id=4568&tab=chat).
2. Chat persistence in localStorage.
3. User-provided LLM API Key setting and /copilot/validate-key endpoint.
4. Visual Stacked Progress Bar for financial delay & tarmac penalty breakdown.
5. Soft Toast notifications with sample flight ID suggestions and 404 error handling.
"""
import pytest
from fastapi.testclient import TestClient

from ml.api import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_homepage_includes_all_five_upgrades(client):
    """Verify that GET / returns HTML containing all 5 required upgrades."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # 1. Deep-link URL Param handling
    assert "window.location.search" in html
    assert "flight_id" in html
    assert "tabParam" in html or "params.get('tab')" in html
    assert "quickFill" in html

    # 2. Chat history persistence (localStorage)
    assert "occ_copilot_chat_history_v2" in html
    assert "saveChatHistoryToStorage" in html
    assert "loadChatHistoryFromStorage" in html

    # 3. Settings modal & LLM API Key input
    assert "settings-modal" in html
    assert "setting-gemini-key" in html
    assert "saveApiKeys" in html
    assert "testApiKey" in html
    assert "/copilot/validate-key" in html

    # 4. Visual Stacked Progress Bar for Financial Cost Breakdown
    assert "stacked-bar-wrapper" in html
    assert "bar-base-delay" in html
    assert "bar-tarmac-penalty" in html
    assert "bar-cash-refund" in html
    assert "cost-callout-box" in html

    # 5. Toast notification system & sample flight ID suggestions (No alerts)
    assert "toast-container" in html
    assert "showToast" in html
    assert "flight-id-error-banner" in html
    assert "SAMPLE_FLIGHTS" in html
    assert "alert(" not in html  # Zero alert() calls


def test_invalid_flight_id_returns_404_with_informative_message(client):
    """Verify that querying a non-existent flight_id via API returns HTTP 404."""
    resp = client.post("/copilot/advisory", json={"flight_id": 999999})
    assert resp.status_code == 404
    detail = resp.json().get("detail", "")
    assert "999999" in detail
    assert "Không tìm thấy" in detail


def test_valid_flight_id_returns_financial_breakdown_for_visual_chart(client):
    """Verify valid flight_id returns all cost fields needed for stacked progress bar."""
    resp = client.post("/copilot/advisory", json={"flight_id": 4568})
    assert resp.status_code == 200
    data = resp.json()
    fin = data["financial_exposure"]
    assert "base_delay_cost_usd" in fin
    assert "tarmac_penalty_exposure_usd" in fin
    assert "cash_refund_exposure_usd" in fin
    assert fin["base_delay_cost_usd"] > 0
    assert fin["tarmac_penalty_exposure_usd"] >= 0


def test_validate_key_endpoint_gemini_empty(client):
    """Verify validation endpoint handles empty key."""
    resp = client.post("/copilot/validate-key", json={"provider": "gemini", "api_key": ""})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert "không được để trống" in data["message"]


def test_validate_key_endpoint_openai_format(client, monkeypatch):
    """Verify validation endpoint checks OpenAI key format."""
    # Mock urllib.request.urlopen for openai validation ping
    from unittest.mock import MagicMock
    import urllib.request
    
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=12: mock_resp)

    resp = client.post(
        "/copilot/validate-key",
        json={"provider": "openai", "api_key": "sk-1234567890abcdef1234567890"},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is True

    resp_bad = client.post(
        "/copilot/validate-key",
        json={"provider": "openai", "api_key": "invalid_key"},
    )
    assert resp_bad.status_code == 200
    assert resp_bad.json()["valid"] is False


def test_chat_endpoint_accepts_custom_api_key(client):
    """Verify chat endpoint accepts optional api_key from frontend settings."""
    resp = client.post(
        "/copilot/chat",
        json={
            "message": "FDP là gì?",
            "model_provider": "offline",
            "api_key": "test_user_key_from_settings",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "FDP" in data["reply"] or "Duty" in data["reply"]
    assert len(data["grounding_citations"]) > 0


def test_slide_insight_modal_and_export_buttons_exist(client):
    """Verify that homepage includes the Executive Slide Modal, PPTX, HTML Deck, and Markdown export."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Slide Modal & interactive elements
    assert "slide-modal" in html
    assert "openSlideModal" in html
    assert "downloadSlidePptx" in html
    assert "openSlideDeckHtml" in html
    assert "downloadSlideMarkdown" in html
    assert "slide-preview-body" in html
    assert "stab-1" in html


def test_embed_chat_endpoint_returns_compact_multi_page_ui(client):
    """Verify GET /embed/chat returns the ultra-compact multi-page embed chat frame."""
    resp = client.get("/embed/chat")
    assert resp.status_code == 200
    html = resp.text

    # Header and page switcher
    assert "mini-header" in html
    assert "page-switcher" in html
    assert "btn-p1" in html
    assert "btn-p2" in html
    assert "btn-p3" in html
    assert "btn-p4" in html

    # Page config & multi-page support
    assert "PAGE_CONFIG" in html
    assert "Trang 1: Executive Overview" in html
    assert "Trang 2: Delay Root-Causes" in html
    assert "Trang 3: Hubs & Routes" in html
    assert "Trang 4: AI Risk & Governance" in html

    # Core elements: chips, input bar, chat stream
    assert "starter-chips-container" in html
    assert "chat-stream" in html
    assert "user-input" in html
    assert "btn-send" in html
    assert "formatMarkdown" in html
    assert "context-bar" in html

    # Clean code: zero blocking alerts
    assert "alert(" not in html


def test_embed_chat_with_deep_link_parameters(client):
    """Verify GET /embed/chat accepts page, flight_id, carrier, origin, dest, theme, prompt."""
    resp = client.get(
        "/embed/chat",
        params={
            "page": "4",
            "flight_id": "4568",
            "carrier": "UA",
            "origin": "LAS",
            "dest": "BOS",
            "theme": "dark",
            "prompt": "Đánh giá rủi ro chuyến bay",
        },
    )
    assert resp.status_code == 200
    assert "SkyOps Copilot | Embedded Assistant" in resp.text
    assert "switchPage" in resp.text
    assert "submitText" in resp.text


def test_dax_measures_contain_header_ai_buttons():
    """Verify that dashboards/powerbi/measures.dax defines Header AI buttons for all 4 pages."""
    from pathlib import Path
    dax_path = Path("dashboards/powerbi/measures.dax")
    assert dax_path.exists()
    content = dax_path.read_text(encoding="utf-8")

    assert "AI Copilot Header URL - Page 1" in content
    assert "AI Copilot Header URL - Page 2" in content
    assert "AI Copilot Header URL - Page 3" in content
    assert "AI Copilot Header URL - Page 4" in content
    assert "AI Copilot Header Label - Page 1" in content
    assert "AI Copilot Header Tooltip - Page 1" in content
    assert "AI Copilot Universal Header URL" in content
    assert "AI Header Button Fill Color" in content
    assert "AI Header Button Text Color" in content
    assert "/embed/chat" in content


def test_settings_modal_dark_mode_visibility_and_classes(client):
    """Verify settings modal title, status box and text colors in dark and light modes."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Setting status box classes & styles
    assert "setting-status-box" in html
    assert ".setting-status-box.status-success" in html
    assert ":root[data-theme=\"dark\"] .setting-status-box.status-success" in html
    assert ":root[data-theme=\"dark\"] .settings-modal-title" in html
    assert "setting-status-text" in html


def test_main_tab_persistence_across_refresh(client):
    """Verify that main web page saves and restores active tab via sessionStorage/localStorage."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Check tab persistence logic in switchTab
    assert "sessionStorage.setItem('occ_active_tab'" in html
    assert "localStorage.setItem('occ_active_tab'" in html
    assert "sessionStorage.getItem('occ_active_tab')" in html


def test_powerbi_embed_chat_session_storage_persistence(client):
    """Verify that Power BI embed chat preserves conversation on refresh via sessionStorage and clears on reset."""
    resp = client.get("/embed/chat")
    assert resp.status_code == 200
    html = resp.text

    # Dual persistence (sessionStorage + localStorage for permanence across tab closes)
    assert "skyops_embed_chat_history_session" in html
    assert "saveSessionChat" in html
    assert "loadSessionChat" in html
    assert "sessionStorage.setItem(EMBED_SESSION_KEY" in html
    assert "localStorage.setItem(EMBED_SESSION_KEY" in html
    assert "sessionStorage.getItem(EMBED_SESSION_KEY" in html
    assert "localStorage.getItem(EMBED_SESSION_KEY" in html
    assert "sessionStorage.removeItem(EMBED_SESSION_KEY" in html
    assert "localStorage.removeItem(EMBED_SESSION_KEY" in html


def test_toast_dark_mode_visibility_and_contrast(client):
    """Verify toast notification has high-contrast background and text in dark mode."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Dark mode toast rules
    assert ':root[data-theme="dark"] .toast' in html
    assert ':root[data-theme="dark"] .toast-header' in html
    assert ':root[data-theme="dark"] .toast-body' in html
    assert ':root[data-theme="dark"] .toast.toast-success' in html
    assert "toast-hint-title" in html


def test_powerbi_embed_chat_turn_anchoring_scroll(client):
    """Verify that Power BI embed chat anchors scrolling to user's question instead of jumping to bottom."""
    resp = client.get("/embed/chat")
    assert resp.status_code == 200
    html = resp.text

    # Check focusOnCurrentTurn implementation and lastUserMsgElement anchoring
    assert "lastUserMsgElement" in html
    assert "function focusOnCurrentTurn()" in html
    assert "lastUserMsgElement = msgDiv;" in html
    assert "top: Math.max(0, relativeTop - 12)" in html


def test_copilot_runtime_mode_endpoints(client):
    """Verify runtime-mode GET and POST endpoints for cross-client state sync."""
    # 1. GET runtime mode
    get_res = client.get("/copilot/runtime-mode")
    assert get_res.status_code == 200
    data = get_res.json()
    assert "provider" in data
    assert "is_online" in data
    assert "server_has_gemini_key" in data

    # 2. POST update runtime mode to gemini (online)
    post_res = client.post(
        "/copilot/runtime-mode",
        json={"provider": "gemini", "api_key": "test-key-123", "theme": "dark"},
    )
    assert post_res.status_code == 200
    res_data = post_res.json()
    assert res_data["status"] == "ok"
    assert res_data["mode"]["provider"] == "gemini"
    assert res_data["mode"]["is_online"] is True
    assert res_data["mode"]["theme"] == "dark"

    # 3. POST update runtime mode to offline
    post_offline = client.post(
        "/copilot/runtime-mode",
        json={"provider": "offline", "api_key": None, "theme": "light"},
    )
    assert post_offline.status_code == 200
    off_data = post_offline.json()
    assert off_data["mode"]["provider"] == "offline"
    assert off_data["mode"]["is_online"] is False


def test_cross_tab_realtime_synchronization_bus(client):
    """Verify that both Main Web UI and Power BI embed frame contain BroadcastChannel, storage listeners and sync bus."""
    # Main Web UI
    resp_main = client.get("/")
    assert resp_main.status_code == 200
    main_html = resp_main.text
    assert "skyops_runtime_sync" in main_html
    assert "broadcastModeUpdate" in main_html
    assert "toggleHeaderOnlineMode" in main_html
    assert "header-llm-badge" in main_html
    assert "skyops_sync_tick" in main_html
    assert "/copilot/runtime-mode" in main_html

    # Power BI Embed Chat
    resp_embed = client.get("/embed/chat")
    assert resp_embed.status_code == 200
    embed_html = resp_embed.text
    assert "skyops_runtime_sync" in embed_html
    assert "embedSyncChannel" in embed_html
    assert "window.addEventListener('storage'" in embed_html
    assert "badgeSyncPulse" in embed_html
    assert "embed-sync-toast" in embed_html
    assert "toggleEmbedOnlineMode" in embed_html
    assert "/copilot/runtime-mode" in embed_html


def test_typewriter_streaming_engine_present(client):
    """Verify that Typewriter streaming effect is integrated in both Main UI and Embed frame."""
    # Main UI
    resp_main = client.get("/")
    assert resp_main.status_code == 200
    html_main = resp_main.text
    assert "typewriter-cursor" in html_main
    assert "streamChatMessageToDOM" in html_main
    assert "stream-text-node" in html_main

    # Embed frame
    resp_embed = client.get("/embed/chat")
    assert resp_embed.status_code == 200
    html_embed = resp_embed.text
    assert "typewriter-cursor" in html_embed
    assert "streamMessageDOM" in html_embed
    assert "stream-content" in html_embed


def test_voice_recognition_web_speech_api(client):
    """Verify that Web Speech API microphone voice input is present in Main UI and Embed frame."""
    # Main UI
    resp_main = client.get("/")
    assert resp_main.status_code == 200
    html_main = resp_main.text
    assert "btn-voice-main" in html_main
    assert "toggleVoiceInput" in html_main
    assert "voice-btn" in html_main
    assert "voicePulseRing" in html_main

    # Embed frame
    resp_embed = client.get("/embed/chat")
    assert resp_embed.status_code == 200
    html_embed = resp_embed.text
    assert "btn-voice-embed" in html_embed
    assert "toggleVoiceInput" in html_embed
    assert "voice-btn" in html_embed
    assert "voicePulseRing" in html_embed


def test_export_occ_chat_audit_log(client):
    """Verify that OCC Chat Audit Log export (Markdown & PDF) is available in Main UI and Embed frame."""
    # Main UI
    resp_main = client.get("/")
    assert resp_main.status_code == 200
    html_main = resp_main.text
    assert "btn-export-chat-audit" in html_main
    assert "audit-export-modal" in html_main
    assert "generateOCCAuditLogMarkdown" in html_main
    assert "downloadAuditLogMarkdown" in html_main
    assert "printOCCAuditLog" in html_main
    assert "14 CFR § 259.4" in html_main

    # Embed frame
    resp_embed = client.get("/embed/chat")
    assert resp_embed.status_code == 200
    html_embed = resp_embed.text
    assert "btn-embed-export-audit" in html_embed
    assert "embed-audit-modal" in html_embed
    assert "generateEmbedAuditLogMarkdown" in html_embed
    assert "downloadEmbedAuditMarkdown" in html_embed
    assert "printEmbedAuditLog" in html_embed


def test_gemini_speed_optimization_and_model_caching():
    """Verify Gemini API configuration prioritizes fast models and caches active endpoint."""
    from ml.chat import FAST_GEMINI_CANDIDATES, validate_gemini_key

    # Check candidates
    assert "gemini-3.8-flash" in FAST_GEMINI_CANDIDATES  # Supported flagship model
    assert "gemini-2.5-flash" in FAST_GEMINI_CANDIDATES
    assert "gemini-2.0-flash" in FAST_GEMINI_CANDIDATES
    assert "gemini-1.5-flash" in FAST_GEMINI_CANDIDATES

    # Test key validation error format
    ok, msg = validate_gemini_key("")
    assert ok is False
    assert "trống" in msg

    ok_short, msg_short = validate_gemini_key("short")
    assert ok_short is False
    assert "quá ngắn" in msg_short


def test_collapsible_history_cards_on_refresh_and_reopen(client):
    """Verify that both main web and embed chat render collapsible question cards with expandable answers upon refresh."""
    # 1. Main Web UI
    resp_main = client.get("/")
    assert resp_main.status_code == 200
    html_main = resp_main.text
    assert "chat-history-card" in html_main
    assert "chat-history-header" in html_main
    assert "chat-history-question" in html_main
    assert "chat-history-answer-drawer" in html_main
    assert "groupChatMessagesIntoPairs" in html_main
    assert "renderMainHistoryCard" in html_main
    assert "toggleMainHistoryCard" in html_main
    assert "toggleAllMainHistoryCards" in html_main
    assert "Báo Cáo Phân Tích Chẩn Đoán" in html_main
    assert "history-toggle-badge" in html_main

    # 2. Embed Chat UI
    resp_embed = client.get("/embed/chat")
    assert resp_embed.status_code == 200
    html_embed = resp_embed.text
    assert "chat-history-card" in html_embed
    assert "chat-history-header" in html_embed
    assert "chat-history-question" in html_embed
    assert "chat-history-answer-drawer" in html_embed
    assert "groupEmbedTurnsIntoPairs" in html_embed
    assert "renderEmbedHistoryCard" in html_embed
    assert "toggleEmbedHistoryCard" in html_embed
    assert "toggleAllEmbedHistoryCards" in html_embed
    assert "Báo Cáo Phân Tích" in html_embed







