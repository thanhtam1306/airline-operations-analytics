# BÁO CÁO POWER BI TRANG 4: AI PREDICTIVE RISK & AVIATION REGULATORY GOVERNANCE
## (DỰ BÁO RỦI RO BẰNG MÁY HỌC & QUẢN TRỊ TUÂN THỦ PHÁP LUẬT HÀNG KHÔNG)

---

## 1. MẠCH KỂ CHUYỆN LIỀN MẠCH XUYÊN SUỐT 4 TRANG (THE 4-STAGE ANALYTICS STORYLINE)

Để báo cáo đạt chuẩn Enterprise BI cao cấp, Trang 4 được thiết kế như là **đỉnh cao logic (climax)** của toàn bộ chuỗi phân tích 4 giai đoạn theo khung kiến trúc kinh điển của Gartner:

```
┌─────────────────────────┐       ┌─────────────────────────┐
│ TRANG 1: DESCRIPTIVE    │  ───> │ TRANG 2: DIAGNOSTIC     │
│ Chuyện gì đã xảy ra?    │       │ Tại sao lại trễ?        │
│ OTP, Hủy chuyến, Min TB │       │ 5 nguyên nhân DOT &     │
│ Benchmark ngành (< 80%) │       │ Domino quay đầu tàu bay │
└─────────────────────────┘       └─────────────────────────┘
             │                                 │
             ▼                                 ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│ TRANG 3: DIAGNOSTIC DEEP│  ───> │ TRANG 4: PREDICTIVE &   │
│ Nghẽn ở đâu & chặng nào?│       │ PRESCRIPTIVE GOVERNANCE │
│ Mega Hub DFW, ORD, ATL  │       │ AI dự báo chuyến nào trễ│
│ Giờ cao điểm chiều tối  │       │ Vi phạm luật gì & OCC ra│
│ Taxi-out tăng vọt       │       │ lệnh hành động cụ thể!  │
└─────────────────────────┘       └─────────────────────────┘
```

### Chi tiết mạch dẫn chuyện (Narrative Flow):
1. **Trang 1 (Executive Operations Overview - Bức tranh tổng quan)**:
   - *Thông điệp*: Tỷ lệ đúng giờ (OTP) toàn mạng bay chỉ dao động ở mức 75% - 78%, không đạt mốc kỳ vọng của ban điều hành (80%). Hàng nghìn chuyến bay bị trễ với số phút trễ trung bình đáng báo động.
   - *Câu hỏi bỏ ngỏ*: *Ai và nguyên nhân gốc rễ nào gây ra sự trễ chuyến diện rộng này?*
2. **Trang 2 (Delay Root-Cause & Cascading Domino - Bóc tách nguyên nhân)**:
   - *Thông điệp*: Phân rã 5 nhóm nguyên nhân theo chuẩn US DOT BTS chỉ ra rằng: Hiệu ứng Domino "Late Aircraft Delay" chiếm tới hơn 35-40% tổng số phút trễ. Đồng thời, có sự phân hóa rõ rệt giữa mô hình Hub-and-Spoke (Legacy Carrier gánh nặng nối chuyến) và Point-to-Point (LCC).
   - *Câu hỏi bỏ ngỏ*: *Các điểm nghẽn vật lý cụ thể nằm ở đâu trong mạng lưới đường bay?*
3. **Trang 3 (Hub Bottlenecks & Route Performance - Định vị không gian điểm nghẽn)**:
   - *Thông điệp*: Định vị chính xác các Mega Hub đầu não (DFW, ORD, ATL, DEN) bị quá tải nghiêm trọng vào khung giờ cao điểm chiều tối (16:00 - 20:00). Mật độ cất cánh dày đặc khiến thời gian lăn bánh ra đường băng (Taxi-out) tăng gấp đôi, làm vỡ lịch trình quay đầu máy bay.
   - *Câu hỏi bỏ ngỏ*: *Khi đã biết quá khứ trễ ở đâu và tại sao, làm thế nào để đi trước một bước: Dự báo chính xác chuyến bay sắp tới bị trễ và ngăn chặn nguy cơ bị phạt hàng chục triệu USD theo luật hàng không?*
