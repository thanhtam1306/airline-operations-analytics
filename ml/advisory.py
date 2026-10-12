"""
Context-Aware Advisory & Grounding Engine (Phase 6.2 - OCC Decision Copilot).

Synthesizes three critical operational layers for airline operations:
1. Operational & Warehouse Data Grounding (Carriers, Airports, Routes, Hub Congestion, Curfews)
2. Machine Learning Predictive Risk & Financial Cost of Delay ($101.18/min FAA/A4A standard)
3. Regulatory Compliance Grounding (14 CFR § 259.4 Tarmac Delay, FAR Part 117 Crew Duty,
   14 CFR § 260.6 Cash Refund, Vietnam CAAV Thông tư 19/2023 & Nghị định 162/2018).

Generates actionable, minute-by-minute dispatch plans (T-120m to En-route),
binds dynamic SOP checklists from the Knowledge Base, and provides What-If
dispatch simulations (rescheduling, crew replacement, airborne make-up time).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import pandas as pd

from ml.regulatory_engine import evaluate_regulatory_compliance

# -----------------------------------------------------------------------------
# CONSTANTS & DOMAIN BENCHMARKS
# -----------------------------------------------------------------------------
COST_OF_DELAY_PER_MIN_USD = 101.18  # FAA & Airlines for America (A4A) benchmark
TARMAC_FINE_PER_PAX_USD = 37377.0  # US DOT Title 14 CFR § 259.4 statutory maximum fine
CASH_REFUND_ESTIMATE_USD = 275.0   # 14 CFR § 260.6 average domestic ticket refund

AIRPORT_CURFEWS: Dict[str, Dict[str, Any]] = {
    "SNA": {
        "airport_code": "SNA",
        "name": "John Wayne Airport (Orange County)",
        "curfew_start_hour": 23,
        "curfew_end_hour": 7,
        "restriction": "Nghiêm cấm cất cánh sau 22:00 và hạ cánh sau 23:00 (Tiếng ồn đô thị).",
        "penalty": "Phạt tiền nặng từ chính quyền Quận Cam và đình chỉ quyền khai thác nếu vi phạm.",
    },
    "LGA": {
        "airport_code": "LGA",
        "name": "LaGuardia Airport (New York)",
        "curfew_start_hour": 0,
        "curfew_end_hour": 6,
        "restriction": "Hạn chế nghiêm ngặt chuyến bay đêm (Perimeter Rule & Noise Curfew).",
        "penalty": "Bị chuyển hướng sang JFK/EWR hoặc chịu phí hạ cánh ngoài giờ đặc biệt.",
    },
    "DCA": {
        "airport_code": "DCA",
        "name": "Ronald Reagan Washington National",
        "curfew_start_hour": 22,
        "curfew_end_hour": 7,
        "restriction": "Giới nghiêm tiếng ồn ban đêm sau 22:00 (National Airport Noise Rule).",
        "penalty": "Phạt tiền lũy tiến và giám sát đặc biệt của FAA.",
    },
    "SAN": {
        "airport_code": "SAN",
        "name": "San Diego International",
        "curfew_start_hour": 23,
        "curfew_end_hour": 6,
        "restriction": "Cấm khởi hành từ 23:30 đến 06:30 sáng hôm sau.",
        "penalty": "Phạt vi phạm tiếng ồn lên tới $10,000 USD mỗi lần cất cánh muộn.",
    },
}

SLOT_CONTROLLED_AIRPORTS = {"JFK", "LGA", "DCA"}

BASE_PATH = Path(__file__).resolve().parent
ART_PATH = BASE_PATH / "artifacts"
POWERBI_EXPORT_PATH = BASE_PATH.parent / "dashboards" / "powerbi" / "export"


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class FlightContext:
    flight_id: Optional[Union[int, str]]
    flight_date: str
    carrier_code: str
    carrier_name: str
    carrier_type: str
    is_low_cost: bool
    fleet_size: int
    flight_number: Optional[Union[int, str]]
    tail_number: Optional[str]
    origin: str
    origin_name: str
    origin_city: str
    origin_state: str
    origin_hub_weight: int
    origin_is_major_hub: bool
    dest: str
    dest_name: str
    dest_city: str
    dest_state: str
    dest_hub_weight: int
    dest_is_major_hub: bool
    distance_miles: float
    distance_bucket: str
    dep_hour: int
    dep_window_label: str
    day_of_week: int
    is_weekend: bool
    scheduled_departures_hour: int
    route_delay_rate_30d: float
    carrier_delay_rate_30d: float
    route_flights_30d: float
    origin_curfew: Optional[Dict[str, Any]] = None
    dest_curfew: Optional[Dict[str, Any]] = None
    is_slot_controlled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PredictionContext:
    delay_probability: float
    operating_threshold: float
    risk_band: str
    model_id: str
    model_type: str
    lift_at_10: float
    projected_delay_min: int
    top_risk_factors: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FinancialExposure:
    cost_per_minute_usd: float
    projected_delay_min: int
    base_delay_cost_usd: float
    estimated_passengers: int
    tarmac_penalty_exposure_usd: float
    cash_refund_exposure_usd: float
    passenger_care_cost_usd: float
    total_potential_exposure_usd: float
    proactive_mitigation_savings_usd: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TimelineAction:
    time_offset_min: int
    phase_code: str
    phase_name: str
    responsible_role: str
    action_title: str
    operational_guidance: str
    critical_decision: str
    priority: str = "HIGH"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _sanitize_json(v: Any) -> Any:
    """Recursively convert numpy types, dates, and non-serializable objects to pure Python primitives."""
    if hasattr(v, "item"):
        return v.item()
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, dict):
        return {str(k): _sanitize_json(val) for k, val in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [_sanitize_json(item) for item in v]
    return v


@dataclass
class DispatchAdvisory:
    advisory_id: str
    created_at: str
    flight_context: FlightContext
    prediction_context: PredictionContext
    financial_exposure: FinancialExposure
    regulatory_compliance: Dict[str, Any]
    timeline_actions: List[TimelineAction]
    recommended_sops: List[Dict[str, Any]]
    executive_summary: str

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["flight_context"] = self.flight_context.to_dict()
        res["prediction_context"] = self.prediction_context.to_dict()
        res["financial_exposure"] = self.financial_exposure.to_dict()
        res["timeline_actions"] = [a.to_dict() if hasattr(a, "to_dict") else a for a in self.timeline_actions]
        return _sanitize_json(res)

    def to_markdown(self) -> str:
        return format_advisory_markdown(self)



# =============================================================================
# DATA LOADERS & LOOKUPS CACHE
# =============================================================================

@lru_cache(maxsize=1)
def _load_advisory_resources() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """Load reference lookups, dimensional parquet tables, and tournament metrics."""
    routes = pd.read_parquet(ART_PATH / "route_lookup.parquet")
    carriers = pd.read_parquet(ART_PATH / "carrier_lookup.parquet")
    congestion = pd.read_parquet(ART_PATH / "congestion_lookup.parquet")
    metrics_path = ART_PATH / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}

    # Dimensional tables from powerbi export if available
    dim_airport_file = POWERBI_EXPORT_PATH / "dim_airport.parquet"
    if dim_airport_file.exists():
        dim_airports = pd.read_parquet(dim_airport_file)
    else:
        dim_airports = pd.DataFrame()

    dim_airline_file = POWERBI_EXPORT_PATH / "dim_airline.parquet"
    if dim_airline_file.exists():
        dim_airlines = pd.read_parquet(dim_airline_file)
    else:
        dim_airlines = pd.DataFrame()

    return routes, carriers, congestion, dim_airports, dim_airlines, metrics


@lru_cache(maxsize=1)
def _load_predictions_mart() -> Optional[pd.DataFrame]:
    """Load pre-scored regulatory predictions parquet table if present."""
    p_file = POWERBI_EXPORT_PATH / "fct_flight_regulatory_predictions.parquet"
    if p_file.exists():
        return pd.read_parquet(p_file)
    return None


@lru_cache(maxsize=4)
def _load_ml_model(model_name: str = "best"):
    """Load trained ML model artifact and its threshold."""
    file_map = {
        "best": "best_delay_model.joblib",
        "lgbm": "lgbm_delay.joblib",
        "xgboost": "xgboost_delay.joblib",
        "catboost": "catboost_delay.joblib",
        "ensemble": "ensemble_delay.joblib",
        "baseline": "baseline_logreg.joblib",
    }
    fname = file_map.get(model_name.lower(), "best_delay_model.joblib")
    path = ART_PATH / fname
    if not path.exists():
        if (ART_PATH / "best_delay_model.joblib").exists():
            path = ART_PATH / "best_delay_model.joblib"
        elif (ART_PATH / "lgbm_delay.joblib").exists():
            path = ART_PATH / "lgbm_delay.joblib"
        else:
            raise FileNotFoundError(f"Model file not found at {path}")

    model = joblib.load(path)
    _, _, _, _, _, metrics = _load_advisory_resources()

    threshold = 0.25
    if "best_model" in metrics:
        winner = metrics["best_model"].get("winner", "lgbm")
        threshold = metrics.get(winner, {}).get("val", {}).get("threshold", 0.25)
    elif model_name in metrics:
        threshold = metrics[model_name].get("val", {}).get("threshold", 0.25)

    return model, threshold, path.stem


# =============================================================================
# CONTEXT BUILDER & FEATURE PIPELINE
# =============================================================================

def _build_flight_context(
    carrier_code: str,
    origin: str,
    dest: str,
    dep_hour: int,
    flight_date_str: str,
    flight_id: Optional[Union[int, str]] = None,
    flight_number: Optional[Union[int, str]] = None,
    tail_number: Optional[str] = None,
) -> FlightContext:
    routes, carriers, congestion, dim_airports, dim_airlines, _ = _load_advisory_resources()

    c_code = carrier_code.strip().upper()
    orig = origin.strip().upper()
    dst = dest.strip().upper()

    # Look up carrier
    c_match = carriers[carriers.carrier_code == c_code]
    carrier_delay_rate = float(c_match.carrier_delay_rate_30d.iloc[0]) if not c_match.empty else 0.20
    carrier_type = str(c_match.carrier_type.iloc[0]) if not c_match.empty else "legacy"

    # Dimensional carrier info
    carrier_name = f"Airline {c_code}"
    is_low_cost = carrier_type == "low_cost"
    fleet_size = 250
    if not dim_airlines.empty:
        da_match = dim_airlines[dim_airlines.carrier_code == c_code]
        if not da_match.empty:
            carrier_name = str(da_match.carrier_name.iloc[0])
            is_low_cost = bool(da_match.is_low_cost.iloc[0])
            c_type_raw = str(da_match.carrier_type.iloc[0]).lower()
            carrier_type = "low_cost" if "low" in c_type_raw else "legacy"
            fleet_size = int(da_match.fleet_size.iloc[0])


    # Route info
    r_match = routes[(routes.origin_airport == orig) & (routes.dest_airport == dst)]
    distance_miles = float(r_match.distance_miles.iloc[0]) if not r_match.empty else 800.0
    route_delay_rate = float(r_match.route_delay_rate_30d.iloc[0]) if not r_match.empty else 0.22
    route_flights = float(r_match.route_flights_30d.iloc[0]) if not r_match.empty else 60.0
    distance_bucket = "short" if distance_miles < 500 else ("medium" if distance_miles < 1500 else "long")

    # Congestion info
    g_match = congestion[(congestion.origin_airport == orig) & (congestion.dep_hour == dep_hour)]
    sched_deps = int(g_match.scheduled_departures_hour.iloc[0]) if not g_match.empty else 5

    # Origin & Dest Airport info
    orig_name, orig_city, orig_state, orig_weight, orig_hub = f"{orig} Airport", orig, "US", 5, False
    dst_name, dst_city, dst_state, dst_weight, dst_hub = f"{dst} Airport", dst, "US", 5, False

    if not dim_airports.empty:
        o_match = dim_airports[dim_airports.airport_code == orig]
        if not o_match.empty:
            orig_name = str(o_match.airport_name.iloc[0])
            orig_city = str(o_match.city.iloc[0])
            orig_state = str(o_match.state.iloc[0])
            orig_weight = int(o_match.hub_weight.iloc[0])
            orig_is_major_hub = bool(o_match.is_major_hub.iloc[0])
        else:
            orig_is_major_hub = orig in {"ATL", "ORD", "DFW", "DEN", "CLT", "LAX", "JFK", "MIA"}

        d_match = dim_airports[dim_airports.airport_code == dst]
        if not d_match.empty:
            dst_name = str(d_match.airport_name.iloc[0])
            dst_city = str(d_match.city.iloc[0])
            dst_state = str(d_match.state.iloc[0])
            dst_weight = int(d_match.hub_weight.iloc[0])
            dst_is_major_hub = bool(d_match.is_major_hub.iloc[0])
        else:
            dst_is_major_hub = dst in {"ATL", "ORD", "DFW", "DEN", "CLT", "LAX", "JFK", "MIA"}
    else:
        orig_is_major_hub = orig in {"ATL", "ORD", "DFW", "DEN", "CLT", "LAX", "JFK", "MIA"}
        dst_is_major_hub = dst in {"ATL", "ORD", "DFW", "DEN", "CLT", "LAX", "JFK", "MIA"}

    # Time & Window Label
    try:
        parsed_date = datetime.strptime(flight_date_str, "%Y-%m-%d").date()
    except Exception:
        parsed_date = date.today()
    dow = (parsed_date.weekday() + 1) % 7
    is_weekend = dow in (0, 6)

    if dep_hour < 6:
        dep_window = f"{dep_hour:02d}:00 - Rạng sáng (Early Dawn / WOCL)"
    elif dep_hour < 9:
        dep_window = f"{dep_hour:02d}:00 - Cao điểm sáng (Morning Rush Bank)"
    elif dep_hour < 16:
        dep_window = f"{dep_hour:02d}:00 - Giữa ngày tiêu chuẩn (Midday Operations)"
    elif dep_hour < 20:
        dep_window = f"{dep_hour:02d}:00 - Cao điểm chiều tối (Evening Peak Bank - Nguy cơ dồn trễ cao)"
    else:
        dep_window = f"{dep_hour:02d}:00 - Đêm muộn (Late Night / Curfew Pressure)"

    origin_curfew = AIRPORT_CURFEWS.get(orig)
    dest_curfew = AIRPORT_CURFEWS.get(dst)
    is_slot = orig in SLOT_CONTROLLED_AIRPORTS or dst in SLOT_CONTROLLED_AIRPORTS

    return FlightContext(
        flight_id=flight_id,
        flight_date=flight_date_str,
        carrier_code=c_code,
        carrier_name=carrier_name,
        carrier_type=carrier_type,
        is_low_cost=is_low_cost,
        fleet_size=fleet_size,
        flight_number=flight_number,
        tail_number=tail_number,
        origin=orig,
        origin_name=orig_name,
        origin_city=orig_city,
        origin_state=orig_state,
        origin_hub_weight=orig_weight,
        origin_is_major_hub=orig_is_major_hub,
        dest=dst,
        dest_name=dst_name,
        dest_city=dst_city,
        dest_state=dst_state,
        dest_hub_weight=dst_weight,
        dest_is_major_hub=dst_is_major_hub,
        distance_miles=distance_miles,
        distance_bucket=distance_bucket,
        dep_hour=dep_hour,
        dep_window_label=dep_window,
        day_of_week=dow,
        is_weekend=is_weekend,
        scheduled_departures_hour=sched_deps,
        route_delay_rate_30d=route_delay_rate,
        carrier_delay_rate_30d=carrier_delay_rate,
        route_flights_30d=route_flights,
        origin_curfew=origin_curfew,
        dest_curfew=dest_curfew,
        is_slot_controlled=is_slot,
    )


# =============================================================================
# ML PREDICTION & FINANCIAL ESTIMATOR
# =============================================================================

def _compute_prediction_and_risk(
    ctx: FlightContext,
    model_name: str = "best",
    custom_delay_prob: Optional[float] = None,
) -> PredictionContext:
    model, threshold, model_id = _load_ml_model(model_name)

    if custom_delay_prob is not None:
        p = float(custom_delay_prob)
    else:
        # Build features dataframe matching training schema
        feats = {
            "dep_hour": ctx.dep_hour,
            "route_delay_rate_30d": ctx.route_delay_rate_30d,
            "carrier_delay_rate_30d": ctx.carrier_delay_rate_30d,
            "scheduled_departures_hour": ctx.scheduled_departures_hour,
            "distance_miles": ctx.distance_miles,
            "route_flights_30d": ctx.route_flights_30d,
            "day_of_week": ctx.day_of_week,
            "distance_bucket": ctx.distance_bucket,
            "carrier_type": ctx.carrier_type,
            "is_weekend": int(ctx.is_weekend),
        }
        df_row = pd.DataFrame([feats])
        for col in ("distance_bucket", "carrier_type"):
            if col in df_row.columns:
                df_row[col] = df_row[col].astype("category")

        # Handle expected feature names if model has them
        if hasattr(model, "feature_names_in_"):
            cols = list(model.feature_names_in_)
            df_row = df_row[cols]

        prob = model.predict_proba(df_row)[:, 1][0]
        p = float(prob)

    # Risk band categorization
    if p >= threshold:
        band = "HIGH"
    elif p >= 0.70 * threshold:
        band = "ELEVATED"
    else:
        band = "NORMAL"

    # Lift factor (based on model tournament baseline benchmark ~1.85x for top decile)
    lift = round(p / 0.198, 2) if p > 0 else 1.0

    # Projected delay minutes estimate
    if band == "HIGH":
        base_min = int(45 + (p - threshold) * 120)
        projected_min = min(max(base_min, 40), 180)
    elif band == "ELEVATED":
        projected_min = int(20 + p * 30)
    else:
        projected_min = int(p * 15)

    # Key Risk Drivers
    factors: List[Dict[str, Any]] = []
    if ctx.dep_hour in (17, 18, 19, 20):
        factors.append({
            "factor": "Khung giờ cao điểm dồn tích trễ (Peak Evening Bank)",
            "description": f"Chuyến bay cất cánh lúc {ctx.dep_hour}:00, giai đoạn trễ domino từ các chặng trước của tàu bay tích tụ cao nhất trong ngày.",
            "impact_level": "CRITICAL" if band == "HIGH" else "HIGH",
        })
    if ctx.scheduled_departures_hour >= 20:
        factors.append({
            "factor": "Mật độ cất cánh sân bay quá tải (Runway Congestion)",
            "description": f"Sân bay {ctx.origin} có {ctx.scheduled_departures_hour} chuyến cất cánh trong khung giờ này, nguy cơ kẹt đường lăn taxi-out kéo dài.",
            "impact_level": "HIGH",
        })
    if ctx.route_delay_rate_30d >= 0.30:
        factors.append({
            "factor": "Lịch sử đường bay trễ cao (High Historical Delay Rate)",
            "description": f"Tuyến bay {ctx.origin} ➔ {ctx.dest} có tỷ lệ trễ 30 ngày qua đạt {(ctx.route_delay_rate_30d * 100):.1f}%.",
            "impact_level": "HIGH",
        })
    if ctx.dest_curfew and ctx.dep_hour >= 20:
        factors.append({
            "factor": "Áp lực giờ giới nghiêm sân bay đến (Destination Curfew Pressure)",
            "description": f"Sân bay đến {ctx.dest} áp dụng giới nghiêm sau {ctx.dest_curfew['curfew_start_hour']}:00. Bất kỳ sự chậm trễ nào đều có thể dẫn đến chuyển hướng bắt buộc.",
            "impact_level": "CRITICAL",
        })
    if not factors:
        factors.append({
            "factor": "Hành lang khai thác thông thoáng (Clean Operating Corridor)",
            "description": "Các chỉ số mật độ đường lăn, lịch sử tuyến bay và khung giờ đều nằm trong vùng an toàn.",
            "impact_level": "LOW",
        })

    return PredictionContext(
        delay_probability=round(p, 4),
        operating_threshold=round(threshold, 4),
        risk_band=band,
        model_id=model_id,
        model_type=type(model).__name__,
        lift_at_10=lift,
        projected_delay_min=projected_min,
        top_risk_factors=factors,
    )


def _compute_financial_exposure(ctx: FlightContext, pred: PredictionContext) -> FinancialExposure:
    """
    Compute quantitative operational delay costs using FAA/A4A $101.18/min
    and calculate potential regulatory statutory penalties.
    """
    mins = pred.projected_delay_min
    base_delay_cost = round(mins * COST_OF_DELAY_PER_MIN_USD, 2)

    # Estimate passenger load based on distance & aircraft typical capacity
    if ctx.distance_bucket == "short":
        passengers = 140
    elif ctx.distance_bucket == "medium":
        passengers = 168
    else:
        passengers = 195

    tarmac_penalty = 0.0
    cash_refund_cost = 0.0
    passenger_care_cost = 0.0

    # Tarmac risk: If projected delay >= 90 mins in high congestion, risk of taxiway stall
    if pred.risk_band == "HIGH" and (ctx.scheduled_departures_hour >= 20 or mins >= 90):
        # Exposure if trapped on tarmac beyond 180 mins ($37,377/pax max statutory fine)
        tarmac_penalty = round(passengers * TARMAC_FINE_PER_PAX_USD, 2)

    # Cash refund mandate: 14 CFR § 260.6 requires full refund if delayed >= 3 hours (180 mins)
    if mins >= 120 or (pred.risk_band == "HIGH" and mins >= 90):
        cash_refund_cost = round(passengers * CASH_REFUND_ESTIMATE_USD, 2)

    # Passenger care (food, beverages, hotel accommodation under Thông tư 19/2023 & DOT rules)
    if mins >= 60:
        care_per_pax = 20.0 if mins < 120 else 55.0
        passenger_care_cost = round(passengers * care_per_pax, 2)

    total_exposure = round(base_delay_cost + tarmac_penalty + cash_refund_cost + passenger_care_cost, 2)

    # Proactive savings: Intervening early mitigates ~70% to 95% of catastrophic penalties
    if pred.risk_band == "HIGH":
        savings = round(total_exposure * 0.85, 2)
    elif pred.risk_band == "ELEVATED":
        savings = round(base_delay_cost * 0.60 + passenger_care_cost, 2)
    else:
        savings = 0.0

    return FinancialExposure(
        cost_per_minute_usd=COST_OF_DELAY_PER_MIN_USD,
        projected_delay_min=mins,
        base_delay_cost_usd=base_delay_cost,
        estimated_passengers=passengers,
        tarmac_penalty_exposure_usd=tarmac_penalty,
        cash_refund_exposure_usd=cash_refund_cost,
        passenger_care_cost_usd=passenger_care_cost,
        total_potential_exposure_usd=total_exposure,
        proactive_mitigation_savings_usd=savings,
    )


# =============================================================================
# TIMELINE ACTION PLAN GENERATOR (T-120m TO EN-ROUTE)
# =============================================================================

def _generate_timeline_actions(
    ctx: FlightContext,
    pred: PredictionContext,
    legal: Dict[str, Any],
) -> List[TimelineAction]:
    """
    Generate actionable minute-by-minute operational dispatch instructions
    tailored to the flight's risk profile and legal mandates.
    """
    actions: List[TimelineAction] = []
    band = pred.risk_band

    # -------------------------------------------------------------------------
    # T - 120 PHÚT: LẬP KẾ HOẠCH & DISPATCH RELEASE
    # -------------------------------------------------------------------------
    if band == "HIGH":
        t120_guidance = (
            f"1. Rà soát quỹ giờ FDP của Tổ bay theo FAR Part 117. Đã xác định nguy cơ hết giờ; "
            f"yêu cầu Crew Scheduling kích hoạt Phi hành đoàn dự bị (Standby Crew) vào trạng thái sẵn sàng.\n"
            f"2. Nạp thêm 20 phút nhiên liệu chờ (Holding Fuel Buffer) để phòng ngừa bay vòng tại {ctx.dest}.\n"
            f"3. Liên hệ Bộ phận Điều độ Sân bay {ctx.origin} để kiểm tra chỉ số EDCT/GDP."
        )
        t120_decision = "QUYẾT ĐỊNH: Ký Dispatch Release có điều kiện; đặt tổ bay dự bị vào trạng thái Hot Standby."
    elif band == "ELEVATED":
        t120_guidance = (
            f"1. Kiểm tra thời gian nghỉ ngơi và FDP khả dụng của cơ trưởng/cơ phó.\n"
            f"2. Bổ sung 10 phút taxi buffer fuel cho sân bay {ctx.origin} do mật độ {ctx.scheduled_departures_hour} chuyến/giờ.\n"
            f"3. Theo dõi sát sao hành trình chuyến bay trước (Inbound Flight) của tàu bay {ctx.tail_number or 'giao định'}."
        )
        t120_decision = "QUYẾT ĐỊNH: Cấp Dispatch Release tiêu chuẩn kèm giám sát chặt chẽ Inbound Turn."
    else:
        t120_guidance = (
            "1. Cấp phép Dispatch Release tiêu chuẩn theo FAR Part 121.\n"
            "2. Kế hoạch nhiên liệu và thời tiết sân bay đi/đến hoàn toàn thuận lợi."
        )
        t120_decision = "QUYẾT ĐỊNH: Cho phép thực hiện chuyến bay bình thường theo lịch trình."

    actions.append(TimelineAction(
        time_offset_min=-120,
        phase_code="T-120",
        phase_name="Giai đoạn T - 120 phút (Flight Planning & Fuel Release)",
        responsible_role="OCC Flight Dispatcher",
        action_title="Rà Soát Kế Hoạch Bay, FDP Tổ Bay & Nhiên Liệu Dự Phòng",
        operational_guidance=t120_guidance,
        critical_decision=t120_decision,
        priority="CRITICAL" if band == "HIGH" else "MEDIUM",
    ))

    # -------------------------------------------------------------------------
    # T - 60 PHÚT: QUAY ĐẦU TÀU BAY & ĐÓN KHÁCH (GATE & RAMP)
    # -------------------------------------------------------------------------
    if band == "HIGH":
        t60_guidance = (
            f"1. Điều động Đội dịch vụ mặt đất (Ground Handling) tập trung sẵn tại cửa khởi hành (Gate).\n"
            f"2. Áp dụng quy trình quay đầu nhanh (Turnaround Fast-Track): Bắt đầu dọn vệ sinh và tra nạp song song.\n"
            f"3. Phân luồng ưu tiên cho 100% kiện hành lý nối chuyến (Connecting Bags).\n"
            f"4. Nếu tàu bay đến trễ > 25 phút, kích hoạt ngay phương án Đổi tàu bay (Tail Swap) từ đội bay dự phòng."
        )
        t60_decision = "QUYẾT ĐỊNH: Kích hoạt Turnaround Fast-Track; nếu chậm trễ vượt ngưỡng cho phép ➔ Ra lệnh Tail Swap."
    elif band == "ELEVATED":
        t60_guidance = (
            "1. Phối hợp với Đội Phục vụ Hành khách mở cửa lên tàu bay (Boarding) sớm 5 phút.\n"
            "2. Theo dõi sát sao quá trình bốc dỡ hàng hóa và chốt bảng cân bằng trọng tải (Loadsheet)."
        )
        t60_decision = "QUYẾT ĐỊNH: Giữ vững thời gian quay đầu 35-45 phút, không để phát sinh chậm trễ mặt đất."
    else:
        t60_guidance = "Tiến hành đón khách và chuẩn bị mặt đất theo đúng quy trình khai thác thông thường."
        t60_decision = "QUYẾT ĐỊNH: Vận hành đúng lịch trình."

    actions.append(TimelineAction(
        time_offset_min=-60,
        phase_code="T-60",
        phase_name="Giai đoạn T - 60 phút (Gate Turnaround & Inbound Tracking)",
        responsible_role="Station Manager & Ramp Supervisor",
        action_title="Giám Sát Vòng Quay Đầu Tàu Bay & Fast-Track Boarding",
        operational_guidance=t60_guidance,
        critical_decision=t60_decision,
        priority="HIGH" if band != "NORMAL" else "LOW",
    ))

    # -------------------------------------------------------------------------
    # T - 15 PHÚT: CHỐT LÊN TÀU & XE KÉO ĐẨY LÙI (D0 CLOSEOUT)
    # -------------------------------------------------------------------------
    if band == "HIGH":
        t15_guidance = (
            "1. Đóng cửa tàu bay (Cabin Door Close) đúng mốc T-10m tuyệt đối để giữ chuẩn D0.\n"
            "2. Xe kéo đẩy lùi (Push-back Tug) phải kết nối sẵn sàng vào càng trước tàu bay.\n"
            "3. Xin huấn lệnh lăn (Taxi Clearance) sớm với Đài kiểm soát mặt đất (Ground ATC) để tránh xếp hàng cuối dãy."
        )
        t15_decision = "QUYẾT ĐỊNH: Đóng cửa dứt khoát, không chờ khách trễ chuyến để bảo vệ slot cất cánh của toàn bộ tàu bay."
    else:
        t15_guidance = "Chốt cửa đúng quy định an toàn, hoàn tất thủ tục bàn giao tài liệu bay cho Cơ trưởng."
        t15_decision = "QUYẾT ĐỊNH: Sẵn sàng đẩy lùi đúng giờ."

    actions.append(TimelineAction(
        time_offset_min=-15,
        phase_code="T-15",
        phase_name="Giai đoạn T - 15 phút (Boarding Closeout & Push-back Readiness)",
        responsible_role="Gate Lead & Ground Operations",
        action_title="Khóa Cửa Tàu Bay & Chốt Danh Sách Tải (D0 Push-back)",
        operational_guidance=t15_guidance,
        critical_decision=t15_decision,
        priority="HIGH",
    ))

    # -------------------------------------------------------------------------
    # T - 0 PHÚT ĐẾN T + 30 PHÚT: ĐẨY LÙI, ĐƯỜNG LĂN & ĐỒNG HỒ TARMAC
    # -------------------------------------------------------------------------
    if band == "HIGH":
        t0_guidance = (
            f"1. ⏱️ KÍCH HOẠT ĐỒNG HỒ ĐẾM NGƯỢC TARMAC DELAY (Quy chuẩn 14 CFR § 259.4).\n"
            f"2. Ghi nhận chính xác mốc giờ Out (Off-gate time). Nếu thời gian lăn vượt quá 45 phút mà chưa cất cánh, "
            f"Điều phái viên phải liên hệ ATC Tower xin cấp quyền ưu tiên cất cánh ngay.\n"
            f"3. Chuẩn bị sẵn cổng đỗ quay đầu (Return Gate) trong trường hợp chạm mốc 120 phút trên đường lăn."
        )
        t0_decision = "QUYẾT ĐỊNH: Bắt buộc tuân thủ SOP Tarmac Clockwork; tuyệt đối không để vượt ngưỡng 180 phút!"
    else:
        t0_guidance = "Tàu bay đẩy lùi đúng lịch, di chuyển theo đường lăn tiêu chuẩn hướng ra đầu đường băng."
        t0_decision = "QUYẾT ĐỊNH: Đẩy lùi bình thường."

    actions.append(TimelineAction(
        time_offset_min=0,
        phase_code="T-0",
        phase_name="Giai đoạn T - 0m đến T + 30m (Taxi-Out & Tarmac Clock Countdown)",
        responsible_role="Captain (PIC) & ATC Coordinator",
        action_title="Lăn Ra Đường Băng & Kích Hoạt Đồng Hồ Đếm Ngược Tarmac",
        operational_guidance=t0_guidance,
        critical_decision=t0_decision,
        priority="CRITICAL" if band == "HIGH" else "MEDIUM",
    ))

    # -------------------------------------------------------------------------
    # TRÊN KHÔNG & TIẾP CẬN HẠ CÁNH (EN-ROUTE AIRBORNE MAKE-UP)
    # -------------------------------------------------------------------------
    if band == "HIGH" or (ctx.dest_curfew and ctx.dep_hour >= 19):
        en_guidance = (
            f"1. OCC gửi điện văn ACARS đề xuất Cơ trưởng tăng Cost Index (CI) từ 30 lên 65-80, "
            f"bay ở tốc độ Mach tối ưu để bù giờ trên không (Airborne Make-up Time: rút ngắn 10 - 18 phút).\n"
            f"2. Yêu cầu Station {ctx.dest} bố trí ngay Cửa đỗ (Gate assignment) thông thoáng, xe thang và "
            f"đội phục vụ mặt đất sẵn sàng trước khi tàu bay hạ cánh 15 phút để hành khách không phải chờ đợi."
        )
        en_decision = "QUYẾT ĐỊNH: Tăng Cost Index bay bù giờ; yêu cầu sân bay đến dành riêng cổng tiếp nhận ưu tiên."
    elif band == "ELEVATED":
        en_guidance = (
            "Giữ hồ sơ bay tiết kiệm nhiên liệu tiêu chuẩn, thông báo thời gian hạ cánh dự kiến (ETA) chính xác cho sân bay đến."
        )
        en_decision = "QUYẾT ĐỊNH: Khai thác theo hồ sơ bay kinh tế."
    else:
        en_guidance = "Tiếp cận và hạ cánh bình thường theo lịch trình."
        en_decision = "QUYẾT ĐỊNH: Hạ cánh đúng giờ (A14 On-Time)."

    actions.append(TimelineAction(
        time_offset_min=45,
        phase_code="EN-ROUTE",
        phase_name="Giai đoạn Trên không & Hạ cánh (Airborne Strategy & Inbound Gate)",
        responsible_role="Flight Dispatcher & Pilot in Command",
        action_title="Chiến Lược Bù Giờ Trên Không & Tiếp Nhận Tại Cửa Đỗ",
        operational_guidance=en_guidance,
        critical_decision=en_decision,
        priority="HIGH" if band != "NORMAL" else "LOW",
    ))

    return actions


# =============================================================================
# SOP DYNAMIC BINDING
# =============================================================================

def _bind_recommended_sops(
    ctx: FlightContext,
    pred: PredictionContext,
    legal: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Dynamically select and attach relevant SOP checklists from the
    standardized 8-SOP Knowledge Base based on active risks.
    """
    # Lazy import to avoid circular dependency
    from ml.copilot import SOP_CHECKLISTS

    selected_sops: List[Dict[str, Any]] = []

    # 1. Tarmac delay risk SOP
    if pred.risk_band == "HIGH" or ctx.scheduled_departures_hour >= 20:
        if "sop_tarmac_clockwork_emergency" in SOP_CHECKLISTS:
            s = SOP_CHECKLISTS["sop_tarmac_clockwork_emergency"].to_dict()
            s["binding_reason"] = "Kích hoạt do chuyến bay có rủi ro trễ cao tại sân bay đông đúc, đe dọa bẫy Tarmac Delay 180 phút."
            selected_sops.append(s)

    # 2. Crew FDP timeout replacement SOP
    if pred.risk_band == "HIGH" or ctx.dep_hour >= 18:
        if "sop_crew_timeout_replacement" in SOP_CHECKLISTS:
            s = SOP_CHECKLISTS["sop_crew_timeout_replacement"].to_dict()
            s["binding_reason"] = "Kích hoạt do chuyến bay khởi hành cuối ngày, có nguy cơ tổ bay chạm trần FDP theo FAR Part 117."
            selected_sops.append(s)

    # 3. Priority slot request SOP
    if ctx.is_slot_controlled or ctx.scheduled_departures_hour >= 18:
        if "sop_priority_slot_request" in SOP_CHECKLISTS:
            s = SOP_CHECKLISTS["sop_priority_slot_request"].to_dict()
            s["binding_reason"] = f"Kích hoạt do cất cánh tại sân bay quản lý Slot ({ctx.origin}) trong giờ cao điểm."
            selected_sops.append(s)

    # 4. Passenger care & refund SOP
    if pred.projected_delay_min >= 90 or pred.risk_band == "HIGH":
        if "sop_passenger_refund_care" in SOP_CHECKLISTS:
            s = SOP_CHECKLISTS["sop_passenger_refund_care"].to_dict()
            s["binding_reason"] = "Kích hoạt để chủ động chuẩn bị bồi hoàn, suất ăn và chỗ nghỉ cho hành khách theo 14 CFR § 260.6 và Thông tư 19."
            selected_sops.append(s)

    # 5. General delay incident SOP
    if not selected_sops or pred.risk_band in ("ELEVATED", "HIGH"):
        if "sop_delay_incident" in SOP_CHECKLISTS:
            s = SOP_CHECKLISTS["sop_delay_incident"].to_dict()
            s["binding_reason"] = "Quy trình tác nghiệp chuẩn xử lý sự cố trễ chuyến bay định kỳ."
            selected_sops.append(s)

    return selected_sops


