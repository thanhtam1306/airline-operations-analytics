"""
Aviation & Machine Learning Knowledge Engine (OCC Decision & Knowledge Copilot).

Serves as the standardized, domain-grounded knowledge repository and mentor for
Operations Control Center (OCC) dispatchers, analysts, and business users.
Provides definitions, mathematical formulas, regulatory boundaries, operational
implications, and Standard Operating Procedure (SOP) checklists.

Comprehensive Enterprise Suite: 40 Knowledge Items (18 Aviation + 14 ML + 8 SOPs).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class KnowledgeTerm:
    term_id: str
    name_vi: str
    name_en: str
    acronym: Optional[str]
    category: str  # "aviation_metrics", "ml_metrics", "operational_concepts"
    definition_vi: str
    business_significance: str
    calculation_or_rule: str
    operational_impact: str
    keywords: List[str]
    related_regulations: List[str] = field(default_factory=list)
    common_questions: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SOPStep:
    step_number: int
    action_vi: str
    responsible_role: str
    timeframe: str
    verification_criteria: str
    regulatory_notice: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SOPChecklist:
    sop_id: str
    title_vi: str
    title_en: str
    purpose: str
    target_roles: List[str]
    trigger_condition: str
    steps: List[SOPStep]
    contingency_fallback: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["steps"] = [s.to_dict() if isinstance(s, SOPStep) else s for s in self.steps]
        return d


# =============================================================================
# 1. KNOWLEDGE BASE REPOSITORY (DICTIONARY & DOMAIN KNOWLEDGE - 32 TERMS)
# =============================================================================

KNOWLEDGE_TERMS: Dict[str, KnowledgeTerm] = {
    # -------------------------------------------------------------------------
    # NHÓM 1: 18 CHỈ SỐ VẬN HÀNH & PHÁP LÝ HÀNG KHÔNG (AVIATION METRICS)
    # -------------------------------------------------------------------------
    "fdp": KnowledgeTerm(
        term_id="fdp",
        name_vi="Thời Gian Làm Nhiệm Vụ Bay (FDP)",
        name_en="Flight Duty Period",
        acronym="FDP",
        category="aviation_metrics",
        definition_vi=(
            "Thời gian làm nhiệm vụ bay của thành viên tổ lái (phi công) bắt đầu khi phi công "
            "báo cáo nhiệm vụ (Report time) cho chuyến bay hoặc chuỗi chuyến bay và kết thúc khi "
            "tàu bay đỗ vào vị trí cuối cùng sau chặng bay cuối, tắt động cơ và các thành viên tổ lái "
            "không còn nghĩa vụ vận hành tiếp theo."
        ),
        business_significance=(
            "FDP là rào cản an toàn nghiêm ngặt nhất trong vận hành hàng không. Khi chuyến bay bị "
            "chậm (delay), nguy cơ tổ bay hết giờ làm việc hợp pháp (Crew Time-out) tăng vọt. "
            "Nếu tổ bay chạm trần FDP mà chưa cất cánh, chuyến bay bắt buộc phải hủy hoặc hoãn chờ "
            "tổ bay dự bị (Standby Crew), gây thiệt hại kinh tế dây chuyền hàng chục nghìn USD."
        ),
        calculation_or_rule=(
            "Căn cứ: FAA Title 14 CFR Part 117 (Table B - Flight Duty Period for Unaugmented Operations). "
            "Trần FDP dao động từ 9.0 đến 14.0 giờ tùy thuộc vào giờ trình diện (Report Time) và số chặng bay (Sectors). "
            "Thời điểm nhạy cảm nhất là Vùng Suy Giảm Sinh Học Khí Sắc (WOCL: 02:00 - 05:59). "
            "Quy tắc nới lỏng (Extension): Theo 14 CFR § 117.19(a)(1), FDP trước cất cánh chỉ được gia hạn tối đa "
            "02 giờ khi có sự đồng thuận ký nhận bằng văn bản giữa Cơ trưởng (PIC) và Điều phái viên (Dispatcher)."
        ),
        operational_impact=(
            "Đình chỉ bay ngay lập tức nếu vi phạm trần FDP. Hãng hàng không bị xử phạt vi phạm hành chính, "
            "Cơ trưởng bị đình chỉ bằng lái tạm thời để điều tra."
        ),
        keywords=[
            "fdp", "flight duty period", "thoi gian lam nhiem vu", "gio bay phi cong",
            "het gio bay", "crew time out", "crew timeout", "part 117", "wocl", "to bay"
        ],
        related_regulations=[
            "14 CFR § 117.11(a) (Giới hạn giờ bay tối đa hàng ngày)",
            "14 CFR § 117.19(a)(1) (Gia hạn FDP trước cất cánh)",
            "VAR Part 12 (Quy chế An toàn Hàng không Dân dụng Việt Nam)"
        ],
        common_questions=[
            {
                "q": "Khi chuyến bay chậm 90 phút vào lúc 19:00, tổ bay có bị time-out không?",
                "a": "Cần kiểm tra giờ báo cáo đầu ngày và số chặng đã bay của tổ bay. Sau 17:00, trần FDP bị thu hẹp đáng kể theo Table B. Nếu dự kiến thời gian hạ cánh vượt FDP tối đa, OCC phải kích hoạt Standby Crew ngay trước khi đóng cửa tàu bay."
            }
        ]
    ),

    "tarmac_delay": KnowledgeTerm(
        term_id="tarmac_delay",
        name_vi="Chậm Chuyến Trên Đường Lăn / Sân Đỗ (Tarmac Delay)",
        name_en="Tarmac Delay Rule",
        acronym="TARMAC",
        category="aviation_metrics",
        definition_vi=(
            "Thời gian tàu bay bị giữ lại trên đường lăn hoặc bãi đỗ sau khi đã đóng cửa hành khách "
            "để cất cánh (Taxi-out), hoặc thời gian tàu bay đã hạ cánh nhưng chưa được cập cầu/cửa "
            "cho hành khách rời tàu bay (Taxi-in)."
        ),
        business_significance=(
            "Bảo vệ nhân phẩm và quyền lợi cơ bản của hành khách, ngăn chặn việc giam giữ hành khách "
            "trong khoang kín ngột ngạt không có lối thoát khi sân bay tắc nghẽn hoặc thời tiết xấu."
        ),
        calculation_or_rule=(
            "Căn cứ: US DOT 14 CFR § 259.4 (Contingency Plan for Lengthy Tarmac Delays). "
            "1. Giới hạn thời gian tối đa: Không được vượt quá 03 GIỜ đối với chuyến bay nội địa Hoa Kỳ "
            "và 04 GIỜ đối với chuyến bay quốc tế mà không cho hành khách rời tàu bay (Deplane). "
            "2. Mốc phục vụ thiết yếu: Tại mốc 02 GIỜ, hãng bắt buộc phải phục vụ nước uống và đồ ăn nhẹ "
            "đầy đủ cho toàn bộ hành khách, duy trì điều hòa khoang khách và phòng vệ sinh hoạt động tốt. "
            "3. Chế tài tài chính: Theo 49 U.S.C. § 46301, mức phạt dân sự lên tới $37,377 USD cho MỖI hành khách trên chuyến bay vi phạm."
        ),
        operational_impact=(
            "Nếu chuyến bay có 180 khách vi phạm mốc 3 giờ, tổng mức phạt có thể lên tới 6.7 triệu USD! "
            "OCC phải ban hành lệnh 'Gate Hold' hoặc 'Taxi Return' (quay đầu về cửa) muộn nhất ở phút 150."
        ),
        keywords=[
            "tarmac delay", "cham tren duong lan", "ket tren san do", "san do", "duong lan",
            "part 259", "259.4", "3 gio", "4 gio", "gate return", "deplane", "phat tarmac"
        ],
        related_regulations=[
            "14 CFR § 259.4(b)(1) (Giới hạn 3h nội địa / 4h quốc tế)",
            "14 CFR § 259.4(b)(1)(i) (Phục vụ đồ ăn nước uống tại mốc 2h)",
            "Thông tư 19/2023/TT-BGTVT Điều 8 Khoản 2 Điểm a"
        ],
        common_questions=[
            {
                "q": "Khi nào đồng hồ Tarmac Delay bắt đầu đếm?",
                "a": "Bắt đầu đếm ngay thời điểm cửa ra tàu bay (Cabin Door) được đóng lại và chèn bánh được rút (Push-back/Brakes released)."
            }
        ]
    ),

    "otp": KnowledgeTerm(
        term_id="otp",
        name_vi="Tỷ Lệ Đúng Giờ (On-Time Performance - OTP)",
        name_en="On-Time Performance (A14 Standard)",
        acronym="OTP",
        category="aviation_metrics",
        definition_vi=(
            "Chỉ số đo lường tỷ lệ phần trăm các chuyến bay cất cánh hoặc hạ cánh đúng giờ so với lịch bay thương mại đã công bố."
        ),
        business_significance=(
            "Thước đo uy tín thương hiệu và năng lực điều hành số 1 của hãng hàng không. "
            "OTP cao giúp giảm chi phí bồi thường, tối ưu hóa vòng quay tàu bay và tăng chỉ số hài lòng của khách hàng (NPS)."
        ),
        calculation_or_rule=(
            "Chuẩn US DOT BTS (A14 Standard): Một chuyến bay được coi là 'ĐÚNG GIỜ' nếu thời gian đến thực tế (Actual In) "
            "chậm KHÔNG QUÁ 14 PHÚT so với giờ đến dự kiến (Scheduled In) ghi trên vé. "
            "Từ phút thứ 15 trở đi được tính là Trễ (Delayed - D15+). "
            "Công thức: OTP (%) = (Số chuyến bay đến trễ <= 14 phút) / (Tổng số chuyến bay thực hiện) * 100%."
        ),
        operational_impact=(
            "Xếp hạng công khai hàng tháng trên báo cáo Air Travel Consumer Report của DOT. "
            "Hãng xếp chót bảng thường chịu áp lực lớn từ cổ đông và khách hàng doanh nghiệp."
        ),
        keywords=[
            "otp", "on time performance", "ty le dung gio", "a14", "dung gio",
            "14 phut", "15 phut", "tieu chuan bts", "chi so dung gio"
        ],
        related_regulations=[
            "14 CFR Part 234 (Airline Service Quality Performance Reports)"
        ],
        common_questions=[
            {
                "q": "Tại sao chuyến bay trễ 14 phút vẫn được tính là đúng giờ?",
                "a": "Chuẩn A14 quốc tế (DOT/IATA) cho phép biên độ dung sai 14 phút để dung hòa các biến số điều hành thông thường (xếp hàng đường lăn, thời tiết vi mô, thủ tục cập cầu)."
            }
        ]
    ),

    "d0_d15": KnowledgeTerm(
        term_id="d0_d15",
        name_vi="Đúng Giờ Khởi Hành Tuyệt Đối D0 & Chuẩn D15",
        name_en="Departure Punctuality (D0 on-the-dot vs D15 BTS)",
        acronym="D0/D15",
        category="aviation_metrics",
        definition_vi=(
            "D0: Tỷ lệ chuyến bay rút chèn rời cửa khởi hành (Gate Out) đúng từng phút hoặc sớm hơn giờ lịch trình (Scheduled Departure Time). "
            "D15: Tỷ lệ chuyến bay khởi hành trễ từ 15 phút trở lên theo quy chuẩn US DOT BTS."
        ),
        business_significance=(
            "D0 là tôn chỉ sống còn của các hãng hàng không giá rẻ (LCC như Southwest, Ryanair, Vietjet Air). "
            "Nếu D0 bị trễ dù chỉ 5 phút, toàn bộ chuỗi 6-8 chặng bay tiếp theo trong ngày của tàu bay sẽ vỡ trận. "
            "D15 là chỉ số giám sát chất lượng dịch vụ trước nhà chức trách."
        ),
        calculation_or_rule=(
            "D0: actual_dep <= scheduled_dep (delay <= 0 phút). "
            "D15: dep_delay >= 15 phút. "
            "Hãng hàng không đỉnh cao duy trì D0 >= 75% và D15 <= 12%."
        ),
        operational_impact=(
            "D0 trực tiếp quyết định thời gian giải tỏa cửa đón khách (Gate clearance) và năng suất nhân viên mặt đất."
        ),
        keywords=[
            "d0", "d15", "khoi hanh dung gio", "departure delay", "on the dot", "gate departure", "d0 lcc"
        ],
        related_regulations=["US DOT Form 41 Schedule P-5.2"],
        common_questions=[{"q": "Tại sao LCC lại quan tâm D0 hơn là D15?", "a": "Vì thời gian quay đầu của LCC chỉ 25-30 phút, trễ 5 phút ở chặng 1 sẽ tích lũy thành trễ 45 phút ở chặng 5."}]
    ),

    "taxi_out_in": KnowledgeTerm(
        term_id="taxi_out_in",
        name_vi="Thời Gian Lăn Bánh Ra/Vào (Taxi-Out & Taxi-In)",
        name_en="Taxi-Out and Taxi-In Duration",
        acronym="TAXI",
        category="aviation_metrics",
        definition_vi=(
            "Taxi-Out: Khoảng thời gian từ lúc tàu bay rút chèn rời cửa (Gate Out) đến khi bánh rời mặt đất (Wheels Off). "
            "Taxi-In: Khoảng thời gian từ lúc bánh chạm đường băng (Wheels On) đến khi tàu bay đỗ lại tại cổng (Gate In)."
        ),
        business_significance=(
            "Thời gian lăn phản ánh trực tiếp mức độ tắc nghẽn mặt đất (Ground Congestion). "
            "Taxi-out kéo dài gây tiêu hao nhiên liệu mặt đất khổng lồ, phát thải CO2 và gia tăng nguy cơ vi phạm Tarmac Delay."
        ),
        calculation_or_rule=(
            "Taxi-Out = dep_time (Actual Wheels Off) - actual_dep (Actual Gate Departure). "
            "Taxi-In = actual_arr (Actual Gate In) - arr_time (Actual Wheels On). "
            "Benchmark chuẩn: 12 - 18 phút tại sân bay thông thường; 20 - 35 phút tại siêu hub (JFK, ORD, ATL, LAX). "
            "Nếu Taxi-out > 40 phút, hệ thống phát tín hiệu cảnh báo nghẽn cục bộ."
        ),
        operational_impact=(
            "Tổn hao hàng nghìn tấn nhiên liệu hàng năm và làm chậm giờ đến của tàu bay (Arrival Delay)."
        ),
        keywords=[
            "taxi out", "taxi in", "thoi gian lan", "lan banh", "wheels off",
            "wheels on", "gate out", "gate in", "duong lan mat dat"
        ],
        related_regulations=[
            "FAA Airport Surface Detection Equipment (ASDE-X) Operational Guidelines"
        ],
        common_questions=[
            {
                "q": "Taxi-out cao có làm trễ chuyến bay không nếu cất cánh bay nhanh hơn?",
                "a": "Có thể được bù đắp một phần nhờ 'Make-up Time' trên không, nhưng nếu Taxi-out vượt quá 30 phút thì phần lớn chuyến bay sẽ đến trễ so với lịch trình."
            }
        ]
    ),

    "turnaround_time": KnowledgeTerm(
        term_id="turnaround_time",
        name_vi="Thời Gian Quay Đầu Tàu Bay (Turnaround Time - TAT)",
        name_en="Aircraft Turnaround Time (Chocks-on to Chocks-off)",
        acronym="TAT",
        category="aviation_metrics",
        definition_vi=(
            "Tổng thời gian từ khi tàu bay dừng hẳn tại cổng chặng trước, chèn bánh được cài (Chocks-on / Gate In) "
            "cho đến khi hoàn tất trả khách, dọn vệ sinh, tra nạp nhiên liệu, nhận hàng hóa hành lý mới và rút chèn (Chocks-off / Gate Out) "
            "để thực hiện chặng bay tiếp theo."
        ),
        business_significance=(
            "Chỉ số hiệu quả sử dụng tài sản (Asset Utilization) quan trọng nhất của hãng hàng không. "
            "Máy bay chỉ sinh ra tiền khi đang bay trên trời; nằm dưới đất là cỗ máy đốt tiền. "
            "Rút ngắn 10 phút TAT cho phép hãng thực hiện thêm 1 chuyến bay mỗi ngày trên mỗi tàu bay."
        ),
        calculation_or_rule=(
            "TAT = Actual Gate Out (Flight N) - Actual Gate In (Flight N-1). "
            "Benchmark: LCC thân hẹp (A320/B737) = 25 - 35 phút; Legacy Carrier = 45 - 60 phút; Tàu bay thân rộng (B787/A350) = 90 - 120 phút. "
            "Nếu TAT thực tế < TAT tối thiểu cho phép, vi phạm quy trình kiểm tra kỹ thuật an toàn."
        ),
        operational_impact=(
            "Nếu bất kỳ mắt xích nào bị trễ (tra xăng chậm, thiếu xe thang, khách chậm lên máy bay), "
            "TAT bị kéo dài và dẫn thẳng đến Cascading Delay."
        ),
        keywords=["turnaround", "tat", "quay dau", "chocks on", "chocks off", "tra xang", "don ve sinh", "quay dau tau bay"],
        related_regulations=["ICAO Annex 6 - Aircraft Ground Handling and Pre-flight Inspection"],
        common_questions=[{"q": "Làm thế nào Southwest Airlines đạt được TAT 25 phút huyền thoại?", "a": "Họ sử dụng chính sách không chỉ định chỗ ngồi (Open seating) giúp khách lên tàu bay nhanh gấp đôi và phi hành đoàn cùng tham gia dọn cabin."}]
    ),

    "block_time_air_time": KnowledgeTerm(
        term_id="block_time_air_time",
        name_vi="Thời Gian Chèn Bánh vs Thời Gian Bay Thực Tế (Block Time vs Air Time)",
        name_en="Block Time vs Airborne Flight Time",
        acronym="BLOCK/AIR",
        category="aviation_metrics",
        definition_vi=(
            "Block Time (Giờ chèn bánh): Từ thời điểm rút chèn bánh tại cổng xuất phát đến khi chèn bánh tại cổng đích. "
            "Air Time (Giờ bay trên không): Từ lúc bánh rời mặt đất (Wheels-off) đến khi bánh chạm mặt đất (Wheels-on)."
        ),
        business_significance=(
            "Block Time là cơ sở tính lương cho phi công và tiếp viên, tính giờ bảo dưỡng định kỳ khung thân tàu bay, "
            "và là căn cứ ký kết hợp đồng thuê ướt/thuê khô tàu bay (Wet-lease ACMI)."
        ),
        calculation_or_rule=(
            "Block Time = Actual Gate In - Actual Gate Out = Taxi-Out + Air Time + Taxi-In. "
            "Tỷ lệ hiệu quả hành trình: Air Time / Block Time thường đạt 75% - 85% trên chặng trung bình; "
            "nếu tỷ lệ này < 60% nghĩa là tàu bay mất quá nhiều thời gian nằm chờ trên đường lăn mặt đất."
        ),
        operational_impact=("Block Time vượt định mức làm tăng vọt chi phí nhân công và nhiên liệu mặt đất."),
        keywords=["block time", "air time", "gio chen banh", "gio bay thuc te", "acmi", "luong phi cong", "taxi time"],
        related_regulations=["FAA FAR Part 1 § 1.1 (General Definitions - Time in Service & Flight Time)"],
        common_questions=[{"q": "Phi công được trả lương theo Block Time hay Air Time?", "a": "Theo thông lệ quốc tế và FAR Part 1, phi công được trả lương theo Block Time tính từ lúc rút chèn (Pushback) đến khi đỗ vào cổng."}]
    ),

    "schedule_padding": KnowledgeTerm(
        term_id="schedule_padding",
        name_vi="Độn Lịch Bay / Thời Gian Đệm (Schedule Padding)",
        name_en="Schedule Padding (Buffer Time Inflation)",
        acronym="PADDING",
        category="aviation_metrics",
        definition_vi=(
            "Khoảng thời gian dôi dư được hãng hàng không cố tình cộng thêm vào tổng thời gian bay dự kiến "
            "(Scheduled Block Time) so với thời gian bay thực tế thuần túy trong điều kiện lý tưởng."
        ),
        business_significance=(
            "Chiến lược quản trị rủi ro hai mặt: Một mặt giúp hấp thụ tắc nghẽn giờ cao điểm và bảo vệ chỉ số đúng giờ OTP; "
            "mặt khác làm giảm năng suất sử dụng máy bay và tăng chi phí vé cho hành khách."
        ),
        calculation_or_rule=(
            "Schedule Padding = Scheduled Block Time - 50th Percentile Historical Actual Block Time. "
            "Ví dụ: Tuyến JFK - ORD bay thực tế mất 2h10m, nhưng hãng lên lịch 2h45m -> Padding = 35 phút. "
            "Nếu Padding quá mức (> 40 phút), tuyến bay có nguy cơ bị US DOT điều tra về hành vi 'Lên lịch bay thiếu trung thực' (Unrealistic Scheduling)."
        ),
        operational_impact=("Giúp tỷ lệ đúng giờ trông đẹp mắt trên báo cáo nhưng giấu đi sự tắc nghẽn thực sự của sân bay."),
        keywords=["schedule padding", "padding", "don lich bay", "thoi gian dem", "unrealistic scheduling", "gio ao", "bao ke otp"],
        related_regulations=["14 CFR § 234.12 (Prohibition of Unrealistic Flight Schedules)"],
        common_questions=[{"q": "Tại sao cùng một chặng bay mà chuyến bay buổi tối lại có thời gian ghi trên vé dài hơn chuyến buổi sáng?", "a": "Vì buổi tối là khung giờ tắc nghẽn Hub, hãng chủ động độn thêm 20-30 phút padding vào vé để tránh bị tính là trễ."}]
    ),

    "makeup_time": KnowledgeTerm(
        term_id="makeup_time",
        name_vi="Khả Năng Bù Giờ Trên Không (Airborne Make-up Time)",
        name_en="Airborne Make-up Time",
        acronym="MAKE-UP",
        category="aviation_metrics",
        definition_vi=(
            "Khả năng hấp thụ hoặc rút ngắn thời gian bay trên không (Airborne) so với lịch trình dự kiến "
            "nhờ tăng công suất bay (Cruise Mach), bay đường tắt (Direct routing do ATC cấp), "
            "hoặc tận dụng luồng gió xuôi (Tailwind / Jetstream)."
        ),
        business_significance=(
            "Vũ khí chiến thuật của phi hành đoàn và OCC để 'cứu' một chuyến bay bị chậm khởi hành, "
            "giúp hạ cánh đúng giờ và bảo vệ chỉ số OTP cho chuyến bay tiếp theo."
        ),
        calculation_or_rule=(
            "Make-up Time = dep_delay_min - arr_delay_min. "
            "Nếu giá trị > 0: Chuyến bay đã bù được thời gian trên không (ví dụ trễ cất cánh 30m nhưng hạ cánh chỉ trễ 10m -> Make-up = +20m). "
            "Chuyến bay chặng dài (> 1000 dặm) có biên độ bù giờ từ 15-25 phút; chặng ngắn (< 300 dặm) hầu như không có cơ hội bù giờ."
        ),
        operational_impact=(
            "Đòi hỏi tiêu tốn thêm lượng nhiên liệu đáng kể khi tăng Cost Index / Cruise Speed. "
            "OCC Dispatcher cần cân nhắc chi phí nhiên liệu phụ trội so với chi phí phạt chậm trễ."
        ),
        keywords=[
            "make up time", "bu gio", "bu gio tren khong", "airborne makeup",
            "rut ngan gio bay", "tang toc", "tailwind", "cost index"
        ],
        related_regulations=[
            "ICAO Flight Planning & Fuel Conservation Standards"
        ],
        common_questions=[
            {
                "q": "Có thể bù tối đa bao nhiêu phút cho một chuyến bay nội địa?",
                "a": "Thường từ 10 đến 25 phút trên các chặng xuyên bang (Transcontinental), phụ thuộc vào độ mạnh của luồng gió Jetstream và giới hạn tốc độ trần Vmo/Mmo của tàu bay."
            }
        ]
    ),

    "cascading_delay": KnowledgeTerm(
        term_id="cascading_delay",
        name_vi="Trễ Dây Chuyền / Hiệu Ứng Domino (Cascading / Late Aircraft Delay)",
        name_en="Cascading Delay (Domino Effect)",
        acronym="LATE_AC",
        category="aviation_metrics",
        definition_vi=(
            "Hiện tượng một chuyến bay khởi hành muộn do phải chờ tàu bay (Aircraft) hoặc phi hành đoàn "
            "(Flight/Cabin Crew) đến muộn từ chặng bay trước đó trong chuỗi lịch trình bay trong ngày."
        ),
        business_significance=(
            "Chiếm tỷ trọng lớn nhất (~35% - 45%) trong tổng số phút trễ của các hãng hàng không. "
            "Một sự cố nhỏ buổi sáng tại Hub có thể khuếch đại thành thảm họa trễ toàn mạng vào buổi chiều tối."
        ),
        calculation_or_rule=(
            "Căn cứ: BTS 14 CFR § 234.4(a)(17) - Late Aircraft Delay. "
            "Xảy ra khi: Actual Arrival (Chặng N-1) + Minimum Turnaround Time > Scheduled Departure (Chặng N). "
            "Thời gian quay đầu tối thiểu (Turnaround Buffer) của máy bay thân hẹp thường từ 35-50 phút."
        ),
        operational_impact=(
            "Gây vỡ lịch phân bổ cửa đón khách (Gate conflict), hành khách lỡ chuyến bay chuyển tiếp (Missed connection), "
            "và đẩy tổ bay vào nguy cơ chạm trần FDP."
        ),
        keywords=[
            "cascading delay", "tre day chuyen", "domino", "late aircraft", "tau bay den muon",
            "cho tau bay", "turnaround", "quay dau", "hieu ung domino"
        ],
        related_regulations=[
            "14 CFR § 234.4(a)(17) (Báo cáo nguyên nhân Late Aircraft Delay)",
            "IATA Worldwide Airport Slot Guidelines (WASG)"
        ],
        common_questions=[
            {
                "q": "Làm thế nào để chặn đứng hiệu ứng Domino trễ dây chuyền?",
                "a": "OCC có 3 giải pháp chính: 1) Hoán đổi tàu bay (Aircraft Swap) nếu có tàu bay dự bị hoặc tàu bay rỗi; 2) Bỏ chặng (Cancellation/Consolidation) nếu quá tải; 3) Tái cấu trúc lịch bay tăng Turnaround buffer vào mùa sau."
            }
        ]
    ),

    "hub_congestion": KnowledgeTerm(
        term_id="hub_congestion",
        name_vi="Tắc Nghẽn Tại Trung Tâm Điều Hành (Hub Congestion)",
        name_en="Hub Congestion & Saturation",
        acronym="HUB_SAT",
        category="aviation_metrics",
        definition_vi=(
            "Tình trạng nhu cầu cất/hạ cánh của các chuyến bay vượt quá năng lực tiếp thu tối đa (Acceptance Rate) "
            "của hệ thống đường băng và đường lăn tại các sân bay căn cứ trung tâm (Mega Hubs: ATL, ORD, DFW, DEN, JFK) "
            "vào các khung giờ ngân hàng cao điểm (Bank Hours)."
        ),
        business_significance=(
            "Các Hub là trái tim của mô hình kinh doanh Hub-and-Spoke. Khi Hub bị tắc nghẽn, "
            "toàn bộ các nhánh bay đi và đến đều bị đóng băng, làm bùng nổ chi phí chờ đợi."
        ),
        calculation_or_rule=(
            "Chỉ số: Số chuyến bay cất cánh dự kiến trong giờ (scheduled_departures_hour). "
            "Ngưỡng: >= 8 chuyến/giờ tại một nhà ga hoặc >= 40 chuyến/giờ trên toàn sân bay được phân loại là High Congestion. "
            "Khung giờ cao điểm thông thường: 17:00 - 20:59."
        ),
        operational_impact=(
            "ATC kích hoạt Ground Delay Program (GDP) hoặc cấp giờ cất cánh kỳ vọng (EDCT - Expect Departure Clearance Time), "
            "buộc máy bay phải chờ tại sân bay xuất phát trước khi cất cánh đến Hub."
        ),
        keywords=[
            "hub congestion", "tac nghen hub", "san bay trung tam", "mega hub",
            "gdp", "ground delay program", "edct", "bank hours", "gio cao diem", "atl", "ord", "dfw"
        ],
        related_regulations=[
            "FAA Order JO 7210.3 (Facility Operation and Administration - Traffic Management)"
        ],
        common_questions=[
            {
                "q": "Tại sao các hãng hàng không vẫn thích dồn chuyến vào cùng một khung giờ tại Hub?",
                "a": "Để tối ưu thời gian nối chuyến (Connecting Time) cho hành khách giữa các chuyến bay đến và đi (Wave/Bank structure), tăng khả năng cạnh tranh mạng bay."
            }
        ]
    ),

    "ground_stop": KnowledgeTerm(
        term_id="ground_stop",
        name_vi="Lệnh Ngừng Mặt Đất Toàn Diện (Ground Stop - GS)",
        name_en="Air Traffic Control Ground Stop",
        acronym="GS",
        category="aviation_metrics",
        definition_vi=(
            "Biện pháp quản lý không lưu khẩn cấp nghiêm ngặt nhất do Trung tâm Chỉ huy Không lưu (FAA ATCSCC) ban hành, "
            "yêu cầu tất cả các chuyến bay chuẩn bị bay đến một sân bay cụ thể phải nằm im tại mặt đất ở sân bay xuất phát, "
            "tuyệt đối không được cấp lệnh cất cánh."
        ),
        business_significance=(
            "Biện pháp phòng ngừa sự cố tràn ngập không phận khi sân bay đến bị tê liệt hoàn toàn "
            "(do bão dông quét qua, bão tuyết, mất điện radar, hoặc tai nạn đường băng)."
        ),
        calculation_or_rule=(
            "Tỷ lệ tiếp thu sân bay AAR (Airport Acceptance Rate) bị hạ về 0 chuyến/giờ. "
            "Thời gian hiệu lực thường được gia hạn từng 30-60 phút. Khi có GS, mọi dự báo thời gian bay đều bị vô hiệu hóa."
        ),
        operational_impact=("Đẩy hàng loạt chuyến bay vào trạng thái hoãn vô thời hạn, kích hoạt Gate Hold để tránh bẫy Tarmac Delay."),
        keywords=["ground stop", "gs", "lenh dung bay mat dat", "dong bang san bay", "aar", "atcscc", "cam cat canh"],
        related_regulations=["FAA Order 7210.3 Section 17-5 (Ground Stop Operations)"],
        common_questions=[{"q": "Khi có Ground Stop, máy bay đã đóng cửa có được lăn ra chờ không?", "a": "Không! OCC phải yêu cầu giữ máy bay tại cửa (Gate Hold) hoặc mở lại cửa cho khách vào nhà ga."}]
    ),

    "gdp_edct": KnowledgeTerm(
        term_id="gdp_edct",
        name_vi="Chương Trình Giãn Cách Giờ Bay & Khe EDCT (GDP & EDCT)",
        name_en="Ground Delay Program & Expect Departure Clearance Time",
        acronym="GDP/EDCT",
        category="aviation_metrics",
        definition_vi=(
            "GDP: Biện pháp điều hòa luồng khi năng lực tiếp thu của sân bay đích bị suy giảm nhưng chưa đến mức tê liệt. "
            "EDCT: Giờ cất cánh ấn định mà máy bay bắt buộc phải tuân thủ để đến sân bay đích đúng khe tiếp nhận còn trống."
        ),
        business_significance=(
            "Thay vì để máy bay bay lên rồi phải lượn vòng tốn xăng trên trời (Holding Pattern), "
            "ATC ép máy bay chịu trễ trên mặt đất tại sân bay xuất phát (Ground Delay) để tiết kiệm nhiên liệu và bảo đảm an toàn."
        ),
        calculation_or_rule=(
            "Cửa sổ dung sai cất cánh của EDCT là +/- 5 phút (từ EDCT - 5m đến EDCT + 5m). "
            "Nếu cất cánh ngoài cửa sổ này, chuyến bay vi phạm quy định điều phối không lưu quốc gia."
        ),
        operational_impact=("OCC phải điều phối quy trình đẩy lùi và nổ máy sao cho bánh rời đất chính xác trong cửa sổ 10 phút của EDCT."),
        keywords=["gdp", "edct", "ground delay program", "expect departure clearance time", "khe cat canh", "holding pattern"],
        related_regulations=["FAA Order 7210.3 Section 17-4 (Ground Delay Programs)"],
        common_questions=[{"q": "Nếu lỡ mất giờ EDCT thì sao?", "a": "Chuyến bay sẽ bị mất lượt cất cánh và phải xếp hàng lại từ đầu ở cuối danh sách phân luồng, thời gian trễ có thể tăng thêm 2-3 giờ."}]
    ),

    "airport_slot_8020": KnowledgeTerm(
        term_id="airport_slot_8020",
        name_vi="Khe Giờ Cất Hạ Cánh & Quy Tắc 80/20 (Airport Slot & 80/20 Rule)",
        name_en="Airport Slot Allocation (80/20 'Use-it-or-Lose-it' Rule)",
        acronym="SLOT 80/20",
        category="aviation_metrics",
        definition_vi=(
            "Quyền khai thác một khung giờ cất cánh hoặc hạ cánh tại các sân bay cấp 3 bị hạn chế năng lực (Level 3 Coordinated Airports: JFK, LGA, DCA, LHR, HND). "
            "Quy tắc 80/20: Hãng bay bắt buộc phải khai thác thực tế tối thiểu 80% số slot được cấp trong suốt mùa lịch bay."
        ),
        business_significance=(
            "Slot tại các siêu sân bay như London Heathrow hay New York JFK có giá trị tài sản vô hình hàng chục triệu USD. "
            "Nếu vi phạm quy tắc 80/20, hãng sẽ bị tịch thu slot và trao cho hãng đối thủ cạnh tranh."
        ),
        calculation_or_rule=(
            "Slot Utilization Rate = (Số chuyến bay thực tế thực hiện trên slot) / (Tổng số slot được phân bổ) * 100%. "
            "Nếu tỷ lệ < 80% (không có lý do bất khả kháng được công nhận), quyền lịch sử (Grandfather Rights) bị bãi bỏ."
        ),
        operational_impact=("Buộc các hãng đôi khi phải bay 'chuyến bay ma' (Ghost Flights) chỉ để giữ quyền sở hữu slot."),
        keywords=["slot", "airport slot", "80 20", "use it or lose it", "level 3 airport", "khe gio cat ha canh", "slot bay"],
        related_regulations=["IATA Worldwide Airport Slot Guidelines (WASG)", "14 CFR Part 93 (High Density Traffic Airports)"],
        common_questions=[{"q": "Tại sao các hãng không hủy bớt chuyến vào mùa vắng khách?", "a": "Vì nếu hủy quá 20% số chuyến, họ sẽ mất vĩnh viễn slot cất hạ cánh vào tay đối thủ trong mùa cao điểm sau."}]
    ),

    "curfew": KnowledgeTerm(
        term_id="curfew",
        name_vi="Giờ Giới Nghiêm Tiếng Ồn Sân Bay (Airport Night Curfew)",
        name_en="Airport Night Curfew & Noise Abatement",
        acronym="CURFEW",
        category="aviation_metrics",
        definition_vi=(
            "Quy định pháp lý của chính quyền địa phương hoặc nhà chức trách hàng không cấm hoàn toàn hoặc "
            "hạn chế ngặt nghèo các chuyến bay phản lực cất/hạ cánh vào ban đêm (thường từ 23:00 đến 06:00 sáng) "
            "nhằm chống ô nhiễm tiếng ồn cho khu dân cư phụ cận."
        ),
        business_significance=(
            "Đòn bẩy thời gian nguy hiểm: Một chuyến bay khởi hành muộn có nguy cơ đến sân bay đích sau giờ giới nghiêm. "
            "Nếu chạm trần Curfew, máy bay không được phép hạ cánh và bắt buộc phải chuyển hướng (Divert)."
        ),
        calculation_or_rule=(
            "Estimated Arrival Time (ETA) > Curfew Start Time (ví dụ 23:00). "
            "Mức phạt vi phạm giới nghiêm cực kỳ khốc liệt (từ $10,000 đến $50,000 USD mỗi lần hạ cánh trái phép tại Sydney, Frankfurt, Burbank)."
        ),
        operational_impact=("OCC phải tính toán tốc độ bay (tăng Cost Index) để hạ cánh trước 22:59 hoặc hủy/đổi lịch bay sớm."),
        keywords=["curfew", "gio gioi nghiem", "tieng on", "noise abatement", "cam bay dem", "burbank", "frankfurt", "sydney"],
        related_regulations=["ICAO Annex 16 - Environmental Protection: Aircraft Noise"],
        common_questions=[{"q": "Nếu máy bay đến lúc 23:02 vì lý do kẹt gió thì có được châm chước hạ cánh không?", "a": "Rất hiếm! Đa phần các sân bay có luật Curfew nghiêm ngặt đều từ chối và bắt chuyển hướng sang sân bay khác, trừ trường hợp khẩn cấp cấp cứu y tế hoặc cạn nhiên liệu (Mayday Fuel)."}]
    ),

    "diversion": KnowledgeTerm(
        term_id="diversion",
        name_vi="Chuyển Hướng Hạ Cánh Sân Bay Dự Bị (Flight Diversion)",
        name_en="Flight Diversion to Alternate Airport",
        acronym="DIV",
        category="aviation_metrics",
        definition_vi=(
            "Tình huống tàu bay đang trên hành trình bay nhưng không thể tiếp tục hạ cánh tại sân bay đến dự kiến, "
            "buộc phải chuyển hướng hạ cánh xuống một sân bay dự bị (Alternate Airport) đã được phê chuẩn trong kế hoạch bay."
        ),
        business_significance=(
            "Cơn ác mộng chi phí và điều hành: Tốn hàng chục nghìn USD tiền nhiên liệu bay vòng, phí phục vụ mặt đất đột xuất, "
            "tiền xe khách/khách sạn cho hành khách và làm đứt gãy lịch trình của tàu bay và phi hành đoàn."
        ),
        calculation_or_rule=(
            "Nguyên nhân: Thời tiết dưới tiêu chuẩn tối thiểu (Below Minimums - sương mù RVR thấp, trần mây), "
            "Cấp cứu y tế trên không (Medical Emergency), hoặc Trục trặc kỹ thuật đột xuất. "
            "Căn cứ: 14 CFR § 121.617 & § 121.625 (Quy chuẩn chọn sân bay dự bị cất cánh và hạ cánh)."
        ),
        operational_impact=("Tàu bay bị kẹt tại sân bay phụ (Outstation), OCC phải điều phối tiếp nhiên liệu khẩn để bay về căn cứ."),
        keywords=["diversion", "chuyen huong", "ha canh du bi", "alternate airport", "below minimums", "cap cuu y te", "div"],
        related_regulations=["14 CFR § 121.625 (Alternate Airport Weather Minimums)"],
        common_questions=[{"q": "Hãng có phải bồi thường tiền mặt khi chuyến bay bị chuyển hướng vì bão không?", "a": "Không, thời tiết xấu là lý do bất khả kháng (Force Majeure), hãng chỉ có nghĩa vụ hỗ trợ ăn uống và bố trí phương tiện đưa khách về đích sớm nhất."}]
    ),

    "ferry_flight": KnowledgeTerm(
        term_id="ferry_flight",
        name_vi="Chuyến Bay Chuyển Sân / Rỗng (Ferry / Repositioning Flight)",
        name_en="Ferry / Positioning Flight",
        acronym="FERRY",
        category="aviation_metrics",
        definition_vi=(
            "Chuyến bay kỹ thuật không chở hành khách thu tiền, được thực hiện để di chuyển tàu bay từ sân bay này "
            "đến sân bay khác nhằm phục vụ cân đối đội bay, đưa tàu bay vào xưởng bảo dưỡng (Maintenance), "
            "hoặc chuyển sân bay cùng cụm đô thị (ví dụ: JFK sang LGA, ORD sang MDW, DFW sang DAL)."
        ),
        business_significance=(
            "Giải thích bản chất của các chuyến bay cự ly siêu ngắn (10.6 - 30 dặm) được ghi nhận trong cơ sở dữ liệu. "
            "Không phải là lỗi dữ liệu mà là các chuyến chuyển sân tác nghiệp thực tế."
        ),
        calculation_or_rule=(
            "Đặc điểm nhận diện trong DWH: Cự ly distance_miles <= 40 dặm, air_time từ 8 - 25 phút. "
            "Chuyến bay này được cấp phép theo FAA Special Flight Permit (Ferry Permit) theo 14 CFR § 21.197."
        ),
        operational_impact=(
            "Không phát sinh nghĩa vụ bồi hoàn hành khách theo 14 CFR Part 259/260 nhưng vẫn chịu sự điều phối "
            "không lưu của ATC và trần giờ bay của phi công theo FAR Part 91/121."
        ),
        keywords=[
            "ferry flight", "chuyen san", "bay rong", "repositioning", "chuyen bay ky thuat",
            "cu ly ngan", "jfk lga", "ord mdw", "dfw dal", "ferry permit"
        ],
        related_regulations=[
            "14 CFR § 21.197 (Special Flight Permits)",
            "14 CFR § 91.611 (Ferry Flights with One Engine Inoperative)"
        ],
        common_questions=[
            {
                "q": "Chuyến bay từ JFK sang LGA chỉ có 11 dặm có phải do GPS/Radar ghi nhận lỗi không?",
                "a": "Hoàn toàn không lỗi! Đây là chuyến bay chuyển sân (Ferry flight) giữa 2 sân bay trong cùng đô thị New York để chuẩn bị tàu bay cho lịch trình buổi sáng tiếp theo."
            }
        ]
    ),

    "cost_of_delay": KnowledgeTerm(
        term_id="cost_of_delay",
        name_vi="Chi Phí Thiệt Hại Trễ Chuyến (Economic Cost of Delay)",
        name_en="Total Economic Cost of Flight Delay",
        acronym="COST_DELAY",
        category="aviation_metrics",
        definition_vi=(
            "Tổng thiệt hại tài chính mà mỗi phút trễ chuyến bay gây ra cho nền kinh tế, bao gồm "
            "chi phí vận hành trực tiếp của hãng hàng không (nhiên liệu đốt thêm, lương phụ trội phi hành đoàn, "
            "bảo dưỡng động cơ) và tổn thất thời gian/năng suất của hành khách."
        ),
        business_significance=(
            "Cơ sở tài chính để Giám đốc Vận hành (COO) phê duyệt ngân sách điều hành khẩn cấp (như gọi Standby Crew, đổi tàu bay). "
            "Biết được chi phí mỗi phút giúp quy đổi các quyết định tác nghiệp ra số tiền cụ thể."
        ),
        calculation_or_rule=(
            "Định mức FAA / Airlines for America (A4A Benchmark): "
            "1. Chi phí trực tiếp hãng bay (Direct Aircraft Operating Cost): $47.44 USD / phút trễ. "
            "2. Tổn thất của hành khách (Passenger Value of Time): $53.74 USD / phút trễ. "
            "-> TỔNG CHI PHÍ KINH TẾ = $101.18 USD / phút trễ (tương đương ~6,070 USD mỗi giờ trễ chuyến)."
        ),
        operational_impact=("Một chuyến bay chậm 2 giờ gây thiệt hại tài chính bình quân hơn 12,000 USD."),
        keywords=[
            "cost of delay", "chi phi tre", "thiet hai tre chuyen", "a4a benchmark",
            "gia tri thoi gian", "101 usd phut", "1 phut", "ton bao nhieu tien", "bao nhieu tien"
        ],
        related_regulations=["FAA Economic Values for Investment and Regulatory Decisions"],
        common_questions=[{"q": "Tại sao hãng bay sẵn sàng trả thêm tiền nhiên liệu để bay nhanh hơn bù giờ?", "a": "Vì chi phí xăng đốt thêm thường chỉ khoảng $500-$1000, trong khi tránh được 30 phút trễ tiết kiệm được hơn $3,000 chi phí dây chuyền và tiền bồi thường."}]
    ),

    # -------------------------------------------------------------------------
    # NHÓM 2: 14 CHỈ SỐ MACHINE LEARNING & THỐNG KÊ AI (ML METRICS)
    # -------------------------------------------------------------------------
    "delay_probability": KnowledgeTerm(
        term_id="delay_probability",
        name_vi="Xác Suất Dự Báo Trễ Chuyến (Delay Probability)",
        name_en="Delay Probability Score",
        acronym="P(DELAY)",
        category="ml_metrics",
        definition_vi=(
            "Giá trị xác suất từ 0.0000 đến 1.0000 (tương đương 0% đến 100%) do mô hình Machine Learning "
            "(LightGBM, CatBoost, XGBoost hoặc Soft-Voting Ensemble) dự đoán về khả năng chuyến bay "
            "bị chậm giờ đến từ 15 phút trở lên (arr_delay >= 15)."
        ),
        business_significance=(
            "Thay thế cảm tính trực giác của con người bằng con số định lượng khách quan dựa trên dữ liệu lớn "
            "(thời tiết, mật độ bay, lịch sử đường bay, mô hình hãng bay, khung giờ sinh học)."
        ),
        calculation_or_rule=(
            "P(y = 1 | X) = Predict_Proba(Features). "
            "Được so sánh trực tiếp với Ngưỡng Quyết Định Tối Ưu (Decision Threshold, ví dụ 0.2709) "
            "thay vì ngưỡng 0.50 mặc định để phân loại chuyến bay vào các nhóm rủi ro."
        ),
        operational_impact=(
            "Xác định chuyến bay có cần đưa vào diện Giám Sát Chủ Động (Active Monitoring) hay không."
        ),
        keywords=[
            "delay probability", "xac suat tre", "ti le tre", "diem rui ro", "predict proba",
            "p delay", "du bao tre", "mo hinh ml"
        ],
        related_regulations=[
            "Enterprise AI Governance & Model Validation Standards"
        ],
        common_questions=[
            {
                "q": "Tại sao xác suất 30% lại bị cảnh báo rủi ro cao trong khi đa số (70%) là đúng giờ?",
                "a": "Vì tỷ lệ trễ tự nhiên toàn mạng chỉ khoảng 18-20%. Một chuyến bay có 30% nguy cơ trễ cao hơn gấp 1.5 lần mức trung bình, do đó theo ma trận chi phí-lợi ích, hành động can thiệp sớm là cần thiết để tránh phạt lớn."
            }
        ]
    ),

    "risk_band": KnowledgeTerm(
        term_id="risk_band",
        name_vi="Phân Nhóm Ngưỡng Rủi Ro (Risk Band)",
        name_en="Operational Risk Band",
        acronym="BAND",
        category="ml_metrics",
        definition_vi=(
            "Hệ thống phân tầng mức độ nghiêm trọng gồm 3 nhóm (Normal, Elevated, High) "
            "được phân loại dựa trên xác suất trễ dự báo so với ngưỡng cắt quyết định (Threshold)."
        ),
        business_significance=(
            "Chuẩn hóa ngôn ngữ hành động giữa bộ phận AI và Trực ban Điều hành Bay OCC, "
            "tránh tình trạng quá tải báo động (Alert Fatigue)."
        ),
        calculation_or_rule=(
            "1. High Risk (Đỏ): Delay Probability >= Threshold (ví dụ >= 0.2709). Kích hoạt lệnh tác nghiệp phòng ngừa và chế tài pháp lý.\n"
            "2. Elevated Risk (Vàng): 0.70 * Threshold <= Delay Probability < Threshold. Đưa vào diện theo dõi sát sao, chuẩn bị phương án đệm.\n"
            "3. Normal Risk (Xanh): Delay Probability < 0.70 * Threshold. Khai thác tiêu chuẩn, cấp lệnh Dispatch Release bình thường."
        ),
        operational_impact=(
            "Quyết định thứ tự ưu tiên can thiệp của OCC Dispatcher khi có hàng trăm chuyến bay cất cánh mỗi giờ."
        ),
        keywords=[
            "risk band", "nhom rui ro", "phan tang rui ro", "high risk", "elevated risk",
            "normal risk", "muc do rui ro", "nguong rui ro", "canh bao rui ro"
        ],
        related_regulations=[
            "SOP-OCC-AIRLINE-01 (Quy trình giám sát theo dải rủi ro)"
        ],
        common_questions=[
            {
                "q": "Nhóm Elevated có phải bồi thường hành khách không?",
                "a": "Chưa! Nhóm Elevated chỉ kích hoạt nghĩa vụ thông tin minh bạch theo 14 CFR § 259.8 và theo dõi tổ bay, chưa kích hoạt các khoản bồi hoàn tài chính."
            }
        ]
    ),

    "optimal_threshold": KnowledgeTerm(
        term_id="optimal_threshold",
        name_vi="Ngưỡng Cắt Quyết Định Tối Ưu (Optimal Decision Threshold)",
        name_en="Optimal Classification Decision Threshold",
        acronym="THRESHOLD",
        category="ml_metrics",
        definition_vi=(
            "Điểm cắt xác suất (ví dụ 0.2709) được lựa chọn dựa trên việc tối ưu hóa hàm mục tiêu kinh doanh hoặc F1-Score "
            "thay vì sử dụng ngưỡng mặc định 0.50 của các thư viện Machine Learning tiêu chuẩn."
        ),
        business_significance=(
            "Khắc phục sự mất cân bằng dữ liệu: Trong ngành hàng không, chỉ có ~19% chuyến bay bị trễ. "
            "Nếu giữ nguyên ngưỡng 0.50, mô hình sẽ bỏ lọt phần lớn các chuyến bay bị trễ (False Negatives), "
            "khiến hãng không kịp trở tay trước các án phạt pháp lý triệu đô."
        ),
        calculation_or_rule=(
            "Threshold* = argmax_t [ F1(t) ] hoặc argmin_t [ Cost(FP)*FP(t) + Cost(FN)*FN(t) ]. "
            "Trong dự án Airline Data Platform, ngưỡng tối ưu trên tập Validation đạt mức 0.2709, "
            "tối đa hóa năng lực phát hiện chuyến bay nguy cơ cao."
        ),
        operational_impact=("Mọi chuyến bay có xác suất >= 0.2709 đều được gắn cờ can thiệp sớm."),
        keywords=["threshold", "nguong cat", "nguong toi uu", "decision threshold", "f1 optimization", "cost matrix", "0.2709"],
        related_regulations=["NIST AI Risk Management Framework Section 3.2"],
        common_questions=[{"q": "Tại sao không dùng ngưỡng 0.50 như bình thường?", "a": "Vì ngưỡng 0.50 chỉ phù hợp khi bài toán có 50% đúng và 50% sai. Với dữ liệu mất cân bằng nặng, ngưỡng 0.50 sẽ khiến AI hầu như không bao giờ phát cảnh báo!"}]
    ),

    "roc_auc": KnowledgeTerm(
        term_id="roc_auc",
        name_vi="Diện Tích Dưới Đường Cong ROC (ROC-AUC)",
        name_en="Receiver Operating Characteristic - Area Under Curve",
        acronym="ROC-AUC",
        category="ml_metrics",
        definition_vi=(
            "Thước đo đánh giá khả năng phân biệt tổng quát của mô hình phân loại nhị phân giữa chuyến bay trễ "
            "và chuyến bay đúng giờ trên toàn bộ các ngưỡng cắt quyết định có thể có từ 0.0 đến 1.0."
        ),
        business_significance=(
            "Chỉ số vàng để so sánh hiệu năng giữa các thuật toán trong Đấu trường Mô hình (Tournament). "
            "Không bị ảnh hưởng bởi sự mất cân bằng dữ liệu (Class Imbalance) giữa số chuyến bay trễ và đúng giờ."
        ),
        calculation_or_rule=(
            "Tích phân đường cong ROC vẽ True Positive Rate (Sensitivity) theo False Positive Rate (1 - Specificity). "
            "Thang điểm đánh giá:\n"
            "- AUC = 0.50: Mô hình đoán mò ngẫu nhiên (Vô dụng).\n"
            "- 0.65 - 0.70: Mô hình chấp nhận được.\n"
            "- 0.70 - 0.80: Mô hình tốt, sẵn sàng cho môi trường Production vận hành.\n"
            "- > 0.85: Mô hình xuất sắc (Cần kiểm tra kỹ hiện tượng data leakage)."
        ),
        operational_impact=(
            "Mô hình đạt AUC cao nhất trên tập kiểm thử độc lập (Holdout Test) sẽ được tự động vinh danh "
            "là 'Tournament Winner' và lưu vào best_delay_model.joblib."
        ),
        keywords=[
            "roc auc", "auc", "roc", "dien tich duoi duong cong", "do chinh xac mo hinh",
            "danh gia ml", "true positive rate", "false positive rate", "tournament winner"
        ],
        related_regulations=[
            "IEEE Standard for Machine Learning Model Evaluation"
        ],
        common_questions=[
            {
                "q": "Tại sao trong dự án này Soft-Voting Ensemble hoặc GBDT đạt AUC ~0.72 là rất cao?",
                "a": "Vì dữ liệu trễ chuyến bay hàng không bị chi phối bởi các yếu tố ngoại cảnh ngẫu nhiên (thời tiết vi mô, trục trặc kỹ thuật đột xuất, quyết định cá nhân phi công). Trong ngành hàng không, AUC từ 0.70 - 0.75 trên dữ liệu Out-of-Time là tiêu chuẩn xuất sắc của các hãng quốc tế."
            }
        ]
    ),

    "pr_auc": KnowledgeTerm(
        term_id="pr_auc",
        name_vi="Diện Tích Đường Cong Precision-Recall (PR-AUC / Average Precision)",
        name_en="Precision-Recall Area Under Curve (PR-AUC / AP)",
        acronym="PR-AUC",
        category="ml_metrics",
        definition_vi=(
            "Thước đo đánh giá đường cong biểu diễn sự đánh đổi giữa Độ chuẩn xác (Precision) và Tỷ lệ bắt trúng (Recall) "
            "trên các ngưỡng phân loại khác nhau, đặc biệt nhạy bén trên các tập dữ liệu mất cân bằng (Imbalanced Datasets)."
        ),
        business_significance=(
            "Trong khi ROC-AUC có thể bị 'thổi phồng' bởi số lượng khổng lồ các chuyến bay đúng giờ (True Negatives), "
            "PR-AUC chỉ tập trung khắt khe vào lớp thiểu số (Chuyến bay trễ). Đây là chỉ số mà các Senior MLOps Engineer tin cậy nhất."
        ),
        calculation_or_rule=(
            "Tích phân đường cong Precision theo Recall. "
            "Đường cơ sở ngẫu nhiên (Baseline): PR-AUC ngẫu nhiên bằng đúng tỷ lệ trễ tự nhiên (khoảng 0.19). "
            "Mô hình đạt PR-AUC >= 0.35 - 0.45 được coi là có năng lực thực chiến vượt trội gấp đôi ngẫu nhiên."
        ),
        operational_impact=("Đảm bảo mô hình thực sự học được bản chất của các chuyến bay trễ chứ không chỉ đoán bừa chuyến đúng giờ."),
        keywords=["pr auc", "precision recall", "average precision", "du lieu mat can bang", "imbalance", "ap", "pr curve"],
        related_regulations=["ICML / NeurIPS Guidelines for Imbalanced Classification Benchmark"],
        common_questions=[{"q": "Khi nào nên ưu tiên PR-AUC hơn ROC-AUC?", "a": "Khi tỷ lệ lớp mục tiêu (chuyến trễ) chiếm dưới 25% tổng tập dữ liệu, PR-AUC là thước đo phản ánh trung thực hơn nhiều."}]
    ),

    "lift_at_10": KnowledgeTerm(
        term_id="lift_at_10",
        name_vi="Độ Tăng Tỷ Lệ Phát Hiện Rủi Ro Tại Top 10% (Lift @ 10%)",
        name_en="Lift at Top 10% Riskiest Decile",
        acronym="LIFT@10",
        category="ml_metrics",
        definition_vi=(
            "Tỷ số giữa tỷ lệ chuyến bay trễ thực tế nằm trong 10% chuyến bay được mô hình chấm điểm rủi ro cao nhất "
            "so với tỷ lệ trễ bình quân trên toàn bộ tập dữ liệu."
        ),
        business_significance=(
            "Chỉ số thực chiến quan trọng nhất đối với ban lãnh đạo và giám đốc vận hành bay! "
            "Bởi vì OCC không có đủ nguồn lực để can thiệp 100% chuyến bay. Chỉ số Lift cho biết nếu OCC "
            "chỉ tập trung xử lý đúng 10% chuyến bay rủi ro nhất, họ sẽ đón đầu được bao nhiêu chuyến bay thực sự bị trễ."
        ),
        calculation_or_rule=(
            "Lift @ 10% = (Tỷ lệ trễ trong Top 10% điểm cao nhất) / (Tỷ lệ trễ tổng thể toàn mạng). "
            "Ví dụ: Nếu tỷ lệ trễ toàn mạng là 19.5%, và trong top 10% chuyến bay nguy hiểm nhất có 35.8% chuyến trễ "
            "-> Lift @ 10% = 35.8% / 19.5% = 1.84x (Gấp 1.84 lần so với chọn ngẫu nhiên!). "
            "Tiêu chuẩn chấp thuận của dự án: Lift @ 10% >= 1.50x."
        ),
        operational_impact=(
            "Tối đa hóa hiệu suất sử dụng đội bay dự phòng (Standby Crew) và chuyên viên OCC."
        ),
        keywords=[
            "lift", "lift at 10", "lift 10", "do tang chat luong", "top 10 rui ro",
            "decile lift", "hieu qua can thiep", "ti le don dau"
        ],
        related_regulations=[
            "Operational Efficiency KPI Framework"
        ],
        common_questions=[
            {
                "q": "Lift = 1.8x có ý nghĩa kinh tế gì?",
                "a": "Nghĩa là thay vì lãng phí chi phí theo dõi tràn lan, OCC chỉ cần dồn sự chú ý vào 10 chuyến bay rủi ro nhất thì đã bắt trúng gần gấp đôi số chuyến bay sẽ thực sự gây sự cố!"
            }
        ]
    ),

    "brier_score": KnowledgeTerm(
        term_id="brier_score",
        name_vi="Chỉ Số Hiệu Chuẩn Brier (Brier Score)",
        name_en="Brier Calibration Score",
        acronym="BRIER",
        category="ml_metrics",
        definition_vi=(
            "Thước đo sai số toàn phương trung bình (Mean Squared Error) giữa xác suất dự đoán của mô hình "
            "với kết quả thực tế (0 hoặc 1), phản ánh độ tin cậy và mức độ hiệu chuẩn (Calibration) của con số xác suất."
        ),
        business_significance=(
            "Một mô hình có thể có AUC cao nhưng xác suất lại bị lệch (ví dụ dự báo 90% nhưng thực tế chỉ 30%). "
            "Brier Score đảm bảo rằng khi mô hình nói 'xác suất trễ là 30%' thì chính xác khoảng 30 trong số 100 chuyến bay đó sẽ bị trễ."
        ),
        calculation_or_rule=(
            "Brier Score = (1/N) * sum((p_i - y_i)^2), với p_i là xác suất dự đoán và y_i thuộc {0, 1}. "
            "Giá trị dao động từ 0.0 (Dự báo hoàn hảo) đến 1.0 (Dự báo sai hoàn toàn). "
            "Mô hình đạt Brier Score < 0.15 được xem là đã hiệu chuẩn xác thực rất tốt."
        ),
        operational_impact=(
            "Giúp OCC tự tin sử dụng con số xác suất làm căn cứ giải ngân kinh phí dự phòng rủi ro."
        ),
        keywords=[
            "brier score", "diem brier", "hieu chuan xac suat", "calibration",
            "do tin cay xac suat", "sai so toan phuong", "brier"
        ],
        related_regulations=[
            "Probabilistic Forecast Verification Standards (WMO/FAA)"
        ],
        common_questions=[
            {
                "q": "Brier Score thấp hơn là tốt hơn hay xấu hơn?",
                "a": "Thấp hơn là TỐT HƠN! Vì đây là hàm đo lường sai số (loss). Càng gần 0 nghĩa là xác suất dự đoán càng sát với thực tế diễn ra."
            }
        ]
    ),

    "precision_score": KnowledgeTerm(
        term_id="precision_score",
        name_vi="Độ Chuẩn Xác Cảnh Báo (Precision / Positive Predictive Value)",
        name_en="Precision (Alert Quality)",
        acronym="PRECISION",
        category="ml_metrics",
        definition_vi=(
            "Tỷ lệ các chuyến bay thực sự bị trễ trong tổng số các chuyến bay mà mô hình AI đã phát tín hiệu cảnh báo rủi ro trễ."
        ),
        business_significance=(
            "Bảo vệ niềm tin của điều phái viên: Nếu Precision quá thấp (ví dụ 10%), cứ 10 lần AI hú còi báo động thì 9 lần là sai, "
            "dẫn đến hội chứng 'Cậu bé chăn cừu' (Alert Fatigue) - nhân viên sẽ tắt thông báo của AI."
        ),
        calculation_or_rule=(
            "Precision = TP / (TP + FP). "
            "Trong đó: TP là True Positives (bắt đúng chuyến trễ), FP là False Positives (báo động giả). "
            "Mục tiêu của hệ thống dự báo: Precision >= 40% - 50% trong môi trường imbalanced."
        ),
        operational_impact=("Ngăn chặn lãng phí nhân lực vào việc điều tra các chuyến bay không thực sự có nguy cơ."),
        keywords=["precision", "do chuan xac", "bao dong gia", "alert fatigue", "false alarm", "tp", "fp"],
        related_regulations=["ISO/IEC 42001 (Artificial Intelligence Management System)"],
        common_questions=[{"q": "Làm thế nào để tăng Precision?", "a": "Tăng ngưỡng quyết định (Threshold) lên cao hơn, chấp nhận bỏ bớt một số chuyến trễ nhẹ nhưng hễ cảnh báo là chắc chắn đúng."}]
    ),

    "recall_sensitivity": KnowledgeTerm(
        term_id="recall_sensitivity",
        name_vi="Độ Nhạy / Tỷ Lệ Phát Hiện Rủi Ro (Recall / Sensitivity)",
        name_en="Recall / Sensitivity (True Positive Rate)",
        acronym="RECALL",
        category="ml_metrics",
        definition_vi=(
            "Tỷ lệ các chuyến bay mà mô hình AI phát hiện thành công trong tổng số tất cả các chuyến bay thực tế bị trễ ngoài đời thực."
        ),
        business_significance=(
            "Lưới lọc an toàn pháp lý: Recall cao đảm bảo các chuyến bay có nguy cơ bùng nổ Tarmac Delay 3 giờ hoặc "
            "phi công hết hạn FDP không bị lọt lưới, giúp hãng có đủ thời gian phòng ngừa chế tài."
        ),
        calculation_or_rule=(
            "Recall = TP / (TP + FN). "
            "Trong đó: FN là False Negatives (bỏ lọt rủi ro, AI nói đúng giờ nhưng thực tế lại trễ). "
            "Tiêu chuẩn vận hành an toàn: Recall >= 65% - 75% tại ngưỡng tối ưu."
        ),
        operational_impact=("Triệt tiêu nguy cơ bất ngờ (Surprise Disruption) cho Trung tâm Điều hành Bay."),
        keywords=["recall", "sensitivity", "do nhay", "ty le phat hien", "fn", "bo lot rui ro", "true positive rate"],
        related_regulations=["FAA Safety Management System (SMS) Predictive Risk Controls"],
        common_questions=[{"q": "Tại sao không thể vừa có Precision 100% vừa có Recall 100%?", "a": "Đó là sự đánh đổi kinh điển trong Machine Learning: Muốn bắt trọn mọi rủi ro (Recall cao) thì phải chấp nhận bắt nhầm nhiều hơn (Precision giảm)."}]
    ),

    "f1_fbeta_score": KnowledgeTerm(
        term_id="f1_fbeta_score",
        name_vi="Điểm Cân Bằng F1 & F-beta (F1-Score / F-beta)",
        name_en="F1-Score & F-beta Harmonic Mean",
        acronym="F1/FBETA",
        category="ml_metrics",
        definition_vi=(
            "Trung bình điều hòa giữa Precision và Recall, phản ánh sự cân bằng toàn diện của mô hình phân loại "
            "mà không bị chi phối thiên lệch bởi một chỉ số đơn lẻ."
        ),
        business_significance=(
            "Chỉ số đơn lẻ đáng tin cậy nhất để chọn ra Ngưỡng Quyết Định Tối Ưu (Optimal Threshold). "
            "F-beta (với beta = 2) cho phép gán trọng số ưu tiên cho Recall gấp 2 lần Precision khi sự cố bỏ lọt nguy hiểm hơn báo động giả."
        ),
        calculation_or_rule=(
            "F1 = 2 * (Precision * Recall) / (Precision + Recall). "
            "F_beta = (1 + beta^2) * (Precision * Recall) / ((beta^2 * Precision) + Recall). "
            "F1 dao động từ 0.0 đến 1.0; mô hình trên dữ liệu thực tế đạt F1 >= 0.42 - 0.50 là rất xuất sắc."
        ),
        operational_impact=("Dùng làm tiêu chí tự động quét và chốt ngưỡng cắt trong pipeline huấn luyện `ml/train.py`."),
        keywords=["f1", "f1 score", "fbeta", "trung binh dieu hoa", "can bang precision recall"],
        related_regulations=["Enterprise Machine Learning Governance Standards"],
        common_questions=[{"q": "F1 khác gì với Accuracy thông thường?", "a": "Accuracy đoán bừa toàn bộ chuyến bay là 'Đúng giờ' thì đã đạt 80% nhưng F1 bằng 0 vì không phát hiện được bất kỳ chuyến trễ nào."}]
    ),

    "confusion_matrix_cost": KnowledgeTerm(
        term_id="confusion_matrix_cost",
        name_vi="Ma Trận Nhầm Lẫn & Chi Phí Nhầm Lẫn (Confusion Matrix & Cost-Sensitive Analysis)",
        name_en="Confusion Matrix & Cost-Sensitive Trade-off",
        acronym="CONF_MAT",
        category="ml_metrics",
        definition_vi=(
            "Bảng phân loại kết quả 2x2 gồm 4 ô: True Positive (TP), False Positive (FP), True Negative (TN), False Negative (FN), "
            "kết hợp với ma trận trọng số chi phí tài chính thực tế phát sinh trong vận hành."
        ),
        business_significance=(
            "Bản đồ kinh tế của AI: Giúp Giám đốc Tài chính (CFO) và Giám đốc Vận hành (COO) nhìn thấy "
            "con số tiền bạc được cứu vãn hoặc bị tổn thất sau mỗi quyết định của mô hình."
        ),
        calculation_or_rule=(
            "Chi phí nhầm lẫn: Cost(FN) = $6,000 USD (trễ nặng + phạt luật) vs Cost(FP) = $400 USD (chi phí gọi phi công dự bị dự phòng). "
            "Vì Cost(FN) >> Cost(FP) (gấp 15 lần), mô hình phải được điều chỉnh để ưu tiên giảm thiểu tối đa FN."
        ),
        operational_impact=("Cơ sở chứng minh Giá trị Đầu tư (ROI) của dự án Machine Learning trước ban lãnh đạo."),
        keywords=["confusion matrix", "ma tran nham lan", "cost sensitive", "chi phi nham lan", "tp fp tn fn", "type 1 type 2"],
        related_regulations=["FAA Cost-Benefit Analysis Guidelines"],
        common_questions=[{"q": "Lỗi Type I và Type II trong điều hành bay là gì?", "a": "Type I (FP): Báo động giả, chuẩn bị sẵn đồ ăn/phi công nhưng máy bay lại cất cánh đúng giờ. Type II (FN): Bỏ lọt, máy bay bị trễ 4 tiếng dẫn đến án phạt triệu đô."}]
    ),

    "feature_importance_shap": KnowledgeTerm(
        term_id="feature_importance_shap",
        name_vi="Tầm Quan Trọng Của Đặc Trưng & Giá Trị SHAP",
        name_en="Feature Importance & SHAP Values",
        acronym="SHAP/FI",
        category="ml_metrics",
        definition_vi=(
            "Phương pháp giải thích quyết định của mô hình AI (Explainable AI - XAI), định lượng mức độ đóng góp "
            "và chiều hướng tác động (tăng hay giảm rủi ro) của từng biến đầu vào như giờ bay, hãng bay, "
            "tắc nghẽn sân bay đối với phán quyết trễ chuyến."
        ),
        business_significance=(
            "Xóa bỏ 'hộp đen' (Black-box) của AI. Cung cấp căn cứ khoa học minh bạch để giải trình với cơ quan quản lý "
            "nhà nước (FAA / CAAV) và giúp điều phái viên hiểu rõ 'Tại sao AI lại cảnh báo chuyến bay này?'."
        ),
        calculation_or_rule=(
            "Dựa trên Lý thuyết trò chơi hợp tác (Shapley Values từ Nobel Kinh tế Lloyd Shapley) hoặc "
            "Tổng mức giảm độ phân mảnh Gain / Split trong các cây quyết định GBDT (LightGBM/XGBoost/CatBoost). "
            "Các đặc trưng quan trọng hàng đầu trong mô hình gồm: "
            "1) dep_hour (Khung giờ bay chiều tối), "
            "2) scheduled_departures_hour (Mật độ bay tại sân bay xuất phát), "
            "3) route_delay_rate_30d (Tỷ lệ trễ lịch sử của đường bay), "
            "4) carrier_type (Mô hình khai thác LCC hay Legacy)."
        ),
        operational_impact=(
            "Cho phép OCC can thiệp đúng nguyên nhân gốc rễ (Root Cause) thay vì xử lý triệu chứng."
        ),
        keywords=[
            "feature importance", "shap", "shap values", "tam quan trong dac trung",
            "giai thich ai", "xai", "hop den", "dong gop bien", "nguyen nhan du bao"
        ],
        related_regulations=[
            "EU AI Act & US DOT Algorithmic Transparency Guidelines"
        ],
        common_questions=[
            {
                "q": "Biến nào thường gây trễ chuyến bay nhiều nhất?",
                "a": "Thống kê từ mô hình cho thấy Khung giờ khởi hành (dep_hour) và Mật độ tắc nghẽn sân bay xuất phát (scheduled_departures_hour) chiếm hơn 45% trọng số đóng góp vào xác suất trễ của chuyến bay."
            }
        ]
    ),

    "data_drift_psi": KnowledgeTerm(
        term_id="data_drift_psi",
        name_vi="Độ Lệch Dữ Liệu & Chỉ Số Ổn Định Quần Thể (Data Drift & PSI)",
        name_en="Data Drift & Population Stability Index (PSI)",
        acronym="PSI/DRIFT",
        category="ml_metrics",
        definition_vi=(
            "Thước đo sự thay đổi về mặt phân phối thống kê của các đặc trưng đầu vào hoặc biến mục tiêu "
            "giữa tập dữ liệu huấn luyện trong quá khứ và luồng dữ liệu khai thác thực tế theo thời gian thực."
        ),
        business_significance=(
            "Hệ thống báo cháy cho mô hình AI: Thời tiết chuyển từ mùa hè sang mùa đông bão tuyết sẽ làm dữ liệu trễ bay biến động dữ dội. "
            "PSI giúp phát hiện khi nào mô hình đã bị 'lỗi thời' (Stale) để kích hoạt chu trình tái huấn luyện (Model Retraining)."
        ),
        calculation_or_rule=(
            "PSI = sum( (Actual% - Expected%) * ln(Actual% / Expected%) ). "
            "Thang đo cảnh báo chuẩn:\n"
            "- PSI < 0.10: Dữ liệu ổn định, không có thay đổi đáng kể.\n"
            "- 0.10 <= PSI <= 0.25: Có độ trôi dữ liệu trung bình, cần theo dõi chặt chẽ.\n"
            "- PSI > 0.25: Độ lệch dữ liệu nghiêm trọng! Bắt buộc phải kích hoạt pipeline huấn luyện lại mô hình."
        ),
        operational_impact=("Ngăn chặn hiện tượng mô hình AI đưa ra các dự đoán sai lệch do thời tiết đổi mùa."),
        keywords=["psi", "data drift", "concept drift", "population stability index", "do lech du lieu", "retrain", "tai huan luyen"],
        related_regulations=["Federal Reserve SR 11-7 (Guidance on Model Risk Management)"],
        common_questions=[{"q": "Bao lâu thì nên kiểm tra PSI của mô hình trễ chuyến một lần?", "a": "Nên chạy kiểm tra định kỳ hàng tuần hoặc sau mỗi biến cố lớn như đổi lịch bay mùa (IATA Schedule Change) hay siêu bão tuyết."}]
    ),

    "temporal_split_leakage": KnowledgeTerm(
        term_id="temporal_split_leakage",
        name_vi="Phân Tách Chuỗi Thời Gian & Chống Rò Rỉ Dữ Liệu (Temporal Split vs Data Leakage)",
        name_en="Temporal Train/Val/Test Split & Leakage Prevention",
        acronym="TEMP_SPLIT",
        category="ml_metrics",
        definition_vi=(
            "Quy chuẩn kiến trúc bắt buộc trong Machine Learning hàng không: Phân chia tập dữ liệu huấn luyện, thẩm định "
            "và kiểm thử hoàn toàn theo trục thời gian thực tế (Past -> Future) thay vì phân chia ngẫu nhiên (Random K-Fold)."
        ),
        business_significance=(
            "Triệt tiêu hoàn toàn hiện tượng Rò Rỉ Nhìn Trước (Look-ahead Bias / Data Leakage): "
            "Nếu chia ngẫu nhiên, mô hình sẽ dùng dữ liệu của ngày mai để dự đoán cho hôm nay, "
            "tạo ra kết quả AUC cao giả tạo trên giấy nhưng thất bại thảm hại khi đưa vào vận hành thực tế."
        ),
        calculation_or_rule=(
            "Nguyên tắc: Train (Tháng 2 -> Tháng 10) -> Validation (Tháng 11) -> Holdout Test (Tháng 12 / Tháng 1 năm sau). "
            "Các bảng tra cứu (Lookups như route_delay_rate_30d) chỉ được tính toán trên cửa sổ trượt quá khứ (Rolling 30 days)."
        ),
        operational_impact=("Bảo đảm độ tin cậy tuyệt đối 100% của mô hình khi đối mặt với dữ liệu chưa từng thấy trong tương lai."),
        keywords=["temporal split", "data leakage", "look ahead bias", "ro ri du lieu", "chuoi thoi gian", "holdout test"],
        related_regulations=["NeurIPS Data Science Integrity Standards"],
        common_questions=[{"q": "Tại sao chia ngẫu nhiên (Random Split) lại bị cấm trong dự án này?", "a": "Vì nếu chia ngẫu nhiên, một chuyến bay trễ buổi sáng sẽ làm lộ thông tin cho chuyến bay buổi chiều cùng ngày, khiến AI gian lận điểm số."}]
    ),
}


# =============================================================================
# 2. STANDARD OPERATING PROCEDURE (SOP) CHECKLISTS - 8 SOPs
# =============================================================================

SOP_CHECKLISTS: Dict[str, SOPChecklist] = {
    # -------------------------------------------------------------------------
    # SOP 1: XỬ LÝ SỰ CỐ CHẬM TRỄ CHUYẾN BAY (DELAY INCIDENT PROTOCOL)
    # -------------------------------------------------------------------------
    "sop_delay_incident": SOPChecklist(
        sop_id="sop_delay_incident",
        title_vi="Quy Trình Chuẩn Xử Lý Sự Cố Chậm Trễ Chuyến Bay (SOP-OCC-DELAY-01)",
        title_en="Flight Delay Incident Mitigation Standard Operating Procedure",
        purpose=(
            "Chuẩn hóa các bước hành động khẩn cấp cho Trực ban Điều hành Bay OCC và Điều phái viên (Dispatcher) "
            "ngay khi phát hiện nguy cơ chuyến bay bị chậm trễ kéo dài, nhằm giảm thiểu phản ứng dây chuyền "
            "và triệt tiêu nguy cơ vi phạm luật định."
        ),
        target_roles=["OCC Duty Manager", "Flight Dispatcher", "Station Operations Manager", "Gate Lead"],
        trigger_condition=(
            "Kích hoạt khi: Dự báo trễ cất cánh (Estimated Departure Delay) >= 30 phút HOẶC mô hình AI gán nhãn High Risk."
        ),
        steps=[
            SOPStep(
                step_number=1,
                action_vi="Đánh giá nguyên nhân gốc rễ (Root Cause) & Kiểm tra tính khả thi của Turnaround",
                responsible_role="Flight Dispatcher",
                timeframe="T - 90 phút trước STD",
                verification_criteria="Xác định rõ sự cố thuộc nhóm BTS nào (Carrier, Late AC, Weather, NAS, Security).",
                regulatory_notice="14 CFR § 234.4 (Phân loại chính xác nguyên nhân phục vụ báo cáo kiểm toán BTS)."
            ),
            SOPStep(
                step_number=2,
                action_vi="Rà soát quỹ giờ bay của Tổ bay (Crew FDP Audit) & Kích hoạt kế hoạch dự phòng",
                responsible_role="Crew Controller",
                timeframe="T - 75 phút trước STD",
                verification_criteria="Tính toán giờ hạ cánh dự kiến có vi phạm FAR Part 117 Table B không. Nếu đe dọa FDP, lập tức gọi Standby Crew.",
                regulatory_notice="14 CFR § 117.11(a) (Nghiêm cấm khởi hành nếu chuyến bay sẽ vượt trần FDP)."
            ),
            SOPStep(
                step_number=3,
                action_vi="Cập nhật trạng thái chuyến bay công khai & Thông báo hành khách qua SMS/App",
                responsible_role="Passenger Operations / Station Lead",
                timeframe="Trong vòng 30 phút kể từ khi phát hiện trễ",
                verification_criteria="Hệ thống FIDS tại sân bay và ứng dụng di động hiển thị giờ bay mới chính xác.",
                regulatory_notice="14 CFR § 259.8(a)(1) (Nghĩa vụ cập nhật thông tin chậm chuyến trong vòng 30 phút)."
            ),
            SOPStep(
                step_number=4,
                action_vi="Ban hành lệnh Gate Hold nếu sân bay đến/đi có Ground Stop / GDP",
                responsible_role="Flight Dispatcher",
                timeframe="T - 45 phút trước STD",
                verification_criteria="Giữ khách tại phòng chờ ga, không đóng cửa tàu bay nếu ATC chưa xác nhận khe cất cánh.",
                regulatory_notice="14 CFR § 259.4(b)(1) (Ngăn ngừa bẫy Tarmac Delay 3 giờ trên đường lăn)."
            ),
            SOPStep(
                step_number=5,
                action_vi="Phân tích tác động dây chuyền (Cascading Impact Analysis) cho các chặng tiếp theo",
                responsible_role="OCC Duty Manager",
                timeframe="T - 30 phút trước STD",
                verification_criteria="Điều chỉnh lịch các chặng sau của tàu bay hoặc chuẩn bị phương án hoán đổi tàu bay (Aircraft Swap).",
                regulatory_notice="Bảo toàn lịch bay ngày tiếp theo và chỉ số OTP toàn mạng."
            )
        ],
        contingency_fallback=(
            "Nếu dự kiến trễ vượt quá 180 phút (3 giờ): OCC Duty Manager họp khẩn đánh giá phương án Hủy chuyến (Cancel) "
            "hoặc Chuyển khách sang hãng bạn (Endorsement/Rebooking) theo 14 CFR § 259.5(b)(8) để giải phóng nguồn lực."
        )
    ),

    # -------------------------------------------------------------------------
    # SOP 2: THAY ĐỔI TỔ BAY KHI HẾT HẠN FDP (CREW TIMEOUT PROTOCOL)
    # -------------------------------------------------------------------------
    "sop_crew_timeout_replacement": SOPChecklist(
        sop_id="sop_crew_timeout_replacement",
        title_vi="Quy Trình Đổi Tổ Bay Khi Chạm Trần FDP (SOP-OCC-CREW-02)",
        title_en="Flight Crew Duty Time-Out & Standby Dispatch Protocol",
        purpose=(
            "Xử lý dứt điểm tình huống tổ lái hoặc tiếp viên chạm ngưỡng giờ làm nhiệm vụ bay tối đa, "
            "đảm bảo tuân thủ 100% quy chuẩn an toàn FAR Part 117 và hạn chế hủy chuyến phút chót."
        ),
        target_roles=["Crew Scheduling Manager", "OCC Chief Dispatcher", "Pilot in Command (PIC)"],
        trigger_condition=(
            "Kích hoạt khi: Thời gian dự kiến hoàn thành chặng bay vượt quá giới hạn FDP hợp pháp cho phép trong ngày."
        ),
        steps=[
            SOPStep(
                step_number=1,
                action_vi="Kiểm tra điều kiện gia hạn FDP tối đa 2 giờ trước cất cánh (Pre-takeoff Extension)",
                responsible_role="Dispatcher & Pilot in Command",
                timeframe="T - 60 phút trước ETD",
                verification_criteria="Cơ trưởng và Dispatcher phải đồng thuận bằng văn bản; tổ bay chưa từng được gia hạn quá 1 lần trong chu kỳ 168 giờ.",
                regulatory_notice="14 CFR § 117.19(a)(1) (Điều kiện gia hạn tối đa 2 giờ trước cất cánh)."
            ),
            SOPStep(
                step_number=2,
                action_vi="Kích hoạt Tổ bay dự bị Cấp 1 (Standby Crew Tier-1) tại Hub",
                responsible_role="Crew Scheduling Coordinator",
                timeframe="T - 50 phút trước ETD",
                verification_criteria="Phi công dự bị nhận lệnh điều động (Callout) và có mặt tại phòng thủ tục bay (Crew Briefing) trong vòng 45 phút.",
                regulatory_notice="14 CFR § 117.21 (Quy chuẩn thời gian sẵn sàng của tổ bay dự phòng Airport Reserve)."
            ),
            SOPStep(
                step_number=3,
                action_vi="Bàn giao tài liệu chuyến bay mới (OFP & Dispatch Release) cho tổ bay thay thế",
                responsible_role="Flight Dispatcher",
                timeframe="T - 20 phút trước ETD",
                verification_criteria="Tổ bay mới ký nhận bản Dispatch Release mới, kiểm tra lại NOTAM và thời tiết cập nhật.",
                regulatory_notice="14 CFR § 121.593 (Thẩm quyền ký lệnh cất cánh với tên tổ bay chính xác)."
            ),
            SOPStep(
                step_number=4,
                action_vi="Bố trí thời gian nghỉ ngơi bắt buộc (Rest Period) cho tổ bay cũ",
                responsible_role="Crew Logistics Support",
                timeframe="Ngay sau khi bàn giao",
                verification_criteria="Đặt khách sạn hoặc xe đưa đón; khóa lịch điều động ít nhất 10 giờ liên tục trước nhiệm vụ tiếp theo.",
                regulatory_notice="14 CFR § 117.25(e) (Bắt buộc tối thiểu 10 giờ nghỉ ngơi liên tục với 8 giờ ngủ không bị gián đoạn)."
            )
        ],
        contingency_fallback=(
            "Nếu tại sân bay căn cứ địa phương (Outstation) không có sẵn Standby Crew: "
            "Lập tức rà soát chuyến bay chuyển sân (Deadhead) từ Hub gần nhất, hoặc hoãn chuyến (Delay Overnight) "
            "đến sáng hôm sau và đặt phòng khách sạn cho toàn bộ hành khách."
        )
    ),

    # -------------------------------------------------------------------------
    # SOP 3: XIN SLOT CẤT CÁNH ƯU TIÊN TỪ ATC (AIR TRAFFIC PRIORITY PROTOCOL)
    # -------------------------------------------------------------------------
    "sop_priority_slot_request": SOPChecklist(
        sop_id="sop_priority_slot_request",
        title_vi="Quy Trình Đàm Phán Khe Giờ Cất Cánh Ưu Tiên Với ATC (SOP-OCC-ATC-03)",
        title_en="Collaborative Decision Making & Priority Slot Allocation Protocol",
        purpose=(
            "Hướng dẫn Điều phái viên phối hợp với Trung tâm Điều phối Không lưu (FAA ATCSCC / Quản lý Luồng Không lưu) "
            "để xin cải thiện giờ cất cánh (EDCT) hoặc hoán đổi vị trí cất cánh giữa các chuyến bay của hãng."
        ),
        target_roles=["ATC Coordinator", "Flight Dispatcher", "Ramp Control Lead"],
        trigger_condition=(
            "Kích hoạt khi: Chuyến bay bị gán lệnh EDCT trễ > 45 phút HOẶC có nguy cơ vi phạm Tarmac Delay / Crew Timeout."
        ),
        steps=[
            SOPStep(
                step_number=1,
                action_vi="Truy cập hệ thống Quản lý Không lưu Phối hợp (CDM - Collaborative Decision Making)",
                responsible_role="ATC Coordinator",
                timeframe="T - 60 phút trước STD",
                verification_criteria="Tra cứu vị trí của chuyến bay trong bảng luồng chuyến bay quốc gia (National Flow Program).",
                regulatory_notice="FAA Air Traffic Control System Command Center (ATCSCC) CDM Protocol."
            ),
            SOPStep(
                step_number=2,
                action_vi="Thực hiện hoán đổi vị trí cất cánh nội bộ hãng (Slot Swap / Flight Substitution)",
                responsible_role="OCC Chief Dispatcher",
                timeframe="T - 40 phút trước STD",
                verification_criteria="Hoán đổi khe cất cánh sớm của một chuyến bay ít quan trọng/vắng khách hơn cho chuyến bay có nguy cơ cao.",
                regulatory_notice="FAA CDM Slot Substitution Rules (Được quyền hoán đổi giữa các chuyến cùng hãng)."
            ),
            SOPStep(
                step_number=3,
                action_vi="Gửi đề nghị đường bay thoát tắc nghẽn (Reroute Proposal)",
                responsible_role="Flight Dispatcher",
                timeframe="T - 30 phút trước STD",
                verification_criteria="Đệ trình kế hoạch bay qua hành lang phụ vòng tránh vùng bão hoặc vùng nghẽn không phận ATC.",
                regulatory_notice="14 CFR § 121.655 (Sửa đổi kế hoạch bay theo lộ trình được ATC chấp thuận)."
            ),
            SOPStep(
                step_number=4,
                action_vi="Phối hợp Điều hành Mặt đất (Ramp Tower) xếp thứ tự đẩy tàu bay đúng thời điểm",
                responsible_role="Ramp Coordinator",
                timeframe="T - 15 phút trước EDCT",
                verification_criteria="Tàu bay phải ra điểm chờ đường băng (Runway Threshold) đúng cửa sổ dung sai EDCT (-5 phút / +5 phút).",
                regulatory_notice="FAA ATC Compliance Window (+/- 5 phút so với giờ EDCT)."
            )
        ],
        contingency_fallback=(
            "Nếu ATC từ chối mọi yêu cầu hoán đổi do tắc nghẽn không phận nghiêm trọng (Ground Stop toàn diện): "
            "Lập tức phát lệnh giữ máy bay tại cổng (Gate Hold), mở lại cửa cho hành khách hít thở không khí tự nhiên."
        )
    ),

    # -------------------------------------------------------------------------
    # SOP 4: BỒI HOÀN VÀ CHĂM SÓC HÀNH KHÁCH (PASSENGER CARE & REFUND)
    # -------------------------------------------------------------------------
    "sop_passenger_refund_care": SOPChecklist(
        sop_id="sop_passenger_refund_care",
        title_vi="Quy Trình Chăm Sóc & Bồi Hoàn Hành Khách Khi Trễ Kéo Dài (SOP-OCC-PAX-04)",
        title_en="Passenger Welfare & Mandatory Cash Refund Standard Operating Procedure",
        purpose=(
            "Bảo đảm hãng hàng không thực thi đầy đủ trách nhiệm dân sự đối với hành khách bị ảnh hưởng bởi chậm/hủy chuyến, "
            "tuân thủ nghiêm ngặt quy chế hoàn tiền mặt tự động của US DOT và Thông tư Bộ Giao thông Vận tải."
        ),
        target_roles=["Station Customer Service Manager", "Gate Agents", "Finance/Revenue Accounting"],
        trigger_condition=(
            "Kích hoạt khi: Chuyến bay bị chậm từ 2 giờ trở lên HOẶC bị chậm >= 3 giờ (nội địa) / hủy chuyến."
        ),
        steps=[
            SOPStep(
                step_number=1,
                action_vi="Phục vụ nước uống và thức ăn nhẹ tại cửa ra tàu bay (Mốc 2 Giờ)",
                responsible_role="Station Customer Service Lead",
                timeframe="Tại phút thứ 120 kể từ giờ khởi hành lịch trình",
                verification_criteria="Cung cấp phiếu ăn uống (Meal Voucher) trị giá tương đương hoặc phát trực tiếp nước ngọt/bánh ngọt.",
                regulatory_notice="14 CFR § 259.4(b)(1)(i) & Thông tư 19/2023/TT-BGTVT Điều 8 Khoản 2 Điểm a."
            ),
            SOPStep(
                step_number=2,
                action_vi="Tự động gửi tin nhắn/email thông báo quyền lợi lựa chọn cho hành khách (Mốc 3 Giờ)",
                responsible_role="Passenger Notification System",
                timeframe="Tại phút thứ 180 (3 giờ trễ)",
                verification_criteria="Hành khách nhận được liên kết tự chọn: Đổi chuyến bay miễn phí HOẶC Yêu cầu hoàn 100% tiền mặt.",
                regulatory_notice="14 CFR § 260.6(a)(1) (Định nghĩa chậm >= 3h nội địa là thay đổi lịch bay đáng kể)."
            ),
            SOPStep(
                step_number=3,
                action_vi="Kích hoạt kênh Hoàn tiền mặt Tự động trong 07 ngày (Automated Cash Refund)",
                responsible_role="Revenue Accounting Automation",
                timeframe="Trong vòng 07 ngày làm việc",
                verification_criteria="Tiền được hoàn trả trực tiếp về phương thức thanh toán ban đầu (Thẻ tín dụng/Bank transfer), nghiêm cấm ép nhận voucher.",
                regulatory_notice="14 CFR § 260.6(b) (Quy định bắt buộc hoàn tiền mặt trong 7 ngày đối với thẻ tín dụng)."
            ),
            SOPStep(
                step_number=4,
                action_vi="Bố trí xe đưa đón và khách sạn nghỉ ngơi nếu phải lưu trú qua đêm",
                responsible_role="Airport Hotel Logistics Coordinator",
                timeframe="T - 30 phút sau khi có quyết định hoãn qua đêm",
                verification_criteria="100% hành khách không cư trú tại địa phương được cấp phòng khách sạn và vé ăn sáng.",
                regulatory_notice="Thông tư 19/2023/TT-BGTVT Điều 8 Khoản 2 Điểm b."
            )
        ],
        contingency_fallback=(
            "Trường hợp khách sạn quanh sân bay bị kín phòng (Overbooked): "
            "Cấp khoản bồi thường tiền mặt cố định tương đương chi phí tự đặt phòng của hành khách (lưu giữ biên lai) "
            "kèm khoản bồi thường thiện chí (Goodwill Miles/Voucher phụ thêm)."
        )
    ),

    # -------------------------------------------------------------------------
    # SOP 5: TÀU BAY HỎNG HÓC KỸ THUẬT & ĐỔI TÀU BAY DỰ PHÒNG (AOG & TAIL SWAP)
    # -------------------------------------------------------------------------
    "sop_aircraft_aog_swap": SOPChecklist(
        sop_id="sop_aircraft_aog_swap",
        title_vi="Quy Trình Xử Lý Tàu Bay Hỏng Kỹ Thuật & Đổi Tàu Bay Dự Phòng (SOP-OCC-MAINT-05)",
        title_en="Aircraft On Ground (AOG) & Tail-Swap Dispatch Procedure",
        purpose=(
            "Phản ứng nhanh khi tàu bay bị trục trặc kỹ thuật đột xuất trước giờ cất cánh, "
            "thẩm định danh mục trang thiết bị tối thiểu MEL và hoán đổi tàu bay (Tail Swap) nhằm hạn chế tối đa hủy chuyến."
        ),
        target_roles=["Line Maintenance Control (MCC)", "OCC Duty Manager", "Load & Trim Controller"],
        trigger_condition=(
            "Kích hoạt khi: Phi công hoặc thợ máy báo cáo lỗi kỹ thuật không thể khắc phục trong 20 phút trước ETD."
        ),
        steps=[
            SOPStep(
                step_number=1,
                action_vi="Thẩm định Danh Mục Thiết Bị Tối Thiểu (MEL - Minimum Equipment List) trong 15 phút",
                responsible_role="Maintenance Control Center (MCC)",
                timeframe="T - 45 phút trước STD",
                verification_criteria="Xác định lỗi có thuộc diện hoãn sửa chữa (MEL Rectification Interval Class A/B/C/D) hay buộc phải AOG dừng bay.",
                regulatory_notice="14 CFR § 121.628 (Khai thác tàu bay với các trang thiết bị không hoạt động theo MEL)."
            ),
            SOPStep(
                step_number=2,
                action_vi="Kích hoạt tìm kiếm Tàu bay Dự bị (Spare Aircraft / Tail Swap) tại Hub",
                responsible_role="OCC Fleet Controller",
                timeframe="T - 35 phút trước STD",
                verification_criteria="Rà soát tàu bay dự phòng rỗi tại sân hoặc lấy tàu bay từ chuyến bay ít khách/chặng ngắn để hoán đổi cho chặng dài.",
                regulatory_notice="Bảo toàn khai thác các chặng bay quốc tế và chặng bay có mật độ khách nối chuyến cao."
            ),
            SOPStep(
                step_number=3,
                action_vi="Phát lệnh điều chuyển cửa đón khách (Gate Change) & Chuyển hàng hóa, hành lý",
                responsible_role="Ramp Operations & Baggage Lead",
                timeframe="T - 25 phút trước STD",
                verification_criteria="Toàn bộ hành lý ký gửi và suất ăn được chuyển sang số hiệu đuôi tàu bay mới trong 25 phút.",
                regulatory_notice="IATA Ground Operations Manual (IGOM) Fast Aircraft Transfer."
            ),
            SOPStep(
                step_number=4,
                action_vi="Tính toán lại Bảng Tải Trọng & Trọng Tâm (Loadsheet / Trim Sheet) cho số đuôi mới",
                responsible_role="Flight Dispatcher / Load Controller",
                timeframe="T - 10 phút trước STD",
                verification_criteria="Cơ trưởng ký nhận bản Loadsheet mới có đúng trọng lượng rỗng (DOW) và chỉ số cân bằng của tàu bay thay thế.",
                regulatory_notice="14 CFR § 121.665 (Kiểm soát tải trọng và giới hạn trọng tâm tàu bay trước cất cánh)."
            )
        ],
        contingency_fallback=(
            "Nếu không có sẵn tàu bay dự phòng và thời gian sửa chữa > 4 giờ: "
            "Lập tức ban hành quyết định Hủy chuyến bay (Cancel) hoặc Hoãn qua đêm (Overnight Delay) để hành khách không phải ngồi chờ tại phòng chờ ga."
        )
    ),

    # -------------------------------------------------------------------------
    # SOP 6: CHUYỂN HƯỚNG HẠ CÁNH SÂN BAY DỰ BỊ (FLIGHT DIVERSION MANAGEMENT)
    # -------------------------------------------------------------------------
    "sop_flight_diversion": SOPChecklist(
        sop_id="sop_flight_diversion",
        title_vi="Quy Trình Quản Lý Tàu Bay Chuyển Hướng Hạ Cánh Sân Bay Dự Bị (SOP-OCC-DIV-06)",
        title_en="Flight Diversion to Alternate Airport Management Procedure",
        purpose=(
            "Điều hành toàn diện tình huống khẩn nguy khi máy bay không thể hạ cánh tại sân bay đích (do thời tiết xấu, "
            "cấp cứu y tế hoặc sự cố kỹ thuật) và buộc phải chuyển hướng hạ cánh xuống sân bay dự bị (Alternate Airport)."
        ),
        target_roles=["OCC Chief Dispatcher", "Alternate Station Manager", "Crew Rostering Coordinator"],
        trigger_condition=(
            "Kích hoạt khi: Cơ trưởng thông báo quyết định chuyển hướng (Initiate Diversion) hoặc thời tiết sân bay đích Below Minimums."
        ),
        steps=[
            SOPStep(
                step_number=1,
                action_vi="Phối hợp phi hành đoàn tính toán nhiên liệu hạ cánh an toàn tại sân bay dự bị",
                responsible_role="Flight Dispatcher & PIC",
                timeframe="Ngay khi phát lệnh Diversion",
                verification_criteria="Bảo đảm lượng nhiên liệu khi chạm đất tại sân bay dự bị lớn hơn Nhiên liệu Dự trữ Cuối cùng (Final Reserve Fuel - 30/45 phút).",
                regulatory_notice="14 CFR § 121.639 & § 121.645 (Quy định bắt buộc về lượng nhiên liệu dự trữ tối thiểu)."
            ),
            SOPStep(
                step_number=2,
                action_vi="Kích hoạt Đơn vị Phục vụ Mặt đất khẩn cấp tại Sân bay Dự bị (Outstation Alert)",
                responsible_role="Airport Operations Command",
                timeframe="T - 20 phút trước khi hạ cánh dự bị",
                verification_criteria="Bố trí vị trí đỗ, xe thang đón khách, xe cứu thương (nếu là cấp cứu y tế) và xe cấp nhiên liệu sẵn sàng tại bãi đỗ.",
                regulatory_notice="Sân bay dự bị phải nằm trong danh mục chứng chỉ khai thác (OpSpecs) của hãng."
            ),
            SOPStep(
                step_number=3,
                action_vi="Đánh giá giờ làm nhiệm vụ FDP của phi công & Quyết định cho khách ở lại tàu bay hay vào nhà ga",
                responsible_role="OCC Duty Manager",
                timeframe="15 phút sau khi hạ cánh",
                verification_criteria="Nếu dự kiến bay tiếp được trong vòng 45-60 phút: Giữ khách trên máy bay; nếu không: Cho khách vào nhà ga để tránh Tarmac Delay.",
                regulatory_notice="14 CFR § 259.4 (Đồng hồ Tarmac Delay bắt đầu đếm khi bánh chạm đất tại sân bay dự bị!)."
            ),
            SOPStep(
                step_number=4,
                action_vi="Lập Kế hoạch Bay Tiếp Tục (Re-dispatch OFP) hoặc Bố trí Phương Tiện Vận Chuyển Thay Thế",
                responsible_role="Flight Dispatcher / Passenger Services",
                timeframe="Trong vòng 60 phút",
                verification_criteria="Cấp lệnh Dispatch mới để bay tiếp về đích hoặc thuê xe buýt/đặt khách sạn nếu chuyến bay kết thúc tại sân bay phụ.",
                regulatory_notice="Thông tư 19/2023/TT-BGTVT Điều 8 (Nghĩa vụ đưa hành khách về đúng điểm đến trên vé)."
            )
        ],
        contingency_fallback=(
            "Nếu tổ bay bị hết giờ làm nhiệm vụ (Time-out) tại sân bay dự bị: "
            "Ngay lập tức gửi lệnh điều động Tổ bay cứu viện (Rescue Crew) bằng đường bộ hoặc đường hàng không từ Hub gần nhất."
        )
    ),

    # -------------------------------------------------------------------------
    # SOP 7: ĐẾM NGƯỢC KHẨN NGUY CHỐNG BẪY TARMAC DELAY 180 PHÚT
    # -------------------------------------------------------------------------
    "sop_tarmac_clockwork_emergency": SOPChecklist(
        sop_id="sop_tarmac_clockwork_emergency",
        title_vi="Quy Trình Đếm Ngược Khẩn Nguy Chống Bẫy Tarmac Delay 180 Phút (SOP-OCC-TARMAC-07)",
        title_en="Emergency 180-Minute Tarmac Delay Deplaning Clockwork Protocol",
        purpose=(
            "Thiết lập quy chế đếm ngược thời gian nghiêm ngặt đến từng phút khi tàu bay bị tắc nghẽn trên đường lăn mặt đất, "
            "bảo đảm 100% không bao giờ bị nhà chức trách phạt tiền vi phạm $37,377 USD/hành khách."
        ),
        target_roles=["Pilot in Command (PIC)", "OCC Chief Dispatcher", "Airport Ramp Tower"],
        trigger_condition=(
            "Kích hoạt khi: Thời gian tàu bay kẹt trên đường lăn (Taxi-out / Taxi-in) chạm mốc 90 phút kể từ khi rút chèn/hạ cánh."
        ),
        steps=[
            SOPStep(
                step_number=1,
                action_vi="MỐC PHÚT 90: Truy vấn thứ tự cất cánh từ Đài Kiểm soát Mặt đất (Ground Control)",
                responsible_role="Pilot in Command & Dispatcher",
                timeframe="T + 90 phút từ Gate Out",
                verification_criteria="Đánh giá xem máy bay đang ở vị trí thứ mấy trong hàng chờ cất cánh (Departure Queue).",
                regulatory_notice="Đánh giá khả năng cất cánh trước mốc 150 phút."
            ),
            SOPStep(
                step_number=2,
                action_vi="MỐC PHÚT 120 (BẮT BUỘC): Phát đồ ăn nhẹ, nước uống và duy trì điều hòa khoang khách",
                responsible_role="Purser (Tiếp viên trưởng)",
                timeframe="T + 120 phút",
                verification_criteria="100% hành khách được mời nước uống và đồ ăn nhẹ miễn phí; kiểm tra nhà vệ sinh hoạt động tốt.",
                regulatory_notice="14 CFR § 259.4(b)(1)(i) (Vi phạm mốc 2 giờ này hãng sẽ bị phạt hành chính độc lập!)."
            ),
            SOPStep(
                step_number=3,
                action_vi="MỐC PHÚT 150 (ĐIỂM KHÔNG THỂ ĐẢO NGƯỢC - POINT OF NO RETURN): Phát lệnh Quay Đầu Về Cửa",
                responsible_role="Pilot in Command & OCC Dispatcher",
                timeframe="T + 150 phút",
                verification_criteria="Nếu ATC chưa cam kết bằng văn bản/ghi âm máy bay sẽ Wheels-off trong 15 phút tới -> BẮT BUỘC xin đường lăn quay về cổng.",
                regulatory_notice="Chỉ có lý do an toàn bay khẩn cấp mới được ngoại lệ vượt mốc 180 phút."
            ),
            SOPStep(
                step_number=4,
                action_vi="MỐC PHÚT 165 - 175: Cập cầu đón khách (Jet Bridge) và Mở Cửa Cabin",
                responsible_role="Station Ramp Lead & Gate Agents",
                timeframe="Trước phút thứ 180",
                verification_criteria="Cửa máy bay mở, thông báo cho hành khách quyền được rời tàu bay (Deplane Opportunity) để dừng đồng hồ Tarmac Delay.",
                regulatory_notice="14 CFR § 259.4(b)(1) (Chặn đứng nguy cơ vi phạm mốc 3 giờ nội địa / 4 giờ quốc tế)."
            )
        ],
        contingency_fallback=(
            "Nếu tất cả các cửa ra tàu bay tại nhà ga đều bị kín chỗ: "
            "Điều động xe thang cơ động (Mobile Air Stairs) và xe buýt ra bãi đỗ xa (Remote Stand) để giải tỏa hành khách ngay lập tức."
        )
    ),

    # -------------------------------------------------------------------------
    # SOP 8: HỦY CHUYẾN CÓ CHIẾN LƯỢC & HỢP NHẤT CHUYẾN BAY (CANCEL & CONSOLIDATION)
    # -------------------------------------------------------------------------
    "sop_cancellation_consolidation": SOPChecklist(
        sop_id="sop_cancellation_consolidation",
        title_vi="Quy Trình Hủy Chuyến Có Chiến Lược & Hợp Nhất Chuyến Bay (SOP-OCC-CANCEL-08)",
        title_en="Strategic Flight Cancellation & Flight Consolidation Procedure",
        purpose=(
            "Quy định nguyên tắc ra quyết định hủy chuyến có chủ đích trong các cuộc khủng hoảng diện rộng "
            "(bão tuyết, bão lớn, Ground Stop toàn mạng), bảo toàn tính toàn vẹn của lịch bay ngày hôm sau "
            "và giảm thiểu chi phí bồi thường."
        ),
        target_roles=["OCC Executive Director", "Network Planning Manager", "Passenger Reaccommodation Lead"],
        trigger_condition=(
            "Kích hoạt khi: Sân bay Hub bị cắt giảm > 40% công suất tiếp nhận hoặc có bão tuyết kéo dài trên 6 giờ."
        ),
        steps=[
            SOPStep(
                step_number=1,
                action_vi="Áp dụng Ma Trận Ưu Tiên Hủy Chuyến (Cancellation Priority Matrix)",
                responsible_role="Network Operations Planner",
                timeframe="T - 4 giờ trước đợt cao điểm",
                verification_criteria="Ưu tiên hủy: 1) Chuyến bay rỗng/Ferry; 2) Chặng bay ngắn có tần suất dày (> 6 chuyến/ngày); Bảo vệ: Chuyến quốc tế và chặng độc đạo.",
                regulatory_notice="Tối ưu hóa số lượng hành khách bị ảnh hưởng trên mỗi ghế hủy."
            ),
            SOPStep(
                step_number=2,
                action_vi="Hợp nhất Chuyến bay (Flight Consolidation / Aircraft Upsizing)",
                responsible_role="OCC Duty Manager",
                timeframe="T - 3 giờ trước STD",
                verification_criteria="Gom hành khách của 2 chuyến bay thân hẹp (A320/B737) bị hủy sang 1 chuyến bay sử dụng tàu bay thân rộng (B787/A350).",
                regulatory_notice="Giảm tải 50% số slot cất hạ cánh cần sử dụng tại sân bay nghẽn."
            ),
            SOPStep(
                step_number=3,
                action_vi="Ban hành Chính Sách Miễn Trừ Du Lịch (Travel Waiver Policy)",
                responsible_role="Commercial & Revenue Management",
                timeframe="Ngay khi có quyết định hủy",
                verification_criteria="Mở chức năng cho hành khách tự đổi vé miễn phí sang ngày khác hoặc nhận hoàn 100% tiền mặt tự động trên App/Web.",
                regulatory_notice="14 CFR § 260.6 (Quy định bắt buộc hoàn tiền mặt khi hủy chuyến)."
            ),
            SOPStep(
                step_number=4,
                action_vi="Tái bố trí Vị Trí Nghỉ Đêm Của Tàu Bay (Aircraft Overnight Positioning)",
                responsible_role="Fleet Routing Controller",
                timeframe="T - 2 giờ trước nửa đêm",
                verification_criteria="Đảm bảo máy bay và phi hành đoàn nằm lại đúng các sân bay căn cứ để lịch trình sáng hôm sau khởi động đúng giờ.",
                regulatory_notice="Chặn đứng sự cố hủy chuyến dây chuyền sang ngày hôm sau."
            )
        ],
        contingency_fallback=(
            "Nếu tổng số hành khách bị ảnh hưởng vượt quá 5,000 người: "
            "Kích hoạt Trung tâm Chăm sóc Khách hàng Khẩn cấp (Emergency Call Center Callout) và đàm phán hợp đồng khối với chuỗi khách sạn quanh sân bay."
        )
    ),
}


# =============================================================================
# 3. TEXT UTILITIES & FUZZY MATCHING HELPERS
# =============================================================================

def strip_accents(text: str) -> str:
    """Strip Vietnamese accents and diacritics for robust matching."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", text).lower()