4. **Trang 4 (AI Predictive Risk & Aviation Regulatory Governance - Dự báo & Mệnh lệnh điều hành)**:
   - *Lời giải đáp*: Tận dụng các đặc trưng đã phát hiện ở Trang 2 (tỷ lệ trễ hãng bay, lịch sử tuyến bay) và Trang 3 (mật độ cất cánh theo giờ tại Hub, cự ly bay) để huấn luyện **Đấu trường Đa mô hình Machine Learning**.
   - *Đột phá nghiệp vụ*: Mô hình AI không đưa ra con số xác suất trơ trọi, mà kích hoạt **Động cơ Pháp lý Hàng không (Regulatory Engine)**: Neo chặt dự báo vào chế tài nhà nước:
     - Chuyến bay nào nguy cơ giam khách trên đường lăn quá 3 tiếng sẽ vi phạm **14 CFR § 259.4 (Tarmac Delay)** bị phạt **$37.377 USD/khách**?
     - Chuyến bay nào ca tối muộn vi phạm trần giờ bay của phi hành đoàn theo **FAR Part 117**?
     - Hãng LCC nào phải kích hoạt hoàn tiền mặt 100% theo **14 CFR § 260.6**?
     - Trung tâm Điều hành Khai thác (OCC/Dispatcher) phải ra **Mệnh lệnh hành động bắt buộc nào NGAY BÂY GIỜ** để triệt tiêu tổn thất tài chính?

---

## 2. KIẾN TRÚC MÔ HÌNH DỮ LIỆU POWER BI (STAR SCHEMA ENHANCEMENT)

Trang 4 bổ sung **2 bảng Parquet mới** vào thư mục `dashboards/powerbi/export/`:

| Tên bảng Parquet | Loại bảng | Số dòng | Nội dung cốt lõi |
|---|---|---|---|
| `fct_flight_regulatory_predictions.parquet` | Fact Table | 58.588 | Dữ liệu chuyến bay kèm xác suất trễ AI, phân nhóm rủi ro (High/Elevated/Normal), mã điều luật vi phạm tiềm tàng (Điều, Khoản, Điểm), số tiền phạt dự kiến và lệnh OCC bắt buộc. |
| `ml_tournament_metrics.parquet` | Dimension / Model Mart | 5 | Bảng xếp hạng 5 mô hình ML trong giải đấu Tournament (Baseline LogReg, LightGBM, XGBoost, CatBoost, Soft-Voting Ensemble) với các chỉ số AUC, Lift, Brier Score. |

### Sơ đồ liên kết thực thể (Star Schema Relationships):
Trong màn hình **Model View** của Power BI Desktop, kéo thả thiết lập các mối quan hệ (1-to-many, Single Direction):

```
┌─────────────────────────────────┐
│     dim_date                    │
│     PK: date_key                │
└─────────────────────────────────┘
                 │ 1
                 │ * (Active)
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│  fct_flight_regulatory_         │                 │     dim_airport                 │
│  predictions                    │ *             1 │     PK: airport_key             │
│  FK: date_key                   ├─────────────────┤  - Active: origin_airport_key   │
│  FK: origin_airport_key         │ (Active/Inact)  │  - Inact:  dest_airport_key     │
│  FK: dest_airport_key           │                 └─────────────────────────────────┘
│  FK: airline_key                │
│  PK: flight_id                  │ *
└─────────────────────────────────┘ │
                                    │ 1
                    ┌─────────────────────────────────┐
                    │     dim_airline                 │
                    │     PK: airline_key             │
                    └─────────────────────────────────┘
```

> [!NOTE]
> Bảng `ml_tournament_metrics` có thể để độc lập làm bảng so sánh Benchmark kỹ thuật hoặc tạo liên kết phục vụ slicer mô hình.

---

## 3. THIẾT KẾ GIAO DIỆN & CẤU TRÚC TRỰC QUAN TRANG 4

