"""
Airline Operations Analytics — 3-page Streamlit app over the dbt marts.

Data source resolution (parameterized, zero-config):
  1. live DuckDB warehouse (warehouse/airline.duckdb) when present — local dev
  2. bundled parquet extract (dashboards/public_data/) — public cloud deploy,
     no warehouse needed (this is what share.streamlit.io runs)

Pages: Overview KPIs · Route explorer · Delay causes
KPI definitions: docs/kpi_definitions.md (the single source of truth).

    streamlit run dashboards/streamlit_app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PUBLIC_DIR = Path(__file__).resolve().parent / "public_data"
MARTS = ["operational_kpis", "delay_trends", "route_performance",
         "cancellations", "dim_airport", "dim_airline"]


# ----------------------------- data access --------------------------------- #
EXPORT_DIR = Path(__file__).resolve().parent / "powerbi" / "export"

@st.cache_data(show_spinner=False, ttl=3600)
def load_marts() -> tuple[dict, str]:
    """Return ({mart: DataFrame}, source_label). Warehouse first, export/extract fallback."""
    try:
        from config import settings

        if settings.warehouse == "postgres":
            from config import get_postgres_engine

            engine = get_postgres_engine()
            data = {t: pd.read_sql(f"SELECT * FROM marts.{t}", con=engine) for t in MARTS}
            return data, "live warehouse (PostgreSQL localhost:5432)"

        import duckdb

        if settings.duckdb_path.exists():
            con = duckdb.connect(str(settings.duckdb_path), read_only=True)
            try:
                data = {t: con.sql(f"SELECT * FROM marts.{t}").df() for t in MARTS}
                return data, "live warehouse (DuckDB)"
            finally:
                con.close()
    except Exception:
        pass

    # Fallback to local Parquet export if available
    if EXPORT_DIR.exists() and all((EXPORT_DIR / f"{t}.parquet").exists() for t in MARTS):
        data = {t: pd.read_parquet(EXPORT_DIR / f"{t}.parquet") for t in MARTS}
        return data, "exported warehouse Parquet (dashboards/powerbi/export/)"

    if PUBLIC_DIR.exists() and all((PUBLIC_DIR / f"{t}.parquet").exists() for t in MARTS):
        data = {t: pd.read_parquet(PUBLIC_DIR / f"{t}.parquet") for t in MARTS}
        return data, "bundled real-data extract"

    raise FileNotFoundError(
        "Không tìm thấy kho dữ liệu hoặc tệp dữ liệu nào. "
        "Vui lòng chạy `make pipeline` hoặc khởi chạy PostgreSQL `localhost:5432`."
    )


def provenance(m: dict | None = None) -> str:
    p = PUBLIC_DIR / "_provenance.txt"
    if p.exists():
        kv = dict(line.split("=", 1) for line in p.read_text().splitlines() if "=" in line)
        return (f"{int(kv.get('flights', 0)):,} real flights · US DOT BTS · "
                f"{kv.get('from')} → {kv.get('to')}")
    if m and "operational_kpis" in m:
        total = int(m["operational_kpis"]["total_flights"].sum())
        return f"{total:,} flights · Airline Data Platform"
    return "airline operations data"


# ----------------------------- pages --------------------------------------- #
def page_overview(m: dict) -> None:
    k = m["operational_kpis"]
    trend = m["delay_trends"].sort_values("date_day")

    # Interactive Carrier Filter
    carriers = ["(Tất cả hãng / All)"] + sorted(k["carrier_name"].dropna().unique().tolist())
    selected_carrier = st.selectbox("✈️ Lọc theo hãng hàng không (Carrier Filter)", carriers)

    if selected_carrier != "(Tất cả hãng / All)":
        k_view = k[k["carrier_name"] == selected_carrier]
    else:
        k_view = k

    # Empty State check
    if k_view.empty:
        st.info("⚠️ Không tìm thấy dữ liệu chuyến bay nào khớp với bộ lọc hãng bay.")
        return

    total = int(k_view["total_flights"].sum())
    cancelled = int(k_view["cancelled_flights"].sum())
    completed = total - cancelled
    on_time_pct = (k_view["on_time_pct"] * k_view["total_flights"]).sum() / max(total, 1)
    avg_delay = (k_view["avg_arr_delay_min"] * k_view["total_flights"]).sum() / max(total, 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng chuyến bay (Flights)", f"{total:,}")
    c2.metric("Tỷ lệ đúng giờ (On-Time %)", f"{on_time_pct:.1f}%",
              help="Completed flights arriving < 15 min late (US DOT A14). See docs/kpi_definitions.md")
    c3.metric("Tỷ lệ hủy (Cancellation rate)", f"{100.0 * cancelled / max(total, 1):.2f}%")
    c4.metric("Trễ đến TB (Avg arrival delay)", f"{avg_delay:.1f} min",
              help="Mean over completed flights; early arrivals count negative.")

    st.subheader("Xu hướng chuyến bay trễ và chuyến bay bị hủy theo ngày")
    fig = px.line(trend, x="date_day", y=["delayed_flights", "cancelled_flights"],
                  labels={"value": "Số chuyến bay", "date_day": "Ngày", "variable": "Phân loại"})
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Tỷ lệ đúng giờ theo hãng hàng không (On-Time %)")
        kk = k.sort_values("on_time_pct", ascending=True)
        st.plotly_chart(px.bar(kk, x="on_time_pct", y="carrier_name", orientation="h",
                               labels={"on_time_pct": "Tỷ lệ đúng giờ (%)", "carrier_name": ""}),
                        use_container_width=True)
    with right:
        st.subheader("Cơ cấu nguyên nhân hủy chuyến")
        c = m["cancellations"].groupby("cancellation_reason", as_index=False)["cancelled_flights"].sum()
        st.plotly_chart(px.pie(c, names="cancellation_reason", values="cancelled_flights"),
                        use_container_width=True)


def page_routes(m: dict) -> None:
    rp = m["route_performance"]
    airports = m["dim_airport"]

    st.subheader("Phân tích mạng lưới & Đường bay (Route & Airport Network)")

    tab_map, tab_routes = st.tabs(["🗺️ Bản đồ trễ sân bay (Airport Hub Map)", "🔍 Khám phá đường bay (Route Explorer)"])

    with tab_map:
        st.caption("Phân bổ địa lý các sân bay: kích thước điểm thể hiện lưu lượng chuyến bay, màu sắc thể hiện độ trễ trung bình.")
        airport_stats = (
            rp.groupby("origin_airport", as_index=False)
            .agg(
                total_departures=("total_flights", "sum"),
                avg_arr_delay=("avg_arr_delay_min", "mean"),
                on_time_pct=("on_time_pct", "mean"),
            )
            .merge(airports, left_on="origin_airport", right_on="airport_code", how="inner")
        )

        if not airport_stats.empty:
            fig_map = px.scatter_geo(
                airport_stats,
                lat="latitude",
                lon="longitude",
                size="total_departures",
                color="avg_arr_delay",
                hover_name="airport_name",
                hover_data={
                    "airport_code": True,
                    "city": True,
                    "state": True,
                    "total_departures": True,
                    "avg_arr_delay": ":.1f",
                    "on_time_pct": ":.1f",
                    "latitude": False,
                    "longitude": False,
                },
                scope="usa",
                color_continuous_scale="Reds",
            )
            fig_map.update_layout(height=520, margin={"r": 0, "t": 20, "l": 0, "b": 0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("⚠️ Không tìm thấy tọa độ sân bay để hiển thị bản đồ.")

    with tab_routes:
        st.caption("Các cặp sân bay chiều đi (Origin → Destination). Các đường bay <20 chuyến đã được lọc bỏ theo quy chuẩn.")

        codes = sorted(set(rp["origin_airport"]) | set(rp["dest_airport"]))
        c1, c2, c3 = st.columns([1, 1, 2])
        origin = c1.selectbox("Sân bay đi (Origin)", ["(Tất cả / All)"] + codes)
        dest = c2.selectbox("Sân bay đến (Destination)", ["(Tất cả / All)"] + codes)
        min_flights = c3.slider("Số chuyến tối thiểu trên chặng (Min flights)", 20, 2000, 100, step=20)

        view = rp[rp["total_flights"] >= min_flights]
        if origin != "(Tất cả / All)":
            view = view[view["origin_airport"] == origin]
        if dest != "(Tất cả / All)":
            view = view[view["dest_airport"] == dest]

        # Empty state check
        if view.empty:
            st.info("⚠️ Không tìm thấy đường bay nào khớp với bộ lọc. Vui lòng giảm số chuyến bay tối thiểu hoặc chọn sân bay khác.")
        else:
            st.plotly_chart(
                px.scatter(view, x="on_time_pct", y="avg_arr_delay_min", size="total_flights",
                           hover_name="route", color="cancellation_pct",
                           labels={"on_time_pct": "Tỷ lệ đúng giờ (%)", "avg_arr_delay_min": "Trễ đến trung bình (phút)",
                                   "cancellation_pct": "Tỷ lệ hủy (%)"},
                           color_continuous_scale="Reds"),
                use_container_width=True)

            st.subheader("Top đường bay có độ trễ cao nhất")
            cols = ["route", "total_flights", "on_time_pct", "avg_arr_delay_min", "cancellation_pct"]
            st.dataframe(view.sort_values("avg_arr_delay_min", ascending=False).head(25)[cols],
                         use_container_width=True, hide_index=True)
            st.caption(f"{len(view):,} đường bay đang hiển thị")

        with st.expander("Tra cứu thông tin sân bay (Airport Reference)"):
            st.dataframe(airports[["airport_code", "airport_name", "city", "state", "region"]],
                         use_container_width=True, hide_index=True)


def page_delay_causes(m: dict) -> None:
    trend = m["delay_trends"].sort_values("date_day")
    cause_cols = {
        "total_carrier_delay_min": "Hãng hàng không (Carrier)",
        "total_weather_delay_min": "Thời tiết (Weather)",
        "total_nas_delay_min": "Không phận NAS",
        "total_late_aircraft_delay_min": "Máy bay đến trễ (Late aircraft)",
    }

    st.subheader("Phân bổ số phút trễ theo nguyên nhân (Delay Causes)")
    st.caption("Cơ quan BTS chỉ phân bổ nguyên nhân khi thời gian trễ đến ≥ 15 phút. "
               "'Máy bay đến trễ' là ảnh hưởng dây chuyền từ chặng bay trước đó.")

    totals = trend[list(cause_cols)].sum().rename(index=cause_cols).reset_index()
    totals.columns = ["cause", "minutes"]
    left, right = st.columns([1, 2])
    with left:
        st.plotly_chart(px.pie(totals, names="cause", values="minutes"), use_container_width=True)
    with right:
        long = trend.melt(id_vars="date_day", value_vars=list(cause_cols),
                          var_name="cause", value_name="minutes")
        long["cause"] = long["cause"].map(cause_cols)
        st.plotly_chart(px.area(long, x="date_day", y="minutes", color="cause",
                                labels={"date_day": "Ngày", "minutes": "Tổng số phút trễ", "cause": "Nguyên nhân"}),
                        use_container_width=True)

    st.subheader("Tỷ lệ chuyến bay trễ theo thời gian (Delay Rate ≥ 15min)")
    st.plotly_chart(px.line(trend, x="date_day", y="delayed_pct",
                            labels={"delayed_pct": "Tỷ lệ trễ ≥15 phút (%)", "date_day": "Ngày"}),
                    use_container_width=True)


# ----------------------------- shell ---------------------------------------- #
def main() -> None:
    st.set_page_config(page_title="Airline Operations Analytics", layout="wide", page_icon="✈️")
    
    with st.spinner("Đang tải dữ liệu phân tích vận hành từ kho dữ liệu..."):
        try:
            marts, source = load_marts()
        except Exception as e:
            st.error(
                f"❌ Không thể tải dữ liệu: {e}\n\n"
                "💡 **Hướng dẫn khắc phục:**\n"
                "- Nếu sử dụng PostgreSQL: Đảm bảo dịch vụ PostgreSQL đang chạy tại `localhost:5432` với database `airline_dwh`.\n"
                "- Nếu sử dụng DuckDB: Chạy `make pipeline` để khởi tạo dữ liệu.\n"
                "- Hoặc chạy `python scripts/export_marts.py` để trích xuất dữ liệu Parquet."
            )
            return

    st.sidebar.title("✈️ Airline Ops Analytics")
    page = st.sidebar.radio("Chọn trang phân tích", ["Overview KPIs", "Route explorer", "Delay causes"])
    st.sidebar.markdown("---")
    st.sidebar.caption(f"**Nguồn dữ liệu:** {provenance(marts)}")
    st.sidebar.caption(f"**Kết nối:** {source}")
    st.sidebar.markdown(
        "[KPI definitions](https://github.com/battina1999/airline-data-platform/blob/main/docs/kpi_definitions.md) · "
        "[Always-on dashboard](https://battina1999.github.io/airline-data-platform/) · "
        "[Lineage](https://battina1999.github.io/airline-data-platform/lineage/) · "
        "[Repo](https://github.com/battina1999/airline-data-platform)")

    st.title("Nền tảng Phân tích Vận hành Hàng không")
    st.caption(f"{provenance(marts)} — Được xây dựng từ mô hình dbt Kimball Star Schema trên kho dữ liệu.")

    if page == "Overview KPIs":
        page_overview(marts)
    elif page == "Route explorer":
        page_routes(marts)
    else:
        page_delay_causes(marts)


if __name__ == "__main__":
    main()