def tokenize(text: str) -> Set[str]:
    """Tokenize string into normalized alpha-numeric word tokens."""
    normalized = strip_accents(text)
    tokens = set(re.findall(r"[a-z0-9_]+", normalized))
    return {t for t in tokens if len(t) > 1}


# =============================================================================
# 4. KNOWLEDGE RETRIEVAL & QUERY API
# =============================================================================

def get_knowledge_base() -> Dict[str, KnowledgeTerm]:
    """Return all standardized domain knowledge terms (32 terms)."""
    return KNOWLEDGE_TERMS


def list_terms(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List terms optionally filtered by category."""
    terms = list(KNOWLEDGE_TERMS.values())
    if category:
        terms = [t for t in terms if t.category == category]
    return [t.to_dict() for t in terms]


def lookup_term(query: str) -> Optional[Dict[str, Any]]:
    """
    Search for a single term by exact term_id, acronym, or close alias.
    Returns dictionary of the matched term or None.
    """
    clean_q = query.strip().lower()
    norm_q = strip_accents(clean_q)

    # 1. Exact match on term_id
    if clean_q in KNOWLEDGE_TERMS:
        return KNOWLEDGE_TERMS[clean_q].to_dict()

    # 2. Match on acronym or exact name
    for term_id, term in KNOWLEDGE_TERMS.items():
        if term.acronym and term.acronym.lower() == clean_q:
            return term.to_dict()
        if strip_accents(term.name_vi) == norm_q or term.name_en.lower() == clean_q:
            return term.to_dict()

    # 3. Match keyword in term's keyword list
    for term_id, term in KNOWLEDGE_TERMS.items():
        for kw in term.keywords:
            if strip_accents(kw) == norm_q:
                return term.to_dict()

    return None


def get_sop_checklists() -> Dict[str, SOPChecklist]:
    """Return all 8 Standard Operating Procedure checklists."""
    return SOP_CHECKLISTS


def get_sop_checklist(sop_id: str) -> Optional[Dict[str, Any]]:
    """Return a single SOP checklist by sop_id or alias, or None."""
    clean_id = sop_id.strip().lower()
    if clean_id in SOP_CHECKLISTS:
        return SOP_CHECKLISTS[clean_id].to_dict()

    # Match aliases
    for k, v in SOP_CHECKLISTS.items():
        if clean_id in k or clean_id in v.title_en.lower() or strip_accents(clean_id) in strip_accents(v.title_vi):
            return v.to_dict()

    return None


def search_knowledge(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Intelligent token-based ranking search across all 32 Knowledge Terms and 8 SOPs.
    Returns top_k ranked matches with relevance scores.
    """
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    scored_results: List[Tuple[float, str, Dict[str, Any]]] = []

    # 1. Search in Knowledge Terms (32 items)
    for term_id, term in KNOWLEDGE_TERMS.items():
        score = 0.0
        # Exact acronym match
        if term.acronym and strip_accents(term.acronym.lower()) in query_tokens:
            score += 10.0

        # Term ID match
        if term.term_id in query_tokens:
            score += 8.0

        # Match in keywords
        for kw in term.keywords:
            kw_tokens = tokenize(kw)
            common = query_tokens.intersection(kw_tokens)
            if common:
                score += len(common) * 3.0
                if kw_tokens.issubset(query_tokens):
                    score += 5.0

        # Match in definition / title
        title_tokens = tokenize(f"{term.name_vi} {term.name_en}")
        common_title = query_tokens.intersection(title_tokens)
        score += len(common_title) * 2.0

        if score > 0:
            item_data = term.to_dict()
            item_data["_result_type"] = "term"
            scored_results.append((score, term_id, item_data))

    # 2. Search in SOP Checklists (8 items)
    for sop_id, sop in SOP_CHECKLISTS.items():
        score = 0.0
        clean_sop_id = sop_id.replace("sop_", "")
        if sop_id in query_tokens or clean_sop_id in query_tokens:
            score += 12.0

        step_text = " ".join([st.action_vi for st in sop.steps])
        sop_tokens = tokenize(f"{sop.sop_id} {sop.title_vi} {sop.title_en} {sop.purpose} {step_text}")
        common_sop = query_tokens.intersection(sop_tokens)
        score += len(common_sop) * 3.0

        if "aog" in query_tokens and "aog" in sop_id:
            score += 10.0
        if "diversion" in query_tokens and "diversion" in sop_id:
            score += 10.0

        if "sop" in query_tokens or "quy trinh" in strip_accents(query) or "checklist" in query_tokens:
            score += 6.0

        if score > 0:
            item_data = sop.to_dict()
            item_data["_result_type"] = "sop"
            scored_results.append((score, sop_id, item_data))

    # Sort descending by score
    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [item[2] for item in scored_results[:top_k]]


def explain_term(query: str) -> Dict[str, Any]:
    """
    High-level entry point to explain a concept or return relevant knowledge.
    Tries exact lookup first, falls back to semantic search.
    """
    matched = lookup_term(query)
    if matched:
        return {
            "status": "exact_match",
            "query": query,
            "term": matched,
            "markdown": format_term_card_markdown(matched),
        }

    search_hits = search_knowledge(query, top_k=3)
    if search_hits:
        first_hit = search_hits[0]
        if first_hit.get("_result_type") == "sop":
            md = format_sop_markdown(first_hit)
        else:
            md = format_term_card_markdown(first_hit)

        return {
            "status": "search_hit",
            "query": query,
            "best_match": first_hit,
            "related_results": search_hits[1:],
            "markdown": md,
        }

    return {
        "status": "not_found",
        "query": query,
        "message": f"Không tìm thấy khái niệm hoặc quy trình nào khớp với từ khóa '{query}'.",
        "available_topics": [t.name_vi for t in KNOWLEDGE_TERMS.values()],
    }


# =============================================================================
# 5. MARKDOWN FORMATTERS FOR UI, COPILOT & REPORTS
# =============================================================================

def format_term_card_markdown(term: Dict[str, Any]) -> str:
    """Format a KnowledgeTerm dictionary into a rich, structured Markdown card."""
    acronym_str = f" ({term.get('acronym')})" if term.get("acronym") else ""
    md = [
        f"### 📘 {term.get('name_vi')}{acronym_str}",
        f"**Tên tiếng Anh**: *{term.get('name_en')}*  ",
        f"**Phân loại**: `{term.get('category')}`  \n",
        f"**1. Khái Niệm & Định Nghĩa**:\n> {term.get('definition_vi')}\n",
        f"**2. Ý Nghĩa Đối Với Vận Hành (Business Significance)**:\n{term.get('business_significance')}\n",
        f"**3. Công Thức & Quy Chuẩn Pháp Lý**:\n```text\n{term.get('calculation_or_rule')}\n```\n",
        f"**4. Hậu Quả Tác Nghiệp (Operational Impact)**:\n⚠️ {term.get('operational_impact')}\n",
    ]

    regs = term.get("related_regulations", [])
    if regs:
        md.append("**5. Điều Khoản Luật Định Liên Quan**:")
        for r in regs:
            md.append(f"- ⚖️ {r}")
        md.append("")

    faqs = term.get("common_questions", [])
    if faqs:
        md.append("**6. Câu Hỏi Thường Gặp (OCC Q&A)**:")
        for f in faqs:
            md.append(f"- **Hỏi**: *{f.get('q')}*")
            md.append(f"  **Trả lời**: {f.get('a')}")
        md.append("")

    return "\n".join(md)


def format_sop_markdown(sop: Dict[str, Any]) -> str:
    """Format a SOPChecklist dictionary into a structured step-by-step checklist."""
    roles = ", ".join(sop.get("target_roles", []))
    md = [
        f"### 📋 {sop.get('title_vi')}",
        f"**Mã quy trình**: `{sop.get('sop_id')}` | **English**: *{sop.get('title_en')}*  ",
        f"**Vai trò phụ trách**: {roles}  ",
        f"**Điều kiện kích hoạt**: {sop.get('trigger_condition')}  \n",
        f"**Mục Tiêu Quy Trình**:\n> {sop.get('purpose')}\n",
        "**Các Bước Thực Hiện Bắt Buộc (Step-by-Step Checklist)**:\n",
    ]

    steps = sop.get("steps", [])
    for step in steps:
        s_num = step.get("step_number")
        action = step.get("action_vi")
        role = step.get("responsible_role")
        tf = step.get("timeframe")
        crit = step.get("verification_criteria")
        notice = step.get("regulatory_notice")

        md.append(f"#### Bước {s_num}: {action}")
        md.append(f"- **Phụ trách**: `{role}`")
        md.append(f"- **Thời điểm thực hiện**: ⏱️ `{tf}`")
        md.append(f"- **Tiêu chí nghiệm thu**: ✅ {crit}")
        if notice:
            md.append(f"- **Căn cứ pháp lý**: ⚖️ *{notice}*")
        md.append("")

    fallback = sop.get("contingency_fallback")
    if fallback:
        md.append(f"**Phương Án Xử Lý Dự Phòng (Contingency Fallback)**:\n🚨 {fallback}\n")

    return "\n".join(md)


def format_catalog_markdown() -> str:
    """Format full catalog of all 40 items (32 terms and 8 SOPs) for overview."""
    md = [
        "# 📚 TỪ ĐIỂN TRI THỨC VẬN HÀNH BAY & MACHINE LEARNING (KNOWLEDGE CATALOG - 40 ITEMS)",
        f"\n**Tổng số đề mục**: {len(KNOWLEDGE_TERMS)} thuật ngữ chuyên sâu + {len(SOP_CHECKLISTS)} quy trình tác nghiệp chuẩn.\n",
        "## 1. Chỉ Số Vận Hành & Pháp Lý Hàng Không (Aviation Operational & Legal Metrics - 18 mục)\n",
    ]
    for t in KNOWLEDGE_TERMS.values():
        if t.category == "aviation_metrics":
            acronym = f" ({t.acronym})" if t.acronym else ""
            md.append(f"- **`{t.term_id}`**: **{t.name_vi}{acronym}** - *{t.name_en}*")

    md.append("\n## 2. Chỉ Số Machine Learning & Toán Học (ML & Mathematical Metrics - 14 mục)\n")
    for t in KNOWLEDGE_TERMS.values():
        if t.category == "ml_metrics":
            acronym = f" ({t.acronym})" if t.acronym else ""
            md.append(f"- **`{t.term_id}`**: **{t.name_vi}{acronym}** - *{t.name_en}*")

    md.append("\n## 3. Danh Mục Quy Trình Thao Tác Chuẩn (Standard Operating Procedures - 8 SOPs)\n")
    for s in SOP_CHECKLISTS.values():
        md.append(f"- **`{s.sop_id}`**: **{s.title_vi}** - *{s.title_en}* ({len(s.steps)} bước)")

    return "\n".join(md)


# =============================================================================
# CONTEXT-AWARE ADVISORY ENGINE RE-EXPORTS (PHASE 6.2)
# =============================================================================
from ml.advisory import (  # noqa: E402
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

# =============================================================================
# CONVERSATIONAL CHATBOT Q&A LAZY RE-EXPORTS (PHASE 6.3)
# =============================================================================
def __getattr__(name: str):
    if name in ("ChatMessage", "ChatResponse", "ask_copilot", "get_copilot_quick_prompts"):
        import ml.chat as _chat
        return getattr(_chat, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")



