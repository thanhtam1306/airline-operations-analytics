"""
Executive Slide Generator for SkyOps Platform.
Generates clean, bright, highly-readable 16:9 PowerPoint presentations (.pptx),
standalone interactive HTML slide decks, and Marp-ready Markdown presentations.

Design Standards (Enterprise Operational UI/UX):
- Clean Light Theme: Crisp white/off-white backgrounds, deep corporate navy headings, high contrast.
- Zero AI Hype: Strictly professional aviation operations vocabulary (No 'AI', 'Machine Learning', or 'Robots').
- High Legibility: Optimized typography and spacing for boardroom presentations and direct printing.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pptx
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


# -----------------------------------------------------------------------------
# PALETTE CONSTANTS — CLEAN, BRIGHT EXECUTIVE LIGHT THEME
# -----------------------------------------------------------------------------
BG_WHITE = RGBColor(255, 255, 255)         # Pure Crisp White
BG_LIGHT_SLATE = RGBColor(248, 250, 252)   # #f8fafc Light Neutral
CARD_BG = RGBColor(248, 250, 252)          # #f8fafc Soft Card Surface
CARD_BORDER = RGBColor(226, 232, 240)      # #e2e8f0 Clean Subtle Border
CARD_WHITE = RGBColor(255, 255, 255)       # #ffffff Card

PRIMARY_NAVY = RGBColor(15, 23, 42)        # #0f172a Deep Corporate Navy (Headings)
TEXT_DARK = RGBColor(30, 41, 59)           # #1e293b Main High-Contrast Text
TEXT_BODY = RGBColor(51, 65, 85)           # #334155 Body Text (Easy reading)
TEXT_MUTED = RGBColor(100, 116, 139)       # #64748b Secondary Labels & Subtitles

AVIATION_BLUE = RGBColor(2, 132, 199)      # #0284c7 Primary Operational Accent
EMERALD_GREEN = RGBColor(5, 150, 105)      # #059669 Normal / Compliance
AMBER_WARNING = RGBColor(217, 119, 6)      # #d97706 Elevated / Caution
ROSE_ALERT = RGBColor(220, 38, 38)         # #dc2626 Critical / High Exposure


def _add_slide_header(
    slide: Any,
    category: str,
    title: str,
    flight_tag: str,
    page_num: int,
    total_pages: int = 5,
) -> None:
    """Adds a standardized clean corporate header to content slides."""
    # Top accent bar in Aviation Blue
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = AVIATION_BLUE
    bar.line.fill.background()

    # Header text block
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(9.5), Inches(0.95))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_cat = tf.paragraphs[0]
    p_cat.text = f"SKYOPS PLATFORM  |  {category.upper()}"
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = AVIATION_BLUE

    p_title = tf.add_paragraph()
    p_title.text = title
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = PRIMARY_NAVY
    p_title.space_before = Pt(3)

    # Top right flight badge & page indicator
    tb_meta = slide.shapes.add_textbox(Inches(10.5), Inches(0.4), Inches(2.033), Inches(0.95))
    tf_meta = tb_meta.text_frame
    tf_meta.word_wrap = True
    tf_meta.margin_left = tf_meta.margin_top = tf_meta.margin_right = tf_meta.margin_bottom = 0

    p_flight = tf_meta.paragraphs[0]
    p_flight.alignment = PP_ALIGN.RIGHT
    p_flight.text = flight_tag
    p_flight.font.size = Pt(11)
    p_flight.font.bold = True
    p_flight.font.color.rgb = PRIMARY_NAVY

    p_page = tf_meta.add_paragraph()
    p_page.alignment = PP_ALIGN.RIGHT
    p_page.text = f"Trang {page_num} / {total_pages}"
    p_page.font.size = Pt(10)
    p_page.font.color.rgb = TEXT_MUTED
    p_page.space_before = Pt(3)


def _add_card_shape(
    slide: Any,
    left: float,
    top: float,
    width: float,
    height: float,
    bg_color: RGBColor = CARD_BG,
    border_color: RGBColor = CARD_BORDER,
) -> Any:
    """Creates a clean rounded rectangle card for information grouping."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)
    return card


