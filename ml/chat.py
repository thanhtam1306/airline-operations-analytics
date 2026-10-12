"""
Interactive Conversational Q&A & Intelligent Chatbot Engine (OCC Decision Copilot).
Phase 6.3 - Hybrid Conversational Q&A (LLM with Zero-Dependency Offline Grounded Fallback).

Provides conversational domain grounding for:
1. Operations Control Center (OCC) dispatchers handling high-risk flights.
2. Aviation & Machine Learning concepts, formulas, and metric interpretations.
3. Standard Operating Procedures (8 dynamic SOPs) with step-by-step role checklists.
4. US DOT (14 CFR) & Vietnam CAAV regulatory compliance & financial delay cost exposure.
5. What-If operational dispatch simulation (reschedule, standby crew, speedup, tail swap).
"""
from __future__ import annotations

import json
import logging
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from ml.advisory import (
    DispatchAdvisory,
    generate_dispatch_advisory,
    lookup_flight_advisory,
    simulate_what_if,
)
from ml.copilot import (
    KNOWLEDGE_TERMS,
    SOP_CHECKLISTS,
    KnowledgeTerm,
    SOPChecklist,
    explain_term,
    format_catalog_markdown,
    format_sop_markdown,
    format_term_card_markdown,
    get_sop_checklist,
    lookup_term,
    search_knowledge,
    strip_accents,
    tokenize,
)
from ml.regulatory_engine import evaluate_regulatory_compliance


logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ChatMessage:
    role: str  # "user", "assistant", "system"
    content: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


def _sanitize_chat_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _sanitize_chat_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_sanitize_chat_json(v) for v in obj]
    elif hasattr(obj, "item"):
        return obj.item()
    elif hasattr(obj, "isoformat"):
        return obj.isoformat()
    return obj


@dataclass
class ChatResponse:
    reply: str
    source: str  # "offline_knowledge_engine", "llm_gemini", "llm_openai"
    matched_terms: List[str] = field(default_factory=list)
    grounding_citations: List[str] = field(default_factory=list)
    suggested_questions: List[str] = field(default_factory=list)
    flight_context: Optional[Dict[str, Any]] = None
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return _sanitize_chat_json(asdict(self))



# =============================================================================
# DEFAULT QUICK CHIPS & SUGGESTED PROMPTS (DATA ANALYST COPILOT LENS)
# =============================================================================

DEFAULT_SUGGESTED_QUESTIONS = [
    "Ý nghĩa các chỉ số trên 4 trang Power BI Dashboard là gì?",
    "Tại sao Hub DFW và ORD thường xuyên bị nghẽn nặng vào khung giờ tối?",
    "Giải thích công thức DAX tính Chi Phí Trễ và định mức FAA $101.18/phút.",
    "Tại sao nguyên nhân Late Aircraft chiếm tới gần 40% tổng số phút trễ?",
    "Cách đọc ma trận Đấu Trường Mô Hình (AUC, Lift @ 10%, Brier Score) trên Trang 4?",
    "Quy tắc Tarmac Delay 180 phút của US DOT phạt bao nhiêu USD và yêu cầu gì?",
]


def get_copilot_quick_prompts() -> List[Dict[str, str]]:
    """Return categorized starter prompt chips tailored for Data Analyst Copilot."""
    return [
        {
            "category": "📊 Báo Cáo Power BI",
            "prompt": "Ý nghĩa các chỉ số trên 4 trang Power BI Dashboard là gì?",
        },
        {
            "category": "🔍 Nguyên Nhân Gốc Rễ (RCA)",
            "prompt": "Tại sao Hub DFW và ORD thường xuyên bị nghẽn nặng vào khung giờ tối?",
        },
        {
            "category": "💵 Công Thức DAX & Chi Phí",
            "prompt": "Giải thích công thức DAX tính Chi Phí Trễ và định mức FAA $101.18/phút.",
        },
        {
            "category": "🌪️ Hiệu Ứng Domino",
            "prompt": "Tại sao nguyên nhân Late Aircraft chiếm tới gần 40% tổng số phút trễ?",
        },
        {
            "category": "🤖 Đấu Trường Mô Hình",
            "prompt": "Cách đọc ma trận Đấu Trường Mô Hình (AUC, Lift @ 10%, Brier Score) trên Trang 4?",
        },
        {
            "category": "⚖️ Chế Tài & Bồi Hoàn",
            "prompt": "Quy tắc Tarmac Delay 180 phút của US DOT phạt bao nhiêu USD và yêu cầu gì?",
        },
    ]


# =============================================================================
# HYBRID LLM CLIENTS (GEMINI & OPENAI)
# =============================================================================

def _build_system_prompt(advisory_summary: Optional[str] = None) -> str:
    """Build grounding system prompt for LLMs containing domain context."""
    prompt_parts = [
        "Bạn là Trợ Lý Phân Tích Dữ Liệu Hàng Không & Nghiệp Vụ Tác Nghiệp (Data Analyst Copilot) của Airline Data Platform.",
        "Nhiệm vụ của bạn là hỗ trợ Data Analyst, BI Developer, Quản lý Vận hành và Lãnh đạo Hàng không.",
        "Quy tắc làm việc bất di bất dịch:",
        "1. Luôn căn cứ vào dữ liệu số liệu cụ thể và các điều luật định danh (US DOT 14 CFR, FAA FAR, Vietnam CAAV).",
        "2. Nêu rõ các con số định chuẩn: Chi phí trễ trung bình FAA $101.18/phút, Phạt Tarmac Delay 14 CFR § 259.4 tới $37,377 USD/pax, Quy chuẩn hoàn tiền 14 CFR § 260.6 (trễ >= 3h nội địa / >= 6h quốc tế).",
        "3. Khi nói về 4 trang Power BI: Diễn giải rõ mạch Gartner (Descriptive Overview -> Diagnostic Root Cause -> Diagnostic Deep-dive Hub -> Predictive & Prescriptive Governance).",
        "4. Khi nói về DAX: Nêu rõ công thức DAX chuẩn trong measures.dax và ý nghĩa kinh doanh.",
        "5. Khi nói về mô hình ML: Nêu rõ xác suất trễ, risk band, lift @ 10%, ngưỡng tối ưu (threshold 0.2709), Brier score.",
        "6. Đưa ra phân tích sắc bén, logic, định dạng Markdown chuyên nghiệp phục vụ trích xuất slide báo cáo.",
    ]
    if advisory_summary:
        prompt_parts.append(f"\n--- NGỮ CẢNH CHUYẾN BAY ĐANG XÉT ---\n{advisory_summary}\n----------------------------------")
    return "\n".join(prompt_parts)


# Flagship LLM Model Candidates (2025-2026 Production Generation)
FAST_GEMINI_CANDIDATES = [
    "gemini-3.8-flash",
    "gemini-3.8-pro",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-flash-latest",
]
_CACHED_WORKING_GEMINI_MODEL: Optional[str] = None


