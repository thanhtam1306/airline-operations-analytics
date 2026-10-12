"""
Unit tests for the 4 OCC Cockpit upgrades:
P1 - Cockpit Dark Mode Toggle (:root[data-theme="dark"], localStorage)
P2 - Flight Watch Mini-Table (8 priority flights, one-click load & financial breakdown)
P3 - One-Click Dispatch Release (Aviation format OCC text export)
P4 - Keyboard Hotkeys (Ctrl+K, Alt+1/2/3, Esc)
"""
import pytest
from fastapi.testclient import TestClient

from ml.api import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_p1_dark_mode_toggle_and_occ_palette(client):
    """Verify Header Dark Mode button and OCC color palette :root[data-theme='dark']."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Header toggle button
    assert "theme-toggle-btn" in html
    assert "toggleCockpitTheme" in html
    assert "theme-toggle-icon" in html

    # CSS variables with OCC standard palette
    assert ':root[data-theme="dark"]' in html
    assert "#090e17" in html  # OCC main background
    assert "#111827" in html  # OCC card background
    assert "#1f2937" in html  # OCC border
    assert "#f3f4f6" in html  # OCC text

    # LocalStorage persistence
    assert "occ_cockpit_theme" in html
    assert "initCockpitTheme" in html
    assert "applyCockpitTheme" in html


def test_p2_flight_watch_mini_table(client):
    """Verify Flight Watch Mini-Table with 6-8 priority flights and one-click loader."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    assert "flight-watch-table" in html
    assert "flight-watch-tbody" in html
    assert "Bảng Giám Sát Mạng Bay Trọng Điểm" in html
    assert "selectFlightWatchRow" in html

    # Check key flights in table
    assert "UA4554" in html
    assert "LAS ➔ BOS" in html
    assert "DL3631" in html
    assert "LGB ➔ DCA" in html
    assert "DL6170" in html
    assert "ORD ➔ STL" in html
    assert "UA4406" in html
    assert "AA5957" in html
    assert "WN5880" in html
    assert "WN3117" in html
    assert "AA4451" in html


def test_p3_dispatch_release_export_format(client):
    """Verify One-Click Dispatch Release button and aviation format."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    assert "btn-dispatch-release" in html
    assert "exportDispatchRelease" in html
    assert "Xuất Điện Văn Điều Phái" in html

    # Check required text template elements
    assert "OCC DISPATCH ADVISORY RELEASE - FLIGHT" in html
    assert "ROUTE:" in html
    assert "SCHED DEP:" in html
    assert "RISK LEVEL:" in html
    assert "DELAY PROBABILITY" in html
    assert "PROJECTED DELAY:" in html
    assert "FINANCIAL EXPOSURE:" in html
    assert "REGULATORY WATCH:" in html
    assert "14 CFR 259.4" in html
    assert "FAR PART 117 CREW DUTY" in html
    assert "RECOMMENDED ACTION:" in html
    assert "AUTHORIZED BY: OCC DESK 04" in html


def test_p4_keyboard_hotkeys(client):
    """Verify keyboard shortcuts: Ctrl+K, Alt+1/2/3, Escape."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Hotkey badges in HTML
    assert "Ctrl K" in html
    assert "Alt 1" in html
    assert "Alt 2" in html
    assert "Alt 3" in html

    # JS event listeners
    assert "e.key === 'Escape'" in html
    assert "switchTab('tab-advisory')" in html
    assert "switchTab('tab-chat')" in html
    assert "switchTab('tab-catalog')" in html
    assert "flight_id" in html
    assert "input.select()" in html