def generate_presentation_pptx(adv: Dict[str, Any], output_path: Optional[Union[Path, str]] = None) -> bytes:
    """
    Builds a professional, bright, executive-ready 16:9 PowerPoint presentation (.pptx).
    Returns binary bytes and optionally writes to output_path.
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    ctx = adv.get("flight_context", {})
    pred = adv.get("prediction_context", {})
    fin = adv.get("financial_exposure", {})
    reg = adv.get("regulatory_compliance", {})
    
    carrier = ctx.get("carrier_code", "AA")
    fl_no = ctx.get("flight_number") or ""
    carrier_name = ctx.get("carrier_name", "Hãng Hàng Không")
    origin = ctx.get("origin", "ATL")
    dest = ctx.get("dest", "DFW")
    origin_name = ctx.get("origin_name", origin)
    dest_name = ctx.get("dest_name", dest)
    flight_date = ctx.get("flight_date", "2025-02-14")
    dep_window = ctx.get("dep_window_label", "17:00 - 18:00")
    distance = ctx.get("distance_miles", 0)
    dist_bucket = ctx.get("distance_bucket", "MEDIUM").upper()

    prob = pred.get("delay_probability", 0.0)
    prob_pct = f"{prob * 100:.1f}%"
    risk_band = pred.get("risk_band", "normal").upper()
    proj_delay = pred.get("projected_delay_min", 0)
    lift = pred.get("lift_at_10", 1.0)
    
    cost_base = fin.get("base_delay_cost_usd", 0.0)
    cost_tarmac = fin.get("tarmac_penalty_exposure_usd", 0.0)
    cost_refund = fin.get("cash_refund_exposure_usd", 0.0)
    total_exposure = fin.get("total_potential_exposure_usd", cost_base + cost_tarmac + cost_refund)
    savings = fin.get("proactive_mitigation_savings_usd", 0.0)

    leg_evals = reg.get("legal_evaluations", [])
    top_leg = leg_evals[0] if leg_evals else {}
    best_action = adv.get("best_contingency_action", "Điều chỉnh khung giờ khởi hành hoặc kích hoạt Standby Crew")
    flight_tag = f"{carrier}{fl_no}  |  {origin} ➔ {dest}"

    # Determine risk badge color
    badge_color = ROSE_ALERT if risk_band in ("HIGH", "CRITICAL") else AMBER_WARNING if risk_band == "ELEVATED" else EMERALD_GREEN

    # =========================================================================
    # SLIDE 1: EXECUTIVE COVER & FLIGHT PROFILE (BRIGHT LIGHT THEME)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = BG_WHITE
    bg1.line.fill.background()

    # Top accent bar
    bar1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.1))
    bar1.fill.solid()
    bar1.fill.fore_color.rgb = AVIATION_BLUE
    bar1.line.fill.background()

    # Platform tag
    tb1_top = s1.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.35))
    tf1_top = tb1_top.text_frame
    p = tf1_top.paragraphs[0]
    p.text = "SKYOPS PLATFORM  |  BÁO CÁO TÁC NGHIỆP VẬN HÀNH & PHÁP CHẾ"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = AVIATION_BLUE

    # Title & Route
    tb1_title = s1.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(1.35))
    tf1_title = tb1_title.text_frame
    tf1_title.word_wrap = True
    p_t = tf1_title.paragraphs[0]
    p_t.text = f"Hồ Sơ Giám Sát Chuyến Bay: {carrier}{fl_no} ({origin} ➔ {dest})"
    p_t.font.size = Pt(26)
    p_t.font.bold = True
    p_t.font.color.rgb = PRIMARY_NAVY

    p_sub = tf1_title.add_paragraph()
    p_sub.text = f"Hãng: {carrier_name} ({carrier})  |  Chặng: {origin} ({origin_name}) ➔ {dest} ({dest_name})  |  Ngày bay: {flight_date} ({dep_window})"
    p_sub.font.size = Pt(12)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.space_before = Pt(5)

    # 4 Executive KPI Callout Cards (Light Soft Grey background with crisp borders)
    kpi_defs = [
        ("XÁC SUẤT CHẬM TRỄ", prob_pct, f"Phân hạng: {risk_band}", badge_color),
        ("ĐỘ TRỄ DỰ PHÓNG", f"~{proj_delay} phút", f"Hệ số Risk Lift: {lift:.2f}x", AVIATION_BLUE),
        ("RỦI RO THIỆT HẠI", f"${total_exposure:,.0f}", f"Định mức FAA $101.18/phút", AMBER_WARNING),
        ("TIẾT KIỆM CAN THIỆP", f"${savings:,.0f}", "Bảo toàn dòng tiền ròng", EMERALD_GREEN),
    ]

    card_w, card_h = 2.75, 1.45
    card_gap = 0.233
    start_x = 0.8
    y_kpis = 2.45

    for idx, (label, val, sub, accent) in enumerate(kpi_defs):
        x = start_x + idx * (card_w + card_gap)
        _add_card_shape(s1, x, y_kpis, card_w, card_h, CARD_BG, CARD_BORDER)
        tb_kpi = s1.shapes.add_textbox(Inches(x + 0.15), Inches(y_kpis + 0.12), Inches(card_w - 0.3), Inches(card_h - 0.24))
        tf_kpi = tb_kpi.text_frame
        tf_kpi.word_wrap = True
        
        p_lbl = tf_kpi.paragraphs[0]
        p_lbl.text = label
        p_lbl.font.size = Pt(9.5)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = TEXT_MUTED

        p_val = tf_kpi.add_paragraph()
        p_val.text = val
        p_val.font.size = Pt(22)
        p_val.font.bold = True
        p_val.font.color.rgb = accent
        p_val.space_before = Pt(2)

        p_subk = tf_kpi.add_paragraph()
        p_subk.text = sub
        p_subk.font.size = Pt(9.5)
        p_subk.font.color.rgb = TEXT_BODY
        p_subk.space_before = Pt(2)

    # Executive Summary Card
    y_sum = 4.15
    w_sum = 11.733
    h_sum = 2.75
    _add_card_shape(s1, start_x, y_sum, w_sum, h_sum, CARD_WHITE, CARD_BORDER)
    tb_sum = s1.shapes.add_textbox(Inches(start_x + 0.25), Inches(y_sum + 0.2), Inches(w_sum - 0.5), Inches(h_sum - 0.4))
    tf_sum = tb_sum.text_frame
    tf_sum.word_wrap = True

    p_sh = tf_sum.paragraphs[0]
    p_sh.text = "TỔNG HỢP NHẬN ĐỊNH ĐIỀU HÀNH (EXECUTIVE DISPATCH BRIEFING):"
    p_sh.font.size = Pt(11)
    p_sh.font.bold = True
    p_sh.font.color.rgb = AVIATION_BLUE

    bullets = [
        f"Đánh giá rủi ro khởi hành: Hệ thống ghi nhận mức độ rủi ro {risk_band} với xác suất chậm trễ đạt {prob_pct}, dự báo độ trễ phát sinh ~{proj_delay} phút.",
        f"Bối cảnh tuyến bay & sân bay: Cự ly {distance:,.0f} dặm ({dist_bucket}). Khung giờ khởi hành {dep_window} có mật độ cất cánh {ctx.get('scheduled_departures_hour', 0)} chuyến/giờ tại {origin}.",
        f"Tuân thủ quy chuẩn & Pháp lý: Đang chịu sự điều chỉnh của {top_leg.get('legal_code', '14 CFR § 259.4')} ({top_leg.get('citation', 'Tarmac Delay Rule')}). Chế tài ước tính: {top_leg.get('statutory_penalty', 'N/A')}.",
        f"Khuyến nghị can thiệp OCC: {best_action}. Ước tính bảo toàn ròng ${savings:,.0f} USD so với kịch bản vận hành bị động.",
    ]
    for b in bullets:
        p_b = tf_sum.add_paragraph()
        p_b.text = f"•  {b}"
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = TEXT_BODY
        p_b.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: ROOT CAUSES & NETWORK BOTTLENECKS (NO AI HYPE)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    bg2 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg2.fill.solid()
    bg2.fill.fore_color.rgb = BG_WHITE
    bg2.line.fill.background()
    _add_slide_header(s2, "Phân Tích Căn Nguyên & Điểm Nghẽn", "Chẩn Đoán Rủi Ro Khởi Hành & Điểm Nghẽn Mạng Lưới", flight_tag, 2)

    # Left Column: Operational Metrics & Reliability (width 4.2 in)
    _add_card_shape(s2, 0.8, 1.5, 4.2, 5.4, CARD_BG, CARD_BORDER)
    tb_s2_left = s2.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(3.8), Inches(5.0))
    tf2_l = tb_s2_left.text_frame
    tf2_l.word_wrap = True

    p = tf2_l.paragraphs[0]
    p.text = "CHỈ SỐ DỰ BÁO & ĐỘ TIN CẬY VẬN HÀNH"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = AVIATION_BLUE

    op_stats = [
        ("Xác suất chậm trễ", prob_pct),
        ("Phân nhóm rủi ro", risk_band),
        ("Độ trễ dự phóng", f"~{proj_delay} phút"),
        ("Ngưỡng cảnh báo tác nghiệp", f"{pred.get('threshold', 0.25):.4f}"),
        ("Hệ số khuếch đại rủi ro (Lift)", f"{lift:.2f}x"),
        ("Tỷ lệ trễ tuyến 30 ngày qua", f"{ctx.get('route_delay_rate_30d', 0)*100:.1f}%"),
        ("Tỷ lệ trễ hãng 30 ngày qua", f"{ctx.get('carrier_delay_rate_30d', 0)*100:.1f}%"),
        ("Mật độ cất cánh tại sân bay", f"{ctx.get('scheduled_departures_hour', 0)} chuyến/giờ"),
    ]
    for k, v in op_stats:
        p_item = tf2_l.add_paragraph()
        p_item.text = f"{k}:  {v}"
        p_item.font.size = Pt(10.5)
        p_item.font.color.rgb = TEXT_BODY
        p_item.space_before = Pt(8)

    # Right Column: Top 4 Risk Drivers & Bottlenecks
    drivers = pred.get("top_risk_factors", [])
    if not drivers:
        drivers = [
            {"factor": "Mật độ cất cánh giờ cao điểm", "description": f"Sân bay {origin} đạt {ctx.get('scheduled_departures_hour', 0)} chuyến/giờ, tạo áp lực tắc nghẽn đường lăn và chậm cất cánh."},
            {"factor": "Lịch sử trễ tích lũy chặng bay", "description": f"Tuyến bay {origin}-{dest} có tỷ lệ trễ lịch sử đạt {ctx.get('route_delay_rate_30d', 0)*100:.1f}% trong 30 ngày gần nhất."},
            {"factor": "Hiệu suất đúng giờ của hãng", "description": f"Tỷ lệ trễ mạng lưới hãng {carrier} đạt {ctx.get('carrier_delay_rate_30d', 0)*100:.1f}%, cần kiểm soát chặt chẽ thời gian quay đầu."},
            {"factor": "Đặc thù cự ly & Khung giờ", "description": f"Chặng bay {dist_bucket} ({distance:.0f} dặm) lúc {dep_window} có nguy cơ chịu hiệu ứng trễ dây chuyền từ chặng bay trước."},
        ]

    for idx, d in enumerate(drivers[:4]):
        y_d = 1.5 + idx * 1.35
        _add_card_shape(s2, 5.2, y_d, 7.333, 1.2, CARD_WHITE, CARD_BORDER)
        tb_d = s2.shapes.add_textbox(Inches(5.4), Inches(y_d + 0.12), Inches(6.9), Inches(0.96))
        tf_d = tb_d.text_frame
        tf_d.word_wrap = True

        p_dh = tf_d.paragraphs[0]
        p_dh.text = f"{idx+1}. {d.get('factor', 'Yếu tố rủi ro')}"
        p_dh.font.size = Pt(11)
        p_dh.font.bold = True
        p_dh.font.color.rgb = AMBER_WARNING if idx == 0 else AVIATION_BLUE

        p_db = tf_d.add_paragraph()
        p_db.text = str(d.get("description", ""))
        p_db.font.size = Pt(10)
        p_db.font.color.rgb = TEXT_BODY
        p_db.space_before = Pt(3)

    # =========================================================================
    # SLIDE 3: AVIATION REGULATORY GOVERNANCE & STATUTORY PENALTIES
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    bg3 = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg3.fill.solid()
    bg3.fill.fore_color.rgb = BG_WHITE
    bg3.line.fill.background()
    _add_slide_header(s3, "Pháp Chế & Tuân Thủ Hàng Không", "Thẩm Định Pháp Luật & Chế Tài Quản Lý Nhà Nước", flight_tag, 3)

    col_w = 3.75
    col_gap = 0.24
    cards_data = [
        (
            "14 CFR § 259.4",
            "TARMAC DELAY RULE",
            "Chế tài: Tới $37,377 USD / hành khách",
            "Nghiêm cấm giữ hành khách trên máy bay quá 180 phút đối với chuyến bay nội địa Hoa Kỳ mà không mở cửa cầu dẫn cho khách xuống. Bắt buộc cung cấp nước, thức ăn và chăm sóc y tế sau 120 phút trên đường lăn.",
            ROSE_ALERT,
        ),
        (
            "FAR PART 117",
            "FLIGHT DUTY PERIOD (FDP)",
            "Chế tài: Đình chỉ bay & Xử phạt FAA",
            "Giới hạn thời gian làm nhiệm vụ bay tối đa của phi công và tiếp viên. Nếu thời gian chậm trễ đẩy FDP vượt ngưỡng luật định, toàn bộ tổ bay sẽ bị truất quyền điều khiển, bắt buộc kích hoạt Standby Crew ngay lập tức.",
            AMBER_WARNING,
        ),
        (
            "14 CFR § 260.6 & TT 19",
            "CASH REFUND MANDATE",
            "Chế tài: Hoàn trả 100% tiền mặt tự động",
            "Luật DOT 2024 quy định hãng bay bắt buộc hoàn tiền mặt tự động cho khách khi chuyến bay trễ từ 3 tiếng trở lên mà khách không chấp nhận phương án thay thế. Đối chiếu Thông tư 19/2023/TT-BGTVT và Nghị định 162/2018.",
            AVIATION_BLUE,
        ),
    ]

    for idx, (code, title, penalty, desc, accent) in enumerate(cards_data):
        x = start_x + idx * (col_w + col_gap)
        _add_card_shape(s3, x, 1.5, col_w, 3.6, CARD_WHITE, CARD_BORDER)
        tb_c = s3.shapes.add_textbox(Inches(x + 0.2), Inches(1.7), Inches(col_w - 0.4), Inches(3.2))
        tfc = tb_c.text_frame
        tfc.word_wrap = True

        p_c1 = tfc.paragraphs[0]
        p_c1.text = code
        p_c1.font.size = Pt(13)
        p_c1.font.bold = True
        p_c1.font.color.rgb = accent

        p_c2 = tfc.add_paragraph()
        p_c2.text = title
        p_c2.font.size = Pt(10)
        p_c2.font.bold = True
        p_c2.font.color.rgb = PRIMARY_NAVY
        p_c2.space_before = Pt(2)

        p_c3 = tfc.add_paragraph()
        p_c3.text = penalty
        p_c3.font.size = Pt(9.5)
        p_c3.font.bold = True
        p_c3.font.color.rgb = AMBER_WARNING
        p_c3.space_before = Pt(6)

        p_c4 = tfc.add_paragraph()
        p_c4.text = desc
        p_c4.font.size = Pt(9.5)
        p_c4.font.color.rgb = TEXT_BODY
        p_c4.space_before = Pt(6)

    # Bottom Full-width Card: Mandatory Dispatch Action
    _add_card_shape(s3, start_x, 5.3, 11.733, 1.6, CARD_BG, CARD_BORDER)
    tb_act = s3.shapes.add_textbox(Inches(start_x + 0.25), Inches(5.45), Inches(11.2), Inches(1.3))
    tf_act = tb_act.text_frame
    tf_act.word_wrap = True

    p_ah = tf_act.paragraphs[0]
    p_ah.text = "MỆNH LỆNH ĐIỀU HÀNH BẮT BUỘC TỪ TRƯỞNG CA OCC (DISPATCH DIRECTIVE):"
    p_ah.font.size = Pt(10.5)
    p_ah.font.bold = True
    p_ah.font.color.rgb = EMERALD_GREEN

    p_ab = tf_act.add_paragraph()
    p_ab.text = f"{top_leg.get('mandatory_action', 'Yêu cầu Dispatcher theo dõi sát sao tiến độ quay đầu máy bay, chủ động liên hệ ATC và chuẩn bị phương án đổi giờ cất cánh để không vi phạm luật.')}"
    p_ab.font.size = Pt(11)
    p_ab.font.color.rgb = TEXT_DARK
    p_ab.space_before = Pt(4)

    # =========================================================================
    # SLIDE 4: FINANCIAL COST EXPOSURE & WHAT-IF MITIGATION ROI
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    bg4 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg4.fill.solid()
    bg4.fill.fore_color.rgb = BG_WHITE
    bg4.line.fill.background()
    _add_slide_header(s4, "Bóc Tách Chi Phí FAA & Phương Án Can Thiệp", "Phân Tích Thiệt Hại Tài Chính & ROI Can Thiệp Điều Hành", flight_tag, 4)

    # Left: Financial Breakdown Card
    _add_card_shape(s4, 0.8, 1.5, 5.6, 5.4, CARD_WHITE, CARD_BORDER)
    tb_f = s4.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(5.0))
    tff = tb_f.text_frame
    tff.word_wrap = True

    p = tff.paragraphs[0]
    p.text = "BÓC TÁCH PHƠI NHIỄM TÀI CHÍNH (FAA $101.18/MIN)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = AVIATION_BLUE

    fin_items = [
        ("Chi phí trễ cơ sở FAA ($101.18/phút)", f"${cost_base:,.2f} USD"),
        ("Rủi ro phạt Tarmac (§ 259.4)", f"${cost_tarmac:,.2f} USD"),
        ("Rủi ro hoàn vé tiền mặt (§ 260.6)", f"${cost_refund:,.2f} USD"),
        ("Chi phí chăm sóc hành khách", f"${fin.get('passenger_care_cost_usd', 0):,.2f} USD"),
        ("TỔNG RỦI RO TÀI CHÍNH PHƠI NHIỄM", f"${total_exposure:,.2f} USD"),
    ]
    for idx, (label, val) in enumerate(fin_items):
        p_item = tff.add_paragraph()
        p_item.text = f"{label}:\n{val}"
        p_item.font.size = Pt(11 if idx < 4 else 12.5)
        p_item.font.bold = (idx == 4)
        p_item.font.color.rgb = ROSE_ALERT if idx == 4 else TEXT_DARK
        p_item.space_before = Pt(8)

    # Right: Proactive Intervention ROI
    _add_card_shape(s4, 6.7, 1.5, 5.833, 5.4, CARD_BG, CARD_BORDER)
    tb_roi = s4.shapes.add_textbox(Inches(6.9), Inches(1.7), Inches(5.4), Inches(5.0))
    tf_roi = tb_roi.text_frame
    tf_roi.word_wrap = True

    p = tf_roi.paragraphs[0]
    p.text = "HIỆU QUẢ KINH TẾ CAN THIỆP CHỦ ĐỘNG (INTERVENTION ROI)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN

    roi_items = [
        ("Phương án can thiệp tối ưu", best_action),
        ("Tiết kiệm tài chính tiềm năng", f"${savings:,.2f} USD"),
        ("Giảm thiểu độ trễ dự kiến", f"Giảm từ ~{proj_delay} phút xuống ngưỡng an toàn"),
        ("Bảo toàn uy tín thương hiệu", "Triệt tiêu nguy cơ vi phạm pháp chế DOT & CAAV"),
        ("Tối ưu hóa nguồn lực tàu bay", "Ngăn chặn hiệu ứng trễ dây chuyền sang các chặng sau"),
    ]
    for idx, (k, v) in enumerate(roi_items):
        p_item = tf_roi.add_paragraph()
        p_item.text = f"•  {k}:\n    {v}"
        p_item.font.size = Pt(10.5)
        p_item.font.color.rgb = TEXT_BODY
        p_item.space_before = Pt(8)

    # =========================================================================
    # SLIDE 5: ACTIONABLE DISPATCH OPERATIONAL TIMELINE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    bg5 = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg5.fill.solid()
    bg5.fill.fore_color.rgb = BG_WHITE
    bg5.line.fill.background()
    _add_slide_header(s5, "Kế Hoạch Tác Nghiệp Khép Kín", "Lộ Trình Kiểm Soát Thời Gian & Giảm Thiểu Rủi Ro", flight_tag, 5)

    phases = [
        ("T-120 PHÚT", "LẬP KẾ HOẠCH & CHUẨN BỊ", "Dispatcher / OCC", "Đánh giá slot cất cánh, kiểm tra tình hình thời tiết và luồng ATC tại sân bay đi/đến. Xác định phương án nạp dầu và kịch bản dự phòng.", AVIATION_BLUE),
        ("T-60 PHÚT", "ĐIỀU PHỐI TỔ BAY & CỬA GA", "Crew Scheduling & Gate", "Kiểm tra FDP của tổ bay. Nếu có nguy cơ vượt giờ làm nhiệm vụ, điều động ngay tổ bay dự bị (Standby Crew). Thông báo mở cửa nhận khách đúng giờ.", AMBER_WARNING),
        ("T-15 PHÚT", "ĐÓNG CỬA & RÚT CẦU DẪN", "Ramp Control & Ground", "Hoàn tất kiểm đếm hành khách. Đóng cửa tàu bay và rút cầu dẫn. Kích hoạt đồng hồ giám sát thời gian trên đường lăn (Tarmac Clock).", ROSE_ALERT),
        ("EN-ROUTE", "THEO DÕI ĐƯỜNG BAY & HẠ CÁNH", "ATC Coordinator", "Yêu cầu ATC đường bay thẳng (direct routing) hoặc điều chỉnh tốc độ bay để bù lại thời gian chậm trễ trên mặt đất.", EMERALD_GREEN),
    ]

    card_tw = 2.75
    for idx, (time_lbl, title, role, desc, accent) in enumerate(phases):
        x = start_x + idx * (card_tw + card_gap)
        _add_card_shape(s5, x, 1.5, card_tw, 5.4, CARD_WHITE, CARD_BORDER)
        tb_ph = s5.shapes.add_textbox(Inches(x + 0.18), Inches(1.7), Inches(card_tw - 0.36), Inches(5.0))
        tf_ph = tb_ph.text_frame
        tf_ph.word_wrap = True

        p_t1 = tf_ph.paragraphs[0]
        p_t1.text = time_lbl
        p_t1.font.size = Pt(13)
        p_t1.font.bold = True
        p_t1.font.color.rgb = accent

        p_t2 = tf_ph.add_paragraph()
        p_t2.text = title
        p_t2.font.size = Pt(10)
        p_t2.font.bold = True
        p_t2.font.color.rgb = PRIMARY_NAVY
        p_t2.space_before = Pt(3)

        p_t3 = tf_ph.add_paragraph()
        p_t3.text = f"Phụ trách: {role}"
        p_t3.font.size = Pt(9.5)
        p_t3.font.color.rgb = TEXT_MUTED
        p_t3.space_before = Pt(6)

        p_t4 = tf_ph.add_paragraph()
        p_t4.text = desc
        p_t4.font.size = Pt(9.5)
        p_t4.font.color.rgb = TEXT_BODY
        p_t4.space_before = Pt(10)

    # Save to buffer
    buf = io.BytesIO()
    prs.save(buf)
    content = buf.getvalue()

    if output_path:
        p_out = Path(output_path)
        p_out.parent.mkdir(parents=True, exist_ok=True)
        p_out.write_bytes(content)

    return content


def generate_presentation_markdown(adv: Dict[str, Any]) -> str:
    """Generates Marp-compatible markdown presentation slides in clean light style."""
    ctx = adv.get("flight_context", {})
    pred = adv.get("prediction_context", {})
    fin = adv.get("financial_exposure", {})
    reg = adv.get("regulatory_compliance", {})
    
    carrier = ctx.get("carrier_code", "AA")
    fl_no = ctx.get("flight_number") or ""
    origin = ctx.get("origin", "ATL")
    dest = ctx.get("dest", "DFW")
    prob_pct = f"{pred.get('delay_probability', 0)*100:.1f}%"
    risk_band = pred.get("risk_band", "normal").upper()
    proj_delay = pred.get("projected_delay_min", 0)
    total_exposure = fin.get("total_potential_exposure_usd", 0.0)
    savings = fin.get("proactive_mitigation_savings_usd", 0.0)
    leg = (reg.get("legal_evaluations") or [{}])[0]
    
    return f"""---
