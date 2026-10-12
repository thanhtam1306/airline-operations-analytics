"""
Flight delay-risk API (FastAPI) with multi-model tournament support.

    uvicorn ml.api:app --port 8000
    POST /predict  {"carrier_code":"AA","origin":"ATL","dest":"DFW",
                    "flight_date":"2025-02-14","dep_hour":17}
    GET  /models   List trained models and evaluation tournament leaderboard

Serving features are built from the SAME dbt feature definitions via lookup
tables exported at training time (route/carrier rolling rates, congestion
medians) — zero training/serving skew. Model card: docs/model_card.md.
"""
from __future__ import annotations

import json
import os
import time
from datetime import date as date_type
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field

from ml.advisory import (
    format_advisory_markdown,
    generate_dispatch_advisory,
    simulate_what_if,
)
from ml.slide_generator import (
    generate_presentation_html,
    generate_presentation_markdown,
    generate_presentation_pptx,
)
from ml.chat import (
    ChatMessage,
    ChatResponse,
    ask_copilot,
    get_copilot_quick_prompts,
    validate_gemini_key,
    validate_claude_key,
    validate_openai_key,
    validate_deepseek_key,
)
from ml.copilot import (
    KNOWLEDGE_TERMS,
    SOP_CHECKLISTS,
)
from ml.ensemble import SoftVotingEnsemble
from ml.regulatory_engine import evaluate_regulatory_compliance
from ml.web_ui import (
    HTML_TEMPLATE,
    KNOWN_AIRPORTS,
    KNOWN_CARRIERS,
    render_embed_chat,
    render_homepage,
)



ART = Path(__file__).resolve().parent / "artifacts"

app = FastAPI(
    title="Flight Delay-Risk API",
    version="2.0.0",
    description="Multi-model real-time flight departure delay risk API (Logistic Regression, "
                "LightGBM, XGBoost, CatBoost, and Soft-Voting Ensemble). Features defined in dbt. "
                "See docs/model_card.md for metrics and operational guidance.",
)

BASELINE_FEATURES = ["dep_hour", "route_delay_rate_30d", "carrier_delay_rate_30d",
                     "scheduled_departures_hour", "distance_miles"]
ALL_FEATURES = ["dep_hour", "route_delay_rate_30d", "carrier_delay_rate_30d",
                "scheduled_departures_hour", "distance_miles", "route_flights_30d",
                "day_of_week", "distance_bucket", "carrier_type", "is_weekend"]

MODEL_FILES = {
    "best": "best_delay_model.joblib",
    "lgbm": "lgbm_delay.joblib",
    "xgboost": "xgboost_delay.joblib",
    "catboost": "catboost_delay.joblib",
    "ensemble": "ensemble_delay.joblib",
    "baseline": "baseline_logreg.joblib",
}


class PredictRequest(BaseModel):
    carrier_code: str = Field(..., examples=["AA"], min_length=2, max_length=3)
    origin: str = Field(..., examples=["ATL"], min_length=3, max_length=3)
    dest: str = Field(..., examples=["DFW"], min_length=3, max_length=3)
    flight_date: date_type = Field(..., examples=["2025-02-14"])
    dep_hour: int = Field(..., ge=0, le=23, examples=[17])


class PredictResponse(BaseModel):
    delay_probability: float
    risk_band: str
    threshold: float
    model: str
    model_type: str
    features_used: dict
    regulatory_compliance: dict


class AdvisoryRequest(BaseModel):
    flight_id: Optional[Union[int, str]] = Field(None, examples=[4568], description="Optional flight_id from warehouse")
    carrier_code: Optional[str] = Field(None, examples=["AA"], min_length=2, max_length=3)
    origin: Optional[str] = Field(None, examples=["ATL"], min_length=3, max_length=3)
    dest: Optional[str] = Field(None, examples=["DFW"], min_length=3, max_length=3)
    flight_date: Optional[str] = Field(None, examples=["2025-02-14"])
    dep_hour: Optional[int] = Field(None, ge=0, le=23, examples=[17])
    flight_number: Optional[Union[int, str]] = None
    model: str = Field("best", description="Model candidate to use: best, lgbm, xgboost, catboost, ensemble, baseline")