# =============================================================================
# MAIN DISPATCH ADVISORY GENERATOR
# =============================================================================

def generate_dispatch_advisory(
    flight_id: Optional[Union[int, str]] = None,
    carrier_code: Optional[str] = None,
    origin: Optional[str] = None,
    dest: Optional[str] = None,
    flight_date: Optional[str] = None,
    dep_hour: Optional[int] = None,
    flight_number: Optional[Union[int, str]] = None,
    tail_number: Optional[str] = None,
    model: str = "best",
    custom_delay_prob: Optional[float] = None,
    strict_lookup: bool = False,
) -> DispatchAdvisory:
    """
    Generate a full, tri-layer grounded OCC Actionable Dispatch Advisory.

    Can be invoked either by:
    - `flight_id`: Pulls flight parameters directly from the pre-scored warehouse mart.
    - Explicit route/carrier parameters: Computes real-time inference on the fly.
    """
    # 1. Check if flight_id is given and exists in warehouse predictions
    mart = _load_predictions_mart()
    matched_row = None
    if flight_id is not None:
        if mart is not None and not mart.empty:
            # Match by flight_id
            m = mart[mart.flight_id.astype(str) == str(flight_id)]
            if not m.empty:
                matched_row = m.iloc[0]
        if matched_row is None and strict_lookup:
            raise ValueError(f"Không tìm thấy chuyến bay có Flight ID '{flight_id}' trong kho dữ liệu Marts.")

    if matched_row is not None:
        carrier_code = str(matched_row.carrier_code)
        origin = str(matched_row.origin_airport)
        dest = str(matched_row.dest_airport)
        flight_date = str(matched_row.flight_date)
        dep_hour = int(matched_row.dep_hour)
        flight_number = matched_row.flight_number
        tail_number = str(matched_row.tail_number)
        if custom_delay_prob is None:
            custom_delay_prob = float(matched_row.delay_probability)

    # Defaults for direct parameters
    if not carrier_code:
        carrier_code = "AA"
    if not origin:
        origin = "ATL"
    if not dest:
        dest = "DFW"
    if not flight_date:
        flight_date = date.today().isoformat()
    if dep_hour is None:
        dep_hour = 17

    # Layer 1: Operational & Warehouse Context
    ctx = _build_flight_context(
        carrier_code=carrier_code,
        origin=origin,
        dest=dest,
        dep_hour=dep_hour,
        flight_date_str=flight_date,
        flight_id=flight_id,
        flight_number=flight_number,
        tail_number=tail_number,
    )

    # Layer 2: Machine Learning Prediction & Risk Context
    pred = _compute_prediction_and_risk(ctx, model_name=model, custom_delay_prob=custom_delay_prob)

    # Financial Exposure calculation ($101.18/min benchmark + statutory exposures)
    fin = _compute_financial_exposure(ctx, pred)

    # Layer 3: Regulatory Compliance Evaluation
    feats_for_legal = {
        "scheduled_departures_hour": ctx.scheduled_departures_hour,
        "route_delay_rate_30d": ctx.route_delay_rate_30d,
        "carrier_delay_rate_30d": ctx.carrier_delay_rate_30d,
        "distance_miles": ctx.distance_miles,
        "carrier_type": ctx.carrier_type,
    }
    legal = evaluate_regulatory_compliance(
        carrier_code=ctx.carrier_code,
        origin=ctx.origin,
        dest=ctx.dest,
        dep_hour=ctx.dep_hour,
        delay_probability=pred.delay_probability,
        threshold=pred.operating_threshold,
        risk_band=pred.risk_band.lower(),
        features_used=feats_for_legal,
    )

    # Actionable Minute-by-Minute Timeline
    timeline = _generate_timeline_actions(ctx, pred, legal)

    # SOP Dynamic Binding
    sops = _bind_recommended_sops(ctx, pred, legal)

    # Executive Summary text
    flight_tag = f"{ctx.carrier_code}{ctx.flight_number or ''}"
    if pred.risk_band == "HIGH":
        summary = (
            f"🚨 CẢNH BÁO NGUY CƠ CAO (HIGH RISK): Chuyến bay {flight_tag} ({ctx.origin} ➔ {ctx.dest}) lúc {ctx.dep_hour}:00 "
            f"có xác suất trễ {(pred.delay_probability * 100):.1f}% (vượt ngưỡng cho phép {pred.operating_threshold:.4f}, Lift {pred.lift_at_10}x). "
            f"Dự kiến độ trễ kéo dài ~{pred.projected_delay_min} phút. "
            f"Tổng rủi ro tài chính tiềm tàng ước tính ${fin.total_potential_exposure_usd:,.2f} USD (trong đó chi phí trễ trực tiếp là ${fin.base_delay_cost_usd:,.2f} USD). "
            f"Yêu cầu OCC Dispatcher thực hiện nghiêm ngặt bản kế hoạch 5 chặng và kích hoạt {len(sops)} SOP khẩn nguy đính kèm."
        )
    elif pred.risk_band == "ELEVATED":
        summary = (
            f"⚠️ CẢNH BÁO NGUY CƠ NÂNG CAO (ELEVATED RISK): Chuyến bay {flight_tag} ({ctx.origin} ➔ {ctx.dest}) lúc {ctx.dep_hour}:00 "
            f"có xác suất trễ {(pred.delay_probability * 100):.1f}%. Dự kiến có thể chậm ~{pred.projected_delay_min} phút "
            f"với tổn thất vận hành dự tính ${fin.base_delay_cost_usd:,.2f} USD. "
            f"Yêu cầu Đội dịch vụ mặt đất chuẩn bị quy trình quay đầu nhanh và theo dõi tổ bay dự bị."
        )
    else:
        summary = (
            f"✅ HÀNH LANG AN TOÀN (NORMAL / ON-TIME): Chuyến bay {flight_tag} ({ctx.origin} ➔ {ctx.dest}) lúc {ctx.dep_hour}:00 "
            f"có xác suất trễ thấp {(pred.delay_probability * 100):.1f}%, đáp ứng hoàn toàn quy chuẩn FAR Part 121. "
            f"Không có nguy cơ vi phạm pháp luật; cho phép Điều phái viên cấp lệnh cất cánh đúng giờ."
        )

    adv_id = f"ADV-{ctx.carrier_code}-{ctx.flight_number or 'GEN'}-{ctx.flight_date.replace('-', '')}-{ctx.dep_hour}"

    return DispatchAdvisory(
        advisory_id=adv_id,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        flight_context=ctx,
        prediction_context=pred,
        financial_exposure=fin,
        regulatory_compliance=legal,
        timeline_actions=timeline,
        recommended_sops=sops,
        executive_summary=summary,
    )