marp: true
theme: default
paginate: true
header: 'SkyOps Platform — Flight Operations & Regulatory Governance'
footer: 'Chuyến bay: {carrier}{fl_no} ({origin} ➔ {dest})'
---

# BÁO CÁO QUẢN TRỊ ĐIỀU HÀNH
## Chuyến bay {carrier}{fl_no} | Tuyến: {origin} ➔ {dest}
### Mức độ rủi ro: **{risk_band}** | Xác suất chậm trễ: **{prob_pct}**

- **Hãng khai thác**: {ctx.get('carrier_name', carrier)}
- **Ngày bay**: {ctx.get('flight_date')} | Khung giờ: {ctx.get('dep_window_label')}
- **Độ trễ dự phóng**: ~{proj_delay} phút
- **Rủi ro tài chính phơi nhiễm**: ${total_exposure:,.2f} USD

---

# 1. PHÂN TÍCH CĂN NGUYÊN & ĐIỂM NGHẼN
- **Mật độ cất cánh sân bay {origin}**: {ctx.get('scheduled_departures_hour', 0)} chuyến/giờ (Khung giờ cao điểm)
- **Hệ số rủi ro (Risk Lift)**: {pred.get('lift_at_10', 1.0):.2f}x
- **Tỷ lệ trễ tuyến bay 30 ngày**: {ctx.get('route_delay_rate_30d', 0)*100:.1f}%
- **Tỷ lệ trễ mạng lưới hãng 30 ngày**: {ctx.get('carrier_delay_rate_30d', 0)*100:.1f}%
- **Cự ly bay**: {ctx.get('distance_miles', 0):,.0f} dặm ({ctx.get('distance_bucket', 'medium')})

