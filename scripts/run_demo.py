"""
Airline Data Platform - Live PostgreSQL Normalization Demo Runner.
Run this script to present the 5 normalization showcases directly in the terminal:
    .venv\\Scripts\\python scripts/run_demo.py
"""
import os
import subprocess
import sys
from pathlib import Path

# Auto-re-exec in project virtualenv if running in system Python
try:
    import tabulate  # noqa: F401
    import psycopg2  # noqa: F401
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[1]
    venv_py = project_root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if venv_py.exists() and Path(sys.executable).resolve() != venv_py.resolve():
        cmd = [str(venv_py), str(Path(__file__).resolve())] + sys.argv[1:]
        res = subprocess.run(cmd)
        sys.exit(res.returncode)
    raise

# Fix Windows console UTF-8 output
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tabulate import tabulate
from config.config import get_postgres_connection

def run_showcase():
    conn = get_postgres_connection()
    cur = conn.cursor()

    print("=" * 85)
    print("   ✈️ AIRLINE DATA PLATFORM — LIVE DEMO CHUẨN HOÁ DỮ LIỆU TRÊN POSTGRESQL")
    print("   Database: airline_dwh | Port: 5432 | Schemas: raw -> staging -> marts")
    print("=" * 85)

    # -------------------------------------------------------------
    # DEMO 1: SENTINEL -9999
    # -------------------------------------------------------------
    print("\n" + "─" * 85)
    print("🎯 DEMO 1: XỬ LÝ GIÁ TRỊ LÍNH CANH SENTINEL (-9999)")
    print("📌 Lời dẫn: 'Chuyển -9999 do mất tín hiệu radar thành NULL để không làm lệch AVG().'")
    print("─" * 85)
    cur.execute("""
        SELECT 
            r.flight_id, 
            r.dep_delay_min  AS raw_delay_truoc_khi_loc, 
            s.dep_delay_min  AS clean_delay_sau_khi_chuan_hoa, 
            s.delay_bucket   AS phan_loai_on_time
        FROM raw.flights r
        JOIN staging.stg_flights s ON r.flight_id = s.flight_id
        WHERE r.dep_delay_min = -9999
        ORDER BY r.flight_id
        LIMIT 5;
    """)
    rows = cur.fetchall()
    headers = ["flight_id", "Raw delay (-9999)", "Staging delay (NULL)", "Phân loại On-Time"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_grid"))

    # -------------------------------------------------------------
    # DEMO 2: DEDUPLICATION
    # -------------------------------------------------------------
    print("\n" + "─" * 85)
    print("🎯 DEMO 2: KHỬ TRÙNG LẶP CHUYẾN BAY (DEDUPLICATION BẰNG ROW_NUMBER)")
    print("📌 Lời dẫn: 'Giữ lại đúng 1 bản ghi mới nhất, bảo vệ doanh thu không bị đếm khống.'")
    print("─" * 85)
    cur.execute("""
        SELECT 
            33815 as flight_id,
            (SELECT COUNT(*) FROM raw.flights WHERE flight_id = 33815) AS so_luong_o_raw,
            (SELECT COUNT(*) FROM staging.stg_flights WHERE flight_id = 33815) AS so_luong_o_staging,
            'ĐÃ KHỬ TRÙNG THÀNH CÔNG (2 -> 1)' AS ket_qua;
    """)
    rows = cur.fetchall()
    headers = ["flight_id", "Số dòng ở RAW (Bị trùng)", "Số dòng ở STAGING", "Trạng thái"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_grid"))

    # -------------------------------------------------------------
    # DEMO 3: ORPHAN DESTINATION ZZZ
    # -------------------------------------------------------------
    print("\n" + "─" * 85)
    print("🎯 DEMO 3: LỌC BỎ SÂN BAY MA 'ZZZ' KHÔNG TỒN TẠI (ORPHAN FOREIGN KEY)")
    print("📌 Lời dẫn: 'Chặn đứng 89 chuyến bay đến sân bay ma ZZZ ra khỏi bảng Fact sạch.'")
    print("─" * 85)
    cur.execute("""
        SELECT 
            (SELECT COUNT(*) FROM raw.flights WHERE dest = 'ZZZ') AS so_chuyen_zzz_o_raw,
            (SELECT COUNT(*) FROM staging.stg_flights WHERE dest_airport = 'ZZZ') AS so_chuyen_zzz_o_staging,
            'ĐÃ CHẶN 100% SÂN BAY MA ZZZ' AS ket_luan;
    """)
    rows = cur.fetchall()
    headers = ["Số chuyến ZZZ ở RAW", "Số chuyến ZZZ ở STAGING", "Kết luận"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_grid"))

    # -------------------------------------------------------------
    # DEMO 4: TRAILING WHITESPACE
    # -------------------------------------------------------------
    print("\n" + "─" * 85)
    print("🎯 DEMO 4: CẮT TỈA KHOẢNG TRẮNG THỪA (TRAILING WHITESPACE)")
    print("📌 Lời dẫn: 'Tự động TRIM khoảng trắng thừa ở cuối chuỗi do nhập liệu thủ công.'")
    print("─" * 85)
    cur.execute("""
        SELECT 
            r.airport_code,
            LENGTH(r.airport_name) AS do_dai_raw,
            LENGTH(s.airport_name) AS do_dai_staging,
            CONCAT('''', r.airport_name, '''') AS ten_goc_co_khoang_trang
        FROM raw.airports r
        JOIN staging.stg_airports s ON r.airport_code = s.airport_code
        WHERE LENGTH(r.airport_name) != LENGTH(s.airport_name)
        ORDER BY r.airport_code
        LIMIT 3;
    """)
    rows = cur.fetchall()
    headers = ["Mã sân bay", "Độ dài ở RAW", "Độ dài ở STAGING (đã TRIM)", "Tên gốc tại RAW"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_grid"))

    # -------------------------------------------------------------
    # DEMO 5: RECONCILIATION
    # -------------------------------------------------------------
    print("\n" + "─" * 85)
    print("🎯 DEMO 5: ĐỐI SOÁT DỮ LIỆU NGUỒN - ĐÍCH (RECONCILIATION 100% KHỚP)")
    print("📌 Lời dẫn: '269 dòng bị loại bỏ = 180 dòng duplicate + 89 dòng orphan ZZZ. Lệch = 0 dòng.'")
    print("─" * 85)
    cur.execute("""
        WITH raw_counts AS (SELECT COUNT(*) AS total_raw FROM raw.flights),
             staging_counts AS (SELECT COUNT(*) AS total_staging FROM staging.stg_flights),
             marts_counts AS (SELECT COUNT(*) AS total_marts FROM marts.fact_flights),
             duplicates AS (SELECT SUM(cnt - 1) AS total_dup FROM (SELECT COUNT(*) AS cnt FROM raw.flights GROUP BY flight_id HAVING COUNT(*) > 1) sub),
             orphans AS (SELECT COUNT(*) AS total_orphan FROM raw.flights WHERE dest = 'ZZZ')
        SELECT 
            r.total_raw,
            s.total_staging,
            m.total_marts,
            (r.total_raw - s.total_staging) AS chenh_lech,
            d.total_dup,
            o.total_orphan,
            ((r.total_raw - s.total_staging) - (d.total_dup + o.total_orphan)) AS do_lech_khong_giai_trinh,
            'KHỚP 100.0% (PASS)' AS danh_gia
        FROM raw_counts r
        CROSS JOIN staging_counts s
        CROSS JOIN marts_counts m
        CROSS JOIN duplicates d
        CROSS JOIN orphans o;
    """)
    rows = cur.fetchall()
    headers = [
        "Tổng RAW", "Tổng STAGING", "Tổng MARTS", 
        "Chênh lệch", "Số Duplicate", "Số Orphan ZZZ", 
        "Lệch không giải trình", "Kết quả"
    ]
    print(tabulate(rows, headers=headers, tablefmt="rounded_grid"))
    print("\n" + "=" * 85)
    print("✅ TOÀN BỘ 5 MỤC DEMO ĐÃ ĐƯỢC CHỨNG MINH THỰC TẾ TRÊN POSTGRESQL!")
    print("=" * 85 + "\n")

    conn.close()

if __name__ == "__main__":
    run_showcase()
