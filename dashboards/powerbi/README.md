# Power BI Semantic Model & Connection Guide

The dbt marts are the single source of truth. Power BI connects to the **same
star schema** the Streamlit app uses, so both tools show identical numbers.

## 1. Connect Power BI to the marts

Pick whichever matches how you ran the platform:

**A. Local PostgreSQL (Active Warehouse, localhost:5432)**
In Power BI Desktop:
1. *Get Data → PostgreSQL database*
2. Server: `localhost:5432`
3. Database: `airline_dwh`
4. Schema: `marts` (select all mart tables)
5. Alternatively, connect directly to the pre-exported Parquet files in `dashboards/powerbi/export/` for instant, high-speed import without needing database credentials.

**B. Local DuckDB (offline / single-file warehouse)**
The pipeline writes `warehouse/airline.duckdb`. Export the marts to Parquet
once and point Power BI at them (DuckDB has no native Power BI connector):

```bash
python scripts/export_marts.py      # writes dashboards/powerbi/export/*.parquet
```

Then in Power BI Desktop: *Get Data → Parquet* → select each file in
`dashboards/powerbi/export/`.

**C. Snowflake (cloud target)**
When the platform runs with `WAREHOUSE=snowflake`, the marts live in
`AIRLINE_DWH.MARTS`. In Power BI: *Get Data → Snowflake*, enter your account
URL and warehouse, and select the `MARTS` schema. Use **Import** mode for this
data volume (DirectQuery is available if you need live refresh).

## 2. Model (star schema)

Import these tables and set relationships (single-direction, one-to-many from
dimension to fact):

| From (dimension)          | To (fact)            | Key                 |
|---------------------------|----------------------|---------------------|
| `dim_date[date_key]`      | `fact_flights`       | `date_key`          |
| `dim_airport[airport_key]`| `fact_flights`       | `origin_airport_key`|
| `dim_airport[airport_key]`| `fact_flights`       | `dest_airport_key` *(inactive; USERELATIONSHIP for destination analysis)* |
| `dim_airline[airline_key]`| `fact_flights`       | `airline_key`       |
| `dim_date[date_key]`      | `fact_flight_delays` | `date_key`          |
| `dim_airline[airline_key]`| `fact_flight_delays` | `airline_key`       |

Mark `dim_date` as the official **Date table** (`date_day`).

## 3. Measures

All measures are in [`measures.dax`](./measures.dax). Core set:

- **Total Flights**, **Cancelled Flights**, **Cancellation %**
- **On-Time %**, **Completion Factor %**
- **Avg Arrival Delay**, **Avg Departure Delay**
- **Total Delay Minutes** + one measure per cause (Carrier / Weather / NAS /
  Security / Late Aircraft) for a delay-cause breakdown visual

## 4. Report pages (Cohesive 4-Stage Analytics Storyline)

Xem tài liệu thiết kế chi tiết tại [`PAGE_4_DESIGN.md`](./PAGE_4_DESIGN.md):

1. **Page 1: Executive Operations Overview (Descriptive)**:
   - "Chuyện gì đã xảy ra?" — Đo lường OTP (75-78%), tỷ lệ hủy chuyến, số phút trễ trung bình.
2. **Page 2: Delay Root-Cause & Cascading Domino (Diagnostic)**:
   - "Tại sao lại trễ?" — Phân tích 5 nguyên nhân US DOT BTS & hiệu ứng domino "Late Aircraft" chiếm ~40% số phút trễ.
3. **Page 3: Hub Bottlenecks & Route Performance (Diagnostic Deep-dive)**:
   - "Nghẽn ở đâu và chặng nào?" — Điểm nghẽn không gian tại Mega Hub (DFW, ORD, ATL) vào giờ cao điểm chiều tối.
4. **Page 4: AI Predictive Risk & Aviation Regulatory Governance (Predictive & Prescriptive)**:
   - "Tương lai chuyến nào sẽ trễ, vi phạm luật gì và OCC phải ra lệnh gì?" — Đấu trường 5 mô hình ML, dự báo xác suất trễ theo giờ bay, thẩm định pháp lý tự động (14 CFR § 259.4 Tarmac Delay, FAR Part 117 Crew Duty, 14 CFR § 260.6 Cash Refund, 14 CFR § 234.11 Chronic Route) và bảng tác nghiệp OCC Dispatcher trực tiếp.

## 5. Exporting Parquet Tables for Power BI

```bash
# Xuất các bảng dbt marts cơ bản (fact_flights, dim_*, route_performance, ...)
python scripts/export_marts.py

# Xuất các bảng ML Tournament & Thẩm định Pháp lý (Page 4)
python scripts/export_ml_powerbi.py
```

