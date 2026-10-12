-- =====================================================================
-- AIRLINE DATA PLATFORM: AD-HOC BUSINESS INTELLIGENCE & INSIGHT QUERIES
-- Mục tiêu: Giải quyết 4 bài toán kinh doanh hóc búa của ngành hàng không
-- Hỗ trợ: PostgreSQL (marts schema) & DuckDB
-- =====================================================================

-- ---------------------------------------------------------------------
-- 🧩 BÀI TOÁN 1: HUB BOTTLENECK & PHÂN TÍCH KHUNG GIỜ CAO ĐIỂM
-- Mục tiêu: Tìm 10 sân bay xuất phát (origin_airport) có tình trạng trễ nghiêm trọng nhất 
--           và xác định khung giờ khởi hành nào trong ngày là "thảm họa" nhất.
-- Tiêu chuẩn On-time A14: Đến trễ dưới 15 phút (arr_delay_min < 15) và không bị hủy/chuyển hướng.
-- ---------------------------------------------------------------------

-- Cách 1A: Chi tiết theo từng cặp (Sân bay x Khung giờ khởi hành)
WITH airport_hour_delays AS (
    SELECT 
        f.origin_airport,
        a.airport_name,
        a.city,
        EXTRACT(HOUR FROM f.scheduled_departure_ts)::int AS dep_hour,
        COUNT(*) AS total_flights,
        ROUND(100.0 * COUNT(*) FILTER (WHERE f.is_on_time) / COUNT(*), 2) AS ontime_pct,
        ROUND(AVG(f.dep_delay_min)::numeric, 2) AS avg_dep_delay
    FROM marts.fact_flights f
    JOIN marts.dim_airport a ON f.origin_airport = a.airport_code
    GROUP BY 
        f.origin_airport, 
        a.airport_name, 
        a.city, 
        EXTRACT(HOUR FROM f.scheduled_departure_ts)
)
SELECT 
    origin_airport,
    airport_name,
    city,
    dep_hour,
    total_flights,
    ontime_pct,
    avg_dep_delay
FROM airport_hour_delays
WHERE total_flights >= 20  -- Loại bỏ khung giờ có quá ít chuyến bay
ORDER BY avg_dep_delay DESC
LIMIT 10;

-- Cách 1B: Tìm Top 10 Sân bay có mức trễ cao nhất toàn hệ thống, 
-- sau đó trích xuất chính xác "Khung giờ thảm họa nhất" của từng sân bay đó
WITH top_delayed_airports AS (
    SELECT 
        origin_airport,
        AVG(dep_delay_min) AS overall_avg_delay
    FROM marts.fact_flights
    WHERE NOT is_cancelled
    GROUP BY origin_airport
    HAVING COUNT(*) >= 500
    ORDER BY overall_avg_delay DESC
    LIMIT 10
),
hourly_stats AS (
    SELECT 
        f.origin_airport,
        a.airport_name,
        a.city,
        EXTRACT(HOUR FROM f.scheduled_departure_ts)::int AS dep_hour,
        COUNT(*) AS total_flights,
        ROUND(100.0 * COUNT(*) FILTER (WHERE f.is_on_time) / COUNT(*), 2) AS ontime_pct,
        ROUND(AVG(f.dep_delay_min)::numeric, 2) AS avg_dep_delay,
        ROW_NUMBER() OVER (
            PARTITION BY f.origin_airport 
            ORDER BY AVG(f.dep_delay_min) DESC
        ) AS rank_worst_hour
    FROM marts.fact_flights f
    JOIN marts.dim_airport a ON f.origin_airport = a.airport_code
    WHERE f.origin_airport IN (SELECT origin_airport FROM top_delayed_airports)
    GROUP BY f.origin_airport, a.airport_name, a.city, EXTRACT(HOUR FROM f.scheduled_departure_ts)
    HAVING COUNT(*) >= 20
)
SELECT 
    origin_airport,
    airport_name,
    city,
    dep_hour,
    total_flights,
    ontime_pct,
    avg_dep_delay
FROM hourly_stats
WHERE rank_worst_hour = 1
ORDER BY avg_dep_delay DESC;


-- ---------------------------------------------------------------------
-- 🧩 BÀI TOÁN 2: CASCADING DELAYS (HIỆU ỨNG TRỄ DÂY CHUYỀN THEO TÀU BAY)
-- Mục tiêu: Theo dõi hành trình máy bay theo từng số hiệu đuôi (tail_number) trong ngày.
--           Xác định khi chặng trước bị trễ, chặng tiếp theo bị kéo theo ra sao.
-- ---------------------------------------------------------------------

-- Bảng chi tiết từng chặng bay kèm thông tin trễ chặng trước
WITH flight_legs AS (
    SELECT 
        tail_number,
        flight_date,
        flight_number,
        origin_airport,
        dest_airport,
        TO_CHAR(scheduled_departure_ts, 'HH24:MI') AS crs_dep_time,
        scheduled_departure_ts,
        dep_delay_min AS current_dep_delay,
        arr_delay_min AS current_arr_delay,
        ROW_NUMBER() OVER (
            PARTITION BY tail_number, flight_date 
            ORDER BY scheduled_departure_ts
        ) AS leg_sequence,
        LAG(arr_delay_min) OVER (
            PARTITION BY tail_number, flight_date 
            ORDER BY scheduled_departure_ts
        ) AS prev_arr_delay
    FROM marts.fact_flights
    WHERE tail_number IS NOT NULL
      AND NOT is_cancelled
)
SELECT 
    tail_number,
    flight_date,
    flight_number,
    origin_airport,
    dest_airport,
    crs_dep_time,
    leg_sequence,
    prev_arr_delay,
    current_dep_delay
