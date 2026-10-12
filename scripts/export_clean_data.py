"""
Export cleaned datasets from PostgreSQL into pure CSV files.
Output Directory: data/clean/
"""
import os
import subprocess
import sys
from pathlib import Path

# Auto-re-exec in project virtualenv if running in system Python
try:
    import pandas as pd  # noqa: F401
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

import pandas as pd
from config.config import get_postgres_engine

CLEAN_DIR = PROJECT_ROOT / "data" / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

TABLES_TO_EXPORT = [
    ("marts", "fact_flights", "clean_fact_flights"),
    ("marts", "fact_flight_delays", "clean_fact_flight_delays"),
    ("marts", "dim_airport", "clean_dim_airport"),
    ("marts", "dim_airline", "clean_dim_airline"),
    ("marts", "dim_date", "clean_dim_date"),
    ("marts", "operational_kpis", "clean_operational_kpis"),
    ("marts", "route_performance", "clean_route_performance"),
    ("marts", "cancellations", "clean_cancellations"),
    ("staging", "stg_flights", "clean_stg_flights"),
]

def export_csv_only():
    engine = get_postgres_engine()
    print("=" * 75)
    print("🚀 ĐANG XUẤT BỘ DỮ LIỆU SẠCH TỪ POSTGRESQL RA FILE CSV")
    print(f"📁 Thư mục lưu: {CLEAN_DIR}")
    print("=" * 75)

    # Xoá file xlsx cũ nếu có
    for old_file in CLEAN_DIR.glob("*.xlsx"):
        try:
            old_file.unlink()
        except Exception:
            pass

    for schema, table, filename in TABLES_TO_EXPORT:
        query = f"SELECT * FROM {schema}.{table}"
        df = pd.read_sql(query, con=engine)
        
        # Xuất file CSV định dạng UTF-8 có BOM để Excel mở không bao giờ bị lỗi font tiếng Việt
        csv_path = CLEAN_DIR / f"{filename}.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        
        fsize_kb = csv_path.stat().st_size / 1024
        print(f"  ✅ Đã xuất {schema}.{table:<20} ({len(df):>6,} dòng, {fsize_kb:>8.1f} KB) -> {csv_path.name}")

    print("=" * 75)
    print("🎉 HOÀN TẤT XUẤT TOÀN BỘ FILE CSV SẠCH!")

if __name__ == "__main__":
    export_csv_only()
