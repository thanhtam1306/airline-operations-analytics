"""
Unit tests for the Streamlit dashboard data loader and components.
"""
from __future__ import annotations

import pytest
import pandas as pd
pytest.importorskip("streamlit")
pytest.importorskip("plotly")
from dashboards.streamlit_app import MARTS, load_marts, provenance


def test_load_marts_returns_all_required_tables():
    data, source = load_marts()
    assert isinstance(data, dict)
    assert isinstance(source, str)
    assert len(source) > 0

    for table in MARTS:
        assert table in data, f"Missing table {table} in load_marts"
        df = data[table]
        assert isinstance(df, pd.DataFrame), f"{table} is not a DataFrame"
        assert not df.empty, f"{table} dataframe is empty"


def test_provenance_handles_live_data():
    data, _ = load_marts()
    prov_text = provenance(data)
    assert isinstance(prov_text, str)
    assert len(prov_text) > 0


def test_airport_geo_join_for_map():
    data, _ = load_marts()
    rp = data["route_performance"]
    airports = data["dim_airport"]

    airport_stats = (
        rp.groupby("origin_airport", as_index=False)
        .agg(
            total_departures=("total_flights", "sum"),
            avg_arr_delay=("avg_arr_delay_min", "mean"),
            on_time_pct=("on_time_pct", "mean"),
        )
        .merge(airports, left_on="origin_airport", right_on="airport_code", how="inner")
    )
    assert not airport_stats.empty
    assert "latitude" in airport_stats.columns
    assert "longitude" in airport_stats.columns
    assert airport_stats["latitude"].notnull().all()
    assert airport_stats["longitude"].notnull().all()