class SimulateRequest(BaseModel):
    flight_id: Optional[Union[int, str]] = None
    carrier_code: Optional[str] = None
    origin: Optional[str] = None
    dest: Optional[str] = None
    flight_date: Optional[str] = None
    dep_hour: Optional[int] = None
    flight_number: Optional[Union[int, str]] = None
    model: str = "best"
    scenario_type: str = Field(..., description="reschedule_hour, crew_standby, airborne_speedup, tail_swap")
    scenario_params: Optional[dict] = None


class ChatRequest(BaseModel):
    message: str = Field(..., examples=["FDP là gì và khi nào bị coi là vi phạm?"])
    flight_id: Optional[Union[int, str]] = None
    flight_context: Optional[dict] = None
    conversation_history: Optional[list] = None
    model_provider: str = Field("auto", description="auto, gemini, claude, openai, deepseek, offline")
    model_name: Optional[str] = Field(None, description="Specific model ID (e.g. gemini-3.8-flash, claude-3-7-sonnet-latest, o3-mini, deepseek-reasoner)")
    api_key: Optional[str] = Field(None, description="Optional API Key provided by user via frontend settings")


class ValidateKeyRequest(BaseModel):
    provider: str = Field("gemini", description="gemini, claude, openai, deepseek")
    api_key: str = Field(..., description="API Key string to test")
    model_name: Optional[str] = Field(None, description="Optional specific model ID to test")




@lru_cache(maxsize=1)
def _load_lookups():
    routes = pd.read_parquet(ART / "route_lookup.parquet")
    carriers = pd.read_parquet(ART / "carrier_lookup.parquet")
    congestion = pd.read_parquet(ART / "congestion_lookup.parquet")
    metrics_path = ART / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    return routes, carriers, congestion, metrics


@lru_cache(maxsize=8)
def _load_model(model_name: str):
    file_name = MODEL_FILES.get(model_name.lower())
    if not file_name:
        raise HTTPException(400, f"Unsupported model '{model_name}'. Choose from: {list(MODEL_FILES.keys())}")
    
    path = ART / file_name
    if not path.exists():
        # Fallback for 'best'
        if model_name == "best" and (ART / "lgbm_delay.joblib").exists():
            path = ART / "lgbm_delay.joblib"
        else:
            raise HTTPException(404, f"Model artifact '{file_name}' not found. Please run: make train")

    model = joblib.load(path)
    _, _, _, metrics = _load_lookups()

    # Determine threshold
    thr = 0.25
    if model_name == "best" and "best_model" in metrics:
        winner = metrics["best_model"].get("winner", "lgbm")
        thr = metrics.get(winner, {}).get("val", {}).get("threshold", 0.25)
    elif model_name in metrics:
        thr = metrics[model_name].get("val", {}).get("threshold", 0.25)
    elif "baseline" in model_name and "baseline_logreg" in metrics:
        thr = metrics["baseline_logreg"].get("val", {}).get("threshold", 0.25)
    elif "lgbm" in metrics:
        thr = metrics["lgbm"].get("val", {}).get("threshold", 0.25)

    return model, thr, path.stem


def build_features(req: PredictRequest) -> dict:
    routes, carriers, congestion, _ = _load_lookups()

    r = routes[(routes.origin_airport == req.origin.upper())
               & (routes.dest_airport == req.dest.upper())]
    c = carriers[carriers.carrier_code == req.carrier_code.upper()]
    g = congestion[(congestion.origin_airport == req.origin.upper())
                   & (congestion.dep_hour == req.dep_hour)]

    if c.empty:
        raise HTTPException(422, f"unknown carrier '{req.carrier_code}'")
    distance = float(r.distance_miles.iloc[0]) if not r.empty else 800.0

    dow = (req.flight_date.weekday() + 1) % 7  # dim_date: 0=Sunday
    return {
        "dep_hour": req.dep_hour,
        "route_delay_rate_30d": float(r.route_delay_rate_30d.iloc[0]) if not r.empty else 0.0,
        "carrier_delay_rate_30d": float(c.carrier_delay_rate_30d.iloc[0]),
        "scheduled_departures_hour": int(g.scheduled_departures_hour.iloc[0]) if not g.empty else 5,
        "distance_miles": distance,
        "route_flights_30d": float(r.route_flights_30d.iloc[0]) if not r.empty else 0.0,
        "day_of_week": dow,
        "distance_bucket": ("short" if distance < 500 else "medium" if distance < 1500 else "long"),
        "carrier_type": str(c.carrier_type.iloc[0]),
        "is_weekend": int(dow in (0, 6)),
    }