FROM flight_legs
ORDER BY flight_date, tail_number, leg_sequence
LIMIT 20;

-- Truy vấn phân tích mở rộng: Đánh giá mức độ lây lan trễ từ chặng trước sang chặng sau
WITH flight_legs AS (
    SELECT 
        tail_number,
        flight_date,
        dep_delay_min,
        arr_delay_min,
        ROW_NUMBER() OVER (
            PARTITION BY tail_number, flight_date 
            ORDER BY scheduled_departure_ts
        ) AS leg_sequence,
        LAG(arr_delay_min) OVER (
            PARTITION BY tail_number, flight_date 
            ORDER BY scheduled_departure_ts
        ) AS prev_arr_delay
    FROM marts.fact_flights
    WHERE tail_number IS NOT NULL
      AND NOT is_cancelled
)
SELECT 
    CASE 
        WHEN prev_arr_delay IS NULL THEN '1. Chặng đầu tiên trong ngày'
        WHEN prev_arr_delay < 0 THEN '2. Chặng trước đến sớm (< 0p)'
        WHEN prev_arr_delay < 15 THEN '3. Chặng trước đúng giờ (0-14p)'
        WHEN prev_arr_delay < 45 THEN '4. Chặng trước trễ nhẹ (15-44p)'
        ELSE '5. Chặng trước trễ nặng (>= 45p)'
    END AS prev_leg_status,
    COUNT(*) AS total_legs,
    ROUND(100.0 * COUNT(*) FILTER (WHERE dep_delay_min >= 15) / COUNT(*), 2) AS delayed_dep_pct,
    ROUND(AVG(dep_delay_min)::numeric, 2) AS avg_dep_delay,
    ROUND(AVG(arr_delay_min)::numeric, 2) AS avg_arr_delay
FROM flight_legs
GROUP BY 1
ORDER BY 1;


-- ---------------------------------------------------------------------
-- 🧩 BÀI TOÁN 3: HÃNG GIÁ RẺ (LCC) VS HÃNG TRUYỀN THỐNG (LEGACY)
-- Mục tiêu: So sánh hiệu quả vận hành giữa 2 mô hình kinh doanh hàng không:
--   - Legacy: Delta (DL), American Airlines (AA), United Airlines (UA).
--   - LCC: Southwest (WN), Spirit (NK), Frontier (F9), Allegiant (G4).
-- ---------------------------------------------------------------------

WITH carrier_performance AS (
    SELECT 
        f.flight_id,
        f.carrier_code,
        a.carrier_name,
        CASE 
            WHEN f.carrier_code IN ('DL', 'AA', 'UA') THEN 'Legacy'
            WHEN f.carrier_code IN ('WN', 'NK', 'F9', 'G4') THEN 'LCC'
            ELSE 'Other'
        END AS carrier_group,
        f.is_on_time,
        f.is_cancelled,
        f.carrier_delay_min,
        f.late_aircraft_delay_min,
        f.nas_delay_min,
        (f.carrier_delay_min + f.weather_delay_min + f.nas_delay_min + f.security_delay_min + f.late_aircraft_delay_min) AS total_delay_mins
    FROM marts.fact_flights f
    JOIN marts.dim_airline a ON f.carrier_code = a.carrier_code
    WHERE f.carrier_code IN ('DL', 'AA', 'UA', 'WN', 'NK', 'F9', 'G4')
)
SELECT 
    carrier_group,
    carrier_name,
    COUNT(*) AS total_flights,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_on_time) / COUNT(*), 2) AS ontime_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_cancelled) / COUNT(*), 2) AS cancellation_pct,
    ROUND(100.0 * SUM(carrier_delay_min) / NULLIF(SUM(total_delay_mins), 0), 2) AS pct_carrier_delay,
    ROUND(100.0 * SUM(late_aircraft_delay_min) / NULLIF(SUM(total_delay_mins), 0), 2) AS pct_late_aircraft_delay,
    ROUND(100.0 * SUM(nas_delay_min) / NULLIF(SUM(total_delay_mins), 0), 2) AS pct_nas_delay
FROM carrier_performance
GROUP BY carrier_group, carrier_name
ORDER BY carrier_group, total_flights DESC;


-- ---------------------------------------------------------------------
-- 🧩 BÀI TOÁN 4: KHẢ NĂNG "BÙ GIỜ TRÊN KHÔNG" (AIRBORNE MAKE-UP TIME)
-- Mục tiêu: Đánh giá khả năng bù giờ của phi công khi cất cánh trễ >= 15 phút.
--           Tìm ra tuyến bay (Route) có tỷ lệ "cứu trễ" ngoạn mục nhất.
-- ---------------------------------------------------------------------

SELECT 
    (origin_airport || ' -> ' || dest_airport) AS route,
    COUNT(*) AS delayed_departures,
    COUNT(*) FILTER (WHERE arr_delay_min < 15) AS saved_flights,
    ROUND(100.0 * COUNT(*) FILTER (WHERE arr_delay_min < 15) / COUNT(*), 2) AS recovery_rate_pct,
    ROUND(AVG(dep_delay_min - arr_delay_min)::numeric, 2) AS avg_minutes_made_up
FROM marts.fact_flights
WHERE dep_delay_min >= 15
  AND NOT is_cancelled
  AND NOT is_diverted
GROUP BY origin_airport, dest_airport
HAVING COUNT(*) >= 15  -- Ngưỡng thống kê đủ tin cậy trên tập dữ liệu
ORDER BY recovery_rate_pct DESC, avg_minutes_made_up DESC
LIMIT 15;