---

# 2. THẨM ĐỊNH PHÁP CHẾ & CHẾ TÀI HÀNG KHÔNG
- **Căn cứ pháp lý chủ đạo**: {leg.get('legal_code', '14 CFR § 259.4')} - {leg.get('citation', 'Tarmac Delay Rule')}
- **Mức phạt theo luật**: {leg.get('statutory_penalty', 'N/A')}
- **Quy định FDP Tổ bay**: FAR Part 117 — Giới hạn giờ bay nhiệm vụ
- **Hoàn vé tiền mặt bắt buộc**: 14 CFR § 260.6 (Trễ $\ge 3$ tiếng nội địa)
- **Mệnh lệnh OCC**: {leg.get('mandatory_action', 'Theo dõi sát và can thiệp kịp thời')}

---

# 3. BÓC TÁCH CHI PHÍ TÀI CHÍNH (FAA $101.18/MIN)
- **Chi phí trễ cơ sở FAA**: ${fin.get('base_delay_cost_usd', 0):,.2f} USD
- **Rủi ro phạt Tarmac & Hoàn tiền vé**: ${fin.get('tarmac_penalty_exposure_usd', 0) + fin.get('cash_refund_exposure_usd', 0):,.2f} USD
- **Tổng rủi ro tài chính**: ${total_exposure:,.2f} USD
- **Phương án đề xuất**: {adv.get('best_contingency_action', 'Điều chỉnh giờ cất cánh')}
- **Tiết kiệm kinh tế ròng**: **${savings:,.2f} USD**