Giao diện Trang 4 được chia thành 4 khu vực chức năng trực quan:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  HEADER: AI PREDICTIVE RISK & AVIATION REGULATORY COMPLIANCE DASHBOARD                           │
│  [Story Tracker]: 1. Overview  ──>  2. Root Cause  ──>  3. Hub Bottleneck  ──>  4. AI & Reg (ACTIVE) │
├────────────────────────────────┬────────────────────────────────┬────────────────────────────────┤
│  CARD 1: HIGH RISK FLIGHTS     │  CARD 2: TARMAC VIOLATIONS     │  CARD 3: POTENTIAL PENALTY     │
│  19,333 flights (33.0%)        │  11,260 flights (14 CFR § 259) │  $75.76B Max Exposure (DOT)    │
├────────────────────────────────┴────────────────────────────────┴────────────────────────────────┤
│  SECTION A (Trái): MODEL TOURNAMENT       │  SECTION B (Phải): REGULATORY LIABILITIES BY CARRIER │
│  - Biểu đồ Cột & Đường:                   │  - 100% Stacked Bar Chart:                           │
│    Test AUC & Lift @ 10% của 5 mô hình    │    Phân bổ rủi ro theo Hãng & Chế tài                │
│    (Baseline vs LGBM vs XGB vs CAT vs Ens)│    (Tarmac, Crew Duty, Refund, Rebooking)            │
├───────────────────────────────────────────┴──────────────────────────────────────────────────────┤
│  SECTION C (Giữa): HUB CONGESTION & TARMAC RISK MATRIX (Scatter / Heatmap)                       │
│  - Trục X: Giờ khởi hành (0-23h) | Trục Y: Mật độ sân bay | Bong bóng: Xác suất trễ AI           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  SECTION D (Dưới): OCC LIVE DISPATCHER & COMPLIANCE ACTION MATRIX (Bảng tác nghiệp trực tiếp)   │
│  - Cột: Chuyến bay | Chặng | Giờ bay | AI Prob | Risk Band | Điều luật vi phạm | Mệnh lệnh OCC    │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. CHI TIẾT TỪNG VISUAL TRÊN CANVAS

### 4.1. Dải Thẻ Đo Lường Điều Hành (Executive KPI Cards - Top Row)
- **Card 1: High Risk Flights (AI Alert)**
  - *Measure*: `[High Risk Flights (AI Alert)]` kèm subtitle `[High Risk Flight %]`.
  - *Ý nghĩa*: Số lượng chuyến bay AI nhận diện rơi vào vùng rủi ro trễ nghiêm trọng cần điều hành can thiệp.
  - *Màu sắc*: Đỏ `#E74C3C`.
- **Card 2: Tarmac Delay Risk Count (14 CFR § 259.4)**
  - *Measure*: `[Tarmac Delay Risk Count (14 CFR § 259.4)]`.
  - *Ý nghĩa*: Số chuyến bay tại các Hub đông đúc rơi vào giờ cao điểm, có nguy cơ kẹt quá 3 tiếng trên đường lăn.
  - *Màu sắc*: Đỏ cam `#E67E22`.
- **Card 3: Potential DOT Penalty Exposure ($)**
  - *Measure*: `[Potential DOT Penalty Exposure ($)]`.
  - *Ý nghĩa*: Tổng rủi ro tài chính tối đa nếu hãng để xảy ra vi phạm chế tài Tarmac Delay ($37.377 USD/pax x 180 khách/chuyến).
  - *Conditional Color*: Áp dụng measure `[Penalty Exposure Severity Color]`.
- **Card 4: Tournament Champion Model Performance**
  - *Measure*: `[Tournament Winner Test AUC]` & `[Tournament Winner Lift @ 10%]`.
  - *Ý nghĩa*: Chứng chỉ kỹ thuật bảo chứng độ tin cậy của mô hình phục vụ suy luận.

---

### 4.2. Visual 1: Model Tournament Comparison (Đấu Trường Mô Hình)
- **Loại Visual**: *Line and Clustered Column Chart*.
- **X-axis**: `ml_tournament_metrics[model_name]`.
- **Column y-axis**: `ml_tournament_metrics[test_auc]` (Thước đo phân loại tổng quát).
- **Line y-axis**: `ml_tournament_metrics[test_lift_top10pct]` (Hiệu quả tìm trễ trong Top 10% nguy cơ cao nhất).
- **Tooltips**: `val_auc`, `test_brier_score`, `features_count`.
- **Insight rút ra cho Ban Lãnh đạo**:
  Minh bạch hóa lý do chọn mô hình: Mô hình được lựa chọn dựa trên bài kiểm tra thực nghiệm (Temporal Holdout Test) chứ không thiên vị thuật toán phức tạp.

---

### 4.3. Visual 2: Regulatory Liabilities by Carrier (Phân Bổ Rủi Ro Chế Tài Theo Hãng)
- **Loại Visual**: *100% Stacked Bar Chart* (Biểu đồ thanh xếp chồng 100%).
- **Y-axis**: `dim_airline[carrier_name]` hoặc `carrier_code`.
- **X-axis**:
  - `[Tarmac Delay Risk Count (14 CFR § 259.4)]`
  - `[Crew Time-out Risk Count (FAR Part 117)]`
  - `[Interline Rebooking Mandate Count (14 CFR § 259.5)]`
  - `[Mandatory Refund Risk Count (14 CFR § 260.6)]`
  - `[Chronically Delayed Routes Count (14 CFR § 234.11)]`