@app.get("/health")
def health() -> dict:
    routes, carriers, _, metrics = _load_lookups()
    model, thr, model_id = _load_model("best")
    winner = metrics.get("best_model", {}).get("winner", model_id)
    return {
        "status": "ok",
        "active_model": model_id,
        "model_type": type(model).__name__,
        "tournament_winner": winner,
        "routes_known": int(len(routes)),
        "carriers_known": int(len(carriers)),
        "operating_threshold": round(thr, 4),
    }


@app.get("/models")
def get_models() -> dict:
    """Return tournament results and available candidate models."""
    _, _, _, metrics = _load_lookups()
    available = []
    for name, fname in MODEL_FILES.items():
        if (ART / fname).exists():
            available.append(name)
    return {
        "available_models": available,
        "tournament_leaderboard": metrics,
    }


@app.post("/predict", response_model=PredictResponse)
def predict(
    req: PredictRequest,
    model: str = Query("best", description="Model architecture to use: best, lgbm, catboost, xgboost, ensemble, baseline"),
) -> PredictResponse:
    clf, thr, model_id = _load_model(model)
    feats = build_features(req)

    expected_features = None
    if hasattr(clf, "feature_names_in_"):
        expected_features = list(clf.feature_names_in_)
    elif hasattr(clf, "feature_names_"):
        expected_features = list(clf.feature_names_)

    if expected_features:
        row = pd.DataFrame([feats])[expected_features]
    else:
        row = pd.DataFrame([feats])[ALL_FEATURES]

    for col in ("distance_bucket", "carrier_type"):
        if col in row.columns:
            row[col] = row[col].astype("category")
    if "is_weekend" in row.columns:
        row["is_weekend"] = row["is_weekend"].astype(int)

    p = float(clf.predict_proba(row)[:, 1][0])
    band = "high" if p >= thr else ("elevated" if p >= 0.7 * thr else "normal")

    compliance = evaluate_regulatory_compliance(
        carrier_code=req.carrier_code,
        origin=req.origin,
        dest=req.dest,
        dep_hour=req.dep_hour,
        delay_probability=p,
        threshold=thr,
        risk_band=band,
        features_used=feats,
    )

    return PredictResponse(
        delay_probability=round(p, 4),
        risk_band=band,
        threshold=round(thr, 4),
        model=model_id,
        model_type=type(clf).__name__,
        features_used=feats,
        regulatory_compliance=compliance,
    )


@app.post("/copilot/advisory")
def get_copilot_advisory(req: AdvisoryRequest) -> dict:
    """
    Generate a comprehensive, tri-layer grounded OCC Actionable Dispatch Advisory.
    Connects Data Warehouse + ML Prediction + Regulatory Legal Engine.
    """
    try:
        adv = generate_dispatch_advisory(
            flight_id=req.flight_id,
            carrier_code=req.carrier_code,
            origin=req.origin,
            dest=req.dest,
            flight_date=req.flight_date,
            dep_hour=req.dep_hour,
            flight_number=req.flight_number,
            model=req.model,
            strict_lookup=(req.flight_id is not None),
        )
        res = adv.to_dict()
        res["markdown_report"] = adv.to_markdown()
        return res
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error generating dispatch advisory: {str(e)}")


@app.post("/copilot/simulate")
def simulate_copilot_action(req: SimulateRequest) -> dict:
    """
    Simulate operational dispatch interventions (rescheduling, standby crew,
    airborne make-up time, or aircraft tail swap) and calculate net ROI.
    """
    try:
        adv = generate_dispatch_advisory(
            flight_id=req.flight_id,
            carrier_code=req.carrier_code,
            origin=req.origin,
            dest=req.dest,
            flight_date=req.flight_date,
            dep_hour=req.dep_hour,
            flight_number=req.flight_number,
            model=req.model,
        )
        return simulate_what_if(adv, req.scenario_type, req.scenario_params)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error simulating dispatch action: {str(e)}")


