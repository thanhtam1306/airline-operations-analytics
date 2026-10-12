import os
import subprocess
import sys
from pathlib import Path

# Auto-re-exec in project virtualenv if running in system Python
try:
    import pandas as pd  # noqa: F401
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[1]
    venv_py = project_root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if venv_py.exists() and Path(sys.executable).resolve() != venv_py.resolve():
        cmd = [str(venv_py), str(Path(__file__).resolve())] + sys.argv[1:]
        res = subprocess.run(cmd)
        sys.exit(res.returncode)
    raise

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import get_postgres_connection
import pandas as pd

pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 1000)

def main():
    con = get_postgres_connection()
    print("=" * 80)
    print("AIRLINE DATA PLATFORM - BUSINESS INTELLIGENCE INSIGHTS")
    print("=" * 80)

    # Problem 1
    print("\n[BÀI TOÁN 1] Top 10 Sân Bay & Khung Giờ Khởi Hành Trễ Nghiêm Trọng Nhất:")
    q1 = """
    WITH flight_stats AS (
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
        GROUP BY f.origin_airport, a.airport_name, a.city, EXTRACT(HOUR FROM f.scheduled_departure_ts)
        HAVING COUNT(*) >= 20
    )
    SELECT *
    FROM flight_stats
    ORDER BY avg_dep_delay DESC
    LIMIT 10;
    """
    df1 = pd.read_sql(q1, con)
    print(df1.to_string(index=False))

    # Problem 2
    print("\n" + "=" * 80)
    print("[BÀI TOÁN 2] Cascading Delays - Trễ Dây Chuyền Theo Vòng Đời Tàu Bay:")
    q2 = """
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
    WHERE leg_sequence > 1 AND prev_arr_delay >= 15
    ORDER BY flight_date, tail_number, leg_sequence
    LIMIT 10;
    """
    df2 = pd.read_sql(q2, con)
    print(df2.to_string(index=False))

    # Problem 3
    print("\n" + "=" * 80)
    print("[BÀI TOÁN 3] So Sánh Hiệu Quả Hãng Giá Rẻ (LCC) vs Hãng Truyền Thống (Legacy):")
    q3 = """
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
    """
    df3 = pd.read_sql(q3, con)
    print(df3.to_string(index=False))

    # Problem 4
    print("\n" + "=" * 80)
    print("[BÀI TOÁN 4] Khả Năng Bù Giờ Trên Không (Airborne Make-up Time) Theo Tuyến Bay:")
    q4 = """
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
    HAVING COUNT(*) >= 15
    ORDER BY recovery_rate_pct DESC, avg_minutes_made_up DESC
    LIMIT 10;
    """
    df4 = pd.read_sql(q4, con)
    print(df4.to_string(index=False))
    print("=" * 80)

if __name__ == "__main__":
    main()