---

# 4. KẾ HOẠCH TÁC NGHIỆP THEO DÒNG THỜI GIAN
- **T-120m**: Đánh giá slot cất cánh và dự báo luồng không lưu ATC.
- **T-60m**: Rà soát giờ làm nhiệm vụ FDP tổ bay, sẵn sàng Standby Crew.
- **T-15m**: Đóng cửa tàu bay, rút cầu dẫn và bật đồng hồ Tarmac Clock.
- **En-route**: Xin đường bay thẳng (direct route) để bù giờ trên không.
"""


def generate_presentation_html(adv: Dict[str, Any]) -> str:
    """Generates an interactive, bright, standalone 16:9 HTML slide deck presentation."""
    ctx = adv.get("flight_context", {})
    pred = adv.get("prediction_context", {})
    fin = adv.get("financial_exposure", {})
    reg = adv.get("regulatory_compliance", {})
    
    carrier = ctx.get("carrier_code", "AA")
    fl_no = ctx.get("flight_number") or ""
    origin = ctx.get("origin", "ATL")
    dest = ctx.get("dest", "DFW")
    distance = ctx.get("distance_miles", 0)
    prob_pct = f"{pred.get('delay_probability', 0)*100:.1f}%"
    risk_band = pred.get("risk_band", "normal").upper()
    proj_delay = pred.get("projected_delay_min", 0)
    total_exposure = fin.get("total_potential_exposure_usd", 0.0)
    savings = fin.get("proactive_mitigation_savings_usd", 0.0)
    leg = (reg.get("legal_evaluations") or [{}])[0]

    return f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SkyOps Slide Deck — {carrier}{fl_no} ({origin} ➔ {dest})</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #f1f5f9;
      color: #0f172a;
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      overflow-x: hidden;
      padding: 20px;
    }}
    .deck-container {{
      width: 100%;
      max-width: 1240px;
      aspect-ratio: 16 / 9;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 16px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.08);
      display: flex;
      flex-direction: column;
    }}
    .slide {{
      display: none;
      width: 100%;
      height: 100%;
      padding: 44px 54px;
      flex-direction: column;
      justify-content: space-between;
      background: #ffffff;
    }}
    .slide.active {{
      display: flex;
      animation: fadeIn 0.25s ease;
    }}
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .slide-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 2px solid #f1f5f9;
      padding-bottom: 18px;
    }}
    .slide-tag {{
      font-size: 11px;
      font-weight: 700;
      color: #0284c7;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      font-family: 'JetBrains Mono', monospace;
    }}
    .slide-title {{
      font-size: 26px;
      font-weight: 800;
      color: #0f172a;
      margin-top: 4px;
      letter-spacing: -0.3px;
    }}
    .grid-4 {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-top: 22px;
    }}
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-top: 20px;
    }}
    .card {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 20px;
    }}
    .card-label {{ font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
    .card-value {{ font-size: 28px; font-weight: 800; color: #0284c7; margin: 6px 0; }}
    .card-sub {{ font-size: 12px; color: #475569; }}
    .deck-nav {{
      position: absolute;
      bottom: 22px;
      right: 32px;
      display: flex;
      gap: 10px;
      z-index: 10;
    }}
    .nav-btn {{
      background: #0284c7;
      color: white;
      border: none;
      padding: 8px 18px;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 700;
      font-size: 13px;
      transition: background 0.15s ease;
    }}
    .nav-btn:hover {{ background: #0369a1; }}
    .print-btn {{ background: #059669; }}
    .print-btn:hover {{ background: #047857; }}
    @media print {{
      body {{ background: white; padding: 0; }}
      .deck-nav {{ display: none; }}
      .deck-container {{ border: none; box-shadow: none; max-width: 100%; border-radius: 0; }}
      .slide {{ display: flex !important; page-break-after: always; padding: 30px; }}
    }}
  </style>
</head>
<body>
  <div class="deck-container">
    <!-- SLIDE 1 -->
    <div class="slide active" id="slide-1">
      <div class="slide-header">
        <div>
          <div class="slide-tag">SkyOps Platform  |  Báo Cáo Tác Nghiệp Khởi Hành</div>
          <div class="slide-title">Hồ Sơ Giám Sát Chuyến Bay {carrier}{fl_no}</div>
        </div>
        <div style="text-align:right">
          <div style="font-weight:800;color:#0284c7;font-size:17px">{origin} ➔ {dest}</div>
          <div style="font-size:12px;color:#64748b;margin-top:2px">{ctx.get('flight_date')} | {ctx.get('dep_window_label')}</div>
        </div>
      </div>
      <div class="grid-4">
        <div class="card">
          <div class="card-label">Xác Suất Chậm Trễ</div>
          <div class="card-value" style="color:{'#dc2626' if risk_band in ('HIGH', 'CRITICAL') else '#059669'}">{prob_pct}</div>
          <div class="card-sub">Phân hạng: <strong>{risk_band}</strong></div>
        </div>
        <div class="card">
          <div class="card-label">Độ Trễ Dự Phóng</div>
          <div class="card-value">~{proj_delay}m</div>
          <div class="card-sub">Hệ số Lift: {pred.get('lift_at_10', 1.0):.2f}x</div>
        </div>
        <div class="card">
          <div class="card-label">Phơi Nhiễm Tài Chính</div>
          <div class="card-value" style="color:#d97706">${total_exposure:,.0f}</div>
          <div class="card-sub">Định mức FAA $101.18/phút</div>
        </div>
        <div class="card">
          <div class="card-label">Tiết Kiệm Can Thiệp</div>
          <div class="card-value" style="color:#059669">${savings:,.0f}</div>
          <div class="card-sub">Bảo toàn dòng tiền ròng</div>
        </div>
      </div>
      <div class="card" style="margin-top:20px;line-height:1.7;font-size:13.5px;color:#334155;background:#ffffff;border:1px solid #cbd5e1">
        <strong style="color:#0284c7">TỔNG QUAN ĐIỀU HÀNH:</strong> Chuyến bay {carrier}{fl_no} từ {origin} đi {dest} ({distance:,.0f} dặm) đang ở mức rủi ro <strong>{risk_band}</strong>. Khuyến nghị can thiệp tác nghiệp: <em>{adv.get('best_contingency_action')}</em> để giảm thiểu rủi ro vi phạm quy định pháp chế và bảo toàn chi phí vận hành.
      </div>
      <div style="font-size:11px;color:#94a3b8;margin-top:10px">Slide 1 / 4  |  Dùng phím ➔ hoặc nút bấm bên dưới để chuyển slide</div>
    </div>

    <!-- SLIDE 2 -->
    <div class="slide" id="slide-2">
      <div class="slide-header">
        <div>
          <div class="slide-tag">Departure Risk & Root Causes</div>
          <div class="slide-title">Chẩn Đoán Rủi Ro Khởi Hành & Điểm Nghẽn Mạng Lưới</div>
        </div>
        <div style="font-size:14px;color:#0284c7;font-weight:700">{carrier}{fl_no}</div>
      </div>
      <div class="grid-2">
        <div class="card">
          <div class="card-label" style="color:#0284c7">Chỉ Số Đánh Giá & Độ Tin Cậy Vận Hành</div>
          <div style="margin-top:14px;line-height:2.2;font-size:13.5px;color:#334155">
            • <strong>Phân hạng rủi ro:</strong> {risk_band}<br>
            • <strong>Xác suất chậm trễ:</strong> {prob_pct}<br>
            • <strong>Ngưỡng cảnh báo:</strong> {pred.get('threshold', 0.25):.4f}<br>
            • <strong>Hệ số khuếch đại rủi ro (Lift):</strong> {pred.get('lift_at_10', 1.0):.2f}x<br>
            • <strong>Tỷ lệ trễ tuyến 30 ngày:</strong> {ctx.get('route_delay_rate_30d', 0)*100:.1f}%<br>
            • <strong>Tỷ lệ trễ hãng 30 ngày:</strong> {ctx.get('carrier_delay_rate_30d', 0)*100:.1f}%
          </div>
        </div>
        <div class="card">
          <div class="card-label" style="color:#d97706">Căn Nguyên & Điểm Nghẽn Chính</div>
          <div style="margin-top:14px;line-height:1.9;font-size:13.5px;color:#334155">
            • <strong>Mật độ cất cánh:</strong> {ctx.get('scheduled_departures_hour', 0)} chuyến/giờ tại {origin} (Khung giờ cao điểm đường lăn).<br>
            • <strong>Cự ly chặng:</strong> {distance:,.0f} dặm ({ctx.get('distance_bucket', 'medium')}).<br>
            • <strong>Rủi ro dây chuyền:</strong> Khả năng máy bay đến trễ (Late Aircraft) gây trễ tích lũy chặng tiếp theo.
          </div>
        </div>
      </div>
      <div style="font-size:11px;color:#94a3b8;margin-top:10px">Slide 2 / 4</div>
    </div>

    <!-- SLIDE 3 -->
    <div class="slide" id="slide-3">
      <div class="slide-header">
        <div>
          <div class="slide-tag">Aviation Regulatory Governance</div>
          <div class="slide-title">Thẩm Định Pháp Luật & Chế Tài Hàng Không</div>
        </div>
        <div style="font-size:14px;color:#0284c7;font-weight:700">{carrier}{fl_no}</div>
      </div>
      <div class="grid-2">
        <div class="card">
          <div class="card-label" style="color:#dc2626">14 CFR § 259.4 — Tarmac Delay Rule</div>
          <p style="font-size:13px;color:#334155;margin-top:10px;line-height:1.6">
            Nghiêm cấm giữ khách trên tàu bay quá 180 phút đối với chuyến bay nội địa. Phạt tối đa <strong>$37,377 USD/pax</strong>. Sau 120 phút phải cung cấp thức ăn, nước uống.
          </p>
          <div class="card-label" style="color:#d97706;margin-top:16px">FAR Part 117 — Flight Duty Period (FDP)</div>
          <p style="font-size:13px;color:#334155;margin-top:6px;line-height:1.6">
            Giới hạn thời gian làm nhiệm vụ bay của tổ bay. Kích hoạt Standby Crew ngay khi có nguy cơ vượt ngưỡng FDP.
          </p>
        </div>
        <div class="card">
          <div class="card-label" style="color:#0284c7">14 CFR § 260.6 — Cash Refund Mandate</div>
          <p style="font-size:13px;color:#334155;margin-top:10px;line-height:1.6">
            Quy định DOT 2024: Bắt buộc hoàn tiền mặt tự động nếu chuyến bay trễ từ 3 tiếng trở lên đối với chuyến nội địa.
          </p>
          <div class="card-label" style="color:#059669;margin-top:16px">Mệnh Lệnh Điều Hành OCC</div>
          <p style="font-size:13px;color:#0f172a;margin-top:6px;line-height:1.6">
            <strong>{leg.get('mandatory_action', 'Theo dõi sát tiến độ, chuẩn bị phương án dự phòng.')}</strong>
          </p>
        </div>
      </div>
      <div style="font-size:11px;color:#94a3b8;margin-top:10px">Slide 3 / 4</div>
    </div>

    <!-- SLIDE 4 -->
    <div class="slide" id="slide-4">
      <div class="slide-header">
        <div>
          <div class="slide-tag">Financial Exposure & Contingency ROI</div>
          <div class="slide-title">Bóc Tách Chi Phí FAA & Phương Án Can Thiệp</div>
        </div>
        <div style="font-size:14px;color:#0284c7;font-weight:700">{carrier}{fl_no}</div>
      </div>
      <div class="grid-2">
        <div class="card">
          <div class="card-label" style="color:#d97706">Bóc Tách Chi Phí Rủi Ro (FAA $101.18/phút)</div>
          <div style="margin-top:14px;line-height:2.1;font-size:13.5px;color:#334155">
            • Chi phí trễ cơ sở: <strong>${fin.get('base_delay_cost_usd', 0):,.2f} USD</strong><br>
            • Rủi ro phạt Tarmac: <strong>${fin.get('tarmac_penalty_exposure_usd', 0):,.2f} USD</strong><br>
            • Rủi ro hoàn vé tiền mặt: <strong>${fin.get('cash_refund_exposure_usd', 0):,.2f} USD</strong><br>
            • <strong style="color:#dc2626">Tổng phơi nhiễm: ${total_exposure:,.2f} USD</strong>
          </div>
        </div>
        <div class="card">
          <div class="card-label" style="color:#059669">Phương Án & Lợi Ích Bảo Toàn Ròng</div>
          <div style="margin-top:14px;line-height:1.9;font-size:13.5px;color:#334155">
            • <strong>Hành động tối ưu:</strong> {adv.get('best_contingency_action')}<br>
            • <strong>Tiết kiệm tài chính tiềm năng:</strong> <strong style="color:#059669">${savings:,.2f} USD</strong><br>
            • <strong>Lợi ích phi tài chính:</strong> Bảo vệ chỉ số OTP, ngăn chặn hủy chuyến và bảo toàn lịch bay của hành khách.
          </div>
        </div>
      </div>
      <div style="font-size:11px;color:#94a3b8;margin-top:10px">Slide 4 / 4</div>
    </div>

    <!-- NAVIGATION BAR -->
    <div class="deck-nav">
      <button class="nav-btn" onclick="prevSlide()">◀ Trước</button>
      <button class="nav-btn" onclick="nextSlide()">Sau ▶</button>
      <button class="nav-btn print-btn" onclick="window.print()">🖨️ In / Xuất PDF</button>
    </div>
  </div>

  <script>
    let cur = 1;
    const total = 4;
    function show(n) {{
      document.querySelectorAll('.slide').forEach(s => s.classList.remove('active'));
      const target = document.getElementById('slide-' + n);
      if (target) target.classList.add('active');
      cur = n;
    }}
    function nextSlide() {{ cur = cur < total ? cur + 1 : 1; show(cur); }}
    function prevSlide() {{ cur = cur > 1 ? cur - 1 : total; show(cur); }}
    window.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
      if (e.key === 'ArrowLeft') prevSlide();
    }});
  </script>
</body>
</html>"""
