"""
Generate comprehensive Word (.docx) project report for Data Analyst role.
Covers end-to-end architecture, business problems, data profiling, dbt modeling,
ML tournament, Power BI reporting, and interview cheatsheet.
"""

from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOCX_PATH = Path("docs/BAO_CAO_DU_AN_DATA_ANALYST.docx")

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = Document()

    # Set page margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles & Colors
    NAVY = RGBColor(27, 54, 93)      # #1B365D Primary
    SLATE = RGBColor(74, 96, 122)    # #4A607A Secondary
    DARK = RGBColor(34, 34, 34)      # Body text
    GOLD = RGBColor(184, 134, 11)    # Highlights
    GRAY_BG = "F4F6F9"
    HEADER_BG = "1B365D"

    # Title Cover Page / Header
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(20)
    title_p.paragraph_format.space_after = Pt(6)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = title_p.add_run("BÁO CÁO TỔNG QUAN DỰ ÁN & HỒ SƠ NĂNG LỰC DATA ANALYST")
    run_t.font.name = "Arial"
    run_t.font.size = Pt(22)
    run_t.font.bold = True
    run_t.font.color.rgb = NAVY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(24)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub_p.add_run("NỀN TẢNG KỸ THUẬT DỮ LIỆU & PHÂN TÍCH VẬN HÀNH HÀNG KHÔNG\n(AIRLINE DATA PLATFORM & OPERATIONS ANALYTICS)")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(13)
    run_sub.font.bold = True
    run_sub.font.color.rgb = SLATE

    # Author metadata box
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    meta_info = [
        ("Người thực hiện:", "Nguyễn Hoàng Thanh Tâm"),
        ("Vai trò dự án:", "Data Analyst (Chủ trì Nghiệp vụ & Mô hình Phân tích)"),
        ("Email liên hệ:", "tamnguyen130620004@gmail.com"),
        ("Kho lưu trữ GitHub:", "https://github.com/battina1999/airline-data-platform")
    ]
    for idx, (label, val) in enumerate(meta_info):
        row = meta_table.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        cell_lbl.width = Inches(2.2)
        cell_val.width = Inches(4.3)
        set_cell_background(cell_lbl, "EAEEF3")
        set_cell_background(cell_val, "FAFAFA")
        set_cell_margins(cell_lbl, top=80, bottom=80, left=120, right=120)
        set_cell_margins(cell_val, top=80, bottom=80, left=120, right=120)

        p1 = cell_lbl.paragraphs[0]
        r1 = p1.add_run(label)
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = NAVY

        p2 = cell_val.paragraphs[0]
        r2 = p2.add_run(val)
        r2.font.size = Pt(10)
        r2.font.bold = (idx == 0 or idx == 1)
        r2.font.color.rgb = DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(18)

    def add_sec_heading(title_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title_text)
        run.font.name = "Arial"
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = NAVY
        return p

    def add_sub_heading(title_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title_text)
        run.font.name = "Arial"
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = SLATE
        return p

    def add_body_p(text, bold_prefix="", italic_note=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.bold = True
            r_b.font.size = Pt(10.5)
            r_b.font.color.rgb = NAVY
        r_t = p.add_run(text)
        r_t.font.size = Pt(10.5)
        r_t.font.color.rgb = DARK
        if italic_note:
            r_i = p.add_run(italic_note)
            r_i.font.italic = True
            r_i.font.size = Pt(9.5)
            r_i.font.color.rgb = SLATE
        return p

    def add_callout(text, prefix="LƯU Ý TRỌNG TÂM: "):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.rows[0].cells[0]
        cell.width = Inches(6.5)
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, top=100, bottom=100, left=180, right=180)
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.15
        r_p = p.add_run(prefix)
        r_p.font.bold = True
        r_p.font.size = Pt(10)
        r_p.font.color.rgb = NAVY
        r_c = p.add_run(text)
        r_c.font.size = Pt(10)
        r_c.font.color.rgb = DARK
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 1. TỔNG QUAN
    add_sec_heading("1. TỔNG QUAN DỰ ÁN & VAI TRÒ DATA ANALYST")
    add_body_p(
        "Airline Data Platform là dự án xây dựng một hệ sinh thái kỹ thuật dữ liệu và phân tích vận hành hoàn chỉnh chuẩn doanh nghiệp. "
        "Dự án được thiết kế để giải quyết bài toán cốt lõi của ngành hàng không: giám sát tỷ lệ đúng giờ (On-Time Performance - OTP), "
        "bóc tách nguyên nhân gốc rễ gây trễ chuyến, định lượng thiệt hại tài chính và dự báo rủi ro trễ chuyến trước giờ khởi hành."
    )
    add_body_p(
        "Hệ thống có khả năng xử lý mượt mà trên bộ dữ liệu thực tế khổng lồ gồm 3.453.795 chuyến bay từ Cục Thống kê Vận tải Hoa Kỳ (US DOT BTS) "
        "trải rộng trên 345 sân bay và 15 hãng hàng không thương mại hàng đầu nước Mỹ."
    )
    add_body_p(
        "Trong dự án này, bạn đảm nhiệm vai trò Data Analyst chủ trì, trực tiếp tham gia và thực thi xuyên suốt các mắt xích: "
        "khảo sát dữ liệu thô (Data Profiling), thiết lập bài toán kinh doanh, tham gia thiết kế mô hình kho dữ liệu đa chiều (dbt Kimball Star Schema), "
        "kiểm tra hợp đồng dữ liệu & đối soát, đánh giá đấu trường 5 mô hình học máy (ML Tournament), và trực tiếp phát triển báo cáo Power BI 4 trang "
        "đạt chuẩn Gartner Analytics Maturity cùng bảng điều khiển vận hành OCC Console."
    )

    # 2. BÀI TOÁN KINH DOANH
    add_sec_heading("2. BÀI TOÁN KINH DOANH & CÁC QUY CHUẨN NGÀNH HÀNG KHÔNG")
    add_body_p(
        "Trong ngành hàng không, trễ chuyến bay không đơn thuần là sự chậm trễ lịch trình mà là một chuỗi rủi ro liên hoàn tác động nghiêm trọng đến chi phí và pháp lý:"
    )
    add_body_p(
        "Định mức thiệt hại tài chính của FAA ($101.18 USD / phút): ",
        bold_prefix="• Chi phí vận hành trực tiếp: "
    )
    add_body_p(
        "Theo nghiên cứu chính thức của Cục Hàng không Liên bang Hoa Kỳ (FAA) phối hợp cùng Hiệp hội Airlines for America (A4A), "
        "mỗi phút chuyến bay bị trễ gây thiệt hại bình quân $101.18 USD chi phí vận hành trực tiếp (Direct Operating Cost), "
        "bao gồm nhiên liệu tiêu hao khi máy bay nổ máy chờ trên đường lăn, tiền lương phụ trội ngoài giờ của phi hành đoàn, "
        "chi phí bảo dưỡng gia tăng và chi phí dịch vụ chăm sóc hành khách tại cửa khẩu."
    )
    add_body_p(
        "Hiệu ứng Domino từ máy bay quay đầu (Late Aircraft Delay): ",
        bold_prefix="• Trễ lây lan dây chuyền: "
    )
    add_body_p(
        "Do một chiếc máy bay thường thực hiện liên tiếp 4–6 chặng bay trong một ngày, một sự cố trễ chuyến vào buổi sáng tại sân bay xuất phát "
        "sẽ kích hoạt hiệu ứng domino làm trễ toàn bộ các chuyến bay tiếp theo của chính chiếc máy bay đó. Phân tích dữ liệu cho thấy "
        "nguyên nhân Late Aircraft chiếm tới gần 40% tổng số phút trễ của toàn mạng bay."
    )
    add_body_p(
        "Chế tài pháp lý nghiêm khắc của cơ quan quản lý: ",
        bold_prefix="• Rủi ro pháp lý & chế tài: "
    )
    add_body_p(
        "- 14 CFR § 259.4 (Tarmac Delay Rule): Phạt hành chính lên tới $37.377 USD trên mỗi hành khách nếu máy bay bị kẹt trên sân đỗ hoặc đường lăn quá 180 phút (đối với chuyến nội địa) mà không cho hành khách rời tàu bay.\n"
        "- 14 CFR § 260.6 (Cash Refund Mandate): Bắt buộc các hãng bay phải hoàn tiền mặt 100% tự động (ước tính $275 USD/khách) nếu chuyến bay bị trễ đáng kể từ 3 tiếng trở lên.\n"
        "- FAR Part 117 (Flight Duty Period): Quy định nghiêm ngặt thời gian làm nhiệm vụ bay của phi công và tiếp viên. Nếu chuyến bay trễ vượt ngưỡng FDP, hãng bay bắt buộc phải hủy chuyến hoặc kích hoạt tổ bay dự phòng."
    )

    # 3. HÀNH TRÌNH THỰC HIỆN
    add_sec_heading("3. HÀNH TRÌNH DỰ ÁN: TOÀN BỘ CÔNG VIỆC BẠN ĐÃ THỰC HIỆN")

    add_sub_heading("3.1. Khám phá & Đọc hiểu dữ liệu thô (Data Profiling & Understanding)")
    add_body_p(
        "Bạn đã khảo sát chi tiết bộ dữ liệu thô 3.45 triệu dòng và phát hiện 9 vấn đề chất lượng dữ liệu then chốt (Business Questions BQ-01 đến BQ-09):"
    )

    # Bảng 9 vấn đề
    tbl_bq = doc.add_table(rows=10, cols=3)
    tbl_bq.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_bq.autofit = False

    headers_bq = ["Mã bài toán", "Hiện tượng trong dữ liệu thô", "Bản chất nghiệp vụ & Giải pháp bạn đưa ra"]
    for i, h in enumerate(headers_bq):
        c = tbl_bq.rows[0].cells[i]
        set_cell_background(c, HEADER_BG)
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    tbl_bq.rows[0].cells[0].width = Inches(1.0)
    tbl_bq.rows[0].cells[1].width = Inches(2.2)
    tbl_bq.rows[0].cells[2].width = Inches(3.3)

    bq_data = [
        ("BQ-01", "Giá trị sentinel -9999 ở các cột mốc giờ", "115/116 dòng có cancelled = 0. Đây là lỗi mất tín hiệu radar/transponder chứ không phải hủy chuyến. Đưa về NULL ở staging."),
        ("BQ-02", "3 dòng dữ liệu bị trùng lặp 100%", "Do cơ quan BTS vô tình lưu trùng bản ghi cùng mốc giờ. Giải pháp: ghi nhận vào nhật ký kiểm toán và dùng DISTINCT khử trùng ở staging."),
        ("BQ-03", "Lệch 1-5 phút giữa tổng 5 cột trễ và arr_delay_min", "Do sai số làm tròn số học giữa các đơn vị báo cáo. Quy chuẩn: Lấy cột arr_delay_min làm mốc chuẩn tính toán."),
        ("BQ-04", "Chuyến bay có cự ly siêu ngắn (10-30 dặm)", "Là các chuyến bay chuyển sân (ferry/repositioning) giữa các sân bay cùng cụm đô thị (JFK-LGA, ORD-MDW). Giữ lại và gắn cờ riêng."),
        ("BQ-05", "Số hiệu chuyến bay (flight_number) bị trùng", "Mỗi hãng bay tái sử dụng số hiệu chuyến bay mỗi ngày. Bạn thiết kế khóa thay thế Surrogate Key từ carrier + flight_num + date + origin."),
        ("BQ-06", "Mốc giờ là số nguyên (1430, 915, 5)", "Chuẩn hóa sang kiểu thời gian chuẩn HH:MM và timestamp để phục vụ phân tích theo dải giờ cao điểm."),
        ("BQ-07", "Quy chuẩn đúng giờ A14", "Theo chuẩn FAA, chuyến bay chỉ bị coi là trễ khi đến trễ từ 15 phút trở lên (arr_delay > 14)."),
        ("BQ-08", "Thời gian quay đầu (Turnaround time)", "Truy vết theo tail_number để tính khoảng cách giữa giờ hạ cánh chuyến trước và giờ cất cánh chuyến sau của cùng một máy bay."),
        ("BQ-09", "Chuyến bay bị hủy và chuyển hướng", "Tách riêng luồng phân tích cancelled = 1 và diverted = 1 khỏi tập huấn luyện dự báo trễ để tránh làm lệch phân phối mô hình.")
    ]

    for idx, (b_id, phen, sol) in enumerate(bq_data):
        row = tbl_bq.rows[idx + 1]
        row.cells[0].width = Inches(1.0)
        row.cells[1].width = Inches(2.2)
        row.cells[2].width = Inches(3.3)
        bg = GRAY_BG if idx % 2 == 1 else "FFFFFF"
        for i_c, text_val in enumerate([b_id, phen, sol]):
            c = row.cells[i_c]
            set_cell_background(c, bg)
            set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            p = c.paragraphs[0]
            r = p.add_run(text_val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = DARK
            if i_c == 0:
                r.font.bold = True
                r.font.color.rgb = NAVY

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_sub_heading("3.2. Mô hình hóa kho dữ liệu Kimball Star Schema qua dbt")
    add_body_p(
        "Bạn đã áp dụng phương pháp luận mô hình hóa chiều (Dimensional Modeling) của Ralph Kimball, chia pipeline thành các tầng chuyên biệt:"
    )
    add_body_p(
        "• Tầng Staging (stg_*): Làm sạch dữ liệu thô, ép kiểu dữ liệu chuẩn, khử trùng lặp, tính cờ boolean và loại bỏ sentinel -9999.\n"
        "• Tầng Bảng Chiều (dim_*): dim_airport (tọa độ, phân loại hub), dim_airline (tên hãng, mã IATA), dim_date (lịch biểu, quý, ngày cuối tuần), dim_aircraft (số hiệu đuôi tàu bay).\n"
        "• Tầng Bảng Sự Kiện (fact_*): fact_flights (chứa 3.45M dòng chuyến bay và các độ đo định lượng), fact_flight_delays (chứa chi tiết 5 nhóm nguyên nhân trễ).\n"
        "• Tầng Phân tích & Đặc trưng (marts_*): route_performance (tổng hợp hiệu năng từng chặng bay), fct_features_flight (feature store phục vụ học máy)."
    )
    add_callout("Hiệu năng thực tế: 56/56 model dbt và schema test đã hoàn tất thành công trong 3.34 giây trên PostgreSQL và 11 giây trên 3.45 triệu dòng dữ liệu BTS.")

    add_sub_heading("3.3. Kiểm định chất lượng & Đối soát dữ liệu (Data Governance & Reconciliation)")
    add_body_p(
        "Để đảm bảo dữ liệu khi lên báo cáo đạt độ tin cậy tuyệt đối:\n"
        "• Hợp đồng dữ liệu Great Expectations v0.18: Thiết lập bộ kiểm thử tự động kiểm tra schema, ràng buộc không được rỗng, miền giá trị cự ly > 0.\n"
        "• Đối soát dữ liệu 100% dòng (Reconciliation Engine): Xây dựng module tự động so khớp số dòng giữa Nguồn -> Bảng Raw -> Bảng Fact. Đảm bảo 100% dòng dữ liệu đều được giải trình minh bạch, không có bản ghi nào bị thất thoát."
    )

    add_sub_heading("3.4. Đấu trường Học máy dự báo trễ chuyến (Machine Learning Tournament)")
    add_body_p(
        "Bạn tham gia thiết kế bài toán phân loại nhị phân dự báo trễ chuyến A14 với quy chuẩn kỹ thuật cao:\n"
        "• Chống rò rỉ dữ liệu bằng Temporal Split: Phân chia tập huấn luyện và kiểm thử nghiêm ngặt theo trục thời gian (FlightDate). Không dùng Random Split để tránh dùng dữ liệu tương lai đoán quá khứ.\n"
        "• Đấu trường 5 Thuật toán: So tài giữa Logistic Regression (Baseline), LightGBM, CatBoost, XGBoost và Soft-Voting Ensemble.\n"
        "• Bộ chỉ số đánh giá thực tế: Đạt Holdout Test AUC 0.741+, Lift @ 10% đạt 2.37x (chứng minh top 10% chuyến bay cảnh báo bắt trúng chuyến trễ cao gấp 2.37 lần ngẫu nhiên), Brier Score được chuẩn hóa tin cậy.\n"
        "• Tối ưu ngưỡng quyết định (Threshold Tuning): Tinh chỉnh ngưỡng phân loại ưu tiên Recall nhằm phát hiện sớm tối đa các chuyến bay có nguy cơ trễ cao."
    )

    add_sub_heading("3.5. Xây dựng Báo cáo Power BI 4 Trang Chuẩn Gartner")
    add_body_p(
        "Bạn trực tiếp xây dựng file Dashboard.pbix với giao diện tối (Dark Mode) chuẩn phòng điều hành bay, dẫn dắt câu chuyện qua 4 cấp độ phân tích của Gartner:"
    )
    add_body_p(
        "1. Trang 1 - Executive Operations Overview (Phân tích Mô tả - Descriptive):\n"
        "   - Cung cấp bức tranh tổng thể: Tổng số chuyến bay, Tỷ lệ đúng giờ (OTP %), Tỷ lệ hủy chuyến, và Tổng tổn thất chi phí trễ trực tiếp ($101.18/phút).\n"
        "   - Phân bổ xu hướng theo thời gian và thị phần các hãng bay.\n\n"
        "2. Trang 2 - Delay Root-Cause & Domino Propagation (Phân tích Chẩn đoán - Diagnostic):\n"
        "   - Bóc tách 5 nguyên nhân gốc rễ: Carrier, Weather, NAS, Security, Late Aircraft.\n"
        "   - Phân tích hiệu ứng Domino: Chứng minh Late Aircraft delay chiếm ~40% tổng số phút trễ do vòng quay tàu bay.\n\n"
        "3. Trang 3 - Hub Bottlenecks & Route Economics (Đào sâu Nút thắt - Diagnostic Deep-Dive):\n"
        "   - Ma trận tắc nghẽn tại 5 sân bay trung chuyển lớn nhất nước Mỹ (DFW, ORD, ATL, JFK, DEN).\n"
        "   - Phân tích thời gian lăn bánh trước cất cánh (Taxi-out) tăng vọt lên 35–48 phút trong khung giờ cao điểm tối 17h–20h.\n\n"
        "4. Trang 4 - Predictive Delay Risk & Regulatory Governance (Phân tích Dự báo & Đề xuất - Predictive & Prescriptive):\n"
        "   - Bảng tổng hợp chất lượng mô hình dự báo (AUC, Lift@10%, Brier Score).\n"
        "   - Phân bổ xác suất rủi ro và danh mục các chuyến bay sắp tới cần ưu tiên can thiệp.\n"
        "   - Giám sát nguy cơ vi phạm luật kẹt sân đỗ 180 phút (14 CFR § 259.4 Tarmac Delay) và tích hợp khung điều phối vận hành.\n\n"
        "• Hệ thống hơn 50 thước đo DAX chuyên sâu: Viết toàn bộ các công thức tính toán lũy kế, Time Intelligence, lọc động theo điều kiện."
    )

    add_sub_heading("3.6. Xây dựng Giao diện Điều phối Vận hành OCC Console")
    add_body_p(
        "Bạn kết hợp phát triển giao diện điều phối vận hành phòng OCC hỗ trợ tác nghiệp thời gian thực:\n"
        "• Tra cứu chuyến bay theo số hiệu, hiển thị thẻ Hero Boarding Pass với mã chặng bay và xác suất rủi ro.\n"
        "• Bóc tách 4 tầng rủi ro tài chính: Chi phí trễ thông thường, Phạt kẹt sân đỗ Tarmac ($37.377/khách), Hoàn tiền mặt bắt buộc ($275/khách), và Tổng tổn thất tiềm năng.\n"
        "• Bộ mô phỏng What-If: Tính toán ngay số tiền tiết kiệm được (Net Savings) khi điều phối viên thực hiện: đổi giờ bay, kích hoạt tổ bay dự phòng, tăng tốc hành trình, hoặc đổi máy bay rảnh rỗi.\n"
        "• Tự động xuất slide PowerPoint 16:9 (.pptx) và báo cáo HTML chỉ bằng 1 cú nhấp chuột."
    )

    # 4. CÁC CON SỐ ĐO LƯỜNG
    add_sec_heading("4. BẢNG TỔNG HỢP CÁC CON SỐ ĐO LƯỜNG THỰC TẾ")

    tbl_metrics = doc.add_table(rows=9, cols=3)
    tbl_metrics.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_metrics.autofit = False

    headers_m = ["Chỉ số", "Giá trị thực nghiệm đạt được", "Ý nghĩa chuyên môn"]
    for i, h in enumerate(headers_m):
        c = tbl_metrics.rows[0].cells[i]
        set_cell_background(c, HEADER_BG)
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    tbl_metrics.rows[0].cells[0].width = Inches(2.0)
    tbl_metrics.rows[0].cells[1].width = Inches(2.0)
    tbl_metrics.rows[0].cells[2].width = Inches(2.5)

    metrics_data = [
        ("Số lượng chuyến bay nạp", "3.453.795 chuyến bay", "Nạp 1.5 GB file CSV trong ~25 giây vào kho dữ liệu."),
        ("Quy mô mạng lưới", "345 sân bay & 15 hãng bay", "Bao phủ toàn bộ mạng bay nội địa thương mại Hoa Kỳ."),
        ("Tốc độ build dbt", "56/56 models pass trong 3.34s", "Mô hình hóa Star Schema đạt chuẩn, tốc độ cực nhanh."),
        ("Độ tin cậy đối soát", "100% dòng được giải trình", "Khớp số dòng giữa nguồn, raw và fact, minh bạch 100%."),
        ("Chỉ số Holdout Test AUC", "0.741+", "Đo trên tập dữ liệu kiểm thử độc lập theo thời gian."),
        ("Chỉ số Lift @ 10%", "2.37x", "Bắt trúng chuyến trễ trong top 10% rủi ro cao gấp 2.37 lần ngẫu nhiên."),
        ("Báo cáo Power BI", "4 Trang chuẩn Gartner (50+ DAX)", "Đầy đủ 4 cấp độ phân tích với mô hình dữ liệu Star Schema."),
        ("Kiểm thử tự động", "115 / 115 tests PASS (100%)", "Kiểm thử toàn diện từ Ingestion, dbt, API đến các quy tắc nghiệp vụ.")
    ]

    for idx, (m_name, m_val, m_desc) in enumerate(metrics_data):
        row = tbl_metrics.rows[idx + 1]
        row.cells[0].width = Inches(2.0)
        row.cells[1].width = Inches(2.0)
        row.cells[2].width = Inches(2.5)
        bg = GRAY_BG if idx % 2 == 1 else "FFFFFF"
        for i_c, val in enumerate([m_name, m_val, m_desc]):
            c = row.cells[i_c]
            set_cell_background(c, bg)
            set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = DARK
            if i_c == 0:
                r.font.bold = True
                r.font.color.rgb = NAVY
            elif i_c == 1:
                r.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 5. HƯỚNG DẪN VẬN HÀNH
    add_sec_heading("5. HƯỚNG DẪN VẬN HÀNH DỰ ÁN TỪNG BƯỚC (STEP-BY-STEP GUIDE)")
    add_body_p(
        "Khi cần chạy lại dự án hoặc chuẩn bị máy để demo, bạn chỉ cần thực hiện lần lượt các bước sau:"
    )
    add_body_p("Bước 1: Kích hoạt môi trường ảo Python", bold_prefix="1. Môi trường: ")
    add_body_p(
        "Mở terminal tại thư mục dự án và chạy:\n"
        "  .venv\\Scripts\\activate   (trên Windows)\n"
        "  pip install -r requirements.txt"
    )
    add_body_p("Bước 2: Chạy toàn bộ luồng dữ liệu tự động", bold_prefix="2. Chạy Pipeline: ")
    add_body_p(
        "Chỉ cần 1 lệnh duy nhất để chạy từ nạp dữ liệu đến dbt, đối soát và huấn luyện mô hình:\n"
        "  python -m orchestration.run_pipeline"
    )
    add_body_p("Bước 3: Mở Giao diện Điều phối Vận hành (OCC Console)", bold_prefix="3. Khởi động Console: ")
    add_body_p(
        "Nhấp đúp vào file START_SKYOPS.bat hoặc chạy lệnh:\n"
        "  python -m uvicorn ml.api:app --reload --host 0.0.0.0 --port 8000\n"
        "Mở trình duyệt tại: http://localhost:8000"
    )
    add_body_p("Bước 4: Mở và Tương tác Dashboard Power BI", bold_prefix="4. Báo cáo Power BI: ")
    add_body_p(
        "Mở file dashboards/powerbi/Dashboard.pbix bằng Power BI Desktop. "
        "Bấm nút Refresh trên thanh Home để nạp các file Parquet mới nhất từ dashboards/powerbi/export/."
    )
    add_body_p("Bước 5: Chạy bộ kiểm thử tự động xác nhận hệ thống", bold_prefix="5. Kiểm thử hệ thống: ")
    add_body_p(
        "Chạy lệnh sau để chứng minh 100% test case hoạt động hoàn hảo:\n"
        "  pytest -q   (Kết quả: 115 passed)"
    )

    # 6. PHỎNG VẤN & BẢO VỆ
    add_sec_heading("6. BỘ PHỎNG VẤN & BẢO VỆ ĐỒ ÁN (INTERVIEW & DEFENSE CHEATSHEET)")
    add_body_p(
        "Dưới đây là 7 câu hỏi phỏng vấn thực tế và câu trả lời mẫu xuất sắc giúp bạn ghi điểm tuyệt đối trước nhà tuyển dụng hoặc hội đồng chấm thi:"
    )

    qa_list = [
        ("Câu hỏi 1: Giới thiệu tổng quan về dự án này?",
         "Dạ, đây là dự án Airline Data Platform & Operations Analytics mà em xây dựng nhằm giải quyết bài toán tối ưu hóa vận hành và giảm thiểu tổn thất trễ chuyến bay trong ngành hàng không. Dự án xử lý bộ dữ liệu thực tế hơn 3.45 triệu chuyến bay của Cục Thống kê Vận tải Hoa Kỳ (US DOT BTS). Em tham gia xây dựng giải pháp từ khâu làm sạch, kiểm định chất lượng dữ liệu với Great Expectations, mô hình hóa dữ liệu dạng Kimball Star Schema qua dbt, phân tích nguyên nhân gốc rễ và đánh giá mô hình học máy dự báo trễ, cho đến việc trực tiếp thiết kế hệ thống báo cáo quản trị Power BI 4 trang đạt chuẩn Gartner và console điều phối vận hành thời gian thực."),

        ("Câu hỏi 2: Bạn đóng vai trò gì và chịu trách nhiệm phần nào trong dự án?",
         "Dạ, vai trò chính của em trong dự án là Data Analyst. Trách nhiệm cốt lõi của em bao gồm: (1) Đọc hiểu và phân tích sâu dữ liệu thô (Data Profiling), phát hiện 9 vấn đề chất lượng dữ liệu như các giá trị ngoại lai -9999, dữ liệu trùng lặp và chuyến bay chuyển sân để đưa ra giải pháp xử lý; (2) Tham gia thiết kế các bảng chiều và bảng sự kiện trong mô hình dbt để phục vụ đúng các góc nhìn phân tích; (3) Đánh giá chất lượng các mô hình học máy (ML Tournament) dựa trên các chỉ số AUC, Brier Score và Lift@10%; (4) Trực tiếp thiết kế và viết toàn bộ hơn 50 công thức DAX cho Dashboard Power BI 4 trang, dẫn dắt người xem từ bức tranh toàn cảnh đến chi tiết căn nguyên và dự báo rủi ro pháp lý."),

        ("Câu hỏi 3: Tại sao bạn lại chọn kiến trúc Kimball Star Schema thay vì để 1 bảng phẳng duy nhất (One Big Table - OBT)?",
         "Dạ, với quy mô hơn 3.45 triệu dòng dữ liệu bay, nếu để một bảng phẳng lớn duy nhất (OBT): dung lượng lưu trữ sẽ phình to gấp nhiều lần do lặp lại các thuộc tính của sân bay và hãng hàng không trên từng dòng chuyến bay; đồng thời khi dữ liệu sân bay có sự thay đổi, ta sẽ gặp rủi ro bất nhất quán dữ liệu (Update Anomaly). Bằng cách tách thành Star Schema với bảng sự kiện trung tâm fact_flights và các bảng chiều dim_airport, dim_airline, dim_date, dim_aircraft, mô hình giúp Power BI tận dụng tối đa cơ chế VertiPaq nén dữ liệu theo cột, tăng tốc độ lọc chéo giữa các visual lên gấp nhiều lần và giúp mô hình mở rộng rất linh hoạt."),

        ("Câu hỏi 4: Những phát hiện kinh doanh (Business Insights) quan trọng nhất bạn tìm ra là gì?",
         "Dạ, qua quá trình phân tích chẩn đoán, em rút ra 3 phát hiện kinh doanh then chốt: (1) Hiệu ứng Domino chiếm tỷ trọng lớn nhất: Trễ dây chuyền từ máy bay quay đầu (Late Aircraft Delay) chiếm tới gần 40% tổng số phút trễ của toàn mạng bay. Một chuyến bay trễ vào buổi sáng tại Hub sẽ gây trễ lan truyền cho 3-4 chuyến bay tiếp theo của tàu bay đó trong ngày; (2) Nút thắt đường lăn giờ cao điểm (Taxi-out Bottleneck): Tại các sân bay Hub lớn như ORD, DFW, JFK, vào khung giờ 17h–20h, thời gian máy bay lăn ra đường băng tăng vọt lên 35–48 phút do tắc nghẽn mặt đất, đẩy chi phí đốt nhiên liệu phụ trội tăng vọt; (3) Rủi ro chế tài pháp lý Tarmac Delay: Các chuyến bay có thời gian lăn quá dài vào buổi tối đối mặt nguy cơ kẹt quá 180 phút. Mức phạt theo luật 14 CFR § 259.4 lên tới $37.377 USD/hành khách, lớn hơn gấp hàng trăm lần so với chi phí trễ thông thường."),

        ("Câu hỏi 5: Bạn giải quyết vấn đề chất lượng dữ liệu như thế nào?",
         "Dạ, em tiếp cận chất lượng dữ liệu theo tư duy Data Governance chủ động: Ở tầng nạp thô, em thiết lập các bộ kiểm tra tự động với Great Expectations để chặn đứng dữ liệu sai schema, null ở các trường bắt buộc, hoặc cự ly bay âm. Sau đó, em xây dựng một module Đối soát dữ liệu (Reconciliation) chạy tự động sau mỗi lần nạp để so khớp số lượng dòng giữa nguồn gốc, bảng raw và bảng fact. Kết quả là 100% dòng dữ liệu được giải trình minh bạch, phát hiện đúng 3 dòng trùng lặp thực tế từ nguồn BTS để xử lý."),

        ("Câu hỏi 6: Tại sao lại cần so sánh 5 mô hình Machine Learning và bạn đánh giá chúng ra sao?",
         "Dạ, trong thực tế không có một mô hình nào luôn luôn tối ưu cho mọi bài toán (No Free Lunch theorem). Do đó, dự án tổ chức một Đấu trường Đa Mô hình (Tournament) gồm Logistic Regression (Baseline), LightGBM, CatBoost, XGBoost và Soft-Voting Ensemble. Đặc biệt, dưới góc độ phân tích kinh doanh, em không chỉ nhìn vào Accuracy đơn thuần (vì dữ liệu trễ chuyến bị mất cân bằng lớp - Imbalanced Data), mà em đánh giá dựa trên: (1) Holdout Test AUC: Đo khả năng phân biệt tổng quát, đạt mức 0.741+; (2) Lift @ 10%: Đạt 2.37x, chứng minh mô hình giúp trung tâm điều phối tập trung nguồn lực rà soát top 10% chuyến bay rủi ro nhất với hiệu quả bắt trúng gấp hơn 2 lần so với rà soát ngẫu nhiên; (3) Brier Score: Đảm bảo xác suất dự báo được chuẩn hóa chính xác để tính toán tổn thất tài chính kỳ vọng."),

        ("Câu hỏi 7: Thách thức lớn nhất bạn đã vượt qua trong dự án này là gì?",
         "Dạ, thách thức lớn nhất là xử lý khối lượng dữ liệu lớn 3.45 triệu dòng một cách mượt mà trên môi trường máy cá nhân mà không làm tràn RAM. Để vượt qua thách thức này, em đã áp dụng phương pháp: Dùng cơ chế ELT (Python chỉ làm nhiệm vụ nạp thô, toàn bộ việc tính toán biến đổi phức tạp được đẩy trực tiếp vào kho dữ liệu qua các truy vấn SQL tối ưu của dbt); và Xuất các bảng Marts sang định dạng Apache Parquet cột nén cao để nạp vào Power BI thay vì dùng file CSV cồng kềnh, giúp file báo cáo Power BI chỉ nặng hơn 5MB nhưng phản hồi cực kỳ nhanh nhạy.")
    ]

    for q, a in qa_list:
        add_body_p(q, bold_prefix="Q: ")
        add_body_p(a, bold_prefix="A: ")
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Save document
    doc.save(str(DOCX_PATH))
    print(f"Document successfully created at: {DOCX_PATH.resolve()}")

if __name__ == "__main__":
    create_report()