- **Insight rút ra cho Ban Lãnh đạo**:
  - **Hãng truyền thống (Legacy - AA, DL, UA)** chịu rủi ro cao nhất ở nhóm **Tarmac Delay** (do tập trung tại các Mega Hub lớn) và **Bảo vệ khách lỡ nối chuyến (14 CFR § 259.5)**.
  - **Hãng giá rẻ (LCC - WN, B6, NK)** chịu rủi ro nặng nề nhất ở nhóm **Nghĩa vụ hoàn tiền mặt 100% (14 CFR § 260.6)** do mô hình bay vòng quay nhanh không có mạng lưới liên danh.

---

### 4.4. Visual 3: Hub Congestion vs Delay Risk Heatmap (Ma Trận Điểm Nghẽn & Rủi Ro)
- **Loại Visual**: *Scatter Chart* hoặc *Matrix Heatmap*.
- **Values / Y-axis**: `fct_flight_regulatory_predictions[delay_probability]`.
- **X-axis**: `fct_flight_regulatory_predictions[dep_hour]`.
- **Legend / Small multiples**: `origin_airport` (Lọc các Hub: ATL, DFW, ORD, DEN).
- **Size**: `fct_flight_regulatory_predictions[max_penalty_exposure_usd]`.
- **Insight**: Khung giờ 17h - 20h tại DFW và ORD là "tâm chấn" của các rủi ro chế tài pháp lý nặng nề nhất.

---

### 4.5. Visual 4: OCC Live Dispatcher Action Matrix (Bảng Tác Nghiệp Thời Gian Thực)
- **Loại Visual**: *Table* hoặc *Matrix*.
- **Các trường dữ liệu hiển thị**:
  1. `flight_number`: Số hiệu chuyến bay.
  2. `carrier_code`: Hãng khai thác.
  3. `route`: Tuyến bay (`origin` ➔ `dest`).
  4. `dep_hour`: Giờ bay dự kiến.
  5. `delay_probability`: Xác suất trễ AI (Định dạng % và bật Data Bars màu đỏ).
  6. `risk_band`: Nhóm rủi ro (Áp dụng Conditional Formatting màu nền bằng `[Risk Band Color]`).
  7. `primary_legal_code`: Căn cứ pháp lý (VD: `14 CFR § 259.4(b)(1)`).
  8. `statutory_penalty_potential_usd`: Mức phạt chế tài tiềm tàng.
  9. `mandatory_occ_action`: **Mệnh lệnh hành động bắt buộc cho Điều phái viên bay** (VD: *GATE HOLD: Giữ máy bay tại cửa, cấm đẩy lùi khi chưa có khe ATC*).
  10. `vietnam_legal_equivalent`: Đối chiếu quy định Việt Nam (Thông tư 19/2023/TT-BGTVT).

---

## 5. BỘ CÔNG THỨC DAX CHUYÊN BIỆT CHO TRANG 4

Toàn bộ các measures dưới đây đã được cập nhật sẵn trong [`dashboards/powerbi/measures.dax`](./measures.dax):

