# 📘 CẨM NANG HƯỚNG DẪN SỬ DỤNG & VẬN HÀNH NỀN TẢNG
# AIRLINE DATA PLATFORM & SKYOPS COPILOT™

---

## 📑 MỤC LỤC
1. [Giới Thiệu Tổng Quan](#1-giới-thiệu-tổng-quan)
2. [Cài Đặt & Khởi Động Nhanh](#2-cài-đặt--khởi-động-nhanh)
3. [Cẩm Nang Điều Phái Bay & Tác Nghiệp (SkyOps OCC Cockpit)](#3-cẩm-nang-điều-phái-bay--tác-nghiệp-skyops-occ-cockpit)
   - 3.1. Tra cứu & Giám sát Chuyến bay
   - 3.2. Bóc tách Thiệt hại Tài chính FAA $101.18/phút & Rủi ro Pháp lý
   - 3.3. Mô phỏng Phương án Cứu nguy What-If
   - 3.4. Trợ lý Tác nghiệp Copilot (Chat, Voice 🎙️, Prompt Chips)
   - 3.5. Xuất Slide Trình chiếu PowerPoint (.pptx 16:9) & Biên bản Kiểm toán PDF
4. [Cẩm Nang Phân Tích Dữ Liệu & Báo Cáo Power BI](#4-cẩm-nang-phân-tích-dữ-liệu--báo-cáo-power-bi)
   - 4.1. Mạch dẫn chuyện 4 Trang chuẩn Gartner
   - 4.2. Khung Chat Nhúng Siêu Gọn `/embed/chat` trên Power BI
   - 4.3. Từ điển Chỉ số & Công thức DAX
5. [Cẩm Nang Kỹ Thuật & Quản Trị Hệ Thống (Data Engineer & MLOps)](#5-cẩm-nang-kỹ-thuật--quản-trị-hệ-thống-data-engineer--mlops)
   - 5.1. Vận hành Pipeline Toàn trình (ELT & Reconciliation)
   - 5.2. Chuyển đổi Kho Dữ liệu (DuckDB ↔ PostgreSQL ↔ Snowflake)
   - 5.3. Huấn luyện Đấu trường Đa Mô hình ML (Tournament)
   - 5.4. Cấu hình Cổng LLM Đa Nhà Cung Cấp (Online & Offline)
   - 5.5. Kiểm thử Tự động (Automated Test Suite)
6. [Xử Lý Sự Cố Thường Gặp (Troubleshooting & FAQs)](#6-xử-lý-sự-cố-thường-gặp-troubleshooting--faqs)

---

## 1. GIỚI THIỆU TỔNG QUAN

**Airline Data Platform & SkyOps Copilot™** là nền tảng kỹ thuật dữ liệu và trợ lý trí tuệ nhân tạo cấp độ Doanh nghiệp (Enterprise Data & AI Platform) dành cho ngành hàng không thương mại:
- **Xử lý dữ liệu quy mô lớn**: Hỗ trợ từ tập dữ liệu giả lập (synthetic) đến **3.453.795 chuyến bay thực tế** của Cục Thống kê Vận tải Hoa Kỳ (US DOT BTS).
- **Kiến trúc kho dữ liệu linh hoạt (Tri-Warehouse Architecture)**: Hỗ trợ chuyển đổi liền mạch giữa **PostgreSQL** (`airline_dwh`), tệp nhúng nội bộ siêu tốc **DuckDB** và kho dữ liệu đám mây **Snowflake**.
- **Chất lượng dữ liệu & Mô hình hóa**: Hợp đồng dữ liệu Great Expectations, mô hình hóa Kimball Star Schema qua dbt (56 models & tests xanh 100%), đối soát dòng 100% minh bạch.
- **Đấu trường Đa Mô hình Học Máy (ML Tournament)**: 5 thuật toán so tài (Logistic Regression, LightGBM, CatBoost, XGBoost, Soft-Voting Ensemble) với cơ chế Temporal Split chống rò rỉ dữ liệu.
- **Thẩm định Pháp lý & Chế tài Quản lý Nhà nước**: Neo chặt phán quyết vào 14 CFR § 259.4 (Tarmac Delay), FAR Part 117 (Giới hạn FDP), 14 CFR § 260.6 (Hoàn tiền mặt tự động), và Thông tư 19/2023/TT-BGTVT của Việt Nam.
- **Trợ lý Vận hành & Phân tích SkyOps Copilot™**: Giao diện OCC Cockpit tương tác thời gian thực, mô phỏng What-If, xuất slide PowerPoint 1 chạm, nhận diện giọng nói Web Speech API và khung chat nhúng tối ưu cho Power BI.

---

## 2. CÀI ĐẶT & KHỞI ĐỘNG NHANH

### 2.1. Yêu cầu Hệ thống
- **Hệ điều hành**: Windows 10/11, macOS hoặc Linux.
- **Python**: Phiên bản 3.10 trở lên.
- **RAM**: Tối thiểu 4 GB (khuyến nghị 8 GB trở lên khi chạy toàn bộ tập dữ liệu BTS).
- **Trình duyệt**: Google Chrome hoặc Microsoft Edge (để hỗ trợ tính năng Web Speech API giọng nói).

### 2.2. Cài đặt Môi trường
```bash
# 1. Clone mã nguồn về máy
git clone https://github.com/battina1999/airline-data-platform.git
cd airline-data-platform

# 2. Tạo và kích hoạt môi trường ảo Python
python -m venv .venv
# Trên Windows:
.venv\Scripts\activate
# Trên macOS / Linux:
source .venv/bin/activate

# 3. Cài đặt các gói phụ thuộc
pip install -r requirements.txt
```

### 2.3. Khởi động Nền tảng
- **Cách 1: Khởi động 1 chạm trên Windows (Khuyến nghị)**
  Nhấp đúp chuột vào tệp [`START_SKYOPS.bat`](file:///c:/airline-data-platform/START_SKYOPS.bat). Hệ thống sẽ tự động khởi động máy chủ FastAPI và mở trình duyệt tại `http://skyops.local:8000` (hoặc `http://localhost:8000`).
- **Cách 2: Khởi động qua dòng lệnh**
  ```bash
  python -m uvicorn ml.api:app --reload --host 0.0.0.0 --port 8000
  # hoặc dùng lệnh make:
  make skyops
  ```
- **Cách 3: Khởi động Streamlit Analytics Dashboard**
  ```bash
  make dashboard
  # Mở tại http://localhost:8501
  ```

---

## 3. CẨM NANG ĐIỀU PHÁI BAY & TÁC NGHIỆP (SKYOPS OCC COCKPIT)

Truy cập giao diện chính tại `http://localhost:8000` (hoặc `http://skyops.local:8000`). Giao diện được thiết kế theo bố cục **Split-Screen OCC Cockpit** chuẩn phòng điều hành bay hiện đại.

### 3.1. Tra cứu & Giám sát Chuyến bay
1. **Tìm kiếm nhanh theo ID**: Nhập số hiệu định danh chuyến bay vào ô `Mã chuyến bay` (ví dụ: `4568`, `48339`, `25413`, `8626`, `2619`) và bấm **"Tra cứu"**.
2. **Khắc phục lỗi tự động (Self-Healing)**: Nếu nhập sai mã hoặc chuyến bay không tồn tại, hệ thống không bật thông báo lỗi gián đoạn mà hiển thị ngay dải chip chuyến bay mẫu thực tế để nhấp chọn tức thì.
3. **Thẻ Hero Boarding Pass HUD**: Hiển thị trực quan chặng bay (ví dụ: `LAS ➔ BOS`), hãng hàng không, số hiệu chuyến bay, cự ly, xác suất trễ dự báo và phân nhóm rủi ro (Normal, Elevated, High).

### 3.2. Bóc tách Thiệt hại Tài chính FAA $101.18/phút & Rủi ro Pháp lý
- **Dải 4 thẻ tài chính định lượng**:
  - `Chi phí trễ cơ sở`: Tính theo định mức chính thức của FAA/A4A: `$101.18 USD / phút trễ`.
  - `Rủi ro phạt Tarmac`: Căn cứ theo **14 CFR § 259.4**, mức phạt lên tới **$37.377 USD / hành khách** nếu tàu bay kẹt trên đường lăn quá 180 phút (nội địa) mà không cho khách rời tàu.
  - `Bồi hoàn tiền mặt`: Căn cứ theo **14 CFR § 260.6**, bắt buộc hoàn 100% tiền mặt tự động (ước tính $275 USD/khách) khi trễ từ 3 tiếng trở lên.
  - `Tổng tổn thất tiềm tàng`: Tổng hợp toàn bộ rủi ro tài chính của chuyến bay.
- **Thanh tiến trình xếp chồng (Stacked Progress Bar)**: Trực quan hóa tỷ trọng giữa chi phí trễ thông thường và các chế tài xử phạt hành chính khổng lồ, nhấn mạnh tính cấp bách trong xử lý.

### 3.3. Mô phỏng Phương án Cứu nguy What-If
Khu vực Console bên cột trái cung cấp 4 phương án can thiệp chiến lược:
1. **Đổi giờ cất cánh (Reschedule Departure Hour)**: Lùi giờ bay sang khung giờ thấp điểm để tránh nghẽn đường lăn và sóng cất cánh dồn dập tại sân bay Hub.
2. **Kích hoạt Tổ bay Dự phòng (Activate Standby Crew)**: Triệt tiêu nguy cơ vi phạm giờ bay FAR Part 117 khi tổ bay chính sắp chạm ngưỡng Duty Period.
3. **Tăng tốc bay bù giờ (Airborne Speedup via Cost Index)**: Tận dụng biên độ bù giờ trên đường bay (Airborne Make-up Time).
4. **Đổi tàu bay dự bị (Tail Swap - Spare Aircraft)**: Thay thế tàu bay gặp cảnh báo hỏng kỹ thuật.
> Bấm **"Chạy Mô Phỏng What-If"** để xem ngay: Xác suất trễ mới, Rủi ro pháp lý sau can thiệp và **Số tiền tiết kiệm ròng (Net Cost Savings)**.

### 3.4. Trợ lý Tác nghiệp Copilot (Chat, Voice 🎙️, Prompt Chips)
Chuyển sang **Tab 2 (Trợ Lý Phân Tích Nghiệp Vụ)**:
- **Tương tác đa dạng**:
  - *Nhập văn bản*: Đặt bất kỳ câu hỏi nào bằng tiếng Việt hoặc tiếng Anh.
  - *Ra lệnh bằng giọng nói*: Nhấp vào biểu tượng micro `🎙️`, nói câu lệnh (ví dụ: *"Phân tích chuyến bay 4568"* hoặc *"Chuyến bay này có nguy cơ vi phạm Tarmac Delay không"*), hệ thống tự động nhận diện và gửi lệnh.
  - *Starter Chips gợi ý*: Bấm vào các chip câu hỏi sẵn có để tra cứu nhanh.
- **Trích xuất mã hiệu chuyến bay tự động (NLP Entity Extraction)**: Khi bạn nói hoặc gõ câu hỏi có chứa số hiệu chuyến bay, Copilot sẽ tự động tra cứu hồ sơ và kích hoạt chẩn đoán chuyên sâu mà không cần thao tác thủ công.
- **Hiệu ứng Typewriter Streaming**: Phản hồi được truyền mượt mà theo nhịp thời gian thực kèm trích dẫn điều luật (`⚖️ 14 CFR § 259.4`, `FAR Part 117`) và chip câu hỏi tiếp nối.
- **Thẻ lịch sử co giãn (Collapsible Accordion History)**: Khi làm mới trang, lịch sử hội thoại được khôi phục thành các thẻ co giãn gọn gàng; bấm vào thẻ để mở bung câu trả lời mà không làm trôi màn hình.

### 3.5. Xuất Slide Trình chiếu PowerPoint (.pptx 16:9) & Biên bản Kiểm toán PDF
- **Xuất Slide Insight Ban Điều Hành**:
  1. Nhấp nút **"📊 Xuất Slide Insight (PowerPoint / Trình Chiếu)"** trên thẻ Boarding Pass.
  2. Cửa sổ Modal hiển thị bản xem trước 16:9 phong cách Clean Executive Light Theme.
  3. Bấm **"📥 Tải PowerPoint (.pptx)"** để nhận ngay tệp trình chiếu Microsoft PowerPoint chính thức sẵn sàng báo cáo cuộc họp.
  4. Hoặc bấm **"🌐 Trình Chiếu F11"** để mở slide deck tương tác toàn màn hình.
- **Xuất Biên bản Kiểm toán Tác nghiệp (OCC Chat Audit Log)**:
  1. Nhấp nút **"📥 Xuất Biên Bản Hội Thoại (Audit Log)"** trên thanh công cụ chat.
  2. Chọn **"🖨️ In / Xuất Hồ Sơ PDF (FAA Compliance)"** để xuất tài liệu kiểm toán có đầy đủ mốc thời gian, khuyến nghị và khung chữ ký xác nhận của Trực ban OCC / Chuyên viên Phân tích.

---

## 4. CẨM NANG PHÂN TÍCH DỮ LIỆU & BÁO CÁO POWER BI

Tệp báo cáo chính thức nằm tại: [`dashboards/powerbi/Dashboard.pbix`](file:///c:/airline-data-platform/dashboards/powerbi/Dashboard.pbix).

### 4.1. Mạch Dẫn Chuyện 4 Trang Chuẩn Gartner
Báo cáo được cấu trúc chặt chẽ theo thang đo độ trưởng thành phân tích dữ liệu (Analytics Maturity Curve):
1. **Trang 1: Executive Operations Overview (Phân tích Mô tả - Descriptive)**
   - *Câu hỏi trả lời*: Tình hình vận hành tổng thể đang diễn ra như thế nào?
   - *Trọng tâm*: Tỷ lệ đúng giờ OTP (chuẩn A14), Tỷ lệ hủy chuyến, và Tổng thiệt hại trễ chuyến trực tiếp theo định mức FAA $101.18/phút.
2. **Trang 2: Delay Root-Cause & Cascading Analysis (Phân tích Chẩn đoán - Diagnostic)**
   - *Câu hỏi trả lời*: Tại sao các chuyến bay lại bị trễ?
   - *Trọng tâm*: Bóc tách 5 nguyên nhân theo chuẩn BTS. Phân tích hiện tượng Domino Late Aircraft chiếm tới gần 40% nguyên nhân trễ lan truyền.
3. **Trang 3: Hub Bottlenecks & Route Performance (Chẩn đoán Chuyên sâu - Bottleneck Deep-Dive)**
   - *Câu hỏi trả lời*: Điểm nghẽn nằm ở đâu và vào khung giờ nào?
   - *Trọng tâm*: Sóng kết nối tại các siêu sân bay Hub (DFW, ORD, ATL, DEN), hiện tượng dồn toa lăn bánh (Taxi-out 35-48 phút) và nguy cơ chạm giờ giới nghiêm tiếng ồn đêm (Night Curfew tại SNA, LGA, DCA).
4. **Trang 4: AI Predictive Risk & Aviation Regulatory Governance (Dự đoán & Phán quyết - Predictive & Prescriptive)**
   - *Câu hỏi trả lời*: Chuyến bay nào sắp tới có rủi ro trễ, đe dọa vi phạm điều luật nào và điều độ phải làm gì?
   - *Trọng tâm*: Điểm số rủi ro trễ từ Đấu trường mô hình ML, rủi ro phạt Tarmac 14 CFR § 259.4, FAR Part 117 và bảng điều hành tác nghiệp khép kín.
   - *Điểm đánh giá*: Đã qua kiểm toán metadata PBIR đạt điểm tuyệt đối **10/10 Enterprise BI**.

### 4.2. Khung Chat Nhúng Siêu Gọn `/embed/chat` trên Power BI
- **Truy cập**: `http://localhost:8000/embed/chat?page=1`
- **Tích hợp vào Power BI Desktop**:
  1. Gắn nút bấm **Action Button** trên Header của từng trang trong Power BI.
  2. Trong phần Format Button: Chọn `Action` $\to$ `Type: Web URL` $\to$ Bấm vào nút `fx` và chọn DAX Measure tương ứng (`[AI Copilot Header URL - Page 1]`, `Page 2`, `Page 3`, `Page 4` hoặc `[AI Copilot Universal Header URL]`).
  3. Khi click nút trên Power BI, trình duyệt sẽ mở ngay khung chat nhúng với ngữ cảnh phân tích chính xác của trang và các bộ lọc đang chọn!
- **Tính năng độc quyền trong khung nhúng**:
  - Thanh chuyển trang nhanh `[P1] [P2] [P3] [P4]` ở header.
  - Dải starter chips thay đổi linh hoạt theo nghiệp vụ của trang đang xem.
  - Lưu trữ hội thoại bền vững (Dual Storage): Không bị mất dữ liệu khi vô tình đóng tab.

### 4.3. Từ điển Chỉ số & Công thức DAX
Chuyển sang **Tab 3 (Từ Điển Chỉ Số & Quy Chuẩn)** trên giao diện Web để tra cứu:
- 18 thuật ngữ vận hành hàng không (FDP, Tarmac Delay, Block Time, Taxi-Out,...).
- 14 chỉ số thống kê & Machine Learning (AUC, Lift @ 10%, Brier Score, Threshold, SHAP,...).
- Toàn văn 8 quy trình thao tác chuẩn SOP tác nghiệp.
- Cú pháp và ý nghĩa kinh doanh của toàn bộ các thước đo DAX cốt lõi (`measures.dax`).

---

## 5. CẨM NANG KỸ THUẬT & QUẢN TRỊ HỆ THỐNG (DATA ENGINEER & MLOPS)

### 5.1. Vận hành Pipeline Toàn trình (ELT & Reconciliation)
Để chạy toàn bộ chu trình xử lý dữ liệu từ đầu đến cuối:
```bash
# 1. Sinh dữ liệu giả lập (nếu cần)
python -m data.generate_data

# 2. Nạp dữ liệu thô vào warehouse kèm audit log
python -m ingestion.run_ingestion

# 3. Kiểm định hợp đồng dữ liệu Great Expectations
python -m quality.validate

# 4. Xây dựng và kiểm thử mô hình dbt (staging -> dims/facts -> marts)
cd dbt/airline_dwh && dbt build --profiles-dir . && cd ../..

# 5. Đối soát số liệu nguồn - đích (Reconciliation 100% dòng)
python -m quality.reconciliation

# HOẶC CHẠY 1 LỆNH DUY NHẤT:
python -m orchestration.run_pipeline
# hoặc:
make pipeline
```

### 5.2. Chuyển đổi Kho Dữ liệu (DuckDB ↔ PostgreSQL ↔ Snowflake)
Cấu hình kho dữ liệu thông qua tệp `.env` hoặc biến môi trường:
- **Chạy trên DuckDB (Mặc định - Local Embedded)**:
  ```env
  WAREHOUSE=duckdb
  DUCKDB_PATH=warehouse/airline.duckdb
  ```
- **Chạy trên PostgreSQL (Database: `airline_dwh`)**:
  ```env
  WAREHOUSE=postgres
  POSTGRES_HOST=localhost
  POSTGRES_PORT=5432
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=your_password
  POSTGRES_DB=airline_dwh
  ```
- **Chạy trên Snowflake (Cloud Warehouse)**:
  ```env
  WAREHOUSE=snowflake
  SNOWFLAKE_ACCOUNT=your_account.region
  SNOWFLAKE_USER=your_user
  SNOWFLAKE_PASSWORD=your_password
  SNOWFLAKE_DATABASE=AIRLINE_DWH
  ```

### 5.3. Huấn luyện Đấu trường Đa Mô hình ML (Tournament)
Để chạy lại quá trình huấn luyện 5 mô hình ML so tài trên dữ liệu mới:
```bash
python ml/train.py --model tournament
# hoặc:
make train
```
Tiến trình sẽ tự động:
1. Nạp dữ liệu từ warehouse (Postgres hoặc DuckDB).
2. Tách chuỗi thời gian không rò rỉ (Temporal Train/Val/Test Split).
3. Huấn luyện 5 thuật toán: Logistic Regression, LightGBM, CatBoost, XGBoost, Soft-Voting Ensemble.
4. Đánh giá AUC, Lift @ 10%, Brier Score và tự động lưu mô hình chiến thắng vào `ml/artifacts/best_delay_model.joblib`.
5. Cập nhật các bảng tra cứu Parquet và xuất biểu đồ `docs/img/ml_feature_importance.png`.

### 5.4. Cấu hình Cổng LLM Đa Nhà Cung Cấp (Online & Offline)
Hệ thống hỗ trợ 2 phương thức cấu hình khóa API cho Copilot:
1. **Cách 1: Nhập trực tiếp trên Web (Khuyến nghị cho Người dùng)**:
   - Bấm vào nút `⚙️ Cài Đặt LLM Key` trên góc phải giao diện Web.
   - Nhập khóa API của nhà cung cấp bạn có (Google Gemini, Anthropic Claude, OpenAI, DeepSeek).
   - Bấm **"Kiểm tra kết nối (Ping Test)"** để xác thực, sau đó bấm **"Lưu cấu hình"**. Khóa được lưu an toàn trong `localStorage` của trình duyệt.
2. **Cách 2: Cấu hình qua biến môi trường (Cho Máy chủ)**:
   - Thêm vào file `.env`:
     ```env
     GEMINI_API_KEY=your_key
     ANTHROPIC_API_KEY=your_key
     OPENAI_API_KEY=your_key
     DEEPSEEK_API_KEY=your_key
     ```
> **Lưu ý quan trọng**: Nếu không có bất kỳ API Key nào hoặc mất kết nối mạng, hệ thống **tự động kích hoạt Động cơ Offline Grounding 40 đề mục**, đảm bảo hệ thống phản hồi 100% thời gian thực, không bao giờ bị gián đoạn hay phụ thuộc bên thứ ba!

### 5.5. Kiểm thử Tự động (Automated Test Suite)
Chạy toàn bộ 115 unit test cases:
```bash
python run_tests.py
# hoặc:
pytest -v
```
*(Kết quả yêu cầu: 115 passed 100% xanh).*

---

## 6. XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING & FAQS)

### Q1: Bị lỗi `Address already in use` hoặc không khởi động được port 8000?
- **Nguyên nhân**: Đang có một tiến trình uvicorn hoặc dịch vụ khác chạy chiếm port 8000.
- **Khắc phục**:
  - Mở PowerShell và kiểm tra: `Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force`
  - Hoặc đổi sang chạy cổng khác: `python -m uvicorn ml.api:app --port 8080`

### Q2: Tính năng nhận diện giọng nói (Micro 🎙️) báo lỗi không hoạt động?
- **Nguyên nhân**: Trình duyệt chưa được cấp quyền micro hoặc truy cập qua giao thức không bảo mật trên mạng LAN.
- **Khắc phục**:
  - Nhấp vào biểu tượng ổ khóa/cài đặt cạnh thanh địa chỉ trình duyệt `http://localhost:8000`, bật quyền `Microphone` thành `Allow`.
  - Khuyến nghị sử dụng trình duyệt Google Chrome hoặc Microsoft Edge phiên bản mới.

### Q3: Bị lỗi DuckDB file locked (`Resource temporarily unavailable`)?
- **Nguyên nhân**: DuckDB chỉ cho phép 1 tiến trình ghi tại một thời điểm. Nếu pipeline đang chạy ingestion hoặc dbt build mà Streamlit cũng kết nối ghi, file sẽ bị khóa.
- **Khắc phục**: Khi kết nối đọc từ dashboard hoặc script phân tích, luôn truyền tham số `read_only=True` vào hàm kết nối (`duckdb.connect(..., read_only=True)`).

### Q4: Power BI không tải được dữ liệu từ Parquet?
- **Khắc phục**: Chạy lệnh `make export-powerbi` (hoặc `python scripts/export_marts.py` và `python scripts/export_ml_powerbi.py`) để làm mới toàn bộ các tệp `.parquet` trong thư mục `dashboards/powerbi/export/`.

---

*Tài liệu được phát hành và kiểm định bởi Đội ngũ Kỹ sư Dữ liệu Nền tảng Hàng Không (Airline Data Platform Team).*