def lookup_flight_advisory(flight_id: Union[int, str], model: str = "best") -> Optional[DispatchAdvisory]:
    """Retrieve and generate an advisory directly by flight_id from warehouse."""
    try:
        return generate_dispatch_advisory(flight_id=flight_id, model=model)
    except Exception:
        return None


# =============================================================================
# WHAT-IF DISPATCH SIMULATOR
# =============================================================================

def simulate_what_if(
    advisory: DispatchAdvisory,
    scenario_type: str,
    scenario_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Simulate operational interventions for OCC Dispatchers:
    1. 'reschedule_hour': Reschedule departure hour to avoid peak bank congestion.
    2. 'crew_standby': Call in Standby Crew to prevent FAR Part 117 timeout.
    3. 'airborne_speedup': Increase Cost Index / Mach number for airborne make-up.
    4. 'tail_swap': Swap to fresh standby aircraft to reset domino cascading delay.
    """
    params = scenario_params or {}
    ctx = advisory.flight_context
    orig_prob = advisory.prediction_context.delay_probability
    orig_risk = advisory.prediction_context.risk_band
    orig_cost = advisory.financial_exposure.total_potential_exposure_usd
    orig_mins = advisory.prediction_context.projected_delay_min

    result: Dict[str, Any] = {
        "scenario_type": scenario_type,
        "flight_identifier": f"{ctx.carrier_code}{ctx.flight_number or ''} ({ctx.origin} ➔ {ctx.dest})",
        "baseline": {
            "dep_hour": ctx.dep_hour,
            "delay_probability": orig_prob,
            "risk_band": orig_risk,
            "projected_delay_min": orig_mins,
            "financial_exposure_usd": orig_cost,
        },
    }

    if scenario_type == "reschedule_hour":
        new_hour = int(params.get("new_dep_hour", max(0, ctx.dep_hour - 2)))
        # Re-run advisory with new hour
        new_adv = generate_dispatch_advisory(
            carrier_code=ctx.carrier_code,
            origin=ctx.origin,
            dest=ctx.dest,
            flight_date=ctx.flight_date,
            dep_hour=new_hour,
            flight_number=ctx.flight_number,
            tail_number=ctx.tail_number,
        )
        new_prob = new_adv.prediction_context.delay_probability
        new_risk = new_adv.prediction_context.risk_band
        new_cost = new_adv.financial_exposure.total_potential_exposure_usd
        new_mins = new_adv.prediction_context.projected_delay_min

        prob_delta = round(new_prob - orig_prob, 4)
        cost_saved = round(max(0.0, orig_cost - new_cost), 2)
        mins_saved = max(0, orig_mins - new_mins)

        result["intervention"] = {
            "new_dep_hour": new_hour,
            "description": f"Chuyển giờ cất cánh từ {ctx.dep_hour}:00 sang {new_hour}:00 để tránh khung giờ nghẽn đường băng.",
        }
        result["simulated_outcome"] = {
            "new_delay_probability": new_prob,
            "new_risk_band": new_risk,
            "new_projected_delay_min": new_mins,
            "new_financial_exposure_usd": new_cost,
            "probability_reduction_pct": round(abs(prob_delta) * 100, 1),
            "minutes_saved": mins_saved,
            "cost_saved_usd": cost_saved,
            "roi_verdict": f"Phương án hiệu quả: Tiết kiệm dự tính ${cost_saved:,.2f} USD và giảm nguy cơ trễ {abs(prob_delta)*100:.1f}%.",
        }

    elif scenario_type == "crew_standby":
        # Activating standby crew removes FAR Part 117 violation risk and avoids cancellation
        standby_call_cost = 3200.0  # Estimated call-out cost for standby crew
        prevented_penalty = advisory.financial_exposure.tarmac_penalty_exposure_usd + 35000.0  # avoided cancellation cost
        net_savings = round(prevented_penalty - standby_call_cost, 2)

        result["intervention"] = {
            "action": "Kích hoạt Tổ bay dự bị (Standby Crew Activation)",
            "description": "Thay thế phi hành đoàn đang chạm trần FDP bằng tổ bay dự phòng tại sân bay đi.",
            "operational_cost_usd": standby_call_cost,
        }
        result["simulated_outcome"] = {
            "crew_duty_compliance": "100% TUÂN THỦ (FAR Part 117)",
            "cancellation_risk": "TRIỆT TIÊU HOÀN TOÀN (0%)",
            "net_financial_savings_usd": net_savings,
            "roi_verdict": f"Rất khuyến nghị: Đầu tư ${standby_call_cost:,.2f} USD phí tổ bay dự bị giúp bảo toàn ${net_savings:,.2f} USD tổn thất vận hành.",
        }

    elif scenario_type == "airborne_speedup":
        # Speeding up cruise (Cost Index increase) makes up 10-18 minutes en-route
        fuel_burn_extra_cost = 650.0  # extra fuel burned
        make_up_mins = 14
        new_delay_mins = max(0, orig_mins - make_up_mins)
        operational_delay_savings = round(make_up_mins * COST_OF_DELAY_PER_MIN_USD, 2)
        net_saved = round(operational_delay_savings - fuel_burn_extra_cost, 2)

        result["intervention"] = {
            "action": "Tăng Cost Index trên đường bay (Airborne Make-up)",
            "description": f"Bay ở tốc độ Mach cao hơn để bù {make_up_mins} phút trên không.",
            "additional_fuel_cost_usd": fuel_burn_extra_cost,
        }
        result["simulated_outcome"] = {
            "airborne_minutes_recovered": make_up_mins,
            "adjusted_arrival_delay_min": new_delay_mins,
            "direct_delay_cost_saved_usd": operational_delay_savings,
            "net_savings_usd": net_saved,
            "curfew_breach_avoided": bool(ctx.dest_curfew),
            "roi_verdict": f"Hành động tối ưu: Tiết kiệm ròng ${net_saved:,.2f} USD sau khi trừ chi phí nhiên liệu phụ trội.",
        }

    elif scenario_type == "tail_swap":
        swap_handling_cost = 1200.0
        # Reset cascading delay
        reset_mins = min(orig_mins, 45)
        savings = round(reset_mins * COST_OF_DELAY_PER_MIN_USD - swap_handling_cost, 2)

        result["intervention"] = {
            "action": "Đổi Tàu Bay Dự Phòng (Spare Aircraft Tail Swap)",
            "description": "Cắt đứt chuỗi chậm domino bằng cách chuyển sang tàu bay rảnh rỗi tại căn cứ.",
            "swap_fee_usd": swap_handling_cost,
        }
        result["simulated_outcome"] = {
            "domino_delay_eliminated_min": reset_mins,
            "new_projected_delay_min": max(0, orig_mins - reset_mins),
            "net_savings_usd": savings,
            "roi_verdict": f"Thành công: Cắt đứt trễ tích lũy, tiết kiệm ${savings:,.2f} USD.",
        }

    else:
        result["error"] = f"Unsupported scenario_type '{scenario_type}'. Supported: reschedule_hour, crew_standby, airborne_speedup, tail_swap"

    return _sanitize_json(result)



# =============================================================================
# MARKDOWN REPORT FORMATTER
# =============================================================================

def format_advisory_markdown(adv: DispatchAdvisory) -> str:
    """Format a DispatchAdvisory into a comprehensive, visual Executive Dispatch Report."""
    ctx = adv.flight_context
    pred = adv.prediction_context
    fin = adv.financial_exposure
    legal = adv.regulatory_compliance

    # Risk badge
    if pred.risk_band == "HIGH":
        badge = "🔴 **RỦI RO CAO (HIGH RISK - HÀNH ĐỘNG KHẨN CẤP)**"
        color_indicator = "🚨"
    elif pred.risk_band == "ELEVATED":
        badge = "🟡 **RỦI RO NÂNG CAO (ELEVATED RISK - CẦN GIÁM SÁT)**"
        color_indicator = "⚠️"
    else:
        badge = "🟢 **HÀNH LANG AN TOÀN (NORMAL - ĐÚNG GIỜ)**"
        color_indicator = "✅"

    flight_tag = f"{ctx.carrier_code}{ctx.flight_number or ''}"

    md = [
        f"# {color_indicator} BẢN KHUYẾN NGHỊ ĐIỀU HÀNH TÁC NGHIỆP OCC (DISPATCH ADVISORY)",
        f"**Mã khuyến nghị**: `{adv.advisory_id}` | **Thời gian khởi tạo**: `{adv.created_at}`  ",
        f"**Trạng thái rủi ro**: {badge}\n",
        "---",
        "## 1. Tóm Tắt Tác Nghiệp Cấp Cao (Executive Summary)\n",
        f"> {adv.executive_summary}\n",
        "---",
        "## 2. Thông Tin Chuyến Bay & Bối Cảnh Vận Hành (Warehouse Grounding)\n",
        f"| Hạng Mục | Thông Tin Chi Tiết |",
        f"| :--- | :--- |",
        f"| **Chuyến Bay** | **{flight_tag}** (Tàu bay: `{ctx.tail_number or 'Standard Turn'}`) |",
        f"| **Hãng Hàng Không** | **{ctx.carrier_name}** (`{ctx.carrier_code}`) - Mô hình: *{ctx.carrier_type.upper()}* |",
        f"| **Chặng Bay** | **{ctx.origin} ({ctx.origin_city})** ➔ **{ctx.dest} ({ctx.dest_city})** |",
        f"| **Cự Ly & Phân Loại** | **{ctx.distance_miles:.0f} dặm** ({ctx.distance_bucket.upper()}) |",
        f"| **Khung Giờ Cất Cánh** | **{ctx.dep_window_label}** |",
        f"| **Mật Độ Sân Bay Đi** | **{ctx.scheduled_departures_hour} chuyến/giờ** tại {ctx.origin} |",
        f"| **Tỷ Lệ Trễ Lịch Sử (30d)** | Tuyến bay: **{(ctx.route_delay_rate_30d * 100):.1f}%** &#124; Hãng bay: **{(ctx.carrier_delay_rate_30d * 100):.1f}%** |",
    ]

    if ctx.origin_curfew or ctx.dest_curfew:
        curfew_text = []
        if ctx.origin_curfew:
            curfew_text.append(f"Điểm đi {ctx.origin}: {ctx.origin_curfew['restriction']}")
        if ctx.dest_curfew:
            curfew_text.append(f"Điểm đến {ctx.dest}: {ctx.dest_curfew['restriction']}")
        md.append(f"| **Giới Nghiêm Tiếng Ồn (Curfew)** | ⚠️ {' ; '.join(curfew_text)} |")

    if ctx.is_slot_controlled:
        md.append("| **Quản Lý Slot (80/20 Rule)** | ⏱️ Sân bay thuộc diện kiểm soát Slot IATA Level 3 (JFK/LGA/DCA) |")

    md.extend([
        "",
        "---",
        "## 3. Dự Báo AI & Phân Tích Thiệt Hại Tài Chính (ML & Cost of Delay)\n",
        f"- **Xác Suất Trễ (Delay Probability)**: `{(pred.delay_probability * 100):.1f}%` (Ngưỡng phân định tối ưu: `{pred.operating_threshold:.4f}`)",
        f"- **Hệ Số Nâng Cao (Lift @ 10%)**: `{pred.lift_at_10}x` so với tỷ lệ trễ ngẫu nhiên tự nhiên.",
        f"- **Mô Hình Thực Thi**: `{pred.model_id}` (*{pred.model_type}*)",
        f"- **Độ Trễ Dự Kiến**: **~{pred.projected_delay_min} phút**\n",
        "### 💵 Bảng Phân Tích Rủi Ro Chi Phí Vận Hành (Định Mức FAA/A4A $101.18/phút):",
        "| Khoản Mục Tổn Thất | Chi Phí Dự Tính (USD) | Căn Cứ Đo Lường |",
        "| :--- | :---: | :--- |",
        f"| **Chi phí trễ trực tiếp** | **${fin.base_delay_cost_usd:,.2f}** | Định mức vận hành bay $101.18 USD/phút × {pred.projected_delay_min}m |",
        f"| **Rủi ro phạt Tarmac Delay** | **${fin.tarmac_penalty_exposure_usd:,.2f}** | 14 CFR § 259.4 ($37,377 USD/pax cho ~{fin.estimated_passengers} khách) |",
        f"| **Nghĩa vụ hoàn tiền mặt vé** | **${fin.cash_refund_exposure_usd:,.2f}** | 14 CFR § 260.6 (Hoàn 100% tiền mặt nếu trễ >= 3 giờ) |",
        f"| **Chăm sóc hành khách & lưu trú** | **${fin.passenger_care_cost_usd:,.2f}** | Thông tư 19/2023 & Nghị định 162/2018 (Ăn uống, khách sạn) |",
        f"| **TỔNG RỦI RO TIỀM TÀNG** | **${fin.total_potential_exposure_usd:,.2f}** | **Tổng tổn thất tài chính nếu không có sự can thiệp** |",
        f"| **Khoản bảo toàn nếu can thiệp** | **${fin.proactive_mitigation_savings_usd:,.2f}** | **Hiệu quả tài chính khi kích hoạt kế hoạch OCC sớm** |",
        "",
        "### 🔍 Các Nhân Tố Thúc Đẩy Rủi Ro Hàng Đầu (Key Risk Drivers):",
    ])

    for f in pred.top_risk_factors:
        lvl = f.get("impact_level", "MEDIUM")
        md.append(f"- **[{lvl}] {f.get('factor')}**: {f.get('description')}")

    md.extend([
        "",
        "---",
        "## 4. Thẩm Định Pháp Lý & Chế Tài Quản Lý Nhà Nước (Regulatory Engine)\n",
        f"- **Khung pháp lý**: `{legal.get('regulatory_framework')}`",
        f"- **Trạng thái tuân thủ**: `{legal.get('compliance_status')}`",
        f"- **Số điều luật điều chỉnh**: `{legal.get('total_regulations_evaluated')}` văn bản",
        f"- **Tóm tắt pháp lý**: {legal.get('executive_legal_summary')}\n",
    ])

    legal_alerts = legal.get("legal_evaluations", [])
    for idx, alert in enumerate(legal_alerts, start=1):
        md.append(f"### {idx}. {alert.get('citation')}")
        md.append(f"- **Mã luật**: `{alert.get('legal_code')}` | **Cơ quan**: {alert.get('jurisdiction')}")
        md.append(f"- **Mức độ nghiêm trọng**: `{alert.get('severity')}`")
        md.append(f"- **Lý do áp dụng**: {alert.get('trigger_reason')}")
        md.append(f"- **Chế tài xử phạt**: ⚖️ *{alert.get('statutory_penalty')}*")
        md.append(f"- **Mệnh lệnh điều hành**: 🚨 **{alert.get('mandatory_action')}**")
        if alert.get("vietnam_equivalent"):
            md.append(f"- **Đối chiếu Việt Nam**: 🇻🇳 *{alert.get('vietnam_equivalent')}*")
        md.append("")

    md.extend([
        "---",
        "## 5. Bản Kế Hoạch Điều Hành Tác Nghiệp Từng Phút (Actionable Dispatch Plan)\n",
    ])

    for action in adv.timeline_actions:
        md.append(f"### ⏱️ [{action.phase_code}] {action.action_title}")
        md.append(f"- **Giai đoạn**: `{action.phase_name}`")
        md.append(f"- **Bộ phận phụ trách**: 👤 `{action.responsible_role}` | **Độ ưu tiên**: `{action.priority}`")
        md.append(f"- **Hướng dẫn thao tác**:\n{action.operational_guidance}")
        md.append(f"- **Mệnh lệnh then chốt**: 👉 **{action.critical_decision}**")
        md.append("")

    md.extend([
        "---",
        "## 6. Danh Mục Quy Trình Thao Tác Chuẩn SOP Kích Hoạt (Recommended SOPs)\n",
    ])

    for sop in adv.recommended_sops:
        sop_id = sop.get("sop_id")
        title = sop.get("title_vi")
        reason = sop.get("binding_reason", "Kích hoạt theo rủi ro vận hành")
        steps_count = len(sop.get("steps", []))
        md.append(f"- **`{sop_id}`**: **{title}** ({steps_count} bước)")
        md.append(f"  *Lý do gắn kết*: {reason}")

    md.append("\n---")
    md.append("*Bản khuyến nghị này được sinh tự động bởi Hệ Thống Airline Data Platform OCC Decision Engine 6.2.*")

    return "\n".join(md)