```dax
// 1. Nhóm Chỉ số Dự báo Máy học
Total Scored Flights = COUNTROWS ( fct_flight_regulatory_predictions )

High Risk Flights (AI Alert) = 
CALCULATE (
    COUNTROWS ( fct_flight_regulatory_predictions ),
    fct_flight_regulatory_predictions[is_predicted_delayed] = TRUE ()
)

High Risk Flight % = 
DIVIDE ( [High Risk Flights (AI Alert)], [Total Scored Flights] )

Avg Predicted Delay Probability = 
AVERAGE ( fct_flight_regulatory_predictions[delay_probability] )

// 2. Nhóm Chỉ số Đấu trường Mô hình (Tournament Champion)
Tournament Winner Model = 
CALCULATE (
    MAX ( ml_tournament_metrics[model_name] ),
    ml_tournament_metrics[is_winner] = TRUE ()
)

Tournament Winner Test AUC = 
CALCULATE (
    MAX ( ml_tournament_metrics[test_auc] ),
    ml_tournament_metrics[is_winner] = TRUE ()
)

// 3. Nhóm Chỉ số Rủi ro Pháp lý & Chế tài Nhà nước
Tarmac Delay Risk Count (14 CFR § 259.4) = 
CALCULATE (
    COUNTROWS ( fct_flight_regulatory_predictions ),
    fct_flight_regulatory_predictions[is_tarmac_risk] = TRUE ()
)

Potential DOT Penalty Exposure ($) = 
SUM ( fct_flight_regulatory_predictions[max_penalty_exposure_usd] )

Crew Time-out Risk Count (FAR Part 117) = 
CALCULATE (
    COUNTROWS ( fct_flight_regulatory_predictions ),
    fct_flight_regulatory_predictions[is_crew_duty_risk] = TRUE ()
)

Mandatory Refund Risk Count (14 CFR § 260.6) = 
CALCULATE (
    COUNTROWS ( fct_flight_regulatory_predictions ),
    fct_flight_regulatory_predictions[is_cash_refund_mandate] = TRUE ()
)

// 4. Màu sắc Định dạng Điều kiện (Conditional Formatting)
Risk Band Color = 
SWITCH (
    SELECTEDVALUE ( fct_flight_regulatory_predictions[risk_band] ),
    "High", "#E74C3C",        // Đỏ (Rủi ro cao & chế tài pháp lý)
    "Elevated", "#F39C12",    // Cam (Cần giám sát & cập nhật hành khách)
    "Normal", "#2ECC71",      // Xanh lá (Hành lang bay an toàn)
    "#95A5A6"
)

Penalty Exposure Severity Color = 
SWITCH (
    TRUE (),
    [Potential DOT Penalty Exposure ($)] >= 50000000, "#C0392B", // Đỏ sẫm (> $50M rủi ro)
    [Potential DOT Penalty Exposure ($)] > 0, "#E67E22",         // Vàng cam
    "#27AE60"                                                    // Xanh lá (An toàn)
)
```

---

## 6. HƯỚNG DẪN THỰC HIỆN TỪNG BƯỚC TRONG POWER BI DESKTOP

1. **Bước 1: Nạp 2 bảng dữ liệu Parquet mới**:
   - Mở Power BI Desktop $\to$ *Get Data* $\to$ *Parquet*.
   - Chọn `dashboards/powerbi/export/ml_tournament_metrics.parquet`.
   - Chọn `dashboards/powerbi/export/fct_flight_regulatory_predictions.parquet`.
   - Nhấn *Load*.

2. **Bước 2: Thiết lập mối quan hệ trong Model View**:
   - Kéo `dim_date[date_key]` $\to$ `fct_flight_regulatory_predictions[date_key]`.
   - Kéo `dim_airport[airport_key]` $\to$ `fct_flight_regulatory_predictions[origin_airport_key]`.
   - Kéo `dim_airline[airline_key]` $\to$ `fct_flight_regulatory_predictions[airline_key]`.

3. **Bước 3: Tạo Measures**:
   - Chọn bảng `fct_flight_regulatory_predictions` $\to$ *New Measure*.
   - Copy & paste lần lượt các measures trong mục 5 vào.

4. **Bước 4: Tạo Trang 4 (Page 4)**:
   - Đặt tên trang: `4. AI Predictive Risk & Compliance`.
   - Kéo thả 4 thẻ KPI lên hàng đầu.
   - Thêm biểu đồ cột so sánh Tournament models ở góc trên bên trái.
   - Thêm biểu đồ xếp chồng rủi ro pháp lý theo hãng ở góc trên bên phải.
   - Thêm bảng ma trận tác nghiệp OCC ở nửa dưới trang.

5. **Bước 5: Thiết lập Định dạng màu điều kiện (Conditional Formatting)**:
   - Trên bảng ma trận OCC: Chọn cột `risk_band` $\to$ *Conditional Formatting* $\to$ *Background color* $\to$ chọn Format style: *Field value* $\to$ chọn measure `[Risk Band Color]`.
   - Chọn cột `delay_probability` $\to$ *Conditional Formatting* $\to$ *Data bars* (màu đỏ nhạt).

🎉 **KẾT QUẢ ĐẠT ĐƯỢC**: Báo cáo Power BI sở hữu một mạch phân tích xuyên suốt 4 trang hoàn chỉnh từ **Quá khứ $\to$ Nguyên nhân $\to$ Không gian mạng lưới $\to$ Tương lai & Mệnh lệnh điều hành thực tế**, đáp ứng hoàn hảo yêu cầu khắt khe của một Kỹ sư Trưởng Dữ liệu & Chuyên gia Phân tích Doanh nghiệp!