@app.post("/copilot/chat")
def chat_with_copilot(req: ChatRequest) -> dict:
    """
    Interactive Q&A with the OCC Copilot (Phase 6.3 & 6.4).
    Supports domain knowledge grounding, flight context, regulatory citations,
    and automatic fallback to offline knowledge engine (zero-dependency).
    """
    try:
        res = ask_copilot(
            message=req.message,
            flight_id=req.flight_id,
            flight_context=req.flight_context,
            conversation_history=req.conversation_history,
            model_provider=req.model_provider,
            model_name=req.model_name,
            api_key=req.api_key,
        )
        return res.to_dict()
    except Exception as e:
        raise HTTPException(500, f"Error processing Copilot chat: {str(e)}")


@app.post("/copilot/validate-key")
def validate_llm_key(req: ValidateKeyRequest) -> dict:
    """
    Validate user-provided API key from frontend Settings modal across all flagship providers.
    """
    prov = req.provider.lower().strip()
    if prov == "gemini":
        ok, msg = validate_gemini_key(req.api_key, model_name=req.model_name)
        return {"provider": "gemini", "valid": ok, "message": msg}
    elif prov in ("claude", "anthropic"):
        ok, msg = validate_claude_key(req.api_key, model_name=req.model_name)
        return {"provider": "claude", "valid": ok, "message": msg}
    elif prov == "openai":
        ok, msg = validate_openai_key(req.api_key, model_name=req.model_name)
        return {"provider": "openai", "valid": ok, "message": msg}
    elif prov == "deepseek":
        ok, msg = validate_deepseek_key(req.api_key, model_name=req.model_name)
        return {"provider": "deepseek", "valid": ok, "message": msg}
    return {"provider": prov, "valid": False, "message": f"Provider '{prov}' chưa được hỗ trợ kiểm tra."}


@app.get("/copilot/llm-catalog")
def get_copilot_llm_catalog() -> dict:
    """
    Return flagship AI models categorized by provider for UI selection.
    """
    return {
        "providers": [
            {
                "id": "gemini",
                "name": "Google Gemini",
                "icon": "⚡",
                "default_model": "gemini-3.8-flash",
                "models": [
                    {"id": "gemini-3.8-flash", "name": "Gemini 3.8 Flash (Mới nhất • Siêu tốc)", "badge": "New 3.8"},
                    {"id": "gemini-3.8-pro", "name": "Gemini 3.8 Pro (Mới nhất • Chuyên sâu)", "badge": "New 3.8"},
                    {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "badge": "Stable"},
                ],
            },
            {
                "id": "claude",
                "name": "Anthropic Claude",
                "icon": "🟣",
                "default_model": "claude-3-7-sonnet-latest",
                "models": [
                    {"id": "claude-3-7-sonnet-latest", "name": "Claude 3.7 Sonnet (Hybrid Reasoning)", "badge": "Flagship 3.7"},
                    {"id": "claude-3-5-sonnet-latest", "name": "Claude 3.5 Sonnet v2", "badge": "High Accuracy"},
                    {"id": "claude-3-5-haiku-latest", "name": "Claude 3.5 Haiku", "badge": "Fastest"},
                ],
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "icon": "🟢",
                "default_model": "o3-mini",
                "models": [
                    {"id": "o3-mini", "name": "OpenAI o3-mini (High-speed Reasoning)", "badge": "New o3"},
                    {"id": "o1", "name": "OpenAI o1 (Deep Reasoning)", "badge": "Flagship o1"},
                    {"id": "gpt-4.5-preview", "name": "GPT-4.5 Preview", "badge": "Preview"},
                    {"id": "gpt-4o", "name": "GPT-4o Omnichannel", "badge": "Stable"},
                ],
            },
            {
                "id": "deepseek",
                "name": "DeepSeek",
                "icon": "🔵",
                "default_model": "deepseek-reasoner",
                "models": [
                    {"id": "deepseek-reasoner", "name": "DeepSeek-R1 Reasoner (CoT Open)", "badge": "R1 CoT"},
                    {"id": "deepseek-chat", "name": "DeepSeek-V3 Chat", "badge": "V3"},
                ],
            },
            {
                "id": "offline",
                "name": "Hệ thống Nội bộ",
                "icon": "🛡️",
                "default_model": "offline",
                "models": [
                    {"id": "offline", "name": "Offline Grounding Engine (40 Đề mục • 0ms Latency)", "badge": "Free / 100% Uptime"},
                ],
            },
        ]
    }


