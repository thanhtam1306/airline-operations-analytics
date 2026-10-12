"""
Aviation Regulatory & Compliance Decision Engine.

Provides situational, context-aware legal evaluations down to Article, Clause,
and Subsection (Điều, Khoản, Điểm) under US DOT (14 CFR), FAA (FAR Part 117),
and Vietnam CAAV (Thông tư 19/2023/TT-BGTVT).

Rules are dynamically matched to the SPECIFIC flight profile:
- Departure time & Circadian window (dep_hour, WOCL)
- Airport congestion & Hub taxiway saturation (scheduled_departures_hour)
- Carrier business model (Legacy/Network Carrier vs Low-Cost Carrier)
- Route history (Chronically delayed threshold)
- Model risk band (normal, elevated, high)
"""
from __future__ import annotations

from typing import Any, Dict, List

LEGACY_CARRIERS = {"AA", "DL", "UA", "AS"}
LOW_COST_CARRIERS = {"WN", "B6", "F9", "NK", "G4", "HA"}


def evaluate_regulatory_compliance(
    carrier_code: str,
    origin: str,
    dest: str,
    dep_hour: int,
    delay_probability: float,
    threshold: float,
    risk_band: str,
    features_used: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Dynamically select and evaluate ONLY the legal regulations that fit
    the specific flight scenario, identifying exact Điều, Khoản, Điểm,
    statutory penalties, operational orders, and the reason for triggering.
    """
    alerts: List[Dict[str, Any]] = []
    carrier_code_upper = carrier_code.upper()
    is_legacy = carrier_code_upper in LEGACY_CARRIERS or features_used.get("carrier_type") == "legacy"
    congestion = int(features_used.get("scheduled_departures_hour", 5))
    route_delay_rate = float(features_used.get("route_delay_rate_30d", 0.0))
    distance = float(features_used.get("distance_miles", 800.0))

    is_high_risk = risk_band == "high" or delay_probability >= threshold
    is_elevated_risk = risk_band == "elevated" or (delay_probability >= 0.7 * threshold and not is_high_risk)
    is_normal_risk = not is_high_risk and not is_elevated_risk

    # -------------------------------------------------------------------------
    # KỊCH BẢN 1: CHUYẾN BAY AN TOÀN / ĐÚNG GIỜ (NORMAL RISK)
    # Chỉ áp dụng quy chuẩn khai thác tiêu chuẩn, KHÔNG kích hoạt chế tài trễ!
    # -------------------------------------------------------------------------
    if is_normal_risk:
        alerts.append({
            "legal_code": "14 CFR § 121.593 & § 121.597",
            "jurisdiction": "Cục Hàng không Liên bang Hoa Kỳ (FAA)",
            "citation": "Điều 121.593 & Điều 121.597 - Thẩm quyền cấp lệnh cất cánh tiêu chuẩn (Dispatch Release Corridor)",
            "trigger_reason": (
                f"Kích hoạt cho chuyến bay có xác suất trễ thấp ({(delay_probability*100):.1f}% < ngưỡng {threshold}). "
                "Chuyến bay nằm hoàn toàn trong hành lang khai thác an toàn, không có nguy cơ vi phạm pháp luật."
            ),
            "statutory_text": (
                "Chuyến bay đủ điều kiện an toàn, thời gian làm nhiệm vụ của phi hành đoàn và kế hoạch nhiên liệu "
                "đáp ứng đầy đủ quy chuẩn FAR Part 121. Cho phép Điều phái viên cấp lệnh bay đúng lịch trình."
            ),
            "subsections": [
                {
                    "item": "Điều 121.593",
                    "requirement": "Ký nhận bản Dispatch Release tiêu chuẩn cho chuyến bay nội địa định kỳ."
                },
                {
                    "item": "Điều 121.617",
                    "requirement": "Sân bay dự bị đáp ứng tiêu chuẩn thời tiết thông thường (Alternate Airport Standards)."
                }
            ],
            "severity": "NORMAL",
            "statutory_penalty": "Không có chế tài xử phạt (Tuân thủ 100% quy chuẩn an toàn).",
            "mandatory_action": (
                f"LỆNH CHO ĐIỀU PHÁI VIÊN (DISPATCH): Tiến hành làm thủ tục đẩy lùi (Push-back) đúng giờ lúc {dep_hour}:00. "
                "Không cần kích hoạt bất kỳ quy trình dự phòng hoặc đội bay dự bị nào."
            ),
            "vietnam_equivalent": "Luật Hàng không Dân dụng Việt Nam Điều 158 Khoản 1 Điểm a (Khai thác chuyến bay theo đúng kế hoạch được cấp phép)."
        })

    # -------------------------------------------------------------------------
    # KỊCH BẢN 2: CHUYẾN BAY CẢNH BÁO SỚM (ELEVATED RISK - NẰM TRONG VÙNG ĐỆM)
    # Kích hoạt nghĩa vụ cung cấp thông tin và cảnh báo trước
    # -------------------------------------------------------------------------
    elif is_elevated_risk:
        alerts.append({
            "legal_code": "14 CFR § 259.8(a)(1)",
            "jurisdiction": "Bộ Giao thông Vận tải Hoa Kỳ (US DOT Flight Status Notification)",
            "citation": "Điều 259.8, Khoản (a), Điểm (1) - Nghĩa vụ cập nhật thông tin chuyến bay định kỳ 30 phút",
            "trigger_reason": (
                f"Kích hoạt do chuyến bay có dấu hiệu rủi ro trễ trung bình ({(delay_probability*100):.1f}%). "
                "Chưa vi phạm mốc phạt nhưng bắt buộc phải kích hoạt nghĩa vụ thông tin minh bạch."
            ),
            "statutory_text": (
                "Hãng hàng không có nghĩa vụ cập nhật tình trạng chuyến bay (Flight Status Change) cho hành khách "
                "và công chúng trong vòng 30 phút kể từ khi phát hiện nguy cơ chậm hoặc thay đổi cửa ra tàu bay."
            ),
            "subsections": [
                {
                    "item": "Khoản (a), Điểm (1), Tiểu mục (i)",
                    "requirement": "Cập nhật tức thời lên bảng hiển thị thông tin chuyến bay (FIDS) tại sân bay khởi hành."
                },
                {
                    "item": "Khoản (a), Điểm (1), Tiểu mục (ii)",
                    "requirement": "Gửi tin nhắn cảnh báo tự động qua ứng dụng di động hoặc SMS cho hành khách đã đăng ký thông tin."
                }
            ],
            "severity": "MONITORING_ALERT",
            "statutory_penalty": "Xử phạt hành chính nếu để xảy ra tình trạng thông tin chậm trễ gây hỗn loạn tại phòng chờ.",
            "mandatory_action": (
                "LỆNH CHO BỘ PHẬN TRUYỀN THÔNG & DỊCH VỤ HÀNH KHÁCH: Thiết lập cơ chế giám sát mốc thời gian 30 phút. "
                "Sẵn sàng tin nhắn thông báo điều chỉnh giờ cất cánh nếu tình trạng ùn ứ tiếp tục diễn biến xấu."
            ),
            "vietnam_equivalent": "Thông tư 19/2023/TT-BGTVT Điều 8 Khoản 1 Điểm a (Nghĩa vụ cập nhật kịp thời thông tin chuyến bay cho hành khách)."
        })

    # -------------------------------------------------------------------------
    # KỊCH BẢN 3: CHUYẾN BAY NGUY CƠ CAO (HIGH RISK)
    # Phân luồng chính xác từng quy định phù hợp với ĐẶC THÙ chuyến bay này
    # -------------------------------------------------------------------------
    if is_high_risk:
        # 3.1. QUY ĐỊNH TẮC NGHẼN ĐƯỜNG LĂN (TARMAC DELAY RULE)
        # CHỈ áp dụng nếu sân bay đông đúc (>=8 chuyến/giờ) HOẶC rơi vào giờ cao điểm chiều tối (16h-21h)
        is_congested_airport = congestion >= 8 or dep_hour in [16, 17, 18, 19, 20]
        if is_congested_airport:
            alerts.append({
                "legal_code": "14 CFR § 259.4(b)(1)",
                "jurisdiction": "Bộ Giao thông Vận tải Hoa Kỳ (US DOT)",
                "citation": "Điều 259.4, Khoản (b), Điểm (1) - Giới hạn giam khách trên đường lăn (Tarmac Delay Rule)",
                "trigger_reason": (
                    f"Kích hoạt ĐẶC THÙ do sân bay {origin} đang có mật độ cất cánh đông đúc ({congestion} chuyến/giờ) "
                    f"vào khung giờ cao điểm ({dep_hour}:00) kết hợp với rủi ro trễ cao ({(delay_probability*100):.1f}%)."
                ),
                "statutory_text": (
                    "Hãng hàng không không được phép giữ tàu bay trên đường lăn (tarmac) quá 03 giờ đối với chuyến bay nội địa "
                    "mà không cung cấp cho hành khách cơ hội xuống tàu bay an toàn."
                ),
                "subsections": [
                    {
                        "item": "Điểm (1), Tiểu mục (i)",
                        "requirement": "Bắt buộc cung cấp đồ ăn nhẹ và nước uống đóng chai không muộn hơn 02 giờ sau khi tàu bay rời cửa (push-back)."
                    },
                    {
                        "item": "Điểm (1), Tiểu mục (ii)",
                        "requirement": "Bắt buộc duy trì điều hòa, hệ thống nhà vệ sinh hoạt động và cung cấp dịch vụ y tế khẩn cấp."
                    }
                ],
                "severity": "CRITICAL",
                "statutory_penalty": "Phạt vi phạm dân sự theo 49 U.S.C. § 46301 lên tới 37.377 USD cho MỖI hành khách trên chuyến bay.",
                "mandatory_action": (
                    "LỆNH BẮT BUỘC (OCC GATE HOLD): Giữ máy bay tại cửa (Gate Hold), TUYỆT ĐỐI KHÔNG cấp lệnh đẩy lùi ra đường lăn "
                    "nếu ATC chưa xác nhận khe cất cánh (Take-off slot) trong 45 phút tới để không bị rơi vào 'bẫy đếm ngược 3 tiếng'."
                ),
                "vietnam_equivalent": "Thông tư 19/2023/TT-BGTVT Điều 8 Khoản 2 Điểm a & Nghị định 162/2018/NĐ-CP Điều 24 Khoản 2."
            })

        # 3.2. GIỚI HẠN GIỜ BAY CỦA PHI HÀNH ĐOÀN (CREW DUTY PERIOD & WOCL)
        # CHỈ áp dụng nếu bay ca tối muộn/khuya (>=17h hoặc <=5h sáng) - nơi nguy cơ Crew Time-Out là có thật!
        is_evening_or_night = dep_hour >= 17 or dep_hour <= 5
        if is_evening_or_night:
            alerts.append({
                "legal_code": "14 CFR § 117.11(a) & § 117.19(a)(1)",
                "jurisdiction": "Cục Hàng không Liên bang Hoa Kỳ (FAA)",
                "citation": "Điều 117.11, Khoản (a) & Điều 117.19, Khoản (a), Điểm (1) - Giới hạn thời gian làm nhiệm vụ bay (FDP)",
                "trigger_reason": (
                    f"Kích hoạt ĐẶC THÙ do chuyến bay khởi hành vào ca tối/đêm ({dep_hour}:00). "
                    "Phi hành đoàn đã tích lũy giờ bay từ các chặng trước, đối mặt với nguy cơ hết giờ bay hợp pháp (Crew Time-Out)."
                ),
                "statutory_text": (
                    "Nghiêm cấm phân công hoặc bắt đầu chuyến bay nếu thời gian làm nhiệm vụ bay dự kiến (FDP) vượt quá bảng Table B. "
                    "Chỉ được phép gia hạn tối đa 02 giờ trước cất cánh nếu có ký nhận đồng thuận giữa Cơ trưởng (PIC) và Dispatcher."
                ),
                "subsections": [
                    {
                        "item": "Khoản (a), Điều 117.11",
                        "requirement": "Xác định trần FDP tối đa dựa trên giờ báo cáo (Report Time) và số lượng chặng bay trong ngày."
                    },
                    {
                        "item": "Khoản (a), Điểm (1), Điều 117.19",
                        "requirement": "Gia hạn FDP trước cất cánh bắt buộc phải có sự đồng thuận ký văn bản giữa Cơ trưởng (PIC) và Dispatcher."
                    }
                ],
                "severity": "CRITICAL",
                "statutory_penalty": "Đình chỉ bay ngay lập tức (Aircraft Grounded), xử phạt hành chính đối với hãng và tước bằng lái của tổ bay.",
                "mandatory_action": (
                    "LỆNH ĐIỀU PHỐI TỔ BAY (CREW DISPATCH): Rà soát quỹ giờ bay còn lại của Tổ lái. Kích hoạt ngay Tổ bay dự phòng "
                    f"(Standby Crew Tier-1) tại {origin} sẵn sàng tiếp quản tàu bay nếu chuyến bay bị trễ quá 60 phút."
                ),
                "vietnam_equivalent": "Quy chế An toàn Hàng không Việt Nam (VAR Part 12) - Giới hạn thời gian làm nhiệm vụ và nghỉ ngơi của tổ lái."
            })

        # 3.3. CHÍNH SÁCH ĐẶC THÙ THEO MÔ HÌNH HÃNG BAY (LEGACY vs LOW-COST)
        if is_legacy:
            # Hãng truyền thống (AA, DL, UA): Khách chủ yếu là transit kết nối mạng lưới
            alerts.append({
                "legal_code": "14 CFR § 259.5(b)(8)",
                "jurisdiction": "Bộ Giao thông Vận tải Hoa Kỳ (US DOT Customer Service Plan)",
                "citation": "Điều 259.5, Khoản (b), Điểm (8) - Nghĩa vụ bảo vệ hành khách lỡ chuyến nối (Missed Connections & Interline Rebooking)",
                "trigger_reason": (
                    f"Kích hoạt ĐẶC THÙ cho Hãng hàng không truyền thống ({carrier_code_upper}) có mạng lưới trung chuyển: "
                    f"Chặng bay {origin} ➔ {dest} có lượng lớn hành khách nối chuyến tiếp theo sang các điểm đến khác."
                ),
                "statutory_text": (
                    "Hãng hàng không có mạng lưới kết nối bắt buộc phải có phương án bảo đảm chỗ và chuyển tuyến (rebooking) "
                    "cho hành khách bị lỡ chuyến nối chuyến do lỗi chậm chuyến của chặng trước mà không thu thêm phụ phí."
                ),
                "subsections": [
                    {
                        "item": "Khoản (b), Điểm (8)",
                        "requirement": "Tự động kích hoạt cơ chế bảo lưu và chuyển tiếp chuyến bay kế tiếp cùng hãng hoặc hãng đối tác liên danh."
                    },
                    {
                        "item": "Khoản (b), Điểm (4)",
                        "requirement": "Cung cấp phòng khách sạn và dịch vụ đưa đón miễn phí nếu thời gian chờ nối chuyến kéo dài qua đêm."
                    }
                ],
                "severity": "FINANCIAL_RISK",
                "statutory_penalty": "Bồi thường chi phí phát sinh và chịu phạt vi phạm hợp đồng vận chuyển hàng không nếu để rơi khách nối chuyến.",
                "mandatory_action": (
                    "LỆNH CHO PHÒNG ĐẶT CHỖ (PASSENGER REBOOKING): Lọc danh sách hành khách có thời gian nối chuyến (MCT) dưới 45 phút "
                    f"tại sân bay đến {dest}. Tiến hành tự động giữ chỗ (Protect Booking) trên chuyến bay kế tiếp của liên minh."
                ),
                "vietnam_equivalent": "Thông tư 19/2023/TT-BGTVT Điều 8 Khoản 2 Điểm b (Bố trí hành trình phù hợp hoặc chuyển sang chuyến bay khác)."
            })
        else:
            # Hãng giá rẻ (WN, B6, F9, NK): Point-to-point, không có liên danh -> Buộc hoàn tiền mặt theo Mandate 2024
            alerts.append({
                "legal_code": "14 CFR § 260.6(a)(1) & § 260.6(b)",
                "jurisdiction": "Bộ Giao thông Vận tải Hoa Kỳ (US DOT Mandate on Automatic Cash Refunds)",
                "citation": "Điều 260.6, Khoản (a), Điểm (1) & Khoản (b) - Nghĩa vụ hoàn trả tiền mặt tự động khi chậm từ 3 giờ",
                "trigger_reason": (
                    f"Kích hoạt ĐẶC THÙ cho Hãng giá rẻ ({carrier_code_upper}) theo mô hình điểm-nối-điểm (No Interline): "
                    "Không thể chuyển khách sang hãng khác nên bắt buộc phải thực thi nghĩa vụ hoàn tiền mặt trực tiếp."
                ),
                "statutory_text": (
                    "Chuyến bay bị chậm từ 03 giờ trở lên đối với đường bay nội địa là 'Thay đổi lịch bay đáng kể'. "
                    "Hãng bắt buộc hoàn trả 100% tiền vé bằng tiền mặt trong vòng 07 ngày làm việc; cấm ép khách nhận flight voucher."
                ),
                "subsections": [
                    {
                        "item": "Khoản (a), Điểm (1)",
                        "requirement": "Mốc thời gian luật định: Chậm từ 03 tiếng trở lên đối với chặng bay nội địa."
                    },
                    {
                        "item": "Khoản (b)",
                        "requirement": "Nghiêm cấm tự ý cấp voucher tín dụng bay thay cho tiền mặt nếu chưa có sự đồng thuận rõ ràng của khách."
                    }
                ],
                "severity": "FINANCIAL_RISK",
                "statutory_penalty": "Bắt buộc hoàn 100% giá vé gốc bằng tiền mặt kèm chi phí bồi thường chế tài bổ sung.",
                "mandatory_action": (
                    "LỆNH CHO PHÒNG TÀI CHÍNH & VÉ: Nếu thời gian trễ thực tế chạm mốc 150 phút, kích hoạt hệ thống tự động hoàn tiền "
                    "qua cổng thanh toán cho các hành khách từ chối tiếp tục hành trình."
                ),
                "vietnam_equivalent": "Thông tư 19/2023/TT-BGTVT Điều 8 Khoản 2 Điểm c (Chậm từ 05 giờ trở lên bắt buộc hoàn tiền vé)."
            })

        # 3.4. QUY ĐỊNH ĐƯỜNG BAY CHẬM TRỄ KINH NIÊN (CHRONICALLY DELAYED ROUTE)
        # CHỈ áp dụng nếu tuyến bay này trong quá khứ 30 ngày có tỷ lệ trễ >= 30%
        if route_delay_rate >= 0.30:
            alerts.append({
                "legal_code": "14 CFR § 234.11",
                "jurisdiction": "Cục Thống kê Vận tải (US DOT BTS Chronic Delay Directive)",
                "citation": "Điều 234.11 - Kiểm toán và giám sát đặc biệt đường bay chậm trễ kinh niên (Chronically Delayed Flights)",
                "trigger_reason": (
                    f"Kích hoạt ĐẶC THÙ do đường bay {origin}-{dest} có tiền sử trễ kinh niên trong 30 ngày qua ({(route_delay_rate*100):.1f}% >= 30%). "
                    "Thuộc diện giám sát đặc biệt của cơ quan quản lý hàng không liên bang."
                ),
                "statutory_text": (
                    "Chuyến bay bị coi là 'Chậm trễ kinh niên' nếu bị chậm hơn 30 phút với tần suất trên 50% trong một tháng. "
                    "Cơ quan quản lý coi đây là hành vi cạnh tranh không lành mạnh và gian lận lịch bay (Unfair and Deceptive Practice)."
                ),
                "subsections": [
                    {
                        "item": "Điều 234.11, Khoản (a)",
                        "requirement": "Công khai danh sách các chuyến bay chậm kinh niên hàng tháng cho hành khách tra cứu."
                    },
                    {
                        "item": "Điều 234.11, Khoản (d)",
                        "requirement": "Hãng bay có nghĩa vụ giải trình nguyên nhân và kế hoạch khắc phục triệt để bằng văn bản."
                    }
                ],
                "severity": "REGULATORY_AUDIT",
                "statutory_penalty": "Bị thanh tra toàn diện, phạt vi phạm theo 49 U.S.C. § 41712 và có nguy cơ bị tước quyền cất hạ cánh (Slot Allocation).",
                "mandatory_action": (
                    f"LỆNH CHO PHÒNG LẬP LỊCH BAY (NETWORK PLANNING): Tuyến {origin}-{dest} đang trong 'vùng đỏ' kiểm toán kinh niên. "
                    "Bắt buộc nới rộng thời gian quay đầu (Turnaround buffer) thêm 20 phút trong lịch bay mùa tới để tránh bị tước slot."
                ),
                "vietnam_equivalent": "Thông tư 81/2014/TT-BGTVT Điều 25 (Giám sát slot và giờ cất hạ cánh tại các cảng hàng không quá tải)."
            })

    # Xây dựng bản tóm tắt pháp lý điều hành riêng biệt cho chuyến bay này
    applied_codes = [a["legal_code"] for a in alerts]
    summary_text = (
        f"Chuyến bay {carrier_code_upper} ({origin} ➔ {dest}) lúc {dep_hour}:00 đang chịu sự điều chỉnh của {len(alerts)} quy chuẩn: "
        f"{', '.join(applied_codes)}. Các quy chuẩn này được hệ thống chọn lọc riêng biệt dựa trên khung giờ, mật độ sân bay và mô hình hãng bay."
    )

    return {
        "regulatory_framework": "US DOT Title 14 CFR, FAA FAR Part 117 & Vietnam CAAV Alignments",
        "compliance_status": "HIGH_COMPLIANCE_RISK" if is_high_risk else ("MONITORING_REQUIRED" if is_elevated_risk else "COMPLIANT_ON_TIME"),
        "total_regulations_evaluated": len(alerts),
        "critical_violations_risk_count": sum(1 for a in alerts if a["severity"] == "CRITICAL"),
        "legal_evaluations": alerts,
        "executive_legal_summary": summary_text,
    }