def _call_gemini_api(
    message: str,
    api_key: str,
    system_prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
    model_name: Optional[str] = None,
) -> Optional[str]:
    """Call Google Gemini REST API with multi-model fallback and speed optimization."""
    global _CACHED_WORKING_GEMINI_MODEL
    clean_key = (api_key or "").strip()
    if not clean_key:
        return None

    # Prioritize requested model, then previously confirmed working model
    if model_name:
        candidate_models = [model_name] + [m for m in FAST_GEMINI_CANDIDATES if m != model_name]
    elif _CACHED_WORKING_GEMINI_MODEL:
        candidate_models = [_CACHED_WORKING_GEMINI_MODEL] + [m for m in FAST_GEMINI_CANDIDATES if m != _CACHED_WORKING_GEMINI_MODEL]
    else:
        candidate_models = list(FAST_GEMINI_CANDIDATES)

    contents = []
    if history:
        for turn in history[-6:]:  # Keep last 3 turns
            role = "user" if turn.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": turn.get("content", "")}]})

    contents.append({"role": "user", "parts": [{"text": message}]})

    body = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024,
            "topK": 40,
            "topP": 0.95,
        },
    }
    encoded_body = json.dumps(body).encode("utf-8")

    for m_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={clean_key}"
        req = urllib.request.Request(
            url,
            data=encoded_body,
            headers={
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "User-Agent": "SkyOps-Copilot/2.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=18) as response:
                if response.status == 200:
                    res_data = json.loads(response.read().decode("utf-8"))
                    candidates = res_data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            _CACHED_WORKING_GEMINI_MODEL = m_name
                            return parts[0].get("text", "")
        except urllib.error.HTTPError as e:
            if e.code in (404, 400, 503):
                # Try next model candidate
                continue
            logger.warning(f"Gemini API request failed ({e.code}): {e}. Falling back.")
            break
        except Exception as e:
            logger.warning(f"Gemini API request failed: {e}. Falling back.")
            break
    return None


def validate_gemini_key(api_key: str, model_name: Optional[str] = None) -> Tuple[bool, str]:
    """Test ping Google Gemini API with the given API key, with multi-model check."""
    global _CACHED_WORKING_GEMINI_MODEL
    clean_key = (api_key or "").strip()
    if not clean_key:
        return False, "API Key không được để trống."

    if len(clean_key) < 15:
        return False, "API Key quá ngắn hoặc không hợp lệ. Vui lòng kiểm tra lại chuỗi khóa."

    if model_name:
        candidate_models = [model_name] + [m for m in FAST_GEMINI_CANDIDATES if m != model_name]
    elif _CACHED_WORKING_GEMINI_MODEL:
        candidate_models = [_CACHED_WORKING_GEMINI_MODEL] + [m for m in FAST_GEMINI_CANDIDATES if m != _CACHED_WORKING_GEMINI_MODEL]
    else:
        candidate_models = list(FAST_GEMINI_CANDIDATES)

    body = {
        "contents": [{"role": "user", "parts": [{"text": "Ping"}]}],
        "generationConfig": {"maxOutputTokens": 5}
    }
    encoded_body = json.dumps(body).encode("utf-8")

    last_error = ""
    for m_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={clean_key}"
        req = urllib.request.Request(
            url,
            data=encoded_body,
            headers={
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "User-Agent": "SkyOps-Copilot/2.0",
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    _CACHED_WORKING_GEMINI_MODEL = m_name
                    return True, f"Kết nối Google Gemini thành công (Mô hình: {m_name}, API Key hợp lệ)!"
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="ignore")
            try:
                err_json = json.loads(err_msg)
                msg = err_json.get("error", {}).get("message", str(e))
            except Exception:
                msg = str(e)
            last_error = msg
            if e.code in (404, 400, 503):
                continue
            return False, f"Xác thực thất bại: {msg}"
        except Exception as e:
            return False, f"Lỗi kết nối kiểm tra Gemini: {str(e)}"

    return False, f"Xác thực thất bại: {last_error}"


def _call_claude_api(
    message: str,
    api_key: str,
    system_prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
    model_name: Optional[str] = None,
) -> Optional[str]:
    """Call Anthropic Messages REST API (Claude 3.7 Sonnet, 3.5 Sonnet, 3.5 Haiku)."""
    clean_key = (api_key or "").strip()
    if not clean_key:
        return None

    target_model = model_name or "claude-3-7-sonnet-latest"
    url = "https://api.anthropic.com/v1/messages"

    messages = []
    if history:
        for turn in history[-6:]:
            role = "user" if turn.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": turn.get("content", "")})
    messages.append({"role": "user", "content": message})

    body: Dict[str, Any] = {
        "model": target_model,
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": messages,
    }
    if "claude-3-7" not in target_model:
        body["temperature"] = 0.2

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": clean_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "User-Agent": "SkyOps-Copilot/2.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status == 200:
                res_data = json.loads(response.read().decode("utf-8"))
                contents = res_data.get("content", [])
                for block in contents:
                    if block.get("type") == "text":
                        return block.get("text", "")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        logger.warning(f"Claude API failed ({e.code}): {err_msg}")
    except Exception as e:
        logger.warning(f"Claude API request failed ({target_model}): {e}. Falling back.")
    return None


def validate_claude_key(api_key: str, model_name: Optional[str] = None) -> Tuple[bool, str]:
    """Test ping Anthropic Claude API with the given API key."""
    clean_key = (api_key or "").strip()
    if not clean_key:
        return False, "Anthropic Claude API Key không được để trống."
    if len(clean_key) < 15:
        return False, "Anthropic API Key quá ngắn hoặc không hợp lệ (thường bắt đầu bằng 'sk-ant-')."

    target_model = model_name or "claude-3-5-haiku-latest"
    body = {
        "model": target_model,
        "max_tokens": 5,
        "messages": [{"role": "user", "content": "ping"}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": clean_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "User-Agent": "SkyOps-Copilot/2.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                return True, f"Kết nối Anthropic Claude thành công (Mô hình: {target_model}, API Key hợp lệ)!"
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        try:
            err_json = json.loads(err_msg)
            msg = err_json.get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        return False, f"Xác thực Claude thất bại: {msg}"
    except Exception as e:
        return False, f"Lỗi kết nối kiểm tra Claude: {str(e)}"
    return False, "Không thể xác thực khóa Claude."


def _call_openai_api(
    message: str,
    api_key: str,
    system_prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
    model_name: Optional[str] = None,
) -> Optional[str]:
    """Call OpenAI REST API supporting reasoning models (o3-mini, o1) and chat models (gpt-4.5-preview, gpt-4o)."""
    clean_key = (api_key or "").strip()
    if not clean_key:
        return None

    target_model = model_name or "o3-mini"
    is_reasoning = any(m in target_model.lower() for m in ["o1", "o3", "reasoner"])

    url = "https://api.openai.com/v1/chat/completions"
    messages = []

    # Reasoning models in OpenAI (o1, o3-mini) prefer 'developer' role
    sys_role = "developer" if is_reasoning else "system"
    messages.append({"role": sys_role, "content": system_prompt})

    if history:
        for turn in history[-6:]:
            role = turn.get("role", "user")
            messages.append({"role": role, "content": turn.get("content", "")})

    messages.append({"role": "user", "content": message})

    body: Dict[str, Any] = {
        "model": target_model,
        "messages": messages,
    }

    if is_reasoning:
        body["max_completion_tokens"] = 1200
    else:
        body["max_tokens"] = 1024
        body["temperature"] = 0.2

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_key}",
            "User-Agent": "SkyOps-Copilot/2.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status == 200:
                res_data = json.loads(response.read().decode("utf-8"))
                choices = res_data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        logger.warning(f"OpenAI API failed ({e.code}): {err_msg}")
    except Exception as e:
        logger.warning(f"OpenAI API request failed ({target_model}): {e}. Falling back.")
    return None


def validate_openai_key(api_key: str, model_name: Optional[str] = None) -> Tuple[bool, str]:
    """Test ping OpenAI API with the given API key."""
    clean_key = (api_key or "").strip()
    if not clean_key:
        return False, "OpenAI API Key không được để trống."
    if not (clean_key.startswith("sk-") and len(clean_key) >= 15):
        return False, "Định dạng OpenAI API Key không hợp lệ (cần bắt đầu bằng 'sk-')."

    req = urllib.request.Request(
        "https://api.openai.com/v1/models",
        headers={
            "Authorization": f"Bearer {clean_key}",
            "User-Agent": "SkyOps-Copilot/2.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                m_str = model_name or "o3-mini / o1 / GPT-4.5 / GPT-4o"
                return True, f"Kết nối OpenAI thành công (Sẵn sàng phục vụ: {m_str}, API Key hợp lệ)!"
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        try:
            err_json = json.loads(err_msg)
            msg = err_json.get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        return False, f"Xác thực OpenAI thất bại: {msg}"
    except Exception as e:
        return False, f"Lỗi kết nối kiểm tra OpenAI: {str(e)}"
    return False, "Không thể xác thực khóa OpenAI."


def _call_deepseek_api(
    message: str,
    api_key: str,
    system_prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
    model_name: Optional[str] = None,
) -> Optional[str]:
    """Call DeepSeek API supporting DeepSeek-R1 (deepseek-reasoner) and DeepSeek-V3 (deepseek-chat)."""
    clean_key = (api_key or "").strip()
    if not clean_key:
        return None

    target_model = model_name or "deepseek-reasoner"
    url = "https://api.deepseek.com/chat/completions"

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for turn in history[-6:]:
            role = turn.get("role", "user")
            messages.append({"role": role, "content": turn.get("content", "")})
    messages.append({"role": "user", "content": message})

    body: Dict[str, Any] = {
        "model": target_model,
        "messages": messages,
        "max_tokens": 1200,
    }
    if "reasoner" not in target_model.lower():
        body["temperature"] = 0.2

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_key}",
            "User-Agent": "SkyOps-Copilot/2.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status == 200:
                res_data = json.loads(response.read().decode("utf-8"))
                choices = res_data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
    except Exception as e:
        logger.warning(f"DeepSeek API request failed ({target_model}): {e}. Falling back.")
    return None


def validate_deepseek_key(api_key: str, model_name: Optional[str] = None) -> Tuple[bool, str]:
    """Test ping DeepSeek API with the given API key."""
    clean_key = (api_key or "").strip()
    if not clean_key:
        return False, "DeepSeek API Key không được để trống."
    if len(clean_key) < 15:
        return False, "DeepSeek API Key quá ngắn hoặc không hợp lệ."

    req = urllib.request.Request(
        "https://api.deepseek.com/models",
        headers={
            "Authorization": f"Bearer {clean_key}",
            "User-Agent": "SkyOps-Copilot/2.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                m_str = model_name or "deepseek-reasoner (R1) / deepseek-chat (V3)"
                return True, f"Kết nối DeepSeek thành công (Mô hình: {m_str}, API Key hợp lệ)!"
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        try:
            err_json = json.loads(err_msg)
            msg = err_json.get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        return False, f"Xác thực DeepSeek thất bại: {msg}"
    except Exception as e:
        return False, f"Lỗi kết nối kiểm tra DeepSeek: {str(e)}"
    return False, "Không thể xác thực khóa DeepSeek."


# =============================================================================
# OFFLINE OCC DOMAIN GROUNDED ENGINE (100% RELIABLE & ZERO DEPENDENCY)
# =============================================================================

def _ask_offline_knowledge_engine(
    message: str,
    flight_context: Optional[Dict[str, Any]] = None,
    advisory: Optional[DispatchAdvisory] = None,
) -> ChatResponse:
    """
    Intelligent, domain-grounded offline rule-based knowledge engine.
    Guarantees 100% uptime, zero tokens, and zero external network latency.
    """
    # Normalize spoken thousand separators: e.g. "4.568" or "4,568" -> "4568"
    norm_msg = re.sub(r"(?<=\d)[\.,](?=\d)", "", message)
    clean_msg = strip_accents(norm_msg.lower().strip())
    tokens = set(tokenize(clean_msg))

    matched_terms: List[str] = []
    citations: List[str] = []
    suggested: List[str] = []

    # -------------------------------------------------------------------------
    # INTENT 1: What-If Operational Simulation Queries
    # -------------------------------------------------------------------------
    sim_phrases = [
        "what if", "what-if", "mo phong", "can thiep", "doi gio", "reschedule",
        "standby crew", "to bay du bi", "bay nhanh", "speedup",
        "airborne make", "airborne make up", "doi tau bay", "tail swap", "giam chi phi",
    ]
    is_sim_intent = any(p in clean_msg for p in sim_phrases)

    if is_sim_intent:
        # Check what scenario was requested
        scenario = "reschedule_hour"
        new_hour = 10
        hour_match = re.search(r"(?:sang|luc|ve)\s*(\d{1,2})", clean_msg)
        if hour_match:
            try:
                parsed_h = int(hour_match.group(1))
                if 0 <= parsed_h <= 23:
                    new_hour = parsed_h
            except ValueError:
                pass

        params = {"new_dep_hour": new_hour}
        desc = f"Đổi giờ bay sang {new_hour}:00 né khung giờ nghẽn cao điểm"

        if any(w in clean_msg for w in ["crew", "to bay", "phi cong", "fdp", "standby"]):
            scenario = "crew_standby"
            params = {}
            desc = "Kích hoạt tổ bay dự bị (FAR Part 117 Hot Standby Crew)"
        elif any(w in clean_msg for w in ["speedup", "bay nhanh", "makeup", "make up", "cost index"]):
            scenario = "airborne_speedup"
            params = {"cost_index": 85}
            desc = "Tăng Cost Index bay bù giờ trên không (Airborne Make-up Time)"
        elif any(w in clean_msg for w in ["tail", "tau bay", "may bay", "aog", "swap", "trao"]):
            scenario = "tail_swap"
            params = {}
            desc = "Đổi tàu bay dự phòng tại sân (Spare Aircraft Tail Swap)"

        # If we have an advisory, run simulation!
        if advisory is None and flight_context is not None:
            try:
                advisory = generate_dispatch_advisory(
                    carrier_code=flight_context.get("carrier_code"),
                    origin=flight_context.get("origin"),
                    dest=flight_context.get("dest"),
                    flight_date=flight_context.get("flight_date"),
                    dep_hour=flight_context.get("dep_hour"),
                    flight_number=flight_context.get("flight_number"),
                )
            except Exception:
                advisory = None

        if advisory is not None:
            sim_res = simulate_what_if(advisory, scenario, params)
            out = sim_res.get("simulated_outcome", {})
            minutes_saved = out.get("minutes_saved", out.get("airborne_minutes_recovered", 0))
            cost_saved = out.get("cost_saved_usd", out.get("net_savings_usd", 0.0))
            net_saved = out.get("net_financial_savings_usd", out.get("net_savings_usd", 0.0))
            new_prob = out.get("new_delay_probability", 0.0)

            reply = (
                f"### 🧪 Kết Quả Mô Phỏng Can Thiệp Điều Hành ({scenario.upper()})\n"
                f"**Chuyến bay**: `{advisory.flight_context.carrier_code}{advisory.flight_context.flight_number or ''}` "
                f"({advisory.flight_context.origin} ➔ {advisory.flight_context.dest})  \n"
                f"**Phương án can thiệp**: **{desc}**\n\n"
                f"- **Xác suất trễ ban đầu**: `{(advisory.prediction_context.delay_probability*100):.1f}%` ➔ **Sau can thiệp**: `{(new_prob*100):.1f}%`\n"
                f"- **Thời gian bay thu hồi**: **`{minutes_saved} phút`**.\n"
                f"- **Chi phí vận hành tiết kiệm**: **`${cost_saved:,.2f} USD`**.\n"
                f"- **Bảo toàn tài chính ròng**: **`${net_saved:,.2f} USD`**.\n\n"
                f"🏆 **Đánh Giá Hiệu Quả Đầu Tư (ROI Verdict)**:\n> **{out.get('roi_verdict', 'Hiệu quả cao')}**\n"
            )
        else:
            reply = (
                f"### 🧪 4 Phương Án Can Thiệp Điều Hành Tác Nghiệp (What-If Operational Toolkit)\n\n"
                f"Bộ công cụ mô phỏng What-If của OCC Copilot hỗ trợ tính toán tức thì ROI tài chính và thời gian thu hồi cho 4 kịch bản:\n\n"
                f"1. **🔄 Đổi giờ bay né cao điểm (`reschedule_hour`)**:\n"
                f"   - *Cơ chế*: Dời giờ khởi hành sang khung giờ thấp điểm (ví dụ 10:00 thay vì 17:00-19:00).\n"
                f"   - *Hiệu quả*: Giảm mật độ đường lăn từ 35 xuống 5 chuyến/giờ, cắt giảm 60-80% xác suất trễ.\n\n"
                f"2. **👨‍✈️ Kích hoạt tổ bay dự bị (`crew_standby`)**:\n"
                f"   - *Cơ chế*: Kích hoạt Standby Crew theo FAR Part 117 khi tổ bay chính tiếp cận trần FDP.\n"
                f"   - *Hiệu quả*: Triệt tiêu nguy cơ hủy chuyến do thiếu phi công, bảo toàn $8,000 - $12,000 USD.\n\n"
                f"3. **⚡ Tăng tốc bay bù giờ trên không (`airborne_speedup`)**:\n"
                f"   - *Cơ chế*: Điều chỉnh Cost Index (CI) từ 25 lên 85 qua FMS/CDU.\n"
                f"   - *Hiệu quả*: Thu hồi 12-18 phút bay, bảo đảm slot đến và tránh bẫy giờ giới nghiêm Curfew.\n\n"
                f"4. **✈️ Đổi tàu bay dự bị (`tail_swap`)**:\n"
                f"   - *Cơ chế*: Tráo sang tàu bay Spare tại bãi đỗ khi phát hiện hỏng hóc kỹ thuật MEL.\n"
                f"   - *Hiệu quả*: Tiết kiệm 45-90 phút trễ dây chuyền (Cascading Delays).\n\n"
                f"*Mẹo*: Bạn có thể chọn chuyến bay mẫu (ví dụ `4568`) ở trên rồi bấm vào câu hỏi mô phỏng để nhận con số chi phí thực tế!"
            )

        citations = ["FAA Order JO 7210.3 (Air Traffic Management)", "14 CFR Part 117 (Flight Duty Limits)"]
        suggested = [
            "Mô phỏng kích hoạt tổ bay dự bị Standby Crew",
            "Mô phỏng tăng tốc bay bù giờ trên không",
            "Xem quy định Tarmac Delay 180 phút",
            "Quy trình xử lý sự cố trễ sop_delay_incident",
        ]
        return ChatResponse(
            reply=reply,
            source="offline_knowledge_engine",
            matched_terms=["what_if_simulation", scenario],
            grounding_citations=citations,
            suggested_questions=suggested,
            flight_context=advisory.flight_context.to_dict() if advisory else flight_context,
        )

    # -------------------------------------------------------------------------
    # INTENT 2: General Greeting, Help or Catalog Overview
    # -------------------------------------------------------------------------
    help_keywords = {"chao", "hello", "hi", "help", "tro giup", "catalog", "danh muc", "ban co the", "gioi thieu", "ai vay", "ban la ai"}
    if bool(tokens & help_keywords) or any(k in clean_msg for k in ["xin chao", "chao ban", "ban la ai", "ban co the lam gi", "huong dan"]) or len(message.strip()) <= 4:
        greeting_text = (
            "### ✈️ Xin chào! Tôi là OCC Decision & Knowledge Copilot\n\n"
            "Tôi là Trợ lý AI Điều Hành Bay và Hướng Dẫn Tác Nghiệp được neo chặt vào **3 Tầng Dữ Liệu Thực Tế**:\n"
            "1. 🏢 **Kho Dữ Liệu Khoa Học (Warehouse & Lookups)**: Kết nối dữ liệu chuyến bay, tuyến bay và mật độ sân bay.\n"
            "2. 🤖 **Đấu Trường Máy Học (ML Multi-Model Tournament)**: Đánh giá xác suất trễ, risk band, lift @ 10% và giải thích bằng SHAP.\n"
            "3. ⚖️ **Thẩm Định Pháp Lý & Định Lượng Tài Chính**: Đối soát 14 CFR § 259.4 (Tarmac Delay), FAR Part 117 (FDP Tổ bay), 14 CFR § 260.6 (Hoàn tiền mặt), Thông tư 19/2023/TT-BGTVT và định mức FAA $101.18/phút trễ.\n\n"
            "**Tôi có thể giúp bạn:**\n"
            "- 🔍 **Chẩn đoán chuyến bay cụ thể**: Nhập Flight ID hoặc thông số chặng bay để nhận phân tích pháp lý, căn nguyên trễ và chi phí.\n"
            "- 📚 **Giải thích 40 đề mục tri thức**: 18 chỉ số hàng không, 14 chỉ số ML và 8 quy trình SOP chi tiết.\n"
            "- 🧪 **Mô phỏng What-If**: Đổi giờ bay, kích hoạt Standby Crew, tăng tốc bay bù giờ hoặc tráo tàu bay dự bị kèm tính toán ROI ròng!\n\n"
            "👉 *Hãy chọn một trong các câu hỏi gợi ý bên dưới hoặc gõ trực tiếp câu hỏi của bạn!*"
        )
        return ChatResponse(
            reply=greeting_text,
            source="offline_knowledge_engine",
            matched_terms=["copilot_greeting"],
            grounding_citations=[
                "US DOT 14 CFR § 259.4 (Tarmac Delay)",
                "FAA Title 14 CFR Part 117 (Crew Duty)",
                "FAA/A4A Cost of Delay Metric ($101.18/min)",
            ],
            suggested_questions=DEFAULT_SUGGESTED_QUESTIONS,
        )

    # -------------------------------------------------------------------------
    # FLIGHT QUERY IDENTIFICATION & ROUTING
    # -------------------------------------------------------------------------
    # Check if message mentions a specific flight number or warehouse flight_id (e.g., "chuyến 4568", "flight UA100")
    explicit_flight_m = re.search(r"(?:chuyen(?:\s*bay)?|flight|ma(?:\s*so)?|id)\s*[:#]?\s*([a-zA-Z0-9_-]+)", clean_msg)
    extracted_flight_id: Optional[str] = None
    if explicit_flight_m:
        cand = explicit_flight_m.group(1).strip()
        if cand.isdigit():
            extracted_flight_id = cand
        elif re.match(r"^[a-zA-Z]{2}\d{1,4}$", cand):
            extracted_flight_id = cand

    # Only treat as a flight-specific query if the user explicitly references the flight,
    # mentions a flight ID/number, or asks a contextual question about the currently selected flight.
    flight_explicit_phrases = [
        "chuyen bay nay", "chuyen nay", "flight nay", "chuyen bay cua toi",
        "chuyen do", "chuyen bay do", "chuyen bay hien tai", "chuyen hien tai",
        "chuyen bay ua", "chuyen bay aa", "chuyen bay dl", "chuyen bay wn",
        "chuyen bay da chon", "chuyen dang chon", "ve chuyen bay", "chuyen bay co"
    ]
    has_flight_explicit = any(p in clean_msg for p in flight_explicit_phrases) or (extracted_flight_id is not None)

    flight_context_q_phrases = [
        "tai sao tre", "tai sao lai tre", "nguyen nhan tre", "can nguyen tre",
        "co bi phat khong", "bi phat bao nhieu", "co bi phat tien",
        "thiet hai bao nhieu", "chi phi chuyen nay", "mat bao nhieu tien",
        "to bay co bi time out", "to bay co bi qua gio", "phi cong co bi qua gio",
        "can lam gi bay gio", "ke hoach dieu hanh chuyen", "giai phap cho chuyen",
        "nguy co vi pham luat gi", "vi pham dieu luat gi", "chuyen bay nay co nguy co"
    ]
    has_flight_context_q = (flight_context is not None or advisory is not None) and any(p in clean_msg for p in flight_context_q_phrases)

    is_flight_intent = has_flight_explicit or has_flight_context_q

    # If flight ID was extracted from message and we don't have advisory yet, look it up now
    if is_flight_intent and advisory is None and extracted_flight_id is not None:
        try:
            advisory = lookup_flight_advisory(extracted_flight_id)
            if advisory:
                flight_context = advisory.flight_context.to_dict()
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # INTENT 3: Data Analyst Specialized Q&A (Power BI Pages, RCA, DAX & FAA Costs)
    # -------------------------------------------------------------------------
    if not is_flight_intent:
        # Check specific Power BI Page first
        is_pbi_page_4 = any(k in clean_msg for k in ["trang 4", "trang so 4", "trang bon", "page 4", "pbi trang 4", "trang cuoi"])
        is_pbi_page_1 = any(k in clean_msg for k in ["trang 1", "trang so 1", "trang mot", "page 1", "pbi trang 1", "trang dau"])
        is_pbi_page_2 = any(k in clean_msg for k in ["trang 2", "trang so 2", "trang hai", "page 2", "pbi trang 2"])
        is_pbi_page_3 = any(k in clean_msg for k in ["trang 3", "trang so 3", "trang ba", "page 3", "pbi trang 3"])

        # 3A.4: Power BI Page 4 Visual Breakdown (AI Predictive Risk & Regulatory Governance)
        if is_pbi_page_4 and any(k in clean_msg for k in ["bieu do", "visual", "giai thich", "cac bieu do", "y nghia", "trang 4", "page 4", "chi so"]):
            reply = (
                "### 📊 Phân Tích Chi Tiết Các Biểu Đồ Trên Trang 4 Power BI: AI Predictive Risk & Regulatory Governance\n\n"
                "Trang 4 là **đỉnh cao Prescriptive & Governance** trong hệ thống báo cáo Power BI, tích hợp trực tiếp kết quả từ "
                "Đấu trường Đa mô hình Machine Learning và Động cơ Pháp lý Hàng không. Dưới đây là bóc tách chuyên sâu từng biểu đồ (Visuals) trên canvas:\n\n"
                "#### 1️⃣ Dải Thẻ Đo Lường Điều Hành (Executive KPI Cards - Top Row)\n"
                "- **Card 1: High Risk Flights (`[High Risk Flights (AI Alert)]`)**:\n"
                "  - *Con số*: **19.333 chuyến bay (33.0%)** rơi vào vùng nguy cơ trễ nghiêm trọng do AI phát hiện (`p ≥ 0.290`).\n"
                "  - *Ý nghĩa DA*: Đây là tập hợp chuyến bay cần ưu tiên cảnh báo sớm và can thiệp trước giờ cất cánh.\n"
                "- **Card 2: Tarmac Delay Violations Risk (`[Tarmac Delay Risk Count (14 CFR § 259.4)]`)**:\n"
                "  - *Con số*: **11.260 chuyến bay** xuất phát từ các Mega Hub đông đúc vào giờ cao điểm, có nguy cơ kẹt quá 180 phút trên đường lăn.\n"
                "- **Card 3: Potential DOT Penalty Exposure (`[Potential DOT Penalty Exposure ($)]`)**:\n"
                "  - *Con số*: **$75.76 Tỷ USD** phơi nhiễm chế tài tài chính tối đa theo khung xử phạt của Bộ GTVT Hoa Kỳ ($37,377 USD/khách × 180 khách/chuyến).\n"
                "  - *Màu sắc điều kiện*: Tự động chuyển sang đỏ rực `#E74C3C` khi vượt ngưỡng phơi nhiễm rủi ro.\n"
                "- **Card 4: Champion Model Performance**:\n"
                "  - *Con số*: Hiển thị mô hình chiến thắng **LightGBM** với **Test AUC = 0.748** và **Test Lift @ 10% = 2.45x**.\n\n"
                "#### 2️⃣ Biểu Đồ 1: Đấu Trường Đa Mô Hình (Model Tournament - Clustered Column & Line Chart)\n"
                "- **Trục X**: 5 thuật toán máy học tham gia thi đấu (`Logistic Regression Baseline`, `LightGBM`, `CatBoost`, `XGBoost`, `Soft-Voting Ensemble`).\n"
                "- **Trục Cột Y (Columns)**: `test_auc` — Thước đo khả năng phân loại tổng quát trên tập kiểm thử độc lập theo chuỗi thời gian (Temporal Holdout).\n"
                "- **Trục Đường Y (Line)**: `test_lift_top10pct` — Hiệu quả gom nhóm trễ (Mô hình gom trúng số chuyến trễ gấp bao nhiêu lần so với chọn ngẫu nhiên trong Top 10% rủi ro cao nhất).\n"
                "- **Insight Quản Trị**: Minh bạch hóa lý do ban điều hành lựa chọn LightGBM làm mô hình chính thức: Vượt trội hoàn toàn Baseline (AUC 0.748 vs 0.620, Lift 2.45x) và giải quyết trọn vẹn mối quan hệ phi tuyến giữa mật độ sân bay và trễ dây chuyền.\n\n"
                "#### 3️⃣ Biểu Đồ 2: Phân Bổ Rủi Ro Chế Tài Theo Hãng Bay (100% Stacked Bar Chart)\n"
                "- **Trục Y**: Danh sách 10 hãng hàng không (AA, DL, UA, WN, B6, NK,...).\n"
                "- **Trục X (100%)**: Phân bổ tỷ lệ 5 nhóm chế tài luật định:\n"
                "  - 🟥 **14 CFR § 259.4 (Tarmac Delay)**: Chiếm tỷ trọng áp đảo ở các hãng truyền thống (American, Delta, United) do mạng bay Hub-and-Spoke dồn chuyến.\n"
                "  - 🟧 **14 CFR § 260.6 (Nghĩa vụ hoàn tiền mặt 100%)**: Rủi ro cao nhất ở các hãng giá rẻ (Southwest, Spirit, JetBlue) do mô hình Point-to-Point quay đầu nhanh dễ bùng nổ trễ ≥ 3 tiếng.\n"
                "  - 🟨 **FAR Part 117 (Crew Duty Time-out)**: Tập trung vào các chặng bay muộn sau 18:00.\n"
                "  - 🟦 **14 CFR § 259.5 (Bảo vệ khách lỡ nối chuyến)** & **14 CFR § 234.11 (Tuyến trễ kinh niên)**.\n\n"
                "#### 4️⃣ Biểu Đồ 3: Ma Trận Điểm Nghẽn Siêu Hub & Rủi Ro Tarmac (Hub Congestion & Tarmac Risk Scatter/Heatmap)\n"
                "- **Trục X**: Giờ khởi hành trong ngày (`dep_hour` từ 0:00 đến 23:00).\n"
                "- **Trục Y**: Xác suất trễ AI (`delay_probability` từ 0% đến 100%).\n"
                "- **Kích thước bong bóng (Size)**: Mức phạt tài chính tối đa USD (`max_penalty_exposure_usd`).\n"
                "- **Màu sắc bong bóng**: Sân bay xuất phát (lọc 4 Mega Hub: DFW, ORD, ATL, DEN).\n"
                "- **Insight Cốt Lõi**: Khung giờ **17:00 - 20:00** tại DFW và ORD hình thành cụm bong bóng khổng lồ — Đây là \"tâm chấn\" tập trung hơn 70% nguy cơ phạt Tarmac của toàn mạng lưới bay.\n\n"
                "#### 5️⃣ Biểu Đồ 4: Bảng Tác Nghiệp Thời Gian Thực Cho Điều Phái Bay (OCC Live Dispatcher Action Matrix - Table)\n"
                "- **Các trường hiển thị**: Số hiệu chuyến, Tuyến bay, Giờ bay, Xác suất trễ AI (Data bars), Phân nhóm rủi ro (Risk Band màu Đỏ/Cam/Xanh), Căn cứ điều luật, Số tiền phạt tiềm tàng USD, và **Mệnh lệnh hành động bắt buộc của OCC** (Ví dụ: `GATE HOLD: Giữ máy bay tại cửa, cấm đẩy lùi khi chưa có khe ATC`).\n"
                "- **Tương tác 1 chạm**: Điều phái viên hoặc DA có thể copy Flight ID sang Copilot để chạy mô phỏng What-If (đổi giờ bay, gọi Standby Crew) để triệt tiêu nguy cơ vi phạm ngay lập tức!"
            )
            return ChatResponse(
                reply=reply,
                source="offline_knowledge_engine",
                matched_terms=["power_bi_page_4", "visual_breakdown", "regulatory_governance"],
                grounding_citations=[
                    "Power BI Page 4 Design Specification (PAGE_4_DESIGN.md)",
                    "US DOT 14 CFR § 259.4 (Tarmac Delay Rule)",
                    "FAA Title 14 CFR Part 117 (Flight Duty Period)",
                    "US DOT 14 CFR § 260.6 (Mandatory Cash Refunds)",
                ],
                suggested_questions=[
                    "Giải thích biểu đồ Đấu Trường Mô Hình (AUC, Lift @ 10%) trên Trang 4.",
                    "Tại sao Hãng Legacy bị rủi ro Tarmac Delay cao hơn Hãng Giá Rẻ (LCC)?",
                    "Ý nghĩa các chỉ số trên 4 trang Power BI Dashboard là gì?",
                    "Giải thích công thức DAX tính Chi Phí Trễ và định mức FAA $101.18/phút.",
                ],
            )

        # 3A.1: Power BI Page 1 Visual Breakdown (Executive Operations Overview)
        if is_pbi_page_1 and any(k in clean_msg for k in ["bieu do", "visual", "giai thich", "cac bieu do", "y nghia", "trang 1", "page 1", "chi so"]):
            reply = (
                "### 📊 Phân Tích Chi Tiết Các Biểu Đồ Trên Trang 1 Power BI: Executive Operations Overview\n\n"
                "Trang 1 là **bước Descriptive (Mô tả hiện trạng)**, cung cấp cái nhìn toàn cảnh về năng lực khai thác và tỷ lệ đúng giờ của toàn mạng lưới 58.588 chuyến bay:\n\n"
                "#### 1️⃣ Dải Thẻ Đo Lường KPI Vận Hành (Executive KPI Cards - Top Row)\n"
                "- **Card 1: Total Flights (`[Total Flights]`)**: 58.588 chuyến bay thương mại hoàn tất trong kỳ phân tích.\n"
                "- **Card 2: OTP % A14 Standard (`[OTP % (A14)]`)**: Đạt **75.4% - 78.2%** (đến trễ < 15 phút theo chuẩn US DOT).\n"
                "- **Card 3: Cancellation Rate (`[Cancellation %]`)**: Giữ ở mức **~1.8%**, chủ yếu do thời tiết cực đoan.\n"
                "- **Card 4: Avg Arrival Delay (`[Avg Arrival Delay]`)**: Dao động **7.5 - 8.8 phút/chuyến** trên toàn mạng lưới.\n"
                "- **Card 5: Total Direct Delay Cost (`[Total Direct Delay Cost (USD)]`)**: Tổng thiệt hại tài chính theo định mức FAA $101.18/phút.\n\n"
                "#### 2️⃣ Biểu Đồ 1: Xu Hướng OTP & Lưu Lượng Chuyến Bay Theo Ngày (Line & Clustered Column Chart)\n"
                "- **Trục X**: Ngày trong tháng (`flight_date`).\n"
                "- **Cột (Column)**: Tổng sản lượng chuyến bay khai thác mỗi ngày.\n"
                "- **Đường (Line)**: Tỷ lệ đúng giờ `OTP %` đối chiếu đường mục tiêu chuẩn (Target Reference Line 80%).\n"
                "- **Insight**: Giúp DA nhận diện ngay các ngày có sụt giảm OTP đột biến để bóc tách yếu tố thời tiết giông bão trên diện rộng.\n\n"
                "#### 3️⃣ Biểu Đồ 2: Xếp Hạng & So Sánh Đúng Giờ Giữa Các Hãng Bay (Bar Chart - Carrier Performance)\n"
                "- **Trục Y**: Danh sách 10 Hãng hàng không.\n"
                "- **Trục X**: Tỷ lệ `OTP % (A14)`.\n"
                "- **Insight**: Phân nhóm rõ rệt giữa Hãng hàng không truyền thống (Legacy) và Hãng hàng không giá rẻ (LCC), cho thấy Delta (DL) và United (UA) duy trì OTP ổn định hơn nhờ đệm lịch trình tốt.\n\n"
                "#### 4️⃣ Biểu Đồ 3: Tương Quan Trễ Khởi Hành vs Trễ Đến (Scatter Chart: Departure vs Arrival Delay)\n"
                "- **Trục X**: `Avg Dep Delay` (Số phút trễ cất cánh) | **Trục Y**: `Avg Arr Delay` (Số phút trễ hạ cánh).\n"
                "- **Đường chéo 45 độ**: Phân định ranh giới bù giờ (Airborne Make-up): Các chuyến bay nằm dưới đường 45 độ đã thành công thu hồi thời gian bay trên không!"
            )
            return ChatResponse(
                reply=reply,
                source="offline_knowledge_engine",
                matched_terms=["power_bi_page_1", "visual_breakdown", "executive_overview"],
                grounding_citations=[
                    "US DOT BTS Air Travel Consumer Report",
                    "FAA A14 On-Time Standard (14 CFR Part 234)",
                    "Power BI Operations Dashboard Architecture",
                ],
                suggested_questions=[
                    "Giải thích các biểu đồ trên Trang số 2 (Root Cause & Cascading Delays).",
                    "Giải thích các biểu đồ trên Trang số 4 (AI Predictive Risk & Governance).",
                    "Giải thích công thức DAX tính Chi Phí Trễ và định mức FAA $101.18/phút.",
                ],
            )

        # 3A.2: Power BI Page 2 Visual Breakdown (Delay Root-Cause & Cascading Analysis)
        if is_pbi_page_2 and any(k in clean_msg for k in ["bieu do", "visual", "giai thich", "cac bieu do", "y nghia", "trang 2", "page 2", "chi so"]):
            reply = (
                "### 📊 Phân Tích Chi Tiết Các Biểu Đồ Trên Trang 2 Power BI: Delay Root-Cause & Cascading Analysis\n\n"
                "Trang 2 là **bước Diagnostic (Chẩn đoán nguyên nhân)**, đi sâu trả lời câu hỏi: *Tại sao các chuyến bay lại bị chậm trễ?*:\n\n"
                "#### 1️⃣ Biểu Đồ 1: Cơ Cấu 5 Nhóm Nguyên Nhân Trễ Chuẩn BTS (Donut / Treemap / Stacked Bar)\n"
                "- **Phân bổ theo chuẩn 14 CFR Part 234 Subpart B**:\n"
                "  - 🟣 **Late Aircraft Delay**: Chiếm tới **~39.8%** — Nguyên nhân lớn nhất của toàn hệ thống!\n"
                "  - 🔵 **Carrier Delay (Hãng bay)**: Chiếm ~25-28% — Vấn đề bảo dưỡng kỹ thuật, khách lên chậm, thiếu tổ bay.\n"
                "  - 🟢 **National Aviation System (NAS)**: Chiếm ~20-24% — Quá tải kiểm soát không lưu FAA, tắc nghẽn đường băng.\n"
                "  - 🟡 **Weather Delay**: Chiếm ~6-8% — Bão tuyết, giông lốc nghiêm trọng.\n"
                "  - ⚪ **Security Delay**: Chiếm < 0.5% — Sự cố an ninh soi chiếu.\n\n"
                "#### 2️⃣ Biểu Đồ 2: Bóc Tách Hiệu Ứng Domino Trễ Dây Chuyền (Waterfall / Cascading Progression)\n"
                "- **Mô hình chuỗi chặng bay**: Theo dõi 1 máy bay qua 5-6 chặng trong ngày.\n"
                "- **Insight Cốt Lõi**: Một chuyến bay trễ 25 phút lúc 08:00 sáng tại chặng 1 sẽ không thể tiêu hóa hết trong 35 phút quay đầu tại bãi đỗ. "
                "Đến 17:00 chiều tại chặng 5, độ trễ tích lũy bùng phát thành 95 phút, đe dọa trực tiếp trần giờ bay của tổ bay (FAR Part 117).\n\n"
                "#### 3️⃣ Biểu Đồ 3: Tỷ Trọng Trễ Lan Truyền Theo Hãng Bay (Cascading Delay Ratio Bar Chart)\n"
                "- **Measure**: `[Cascading Delay Ratio] = Late Aircraft Minutes / Total Delay Minutes`.\n"
                "- **Insight**: Phơi bày sự tổn thương sâu sắc của các hãng khai thác tần suất cao (High Aircraft Utilization) khi không có máy bay dự bị (Spare Aircraft) cắm chốt tại các trạm trung tâm."
            )
            return ChatResponse(
                reply=reply,
                source="offline_knowledge_engine",
                matched_terms=["power_bi_page_2", "visual_breakdown", "root_cause_analysis"],
                grounding_citations=[
                    "US DOT 14 CFR Part 234.4 (Reporting of Delay Causes)",
                    "FAA System Operations Delay Analysis",
                ],
                suggested_questions=[
                    "Tại sao nguyên nhân Late Aircraft chiếm tới gần 40% tổng số phút trễ?",
                    "Giải thích các biểu đồ trên Trang số 3 (Hub Bottlenecks).",
                    "Giải thích các biểu đồ trên Trang số 4 (AI Predictive Risk & Governance).",
                ],
            )

        # 3A.3: Power BI Page 3 Visual Breakdown (Hub Bottlenecks & Route Performance)
        if is_pbi_page_3 and any(k in clean_msg for k in ["bieu do", "visual", "giai thich", "cac bieu do", "y nghia", "trang 3", "page 3", "chi so"]):
            reply = (
                "### 📊 Phân Tích Chi Tiết Các Biểu Đồ Trên Trang 3 Power BI: Hub Bottlenecks & Route Performance\n\n"
                "Trang 3 là **bước Diagnostic Deep-dive (Khoanh vùng không gian)**, xác định chính xác các điểm nghẽn vật lý trong mạng đường bay:\n\n"
                "#### 1️⃣ Biểu Đồ 1: Mật Độ Chuyến Bay & Thời Gian Lăn Bánh Taxi-Out Theo Khung Giờ (Area / Line Chart)\n"
                "- **Trục X**: Khung giờ trong ngày (0:00 - 23:00).\n"
                "- **Trục Y1**: Sản lượng cất cánh theo giờ (`Departure Hourly Volume`).\n"
                "- **Trục Y2**: Thời gian lăn ra đường băng (`Avg Taxi-Out Minutes`).\n"
                "- **Insight**: Chỉ rõ hiện tượng tắc nghẽn nghiêm trọng tại các Mega Hub (DFW, ORD, ATL, DEN) từ **16:00 đến 20:00**, khi thời gian lăn vọt từ mức bình thường 15 phút lên tới **35 - 48 phút/chuyến**.\n\n"
                "#### 2️⃣ Biểu Đồ 2: Ma Trận Tuyến Bay Chiến Lược (Route Performance Bubble Scatter Chart)\n"
                "- **Trục X**: Sản lượng chuyến bay trên tuyến (`Flight Volume`).\n"
                "- **Trục Y**: Số phút trễ đến trung bình (`Avg Arrival Delay`).\n"
                "- **Kích thước bong bóng**: Tỷ lệ hủy chuyến (`Cancellation %`).\n"
                "- **Insight**: Phân nhóm 4 góc phần tư: Tuyến huyết mạch ổn định vs Tuyến rủi ro cao (High-volume & High-delay) cần lập phương án ứng phó khẩn cấp.\n\n"
                "#### 3️⃣ Biểu Đồ 3: Khả Năng Bay Bù Giờ Trên Không (Airborne Make-up Time Matrix)\n"
                "- **Phân loại**: Tuyến ngắn (< 500 dặm), Tuyến trung bình (500 - 1000 dặm), Tuyến dài (> 1000 dặm).\n"
                "- **Insight**: Tuyến dài có khả năng hấp thụ và bù lại 10-15 phút trễ nhờ đệm lịch trình (Schedule Padding) và điều chỉnh Cost Index, trong khi các chặng ngắn hoàn toàn bất lực trước trễ khởi hành."
            )
            return ChatResponse(
                reply=reply,
                source="offline_knowledge_engine",
                matched_terms=["power_bi_page_3", "visual_breakdown", "hub_bottlenecks"],
                grounding_citations=[
                    "FAA Order JO 7210.3 (Air Traffic Facility Management)",
                    "US DOT BTS Route Performance Database",
                ],
                suggested_questions=[
                    "Tại sao Hub DFW và ORD thường xuyên bị nghẽn nặng vào khung giờ tối?",
                    "Giải thích các biểu đồ trên Trang số 4 (AI Predictive Risk & Governance).",
                    "Làm thế nào để đổi giờ bay né cao điểm (What-If)?",
                ],
            )

        # 3A.0: General 4-Page Power BI Dashboard Explanation (Overall architecture)
        if any(k in clean_msg for k in ["4 trang", "power bi", "powerbi", "dashboard", "y nghia cac chi so", "bao cao power bi"]):
            reply = (
                "### 📊 Phân Tích & Ý Nghĩa Các Chỉ Số Trên 4 Trang Power BI Dashboard\n\n"
                "Báo cáo Power BI của nền tảng được thiết kế theo cấu trúc dẫn chuyện chuẩn **Gartner Analytics Maturity** "
                "(từ Mô tả Descriptive đến Dự báo Predictive & Đề xuất Prescriptive Governance):\n\n"
                "#### 1️⃣ Trang 1: Tổng Quan Khai Thác Vận Hành (Executive Operations Overview)\n"
                "- **Quy mô giám sát**: `58.588 chuyến bay` thương mại qua 40 sân bay trọng điểm và 10 hãng hàng không.\n"
                "- **Tỷ lệ đúng giờ (OTP % - A14 Standard)**: Đạt `75.4% - 78.2%` theo chuẩn US DOT (đến trễ < 15 phút được tính là đúng giờ).\n"
                "- **Tỷ lệ hủy chuyến (Cancellation Rate)**: Giữ ở mức an toàn `~1.8%`, chủ yếu do yếu tố thời tiết cực đoan (Weather).\n"
                "- **Trễ đến trung bình (Avg Arrival Delay)**: Dao động `7.5 - 8.8 phút/chuyến` trên toàn mạng lưới.\n"
                "- **Bảng xếp hạng Hãng bay**: So sánh On-Time % giữa nhóm Legacy (Delta, United, American) và Low-Cost (Southwest, JetBlue, Spirit).\n\n"
                "#### 2️⃣ Trang 2: Phân Tích Nguyên Nhân Gốc Rễ & Hiệu Ứng Dây Chuyền (Delay Root-Cause & Cascading Analysis)\n"
                "- **5 Nhóm nguyên nhân chuẩn BTS (14 CFR Part 234)**: Carrier, Weather, National Aviation System (NAS), Security, Late Aircraft.\n"
                "- **Insight Đắt Giá**: Nguyên nhân **Máy bay đến trễ (Late Aircraft Delay)** chiếm tới **~39.8% tổng số phút trễ**! "
                "Đây là hiệu ứng domino dây chuyền: một chuyến bay chậm ở chặng đầu sẽ kéo theo trễ tích lũy ở 4-6 chặng tiếp theo trong ngày.\n"
                "- **Chỉ số Cascading Ratio**: Đo lường mức độ tổn thương do trễ lan truyền của từng đội bay.\n\n"
                "#### 3️⃣ Trang 3: Điểm Nghẽn Siêu Trung Tâm & Hiệu Suất Tuyến Bay (Hub Bottlenecks & Route Performance)\n"
                "- **Điểm nghẽn Mega Hubs**: Các sân bay DFW, ORD, ATL, DEN tập trung lượng trễ cao nhất, đặc biệt nghẽn nghiêm trọng vào khung giờ chiều tối **16:00 - 20:00**.\n"
                "- **Thời gian lăn bánh (Taxi-Out Duration)**: Tăng vọt từ 15 phút lên 35-48 phút trong giờ cao điểm do tắc nghẽn đường lăn.\n"
                "- **Bong bóng Tuyến bay**: Phân tích tương quan Lưu lượng bay vs Độ trễ vs Tỷ lệ hủy.\n"
                "- **Khả năng bay bù giờ (Airborne Make-up Time)**: Các chặng bay đường dài (>1,000 dặm) có khả năng hấp thụ và bù lại 10-15 phút trễ nhờ đệm lịch trình (Padding).\n\n"
                "#### 4️⃣ Trang 4: Dự Báo Rủi Ro AI & Quản Trị Pháp Chế Hàng Không (AI Predictive Risk & Regulatory Governance)\n"
                "- **Đấu trường 5 Mô hình ML (Tournament)**: So sánh LightGBM (chiến thắng với AUC 0.748, Lift @ 10% đạt 2.45x, Brier Score 0.176), CatBoost, XGBoost, Baseline LogReg và Ensemble.\n"
                "- **Phân tầng 3 Dải Rủi Ro (Risk Bands)**: High Risk (33.0% - p ≥ 0.290), Elevated Risk (37.4% - 0.285 ≤ p < 0.290), Normal Safe (29.6% - p < 0.285).\n"
                "- **Đối chiếu Chế tài Luật định**: Tự động bóc tách điều luật **14 CFR § 259.4** (Tarmac Delay), **FAR Part 117** (FDP Phi công), **14 CFR § 260.6** (Hoàn tiền mặt 100%), **14 CFR § 259.5** (Bảo vệ khách nối chuyến).\n"
                "- **Định lượng Tài chính & Mệnh lệnh OCC**: Tính toán phơi nhiễm tiền phạt (USD) và đề xuất can thiệp kịp thời triệt tiêu rủi ro.\n\n"
                "💡 *Mẹo*: Bạn có thể hỏi cụ thể từng trang (ví dụ: *'giải thích các biểu đồ trên trang số 4'* hoặc *'trang 3 có những biểu đồ nào'*) để nhận bóc tách chi tiết từng visual!"
            )
            return ChatResponse(
                reply=reply,
                source="offline_knowledge_engine",
                matched_terms=["power_bi_4_pages", "dashboard_overview"],
                grounding_citations=[
                    "Power BI Operations Dashboard (4 Pages Architecture)",
                    "US DOT 14 CFR Part 234 (Service Quality Reports)",
                    "FAA Order JO 7210.3 (Facility Operation and Administration)",
                ],
                suggested_questions=[
                    "Giải thích các biểu đồ trên trang số 4 Power BI Dashboard.",
                    "Tại sao Hub DFW và ORD thường xuyên bị nghẽn nặng vào khung giờ tối?",
                    "Giải thích công thức DAX tính Chi Phí Trễ và định mức FAA $101.18/phút.",
                    "Tại sao nguyên nhân Late Aircraft chiếm tới gần 40% tổng số phút trễ?",
                ],
            )

        # 3B: Root Cause Analysis (Hub DFW, Hub ORD, Cascading Delays)
        if any(k in clean_msg for k in ["root cause", "rca", "nguyen nhan goc re", "tai sao hub", "hub dfw", "tai sao dfw", "hub ord", "tai sao ord", "tai sao chang", "tai sao hay tre", "domino", "cascading"]):
            if any(h in clean_msg for h in ["dfw", "dallas"]):
                reply = (
                    "### 🔍 Root Cause Analysis (RCA): Tại Sao Siêu Hub DFW Thường Xuyên Bị Nghẽn Nặng?\n\n"
                    "Dựa trên dữ liệu khai thác 58.588 chuyến bay và cấu trúc hạ tầng tại **Dallas/Fort Worth International Airport (DFW)**, "
                    "nguyên nhân gốc rễ bao gồm 4 yếu tố then chốt:\n\n"
                    "1. **🏦 Cấu Trúc Sóng Kết Nối (Banked Hub Structure)**:\n"
                    "   - DFW là đại bản doanh lớn nhất của American Airlines (AA), khai thác theo mô hình sóng dồn chuyến (De-peaked/Complex Waves).\n"
                    "   - Trong mỗi đợt sóng (khoảng 90 phút), hơn 60-80 máy bay cùng hạ cánh dồn dập, giải tỏa khách nối chuyến và cùng khởi hành đồng thời. "
                    "Khi số chuyến vượt quá giới hạn tiếp nhận mặt đất (Acceptance Rate), hiện tượng dồn toa lập tức xuất hiện.\n\n"
                    "2. **🛬 Nghẽn Đường Lăn Taxi-Out Trong Khung Giờ Cao Điểm (16:00 - 20:00)**:\n"
                    "   - Dữ liệu cho thấy thời gian lăn cất cánh (Taxi-Out) tại DFW nhảy vọt từ mức bình thường `15-17 phút` lên tới `35-48 phút` vào giờ cao điểm chiều tối.\n"
                    "   - Máy bay xếp hàng dài chờ cất cánh làm tiêu hao nhiên liệu vô ích và trực tiếp kích hoạt nguy cơ vi phạm trần **Tarmac Delay 14 CFR § 259.4** (phạt tới $37,377 USD/pax).\n\n"
                    "3. **⚡ Tác Động Thời Tiết Giông Lốc Vi Mô (Convective Thunderstorms)**:\n"
                    "   - Khu vực Bắc Texas thường xuyên xuất hiện giông nhiệt mùa hè/thu. Dù giông lốc chỉ diễn ra 30-45 phút tại một góc sân bay, "
                    "FAA bắt buộc phải giãn cách đường bay hoặc áp dụng Ground Stop, khiến toàn bộ lịch bay bị đình trệ.\n\n"
                    "4. **🌪️ Hiệu Ứng Domino Dây Chuyền (Cascading Multiplier)**:\n"
                    "   - Vì DFW là trạm trung chuyển huyết mạch, 1 tàu bay bị trễ 45 phút tại DFW sẽ khiến phi hành đoàn bị chạm trần giờ bay FDP (FAR Part 117), "
                    "làm vỡ lịch của ít nhất 3-5 chặng bay kế tiếp trong ngày.\n\n"
                    "💡 **Khuyến nghị cho DA đưa vào Slide**: Đề xuất OCC áp dụng lệnh **Gate Hold** giữ máy bay tại cửa thay vì đẩy lùi sớm, "
                    "và giãn cách lịch bay 15-20 phút giữa các đợt sóng cao điểm."
                )
            elif any(h in clean_msg for h in ["ord", "chicago"]):
                reply = (
                    "### 🔍 Root Cause Analysis (RCA): Tại Sao Hub Chicago O'Hare (ORD) Bị Tắc Nghẽn?\n\n"
                    "Căn nguyên cốt lõi khiến **Chicago O'Hare (ORD)** là một trong những điểm nóng trễ chuyến lớn nhất nước Mỹ:\n\n"
                    "1. **⚔️ Siêu Hub Tranh Chấp Kép (Dual-Hub Competition)**:\n"
                    "   - Cả United Airlines (UA) và American Airlines (AA) đều chọn ORD làm Mega Hub chiến lược. Cạnh tranh slot bay gay gắt khiến mật độ cất hạ cánh luôn hoạt động ở mức 95-100% công suất thiết kế.\n\n"
                    "2. **❄️ Yếu Tố Khí Hậu Hồ Michigan & Phun Chống Đông (De-icing Operations)**:\n"
                    "   - Mùa đông tuyết rơi và băng giá buộc 100% chuyến bay phải qua bãi phun dung dịch làm tan băng (De-icing pad), làm tăng thêm `20-40 phút/chuyến` trước khi cất cánh.\n"
                    "   - Mùa hè chịu ảnh hưởng bởi gió chéo mạnh từ hồ Michigan làm giảm năng lực sử dụng đường băng.\n\n"
                    "3. **🛑 Can Thiệp Kiểm Soát Không Lưu FAA NAS (Ground Delay Programs - GDP)**:\n"
                    "   - Khi không phận Chicago quá tải, FAA thường xuyên áp dụng lệnh giữ chỗ bay từ xa (EDCT - Expect Departure Clearance Time), buộc các chuyến bay từ sân bay khác bay đến ORD phải hoãn giờ cất cánh tại sân bay xuất phát."
                )
            else:
                reply = (
                    "### 🔍 Root Cause Analysis (RCA): Căn Nguyên Của Hiệu Ứng Trễ Dây Chuyền (Cascading Delays ~40%)\n\n"
                    "Trên Power BI Dashboard Trang 2, chỉ số **Late Aircraft Delay** chiếm tới gần **40% tổng số phút trễ**. "
                    "Đây là nguyên nhân gốc rễ chi phối toàn bộ hệ thống vận hành hàng không:\n\n"
                    "1. **Mô Hình Khai Thác Xoay Vòng Tàu Bay Tối Đa (High Aircraft Utilization)**:\n"
                    "   - Mỗi tàu bay thân hẹp (A320/B737) được lập lịch bay từ `5 đến 7 chặng/ngày` nhằm tối đa hóa doanh thu và hoàn vốn đầu tư.\n"
                    "   - Thời gian xoay đầu tại bãi đỗ (Turnaround time) chỉ được tính toán tối thiểu `35 - 45 phút` (đối với Legacy) và `25 - 30 phút` (đối với LCC).\n\n"
                    "2. **Cơ Chế Lan Truyền Domino Không Có Đệm Hấp Thụ**:\n"
                    "   - Nếu Chặng 1 buổi sáng bị trễ 30 phút (do thời tiết hoặc khách lên chậm), thời gian xoay đầu không thể hấp thụ hết 30 phút này.\n"
                    "   - Số phút trễ sẽ được chuyển tiếp sang Chặng 2, tích lũy thêm tắc nghẽn giờ trưa tại chặng 3, và bùng nổ thành trễ 90-120 phút vào buổi chiều tối ở chặng 5-6.\n\n"
                    "3. **Rào Cản Giờ Làm Việc Tổ Bay (FAR Part 117 Crew Duty Time-Out)**:\n"
                    "   - Khi trễ dây chuyền kéo dài đến chặng cuối buổi tối, phi công và tiếp viên chạm trần FDP (Flight Duty Period). "
                    "Chuyến bay không thể cất cánh dù máy bay hoàn toàn bình thường, dẫn tới hủy chuyến hoặc chờ tổ bay dự bị (Standby Crew).\n\n"
                    "💡 **Giải pháp chiến lược cho DA đề xuất trong báo cáo**:\n"
                    "- Bổ sung **15-20 phút đệm lịch trình (Schedule Padding)** vào các chặng bay buổi chiều qua các Mega Hub.\n"
                    "- Bố trí tổ bay dự bị **Hot Standby Crew** trực sẵn tại các trạm trung tâm DFW, ORD, ATL."
                )
            return ChatResponse(
                reply=reply,
                source="offline_knowledge_engine",
                matched_terms=["root_cause_analysis", "hub_bottlenecks"],
                grounding_citations=[
                    "FAA ATO System Operations Delay Analysis",
                    "US DOT BTS Form 41 Schedule P-5.2",
                    "14 CFR Part 234 Subpart B (Delay Causes)",
                ],
                suggested_questions=[
                    "Giải thích công thức DAX tính Chi Phí Trễ và định mức FAA $101.18/phút.",
                    "Ý nghĩa các chỉ số trên 4 trang Power BI Dashboard là gì?",
                    "Làm thế nào để đổi giờ bay né cao điểm (What-If)?",
                    "Quy tắc Tarmac Delay 180 phút của US DOT phạt bao nhiêu USD?",
                ],
            )

        # 3C: DAX Formulas & FAA Cost Benchmark ($101.18/min)
        if any(k in clean_msg for k in ["cong thuc dax", "dax", "measures", "101.18", "dinh muc faa", "chi phi faa", "dinh muc chi phi", "giai thich dax", "chi phi tre"]):
            reply = (
                "### 💵 Giải Thích Công Thức DAX & Định Mức Chi Phí Trễ Hàng Không FAA ($101.18/phút)\n\n"
                "Tài liệu tham chiếu chuẩn nghiệp vụ dành cho Data Analyst về hệ thống tính toán tài chính và mô hình DAX trong file `dashboards/powerbi/measures.dax`:\n\n"
                "#### 1️⃣ Định Mức Chi Phí Trễ FAA & A4A ($101.18 USD / Phút Bay)\n"
                "Theo nghiên cứu liên ngành của Cục Hàng không Liên bang Hoa Kỳ (FAA) và Hiệp hội Các hãng hàng không Hoa Kỳ (Airlines for America - A4A), "
                "chi phí trễ trực tiếp trung bình của một tàu bay thương mại thân hẹp là **$101.18 USD cho mỗi phút chậm trễ**, bao gồm 4 cấu phần định mức:\n"
                "- **⛽ Nhiên liệu tiêu hao thêm (Fuel Burn)**: `~$38.50/phút (38.1%)` — Nhiên liệu Jet A-1 đốt cháy khi động cơ nổ máy chờ trên đường lăn (Taxi-Out) hoặc bay vòng tiếp cận không phận (Holding Pattern).\n"
                "- **👨‍✈️ Chi phí nhân sự & Tổ bay (Crew Overtime)**: `~$32.20/phút (31.8%)` — Phụ cấp làm thêm giờ, chi phí vượt trần FDP theo FAR Part 117 và chi phí lưu trú khách sạn phát sinh.\n"
                "- **🏢 Dịch vụ mặt đất & Cửa đón khách (Ground Handling & Gate)**: `~$17.10/phút (16.9%)` — Phí giữ cửa quá giờ, nhân công bốc dỡ hành lý, xe đẩy tàu bay và dịch vụ cầu lồng (Jet bridge).\n"
                "- **🛠️ Khấu hao & Bảo dưỡng tàu bay (Aircraft Maintenance)**: `~$13.38/phút (13.2%)` — Khấu hao phụ tùng động cơ và chu kỳ cất hạ cánh theo số giờ hoạt động lũy kế.\n\n"
                "#### 2️⃣ Các Công Thức DAX Cốt Lõi Trên Power BI Dashboard\n\n"
                "##### 🔹 Công thức tính Chi Phí Trễ Trực Tiếp (Total Direct Delay Cost):\n"
                "```dax\n"
                "[Total Direct Delay Cost (USD)] = \n"
                "[Total Delay Minutes] * 101.18\n"
                "```\n"
                "- *Ý nghĩa*: Quy đổi toàn bộ tổng số phút trễ của các chuyến bay hoàn thành thành tổn thất tài chính tiền mặt thực tế của hãng bay.\n\n"
                "##### 🔹 Công thức Tỷ lệ Đúng Giờ Chuẩn US DOT (OTP % A14 Standard):\n"
                "```dax\n"
                "[OTP % (A14)] = \n"
                "DIVIDE(\n"
                "    CALCULATE(COUNTROWS(fact_flights), fact_flights[arr_delay_min] < 15, fact_flights[is_cancelled] = 0),\n"
                "    CALCULATE(COUNTROWS(fact_flights), fact_flights[is_cancelled] = 0),\n"
                "    0\n"
                ")\n"
                "```\n"
                "- *Ý nghĩa*: Tính tỷ lệ chuyến bay đến trễ < 15 phút (theo chuẩn A14 của BTS) trên tổng số chuyến bay thực hiện (không tính chuyến hủy).\n\n"
                "##### 🔹 Công thức Tỷ trọng Trễ Dây Chuyền (Cascading Delay Ratio):\n"
                "```dax\n"
                "[Cascading Delay Ratio] = \n"
                "DIVIDE(\n"
                "    SUM(fact_flight_delays[late_aircraft_delay_min]),\n"
                "    SUM(fact_flight_delays[total_delay_min]),\n"
                "    0\n"
                ")\n"
                "```\n"
                "- *Ý nghĩa*: Đo lường tỷ lệ phần trăm số phút trễ xuất phát từ nguyên nhân máy bay đến trễ từ chặng trước (Late Aircraft).\n\n"
                "##### 🔹 Công thức Rủi Ro Tiền Phạt Hành Chính (Potential Penalty Exposure):\n"
                "```dax\n"
                "[Potential Penalty Exposure (USD)] = \n"
                "SUM(fct_flight_regulatory_predictions[max_penalty_exposure_usd])\n"
                "```\n"
                "- *Ý nghĩa*: Tính tổng phơi nhiễm tài chính tối đa nếu các chuyến bay High Risk vi phạm trần Tarmac Delay 14 CFR § 259.4 ($37,377 USD/pax * 180 khách = $6.72M USD/chuyến)."
            )
            return ChatResponse(
                reply=reply,
                source="offline_knowledge_engine",
                matched_terms=["dax_formulas", "cost_of_delay_faa"],
                grounding_citations=[
                    "FAA/A4A Cost of Delay to U.S. Airlines Study ($101.18/min)",
                    "Power BI Semantic Model (dashboards/powerbi/measures.dax)",
                    "US DOT 14 CFR § 259.4 (Civil Penalty Schedule)",
                ],
                suggested_questions=[
                    "Ý nghĩa các chỉ số trên 4 trang Power BI Dashboard là gì?",
                    "Tại sao Hub DFW và ORD thường xuyên bị nghẽn nặng vào khung giờ tối?",
                    "Tại sao nguyên nhân Late Aircraft chiếm tới gần 40% tổng số phút trễ?",
                    "Cách đọc ma trận Đấu Trường Mô Hình (AUC, Lift @ 10%, Brier Score) trên Trang 4?",
                ],
            )

        # ---------------------------------------------------------------------
        # INTENT 4: Standard SOP checklist & Concept/Metric Explanation
        # ---------------------------------------------------------------------
        # Check SOP checklist queries first
        sop_keywords = {"sop", "quy trinh", "checklist", "cac buoc", "thao tac"}
        if bool(tokens & sop_keywords):
            sop_matches = []
            for s_id, s_obj in SOP_CHECKLISTS.items():
                s_text = strip_accents(f"{s_id} {s_obj.title_vi} {s_obj.title_en} {s_obj.purpose}").lower()
                overlap = len(tokens & set(tokenize(s_text)))
                if overlap > 0:
                    sop_matches.append((overlap, s_id, s_obj))

            if sop_matches:
                sop_matches.sort(key=lambda x: x[0], reverse=True)
                chosen_sop = sop_matches[0][2]
                md = format_sop_markdown(chosen_sop.to_dict())
                citations = [f"SOP: {chosen_sop.sop_id}"]
                for st in chosen_sop.steps:
                    if st.regulatory_notice:
                        citations.append(st.regulatory_notice)

                suggested = [
                    "Cho tôi xem quy trình đổi tổ bay sop_crew_timeout_replacement",
                    "Cho tôi xem quy trình hạ cánh sân bay dự bị sop_flight_diversion",
                    "Chế tài phạt Tarmac Delay 14 CFR § 259.4 là bao nhiêu?",
                    "Chi phí trễ chuyến trung bình được tính như thế nào?",
                ]
                return ChatResponse(
                    reply=md,
                    source="offline_knowledge_engine",
                    matched_terms=[chosen_sop.sop_id],
                    grounding_citations=citations[:4],
                    suggested_questions=suggested,
                )

        # Check concept / metric explanation
        res = explain_term(message)
        if res.get("status") in ("exact_match", "search_hit"):
            item = res.get("term") or res.get("best_match")
            term_id = item.get("term_id") or item.get("sop_id")
            matched_terms.append(term_id)

            regs = item.get("related_regulations", [])
            if regs:
                citations.extend(regs)
            if item.get("steps"):
                citations.append(f"SOP: {item.get('sop_id')}")
                for st in item.get("steps", []):
                    rn = st.get("regulatory_notice") if isinstance(st, dict) else getattr(st, "regulatory_notice", None)
                    if rn:
                        citations.append(rn)
            elif item.get("regulatory_notice"):
                citations.append(item.get("regulatory_notice"))

            # Build reply with optional neat flight contextual bridge
            base_reply = res.get("markdown", "")
            if flight_context is not None:
                c_code = flight_context.get("carrier_code", "AA")
                f_num = flight_context.get("flight_number") or ""
                orig = flight_context.get("origin", "ATL")
                dest = flight_context.get("dest", "DFW")
                h = flight_context.get("dep_hour", 17)
                bridge_note = (
                    f"\n\n---\n"
                    f"✈️ **Liên hệ Chuyến Bay Đang Chọn (`{c_code}{f_num}`: {orig} ➔ {dest} lúc {h}:00)**:  \n"
                    f"Bạn có thể hỏi: *\"Chuyến bay này có nguy cơ vi phạm luật gì?\"* hoặc *\"Tại sao chuyến này bị trễ?\"* "
                    f"để tôi phân tích ngay trên dữ liệu thực tế của chuyến bay này!"
                )
                base_reply += bridge_note

            if item.get("category") == "aviation_metrics" or "fdp" in term_id or "tarmac" in term_id:
                suggested = [
                    "Quy trình SOP tương ứng để xử lý tình huống này là gì?",
                    "Chế tài phạt của US DOT hoặc Cục Hàng không Việt Nam thế nào?",
                    "Chi phí trễ chuyến $101.18/phút được FAA cấu thành từ đâu?",
                    "Làm sao để mô phỏng What-If phương án giải cứu chuyến bay?",
                ]
            elif item.get("category") == "ml_metrics":
                suggested = [
                    "Tại sao mô hình lại dùng Threshold 0.2709 thay vì 0.50?",
                    "Ý nghĩa của chỉ số Lift @ 10% trong xếp hạng rủi ro?",
                    "Brier Score đo lường độ tin cậy của xác suất như thế nào?",
                    "Sự khác biệt giữa PR-AUC và ROC-AUC khi dữ liệu mất cân bằng?",
                ]
            else:
                suggested = DEFAULT_SUGGESTED_QUESTIONS[:4]

            return ChatResponse(
                reply=base_reply,
                source="offline_knowledge_engine",
                matched_terms=matched_terms,
                grounding_citations=citations,
                suggested_questions=suggested,
            )

    # -------------------------------------------------------------------------
    # INTENT 4: Tailored Specific Flight Analysis & OCC Risk Diagnosis
    # -------------------------------------------------------------------------
    if is_flight_intent:
        if advisory is None and flight_context is not None:
            try:
                advisory = generate_dispatch_advisory(
                    carrier_code=flight_context.get("carrier_code"),
                    origin=flight_context.get("origin"),
                    dest=flight_context.get("dest"),
                    flight_date=flight_context.get("flight_date"),
                    dep_hour=flight_context.get("dep_hour"),
                    flight_number=flight_context.get("flight_number"),
                )
            except Exception:
                advisory = None

        if advisory is None and flight_context is None:
            return ChatResponse(
                reply=(
                    "### ℹ️ Bạn Chưa Chọn Chuyến Bay Cụ Thể\n\n"
                    "Để Copilot có thể phân tích rủi ro, căn nguyên trễ hoặc phơi nhiễm pháp lý, bạn vui lòng:\n"
                    "1. Vào **Tab 1: Kế Hoạch 5 Chặng & What-If**.\n"
                    "2. Bấm chọn chuyến bay mẫu (ví dụ: `📌 Mẫu 4568`) hoặc nhập Flight ID kho dữ liệu.\n"
                    "3. Bấm **`💬 Hỏi Copilot Về Chuyến Này`** để tôi chẩn đoán toàn diện cho bạn!"
                ),
                source="offline_knowledge_engine",
                matched_terms=["flight_context_required"],
                grounding_citations=[],
                suggested_questions=[
                    "Quy tắc Tarmac Delay 180 phút của US DOT phạt bao nhiêu USD và yêu cầu gì?",
                    "Giới hạn giờ bay FDP (FAR Part 117) và vùng WOCL ảnh hưởng thế nào đến an toàn?",
                    "Chỉ số Lift @ 10% và Brier Score có ý nghĩa gì?",
                ],
            )

        if advisory is not None:
            ctx = advisory.flight_context
            pred = advisory.prediction_context
            fin = advisory.financial_exposure
            reg = advisory.regulatory_compliance

            matched_terms.append(f"flight_{ctx.carrier_code}_{ctx.flight_number or '4568'}")
            for item in reg.get("legal_evaluations", []):
                citations.append(f"{item.get('legal_code')}: {item.get('citation')}")

            risk_emoji = "🔴" if pred.risk_band == "HIGH" else ("🟡" if pred.risk_band == "ELEVATED" else "🟢")
            flight_header = f"Chuyến bay `{ctx.carrier_code}{ctx.flight_number or ''}` ({ctx.carrier_name}) | Tuyến: `{ctx.origin} ➔ {ctx.dest}` lúc `{ctx.dep_window_label}`"

            # -----------------------------------------------------------------
            # SUB-INTENT 4A: Legal & Regulatory Law Violations & Penalties
            # -----------------------------------------------------------------
            if any(k in clean_msg for k in ["luat", "phap ly", "phat", "che tai", "vi pham", "14 cfr", "far", "thong tu", "nghi dinh"]):
                evals = reg.get("legal_evaluations", [])
                lines = [
                    f"### ⚖️ Thẩm Định Pháp Lý & Chế Tài Xử Phạt: {flight_header}",
                    f"Căn cứ đối soát dữ liệu hành trình theo quy định của **US DOT (Bộ GTVT Hoa Kỳ)** và **Cục Hàng không VN**:\n",
                ]
                for le in evals:
                    sev_icon = "🚨" if le.get("severity") == "CRITICAL" else ("⚠️" if le.get("severity") == "ELEVATED" else "✅")
                    lines.append(f"- {sev_icon} **{le.get('legal_code')}** — *{le.get('citation')}*")
                    lines.append(f"  - **Nội dung quy định**: {le.get('statutory_text')}")
                    lines.append(f"  - **Mức chế tài áp dụng**: `{le.get('statutory_penalty')}`")
                    lines.append(f"  - **🚨 MỆNH LỆNH OCC BẮT BUỘC**: **{le.get('mandatory_action')}**\n")

                lines.append(f"💵 **Tổng Rủi Ro Tiền Phạt Tiềm Tàng**: **`${(fin.tarmac_penalty_exposure_usd + fin.cash_refund_exposure_usd):,.2f} USD`**.")
                suggested = [
                    "Kế hoạch hành động 5 chặng cho chuyến bay này là gì?",
                    "Tại sao chuyến này lại có xác suất trễ cao?",
                    "Mô phỏng đổi giờ bay sang 10:00 sáng để né phạt (What-If)",
                    "Tổ bay có bị time out vượt trần FDP không?",
                ]
                return ChatResponse(
                    reply="\n".join(lines),
                    source="offline_knowledge_engine",
                    matched_terms=matched_terms,
                    grounding_citations=citations,
                    suggested_questions=suggested,
                    flight_context=ctx.to_dict() if hasattr(ctx, "to_dict") else asdict(ctx),
                )

            # -----------------------------------------------------------------
            # SUB-INTENT 4B: Delay Causes & Congestion Analysis
            # -----------------------------------------------------------------
            if any(k in clean_msg for k in ["tai sao", "nguyen nhan", "tac nghen", "can nguyen", "ly do", "yeu to", "huong gio", "thoi tiet"]):
                lines = [
                    f"### 🔍 Phân Tích Căn Nguyên Trễ Chuyến: {flight_header}",
                    f"Mô hình AI dự báo xác suất trễ **`{pred.delay_probability*100:.1f}%`** ({risk_emoji} Mức **{pred.risk_band}**, Lift **`{pred.lift_at_10:.2f}x`**). Căn nguyên trễ xuất phát từ 4 yếu tố then chốt:\n",
                    f"1. 🛫 **Mật độ nghẽn đường lăn sân bay đi (`{ctx.origin}`)**: Đang ghi nhận **`{ctx.scheduled_departures_hour} chuyến/giờ`** (Rơi vào khung giờ cao điểm nghẽn Hub Bank).",
                    f"2. 📈 **Lịch sử tuyến bay 30 ngày qua (`{ctx.origin} ➔ {ctx.dest}`)**: Có tỷ lệ trễ đạt **`{(ctx.route_delay_rate_30d or 0)*100:.1f}%`**.",
                    f"3. 🏢 **Tỷ lệ trễ mạng lưới hãng bay (`{ctx.carrier_code}`)**: Tỷ lệ trễ trung bình của hãng là **`{(ctx.carrier_delay_rate_30d or 0)*100:.1f}%`** (Mô hình: `{ctx.carrier_type.upper()}`).",
                    f"4. 📍 **Cự ly chặng bay**: `{ctx.distance_miles:.0f} dặm` ({ctx.distance_bucket.upper()}) — Khả năng bay bù giờ trên không (Airborne make-up) bị hạn chế.",
                    f"\n⏱️ **Thời gian trễ dự kiến (AI Forecast)**: Khoảng **`~{pred.projected_delay_min} phút`**.",
                ]
                suggested = [
                    "Chuyến bay này có nguy cơ vi phạm luật gì?",
                    "Thiệt hại chi phí trễ chuyến này là bao nhiêu?",
                    "Mô phỏng đổi giờ bay sang 10:00 sáng để né nghẽn",
                    "Kế hoạch 5 chặng xử lý chuyến bay này",
                ]
                return ChatResponse(
                    reply="\n".join(lines),
                    source="offline_knowledge_engine",
                    matched_terms=matched_terms,
                    grounding_citations=citations,
                    suggested_questions=suggested,
                    flight_context=ctx.to_dict() if hasattr(ctx, "to_dict") else asdict(ctx),
                )

            # -----------------------------------------------------------------
            # SUB-INTENT 4C: Crew, Pilot & FDP Time-out Risk
            # -----------------------------------------------------------------
            if any(k in clean_msg for k in ["to bay", "phi cong", "crew", "fdp", "time out", "time-out", "het gio", "gio bay", "standby"]):
                lines = [
                    f"### 👨‍✈️ Giám Sát Giới Hạn Giờ Bay Tổ Bay (FDP): {flight_header}",
                    f"Căn cứ **FAR Part 117 (FAA Flight Duty Period Regulations)**:\n",
                    f"- 🕒 **Khung giờ khởi hành**: `{ctx.dep_window_label}`.",
                    f"- ⚠️ **Đánh giá rủi ro FDP**: Với cự ly `{ctx.distance_miles:.0f} dặm` và thời gian trễ dự kiến `~{pred.projected_delay_min} phút`, thời gian lăn ra đường lăn (Taxi-Out) có nguy cơ kéo dài quá 45 phút.",
                    f"- 🚨 **Nguy cơ vi phạm**: Nếu thời gian làm nhiệm vụ cộng dồn vượt quá 12.0 giờ (theo Table B), tổ bay sẽ **chạm trần FDP** và không được phép cất cánh hợp pháp!",
                    f"- 💡 **Hậu quả tác nghiệp**: Nếu bị time-out trên đường lăn, tàu bay bắt buộc phải quay lại cửa (Gate Return), gây hủy chuyến dây chuyền.",
                    f"\n👉 **MỆNH LỆNH OCC KHUYẾN NGHỊ**:\n"
                    f"1. Kích hoạt ngay tổ bay dự bị **Hot Standby Crew** tại sân `{ctx.origin}` trước T-60m.\n"
                    f"2. Đàm phán với ATC để cấp slot cất cánh ưu tiên né bẫy FDP.",
                ]
                suggested = [
                    "Mô phỏng kích hoạt tổ bay dự bị Standby Crew (What-If)",
                    "Xem quy trình SOP đổi tổ bay sop_crew_timeout_replacement",
                    "Chuyến bay này có nguy cơ vi phạm luật gì?",
                    "Kế hoạch 5 chặng điều hành cho chuyến bay này",
                ]
                return ChatResponse(
                    reply="\n".join(lines),
                    source="offline_knowledge_engine",
                    matched_terms=matched_terms,
                    grounding_citations=["FAA Title 14 CFR Part 117 (Flight Duty Limits)"],
                    suggested_questions=suggested,
                    flight_context=ctx.to_dict() if hasattr(ctx, "to_dict") else asdict(ctx),
                )

            # -----------------------------------------------------------------
            # SUB-INTENT 4D: Financial Exposure & Delay Costs
            # -----------------------------------------------------------------
            if any(k in clean_msg for k in ["chi phi", "thiet hai", "tien", "tai chinh", "mat bao nhieu", "ton that", "bao toan", "tiet kiem", "do la", "usd"]):
                lines = [
                    f"### 💵 Bóc Tách Phơi Nhiễm Tài Chính: {flight_header}",
                    f"Đo lường thiệt hại chi phí định lượng theo chuẩn FAA và các quy chế bồi hoàn:\n",
                    f"- 🕒 **Chi phí trễ vận hành trực tiếp**: **`${fin.base_delay_cost_usd:,.2f} USD`**  \n"
                    f"  *(Căn cứ định mức FAA/A4A: $101.18 USD/phút × ~{pred.projected_delay_min} phút trễ bao gồm nhiên liệu, lương phi hành đoàn và bảo trì)*.",
                    f"- ⚖️ **Rủi ro chế tài phạt Tarmac Delay (14 CFR § 259.4)**: **`${fin.tarmac_penalty_exposure_usd:,.2f} USD`**  \n"
                    f"  *(Mức phạt tối đa $37,377 USD/pax nếu để kẹt khách quá 180 phút trên sân đỗ)*.",
                    f"- 💵 **Rủi ro bồi hoàn tiền mặt bắt buộc (14 CFR § 260.6)**: **`${fin.cash_refund_exposure_usd:,.2f} USD`**  \n"
                    f"  *(Ước tính $275 USD/pax cho {fin.estimated_passengers} hành khách nếu trễ >= 3 tiếng nội địa)*.",
                    f"\n🏆 **Bảo toàn tài chính ròng khi OCC can thiệp chủ động**: **`${fin.proactive_mitigation_savings_usd:,.2f} USD`**.",
                ]
                suggested = [
                    "Những phương án can thiệp nào giúp giảm chi phí? (What-If)",
                    "Chuyến bay này có nguy cơ vi phạm luật gì?",
                    "Kế hoạch 5 chặng hành động cho chuyến bay này",
                    "Tại sao chuyến này lại bị trễ?",
                ]
                return ChatResponse(
                    reply="\n".join(lines),
                    source="offline_knowledge_engine",
                    matched_terms=matched_terms,
                    grounding_citations=["FAA/A4A Cost of Delay Standard ($101.18/min)", "14 CFR § 260.6", "14 CFR § 259.4"],
                    suggested_questions=suggested,
                    flight_context=ctx.to_dict() if hasattr(ctx, "to_dict") else asdict(ctx),
                )

            # -----------------------------------------------------------------
            # SUB-INTENT 4E: Action Plan & 5-Gate Solution Checklist
            # -----------------------------------------------------------------
            if any(k in clean_msg for k in ["can lam gi", "giai phap", "ke hoach", "hanh dong", "xu ly the nao", "phuong an", "5 chang", "timeline", "buoc"]):
                lines = [
                    f"### ⏱️ Bản Kế Hoạch 5 Chặng Tác Nghiệp Bắt Buộc: {flight_header}",
                    f"Lịch trình điều phối từng phút dành cho OCC Dispatcher, Gate Lead và Tổ Bay:\n",
                ]
                for act in advisory.timeline_actions:
                    p_badge = "🔴" if act.priority == "CRITICAL" else ("🟡" if act.priority == "HIGH" else "🟢")
                    lines.append(f"- {p_badge} **[{act.phase_code} - {act.phase_name}]**: **{act.action_title}** *(Phụ trách: `{act.responsible_role}`)*")
                    lines.append(f"  - *Hướng dẫn tác nghiệp*: {act.operational_guidance}")
                    lines.append(f"  - 👉 **Quyết định then chốt**: `{act.critical_decision}`\n")

                if advisory.recommended_sops:
                    lines.append("📋 **Quy Trình SOP Cần Thực Hiện Ngay**:")
                    for s in advisory.recommended_sops:
                        lines.append(f"- `{s.get('sop_id')}`: {s.get('title_vi')} *(Lý do: {s.get('binding_reason')})*")

                suggested = [
                    "Chuyến bay này có nguy cơ vi phạm luật gì?",
                    "Mô phỏng can thiệp What-If để xem số tiền tiết kiệm",
                    "Tổ bay chuyến này có bị time out không?",
                    "Thiệt hại chi phí chuyến này bao nhiêu?",
                ]
                return ChatResponse(
                    reply="\n".join(lines),
                    source="offline_knowledge_engine",
                    matched_terms=matched_terms,
                    grounding_citations=citations,
                    suggested_questions=suggested,
                    flight_context=ctx.to_dict() if hasattr(ctx, "to_dict") else asdict(ctx),
                )

            # -----------------------------------------------------------------
            # SUB-INTENT 4F: Comprehensive Full Flight Overview (Default)
            # -----------------------------------------------------------------
            lines = [
                f"### ✈️ Phân Tích & Khuyến Nghị Tác Nghiệp: {flight_header}",
                f"**Mã Khuyến Nghị**: `{advisory.advisory_id}` | **Đánh Giá AI**: {risk_emoji} **{pred.risk_band}** (Xác suất trễ: `{pred.delay_probability*100:.1f}%`, Lift: `{pred.lift_at_10:.2f}x`)\n",
                f"#### 1. Đánh Giá Tình Hình & Rủi Ro",
                f"- Độ trễ dự kiến: **`~{pred.projected_delay_min} phút`**.",
                f"- Căn nguyên: Tuyến `{ctx.origin} ➔ {ctx.dest}` có tỷ lệ trễ 30 ngày là `{(ctx.route_delay_rate_30d or 0)*100:.1f}%`; Mật độ khởi hành sân bay `{ctx.origin}` đạt `{ctx.scheduled_departures_hour} chuyến/giờ`.",
                "",
                f"#### 2. Phơi Nhiễm Tài Chính & Chế Tài Pháp Lý",
                f"- Chi phí trễ vận hành FAA ($101.18/phút): **`${fin.base_delay_cost_usd:,.2f} USD`**.",
                f"- Rủi ro phạt Tarmac 14 CFR § 259.4: **`${fin.tarmac_penalty_exposure_usd:,.2f} USD`**.",
                f"- Rủi ro hoàn tiền mặt 14 CFR § 260.6: **`${fin.cash_refund_exposure_usd:,.2f} USD`**.",
                f"- Khoản tiết kiệm khi OCC can thiệp chủ động: **`${fin.proactive_mitigation_savings_usd:,.2f} USD`**.",
                "",
                f"#### 3. Mệnh Lệnh OCC Then Chốt",
                f"> **{advisory.timeline_actions[0].critical_decision if advisory.timeline_actions else 'Theo dõi sát sao cửa sổ Tarmac và giới hạn FDP.'}**",
            ]
            suggested = [
                "Chuyến bay này có nguy cơ vi phạm luật gì?",
                "Tại sao chuyến này lại bị trễ?",
                "Tổ bay chuyến này có bị time out không?",
                "Mô phỏng đổi giờ bay sang 10:00 sáng (What-If)",
            ]
            return ChatResponse(
                reply="\n".join(lines),
                source="offline_knowledge_engine",
                matched_terms=matched_terms,
                grounding_citations=citations,
                suggested_questions=suggested,
                flight_context=ctx.to_dict() if hasattr(ctx, "to_dict") else asdict(ctx),
                raw_metadata={"advisory_id": advisory.advisory_id},
            )


    # -------------------------------------------------------------------------
    # INTENT 5: Concept / Metric / Regulatory Law Explanation
    # -------------------------------------------------------------------------
    res = explain_term(message)
    if res.get("status") in ("exact_match", "search_hit"):
        item = res.get("term") or res.get("best_match")
        term_id = item.get("term_id") or item.get("sop_id")
        matched_terms.append(term_id)

        regs = item.get("related_regulations", [])
        if regs:
            citations.extend(regs)
        if item.get("steps"):
            citations.append(f"SOP: {item.get('sop_id')}")
            for st in item.get("steps", []):
                rn = st.get("regulatory_notice") if isinstance(st, dict) else getattr(st, "regulatory_notice", None)
                if rn:
                    citations.append(rn)
        elif item.get("regulatory_notice"):
            citations.append(item.get("regulatory_notice"))


        # Contextual follow-up suggestions
        if item.get("category") == "aviation_metrics" or "fdp" in term_id or "tarmac" in term_id:
            suggested = [
                "Quy trình SOP tương ứng để xử lý tình huống này là gì?",
                "Chế tài phạt của US DOT hoặc Cục Hàng không Việt Nam thế nào?",
                "Chi phí trễ chuyến $101.18/phút được FAA cấu thành từ đâu?",
                "Làm sao để mô phỏng What-If phương án giải cứu chuyến bay?",
            ]
        elif item.get("category") == "ml_metrics":
            suggested = [
                "Tại sao mô hình lại dùng Threshold 0.2709 thay vì 0.50?",
                "Ý nghĩa của chỉ số Lift @ 10% trong xếp hạng rủi ro?",
                "Brier Score đo lường độ tin cậy của xác suất như thế nào?",
                "Sự khác biệt giữa PR-AUC và ROC-AUC khi dữ liệu mất cân bằng?",
            ]
        else:
            suggested = DEFAULT_SUGGESTED_QUESTIONS[:4]

        return ChatResponse(
            reply=res.get("markdown", ""),
            source="offline_knowledge_engine",
            matched_terms=matched_terms,
            grounding_citations=citations,
            suggested_questions=suggested,
        )

    # -------------------------------------------------------------------------
    # FALLBACK: Helpful response with smart search hits or catalog guide
    # -------------------------------------------------------------------------
    top_hits = search_knowledge(message, top_k=4)
    if top_hits:
        lines = [
            f"Tôi chưa tìm thấy định nghĩa chính xác tuyệt đối cho cụm từ *\"{message}\"*, nhưng dưới đây là các khái niệm và quy trình liên quan nhất trong Kho Tri Thức 40 Đề Mục:",
            "",
        ]
        for hit in top_hits:
            if hit.get("_result_type") == "sop":
                lines.append(f"- 📋 **Quy trình SOP `{hit.get('sop_id')}`**: **{hit.get('title_vi')}** — {hit.get('purpose')}")
            else:
                acronym = f" ({hit.get('acronym')})" if hit.get("acronym") else ""
                lines.append(f"- 📘 **`{hit.get('term_id')}`**: **{hit.get('name_vi')}{acronym}** — {hit.get('definition_vi')[:120]}...")

        lines.append("")
        lines.append("Bạn có muốn tôi giải thích chi tiết mục nào ở trên không?")
        return ChatResponse(
            reply="\n".join(lines),
            source="offline_knowledge_engine",
            matched_terms=[h.get("term_id") or h.get("sop_id") for h in top_hits],
            grounding_citations=["Aviation Operations & ML Knowledge Base (40 Items)"],
            suggested_questions=[
                f"Giải thích chi tiết {top_hits[0].get('term_id') or top_hits[0].get('sop_id')}",
                "Xem toàn bộ danh mục 40 đề mục từ điển",
                "Quy tắc Tarmac Delay 180 phút quy định chế tài gì?",
                "Mô phỏng đổi giờ bay né cao điểm What-If",
            ],
        )

    # General fallback
    return ChatResponse(
        reply=(
            f"Tôi không tìm thấy thuật ngữ hay quy trình nào khớp với *\"{message}\"* trong cơ sở dữ liệu.\n\n"
            "Bạn có thể hỏi về:\n"
            "- Các chỉ số vận hành: `FDP`, `Tarmac Delay`, `OTP`, `Taxi-out`, `Turnaround Time`, `Cost of Delay` ($101.18/phút).\n"
            "- Các chỉ số AI: `Delay Probability`, `Risk Band`, `Lift @ 10%`, `Brier Score`, `Optimal Threshold` (0.2709).\n"
            "- Các quy trình SOP: `sop_tarmac_clockwork_emergency`, `sop_crew_timeout_replacement`, `sop_delay_incident`.\n"
            "- Hoặc hỏi trực tiếp về rủi ro của chuyến bay đang xem trên màn hình!"
        ),
        source="offline_knowledge_engine",
        matched_terms=[],
        grounding_citations=[],
        suggested_questions=DEFAULT_SUGGESTED_QUESTIONS,
    )


# =============================================================================
# MAIN HIGH-LEVEL COPILOT ENTRYPOINT
# =============================================================================

def ask_copilot(
    message: str,
    flight_id: Optional[Union[int, str]] = None,
    flight_context: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    model_provider: str = "auto",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
) -> ChatResponse:
    """
    Unified high-level entrypoint for the Conversational OCC Copilot.
    Supports Multi-Provider Flagship LLM execution (Gemini 3.8, Claude 3.7, OpenAI o3-mini/o1, DeepSeek R1)
    with Zero-dependency offline rule-based fallback.
    """
    message = (message or "").strip()
    if not message:
        return _ask_offline_knowledge_engine("help")

    # 1. Resolve flight advisory if flight_id is given OR mentioned in message
    if flight_id is None:
        norm_m = re.sub(r"(?<=\d)[\.,](?=\d)", "", message)
        clean_m = strip_accents(norm_m.lower())
        id_m = re.search(r"(?:chuyen(?:\s*bay)?|flight|ma(?:\s*so)?|id)\s*[:#]?\s*([a-zA-Z0-9_-]+)", clean_m)
        if id_m:
            candidate_id = id_m.group(1).strip()
            # If purely numeric, check if it's a warehouse flight_id
            if candidate_id.isdigit():
                try:
                    cand_adv = lookup_flight_advisory(candidate_id)
                    if cand_adv:
                        flight_id = candidate_id
                except Exception:
                    pass

    advisory: Optional[DispatchAdvisory] = None
    if flight_id is not None:
        try:
            advisory = lookup_flight_advisory(flight_id)
            if advisory:
                flight_context = advisory.flight_context.to_dict()
        except Exception as e:
            logger.warning(f"Could not load flight advisory for {flight_id}: {e}")

    # 2. Parse provider and model name
    raw_prov = (model_provider or "auto").strip().lower()
    target_prov = raw_prov
    target_model = (model_name or "").strip() or None

    if ":" in raw_prov:
        parts = raw_prov.split(":", 1)
        target_prov = parts[0].strip()
        if not target_model:
            target_model = parts[1].strip()

    if target_prov == "offline":
        return _ask_offline_knowledge_engine(message, flight_context=flight_context, advisory=advisory)

    user_key = (api_key or "").strip()
    gemini_key = (user_key if target_prov in ("auto", "gemini") and user_key else None) or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    claude_key = (user_key if target_prov in ("auto", "claude", "anthropic") and user_key else None) or os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    openai_key = (user_key if target_prov in ("auto", "openai") and user_key else None) or os.getenv("OPENAI_API_KEY")
    deepseek_key = (user_key if target_prov in ("auto", "deepseek") and user_key else None) or os.getenv("DEEPSEEK_API_KEY")

    has_any_key = bool(gemini_key or claude_key or openai_key or deepseek_key)

    if has_any_key:
        summary_text = None
        if advisory:
            summary_text = (
                f"Chuyến bay: {advisory.flight_context.carrier_code}{advisory.flight_context.flight_number or ''} "
                f"({advisory.flight_context.origin} -> {advisory.flight_context.dest}), "
                f"Ngày: {advisory.flight_context.flight_date} lúc {advisory.flight_context.dep_window_label}.\n"
                f"Dự báo AI: Xác suất trễ {(advisory.prediction_context.delay_probability*100):.1f}%, "
                f"Mức rủi ro: {advisory.prediction_context.risk_band}, Lift @ 10%: {advisory.prediction_context.lift_at_10:.2f}x.\n"
                f"Chi phí phơi nhiễm: Chi phí trễ FAA ${advisory.financial_exposure.base_delay_cost_usd:,.2f} USD, "
                f"Rủi ro phạt Tarmac ${advisory.financial_exposure.tarmac_penalty_exposure_usd:,.2f} USD, "
                f"Hoàn tiền 14 CFR § 260.6: ${advisory.financial_exposure.cash_refund_exposure_usd:,.2f} USD.\n"
                f"Tóm tắt: {advisory.executive_summary}"
            )
        system_prompt = _build_system_prompt(summary_text)

        llm_reply: Optional[str] = None
        llm_source = "offline_knowledge_engine"
        used_model = target_model or ""

        # Specific provider dispatch
        if target_prov == "claude" and claude_key:
            m = target_model or "claude-3-7-sonnet-latest"
            llm_reply = _call_claude_api(message, claude_key, system_prompt, conversation_history, model_name=m)
            if llm_reply:
                llm_source = "llm_claude"
                used_model = m
        elif target_prov == "openai" and openai_key:
            m = target_model or "o3-mini"
            llm_reply = _call_openai_api(message, openai_key, system_prompt, conversation_history, model_name=m)
            if llm_reply:
                llm_source = "llm_openai"
                used_model = m
        elif target_prov == "gemini" and gemini_key:
            m = target_model or "gemini-3.8-flash"
            llm_reply = _call_gemini_api(message, gemini_key, system_prompt, conversation_history, model_name=m)
            if llm_reply:
                llm_source = "llm_gemini"
                used_model = m
        elif target_prov == "deepseek" and deepseek_key:
            m = target_model or "deepseek-reasoner"
            llm_reply = _call_deepseek_api(message, deepseek_key, system_prompt, conversation_history, model_name=m)
            if llm_reply:
                llm_source = "llm_deepseek"
                used_model = m
        elif target_prov == "auto":
            # Auto fallback priority: Claude -> OpenAI -> Gemini -> DeepSeek
            if claude_key:
                m = target_model or "claude-3-7-sonnet-latest"
                llm_reply = _call_claude_api(message, claude_key, system_prompt, conversation_history, model_name=m)
                if llm_reply:
                    llm_source = "llm_claude"
                    used_model = m
            if not llm_reply and openai_key:
                m = target_model or "o3-mini"
                llm_reply = _call_openai_api(message, openai_key, system_prompt, conversation_history, model_name=m)
                if llm_reply:
                    llm_source = "llm_openai"
                    used_model = m
            if not llm_reply and gemini_key:
                m = target_model or "gemini-3.8-flash"
                llm_reply = _call_gemini_api(message, gemini_key, system_prompt, conversation_history, model_name=m)
                if llm_reply:
                    llm_source = "llm_gemini"
                    used_model = m
            if not llm_reply and deepseek_key:
                m = target_model or "deepseek-reasoner"
                llm_reply = _call_deepseek_api(message, deepseek_key, system_prompt, conversation_history, model_name=m)
                if llm_reply:
                    llm_source = "llm_deepseek"
                    used_model = m

        if llm_reply:
            citations = [
                "US DOT 14 CFR § 259.4 (Tarmac Delay Contingency Plan)",
                "FAA Title 14 CFR Part 117 (Flight Duty Limits)",
                "US DOT 14 CFR § 260.6 (Mandatory Cash Refunds)",
                "FAA/A4A Cost of Delay Standard ($101.18/min)",
            ]
            return ChatResponse(
                reply=llm_reply,
                source=llm_source,
                matched_terms=["llm_grounded_response"],
                grounding_citations=citations,
                suggested_questions=DEFAULT_SUGGESTED_QUESTIONS[:4],
                flight_context=flight_context,
                raw_metadata={"model": used_model, "provider": target_prov},
            )

    # 3. Fallback to our robust offline knowledge engine
    return _ask_offline_knowledge_engine(message, flight_context=flight_context, advisory=advisory)