@app.get("/copilot/prompts")
def get_copilot_prompts() -> dict:
    """Return categorized starter prompt chips for the web interface."""
    return {"prompts": get_copilot_quick_prompts()}


@app.get("/copilot/catalog")
def get_copilot_catalog() -> dict:
    """Return full 40-item enterprise knowledge base (terms and SOPs)."""
    terms = [t.to_dict() for t in KNOWLEDGE_TERMS.values()]
    sops = [s.to_dict() for s in SOP_CHECKLISTS.values()]
    return {
        "total_items": len(terms) + len(sops),
        "aviation_terms_count": sum(1 for t in terms if t.get("category") == "aviation_metrics"),
        "ml_terms_count": sum(1 for t in terms if t.get("category") == "ml_metrics"),
        "sops_count": len(sops),
        "terms": terms,
        "sops": sops,
    }


@app.post("/copilot/export-slide/pptx")
@app.get("/copilot/export-slide/pptx")
def export_slide_pptx(
    flight_id: Optional[Union[int, str]] = Query(None),
    carrier_code: Optional[str] = Query(None),
    origin: Optional[str] = Query(None),
    dest: Optional[str] = Query(None),
    flight_date: Optional[str] = Query(None),
    dep_hour: Optional[int] = Query(None),
    flight_number: Optional[Union[int, str]] = Query(None),
    model: str = Query("best"),
):
    """
    Generate and download an Executive PowerPoint presentation (.pptx)
    grounded in Data Warehouse, Machine Learning risk prediction, and Aviation Regulations.
    """
    try:
        adv = generate_dispatch_advisory(
            flight_id=flight_id,
            carrier_code=carrier_code,
            origin=origin,
            dest=dest,
            flight_date=flight_date,
            dep_hour=dep_hour,
            flight_number=flight_number,
            model=model,
            strict_lookup=(flight_id is not None),
        )
        adv_dict = adv.to_dict()
        pptx_bytes = generate_presentation_pptx(adv_dict)
        fl_code = f"{adv.flight_context.carrier_code}{adv.flight_context.flight_number or ''}"
        filename = f"SkyOps_Executive_Slide_{fl_code}_{adv.flight_context.origin}_{adv.flight_context.dest}.pptx"
        return Response(
            content=pptx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error generating PowerPoint slide deck: {str(e)}")


@app.get("/copilot/slide-deck", response_class=HTMLResponse)
@app.post("/copilot/slide-deck", response_class=HTMLResponse)
def get_slide_deck_html(
    flight_id: Optional[Union[int, str]] = Query(None),
    carrier_code: Optional[str] = Query(None),
    origin: Optional[str] = Query(None),
    dest: Optional[str] = Query(None),
    flight_date: Optional[str] = Query(None),
    dep_hour: Optional[int] = Query(None),
    flight_number: Optional[Union[int, str]] = Query(None),
    model: str = Query("best"),
):
    """
    Interactive standalone 16:9 HTML slide deck presentation with keyboard navigation.
    """
    try:
        adv = generate_dispatch_advisory(
            flight_id=flight_id,
            carrier_code=carrier_code,
            origin=origin,
            dest=dest,
            flight_date=flight_date,
            dep_hour=dep_hour,
            flight_number=flight_number,
            model=model,
            strict_lookup=(flight_id is not None),
        )
        return HTMLResponse(generate_presentation_html(adv.to_dict()))
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error generating HTML slide deck: {str(e)}")


@app.post("/copilot/export-slide/markdown")
@app.get("/copilot/export-slide/markdown")
def export_slide_markdown(
    flight_id: Optional[Union[int, str]] = Query(None),
    carrier_code: Optional[str] = Query(None),
    origin: Optional[str] = Query(None),
    dest: Optional[str] = Query(None),
    flight_date: Optional[str] = Query(None),
    dep_hour: Optional[int] = Query(None),
    flight_number: Optional[Union[int, str]] = Query(None),
    model: str = Query("best"),
):
    """
    Generate Marp-compatible Markdown presentation slides.
    """
    try:
        adv = generate_dispatch_advisory(
            flight_id=flight_id,
            carrier_code=carrier_code,
            origin=origin,
            dest=dest,
            flight_date=flight_date,
            dep_hour=dep_hour,
            flight_number=flight_number,
            model=model,
            strict_lookup=(flight_id is not None),
        )
        md_content = generate_presentation_markdown(adv.to_dict())
        fl_code = f"{adv.flight_context.carrier_code}{adv.flight_context.flight_number or ''}"
        filename = f"SkyOps_Slide_{fl_code}.md"
        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error generating Markdown slide deck: {str(e)}")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> str:
    """Interactive 3-Tab OCC Copilot & Aviation Regulatory Governance Web UI."""
    return render_homepage()


@app.get("/embed/chat", response_class=HTMLResponse)
def embed_chat(
    page: Optional[str] = Query(None, description="Power BI page index or code (1, 2, 3, 4)"),
    flight_id: Optional[Union[int, str]] = Query(None, description="Selected flight ID"),
    carrier: Optional[str] = Query(None, description="Carrier filter code (e.g. AA, DL, UA)"),
    origin: Optional[str] = Query(None, description="Origin airport code (e.g. DFW, ORD)"),
    dest: Optional[str] = Query(None, description="Destination airport code (e.g. ATL)"),
    theme: Optional[str] = Query(None, description="Theme override ('light' or 'dark')"),
    prompt: Optional[str] = Query(None, description="Initial prompt to trigger automatically"),
    q: Optional[str] = Query(None, description="Alias for initial prompt"),
) -> str:
    """
    Ultra-compact embedded Copilot chat frame designed for seamless integration
    into Power BI Desktop / Service reports (all 4 pages) or standalone compact popups.
    """
    initial_prompt = prompt or q
    return render_embed_chat(
        page=page,
        flight_id=flight_id,
        carrier=carrier,
        origin=origin,
        dest=dest,
        theme=theme,
        prompt=initial_prompt,
    )


class RuntimeModePayload(BaseModel):
    provider: str = Field(..., description="Provider: auto, offline, gemini, claude, openai, deepseek")
    model_name: Optional[str] = Field(None, description="Optional model ID")
    api_key: Optional[str] = Field(None, description="Optional API key from client")
    theme: Optional[str] = Field(None, description="Optional theme: light, dark")


_SERVER_RUNTIME_MODE = {
    "provider": "auto",
    "model_name": None,
    "is_online": False,
    "theme": "light",
    "updated_at": 0,
}


@app.get("/copilot/runtime-mode")
def get_runtime_mode() -> dict:
    """Get active runtime mode and sync state for Copilot across web clients & Power BI embed."""
    has_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    has_claude = bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_deepseek = bool(os.getenv("DEEPSEEK_API_KEY"))
    return {
        **_SERVER_RUNTIME_MODE,
        "server_has_gemini_key": has_gemini,
        "server_has_claude_key": has_claude,
        "server_has_openai_key": has_openai,
        "server_has_deepseek_key": has_deepseek,
    }


@app.post("/copilot/runtime-mode")
def set_runtime_mode(req: RuntimeModePayload) -> dict:
    """Update active runtime mode from Web UI or Power BI embed visual."""
    has_server_llm = bool(
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
        or os.getenv("CLAUDE_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("DEEPSEEK_API_KEY")
    )
    is_online = (
        req.provider in ("gemini", "claude", "openai", "deepseek")
        or bool(req.api_key)
        or (req.provider == "auto" and bool(req.api_key or has_server_llm))
    )
    _SERVER_RUNTIME_MODE["provider"] = req.provider
    if req.model_name is not None:
        _SERVER_RUNTIME_MODE["model_name"] = req.model_name
    _SERVER_RUNTIME_MODE["is_online"] = bool(is_online)
    if req.theme:
        _SERVER_RUNTIME_MODE["theme"] = req.theme
    _SERVER_RUNTIME_MODE["updated_at"] = int(time.time() * 1000)
    return {"status": "ok", "mode": _SERVER_RUNTIME_MODE}




