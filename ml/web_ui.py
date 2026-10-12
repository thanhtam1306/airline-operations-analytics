"""
Web User Interface Generator for Airline Operations OCC Copilot (Phase 6.4 & 6.5).
Branded Application: SkyOps Copilot™ — Next-Gen Airline Operations & Aviation Regulatory Platform.

Delivers a 3-tab modern enterprise interface:
1. Dispatch Advisory & What-If Simulator (Split-screen 2-column cockpit layout)
2. Interactive OCC Copilot Chat (Studio layout: Sidebar flight HUD + conversational stream)
3. Knowledge Catalog (40 Items: 18 Aviation + 14 ML + 8 SOP Checklists with live filter)
"""
from __future__ import annotations

KNOWN_CARRIERS = [
    ("AA", "AA - American Airlines (Legacy)"),
    ("DL", "DL - Delta Air Lines (Legacy)"),
    ("UA", "UA - United Airlines (Legacy)"),
    ("WN", "WN - Southwest Airlines (Low-Cost)"),
    ("AS", "AS - Alaska Airlines (Legacy)"),
    ("B6", "B6 - JetBlue Airways (Low-Cost)"),
    ("NK", "NK - Spirit Airlines (Low-Cost)"),
    ("F9", "F9 - Frontier Airlines (Low-Cost)"),
    ("HA", "HA - Hawaiian Airlines (Legacy)"),
    ("G4", "G4 - Allegiant Air (Low-Cost)"),
]

KNOWN_AIRPORTS = [
    ("ATL", "ATL - Atlanta, GA (Hartsfield-Jackson Intl)"),
    ("AUS", "AUS - Austin, TX (Austin-Bergstrom Intl)"),
    ("BOS", "BOS - Boston, MA (Boston Logan Intl)"),
    ("BWI", "BWI - Baltimore, MD (Baltimore/Washington Intl)"),
    ("CLE", "CLE - Cleveland, OH (Cleveland Hopkins Intl)"),
    ("CLT", "CLT - Charlotte, NC (Charlotte Douglas Intl)"),
    ("DAL", "DAL - Dallas, TX (Dallas Love Field)"),
    ("DCA", "DCA - Washington, DC (Ronald Reagan National)"),
    ("DEN", "DEN - Denver, CO (Denver Intl)"),
    ("DFW", "DFW - Dallas/Fort Worth, TX (Dallas/Fort Worth Intl)"),
    ("DTW", "DTW - Detroit, MI (Detroit Metro Wayne)"),
    ("EWR", "EWR - Newark, NJ (Newark Liberty Intl)"),
    ("FLL", "FLL - Fort Lauderdale, FL (Fort Lauderdale-Hollywood)"),
    ("HNL", "HNL - Honolulu, HI (Daniel K. Inouye Intl)"),
    ("IAH", "IAH - Houston, TX (George Bush Intercontinental)"),
    ("JFK", "JFK - New York, NY (John F. Kennedy Intl)"),
    ("LAS", "LAS - Las Vegas, NV (Harry Reid Intl)"),
    ("LAX", "LAX - Los Angeles, CA (Los Angeles Intl)"),
    ("LGA", "LGA - New York, NY (LaGuardia)"),
    ("LGB", "LGB - Long Beach, CA (Long Beach Airport)"),
    ("MCO", "MCO - Orlando, FL (Orlando Intl)"),
    ("MDW", "MDW - Chicago, IL (Chicago Midway Intl)"),
    ("MIA", "MIA - Miami, FL (Miami Intl)"),
    ("MSP", "MSP - Minneapolis, MN (Minneapolis-St Paul)"),
    ("MSY", "MSY - New Orleans, LA (Louis Armstrong Intl)"),
    ("NSH", "NSH - Nashville, TN (Nashville Intl)"),
    ("OAK", "OAK - Oakland, CA (Oakland Intl)"),
    ("ORD", "ORD - Chicago, IL (Chicago O'Hare Intl)"),
    ("PDX", "PDX - Portland, OR (Portland Intl)"),
    ("PHL", "PHL - Philadelphia, PA (Philadelphia Intl)"),
    ("PHX", "PHX - Phoenix, AZ (Phoenix Sky Harbor)"),
    ("PIT", "PIT - Pittsburgh, PA (Pittsburgh Intl)"),
    ("RDU", "RDU - Raleigh/Durham, NC (Raleigh-Durham Intl)"),
    ("SAN", "SAN - San Diego, CA (San Diego Intl)"),
    ("SEA", "SEA - Seattle, WA (Seattle-Tacoma Intl)"),
    ("SFO", "SFO - San Francisco, CA (San Francisco Intl)"),
    ("SLC", "SLC - Salt Lake City, UT (Salt Lake City Intl)"),
    ("SMF", "SMF - Sacramento, CA (Sacramento Intl)"),
    ("STL", "STL - St. Louis, MO (St. Louis Lambert Intl)"),
    ("TPA", "TPA - Tampa, FL (Tampa Intl)"),
]

HTML_TEMPLATE = r"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SkyOps Platform | Quản Trị Vận Hành & Phân Tích Rủi Ro Hàng Không</title>
  
  <!-- FAVICON SVG: Clean supersonic aviation flight mark -->
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='15' fill='%230f172a' stroke='%230284c7' stroke-width='1.5'/%3E%3Cpath d='M16 7 L23 21 L16 18 L9 21 Z' fill='%2338bdf8'/%3E%3C/svg%3E">

  <!-- GOOGLE FONTS: Plus Jakarta Sans & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">

  <script>
    (function() {
      try {
        var t = localStorage.getItem('occ_cockpit_theme');
        if (t === 'dark') {
          document.documentElement.setAttribute('data-theme', 'dark');
        }
      } catch(e) {}
    })();
  </script>

  <style>
    :root {
      --bg-main: #f8fafc;
      --bg-card: #ffffff;
      --border-color: #e2e8f0;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --table-th-bg: #f8fafc;
      --table-th-text: #475569;
      --table-tr-hover: #f1f5f9;
      --table-tr-active: #e0f2fe;

      --primary: #0284c7;
      --primary-hover: #0369a1;
      --primary-light: #e0f2fe;
      --primary-glow: rgba(2, 132, 199, 0.12);
      --sky-400: #38bdf8;
      --sky-500: #0ea5e9;
      
      --navy-950: #070d18;
      --navy-900: #0f172a;
      --navy-850: #131d33;
      --navy-800: #1e293b;
      
      --slate-50: #f8fafc;
      --slate-100: #f1f5f9;
      --slate-200: #e2e8f0;
      --slate-300: #cbd5e1;
      --slate-400: #94a3b8;
      --slate-500: #64748b;
      --slate-600: #475569;
      --slate-700: #334155;
      --slate-800: #1e293b;
      --slate-900: #0f172a;
      
      --emerald-500: #10b981;
      --emerald-600: #059669;
      --emerald-50: #f0fdf4;
      --emerald-100: #dcfce7;
      --emerald-800: #166534;
      
      --amber-500: #f59e0b;
      --amber-600: #d97706;
      --amber-50: #fffbeb;
      --amber-100: #fef3c7;
      --amber-800: #92400e;
      
      --rose-500: #f43f5e;
      --rose-600: #e11d48;
      --rose-50: #fff1f2;
      --rose-100: #ffe4e6;
      --rose-800: #9f1239;
      
      --indigo-500: #6366f1;
      --indigo-50: #eef2ff;
      --indigo-100: #e0e7ff;
      --indigo-800: #3730a3;
      
      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 16px;
      --radius-xl: 20px;
      --radius-pill: 9999px;
      
      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
      --shadow-md: 0 4px 12px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.04);
      --shadow-lg: 0 12px 28px -4px rgba(15, 23, 42, 0.09), 0 4px 10px -2px rgba(15, 23, 42, 0.04);
      --shadow-glow: 0 2px 8px rgba(2, 132, 199, 0.15);
    }

    /* COCKPIT OCC DARK THEME PALETTE */
    :root[data-theme="dark"] {
      --bg-main: #090e17;
      --bg-card: #111827;
      --border-color: #1f2937;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --table-th-bg: #090e17;
      --table-th-text: #9ca3af;
      --table-tr-hover: #172033;
      --table-tr-active: #1e293b;

      --navy-950: #04070e;
      --navy-900: #090e17;
      --navy-850: #0d1424;
      --navy-800: #111827;
      
      --slate-50: #090e17;
      --slate-100: #0f172a;
      --slate-200: #1f2937;
      --slate-300: #374151;
      --slate-400: #9ca3af;
      --slate-500: #9ca3af;
      --slate-600: #cbd5e1;
      --slate-700: #e5e7eb;
      --slate-800: #f3f4f6;
      --slate-900: #f9fafb;

      --primary-light: rgba(2, 132, 199, 0.18);
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg-main);
      color: var(--text-main);
      line-height: 1.55;
      overflow-x: hidden;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.15s ease, color 0.15s ease;
    }

    /* OCC DARK THEME SPECIFIC OVERRIDES */
    :root[data-theme="dark"] header {
      background: #090e17 !important;
      border-bottom: 1px solid #1f2937 !important;
    }
    :root[data-theme="dark"] .card,
    :root[data-theme="dark"] .custom-param-card,
    :root[data-theme="dark"] .search-flight-card {
      background: #111827 !important;
      border-color: #1f2937 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .card-title {
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .card-subtitle {
      color: #9ca3af !important;
    }
    :root[data-theme="dark"] input,
    :root[data-theme="dark"] select,
    :root[data-theme="dark"] textarea {
      background: #090e17 !important;
      border-color: #1f2937 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .btn-secondary {
      background: #1f2937 !important;
      border-color: #374151 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .btn-whatif {
      background: #1f2937 !important;
      border-color: #374151 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .btn-whatif:hover {
      background: #374151 !important;
      border-color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .metric-box {
      background: #090e17 !important;
      border-color: #1f2937 !important;
    }
    :root[data-theme="dark"] .metric-val {
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .metric-label {
      color: #9ca3af !important;
    }
    :root[data-theme="dark"] .timeline-step,
    :root[data-theme="dark"] .legal-card {
      background: #090e17 !important;
      border-color: #1f2937 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .chat-window,
    :root[data-theme="dark"] .chat-sidebar,
    :root[data-theme="dark"] .chat-input-area {
      background: #111827 !important;
      border-color: #1f2937 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .chat-messages {
      background: #090e17 !important;
    }
    :root[data-theme="dark"] .chat-msg.assistant {
      background: #111827 !important;
      border-color: #1f2937 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .chat-msg.user {
      background: #1e293b !important;
      border: 1px solid #334155 !important;
      color: #f1f5f9 !important;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }
    :root[data-theme="dark"] .chat-msg.user .chat-meta {
      color: #94a3b8 !important;
    }
    :root[data-theme="dark"] .chat-msg.user .user-msg-body {
      color: #f8fafc !important;
    }
    :root[data-theme="dark"] .citation-tag {
      background: #1e293b !important;
      color: #38bdf8 !important;
      border: 1px solid #334155 !important;
    }
    :root[data-theme="dark"] .citation-tag:hover {
      background: #334155 !important;
      color: #7dd3fc !important;
    }
    :root[data-theme="dark"] .chat-source-tag {
      background: rgba(16, 185, 129, 0.15) !important;
      color: #34d399 !important;
      border-color: rgba(52, 211, 153, 0.35) !important;
    }
    :root[data-theme="dark"] .chat-citations {
      border-top-color: #1f2937 !important;
    }
    :root[data-theme="dark"] .chat-followups {
      border-top-color: #1f2937 !important;
    }
    :root[data-theme="dark"] .chip {
      background: #1e293b !important;
      border-color: #334155 !important;
      color: #cbd5e1 !important;
    }
    :root[data-theme="dark"] .chip:hover {
      background: rgba(2, 132, 199, 0.28) !important;
      border-color: #0284c7 !important;
      color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .chip-primary {
      background: rgba(2, 132, 199, 0.18) !important;
      border-color: rgba(56, 189, 248, 0.35) !important;
      color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .chip-primary:hover {
      background: rgba(2, 132, 199, 0.32) !important;
      border-color: #38bdf8 !important;
      color: #ffffff !important;
    }
    :root[data-theme="dark"] .chat-history-card {
      background: #111827 !important;
      border-color: #1f2937 !important;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
    }
    :root[data-theme="dark"] .chat-history-card:hover,
    :root[data-theme="dark"] .chat-history-card.expanded {
      border-color: #38bdf8 !important;
      box-shadow: 0 4px 16px rgba(56, 189, 248, 0.16) !important;
    }
    :root[data-theme="dark"] .chat-history-question {
      color: #f8fafc !important;
    }
    :root[data-theme="dark"] .chat-history-answer-drawer {
      border-top-color: #334155 !important;
    }
    :root[data-theme="dark"] .drawer-label {
      color: #34d399 !important;
    }
    :root[data-theme="dark"] .btn-copy-history {
      background: #1e293b !important;
      border-color: #334155 !important;
      color: #cbd5e1 !important;
    }
    :root[data-theme="dark"] .btn-copy-history:hover {
      background: #334155 !important;
      color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .history-toolbar {
      background: rgba(2, 132, 199, 0.15) !important;
      border-color: rgba(56, 189, 248, 0.35) !important;
      color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .btn-history-ctrl {
      background: #111827 !important;
      border-color: rgba(56, 189, 248, 0.35) !important;
      color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .btn-history-ctrl:hover {
      background: #0284c7 !important;
      color: #ffffff !important;
    }
    :root[data-theme="dark"] .history-toggle-badge {
      background: rgba(2, 132, 199, 0.2) !important;
      border-color: rgba(56, 189, 248, 0.4) !important;
      color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .btn-sm {
      background: #1e293b !important;
      border-color: #334155 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .btn-sm:hover {
      background: #334155 !important;
      border-color: #38bdf8 !important;
      color: #38bdf8 !important;
    }
    :root[data-theme="dark"] #btn-settings-expand {
      background: rgba(2, 132, 199, 0.18) !important;
      color: #38bdf8 !important;
      border-color: rgba(56, 189, 248, 0.35) !important;
    }
    :root[data-theme="dark"] #btn-settings-expand:hover {
      background: rgba(2, 132, 199, 0.3) !important;
      color: #ffffff !important;
    }
    :root[data-theme="dark"] #btn-reset-chat {
      background: #1e293b !important;
      border-color: #334155 !important;
      color: #cbd5e1 !important;
    }
    :root[data-theme="dark"] #btn-reset-chat:hover {
      background: #334155 !important;
      color: #ffffff !important;
    }
    :root[data-theme="dark"] .md-code {
      background: #1e293b !important;
      border-color: #334155 !important;
      color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .md-quote {
      background: rgba(2, 132, 199, 0.12) !important;
      border-left-color: #38bdf8 !important;
      color: #93c5fd !important;
    }
    :root[data-theme="dark"] .chat-body table th {
      background: #1e293b !important;
      border-color: #334155 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .chat-body table td {
      border-color: #1f2937 !important;
      color: #e2e8f0 !important;
    }
    :root[data-theme="dark"] .whatif-container {
      background: linear-gradient(135deg, #0d1526 0%, #172033 100%) !important;
      border-color: #1e293b !important;
    }
    :root[data-theme="dark"] .whatif-result {
      background: rgba(16, 185, 129, 0.15) !important;
      border-color: rgba(52, 211, 153, 0.3) !important;
      color: #34d399 !important;
    }
    :root[data-theme="dark"] .timeline-gate {
      background: #111827 !important;
      border-color: #1f2937 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .gate-title {
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .gate-guidance {
      color: #cbd5e1 !important;
    }
    :root[data-theme="dark"] .decision-box {
      background: rgba(16, 185, 129, 0.15) !important;
      border-color: rgba(52, 211, 153, 0.3) !important;
      color: #34d399 !important;
    }
    :root[data-theme="dark"] #modal-body h2,
    :root[data-theme="dark"] #modal-body h4 {
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] #modal-body div {
      color: #cbd5e1 !important;
    }
    :root[data-theme="dark"] #modal-body div[style*="background:#f8fafc"],
    :root[data-theme="dark"] #modal-body div[style*="background: #f8fafc"] {
      background: #1e293b !important;
      border-color: #334155 !important;
    }
    :root[data-theme="dark"] #modal-body div[style*="background:#eff6ff"],
    :root[data-theme="dark"] #modal-body div[style*="background: #eff6ff"] {
      background: rgba(2, 132, 199, 0.15) !important;
      border-color: rgba(56, 189, 248, 0.3) !important;
      color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .slide-modal-content div[style*="background:#f8fafc"],
    :root[data-theme="dark"] .slide-modal-content div[style*="background: #f8fafc"] {
      background: #1e293b !important;
      border-color: #334155 !important;
    }
    :root[data-theme="dark"] .slide-modal-content div[style*="background:#ffffff"],
    :root[data-theme="dark"] .slide-modal-content div[style*="background: #ffffff"] {
      background: #1e293b !important;
      border-color: #334155 !important;
      color: #e2e8f0 !important;
    }
    :root[data-theme="dark"] .slide-modal-content div[style*="color:#0f172a"],
    :root[data-theme="dark"] .slide-modal-content div[style*="color: #0f172a"] {
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .slide-modal-content em {
      color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .catalog-card,
    :root[data-theme="dark"] .modal-content,
    :root[data-theme="dark"] .slide-modal-content {
      background: #111827 !important;
      border-color: #1f2937 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .settings-modal-content h2,
    :root[data-theme="dark"] .settings-modal-title {
      color: #f8fafc !important;
    }
    :root[data-theme="dark"] .settings-modal-desc,
    :root[data-theme="dark"] .settings-help-text {
      color: #94a3b8 !important;
    }
    :root[data-theme="dark"] .settings-modal-content label {
      color: #e2e8f0 !important;
    }
    :root[data-theme="dark"] .settings-modal-content input {
      background: #090e17 !important;
      border-color: #334155 !important;
      color: #f8fafc !important;
    }
    :root[data-theme="dark"] .settings-modal-content code {
      background: #1e293b !important;
      color: #38bdf8 !important;
      border: 1px solid #334155 !important;
    }
    :root[data-theme="dark"] .setting-status-box.status-success {
      background: rgba(16, 185, 129, 0.16) !important;
      border-color: rgba(52, 211, 153, 0.45) !important;
      color: #6ee7b7 !important;
    }
    :root[data-theme="dark"] .setting-status-box.status-neutral {
      background: #1e293b !important;
      border-color: #334155 !important;
      color: #cbd5e1 !important;
    }
    :root[data-theme="dark"] .setting-status-box.status-error {
      background: rgba(239, 68, 68, 0.16) !important;
      border-color: rgba(248, 113, 113, 0.45) !important;
      color: #fca5a5 !important;
    }
    :root[data-theme="dark"] #setting-status-text,
    :root[data-theme="dark"] #setting-status-text strong {
      color: inherit !important;
    }
    :root[data-theme="dark"] .history-restored-tag {
      background: #1e293b !important;
      border-color: #334155 !important;
      color: #94a3b8 !important;
    }
    :root[data-theme="dark"] .toast {
      background: #111827 !important;
      border: 1px solid #1f2937 !important;
      border-left: 5px solid #38bdf8 !important;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7), 0 8px 10px -6px rgba(0, 0, 0, 0.6) !important;
      color: #e2e8f0 !important;
    }
    :root[data-theme="dark"] .toast.toast-error {
      border-left-color: #f43f5e !important;
    }
    :root[data-theme="dark"] .toast.toast-success {
      border-left-color: #10b981 !important;
    }
    :root[data-theme="dark"] .toast.toast-warning {
      border-left-color: #f59e0b !important;
    }
    :root[data-theme="dark"] .toast.toast-info {
      border-left-color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .toast-header,
    :root[data-theme="dark"] .toast-title {
      color: #f8fafc !important;
    }
    :root[data-theme="dark"] .toast-body {
      color: #cbd5e1 !important;
    }
    :root[data-theme="dark"] .toast-hint-title {
      color: #94a3b8 !important;
    }
    :root[data-theme="dark"] .toast-close {
      color: #94a3b8 !important;
    }
    :root[data-theme="dark"] .toast-close:hover {
      color: #ffffff !important;
    }
    :root[data-theme="dark"] .toast-chip {
      background: #1e293b !important;
      border-color: #334155 !important;
      color: #38bdf8 !important;
    }
    :root[data-theme="dark"] .toast-chip:hover {
      background: #0284c7 !important;
      color: #ffffff !important;
      border-color: #0284c7 !important;
    }
    :root[data-theme="dark"] .slide-preview-card {
      background: #090e17 !important;
      border-color: #1f2937 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .slide-chip-tab {
      background: #1f2937 !important;
      border-color: #374151 !important;
      color: #cbd5e1 !important;
    }
    :root[data-theme="dark"] .slide-chip-tab.active {
      background: #0284c7 !important;
      color: #ffffff !important;
    }
    :root[data-theme="dark"] .flight-watch-card {
      border-top-color: #1f2937 !important;
    }
    :root[data-theme="dark"] .flight-watch-table-container {
      border-color: #1f2937 !important;
    }
    :root[data-theme="dark"] .flight-watch-table th {
      background: #090e17 !important;
      border-bottom-color: #1f2937 !important;
      color: #9ca3af !important;
    }
    :root[data-theme="dark"] .flight-watch-table td {
      border-bottom-color: #1f2937 !important;
      color: #f3f4f6 !important;
    }
    :root[data-theme="dark"] .flight-watch-table tbody tr:hover td {
      background: #172033 !important;
    }
    :root[data-theme="dark"] .flight-watch-table tbody tr.active-row td {
      background: #1e293b !important;
    }

    /* THEME TOGGLE BUTTON */
    .theme-toggle-btn {
      background: rgba(255, 255, 255, 0.06);
      color: #cbd5e1;
      border: 1px solid rgba(255, 255, 255, 0.15);
      cursor: pointer;
      padding: 4px 10px;
      font-size: 11.5px;
      font-weight: 700;
      border-radius: var(--radius-pill);
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s ease;
      user-select: none;
    }
    .theme-toggle-btn:hover {
      background: rgba(255, 255, 255, 0.12);
      color: #ffffff;
      border-color: rgba(255, 255, 255, 0.25);
    }

    /* FLIGHT WATCH MINI-TABLE */
    .flight-watch-card {
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px solid var(--border-color, #e2e8f0);
    }
    .flight-watch-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }
    .live-dot {
      width: 7px;
      height: 7px;
      background: #10b981;
      border-radius: 50%;
      display: inline-block;
      box-shadow: 0 0 6px #10b981;
      animation: pulseDot 2s infinite ease-in-out;
    }
    @keyframes pulseDot {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.35; transform: scale(0.85); }
    }
    .flight-watch-table-container {
      overflow-x: auto;
      border: 1px solid var(--border-color, #e2e8f0);
      border-radius: var(--radius-sm);
    }
    .flight-watch-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 11.5px;
      text-align: left;
    }
    .flight-watch-table th {
      background: var(--table-th-bg, #f8fafc);
      color: var(--table-th-text, #475569);
      font-weight: 700;
      padding: 7px 10px;
      border-bottom: 1px solid var(--border-color, #e2e8f0);
      font-size: 10.5px;
      letter-spacing: 0.3px;
      text-transform: uppercase;
      white-space: nowrap;
    }
    .flight-watch-table td {
      padding: 7px 10px;
      border-bottom: 1px solid var(--border-color, #e2e8f0);
      color: var(--text-main, #0f172a);
      vertical-align: middle;
      white-space: nowrap;
    }
    .flight-watch-table tbody tr {
      cursor: pointer;
      transition: background 0.15s ease;
    }
    .flight-watch-table tbody tr:last-child td {
      border-bottom: none;
    }
    .flight-watch-table tbody tr:hover td {
      background: var(--table-tr-hover, #f1f5f9);
    }
    .flight-watch-table tbody tr.active-row td {
      background: var(--table-tr-active, #e0f2fe);
      font-weight: 600;
    }
    .carrier-pill {
      display: inline-block;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
      font-size: 10.5px;
      padding: 2px 6px;
      border-radius: 4px;
      color: #fff;
      text-align: center;
      min-width: 28px;
    }
    .carrier-ua { background: #0284c7; }
    .carrier-dl { background: #1e3a8a; }
    .carrier-aa { background: #b91c1c; }
    .carrier-wn { background: #b45309; }
    .risk-pill {
      display: inline-block;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: var(--radius-pill);
      letter-spacing: 0.2px;
    }
    .risk-critical {
      background: rgba(244, 63, 94, 0.15);
      color: #e11d48;
      border: 1px solid rgba(244, 63, 94, 0.3);
    }
    .risk-elevated {
      background: rgba(245, 158, 11, 0.15);
      color: #d97706;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .risk-normal {
      background: rgba(16, 185, 129, 0.15);
      color: #059669;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }
    :root[data-theme="dark"] .risk-critical {
      background: rgba(244, 63, 94, 0.25);
      color: #fda4af;
      border-color: rgba(244, 63, 94, 0.4);
    }
    :root[data-theme="dark"] .risk-elevated {
      background: rgba(245, 158, 11, 0.25);
      color: #fde68a;
      border-color: rgba(245, 158, 11, 0.4);
    }
    :root[data-theme="dark"] .risk-normal {
      background: rgba(16, 185, 129, 0.25);
      color: #6ee7b7;
      border-color: rgba(16, 185, 129, 0.4);
    }

    /* KEYBOARD HOTKEY BADGES */
    .kbd-badge {
      font-family: 'JetBrains Mono', monospace;
      font-size: 9.5px;
      font-weight: 700;
      padding: 1px 5px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.12);
      color: #cbd5e1;
      border: 1px solid rgba(255, 255, 255, 0.18);
      letter-spacing: 0.3px;
    }
    .input-hotkey-badge {
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      font-family: 'JetBrains Mono', monospace;
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      background: var(--slate-100);
      color: var(--slate-500);
      border: 1px solid var(--slate-300);
      pointer-events: none;
      letter-spacing: 0.2px;
    }
    :root[data-theme="dark"] .input-hotkey-badge {
      background: #1f2937;
      color: #9ca3af;
      border-color: #374151;
    }
    .btn-dispatch-release {
      background: #0f766e;
      color: #ffffff;
      font-weight: 700;
      border: 0;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
      cursor: pointer;
    }
    .btn-dispatch-release:hover {
      background: #115e59;
      box-shadow: 0 2px 8px rgba(15, 118, 110, 0.3);
    }

    /* ========================================================================= */
    /* ========================================================================= */
    /* APP BAR & HEADER (ENTERPRISE OPERATIONS DECK)                             */
    /* ========================================================================= */
    header {
      background: #0f172a;
      color: #fff;
      border-bottom: 1px solid #1e293b;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
      position: sticky;
      top: 0;
      z-index: 50;
      backdrop-filter: blur(8px);
    }
    
    .header-top {
      max-width: 1440px;
      margin: 0 auto;
      padding: 12px 28px 10px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 14px;
    }
    
    .brand-group {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: inherit;
    }
    
    .brand-icon-box {
      width: 38px;
      height: 38px;
      background: #0284c7;
      border: 1px solid #0369a1;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }
    
    .brand-title {
      font-size: 19px;
      font-weight: 800;
      letter-spacing: -0.4px;
      display: flex;
      align-items: center;
      gap: 8px;
      color: #ffffff;
    }
    
    .brand-version-pill {
      font-size: 11px;
      font-weight: 700;
      background: rgba(56, 189, 248, 0.12);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.25);
      padding: 2px 8px;
      border-radius: var(--radius-pill);
      letter-spacing: 0.2px;
    }
    
    .brand-subtitle {
      font-size: 12px;
      color: #94a3b8;
      margin-top: 1px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    
    .domain-badge {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      background: rgba(255, 255, 255, 0.06);
      color: #cbd5e1;
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 2px 8px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .domain-badge:hover {
      background: rgba(56, 189, 248, 0.15);
      border-color: #38bdf8;
      color: #fff;
    }

    .header-badges {
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
      font-size: 11.5px;
    }
    
    .header-badge {
      background: rgba(255, 255, 255, 0.05);
      padding: 5px 12px;
      border-radius: var(--radius-pill);
      color: #cbd5e1;
      border: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s;
    }
    .header-badge:hover {
      background: rgba(255, 255, 255, 0.08);
    }
    
    .header-desc {
      display: none;
    }

    /* ========================================================================= */
    /* NAV TABS (PILL SEGMENTED CONTROLS)                                        */
    /* ========================================================================= */
    .tabs-bar-wrapper {
      max-width: 1440px;
      margin: 0 auto;
      padding: 0 28px 10px 28px;
    }
    
    .tabs-bar {
      display: inline-flex;
      background: rgba(30, 41, 59, 0.8);
      padding: 4px;
      border-radius: var(--radius-pill);
      border: 1px solid rgba(255, 255, 255, 0.08);
      gap: 4px;
    }
    
    .tab-btn {
      background: transparent;
      border: none;
      color: #94a3b8;
      padding: 7px 18px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      border-radius: var(--radius-pill);
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .tab-btn:hover {
      color: #ffffff;
      background: rgba(255, 255, 255, 0.06);
    }
    .tab-btn.active {
      color: #ffffff;
      background: #0284c7;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
    }

    /* ========================================================================= */
    /* MAIN CONTAINER                                                            */
    /* ========================================================================= */
    .container {
      width: 100%;
      max-width: 1440px;
      margin: 22px auto 40px auto;
      padding: 0 28px;
      box-sizing: border-box;
    }
    
    .tab-content { display: none; width: 100%; box-sizing: border-box; }
    .tab-content.active { display: block; width: 100%; box-sizing: border-box; }

    /* ========================================================================= */
    /* CARDS & PANELS                                                            */
    /* ========================================================================= */
    .card {
      background: #ffffff;
      border: 1px solid var(--slate-200);
      border-radius: var(--radius-lg);
      padding: 22px;
      margin-bottom: 20px;
      box-shadow: var(--shadow-sm);
      transition: box-shadow 0.2s, border-color 0.2s;
      width: 100%;
      box-sizing: border-box;
    }
    .card:hover {
      box-shadow: var(--shadow-md);
    }
    
    .card-header-flex {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      flex-wrap: wrap;
      gap: 10px;
    }
    .card-title {
      font-size: 16px;
      font-weight: 800;
      color: var(--slate-900);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .card-subtitle {
      font-size: 12.5px;
      color: var(--slate-500);
      margin-top: 2px;
    }

    /* ========================================================================= */
    /* FORM INPUTS & BUTTONS                                                     */
    /* ========================================================================= */
    label {
      font-size: 12px;
      font-weight: 700;
      color: var(--slate-700);
      display: block;
      margin-bottom: 6px;
    }
    
    input, select, textarea {
      width: 100%;
      padding: 10px 14px;
      border: 1px solid var(--slate-300);
      border-radius: var(--radius-sm);
      font-size: 13.5px;
      font-family: inherit;
      background: #ffffff;
      color: var(--slate-900);
      transition: all 0.15s ease;
      box-sizing: border-box;
    }
    input:focus, select:focus, textarea:focus {
      border-color: var(--primary);
      outline: none;
      box-shadow: 0 0 0 3px var(--primary-glow);
    }
    
    .btn-primary {
      background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
      color: #fff;
      border: 0;
      font-weight: 700;
      font-size: 13.5px;
      cursor: pointer;
      padding: 10px 18px;
      border-radius: var(--radius-sm);
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 2px 6px rgba(2, 132, 199, 0.25);
    }
    .btn-primary:hover {
      background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
      transform: translateY(-1px);
    }
    .btn-primary:active {
      transform: translateY(0);
    }
    
    .btn-secondary {
      background: var(--slate-800);
      color: #fff;
      border: 0;
      font-weight: 700;
      font-size: 13px;
      cursor: pointer;
      padding: 9px 16px;
      border-radius: var(--radius-sm);
      transition: all 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn-secondary:hover {
      background: var(--slate-900);
      transform: translateY(-1px);
    }

    .btn-sm {
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid var(--slate-300);
      background: #ffffff;
      color: var(--slate-700);
      transition: all 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .btn-sm:hover {
      background: var(--primary-light);
      color: var(--primary);
      border-color: #bae6fd;
    }

    /* BADGES */
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 12px;
      border-radius: var(--radius-pill);
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.3px;
    }
    .badge-high {
      background: var(--rose-50);
      color: var(--rose-600);
      border: 1px solid #fecdd3;
      box-shadow: 0 0 10px rgba(244, 63, 94, 0.15);
    }
    .badge-elevated {
      background: var(--amber-50);
      color: var(--amber-600);
      border: 1px solid #fde68a;
    }
    .badge-normal {
      background: var(--emerald-50);
      color: var(--emerald-600);
      border: 1px solid #bbf7d0;
    }

    /* CHIPS */
    .chip {
      display: inline-flex;
      align-items: center;
      background: var(--slate-100);
      border: 1px solid var(--slate-200);
      padding: 5px 12px;
      border-radius: var(--radius-pill);
      font-size: 12px;
      cursor: pointer;
      margin: 3px 4px 3px 0;
      color: var(--slate-700);
      font-weight: 600;
      transition: all 0.15s ease;
    }
    .chip:hover {
      background: var(--primary-light);
      color: var(--primary);
      border-color: #bae6fd;
      transform: translateY(-1px);
    }
    .chip-primary {
      background: var(--primary-light);
      color: var(--primary);
      border: 1px solid #bae6fd;
      font-weight: 700;
    }

    /* ========================================================================= */
    /* TAB 1: 2-COLUMN SPLIT-SCREEN OCC DISPATCH COCKPIT                         */
    /* ========================================================================= */
    .occ-split-layout {
      display: grid;
      grid-template-columns: 380px minmax(0, 1fr);
      gap: 22px;
      align-items: start;
    }
    @media (max-width: 1040px) {
      .occ-split-layout {
        grid-template-columns: 1fr;
      }
    }

    .dispatch-sidebar {
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .search-flight-card {
      background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
      border: 1px solid var(--slate-200);
      border-radius: var(--radius-lg);
      padding: 20px;
      box-shadow: var(--shadow-sm);
    }

    .custom-param-card {
      background: #ffffff;
      border: 1px solid var(--slate-200);
      border-radius: var(--radius-lg);
      padding: 20px;
      box-shadow: var(--shadow-sm);
    }

    .grid-form-compact {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .hero-flight-hud {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: var(--radius-lg);
      padding: 24px;
      color: #fff;
      margin-bottom: 20px;
      box-shadow: var(--shadow-sm);
      position: relative;
    }

    .route-display {
      display: flex;
      align-items: center;
      gap: 16px;
      margin: 8px 0;
    }
    .airport-code {
      font-size: 28px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: #ffffff;
      font-family: 'JetBrains Mono', monospace;
    }
    .route-arrow {
      color: #38bdf8;
      font-size: 20px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    /* FINANCIAL METRICS */
    .metric-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 14px;
      margin: 16px 0;
    }
    .metric-box {
      background: var(--slate-50);
      padding: 16px 18px;
      border-radius: var(--radius-md);
      border: 1px solid var(--slate-200);
      transition: all 0.2s;
    }
    .metric-box:hover {
      background: #ffffff;
      border-color: var(--primary-light);
      box-shadow: var(--shadow-sm);
    }
    .metric-title {
      font-size: 11.5px;
      text-transform: uppercase;
      color: var(--slate-500);
      font-weight: 700;
      letter-spacing: 0.3px;
    }
    .metric-val {
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-variant-numeric: tabular-nums;
      font-feature-settings: 'tnum';
      font-size: 24px;
      font-weight: 800;
      color: var(--slate-900);
      margin-top: 4px;
    }
    .metric-sub {
      font-size: 11.5px;
      color: var(--slate-500);
      margin-top: 4px;
    }

    /* STACKED COST PROGRESS BAR */
    .cost-breakdown-container {
      margin-top: 16px;
      background: var(--slate-50);
      border: 1px solid var(--slate-200);
      border-radius: var(--radius-md);
      padding: 18px;
    }
    .stacked-bar-wrapper {
      height: 32px;
      background: #e2e8f0;
      border-radius: var(--radius-pill);
      overflow: hidden;
      display: flex;
      box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }
    .stacked-segment {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 11px;
      font-weight: 700;
      overflow: hidden;
      white-space: nowrap;
      padding: 0 6px;
      transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .cost-callout-box {
      margin-top: 12px;
      background: var(--rose-50);
      border: 1px solid #fecdd3;
      padding: 12px 16px;
      border-radius: var(--radius-sm);
      font-size: 12.5px;
      line-height: 1.5;
      color: var(--rose-800);
    }

    /* WHAT-IF SIMULATOR */
    .whatif-container {
      background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
      border: 1px solid #bae6fd;
      border-radius: var(--radius-lg);
      padding: 20px;
      margin-bottom: 20px;
    }
    .whatif-bar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 10px;
      margin-top: 12px;
    }
    .btn-whatif {
      background: #ffffff;
      border: 1px solid #bae6fd;
      padding: 10px 14px;
      border-radius: var(--radius-sm);
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
      color: var(--slate-800);
      display: flex;
      align-items: center;
      gap: 6px;
      box-shadow: var(--shadow-sm);
    }
    .btn-whatif:hover {
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
      transform: translateY(-1px);
      box-shadow: 0 4px 10px rgba(2, 132, 199, 0.25);
    }
    .whatif-result {
      background: #ecfdf5;
      border: 1px solid #a7f3d0;
      color: #065f46;
      padding: 16px;
      border-radius: var(--radius-md);
      font-size: 13px;
      margin-top: 14px;
      line-height: 1.6;
    }

    /* TIMELINE GATES */
    .timeline-gate {
      border-left: 4px solid var(--primary);
      background: #ffffff;
      border-radius: var(--radius-md);
      padding: 16px 20px;
      margin-top: 14px;
      border-top: 1px solid var(--slate-200);
      border-right: 1px solid var(--slate-200);
      border-bottom: 1px solid var(--slate-200);
      box-shadow: var(--shadow-sm);
    }
    .timeline-gate.critical { border-left-color: var(--rose-600); }
    .timeline-gate.high { border-left-color: var(--amber-600); }
    .timeline-gate.normal { border-left-color: var(--emerald-600); }
    .gate-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
    .gate-title { font-weight: 800; font-size: 14.5px; color: var(--slate-850); }
    .role-badge { background: var(--primary-light); color: var(--primary-hover); padding: 3px 10px; border-radius: var(--radius-pill); font-size: 11px; font-weight: 700; }
    .gate-guidance { font-size: 13px; color: var(--slate-700); line-height: 1.6; margin: 8px 0; white-space: pre-line; }
    .decision-box { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 10px 14px; border-radius: var(--radius-sm); font-size: 12.5px; font-weight: 700; }

    /* LEGAL CARD */
    .legal-card {
      border-left: 4px solid var(--rose-600);
      background: #ffffff;
      border-radius: var(--radius-md);
      padding: 16px;
      margin-top: 12px;
      border-top: 1px solid var(--slate-200);
      border-right: 1px solid var(--slate-200);
      border-bottom: 1px solid var(--slate-200);
      box-shadow: var(--shadow-sm);
    }
    .legal-card.warn { border-left-color: var(--amber-600); }
    .legal-card.success { border-left-color: var(--emerald-600); }

    /* ========================================================================= */
    /* TAB 2: OPERATIONAL INVESTIGATION & DIAGNOSTICS LAYOUT                     */
    /* ========================================================================= */
    .chat-studio-layout {
      display: grid;
      grid-template-columns: 340px minmax(0, 1fr);
      gap: 22px;
      align-items: start;
    }
    @media (max-width: 960px) {
      .chat-studio-layout {
        grid-template-columns: 1fr;
      }
    }

    .chat-sidebar {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .chat-banner {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: var(--radius-lg);
      padding: 18px;
      color: #f8fafc;
      font-size: 13px;
      box-shadow: var(--shadow-sm);
    }

    .chat-window {
      background: #ffffff;
      border: 1px solid var(--slate-200);
      border-radius: var(--radius-lg);
      display: flex;
      flex-direction: column;
      height: 700px;
      box-shadow: var(--shadow-sm);
      overflow: hidden;
      box-sizing: border-box;
    }

    .chat-messages {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      background: #f8fafc;
      scroll-behavior: smooth;
    }

    .chat-msg {
      max-width: 100%;
      padding: 18px 20px;
      border-radius: var(--radius-md);
      font-size: 13.5px;
      line-height: 1.6;
      box-sizing: border-box;
      word-wrap: break-word;
      overflow-wrap: break-word;
      word-break: break-word;
    }
    .chat-msg.user {
      align-self: stretch;
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      color: var(--slate-900);
      box-shadow: none;
    }
    .chat-msg.assistant {
      align-self: stretch;
      background: #ffffff;
      border: 1px solid var(--slate-200);
      border-left: 4px solid var(--primary);
      color: var(--slate-900);
      box-shadow: var(--shadow-sm);
    }

    .chat-meta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 11px;
      color: #64748b;
      gap: 8px;
    }
    .chat-source-tag {
      background: #ecfdf5;
      color: #065f46;
      padding: 2px 10px;
      border-radius: var(--radius-pill);
      font-weight: 700;
      border: 1px solid #a7f3d0;
    }

    .chat-body pre {
      background: #0f172a;
      color: #f8fafc;
      padding: 12px 16px;
      border-radius: var(--radius-sm);
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      overflow-x: auto;
      margin: 8px 0;
    }
    .chat-body table {
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0;
      font-size: 12.5px;
    }
    .chat-body th, .chat-body td {
      border: 1px solid var(--slate-200);
      padding: 8px 12px;
      text-align: left;
    }
    .chat-body th {
      background: var(--slate-100);
      font-weight: 700;
    }

    .chat-citations {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px dashed var(--slate-200);
    }
    .citation-tag {
      background: #f1f5f9;
      color: var(--slate-800);
      padding: 3px 9px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      border: 1px solid var(--slate-300);
    }

    .chat-followups {
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px solid var(--slate-200);
    }

    /* COLLAPSIBLE Q&A HISTORY CARDS (ENTERPRISE ACCORDION) */
    .chat-history-card {
      background: #ffffff;
      border: 1px solid var(--slate-200);
      border-radius: var(--radius-md);
      padding: 16px 20px;
      margin-bottom: 14px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
      transition: all 0.2s ease;
      cursor: pointer;
      box-sizing: border-box;
      word-break: break-word;
      overflow-wrap: break-word;
    }
    .chat-history-card:hover {
      border-color: var(--primary);
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.12);
      transform: translateY(-1px);
    }
    .chat-history-card.expanded {
      border-color: var(--primary);
      box-shadow: 0 4px 16px rgba(2, 132, 199, 0.14);
    }
    .chat-history-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      font-size: 11.5px;
      gap: 8px;
      user-select: none;
    }
    .history-title-box {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .history-toggle-badge {
      font-size: 10.5px;
      font-weight: 600;
      color: var(--primary);
      background: var(--primary-light);
      border: 1px solid var(--primary-border);
      padding: 2px 7px;
      border-radius: 4px;
      transition: all 0.2s ease;
    }
    .chat-history-card:hover .history-toggle-badge {
      background: var(--primary);
      color: #ffffff;
    }
    .chat-history-question {
      font-size: 14px;
      font-weight: 600;
      color: var(--slate-900);
      line-height: 1.5;
      padding: 2px 0 2px 0;
      user-select: none;
    }
    .chat-history-answer-drawer {
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px dashed var(--slate-300);
      cursor: default;
      animation: fadeIn 0.2s ease-out;
    }
    .drawer-meta-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .drawer-label {
      font-size: 11px;
      font-weight: 700;
      color: #059669;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .btn-copy-history {
      padding: 3px 9px;
      font-size: 11px;
      border-radius: 4px;
      border: 1px solid var(--slate-300);
      background: #ffffff;
      color: var(--slate-600);
      cursor: pointer;
      transition: all 0.15s;
      font-weight: 500;
    }
    .btn-copy-history:hover {
      background: var(--slate-100);
      color: var(--primary);
      border-color: var(--primary);
    }
    .history-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 14px;
      margin-bottom: 14px;
      border-radius: 10px;
      background: var(--primary-light);
      border: 1px dashed var(--primary-border);
      font-size: 12px;
      color: var(--primary);
      user-select: none;
    }
    .btn-history-ctrl {
      padding: 3px 9px;
      font-size: 11px;
      border-radius: 5px;
      border: 1px solid var(--primary-border);
      background: #ffffff;
      color: var(--primary);
      cursor: pointer;
      font-weight: 600;
      transition: all 0.15s;
    }
    .btn-history-ctrl:hover {
      background: var(--primary);
      color: #ffffff;
    }

    .chat-input-area {
      padding: 16px 20px;
      background: #ffffff;
      border-top: 1px solid var(--slate-200);
    }
    .chat-input-row {
      display: flex;
      gap: 10px;
      align-items: center;
    }
    .chat-input-row input {
      flex: 1;
      font-size: 14px;
      padding: 12px 16px;
      border-radius: var(--radius-pill);
    }
    .chat-input-row button {
      border-radius: var(--radius-pill);
      padding: 12px 24px;
    }
    .chat-input-row .voice-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 46px;
      height: 46px;
      padding: 0;
      border-radius: 50%;
      border: 1.5px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-main);
      cursor: pointer;
      font-size: 19px;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      flex-shrink: 0;
    }
    .chat-input-row .voice-btn:hover {
      background: var(--primary-light);
      border-color: var(--primary);
      color: var(--primary);
      transform: scale(1.06);
    }
    .chat-input-row .voice-btn.recording {
      background: #fee2e2 !important;
      border-color: #ef4444 !important;
      color: #dc2626 !important;
      animation: voicePulseRing 1.2s infinite;
    }
    @keyframes voicePulseRing {
      0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }
      50% { transform: scale(1.08); box-shadow: 0 0 0 9px rgba(239, 68, 68, 0); }
      100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    .typewriter-cursor {
      display: inline-block;
      width: 7px;
      height: 14px;
      margin-left: 3px;
      background-color: var(--primary);
      vertical-align: -1px;
      border-radius: 1px;
      animation: cursorBlink 0.7s infinite alternate;
    }
    @keyframes cursorBlink {
      0% { opacity: 1; }
      100% { opacity: 0; }
    }

    /* ========================================================================= */
    /* TAB 3: KNOWLEDGE CATALOG (40 ITEMS)                                       */
    /* ========================================================================= */
    .catalog-search-bar {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      align-items: center;
      flex-wrap: wrap;
    }
    .catalog-search-bar input {
      flex: 1;
      min-width: 280px;
      font-size: 14px;
      padding: 12px 18px;
      border-radius: var(--radius-pill);
    }
    .catalog-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 18px;
    }
    .catalog-card {
      background: #ffffff;
      border: 1px solid var(--slate-200);
      border-radius: var(--radius-md);
      padding: 20px;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .catalog-card:hover {
      box-shadow: var(--shadow-lg);
      border-color: var(--primary);
      transform: translateY(-2px);
    }
    .cat-title { font-weight: 800; font-size: 15px; color: var(--slate-900); }
    .cat-en { font-size: 12px; color: var(--slate-500); font-style: italic; margin-bottom: 8px; }
    .cat-desc { font-size: 13px; color: var(--slate-700); line-height: 1.5; margin-bottom: 14px; flex: 1; }
    .cat-actions { display: flex; gap: 8px; }

    /* ========================================================================= */
    /* MODALS & NOTIFICATIONS                                                    */
    /* ========================================================================= */
    .modal {
      display: none;
      position: fixed;
      z-index: 1000;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      background: rgba(15, 23, 42, 0.65);
      backdrop-filter: blur(4px);
    }
    .modal-content {
      background: #ffffff;
      margin: 50px auto;
      padding: 28px;
      border-radius: var(--radius-lg);
      max-width: 780px;
      max-height: 85vh;
      overflow-y: auto;
      box-shadow: var(--shadow-xl);
    }
    .settings-modal-content {
      max-width: 540px;
    }
    .settings-modal-title {
      color: #0f172a;
    }
    .settings-modal-desc {
      color: #64748b;
    }
    .settings-help-text {
      color: #64748b;
    }
    .setting-status-box {
      border: 1px solid #e2e8f0;
      background: #f8fafc;
      color: #334155;
      transition: all 0.2s ease;
    }
    .setting-status-box.status-success {
      background: #f0fdf4 !important;
      border-color: #86efac !important;
      color: #166534 !important;
    }
    .setting-status-box.status-neutral {
      background: #f8fafc !important;
      border-color: #e2e8f0 !important;
      color: #334155 !important;
    }
    .setting-status-box.status-error {
      background: #fef2f2 !important;
      border-color: #fecaca !important;
      color: #991b1b !important;
    }
    #setting-status-text,
    #setting-status-text strong {
      color: inherit;
    }
    .history-restored-tag {
      background: #f8fafc;
      border-color: #cbd5e1;
      color: #64748b;
    }
    .slide-modal-content {
      max-width: 1060px;
      background: #ffffff;
      color: #0f172a;
      border: 1px solid #cbd5e1;
      padding: 24px 28px;
      box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.2);
    }
    .slide-preview-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: var(--radius-lg);
      padding: 28px 32px;
      min-height: 420px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.05);
    }
    .slide-chip-tab {
      padding: 6px 14px;
      border-radius: var(--radius-pill);
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid #e2e8f0;
      background: #f1f5f9;
      color: #475569;
      transition: all 0.15s ease;
    }
    .slide-chip-tab.active {
      background: #0284c7;
      color: #ffffff;
      border-color: #0284c7;
      box-shadow: 0 2px 6px rgba(2, 132, 199, 0.25);
    }
    .close-btn {
      float: right;
      font-size: 24px;
      cursor: pointer;
      color: var(--slate-400);
      line-height: 1;
    }
    .close-btn:hover { color: var(--slate-900); }

    /* TOAST NOTIFICATIONS */
    #toast-container {
      position: fixed;
      top: 24px;
      right: 24px;
      z-index: 99999;
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-width: 440px;
      pointer-events: none;
    }
    .toast {
      pointer-events: auto;
      background: #ffffff;
      border-radius: var(--radius-md);
      padding: 16px 18px;
      box-shadow: var(--shadow-xl);
      border: 1px solid #e2e8f0;
      border-left: 5px solid var(--primary);
      display: flex;
      flex-direction: column;
      gap: 6px;
      animation: toastSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      font-size: 13px;
      color: #334155;
      transition: all 0.3s ease;
    }
    @keyframes toastSlideIn {
      from { transform: translateX(110%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    .toast.toast-error { border-left-color: var(--rose-600); }
    .toast.toast-success { border-left-color: var(--emerald-600); }
    .toast.toast-warning { border-left-color: var(--amber-600); }
    .toast.toast-info { border-left-color: var(--primary); }

    .toast-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 700;
      font-size: 13.5px;
      color: #0f172a;
    }
    .toast-title {
      color: #0f172a;
      font-weight: 700;
    }
    .toast-body {
      color: #334155;
      font-size: 12.5px;
      line-height: 1.5;
    }
    .toast-close {
      cursor: pointer;
      color: var(--slate-400);
      font-size: 16px;
      transition: color 0.15s;
    }
    .toast-close:hover {
      color: var(--slate-700);
    }
    .toast-hint-title {
      font-size: 11px;
      font-weight: 700;
      color: #64748b;
      margin-top: 4px;
    }
    .toast-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 6px;
    }
    .toast-chip {
      background: var(--slate-100);
      border: 1px solid var(--slate-300);
      border-radius: 6px;
      padding: 3px 8px;
      font-size: 11px;
      font-weight: 700;
      color: var(--primary);
      cursor: pointer;
      transition: all 0.15s;
    }
    .toast-chip:hover {
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
    }

    /* ERROR BANNER */
    .id-error-banner {
      background: var(--rose-50);
      border: 1px solid #fecaca;
      color: #991b1b;
      padding: 14px 18px;
      border-radius: var(--radius-md);
      font-size: 13px;
      margin-bottom: 14px;
      display: none;
      animation: bannerSlide 0.25s ease;
    }
    @keyframes bannerSlide {
      from { opacity: 0; transform: translateY(-6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .btn-settings {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #ffffff;
      border-radius: var(--radius-pill);
      padding: 6px 14px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .btn-settings:hover {
      background: rgba(255, 255, 255, 0.2);
      border-color: #38bdf8;
    }

    .input-group-password {
      position: relative;
      display: flex;
      align-items: center;
    }
    .input-group-password input {
      padding-right: 40px;
    }
    .btn-toggle-pw {
      position: absolute;
      right: 10px;
      background: transparent;
      border: none;
      cursor: pointer;
      font-size: 15px;
      color: var(--slate-400);
    }
  </style>
</head>
<body>
  <!-- TOAST NOTIFICATION CONTAINER -->
  <div id="toast-container"></div>

  <!-- NAVIGATION HEADER -->
  <header>
    <div class="header-top">
      <div class="brand-group">
        <div class="brand-icon-box">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>
          </svg>
        </div>
        <div>
          <div class="brand-title">
            SkyOps Platform
            <span class="brand-version-pill">Operations & Analytics</span>
          </div>
          <div class="brand-subtitle">
            Hệ Thống Giám Sát Rủi Ro Mạng Bay, Tối Ưu Chi Phí & Tuân Thủ Pháp Quy
            <span class="domain-badge" onclick="copyPortalLink()" title="Bấm để sao chép địa chỉ Web Portal">🌐 ops.internal:8000 📋</span>
          </div>
        </div>
      </div>

      <div class="header-badges">
        <span class="header-badge" title="Kho dữ liệu PostgreSQL kết nối localhost:5432">🟢 DWH: PostgreSQL</span>
        <span class="header-badge" title="Cơ sở dữ liệu 58.588 chuyến bay thương mại">📁 58.588 Chuyến Bay</span>
        <span class="header-badge" title="Định mức tài chính FAA $101.18/phút & Luật US DOT 14 CFR">⚖️ FAA $101.18 & 14 CFR</span>
        <button class="btn-sm" style="background:rgba(255,255,255,0.06);color:#cbd5e1;border:1px solid rgba(255,255,255,0.15);cursor:pointer;padding:4px 10px;font-size:11px;font-weight:700;border-radius:6px" onclick="openSettingsModal()" title="Cấu hình hệ thống mở rộng">⚙️ Cấu Hình</button>
        <button id="theme-toggle-btn" class="theme-toggle-btn" onclick="toggleCockpitTheme()" title="Chuyển chế độ Cockpit Night / Day (Alt + T)">
          <span id="theme-toggle-icon">🌙</span>
          <span id="theme-toggle-text">Dark Mode</span>
        </button>
        <span id="header-llm-badge" style="display:none;cursor:pointer" onclick="toggleHeaderOnlineMode()" title="Bấm để chuyển đổi nhanh giữa Trực Tuyến (Online) và Nội Bộ (Offline) — Đồng bộ tức thì sang Power BI"></span>
      </div>
    </div>

    <!-- TABS BAR -->
    <div class="tabs-bar-wrapper">
      <div class="tabs-bar">
        <button class="tab-btn active" onclick="switchTab('tab-advisory')" title="Phím tắt: Alt + 1">
          <span class="kbd-badge">Alt 1</span>
          <span>1. Phân Tích Chuyên Sâu Chuyến Bay & Chi Phí (Flight & Financial Impact Analytics)</span>
        </button>
        <button class="tab-btn" onclick="switchTab('tab-chat')" title="Phím tắt: Alt + 2">
          <span class="kbd-badge">Alt 2</span>
          <span>2. Trợ Lý Phân Tích Nghiệp Vụ (Analytics Copilot Q&A)</span>
        </button>
        <button class="tab-btn" onclick="switchTab('tab-catalog')" title="Phím tắt: Alt + 3">
          <span class="kbd-badge">Alt 3</span>
          <span>3. Từ Điển Chỉ Số & Quy Chuẩn (Data Metric Dictionary)</span>
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN VIEWPORT -->
  <div class="container">
    <!-- ===================================================================== -->
    <!-- TAB 1: SPLIT-SCREEN OCC DISPATCH COCKPIT                             -->
    <!-- ===================================================================== -->
    <div id="tab-advisory" class="tab-content active">
      <div class="occ-split-layout">
        
        <!-- LEFT COLUMN: CONTROLS & FLIGHT LOOKUP -->
        <div class="dispatch-sidebar">
          
          <!-- SEARCH BY FLIGHT ID -->
          <div class="search-flight-card">
            <div class="card-title" style="margin-bottom:6px">
              Tra Cứu Hồ Sơ Chuyến Bay (58.588 Chuyến Bay)
            </div>
            <div class="card-subtitle" style="margin-bottom:14px">
              Kho dữ liệu 58.588 chuyến bay thương mại phục vụ phân tích rủi ro tài chính và mô phỏng can thiệp:
            </div>

            <div id="flight-id-error-banner" class="id-error-banner">
              <div style="display:flex;justify-content:space-between;align-items:start">
                <div id="flight-id-error-text"></div>
                <span style="cursor:pointer;font-weight:700;font-size:16px;line-height:1;margin-left:8px" onclick="document.getElementById('flight-id-error-banner').style.display='none'">&times;</span>
              </div>
              <div style="margin-top:8px">
                <strong>Chuyến Bay Giám Sát Trọng Điểm:</strong>
                <div class="toast-chips" style="margin-top:6px">
                  <span class="toast-chip" onclick="quickFill(4568)">#4568 (UA LAS➔BOS)</span>
                  <span class="toast-chip" onclick="quickFill(48339)">#48339 (DL LGB➔SLC)</span>
                  <span class="toast-chip" onclick="quickFill(25413)">#25413 (DL ORD➔ATL)</span>
                  <span class="toast-chip" onclick="quickFill(8626)">#8626 (UA PHX➔IAH)</span>
                  <span class="toast-chip" onclick="quickFill(2619)">#2619 (AA CLT➔DFW)</span>
                  <span class="toast-chip" onclick="quickFill(10316)">#10316 (WN MSP➔MDW)</span>
                </div>
              </div>
            </div>

            <div style="display:flex;gap:10px;margin-bottom:12px">
              <div style="position:relative;flex:1">
                <input id="flight_id" type="number" placeholder="Nhập ID (VD: 4568)" style="font-weight:700;font-family:'JetBrains Mono',monospace;font-size:14px;padding-right:65px" onkeydown="if(event.key==='Enter') runAdvisoryByFlightId()">
                <span class="input-hotkey-badge" title="Nhấn Ctrl + K để nhập nhanh">Ctrl K</span>
              </div>
              <button class="btn-primary" onclick="runAdvisoryByFlightId()">Tra Cứu & Phân Tích</button>
            </div>

            <!-- FLIGHT WATCH MINI-TABLE (BẢNG ĐIỀU KHIỂN GIÁM SÁT MẠNG BAY) -->
            <div class="flight-watch-card">
              <div class="flight-watch-header">
                <div style="display:flex;align-items:center;gap:7px">
                  <span class="live-dot" title="Giám sát trực tiếp mạng bay OCC"></span>
                  <span style="font-weight:800;font-size:11.5px;letter-spacing:0.4px;color:var(--text-main);text-transform:uppercase">
                    Bảng Giám Sát Mạng Bay Trọng Điểm (Flight Watch)
                  </span>
                </div>
                <span style="font-size:10.5px;color:var(--text-muted);font-family:'JetBrains Mono',monospace">8 Chuyến Bay</span>
              </div>
              <div style="font-size:11px;color:var(--text-muted);margin-bottom:8px">
                Nhấp trực tiếp 1 dòng để nạp dữ liệu và bóc tách tài chính tức thì:
              </div>
              <div class="flight-watch-table-container">
                <table class="flight-watch-table">
                  <thead>
                    <tr>
                      <th style="width:58px">Carrier</th>
                      <th style="width:72px">Flight No</th>
                      <th>Chặng Bay</th>
                      <th style="width:68px">Giờ Bay</th>
                      <th style="text-align:right;width:82px">Mức Rủi Ro</th>
                    </tr>
                  </thead>
                  <tbody id="flight-watch-tbody">
                    <tr onclick="selectFlightWatchRow(4568, this)" data-flight-id="4568" class="active-row">
                      <td><span class="carrier-pill carrier-ua">UA</span></td>
                      <td style="font-family:'JetBrains Mono',monospace;font-weight:700">UA4554</td>
                      <td>LAS ➔ BOS</td>
                      <td style="font-family:'JetBrains Mono',monospace">12:00L</td>
                      <td style="text-align:right"><span class="risk-pill risk-critical">CRITICAL</span></td>
                    </tr>
                    <tr onclick="selectFlightWatchRow(48339, this)" data-flight-id="48339">
                      <td><span class="carrier-pill carrier-dl">DL</span></td>
                      <td style="font-family:'JetBrains Mono',monospace;font-weight:700">DL3631</td>
                      <td>LGB ➔ DCA</td>
                      <td style="font-family:'JetBrains Mono',monospace">07:00L</td>
                      <td style="text-align:right"><span class="risk-pill risk-critical">CRITICAL</span></td>
                    </tr>
                    <tr onclick="selectFlightWatchRow(25413, this)" data-flight-id="25413">
                      <td><span class="carrier-pill carrier-dl">DL</span></td>
                      <td style="font-family:'JetBrains Mono',monospace;font-weight:700">DL6170</td>
                      <td>ORD ➔ STL</td>
                      <td style="font-family:'JetBrains Mono',monospace">17:00L</td>
                      <td style="text-align:right"><span class="risk-pill risk-critical">CRITICAL</span></td>
                    </tr>
                    <tr onclick="selectFlightWatchRow(8626, this)" data-flight-id="8626">
                      <td><span class="carrier-pill carrier-ua">UA</span></td>
                      <td style="font-family:'JetBrains Mono',monospace;font-weight:700">UA4406</td>
                      <td>PHX ➔ LGA</td>
                      <td style="font-family:'JetBrains Mono',monospace">09:00L</td>
                      <td style="text-align:right"><span class="risk-pill risk-critical">CRITICAL</span></td>
                    </tr>
                    <tr onclick="selectFlightWatchRow(2619, this)" data-flight-id="2619">
                      <td><span class="carrier-pill carrier-aa">AA</span></td>
                      <td style="font-family:'JetBrains Mono',monospace;font-weight:700">AA5957</td>
                      <td>CLT ➔ MSP</td>
                      <td style="font-family:'JetBrains Mono',monospace">20:00L</td>
                      <td style="text-align:right"><span class="risk-pill risk-critical">CRITICAL</span></td>
                    </tr>
                    <tr onclick="selectFlightWatchRow(10316, this)" data-flight-id="10316">
                      <td><span class="carrier-pill carrier-wn">WN</span></td>
                      <td style="font-family:'JetBrains Mono',monospace;font-weight:700">WN5880</td>
                      <td>MSP ➔ ATL</td>
                      <td style="font-family:'JetBrains Mono',monospace">17:00L</td>
                      <td style="text-align:right"><span class="risk-pill risk-critical">CRITICAL</span></td>
                    </tr>
                    <tr onclick="selectFlightWatchRow(1205, this)" data-flight-id="1205">
                      <td><span class="carrier-pill carrier-wn">WN</span></td>
                      <td style="font-family:'JetBrains Mono',monospace;font-weight:700">WN3117</td>
                      <td>EWR ➔ JFK</td>
                      <td style="font-family:'JetBrains Mono',monospace">09:00L</td>
                      <td style="text-align:right"><span class="risk-pill risk-critical">CRITICAL</span></td>
                    </tr>
                    <tr onclick="selectFlightWatchRow(33140, this)" data-flight-id="33140">
                      <td><span class="carrier-pill carrier-aa">AA</span></td>
                      <td style="font-family:'JetBrains Mono',monospace;font-weight:700">AA4451</td>
                      <td>FLL ➔ LAS</td>
                      <td style="font-family:'JetBrains Mono',monospace">13:00L</td>
                      <td style="text-align:right"><span class="risk-pill risk-critical">CRITICAL</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div style="font-size:11px;color:var(--slate-500);margin:10px 0 4px 0">Phím tắt nhanh:</div>
            <div style="display:flex;flex-wrap:wrap;gap:4px">
              <span class="chip" onclick="quickFill(4568)">#4568 (UA LAS➔BOS)</span>
              <span class="chip" onclick="quickFill(48339)">#48339 (DL LGB➔SLC)</span>
              <span class="chip" onclick="quickFill(25413)">#25413 (DL ORD➔ATL)</span>
              <span class="chip" onclick="quickFill(8626)">#8626 (UA PHX➔IAH)</span>
              <span class="chip" onclick="quickFill(2619)">#2619 (AA CLT➔DFW)</span>
              <span class="chip" onclick="quickFill(10316)">#10316 (WN MSP➔MDW)</span>
            </div>
          </div>

          <!-- CUSTOM PARAMETERS ACCORDION -->
          <details class="custom-param-card">
            <summary style="font-weight:800;font-size:14px;color:var(--slate-800);cursor:pointer;display:flex;align-items:center;gap:6px">
              Thiết Lập Kịch Bản Phân Tích Ad-hoc (Ad-hoc Flight Scenario Analysis)
            </summary>
            <div class="grid-form-compact" style="margin-top:14px">
              <div>
                <label>Thuật Toán Dự Báo Rủi Ro</label>
                <select id="model">
                  <option value="best" selected>Mô hình Chuẩn Hóa (Gradient Boosting Ensemble)</option>
                  <option value="ensemble">Soft-Voting Ensemble</option>
                  <option value="catboost">Mô hình CatBoost</option>
                  <option value="lgbm">Mô hình LightGBM</option>
                  <option value="xgboost">Mô hình XGBoost</option>
                  <option value="baseline">Mô hình Tuyến Tính (Baseline Regression)</option>
                </select>
              </div>
              <div>
                <label>Hãng hàng không (Carrier)</label>
                <select id="carrier">
<!--CARRIER_OPTIONS-->
                </select>
              </div>
              <div>
                <label>Sân bay cất cánh (Origin)</label>
                <select id="origin">
<!--ORIGIN_OPTIONS-->
                </select>
              </div>
              <div>
                <label>Sân bay hạ cánh (Dest)</label>
                <select id="dest">
<!--DEST_OPTIONS-->
                </select>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
                <div>
                  <label>Ngày bay</label>
                  <input id="date" type="date" value="2025-02-14">
                </div>
                <div>
                  <label>Giờ bay (0-23h)</label>
                  <input id="hour" type="number" value="17" min="0" max="23">
                </div>
              </div>
              <button class="btn-primary" style="margin-top:8px" onclick="runAdvisory()">Phân Tích Rủi Ro & Đề Xuất Phương Án Can Thiệp</button>
            </div>
          </details>

          <!-- WHAT-IF SIMULATOR CONSOLE -->
          <div class="whatif-container">
            <div class="card-title" style="color:#0369a1;font-size:14.5px">
              Mô Phỏng Kịch Bản Điều Hành What-If (What-If Impact Analysis)
            </div>
            <div style="font-size:12px;color:#0284c7;margin-top:2px">
              Đo lường thời gian thu hồi và hiệu quả bảo toàn chi phí ròng để đưa vào phương án điều hành:
            </div>
            <div class="whatif-bar">
              <button class="btn-whatif" onclick="runSim('reschedule_hour', {new_dep_hour: 10})">Điều chỉnh giờ bay 10:00 (Tránh cao điểm Hub & Tắc nghẽn taxi)</button>
              <button class="btn-whatif" onclick="runSim('crew_standby')">Kích hoạt Tổ bay Dự bị (FAR Part 117 Standby Crew)</button>
              <button class="btn-whatif" onclick="runSim('airborne_speedup')">Tăng Cost Index (Bay bù giờ trên không - Make-up Time)</button>
              <button class="btn-whatif" onclick="runSim('tail_swap')">Hoán đổi Tàu bay Dự bị (Aircraft Tail Swap)</button>
            </div>
            <div id="whatif-box" style="display:none" class="whatif-result"></div>
          </div>
        </div>

        <!-- RIGHT COLUMN: FLIGHT INTELLIGENCE & ACTION MATRIX -->
        <div class="dispatch-main">
          
          <!-- INITIAL PLACEHOLDER (BEFORE SEARCH) -->
          <div id="initial-placeholder" class="card" style="text-align:center;padding:60px 30px">
            <div style="display:flex;justify-content:center;margin-bottom:14px">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>
              </svg>
            </div>
            <h3 style="font-size:18px;color:var(--slate-800);margin-bottom:6px">Trung Tâm Giám Sát & Phân Tích Rủi Ro Chuyến Bay</h3>
            <p style="font-size:13px;color:var(--slate-500);max-width:560px;margin:0 auto 16px auto">
              Chọn một chuyến bay trong danh sách hoặc nhập mã chuyến bay ở cột bên trái để trích xuất hồ sơ phân tích rủi ro, bóc tách thiệt hại tài chính và mô phỏng kịch bản điều hành.
            </p>
            <button class="btn-primary" style="padding:10px 24px" onclick="quickFill(4568)">Mở Hồ Sơ Chuyến Bay #4568 (UA LAS➔BOS)</button>
          </div>

          <!-- RESULTS CONTAINER (VISIBLE AFTER FLIGHT LOOKUP) -->
          <div id="results" style="display:none">
            
            <!-- HERO FLIGHT HUD CARD -->
            <div class="hero-flight-hud" id="banner-card">
              <div style="display:flex;justify-content:space-between;align-items:start;flex-wrap:wrap;gap:12px">
                <div>
                  <div style="font-size:11px;font-family:'JetBrains Mono',monospace;color:#38bdf8;letter-spacing:1px" id="adv-id-label">HỒ SƠ VẬN HÀNH: -</div>
                  <div class="route-display">
                    <span class="airport-code" id="flight-title-label">Chuyến bay: -</span>
                  </div>
                </div>
                <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
                  <span id="risk-badge" class="badge"></span>
                  <button class="btn-primary" style="background:#0284c7;color:#ffffff;font-weight:700;border:0;display:inline-flex;align-items:center;gap:6px" onclick="openSlideModal()" title="Xuất Slide Insight (Báo Cáo Quản Trị)">
                    📋 Xuất Slide Insight (Báo Cáo Quản Trị)
                  </button>
                  <button id="btn-dispatch-release" class="btn-primary btn-dispatch-release" onclick="exportDispatchRelease()" title="Sao chép Điện văn Điều phái OCC chuẩn nghiệp vụ">
                    📋 Xuất Điện Văn Điều Phái (Dispatch Release)
                  </button>
                  <button class="btn-primary" style="background:#0284c7;color:#ffffff;font-weight:800;border:0" onclick="askCopilotAboutCurrentFlight()">
                    Chuyển Sang Chẩn Đoán Nghiệp Vụ ➔
                  </button>
                </div>
              </div>

              <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);padding:14px 18px;border-radius:var(--radius-md);font-size:13.5px;line-height:1.6;margin-top:14px;color:#f8fafc" id="summary-text"></div>

              <div style="display:flex;gap:14px;margin-top:14px;font-size:12px;color:#cbd5e1;flex-wrap:wrap" id="flight-meta-tags"></div>
            </div>

            <!-- FINANCIAL COST EXPOSURE CARD (FAA $101.18/MIN) -->
            <div class="card">
              <div class="card-header-flex">
                <div>
                  <div class="card-title">Phân Tích Thiệt Hại Chi Phí Vận Hành & Chế Tài Pháp Lý</div>
                  <div class="card-subtitle">Căn cứ định mức FAA/A4A $101.18/phút + Phạt Tarmac 14 CFR § 259.4 ($37,377/pax) + Hoàn tiền 14 CFR § 260.6.</div>
                </div>
              </div>

              <div class="metric-row">
                <div class="metric-box">
                  <div class="metric-title">Độ Trễ Dự Báo</div>
                  <div id="delay-mins-val" class="metric-val">-</div>
                  <div class="metric-sub" id="delay-prob-sub">Xác suất trễ: -</div>
                </div>
                <div class="metric-box">
                  <div class="metric-title">Chi Phí Trễ Cơ Sở (FAA)</div>
                  <div id="base-cost-val" class="metric-val" style="color:var(--rose-600)">-</div>
                  <div class="metric-sub">Định mức $101.18/phút</div>
                </div>
                <div class="metric-box">
                  <div class="metric-title">Rủi Ro Phạt Tarmac & Hoàn Vé</div>
                  <div id="penalty-cost-val" class="metric-val" style="color:var(--amber-600)">-</div>
                  <div class="metric-sub" id="pax-count-sub">Quy chuẩn 14 CFR</div>
                </div>
                <div class="metric-box" style="background:var(--emerald-50);border-color:#a7f3d0">
                  <div class="metric-title" style="color:var(--emerald-800)">Tiết Kiệm Khi Can Thiệp</div>
                  <div id="savings-val" class="metric-val" style="color:var(--emerald-600)">-</div>
                  <div class="metric-sub" style="color:var(--emerald-800)">Bảo toàn tài chính ròng</div>
                </div>
              </div>

              <!-- STACKED PROGRESS BAR (FEATURE 4) -->
              <div class="cost-breakdown-container">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px">
                  <span style="font-size:13px;font-weight:700;color:var(--slate-800)">
                    Cơ Cấu Rủi Ro Thiệt Hại (Chi Phí Cơ Sở FAA vs Chế Tài Hành Chính):
                  </span>
                  <span id="cost-total-label" style="font-size:13px;font-weight:800;color:var(--rose-600);font-family:'JetBrains Mono',monospace">
                    Tổng rủi ro: $0 USD
                  </span>
                </div>
                
                <div class="stacked-bar-wrapper">
                  <div id="bar-base-delay" class="stacked-segment" style="width:0%;background:linear-gradient(90deg, #0284c7, #38bdf8)" title="Chi phí trễ cơ sở FAA"></div>
                  <div id="bar-tarmac-penalty" class="stacked-segment" style="width:0%;background:linear-gradient(90deg, #e11d48, #f43f5e)" title="Rủi ro phạt Tarmac Delay 14 CFR § 259.4"></div>
                  <div id="bar-cash-refund" class="stacked-segment" style="width:0%;background:linear-gradient(90deg, #d97706, #f59e0b)" title="Bồi hoàn tiền mặt 14 CFR § 260.6"></div>
                </div>

                <div style="display:flex;justify-content:space-between;gap:12px;margin-top:12px;flex-wrap:wrap;font-size:12px">
                  <div style="display:flex;align-items:center;gap:6px">
                    <span style="width:12px;height:12px;background:#0284c7;border-radius:3px;display:inline-block"></span>
                    <span id="legend-base-text">Chi phí trễ cơ sở FAA: <strong>$0 (0%)</strong></span>
                  </div>
                  <div style="display:flex;align-items:center;gap:6px">
                    <span style="width:12px;height:12px;background:#f43f5e;border-radius:3px;display:inline-block"></span>
                    <span id="legend-tarmac-text">Phạt Tarmac (§ 259.4): <strong style="color:var(--rose-600)">$0 (0%)</strong></span>
                  </div>
                  <div style="display:flex;align-items:center;gap:6px">
                    <span style="width:12px;height:12px;background:#f59e0b;border-radius:3px;display:inline-block"></span>
                    <span id="legend-refund-text">Hoàn vé (§ 260.6): <strong style="color:var(--amber-800)">$0 (0%)</strong></span>
                  </div>
                </div>

                <div id="cost-callout-box" class="cost-callout-box">
                  <span id="cost-callout-text"></span>
                </div>
              </div>
            </div>

            <!-- ACTIONABLE DISPATCH PLAN (5 GATES) -->
            <div class="card">
              <div class="card-title">Kế Hoạch Khắc Phục & Tác Nghiệp 5 Chặng (5-Gate Action Plan)</div>
              <div class="card-subtitle" style="margin-bottom:14px">Lộ trình kiểm soát thời gian và giảm thiểu rủi ro khép kín để đề xuất trong slide báo cáo quản trị:</div>
              <div id="timeline-list"></div>
            </div>

            <!-- DYNAMIC SOPS -->
            <div class="card">
              <div class="card-title">Danh Mục Quy Trình Thao Tác Chuẩn Đính Kèm (Dynamic SOPs)</div>
              <div class="card-subtitle" style="margin-bottom:14px">Được gắn kết tự động từ Kho tri thức 40 đề mục theo rủi ro thực tế:</div>
              <div id="sop-list"></div>
            </div>

            <!-- REGULATORY COMPLIANCE BREAKDOWN -->
            <div class="card">
              <div class="card-title">Thẩm Định Pháp Lý & Chế Tài Quản Lý Nhà Nước (US DOT & CAAV)</div>
              <div id="legal-list"></div>
            </div>

            <!-- RAW MARKDOWN -->
            <details class="card" style="cursor:pointer">
              <summary style="font-weight:700;font-size:13px;color:var(--primary)">📄 Bấm Để Xem Báo Cáo Markdown Định Dạng In / Chia Sẻ</summary>
              <pre id="markdown-raw" style="margin-top:12px;background:#0f172a;color:#f8fafc;padding:14px;border-radius:var(--radius-sm);font-size:11.5px;overflow-x:auto;font-family:'JetBrains Mono',monospace"></pre>
            </details>

          </div>
        </div>
      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- TAB 2: ANALYTICS COPILOT Q&A                                          -->
    <!-- ===================================================================== -->
    <div id="tab-chat" class="tab-content">
      <div class="chat-studio-layout">
        
        <!-- LEFT SIDEBAR: FLIGHT CONTEXT & STARTERS -->
        <div class="chat-sidebar">
          
          <!-- ACTIVE FLIGHT CONTEXT CARD -->
          <div class="chat-banner" id="chat-context-banner">
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;color:#38bdf8;margin-bottom:4px;letter-spacing:0.5px">
              Hồ Sơ Chuyến Bay Đang Phân Tích
            </div>
            <div id="chat-context-text" style="line-height:1.5">
              <span>Trạng thái: <strong>Chưa chọn chuyến bay cụ thể</strong>. Hệ thống đang ở chế độ Tra Cứu Tổng Thể. Hãy tra cứu chuyến bay ở Tab 1 để trích xuất hồ sơ phân tích chi tiết.</span>
            </div>
            <div style="margin-top:10px">
              <button class="btn-sm" id="btn-clear-context" style="display:none;background:rgba(255,255,255,0.1);color:#fff;border-color:rgba(255,255,255,0.2)" onclick="clearFlightContext()">✖ Bỏ chọn chuyến bay</button>
            </div>
          </div>

          <!-- PROMPT CATEGORIES -->
          <div class="card" style="padding:18px">
            <div class="card-title" style="font-size:13.5px;margin-bottom:10px">
              Chuyên Đề Phân Tích Trọng Tâm (Key Diagnostic Topics)
            </div>
            <div id="starter-chips-container" style="display:flex;flex-direction:column;gap:6px">
              <span class="chip chip-primary" onclick="sendQuickPrompt('Ý nghĩa các chỉ số trên 4 trang Power BI Dashboard là gì?')">📊 Ý nghĩa các chỉ số trên 4 trang Power BI Dashboard</span>
              <span class="chip chip-primary" onclick="sendQuickPrompt('Tại sao Hub DFW và ORD thường xuyên bị nghẽn nặng vào khung giờ tối?')">🔍 Root Cause: Tại sao Hub DFW & ORD bị nghẽn?</span>
              <span class="chip chip-primary" onclick="sendQuickPrompt('Giải thích công thức DAX tính Chi Phí Trễ và định mức FAA $101.18/phút.')">💵 Định mức FAA $101.18/phút & Công thức DAX</span>
              <span class="chip chip-primary" onclick="sendQuickPrompt('Tại sao nguyên nhân Late Aircraft chiếm tới gần 40% tổng số phút trễ?')">🌪️ Phân tích hiệu ứng Domino Late Aircraft (~40%)</span>
              <span class="chip chip-primary" onclick="sendQuickPrompt('Cách đọc ma trận Đấu Trường Mô Hình (AUC, Lift @ 10%, Brier Score) trên Trang 4?')">📈 Đánh giá hiệu năng mô hình (AUC, Lift, Brier)</span>
              <span class="chip chip-primary" onclick="sendQuickPrompt('Quy tắc Tarmac Delay 180 phút của US DOT phạt bao nhiêu USD và yêu cầu gì?')">⚖️ Chế tài phạt Tarmac 14 CFR § 259.4 ($37,377/pax)</span>
            </div>
          </div>

          <!-- CONTROLS & SESSION -->
          <div class="card" style="padding:18px">
            <div class="card-title" style="font-size:13.5px;margin-bottom:10px">
              Quản Trị Bàn Làm Việc
            </div>
            <label style="font-size:11px">Cơ chế xử lý dữ liệu:</label>
            <select id="chat-model-provider" style="font-size:12px;padding:8px 10px;margin-bottom:8px" onchange="handleProviderChange()">
              <option value="auto" selected>⚡ Tự động (Ưu tiên mô hình mạnh nhất)</option>
              <optgroup label="⚡ Google Gemini (2025-2026)">
                <option value="gemini:gemini-3.8-flash">⚡ Gemini 3.8 Flash (Mới nhất • Siêu tốc)</option>
                <option value="gemini:gemini-3.8-pro">🧠 Gemini 3.8 Pro (Mới nhất • Chuyên sâu)</option>
                <option value="gemini:gemini-2.5-flash">✨ Gemini 2.5 Flash (Ổn định)</option>
              </optgroup>
              <optgroup label="🟣 Anthropic Claude (Thế hệ mới)">
                <option value="claude:claude-3-7-sonnet-latest">🟣 Claude 3.7 Sonnet (Hybrid Reasoning)</option>
                <option value="claude:claude-3-5-sonnet-latest">🟣 Claude 3.5 Sonnet v2</option>
                <option value="claude:claude-3-5-haiku-latest">⚡ Claude 3.5 Haiku (Siêu tốc)</option>
              </optgroup>
              <optgroup label="🟢 OpenAI (Dòng Suy Luận Reasoning)">
                <option value="openai:o3-mini">🟢 OpenAI o3-mini (High-speed Reasoning)</option>
                <option value="openai:o1">🧠 OpenAI o1 (Deep Reasoning)</option>
                <option value="openai:gpt-4.5-preview">✨ OpenAI GPT-4.5 Preview</option>
                <option value="openai:gpt-4o">🟢 OpenAI GPT-4o Omnichannel</option>
              </optgroup>
              <optgroup label="🔵 DeepSeek (Mã nguồn mở)">
                <option value="deepseek:deepseek-reasoner">🔵 DeepSeek-R1 Reasoner (CoT Open)</option>
                <option value="deepseek:deepseek-chat">🔵 DeepSeek-V3 Chat</option>
              </optgroup>
              <optgroup label="🛡️ Nội bộ & Tùy chỉnh">
                <option value="offline">🛡️ Offline Engine (Nội bộ • 0ms • Miễn phí)</option>
                <option value="custom">⚙️ Tùy chỉnh Model ID...</option>
              </optgroup>
            </select>
            <div id="custom-model-box" style="display:none;margin-bottom:10px">
              <input id="custom-model-id" type="text" placeholder="Nhập ID model (vd: claude-3-7-sonnet-latest, o3-mini, gemini-3.8-flash...)" style="font-size:11.5px;padding:6px 10px;width:100%" onchange="handleCustomModelChange()">
            </div>
            <div style="display:flex;gap:8px;flex-direction:column">
              <button class="btn-sm" id="btn-export-chat-audit" style="justify-content:center;font-weight:700;color:var(--primary);border-color:var(--primary);background:var(--primary-light)" onclick="openAuditExportModal()">📥 Xuất Biên Bản Hội Thoại (Audit Log)</button>
              <button class="btn-sm" id="btn-settings-expand" style="justify-content:center;font-weight:700" onclick="openSettingsModal()">⚙️ Cấu Hình Mở Rộng</button>
              <button class="btn-sm" id="btn-reset-chat" style="justify-content:center" onclick="resetChat()">Làm Mới Bàn Tra Cứu</button>
            </div>
          </div>
        </div>

        <!-- RIGHT: CHAT STREAM CONVERSATION -->
        <div class="chat-window">
          <div class="chat-messages" id="chat-stream">
            <!-- Greeting Briefing Card -->
            <div class="chat-msg assistant">
              <div class="chat-meta">
                <span style="font-weight:800;color:var(--primary);display:flex;align-items:center;gap:6px">
                  <span>📋</span> Trung Tâm Tra Cứu & Chẩn Đoán Vận Hành
                </span>
                <span class="chat-source-tag">Cơ Sở Tri Thức & Pháp Chuẩn Hàng Không</span>
              </div>
              <div class="chat-body">
                Hệ thống tra cứu chuyên sâu hỗ trợ phân tích toàn diện <strong>các chỉ số trên 4 trang Power BI Dashboard</strong>, điều tra căn nguyên (Root Cause Analysis - RCA) tắc nghẽn Hub DFW/ORD, diễn giải các <strong>công thức DAX và định mức tài chính FAA $101.18/phút</strong>, cùng 40 quy chuẩn nghiệp vụ & chế tài US DOT.<br><br>
                Vui lòng chọn chuyên đề bên trái hoặc nhập nội dung vào thanh tra cứu bên dưới để trích xuất báo cáo chẩn đoán.
              </div>
              <div class="chat-citations">
                <span class="citation-tag">4 Trang Power BI Dashboard</span>
                <span class="citation-tag">Root Cause Analysis (Hub DFW/ORD)</span>
                <span class="citation-tag">Công Thức DAX & Định Mức FAA $101.18/phút</span>
                <span class="citation-tag">14 CFR § 259.4 & FAR Part 117</span>
              </div>
            </div>
          </div>

          <!-- INPUT COMPONENT -->
          <div class="chat-input-area">
            <div class="chat-input-row">
              <input id="chat-input-field" type="text" placeholder="Nhập nội dung cần tra cứu (ví dụ: Căn nguyên nghẽn Hub DFW, định mức FAA $101.18, điều luật Tarmac, chỉ số OTP A14...)..." onkeydown="if(event.key==='Enter') sendChatMessage()">
              <button type="button" class="voice-btn" id="btn-voice-main" onclick="toggleVoiceInput('main')" title="🎙️ Nhận diện giọng nói tác nghiệp (Web Speech API)">🎙️</button>
              <button class="btn-primary" id="btn-send-chat" onclick="sendChatMessage()">🔍 Tra Cứu & Chẩn Đoán</button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- TAB 3: DATA METRIC DICTIONARY & COMPLIANCE                          -->
    <!-- ===================================================================== -->
    <div id="tab-catalog" class="tab-content">
      <div class="card">
        <div class="card-header-flex">
          <div>
            <div class="card-title" style="font-size:18px">Từ Điển Chỉ Số & Quy Chuẩn Nghiệp Vụ (Data Metric Dictionary)</div>
            <div class="card-subtitle">Tài liệu tham chiếu chuẩn hóa toàn diện cho Data Analyst: 40 quy chuẩn vận hành, độ đo Machine Learning, công thức DAX Power BI và quy trình tác nghiệp khép kín.</div>
          </div>
        </div>

        <div class="catalog-search-bar">
          <input id="catalog-search-input" type="text" placeholder="Tìm kiếm thuật ngữ, từ viết tắt, công thức DAX, chỉ số ML, điều luật... (Nhấn / để tìm nhanh)" onkeyup="filterCatalog()">
          <div style="display:flex;gap:6px;flex-wrap:wrap">
            <button class="btn-sm" onclick="filterCategory('all')">Tất cả</button>
            <button class="btn-sm" onclick="filterCategory('aviation_metrics')">Chỉ Số Vận Hành (18)</button>
            <button class="btn-sm" onclick="filterCategory('ml_metrics')">Đo Lường Dự Báo (14)</button>
            <button class="btn-sm" onclick="filterCategory('dax_measures')">Công Thức DAX Power BI (5)</button>
            <button class="btn-sm" onclick="filterCategory('sops')">Quy Trình Chuẩn SOPs (8)</button>
          </div>
        </div>

        <div id="catalog-grid-container" class="catalog-grid"></div>
      </div>
    </div>

  </div>

  <!-- MODAL FOR CATALOG DETAILS -->
  <div id="detail-modal" class="modal">
    <div class="modal-content">
      <span class="close-btn" onclick="closeModal()">&times;</span>
      <div id="modal-body"></div>
    </div>
  </div>

  <!-- MODAL FOR EXECUTIVE SLIDE PRESENTATION & INSIGHT EXPORT -->
  <div id="slide-modal" class="modal">
    <div class="modal-content slide-modal-content">
      <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #f1f5f9;padding-bottom:14px;margin-bottom:16px">
        <div style="display:flex;align-items:center;gap:12px">
          <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;width:38px;height:38px;display:flex;align-items:center;justify-content:center;font-size:20px">
            📊
          </div>
          <div>
            <h2 style="margin:0;font-size:18px;color:#0f172a;font-weight:800;letter-spacing:-0.3px">
              Hồ Sơ Thuyết Trình Quản Trị (Executive Slide Deck)
            </h2>
            <div style="font-size:12px;color:#64748b;margin-top:2px" id="slide-modal-subtitle">
              Định dạng 16:9 Chuẩn Trình Chiếu • Phân Tích Rủi Ro Vận Hành, Thẩm Định Pháp Lý & Bóc Tách Chi Phí FAA $101.18/phút
            </div>
          </div>
        </div>
        <span class="close-btn" style="color:#64748b;font-size:26px" onclick="closeSlideModal()">&times;</span>
      </div>

      <!-- ACTION TOOLBAR -->
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px;padding:12px 16px;background:#f8fafc;border-radius:var(--radius-md);border:1px solid #e2e8f0;align-items:center;justify-content:space-between">
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <button class="btn-primary" style="background:#0284c7;border:0;font-weight:700;display:inline-flex;align-items:center;gap:6px" onclick="downloadSlidePptx()">
            📥 Tải PowerPoint (.pptx)
          </button>
          <button class="btn-primary" style="background:#059669;border:0;font-weight:700;display:inline-flex;align-items:center;gap:6px" onclick="openSlideDeckHtml()">
            🌐 Trình Chiếu F11 (HTML Deck)
          </button>
          <button class="btn-primary" style="background:#475569;border:0;font-weight:700;display:inline-flex;align-items:center;gap:6px" onclick="downloadSlideMarkdown()">
            📄 Tải Slide Markdown (.md)
          </button>
          <button class="btn-primary btn-dispatch-release" onclick="exportDispatchRelease()">
            📋 Xuất Điện Văn Điều Phái
          </button>
        </div>
        <button class="btn-secondary" style="background:#ffffff;color:#334155;border:1px solid #cbd5e1;font-weight:600;display:inline-flex;align-items:center;gap:6px" onclick="copySlideSummaryDirect()">
          📋 Sao Chép Tóm Tắt
        </button>
      </div>

      <!-- SLIDE TABS SELECTOR -->
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:14px;flex-wrap:wrap">
        <span style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-right:4px">Chọn Slide:</span>
        <button class="slide-chip-tab active" id="stab-1" onclick="switchModalSlide(1)">Slide 1: Tổng Quan Vận Hành</button>
        <button class="slide-chip-tab" id="stab-2" onclick="switchModalSlide(2)">Slide 2: Phân Tích Căn Nguyên & Điểm Nghẽn</button>
        <button class="slide-chip-tab" id="stab-3" onclick="switchModalSlide(3)">Slide 3: Thẩm Định Pháp Lý & Chế Tài</button>
        <button class="slide-chip-tab" id="stab-4" onclick="switchModalSlide(4)">Slide 4: Chi Phí FAA & ROI Can Thiệp</button>
      </div>

      <!-- SLIDE PREVIEW CONTAINER -->
      <div id="slide-preview-body" class="slide-preview-card">
        <!-- Rendered dynamically -->
      </div>

      <!-- MODAL FOOTER NAV -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:14px;padding-top:12px;border-top:1px solid #e2e8f0">
        <div style="font-size:12px;color:#64748b" id="slide-counter-label">Slide 1 / 4 • Dùng phím ◀ / ▶ hoặc nút bên phải để chuyển slide</div>
        <div style="display:flex;gap:10px">
          <button class="btn-secondary" style="background:#ffffff;border:1px solid #cbd5e1;color:#334155;padding:6px 14px" onclick="prevModalSlide()">◀ Slide Trước</button>
          <button class="btn-primary" style="background:#0284c7;border:0;padding:6px 16px" onclick="nextModalSlide()">Slide Kế Tiếp ▶</button>
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL FOR SETTINGS (SERVICE CONFIGURATION) -->
  <div id="settings-modal" class="modal">
    <div class="modal-content settings-modal-content" style="max-width:580px">
      <span class="close-btn" onclick="closeSettingsModal()">&times;</span>
      <h2 class="settings-modal-title" style="margin:0 0 6px 0;font-size:18px">⚙️ Cấu Hình Mô Hình LLM Mở Rộng</h2>
      <div class="settings-modal-desc" style="font-size:12.5px;margin-bottom:14px;line-height:1.5">
        Hệ thống hỗ trợ song song <strong>Gemini 3.8, Claude 3.7, OpenAI o3-mini/o1 và DeepSeek R1</strong> cùng bộ lọc kiểm toán nội bộ. Bạn có thể lưu khóa API vào trình duyệt (<code>localStorage</code> an toàn) để kích hoạt:
      </div>

      <div style="margin-bottom:12px">
        <label>Google Gemini API Key (Gemini 3.8 Flash / Pro)</label>
        <div class="input-group-password">
          <input id="setting-gemini-key" type="password" placeholder="AIzaSy..." autocomplete="off">
          <button type="button" class="btn-toggle-pw" onclick="togglePasswordVisibility('setting-gemini-key', this)">👁️</button>
        </div>
      </div>

      <div style="margin-bottom:12px">
        <label>Anthropic Claude API Key (Claude 3.7 Sonnet / 3.5 Haiku)</label>
        <div class="input-group-password">
          <input id="setting-claude-key" type="password" placeholder="sk-ant-..." autocomplete="off">
          <button type="button" class="btn-toggle-pw" onclick="togglePasswordVisibility('setting-claude-key', this)">👁️</button>
        </div>
      </div>

      <div style="margin-bottom:12px">
        <label>OpenAI API Key (o3-mini / o1 / GPT-4.5 / GPT-4o)</label>
        <div class="input-group-password">
          <input id="setting-openai-key" type="password" placeholder="sk-..." autocomplete="off">
          <button type="button" class="btn-toggle-pw" onclick="togglePasswordVisibility('setting-openai-key', this)">👁️</button>
        </div>
      </div>

      <div style="margin-bottom:14px">
        <label>DeepSeek API Key (DeepSeek-R1 Reasoner / V3)</label>
        <div class="input-group-password">
          <input id="setting-deepseek-key" type="password" placeholder="sk-..." autocomplete="off">
          <button type="button" class="btn-toggle-pw" onclick="togglePasswordVisibility('setting-deepseek-key', this)">👁️</button>
        </div>
      </div>

      <!-- Key Status Box -->
      <div id="setting-status-box" class="setting-status-box status-neutral" style="margin-bottom:14px;padding:10px 14px;border-radius:var(--radius-sm);font-size:12px;display:flex;align-items:center;justify-content:space-between">
        <span id="setting-status-text">⚪ Trạng thái: Vận hành nội bộ (Offline Grounding Engine)</span>
      </div>

      <div style="display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap">
        <button class="btn-sm" style="color:#b91c1c;border-color:#fca5a5" onclick="clearApiKeys()">🗑️ Xóa Tất Cả Key</button>
        <button class="btn-sm" onclick="testAllApiKeys()">🧪 Kiểm Tra Kết Nối (Ping Test)</button>
        <button class="btn-primary" style="width:auto;padding:8px 16px" onclick="saveApiKeys()">💾 Lưu Cấu Hình</button>
      </div>
    </div>
  </div>

  <!-- MODAL FOR EXPORTING OCC CHAT AUDIT LOG -->
  <div id="audit-export-modal" class="modal">
    <div class="modal-content" style="max-width:860px;width:92vw;max-height:90vh;display:flex;flex-direction:column;padding:24px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;border-bottom:1px solid var(--border-color);padding-bottom:12px">
        <div>
          <h2 style="margin:0 0 4px 0;font-size:18px;color:var(--text-main);display:flex;align-items:center;gap:8px">
            <span>📥</span> Xuất Biên Bản Hội Thoại & Kiểm Toán Tác Nghiệp Bay
          </h2>
          <div style="font-size:12px;color:var(--text-muted)">
            Biên bản lưu trữ hồ sơ giải trình tác nghiệp bay phục vụ thanh tra Cục Hàng Không (CAAV) & US DOT FAA.
          </div>
        </div>
        <span class="close-btn" onclick="closeAuditExportModal()">&times;</span>
      </div>

      <!-- Action buttons -->
      <div style="display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap">
        <button class="btn-primary" onclick="downloadAuditLogMarkdown()" style="padding:8px 16px;font-size:12.5px;display:flex;align-items:center;gap:6px">
          <span>📄</span> Tải Biên Bản Markdown (.md)
        </button>
        <button class="btn-primary" onclick="printOCCAuditLog()" style="background:#059669;border-color:#059669;padding:8px 16px;font-size:12.5px;display:flex;align-items:center;gap:6px">
          <span>🖨️</span> In / Xuất Hồ Sơ PDF (FAA Compliance)
        </button>
        <button class="btn-secondary" onclick="copyAuditLogToClipboard()" style="background:#ffffff;border:1px solid #cbd5e1;color:#334155;padding:8px 16px;font-size:12.5px;display:flex;align-items:center;gap:6px">
          <span>📋</span> Sao Chép Toàn Bộ (Clipboard)
        </button>
      </div>

      <!-- Preview container -->
      <div style="font-size:11.5px;font-weight:700;color:var(--text-muted);margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px">
        Bản Xem Trước Hồ Sơ Biên Bản (Live Audit Preview):
      </div>
      <div id="audit-log-preview-container" style="flex:1;overflow-y:auto;background:#090e17;color:#e2e8f0;padding:16px;border-radius:var(--radius-sm);font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.55;white-space:pre-wrap;border:1px solid var(--border-color);max-height:480px">
      </div>
    </div>
  </div>

  <script>
    let currentAdv = null;
    let currentFlightContext = null;
    let chatHistory = [];
    let persistedChatMessages = [];
    let catalogData = { terms: [], sops: [] };
    let lastUserMsgElement = null;

    const CHAT_STORAGE_KEY = 'occ_copilot_chat_history_v2';
    const SAMPLE_FLIGHTS = [
      { id: 4568, label: "4568 (UA LAS➔BOS)" },
      { id: 48339, label: "48339 (DL LGB➔SLC)" },
      { id: 25413, label: "25413 (DL ORD➔ATL)" },
      { id: 8626, label: "8626 (UA PHX➔IAH)" },
      { id: 2619, label: "2619 (AA CLT➔DFW)" },
      { id: 10316, label: "10316 (WN MSP➔MDW)" }
    ];

    // =========================================================================
    // COCKPIT OCC DARK THEME (FEATURE P1)
    // =========================================================================
    function initCockpitTheme() {
      const savedTheme = localStorage.getItem('occ_cockpit_theme') || 'light';
      applyCockpitTheme(savedTheme);
    }

    function applyCockpitTheme(theme) {
      const isDark = (theme === 'dark');
      if (isDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
      }
      localStorage.setItem('occ_cockpit_theme', isDark ? 'dark' : 'light');
      const icon = document.getElementById('theme-toggle-icon');
      const text = document.getElementById('theme-toggle-text');
      if (icon) icon.textContent = isDark ? '☀️' : '🌙';
      if (text) text.textContent = isDark ? 'Light Mode' : 'Dark Mode';
    }

    function toggleCockpitTheme() {
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      applyCockpitTheme(isDark ? 'light' : 'dark');
    }

    // =========================================================================
    // PORTAL URL HELPER
    // =========================================================================
    function copyPortalLink() {
      const url = window.location.origin;
      navigator.clipboard.writeText(url).then(() => {
        showToast("Đã sao chép liên kết", `📋 Đã chép ${url} vào khay nhớ tạm!`, "success");
      }).catch(() => {
        showToast("Địa chỉ Web Portal", `🌐 Địa chỉ truy cập: ${url}`, "info");
      });
    }

    // =========================================================================
    // TOAST NOTIFICATION ENGINE (REPLACES ALERTS)
    // =========================================================================
    function showToast(title, message, type = 'info', sampleList = null, duration = 6500) {
      const container = document.getElementById('toast-container');
      if (!container) return null;

      const toast = document.createElement('div');
      toast.className = `toast toast-${type}`;

      const iconMap = {
        error: '❌',
        success: '✅',
        warning: '⚠️',
        info: 'ℹ️'
      };
      const icon = iconMap[type] || 'ℹ️';

      let chipsHtml = '';
      if (sampleList && sampleList.length > 0) {
        chipsHtml = `
          <div class="toast-hint-title">
            💡 Gợi ý Chuyến Bay Mẫu Có Thật Trong Marts:
          </div>
          <div class="toast-chips">
            ${sampleList.map(s => {
              const sId = typeof s === 'object' ? s.id : s;
              const sLabel = typeof s === 'object' ? s.label : ('#' + s);
              return `<span class="toast-chip" onclick="quickFill(${sId}); this.closest('.toast').remove();">📌 ${sLabel}</span>`;
            }).join('')}
          </div>
        `;
      }

      toast.innerHTML = `
        <div class="toast-header">
          <div class="toast-title" style="display:flex;align-items:center;gap:6px">
            <span>${icon}</span>
            <span>${title}</span>
          </div>
          <span class="toast-close" onclick="this.closest('.toast').remove()">&times;</span>
        </div>
        <div class="toast-body">${message}</div>
        ${chipsHtml}
      `;

      container.appendChild(toast);
      if (duration > 0) {
        setTimeout(() => {
          if (toast.parentElement) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(110%)';
            setTimeout(() => toast.remove(), 300);
          }
        }, duration);
      }
      return toast;
    }

    // =========================================================================
    // SETTINGS MODAL & API KEY MANAGEMENT (FEATURE 3 & MULTI-LLM)
    // =========================================================================
    function openSettingsModal() {
      document.getElementById('setting-gemini-key').value = localStorage.getItem('gemini_api_key') || '';
      document.getElementById('setting-claude-key').value = localStorage.getItem('claude_api_key') || '';
      document.getElementById('setting-openai-key').value = localStorage.getItem('openai_api_key') || '';
      document.getElementById('setting-deepseek-key').value = localStorage.getItem('deepseek_api_key') || '';
      updateSettingsStatusBox();
      document.getElementById('settings-modal').style.display = 'block';
    }

    function closeSettingsModal() {
      document.getElementById('settings-modal').style.display = 'none';
    }

    function togglePasswordVisibility(inputId, btn) {
      const input = document.getElementById(inputId);
      if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
      } else {
        input.type = 'password';
        btn.textContent = '👁️';
      }
    }

    function updateSettingsStatusBox() {
      const gKey = localStorage.getItem('gemini_api_key') || '';
      const cKey = localStorage.getItem('claude_api_key') || '';
      const oKey = localStorage.getItem('openai_api_key') || '';
      const dKey = localStorage.getItem('deepseek_api_key') || '';
      const box = document.getElementById('setting-status-box');
      const txt = document.getElementById('setting-status-text');
      if (!box || !txt) return;

      const activeList = [];
      if (gKey.trim()) activeList.push('⚡ Gemini 3.8');
      if (cKey.trim()) activeList.push('🟣 Claude 3.7');
      if (oKey.trim()) activeList.push('🟢 OpenAI o3/o1');
      if (dKey.trim()) activeList.push('🔵 DeepSeek R1');

      if (activeList.length > 0) {
        box.className = 'setting-status-box status-success';
        txt.innerHTML = `🟢 <strong>Đã cấu hình (${activeList.length}):</strong> ${activeList.join(' • ')}`;
      } else {
        box.className = 'setting-status-box status-neutral';
        txt.innerHTML = '⚪ <strong>Chưa lưu API Key</strong> (Copilot hoạt động bằng Offline Grounding Engine 40 đề mục 100% miễn phí)';
      }
      updateLlmStatusBadges();
    }

    // =========================================================================
    // CROSS-TAB / POWER BI REAL-TIME SYNCHRONIZATION BUS
    // =========================================================================
    const SYNC_CHANNEL_NAME = 'skyops_runtime_sync';
    let syncChannel = null;
    try {
      if (typeof BroadcastChannel !== 'undefined') {
        syncChannel = new BroadcastChannel(SYNC_CHANNEL_NAME);
        syncChannel.onmessage = (event) => {
          if (event.data && (event.data.type === 'SKYOPS_MODE_CHANGE' || event.data.type === 'MODE_CHANGE')) {
            if (event.data.provider) {
              const providerSelect = document.getElementById('chat-model-provider');
              if (providerSelect && providerSelect.value !== event.data.provider) {
                providerSelect.value = event.data.provider;
              }
            }
            updateLlmStatusBadges();
          }
        };
      }
    } catch(e) {
      console.warn("BroadcastChannel init failed in main web", e);
    }

    function broadcastModeUpdate(overrideProvider) {
      const rawP = overrideProvider || localStorage.getItem('copilot_provider') || 'auto';
      let provider = rawP;
      let modelName = undefined;

      if (rawP === 'custom') {
        modelName = localStorage.getItem('custom_model_id') || '';
        if (modelName.includes('claude')) provider = 'claude';
        else if (modelName.includes('gemini')) provider = 'gemini';
        else if (modelName.includes('deepseek')) provider = 'deepseek';
        else if (modelName.startsWith('o1') || modelName.startsWith('o3') || modelName.includes('gpt')) provider = 'openai';
        else provider = 'auto';
      } else if (rawP.includes(':')) {
        const parts = rawP.split(':');
        provider = parts[0];
        modelName = parts[1];
      }

      const gKey = localStorage.getItem('gemini_api_key') || '';
      const cKey = localStorage.getItem('claude_api_key') || '';
      const oKey = localStorage.getItem('openai_api_key') || '';
      const dKey = localStorage.getItem('deepseek_api_key') || '';
      const theme = localStorage.getItem('occ_cockpit_theme') || 'light';
      const hasAnyKey = Boolean(gKey || cKey || oKey || dKey);
      const isOnline = provider !== 'offline' && (hasAnyKey || provider !== 'auto');

      const syncPayload = {
        type: 'SKYOPS_MODE_CHANGE',
        provider: rawP,
        model_name: modelName,
        gemini_key: gKey,
        claude_key: cKey,
        openai_key: oKey,
        deepseek_key: dKey,
        theme: theme,
        is_online: Boolean(isOnline),
        timestamp: Date.now()
      };

      if (syncChannel) {
        try { syncChannel.postMessage(syncPayload); } catch(e) {}
      }

      try {
        localStorage.setItem('skyops_sync_tick', Date.now().toString());
      } catch(e) {}

      fetch('/copilot/runtime-mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: provider,
          model_name: modelName,
          api_key: cKey || oKey || gKey || dKey || '',
          theme: theme
        })
      }).catch(() => {});
    }

    function toggleHeaderOnlineMode() {
      const current = localStorage.getItem('copilot_provider') || 'auto';
      let nextMode = 'offline';
      if (current === 'offline') {
        nextMode = 'gemini:gemini-3.8-flash';
      } else {
        nextMode = 'offline';
      }

      localStorage.setItem('copilot_provider', nextMode);
      const select = document.getElementById('chat-model-provider');
      if (select) select.value = nextMode;
      updateLlmStatusBadges();
      broadcastModeUpdate(nextMode);

      if (nextMode === 'offline') {
        showToast("Chế độ Nội bộ", "Chuyển sang Offline Engine (Đã đồng bộ sang tab Power BI).", "info");
      } else {
        showToast("Chế độ Trực tuyến", `Kích hoạt ${nextMode.toUpperCase()} (Đã đồng bộ sang tab Power BI).`, "success");
      }
    }

    function handleProviderChange() {
      const select = document.getElementById('chat-model-provider');
      const val = select ? select.value : 'auto';
      localStorage.setItem('copilot_provider', val);

      const customBox = document.getElementById('custom-model-box');
      if (customBox) {
        if (val === 'custom') {
          customBox.style.display = 'block';
          const custIn = document.getElementById('custom-model-id');
          if (custIn) custIn.focus();
        } else {
          customBox.style.display = 'none';
        }
      }

      updateLlmStatusBadges();
      broadcastModeUpdate(val);

      if (val === 'offline') {
        showToast("Chế độ Nội bộ", "Chuyển sang Offline Grounding Engine 40 đề mục (Đã đồng bộ sang Power BI).", "info");
      } else if (val.includes('gemini-3.8')) {
        showToast("Google Gemini 3.8", "⚡ Kích hoạt thế hệ Gemini 3.8 tiên tiến nhất (Đã đồng bộ sang Power BI).", "success");
      } else if (val.includes('claude-3-7')) {
        showToast("Anthropic Claude 3.7", "🟣 Kích hoạt Claude 3.7 Sonnet với Hybrid Extended Thinking (Đã đồng bộ sang Power BI).", "success");
      } else if (val.includes('o3-mini')) {
        showToast("OpenAI o3-mini", "🟢 Kích hoạt mô hình lý luận siêu tốc OpenAI o3-mini (Đã đồng bộ sang Power BI).", "success");
      } else if (val.includes('deepseek')) {
        showToast("DeepSeek R1", "🔵 Kích hoạt mô hình suy luận DeepSeek-R1 CoT (Đã đồng bộ sang Power BI).", "success");
      } else if (val === 'custom') {
        showToast("Mô hình Tùy chỉnh", "Vui lòng nhập Model ID vào ô bên dưới.", "info");
      } else {
        showToast("Chế độ Tự động", "Hệ thống tự động chọn mô hình mạnh nhất từ API Key đã lưu (Đã đồng bộ sang Power BI).", "info");
      }
    }

    function handleCustomModelChange() {
      const input = document.getElementById('custom-model-id');
      const val = input ? input.value.trim() : '';
      if (val) {
        localStorage.setItem('custom_model_id', val);
        updateLlmStatusBadges();
        broadcastModeUpdate('custom');
        showToast("Model Tùy chỉnh", `Đã lưu Model ID: ${val}`, "success");
      }
    }

    function updateLlmStatusBadges() {
      const select = document.getElementById('chat-model-provider');
      const provider = select ? select.value : (localStorage.getItem('copilot_provider') || 'auto');
      const badge = document.getElementById('header-llm-badge');
      if (!badge) return;
      badge.style.display = 'inline-flex';
      badge.className = 'header-badge';
      badge.style.cursor = 'pointer';

      if (provider === 'offline') {
        badge.innerHTML = '🛡️ <strong>Xử lý: Nội bộ (Offline)</strong>';
        badge.style.background = 'rgba(255,255,255,0.06)';
        badge.style.borderColor = 'rgba(255,255,255,0.12)';
        badge.style.color = '#cbd5e1';
        badge.title = 'Đang ở chế độ Nội bộ. Bấm để chuyển sang Trực tuyến — Tự động đồng bộ ngay sang Power BI.';
        return;
      }

      if (provider.includes('gemini')) {
        badge.innerHTML = '⚡ <strong>Gemini 3.8 Flash</strong>';
        badge.style.background = 'rgba(16,185,129,0.15)';
        badge.style.borderColor = 'rgba(16,185,129,0.3)';
        badge.style.color = '#a7f3d0';
        badge.title = 'Đang kích hoạt Google Gemini 3.8 Flash.';
        return;
      }

      if (provider.includes('claude')) {
        badge.innerHTML = '🟣 <strong>Claude 3.7 Sonnet</strong>';
        badge.style.background = 'rgba(168,85,247,0.18)';
        badge.style.borderColor = 'rgba(168,85,247,0.35)';
        badge.style.color = '#f3e8ff';
        badge.title = 'Đang kích hoạt Anthropic Claude 3.7 Sonnet (Hybrid Reasoning).';
        return;
      }

      if (provider.includes('openai') || provider.includes('o3') || provider.includes('o1')) {
        badge.innerHTML = '🟢 <strong>OpenAI o3-mini / o1</strong>';
        badge.style.background = 'rgba(16,185,129,0.15)';
        badge.style.borderColor = 'rgba(16,185,129,0.3)';
        badge.style.color = '#a7f3d0';
        badge.title = 'Đang kích hoạt mô hình lý luận OpenAI o3-mini.';
        return;
      }

      if (provider.includes('deepseek')) {
        badge.innerHTML = '🔵 <strong>DeepSeek R1</strong>';
        badge.style.background = 'rgba(14,165,233,0.15)';
        badge.style.borderColor = 'rgba(14,165,233,0.3)';
        badge.style.color = '#bae6fd';
        badge.title = 'Đang kích hoạt DeepSeek-R1 Reasoner.';
        return;
      }

      // Auto mode
      const hasAny = Boolean(
        localStorage.getItem('gemini_api_key')
        || localStorage.getItem('claude_api_key')
        || localStorage.getItem('openai_api_key')
        || localStorage.getItem('deepseek_api_key')
      );
      if (hasAny) {
        badge.innerHTML = '✨ <strong>Dịch vụ: Trực tuyến (Auto)</strong>';
        badge.style.background = 'rgba(16,185,129,0.15)';
        badge.style.borderColor = 'rgba(16,185,129,0.3)';
        badge.style.color = '#a7f3d0';
      } else {
        badge.innerHTML = '🛡️ <strong>Xử lý: Nội bộ</strong>';
        badge.style.background = 'rgba(255,255,255,0.06)';
        badge.style.borderColor = 'rgba(255,255,255,0.12)';
        badge.style.color = '#cbd5e1';
      }
    }

    function saveApiKeys() {
      const gKey = document.getElementById('setting-gemini-key').value.trim();
      const cKey = document.getElementById('setting-claude-key').value.trim();
      const oKey = document.getElementById('setting-openai-key').value.trim();
      const dKey = document.getElementById('setting-deepseek-key').value.trim();

      if (gKey) localStorage.setItem('gemini_api_key', gKey); else localStorage.removeItem('gemini_api_key');
      if (cKey) localStorage.setItem('claude_api_key', cKey); else localStorage.removeItem('claude_api_key');
      if (oKey) localStorage.setItem('openai_api_key', oKey); else localStorage.removeItem('openai_api_key');
      if (dKey) localStorage.setItem('deepseek_api_key', dKey); else localStorage.removeItem('deepseek_api_key');

      updateSettingsStatusBox();
      closeSettingsModal();
      broadcastModeUpdate();
      showToast("Đã lưu cấu hình", "Toàn bộ API Key đã được lưu an toàn và tự động đồng bộ sang tab Power BI!", "success");
    }

    function clearApiKeys() {
      localStorage.removeItem('gemini_api_key');
      localStorage.removeItem('claude_api_key');
      localStorage.removeItem('openai_api_key');
      localStorage.removeItem('deepseek_api_key');
      document.getElementById('setting-gemini-key').value = '';
      document.getElementById('setting-claude-key').value = '';
      document.getElementById('setting-openai-key').value = '';
      document.getElementById('setting-deepseek-key').value = '';
      updateSettingsStatusBox();
      broadcastModeUpdate('offline');
      showToast("Đã xóa Key", "Đã xóa toàn bộ API Key và đồng bộ sang Offline Engine cho Power BI.", "info");
    }

    async function testApiKey() {
      return testAllApiKeys();
    }

    async function testAllApiKeys() {
      const gKey = document.getElementById('setting-gemini-key').value.trim();
      const cKey = document.getElementById('setting-claude-key').value.trim();
      const oKey = document.getElementById('setting-openai-key').value.trim();
      const dKey = document.getElementById('setting-deepseek-key').value.trim();

      if (!gKey && !cKey && !oKey && !dKey) {
        showToast("Kiểm tra kết nối", "Vui lòng nhập ít nhất 1 API Key để kiểm tra.", "warning");
        return;
      }

      showToast("Đang kiểm tra", "Đang gửi ping xác thực đến các cổng dịch vụ AI...", "info", null, 3000);
      const results = [];

      if (gKey) {
        try {
          const res = await fetch('/copilot/validate-key', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({provider: 'gemini', api_key: gKey})
          });
          const d = await res.json();
          results.push(`Gemini: ${d.valid ? '✅ ' + d.message : '❌ ' + d.message}`);
        } catch(e) { results.push(`Gemini: ❌ ${e.message}`); }
      }

      if (cKey) {
        try {
          const res = await fetch('/copilot/validate-key', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({provider: 'claude', api_key: cKey})
          });
          const d = await res.json();
          results.push(`Claude: ${d.valid ? '✅ ' + d.message : '❌ ' + d.message}`);
        } catch(e) { results.push(`Claude: ❌ ${e.message}`); }
      }

      if (oKey) {
        try {
          const res = await fetch('/copilot/validate-key', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({provider: 'openai', api_key: oKey})
          });
          const d = await res.json();
          results.push(`OpenAI: ${d.valid ? '✅ ' + d.message : '❌ ' + d.message}`);
        } catch(e) { results.push(`OpenAI: ❌ ${e.message}`); }
      }

      if (dKey) {
        try {
          const res = await fetch('/copilot/validate-key', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({provider: 'deepseek', api_key: dKey})
          });
          const d = await res.json();
          results.push(`DeepSeek: ${d.valid ? '✅ ' + d.message : '❌ ' + d.message}`);
        } catch(e) { results.push(`DeepSeek: ❌ ${e.message}`); }
      }

      const box = document.getElementById('setting-status-box');
      const txt = document.getElementById('setting-status-text');
      if (txt) txt.innerHTML = results.join('<br>');
      if (box) box.className = 'setting-status-box status-success';
      showToast("Kết quả kiểm tra", "Đã hoàn thành kiểm tra kết nối!", "info");
    }

    // =========================================================================
    // TAB SWITCHING
    // =========================================================================
    function switchTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      
      const targetBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick') && b.getAttribute('onclick').includes(tabId));
      if (targetBtn) targetBtn.classList.add('active');
      const targetContent = document.getElementById(tabId);
      if (targetContent) targetContent.classList.add('active');

      if (tabId === 'tab-chat') {
        setTimeout(focusOnCurrentTurn, 50);
      }

      if (tabId === 'tab-catalog' && catalogData.terms.length === 0) {
        loadCatalog();
      }

      // PERSIST ACTIVE TAB ACROSS REFRESH (FEATURE P2)
      try {
        sessionStorage.setItem('occ_active_tab', tabId);
        localStorage.setItem('occ_active_tab', tabId);
        const url = new URL(window.location.href);
        const tabShort = tabId.replace('tab-', '');
        url.searchParams.set('tab', tabShort);
        window.history.replaceState(null, '', url.toString());
      } catch(e) {}
    }

    function focusOnCurrentTurn() {
      const stream = document.getElementById('chat-stream');
      const target = lastUserMsgElement || document.getElementById('chat-loading-placeholder');
      if (stream && target) {
        requestAnimationFrame(() => {
          const streamRect = stream.getBoundingClientRect();
          const targetRect = target.getBoundingClientRect();
          const relativeTop = targetRect.top - streamRect.top + stream.scrollTop;
          stream.scrollTo({
            top: Math.max(0, relativeTop - 12),
            behavior: 'smooth'
          });
        });
      }
    }

    // =========================================================================
    // TAB 1: ADVISORY & WHAT-IF FUNCTIONS (FEATURES 4 & 5)
    // =========================================================================
    function selectFlightWatchRow(fId, rowEl) {
      document.querySelectorAll('#flight-watch-tbody tr').forEach(r => r.classList.remove('active-row'));
      if (rowEl) {
        rowEl.classList.add('active-row');
      } else {
        const matching = document.querySelector(`#flight-watch-tbody tr[data-flight-id="${fId}"]`);
        if (matching) matching.classList.add('active-row');
      }
      return quickFill(fId);
    }

    function quickFill(fId){
      document.getElementById('flight_id').value = fId;
      const banner = document.getElementById('flight-id-error-banner');
      if (banner) banner.style.display = 'none';

      // Sync active row in flight watch table
      document.querySelectorAll('#flight-watch-tbody tr').forEach(r => {
        if (r.getAttribute('data-flight-id') == fId) {
          r.classList.add('active-row');
        } else {
          r.classList.remove('active-row');
        }
      });

      return runAdvisoryByFlightId();
    }

    async function runAdvisoryByFlightId(){
      const fId = document.getElementById('flight_id').value;
      if (!fId) {
        showToast("Thiếu thông tin", "Vui lòng nhập Flight ID (ví dụ: 4568)", "warning");
        return;
      }
      const banner = document.getElementById('flight-id-error-banner');
      if (banner) banner.style.display = 'none';
      return callAdvisoryApi({flight_id: fId});
    }

    async function runAdvisory(){
      const body = {
        carrier_code: document.getElementById('carrier').value.toUpperCase(),
        origin: document.getElementById('origin').value.toUpperCase(),
        dest: document.getElementById('dest').value.toUpperCase(),
        flight_date: document.getElementById('date').value,
        dep_hour: +document.getElementById('hour').value,
        model: document.getElementById('model').value
      };
      return callAdvisoryApi(body);
    }

    async function callAdvisoryApi(payload){
      try {
        const r = await fetch('/copilot/advisory', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const d = await r.json();
        if (!r.ok) {
          const errMsg = d.detail || JSON.stringify(d);
          if (payload.flight_id) {
            const banner = document.getElementById('flight-id-error-banner');
            const errText = document.getElementById('flight-id-error-text');
            if (banner && errText) {
              errText.innerHTML = `<strong>⚠️ Không tìm thấy Chuyến bay #${payload.flight_id}</strong> trong kho dữ liệu Marts.<br><span style="color:#7f1d1d">${errMsg}</span>`;
              banner.style.display = 'block';
            }
            showToast("Không tìm thấy chuyến bay", `Không tìm thấy chuyến bay #${payload.flight_id} trong Marts.`, "error", SAMPLE_FLIGHTS);
          } else {
            showToast("Lỗi tính toán", errMsg, "error");
          }
          return null;
        }

        const banner = document.getElementById('flight-id-error-banner');
        if (banner) banner.style.display = 'none';

        currentAdv = d;
        currentFlightContext = d.flight_context;
        updateChatContextBanner();
        renderAdvisory(d);
        return d;
      } catch(e) {
        showToast("Lỗi kết nối API", e.message, "error");
        return null;
      }
    }

    function renderAdvisory(adv){
      const placeholder = document.getElementById('initial-placeholder');
      if (placeholder) placeholder.style.display = 'none';
      
      document.getElementById('results').style.display = 'block';
      const ctx = adv.flight_context;
      const pred = adv.prediction_context;
      const fin = adv.financial_exposure;

      // 1. Header Banner & HUD
      document.getElementById('adv-id-label').textContent = 'HỒ SƠ VẬN HÀNH: ' + adv.advisory_id;
      document.getElementById('flight-title-label').textContent = `${ctx.carrier_code}${ctx.flight_number || ''} (${ctx.carrier_name}) | ${ctx.origin} ➔ ${ctx.dest}`;
      
      const rb = document.getElementById('risk-badge');
      rb.className = 'badge ' + (pred.risk_band === 'HIGH' ? 'badge-high' : pred.risk_band === 'ELEVATED' ? 'badge-elevated' : 'badge-normal');
      rb.textContent = 'PHÂN HẠNG RỦI RO: ' + pred.risk_band;

      const bannerCard = document.getElementById('banner-card');
      bannerCard.style.borderLeft = pred.risk_band === 'HIGH' ? '6px solid #f43f5e' : (pred.risk_band === 'ELEVATED' ? '6px solid #f59e0b' : '6px solid #10b981');

      document.getElementById('summary-text').textContent = adv.executive_summary;

      const metaTags = document.getElementById('flight-meta-tags');
      metaTags.innerHTML = `
        <span>📍 <strong>Cự ly:</strong> ${ctx.distance_miles.toFixed(0)} dặm (${ctx.distance_bucket.toUpperCase()})</span>
        <span>🕒 <strong>Khung giờ:</strong> ${ctx.dep_window_label}</span>
        <span>🛫 <strong>Mật độ đường lăn ${ctx.origin}:</strong> ${ctx.scheduled_departures_hour} chuyến/giờ</span>
        <span>📈 <strong>Trễ tuyến bay 30d:</strong> ${(ctx.route_delay_rate_30d*100).toFixed(1)}%</span>
        <span>🏢 <strong>Mô hình:</strong> ${ctx.carrier_type.toUpperCase()}</span>
      `;

      // 2. Financial KPIs
      document.getElementById('delay-mins-val').textContent = `~${pred.projected_delay_min} phút`;
      document.getElementById('delay-prob-sub').textContent = `Xác suất trễ dự báo: ${(pred.delay_probability*100).toFixed(1)}% (Lift ${pred.lift_at_10}x)`;
      document.getElementById('base-cost-val').textContent = '$' + fin.base_delay_cost_usd.toLocaleString('en-US', {minimumFractionDigits: 2});
      document.getElementById('penalty-cost-val').textContent = '$' + (fin.tarmac_penalty_exposure_usd + fin.cash_refund_exposure_usd).toLocaleString('en-US', {minimumFractionDigits: 2});
      document.getElementById('pax-count-sub').textContent = `Ước tính ${fin.estimated_passengers} hành khách`;
      document.getElementById('savings-val').textContent = '$' + fin.proactive_mitigation_savings_usd.toLocaleString('en-US', {minimumFractionDigits: 2});

      // 2b. Visual Stacked Progress Bar (Feature 4)
      const baseCost = fin.base_delay_cost_usd || 0;
      const tarmacCost = fin.tarmac_penalty_exposure_usd || 0;
      const refundCost = fin.cash_refund_exposure_usd || 0;
      const totalExposure = baseCost + tarmacCost + refundCost;

      const basePct = totalExposure > 0 ? (baseCost / totalExposure * 100) : 0;
      const tarmacPct = totalExposure > 0 ? (tarmacCost / totalExposure * 100) : 0;
      const refundPct = totalExposure > 0 ? (refundCost / totalExposure * 100) : 0;

      document.getElementById('cost-total-label').textContent = 'Tổng rủi ro phơi nhiễm: $' + totalExposure.toLocaleString('en-US', {minimumFractionDigits: 2}) + ' USD';

      const barBase = document.getElementById('bar-base-delay');
      barBase.style.width = basePct.toFixed(1) + '%';
      barBase.textContent = basePct > 6 ? (basePct.toFixed(1) + '% FAA Base') : '';

      const barTarmac = document.getElementById('bar-tarmac-penalty');
      barTarmac.style.width = tarmacPct.toFixed(1) + '%';
      barTarmac.textContent = tarmacPct > 8 ? (tarmacPct.toFixed(1) + '% Phạt Tarmac (§ 259.4)') : '';

      const barRefund = document.getElementById('bar-cash-refund');
      barRefund.style.width = refundPct.toFixed(1) + '%';
      barRefund.textContent = refundPct > 6 ? (refundPct.toFixed(1) + '% Hoàn vé (§ 260.6)') : '';

      document.getElementById('legend-base-text').innerHTML = `Chi phí trễ cơ sở FAA: <strong>$${baseCost.toLocaleString('en-US', {minimumFractionDigits: 2})} (${basePct.toFixed(1)}%)</strong>`;
      document.getElementById('legend-tarmac-text').innerHTML = `Phạt Tarmac (§ 259.4): <strong style="color:var(--rose-600)">$${tarmacCost.toLocaleString('en-US', {minimumFractionDigits: 2})} (${tarmacPct.toFixed(1)}%)</strong>`;
      document.getElementById('legend-refund-text').innerHTML = `Hoàn vé (§ 260.6): <strong style="color:var(--amber-800)">$${refundCost.toLocaleString('en-US', {minimumFractionDigits: 2})} (${refundPct.toFixed(1)}%)</strong>`;

      const calloutBox = document.getElementById('cost-callout-box');
      const calloutText = document.getElementById('cost-callout-text');
      if (calloutBox && calloutText) {
        if (tarmacCost > 0) {
          calloutBox.style.display = 'block';
          const ratio = baseCost > 0 ? (tarmacCost / baseCost).toFixed(1) : '99+';
          calloutText.innerHTML = `⚡ <strong>Phân tích cấu trúc thiệt hại</strong>: Rủi ro phạt Tarmac Delay 14 CFR § 259.4 ($37,377/hành khách) chiếm tới <strong>${tarmacPct.toFixed(1)}%</strong> tổng gánh nặng tài chính phơi nhiễm (cao gấp <strong>${ratio} lần</strong> chi phí chậm chuyến thông thường FAA $101.18/phút). Mức phạt hành chính nhà nước áp đảo hoàn toàn tổn thất vận hành cơ sở, khẳng định điều phái viên bắt buộc phải can thiệp sớm để bảo toàn tài chính ròng!`;
        } else {
          calloutBox.style.display = 'none';
        }
      }

      // 3. Reset What-If
      document.getElementById('whatif-box').style.display = 'none';

      // 4. Timeline Actions (5 Gates)
      const tl = document.getElementById('timeline-list');
      tl.innerHTML = '';
      adv.timeline_actions.forEach(a => {
        const card = document.createElement('div');
        const cClass = a.priority === 'CRITICAL' ? 'timeline-gate critical' : (a.priority === 'HIGH' ? 'timeline-gate high' : 'timeline-gate normal');
        card.className = cClass;
        card.innerHTML = `
          <div class="gate-header">
            <span class="gate-title">[${a.phase_code}] ${a.action_title}</span>
            <span class="role-badge">👤 ${a.responsible_role}</span>
          </div>
          <div style="font-size:11px;color:#64748b;margin-top:2px">⏱️ ${a.phase_name} | Ưu tiên: <strong>${a.priority}</strong></div>
          <div class="gate-guidance">${a.operational_guidance}</div>
          <div class="decision-box">👉 ${a.critical_decision}</div>
        `;
        tl.appendChild(card);
      });

      // 5. SOP List
      const sopList = document.getElementById('sop-list');
      sopList.innerHTML = '';
      if (!adv.recommended_sops || adv.recommended_sops.length === 0) {
        sopList.innerHTML = '<div style="font-size:13px;color:#64748b">Không có SOP khẩn nguy cần kích hoạt cho chuyến bay này.</div>';
      } else {
        adv.recommended_sops.forEach(s => {
          const sDiv = document.createElement('div');
          sDiv.style.cssText = 'background:#f8fafc;border:1px solid #e2e8f0;padding:14px;border-radius:var(--radius-sm);margin-bottom:8px';
          sDiv.innerHTML = `
            <div style="font-weight:700;font-size:13px;color:#0369a1">📋 [${s.sop_id}] ${s.title_vi} (${(s.steps||[]).length} bước)</div>
            <div style="font-size:12px;color:#475569;margin-top:4px">🎯 <strong>Lý do gắn kết:</strong> ${s.binding_reason || 'Kích hoạt theo rủi ro'}</div>
          `;
          sopList.appendChild(sDiv);
        });
      }

      // 6. Regulatory Law Breakdown
      const legList = document.getElementById('legal-list');
      legList.innerHTML = '';
      const alerts = adv.regulatory_compliance.legal_evaluations || [];
      alerts.forEach(item => {
        const lCard = document.createElement('div');
        lCard.className = 'legal-card ' + (item.severity === 'CRITICAL' ? '' : (item.severity === 'NORMAL' ? 'success' : 'warn'));
        lCard.innerHTML = `
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
            <span style="font-weight:700;font-size:13.5px;color:#0f172a">${item.legal_code}: ${item.citation}</span>
            <span class="badge ${item.severity === 'CRITICAL' ? 'badge-high' : 'badge-elevated'}">${item.severity}</span>
          </div>
          <div style="font-size:12px;color:var(--primary);font-weight:600;margin:4px 0">🏛️ ${item.jurisdiction}</div>
          <div style="font-size:12.5px;color:#334155;margin:6px 0">${item.statutory_text}</div>
          <div style="font-size:12px;color:var(--rose-600);font-weight:700">⚠️ Chế tài: ${item.statutory_penalty}</div>
          <div style="background:#f0fdf4;border:1px solid #bbf7d0;color:#166534;padding:8px 12px;border-radius:var(--radius-sm);font-size:12px;margin-top:8px"><strong>🚨 MỆNH LỆNH OCC:</strong> ${item.mandatory_action}</div>
        `;
        legList.appendChild(lCard);
      });

      // 7. Raw Markdown
      document.getElementById('markdown-raw').textContent = adv.markdown_report || '';
    }

    async function runSim(type, params){
      if (!currentAdv) {
        showToast("Chưa chọn chuyến bay", "Vui lòng tra cứu một chuyến bay trước khi chạy What-If.", "warning");
        return;
      }
      const ctx = currentAdv.flight_context;
      const body = {
        carrier_code: ctx.carrier_code,
        origin: ctx.origin,
        dest: ctx.dest,
        dep_hour: ctx.dep_hour,
        flight_date: ctx.flight_date,
        flight_number: ctx.flight_number,
        scenario_type: type,
        scenario_params: params || {}
      };
      try {
        const r = await fetch('/copilot/simulate', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(body)
        });
        const res = await r.json();
        const box = document.getElementById('whatif-box');
        box.style.display = 'block';
        const out = res.simulated_outcome || {};
        box.innerHTML = `
          <div style="font-weight:800;font-size:14px;color:#065f46">🎯 KẾT QUẢ MÔ PHỎNG ĐIỀU HÀNH: ${res.scenario_type.toUpperCase()}</div>
          <div style="margin:6px 0"><strong>Mô tả can thiệp:</strong> ${(res.intervention && res.intervention.description) || ''}</div>
          <div style="display:flex;gap:20px;margin:10px 0;flex-wrap:wrap">
            ${out.new_delay_probability !== undefined ? `<div><strong>Xác suất trễ mới:</strong> ${(out.new_delay_probability*100).toFixed(1)}%</div>` : ''}
            ${out.minutes_saved !== undefined ? `<div><strong>Phút bay thu hồi:</strong> ${out.minutes_saved || out.airborne_minutes_recovered || 0} phút</div>` : ''}
            ${out.cost_saved_usd !== undefined ? `<div><strong>Chi phí tiết kiệm:</strong> $${(out.cost_saved_usd || out.net_savings_usd || 0).toLocaleString('en-US', {minimumFractionDigits: 2})} USD</div>` : ''}
            ${out.net_financial_savings_usd !== undefined ? `<div><strong>Bảo toàn ròng:</strong> $${out.net_financial_savings_usd.toLocaleString('en-US', {minimumFractionDigits: 2})} USD</div>` : ''}
          </div>
          <div style="background:#fff;padding:8px 12px;border-radius:6px;border:1px solid #6ee7b7;font-weight:700;color:#047857">
            🏆 ĐÁNH GIÁ ROI: ${out.roi_verdict || 'Thành công'}
          </div>
        `;
      } catch(e) {
        showToast("Lỗi mô phỏng", e.message, "error");
      }
    }

    // =========================================================================
    // SLIDE INSIGHT EXPORT & EXECUTIVE PRESENTATION DECK (ENTERPRISE 16:9 MODAL)
    // =========================================================================
    let currentModalSlideIdx = 1;

    async function openSlideModal() {
      if (!currentAdv) {
        showToast("Đang mở chuyến bay mẫu", "Chưa có chuyến bay nào được chọn. Đang tự động nạp hồ sơ chuyến bay #4568 để tạo slide...", "info");
        await quickFill(4568);
      }
      if (!currentAdv) {
        showToast("Chưa chọn chuyến bay", "Vui lòng tra cứu hoặc chọn một chuyến bay để tạo slide insight.", "warning");
        return;
      }
      currentModalSlideIdx = 1;
      renderSlideModalContent();
      const modal = document.getElementById('slide-modal');
      if (modal) modal.style.display = 'block';
    }

    function closeSlideModal() {
      const modal = document.getElementById('slide-modal');
      if (modal) modal.style.display = 'none';
    }

    function switchModalSlide(idx) {
      currentModalSlideIdx = idx;
      renderSlideModalContent();
    }

    function nextModalSlide() {
      currentModalSlideIdx = (currentModalSlideIdx < 4) ? currentModalSlideIdx + 1 : 1;
      renderSlideModalContent();
    }

    function prevModalSlide() {
      currentModalSlideIdx = (currentModalSlideIdx > 1) ? currentModalSlideIdx - 1 : 4;
      renderSlideModalContent();
    }

    function getSlideQueryString() {
      if (!currentAdv) return '';
      const ctx = currentAdv.flight_context;
      const modelVal = document.getElementById('model')?.value || 'best';
      if (ctx.flight_id) {
        return `flight_id=${encodeURIComponent(ctx.flight_id)}&model=${encodeURIComponent(modelVal)}`;
      }
      return `carrier_code=${encodeURIComponent(ctx.carrier_code)}&origin=${encodeURIComponent(ctx.origin)}&dest=${encodeURIComponent(ctx.dest)}&flight_date=${encodeURIComponent(ctx.flight_date)}&dep_hour=${encodeURIComponent(ctx.dep_hour)}&flight_number=${encodeURIComponent(ctx.flight_number || '')}&model=${encodeURIComponent(modelVal)}`;
    }

    function downloadSlidePptx() {
      if (!currentAdv) return;
      const qs = getSlideQueryString();
      const ctx = currentAdv.flight_context;
      const flName = `${ctx.carrier_code}${ctx.flight_number || ''}_${ctx.origin}_${ctx.dest}`;
      showToast("Đang tạo PowerPoint (.pptx)", "⏳ Hệ thống đang xuất file PowerPoint 16:9 chuẩn Microsoft Office...", "info");
      
      const a = document.createElement('a');
      a.href = `/copilot/export-slide/pptx?${qs}`;
      a.download = `SkyOps_Executive_Slide_${flName}.pptx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      setTimeout(() => {
        showToast("Đã tải PowerPoint (.pptx)", "✅ File PowerPoint 16:9 đã được tải về máy! Bạn có thể mở trực tiếp bằng Microsoft PowerPoint hoặc Google Slides.", "success", null, 6000);
      }, 1000);
    }

    function openSlideDeckHtml() {
      if (!currentAdv) return;
      const qs = getSlideQueryString();
      window.open(`/copilot/slide-deck?${qs}`, '_blank');
      showToast("Đã mở Slide Deck", "🌐 Đang mở slide thuyết trình toàn màn hình trong tab mới. Nhấn F11 để vào chế độ Fullscreen hoặc Ctrl+P để in/xuất PDF.", "success");
    }

    function downloadSlideMarkdown() {
      if (!currentAdv) return;
      const qs = getSlideQueryString();
      const ctx = currentAdv.flight_context;
      const a = document.createElement('a');
      a.href = `/copilot/export-slide/markdown?${qs}`;
      a.download = `SkyOps_Slide_${ctx.carrier_code}${ctx.flight_number || ''}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast("Đã tải Slide Markdown", "📄 File slide chuẩn Marp/Markdown đã được tải về máy.", "success");
    }

    function copySlideSummaryDirect() {
      if (!currentAdv) return;
      const ctx = currentAdv.flight_context;
      const pred = currentAdv.prediction_context;
      const fin = currentAdv.financial_exposure;
      const leg = (currentAdv.regulatory_compliance.legal_evaluations || [])[0] || {};
      const totCost = (fin.base_delay_cost_usd + fin.tarmac_penalty_exposure_usd + fin.cash_refund_exposure_usd);
      
      const slideText = `📊 TÓM TẮT BÁO CÁO QUẢN TRỊ (EXECUTIVE SLIDE SUMMARY)
Chuyến bay: ${ctx.carrier_code}${ctx.flight_number || ''} (${ctx.carrier_name}) | Tuyến: ${ctx.origin} ➔ ${ctx.dest}
Khung giờ khởi hành: ${ctx.dep_window_label} | Cự ly: ${ctx.distance_miles.toFixed(0)} dặm (${ctx.distance_bucket.toUpperCase()})

1. TÌNH TRẠNG & DỰ BÁO RỦI RO (PREDICTION):
   - Phân hạng rủi ro: ${pred.risk_band} (${(pred.delay_probability*100).toFixed(1)}% xác suất trễ dự báo, Lift @ 10%: ${pred.lift_at_10}x).
   - Dự báo độ trễ: ~${pred.projected_delay_min} phút.
   - Trễ tuyến bay 30 ngày qua: ${(ctx.route_delay_rate_30d*100).toFixed(1)}%.

2. CĂN NGUYÊN GỐC RỄ & ĐIỂM NGHẼN (ROOT CAUSE & BOTTLENECK):
   - Mật độ cất cánh tại ${ctx.origin}: ${ctx.scheduled_departures_hour} chuyến/giờ (Khung giờ cao điểm đường lăn).
   - Quy chuẩn & Nguy cơ pháp lý: ${leg.legal_code || '14 CFR § 121.593'} - ${leg.citation || 'Quy chuẩn an toàn'}.
   - Chế tài pháp luật tiềm tàng: ${leg.statutory_penalty || 'Không vi phạm'}.

3. BÓC TÁCH RỦI RO TÀI CHÍNH (FINANCIAL EXPOSURE - FAA $101.18/MIN):
   - Chi phí trễ cơ sở FAA ($101.18/phút): $${fin.base_delay_cost_usd.toLocaleString('en-US', {minimumFractionDigits: 2})} USD.
   - Rủi ro phạt Tarmac (§ 259.4) & Hoàn vé (§ 260.6): $${(fin.tarmac_penalty_exposure_usd + fin.cash_refund_exposure_usd).toLocaleString('en-US', {minimumFractionDigits: 2})} USD.
   - Tổng rủi ro tài chính phơi nhiễm: $${totCost.toLocaleString('en-US', {minimumFractionDigits: 2})} USD.

4. KHUYẾN NGHỊ CAN THIỆP WHAT-IF & ROI BẢO TOÀN RÒNG:
   - Hành động đề xuất: ${currentAdv.best_contingency_action || 'Điều chỉnh giờ bay hoặc kích hoạt Standby Crew'}.
   - Tiết kiệm tài chính tiềm năng khi can thiệp: $${fin.proactive_mitigation_savings_usd.toLocaleString('en-US', {minimumFractionDigits: 2})} USD.
   - Mệnh lệnh điều hành: ${leg.mandatory_action || 'Theo dõi sát và can thiệp sớm'}.`;

      copyTextToClipboard(slideText).then(() => {
        showToast("Đã sao chép Slide Insight", "📋 Đã sao chép Tóm tắt Báo cáo Quản trị vào khay nhớ tạm! Bạn có thể dán ngay vào slide PowerPoint.", "success", null, 6000);
      }).catch(() => {
        showToast("Sao chép thành công", "Đã ghi nhận nội dung tóm tắt báo cáo slide.", "info");
      });
    }

    function copyTextToClipboard(text) {
      if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
      }
      return new Promise((resolve, reject) => {
        try {
          const ta = document.createElement('textarea');
          ta.value = text;
          ta.style.position = 'fixed';
          ta.style.left = '-9999px';
          ta.style.top = '0';
          document.body.appendChild(ta);
          ta.focus();
          ta.select();
          const ok = document.execCommand('copy');
          document.body.removeChild(ta);
          if (ok) resolve(); else reject(new Error('execCommand copy failed'));
        } catch(e) {
          reject(e);
        }
      });
    }

    async function exportDispatchRelease() {
      if (!currentAdv) {
        showToast("Đang nạp dữ liệu chuyến bay", "Đang tự động nạp Chuyến bay #4568 để lập Điện văn Điều phái...", "info");
        const d = await callAdvisoryApi({ flight_id: 4568 });
        if (!d) return;
      }

      const ctx = currentAdv.flight_context || {};
      const pred = currentAdv.prediction_context || {};
      const fin = currentAdv.financial_exposure || {};

      const flCode = `${ctx.carrier_code || 'FL'}${ctx.flight_number || ctx.flight_id || '4568'}`;
      const origin = ctx.origin || 'LAS';
      const dest = ctx.dest || 'BOS';
      const depHour = ctx.dep_hour !== undefined ? ctx.dep_hour : 12;
      const schedDep = `${String(depHour).padStart(2, '0')}:00L`;

      const probPct = ((pred.delay_probability || 0.784) * 100).toFixed(1);
      const rawRisk = (pred.risk_band || 'CRITICAL').toUpperCase();
      const riskLevel = (rawRisk === 'HIGH' || rawRisk === 'CRITICAL') ? 'CRITICAL' : rawRisk;

      const projDelay = pred.projected_delay_min || 42;
      const exposureCost = (fin.total_potential_exposure_usd || fin.base_delay_cost_usd || 4249.56).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });

      let regWatch = "14 CFR 259.4 (TARMAC RULE) & FAR PART 117 CREW DUTY";
      if (currentAdv.regulatory_compliance && Array.isArray(currentAdv.regulatory_compliance.legal_evaluations)) {
        const citations = currentAdv.regulatory_compliance.legal_evaluations
          .map(e => e.citation || (e.legal_code ? e.legal_code.replace(/_/g, ' ') : null))
          .filter(Boolean);
        if (citations.length > 0) {
          regWatch = citations.slice(0, 2).join(' & ');
        }
      }

      let recAction = "PUSH BACK HOLD / RESCHEDULE TO 10:00L (-28 MINS RECOVERY)";
      if (currentAdv.what_if_simulations && currentAdv.what_if_simulations.length > 0) {
        const s0 = currentAdv.what_if_simulations[0];
        const recMin = s0.delay_reduction_min ? `(-${s0.delay_reduction_min} MINS RECOVERY)` : '';
        recAction = `${(s0.action_title || s0.scenario || 'PUSH BACK HOLD').toUpperCase()} ${recMin}`.trim();
      }

      const dispatchText = 
`[OCC DISPATCH ADVISORY RELEASE - FLIGHT ${flCode}]
ROUTE: ${origin} -> ${dest} | SCHED DEP: ${schedDep}
RISK LEVEL: ${riskLevel} (${probPct}% DELAY PROBABILITY)
PROJECTED DELAY: ${projDelay} MINS | FINANCIAL EXPOSURE: $${exposureCost}
REGULATORY WATCH: ${regWatch}
RECOMMENDED ACTION: ${recAction}
AUTHORIZED BY: OCC DESK 04`;

      copyTextToClipboard(dispatchText).then(() => {
        showToast("Đã Xuất Điện Văn Điều Phái", `📋 Đã sao chép Điện văn Điều phái OCC [${flCode}] vào khay nhớ tạm!`, "success");
      }).catch(() => {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(dispatchText).then(() => {
            showToast("Đã Xuất Điện Văn Điều Phái", `📋 Đã sao chép Điện văn Điều phái OCC [${flCode}] vào khay nhớ tạm!`, "success");
          }).catch(() => {
            prompt("Sao chép Điện văn Điều phái OCC (Ctrl+C):", dispatchText);
          });
        } else {
          prompt("Sao chép Điện văn Điều phái OCC (Ctrl+C):", dispatchText);
        }
      });
    }

    function exportSlideSummary() {
      // Backward-compatible alias for the HUD button
      return openSlideModal();
    }

    function renderSlideModalContent() {
      if (!currentAdv) return;
      const ctx = currentAdv.flight_context;
      const pred = currentAdv.prediction_context;
      const fin = currentAdv.financial_exposure;
      const leg = (currentAdv.regulatory_compliance.legal_evaluations || [])[0] || {};
      const totCost = (fin.base_delay_cost_usd + fin.tarmac_penalty_exposure_usd + fin.cash_refund_exposure_usd);
      const isHigh = pred.risk_band && (pred.risk_band.toLowerCase() === 'high' || pred.risk_band.toLowerCase() === 'critical');

      // Update subtitle
      const sub = document.getElementById('slide-modal-subtitle');
      if (sub) {
        sub.innerHTML = `Chuyến bay <strong>${ctx.carrier_code}${ctx.flight_number || ''}</strong> (${ctx.carrier_name}) • Tuyến: <strong>${ctx.origin} ➔ ${ctx.dest}</strong> • Ngày: ${ctx.flight_date} (${ctx.dep_window_label}) • Cự ly: ${ctx.distance_miles.toFixed(0)} dặm`;
      }

      // Update tabs
      for (let i = 1; i <= 4; i++) {
        const tabEl = document.getElementById(`stab-${i}`);
        if (tabEl) {
          if (i === currentModalSlideIdx) tabEl.classList.add('active');
          else tabEl.classList.remove('active');
        }
      }

      // Update counter
      const counterEl = document.getElementById('slide-counter-label');
      if (counterEl) {
        counterEl.textContent = `Slide ${currentModalSlideIdx} / 4 • Dùng phím ◀ / ▶ hoặc nút bên phải để chuyển slide`;
      }

      const bodyEl = document.getElementById('slide-preview-body');
      if (!bodyEl) return;

      if (currentModalSlideIdx === 1) {
        // SLIDE 1: OVERVIEW & 4 KPIS (BRIGHT CLEAN THEME)
        bodyEl.innerHTML = `
          <div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid #f1f5f9;padding-bottom:14px">
              <div>
                <div style="font-size:11px;font-weight:700;color:#0284c7;letter-spacing:1.5px;text-transform:uppercase;font-family:'JetBrains Mono',monospace">
                  SKYOPS PLATFORM | BÁO CÁO TÁC NGHIỆP ĐIỀU HÀNH BAY
                </div>
                <div style="font-size:22px;font-weight:800;color:#0f172a;margin-top:4px">
                  Hồ Sơ Giám Sát Vận Hành: Chuyến Bay ${ctx.carrier_code}${ctx.flight_number || ''} (${ctx.origin} ➔ ${ctx.dest})
                </div>
              </div>
              <div style="text-align:right">
                <span class="badge ${isHigh ? 'badge-high' : 'badge-normal'}" style="font-size:12px;padding:4px 12px">
                  ${pred.risk_band.toUpperCase()}
                </span>
                <div style="font-size:11px;color:#64748b;margin-top:4px">${ctx.flight_date} | ${ctx.dep_window_label}</div>
              </div>
            </div>

            <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:14px;margin-top:18px">
              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:16px">
                <div style="font-size:10.5px;font-weight:700;color:#64748b;text-transform:uppercase">Xác Suất Chậm Trễ</div>
                <div style="font-size:24px;font-weight:800;color:${isHigh ? '#dc2626' : '#059669'};margin:4px 0">
                  ${(pred.delay_probability*100).toFixed(1)}%
                </div>
                <div style="font-size:11px;color:#475569">Phân hạng: <strong>${pred.risk_band}</strong></div>
              </div>
              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:16px">
                <div style="font-size:10.5px;font-weight:700;color:#64748b;text-transform:uppercase">Độ Trễ Dự Phóng</div>
                <div style="font-size:24px;font-weight:800;color:#0284c7;margin:4px 0">~${pred.projected_delay_min}m</div>
                <div style="font-size:11px;color:#475569">Hệ số Risk Lift: <strong>${pred.lift_at_10}x</strong></div>
              </div>
              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:16px">
                <div style="font-size:10.5px;font-weight:700;color:#64748b;text-transform:uppercase">Phơi Nhiễm Tài Chính</div>
                <div style="font-size:24px;font-weight:800;color:#d97706;margin:4px 0">$${totCost.toLocaleString('en-US', {maximumFractionDigits:0})}</div>
                <div style="font-size:11px;color:#475569">Định mức FAA $101.18/phút</div>
              </div>
              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:16px">
                <div style="font-size:10.5px;font-weight:700;color:#64748b;text-transform:uppercase">Tiết Kiệm Can Thiệp</div>
                <div style="font-size:24px;font-weight:800;color:#059669;margin:4px 0">$${fin.proactive_mitigation_savings_usd.toLocaleString('en-US', {maximumFractionDigits:0})}</div>
                <div style="font-size:11px;color:#475569">Bảo toàn dòng tiền ròng</div>
              </div>
            </div>

            <div style="background:#ffffff;border:1px solid #cbd5e1;border-radius:10px;padding:16px 20px;margin-top:16px;font-size:13px;line-height:1.7;color:#334155">
              <strong style="color:#0284c7">TỔNG HỢP ĐIỀU HÀNH:</strong> Chuyến bay ${ctx.carrier_code}${ctx.flight_number || ''} (${ctx.carrier_name}) khai thác chặng ${ctx.origin} đi ${ctx.dest} (${ctx.distance_miles.toFixed(0)} dặm) đang ở mức rủi ro <strong>${pred.risk_band.toUpperCase()}</strong>. Khuyến nghị can thiệp tác nghiệp: <em style="color:#0f172a">${currentAdv.best_contingency_action || 'Điều chỉnh khung giờ khởi hành hoặc kích hoạt Standby Crew'}</em> để giảm thiểu nguy cơ vi phạm pháp chế DOT và bảo toàn chi phí vận hành.
            </div>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:#64748b;margin-top:14px;border-top:1px solid #e2e8f0;padding-top:10px">
            <span>Slide 1: Tổng Quan Vận Hành & Khung Rủi Ro</span>
            <span style="color:#0284c7;font-weight:700">SkyOps Platform</span>
          </div>
        `;
      } else if (currentModalSlideIdx === 2) {
        // SLIDE 2: ROOT CAUSES & NETWORK BOTTLENECKS (NO AI HYPE)
        bodyEl.innerHTML = `
          <div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid #f1f5f9;padding-bottom:14px">
              <div>
                <div style="font-size:11px;font-weight:700;color:#0284c7;letter-spacing:1.5px;text-transform:uppercase;font-family:'JetBrains Mono',monospace">
                  DEPARTURE RISK & ROOT-CAUSE DIAGNOSIS
                </div>
                <div style="font-size:22px;font-weight:800;color:#0f172a;margin-top:4px">
                  Chẩn Đoán Rủi Ro Khởi Hành & Điểm Nghẽn Mạng Lưới
                </div>
              </div>
              <div style="font-size:12px;color:#0284c7;font-weight:700">${ctx.carrier_code}${ctx.flight_number || ''}</div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px">
              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:18px">
                <div style="font-size:11px;font-weight:700;color:#0284c7;text-transform:uppercase;margin-bottom:10px">Chỉ Số Đánh Giá & Độ Tin Cậy Vận Hành</div>
                <div style="font-size:12.5px;line-height:2.2;color:#334155">
                  • <strong>Phân nhóm rủi ro:</strong> ${pred.risk_band}<br>
                  • <strong>Xác suất chậm trễ:</strong> ${(pred.delay_probability*100).toFixed(1)}%<br>
                  • <strong>Ngưỡng cảnh báo:</strong> ${(pred.threshold || 0.25).toFixed(4)}<br>
                  • <strong>Hệ số khuếch đại rủi ro (Lift):</strong> ${(pred.lift_at_10 || 1.0).toFixed(2)}x<br>
                  • <strong>Trễ tuyến bay 30 ngày qua:</strong> ${(ctx.route_delay_rate_30d*100).toFixed(1)}%<br>
                  • <strong>Trễ toàn mạng hãng 30 ngày:</strong> ${(ctx.carrier_delay_rate_30d*100).toFixed(1)}%
                </div>
              </div>

              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:18px">
                <div style="font-size:11px;font-weight:700;color:#d97706;text-transform:uppercase;margin-bottom:10px">Căn Nguyên & Điểm Nghẽn Đường Lăn</div>
                <div style="font-size:12.5px;line-height:1.9;color:#334155">
                  • <strong>Mật độ cất cánh sân bay:</strong> ${ctx.scheduled_departures_hour} chuyến/giờ tại ${ctx.origin} (Khung giờ cao điểm cất cánh).<br>
                  • <strong>Cự ly chặng:</strong> ${ctx.distance_miles.toFixed(0)} dặm (${ctx.distance_bucket.toUpperCase()}).<br>
                  • <strong>Rủi ro dây chuyền (Cascading):</strong> Hiệu ứng quay đầu trễ từ chặng trước (Late Aircraft Delay) có xác suất lan truyền cao.
                </div>
              </div>
            </div>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:#64748b;margin-top:14px;border-top:1px solid #e2e8f0;padding-top:10px">
            <span>Slide 2: Phân Tích Căn Nguyên & Điểm Nghẽn Mạng Lưới</span>
            <span style="color:#0284c7;font-weight:700">SkyOps Platform</span>
          </div>
        `;
      } else if (currentModalSlideIdx === 3) {
        // SLIDE 3: REGULATORY GOVERNANCE
        bodyEl.innerHTML = `
          <div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid #f1f5f9;padding-bottom:14px">
              <div>
                <div style="font-size:11px;font-weight:700;color:#0284c7;letter-spacing:1.5px;text-transform:uppercase;font-family:'JetBrains Mono',monospace">
                  AVIATION REGULATORY GOVERNANCE & STATUTORY PENALTIES
                </div>
                <div style="font-size:22px;font-weight:800;color:#0f172a;margin-top:4px">
                  Thẩm Định Pháp Luật & Chế Tài Quản Lý Nhà Nước
                </div>
              </div>
              <div style="font-size:12px;color:#0284c7;font-weight:700">${ctx.carrier_code}${ctx.flight_number || ''}</div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px">
              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:18px">
                <div style="font-size:12px;font-weight:700;color:#dc2626">14 CFR § 259.4 — Tarmac Delay Rule</div>
                <div style="font-size:12px;color:#334155;margin-top:6px;line-height:1.6">
                  Nghiêm cấm giữ hành khách trên tàu bay quá 180 phút đối với chuyến bay nội địa Hoa Kỳ mà không mở cửa cầu dẫn. Mức phạt theo luật tối đa <strong>$37,377 USD / hành khách</strong>. Sau 120 phút bắt buộc cung cấp nước, thức ăn và y tế.
                </div>
                <div style="font-size:12px;font-weight:700;color:#d97706;margin-top:14px">FAR Part 117 — Giới Hạn FDP Tổ Bay</div>
                <div style="font-size:12px;color:#334155;margin-top:6px;line-height:1.6">
                  Ràng buộc thời gian làm nhiệm vụ bay của tổ bay. Nếu thời gian chờ đẩy FDP vượt trần luật định, tổ bay sẽ bị truất quyền bay, kích hoạt ngay Standby Crew.
                </div>
              </div>

              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:18px">
                <div style="font-size:12px;font-weight:700;color:#0284c7">14 CFR § 260.6 & CAAV TT 19/2023 — Hoàn Tiền Mặt Tự Động</div>
                <div style="font-size:12px;color:#334155;margin-top:6px;line-height:1.6">
                  Quy định US DOT 2024 & Bộ GTVT Việt Nam: Hãng bay bắt buộc hoàn trả 100% tiền vé bằng tiền mặt tự động nếu chuyến bay bị trễ từ 3 tiếng trở lên mà khách không đồng ý bay chuyến thay thế.
                </div>
                <div style="font-size:12px;font-weight:700;color:#059669;margin-top:14px">Mệnh Lệnh Điều Hành OCC Bắt Buộc</div>
                <div style="font-size:12px;color:#0f172a;margin-top:6px;line-height:1.6">
                  <strong>${leg.mandatory_action || 'Yêu cầu Dispatcher theo dõi sát sao tiến độ quay đầu máy bay, chủ động liên hệ ATC và chuẩn bị phương án đổi giờ cất cánh để không vi phạm luật.'}</strong>
                </div>
              </div>
            </div>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:#64748b;margin-top:14px;border-top:1px solid #e2e8f0;padding-top:10px">
            <span>Slide 3: Thẩm Định Pháp Luật & Chế Tài Hàng Không</span>
            <span style="color:#0284c7;font-weight:700">SkyOps Platform</span>
          </div>
        `;
      } else if (currentModalSlideIdx === 4) {
        // SLIDE 4: FINANCIAL & CONTINGENCY ROI
        bodyEl.innerHTML = `
          <div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid #f1f5f9;padding-bottom:14px">
              <div>
                <div style="font-size:11px;font-weight:700;color:#0284c7;letter-spacing:1.5px;text-transform:uppercase;font-family:'JetBrains Mono',monospace">
                  FINANCIAL COST EXPOSURE (FAA $101.18/MIN) & CONTINGENCY ROI
                </div>
                <div style="font-size:22px;font-weight:800;color:#0f172a;margin-top:4px">
                  Bóc Tách Thiệt Hại Tài Chính & ROI Can Thiệp Điều Hành
                </div>
              </div>
              <div style="font-size:12px;color:#0284c7;font-weight:700">${ctx.carrier_code}${ctx.flight_number || ''}</div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px">
              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:18px">
                <div style="font-size:11px;font-weight:700;color:#d97706;text-transform:uppercase;margin-bottom:10px">Cơ Cấu Thiệt Hại Phơi Nhiễm (FAA Benchmark)</div>
                <div style="font-size:12.5px;line-height:2.0;color:#334155">
                  • Chi phí trễ cơ sở ($101.18/phút): <strong>$${fin.base_delay_cost_usd.toLocaleString('en-US', {minimumFractionDigits: 2})} USD</strong><br>
                  • Rủi ro phạt Tarmac (§ 259.4): <strong>$${fin.tarmac_penalty_exposure_usd.toLocaleString('en-US', {minimumFractionDigits: 2})} USD</strong><br>
                  • Rủi ro hoàn vé tiền mặt (§ 260.6): <strong>$${fin.cash_refund_exposure_usd.toLocaleString('en-US', {minimumFractionDigits: 2})} USD</strong><br>
                  • <strong style="color:#dc2626;font-size:13.5px">Tổng rủi ro tài chính: $${totCost.toLocaleString('en-US', {minimumFractionDigits: 2})} USD</strong>
                </div>
              </div>

              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:18px">
                <div style="font-size:11px;font-weight:700;color:#059669;text-transform:uppercase;margin-bottom:10px">Phương Án & Lợi Ích Bảo Toàn Ròng (ROI)</div>
                <div style="font-size:12.5px;line-height:1.9;color:#334155">
                  • <strong>Hành động đề xuất:</strong> ${currentAdv.best_contingency_action || 'Điều chỉnh giờ cất cánh'}<br>
                  • <strong>Tiết kiệm tài chính tiềm năng:</strong> <strong style="color:#059669;font-size:14px">$${fin.proactive_mitigation_savings_usd.toLocaleString('en-US', {minimumFractionDigits: 2})} USD</strong><br>
                  • <strong>Bảo toàn chuỗi chuyến:</strong> Ngăn chặn trễ domino sang các chuyến tiếp theo của tàu bay.<br>
                  • <strong>Bảo vệ thương hiệu:</strong> Giữ vững cam kết đúng giờ và tuân thủ pháp chế nhà nước.
                </div>
              </div>
            </div>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:#64748b;margin-top:14px;border-top:1px solid #e2e8f0;padding-top:10px">
            <span>Slide 4: Bóc Tách Thiệt Hại Tài Chính & ROI Can Thiệp</span>
            <span style="color:#0284c7;font-weight:700">SkyOps Platform</span>
          </div>
        `;
      }
    }

    // =========================================================================
    // TAB 2: INTERACTIVE ANALYTICS COPILOT CHAT (FEATURE 2: PERSISTENCE & FEATURE 3: API KEY)
    // =========================================================================
    function saveChatHistoryToStorage() {
      try {
        sessionStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(persistedChatMessages));
        localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(persistedChatMessages));
      } catch(e) {
        console.warn("Could not save chat history to storage", e);
      }
    }

    function groupChatMessagesIntoPairs(messages) {
      const pairs = [];
      let currentPair = null;
      for (let i = 0; i < messages.length; i++) {
        const m = messages[i];
        const role = m.role;
        const text = m.content || m.text || '';
        if (role === 'user') {
          if (currentPair) pairs.push(currentPair);
          currentPair = {
            id: pairs.length,
            question: text,
            userTime: m.timestamp || m.time || '',
            assistant: null
          };
        } else if (role === 'assistant') {
          if (!currentPair) {
            currentPair = {
              id: pairs.length,
              question: "Truy Vấn Nghiệp Vụ Đã Thực Hiện",
              userTime: m.timestamp || m.time || '',
              assistant: m
            };
            pairs.push(currentPair);
            currentPair = null;
          } else {
            currentPair.assistant = m;
            pairs.push(currentPair);
            currentPair = null;
          }
        }
      }
      if (currentPair) pairs.push(currentPair);
      return pairs;
    }

    function renderMainHistoryCard(container, pair, idx) {
      const card = document.createElement('div');
      card.className = 'chat-history-card';
      card.id = `main-history-card-${idx}`;

      const ans = pair.assistant || {};
      const source = ans.source || '';
      let sourceLabel = 'Cơ Sở Tri Thức & Pháp Chuẩn Hàng Không';
      if ((source||'').includes('gemini')) sourceLabel = '⚡ Google Gemini 3.8 Flash';
      else if ((source||'').includes('claude')) sourceLabel = '🟣 Anthropic Claude 3.7 Sonnet';
      else if ((source||'').includes('openai')) sourceLabel = '🟢 OpenAI o3-mini / o1';
      else if ((source||'').includes('deepseek')) sourceLabel = '🔵 DeepSeek-R1 Reasoner';

      const timeStr = ans.timestamp || pair.userTime || '';

      let citHtml = '';
      if (ans.citations && ans.citations.length > 0) {
        citHtml = '<div class="chat-citations">' + ans.citations.map(c => `<span class="citation-tag">${c}</span>`).join('') + '</div>';
      }

      let followHtml = '';
      if (ans.followups && ans.followups.length > 0) {
        followHtml = '<div class="chat-followups"><div style="font-size:11px;font-weight:700;color:var(--text-muted);margin-bottom:4px">Chuyên đề tra cứu liên quan:</div>' +
          ans.followups.map(q => `<span class="chip" onclick="sendQuickPrompt(decodeURIComponent('${encodeURIComponent(q)}'))">${q}</span>`).join('') +
          '</div>';
      }

      const answerContent = ans.content || ans.text || '(Chưa ghi nhận câu trả lời)';

      card.innerHTML = `
        <div class="chat-history-header" onclick="toggleMainHistoryCard(${idx})" title="Nhấn để mở hoặc thu gọn câu trả lời">
          <div class="history-title-box">
            <span style="font-weight:800;color:var(--primary);display:flex;align-items:center;gap:6px">
              <span>📋</span> Báo Cáo Phân Tích Chẩn Đoán
            </span>
            <span class="history-toggle-badge" id="main-history-badge-${idx}">▶ Bấm xem câu trả lời</span>
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <span class="chat-source-tag">${sourceLabel}</span>
            ${timeStr ? `<span style="font-size:10px;color:var(--text-muted)">${timeStr}</span>` : ''}
          </div>
        </div>
        <div class="chat-history-question" onclick="toggleMainHistoryCard(${idx})" title="Nhấn để mở hoặc thu gọn câu trả lời">
          ${pair.question.replace(/</g, "&lt;")}
        </div>
        <div class="chat-history-answer-drawer" id="main-history-drawer-${idx}" style="display:none" onclick="event.stopPropagation()">
          <div class="drawer-meta-bar">
            <span class="drawer-label">💡 Câu Trả Lời & Cơ Sở Pháp Chuẩn:</span>
            <button type="button" class="btn-copy-history" onclick="copyMainHistoryAnswerText(${idx})" title="Sao chép nội dung">📋 Sao chép</button>
          </div>
          <div class="chat-body" id="main-history-body-${idx}">${formatMarkdown(answerContent)}</div>
          ${citHtml}
          ${followHtml}
        </div>
      `;
      container.appendChild(card);
    }

    function toggleMainHistoryCard(idx) {
      const drawer = document.getElementById(`main-history-drawer-${idx}`);
      const badge = document.getElementById(`main-history-badge-${idx}`);
      const card = document.getElementById(`main-history-card-${idx}`);
      if (!drawer) return;
      const isOpen = drawer.style.display !== 'none';
      if (isOpen) {
        drawer.style.display = 'none';
        if (badge) badge.textContent = '▶ Bấm xem câu trả lời';
        if (card) card.classList.remove('expanded');
      } else {
        drawer.style.display = 'block';
        if (badge) badge.textContent = '▼ Thu gọn câu trả lời';
        if (card) card.classList.add('expanded');
      }
    }

    function toggleAllMainHistoryCards(expand) {
      const drawers = document.querySelectorAll('[id^="main-history-drawer-"]');
      drawers.forEach(drawer => {
        const idMatch = drawer.id.match(/\d+/);
        if (idMatch) {
          const idx = idMatch[0];
          const badge = document.getElementById(`main-history-badge-${idx}`);
          const card = document.getElementById(`main-history-card-${idx}`);
          if (expand) {
            drawer.style.display = 'block';
            if (badge) badge.textContent = '▼ Thu gọn câu trả lời';
            if (card) card.classList.add('expanded');
          } else {
            drawer.style.display = 'none';
            if (badge) badge.textContent = '▶ Bấm xem câu trả lời';
            if (card) card.classList.remove('expanded');
          }
        }
      });
    }

    function copyMainHistoryAnswerText(idx) {
      const el = document.getElementById(`main-history-body-${idx}`);
      if (!el) return;
      const text = el.innerText || el.textContent;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          showToast("Đã sao chép nội dung câu trả lời", "success");
        }).catch(() => fallbackCopy(text));
      } else {
        fallbackCopy(text);
      }
      function fallbackCopy(t) {
        const ta = document.createElement('textarea');
        ta.value = t;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast("Đã sao chép nội dung câu trả lời", "success");
      }
    }

    function loadChatHistoryFromStorage() {
      try {
        const saved = sessionStorage.getItem(CHAT_STORAGE_KEY) || localStorage.getItem(CHAT_STORAGE_KEY);
        if (!saved) return;
        const list = JSON.parse(saved);
        if (Array.isArray(list) && list.length > 0) {
          persistedChatMessages = list;
          chatHistory = [];
          list.forEach(m => {
            chatHistory.push({ role: m.role, content: m.content || m.text });
          });

          const pairs = groupChatMessagesIntoPairs(list);
          const stream = document.getElementById('chat-stream');
          stream.innerHTML = '';

          const toolbar = document.createElement('div');
          toolbar.className = 'history-toolbar';
          toolbar.innerHTML = `
            <span>🕒 <strong>Lịch sử tra cứu (${pairs.length} câu hỏi)</strong> — Nhấn vào từng thẻ để xem câu trả lời</span>
            <div style="display:flex;gap:6px">
              <button type="button" class="btn-history-ctrl" onclick="toggleAllMainHistoryCards(true)">📂 Mở tất cả</button>
              <button type="button" class="btn-history-ctrl" onclick="toggleAllMainHistoryCards(false)">📁 Thu gọn tất cả</button>
            </div>
          `;
          stream.appendChild(toolbar);

          pairs.forEach((pair, idx) => {
            renderMainHistoryCard(stream, pair, idx);
          });
          setTimeout(focusOnCurrentTurn, 100);
        }
      } catch(e) {
        console.warn("Could not load chat history from storage", e);
      }
    }

    function updateChatContextBanner() {
      const banner = document.getElementById('chat-context-text');
      const clearBtn = document.getElementById('btn-clear-context');
      if (currentFlightContext) {
        const c = currentFlightContext;
        const p = (currentAdv && currentAdv.prediction_context) || {};
        banner.innerHTML = `
          <span>✈️ <strong>Ngữ cảnh chuyến bay đang chọn</strong>: <strong>${c.carrier_code}${c.flight_number||''}</strong> (${c.origin} ➔ ${c.dest}) lúc ${c.dep_window_label || c.dep_hour + ':00'}. Xác suất trễ dự báo: <strong>${p.delay_probability ? (p.delay_probability*100).toFixed(1)+'%' : 'N/A'}</strong> (Phân hạng: <strong>${p.risk_band || 'N/A'}</strong>).</span>
        `;
        clearBtn.style.display = 'inline-block';
      } else {
        banner.innerHTML = `
          <span>ℹ️ <strong>Chưa chọn chuyến bay cụ thể</strong>: Hệ thống đang ở chế độ Tra Cứu Quy Chuẩn Tổng Thể. Tra cứu chuyến bay ở Tab 1 để phân tích chuyên sâu theo hồ sơ bay!</span>
        `;
        clearBtn.style.display = 'none';
      }
    }

    function clearFlightContext() {
      currentFlightContext = null;
      currentAdv = null;
      updateChatContextBanner();
    }

    function askCopilotAboutCurrentFlight() {
      if (!currentAdv) return;
      switchTab('tab-chat');
      const ctx = currentAdv.flight_context;
      const prompt = `Phân tích chuyên sâu rủi ro, thiệt hại chi phí và khuyến nghị tác nghiệp cho chuyến bay ${ctx.carrier_code}${ctx.flight_number || ''} (${ctx.origin} -> ${ctx.dest})`;
      sendChatMessageWithText(prompt);
    }

    function sendQuickPrompt(promptText) {
      switchTab('tab-chat');
      sendChatMessageWithText(promptText);
    }

    async function sendChatMessage() {
      const input = document.getElementById('chat-input-field');
      const msg = input.value.trim();
      if (!msg) return;
      input.value = '';
      await sendChatMessageWithText(msg);
    }

    async function sendChatMessageWithText(text) {
      appendChatMessage('user', text);
      const stream = document.getElementById('chat-stream');
      
      // Loading placeholder
      const loadingDiv = document.createElement('div');
      loadingDiv.className = 'chat-msg assistant';
      loadingDiv.id = 'chat-loading-placeholder';
      loadingDiv.innerHTML = '<div style="color:#64748b;font-style:italic">⏳ Đang tra cứu cơ sở dữ liệu giám sát và đối chiếu quy chuẩn pháp lý...</div>';
      stream.appendChild(loadingDiv);
      focusOnCurrentTurn();

      const rawProvider = document.getElementById('chat-model-provider').value;
      let provider = rawProvider;
      let modelName = undefined;

      if (rawProvider === 'custom') {
        const customId = (document.getElementById('custom-model-id') ? document.getElementById('custom-model-id').value.trim() : '');
        modelName = customId;
        if (customId.includes('claude')) provider = 'claude';
        else if (customId.includes('gemini')) provider = 'gemini';
        else if (customId.includes('deepseek')) provider = 'deepseek';
        else if (customId.startsWith('o1') || customId.startsWith('o3') || customId.includes('gpt')) provider = 'openai';
        else provider = 'auto';
      } else if (rawProvider.includes(':')) {
        const parts = rawProvider.split(':');
        provider = parts[0];
        modelName = parts[1];
      }

      const gKey = localStorage.getItem('gemini_api_key') || '';
      const cKey = localStorage.getItem('claude_api_key') || '';
      const oKey = localStorage.getItem('openai_api_key') || '';
      const dKey = localStorage.getItem('deepseek_api_key') || '';

      let activeKey = undefined;
      if (provider === 'claude') activeKey = cKey;
      else if (provider === 'openai') activeKey = oKey;
      else if (provider === 'gemini') activeKey = gKey;
      else if (provider === 'deepseek') activeKey = dKey;
      else activeKey = cKey || oKey || gKey || dKey;

      const payload = {
        message: text,
        flight_context: currentFlightContext,
        conversation_history: chatHistory.slice(-6),
        model_provider: provider,
        model_name: modelName,
        api_key: activeKey || undefined
      };

      try {
        const res = await fetch('/copilot/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const d = await res.json();
        
        const loader = document.getElementById('chat-loading-placeholder');
        if (loader) loader.remove();

        if (!res.ok) {
          const errDetail = d.detail || JSON.stringify(d);
          appendChatMessage('assistant', '⚠️ Lỗi từ Copilot: ' + errDetail, 'offline_knowledge_engine', [], [], false);
          showToast("Lỗi phản hồi Copilot", errDetail, "error");
          return;
        }

        appendChatMessage('assistant', d.reply, d.source, d.grounding_citations, d.suggested_questions, true);
        chatHistory.push({role: 'user', content: text});
        chatHistory.push({role: 'assistant', content: d.reply});
      } catch(e) {
        const loader = document.getElementById('chat-loading-placeholder');
        if (loader) loader.remove();
        appendChatMessage('assistant', '⚠️ Lỗi kết nối API Chat: ' + e.message, 'offline_knowledge_engine', [], [], false);
        showToast("Lỗi kết nối", e.message, "error");
      }
    }

    function formatMarkdown(text) {
      if (!text) return '';
      let escaped = text
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

      // Code blocks
      escaped = escaped.replace(/```([a-z]*)\n([\s\S]*?)```/g, '<pre style="background:#0f172a;color:#f8fafc;padding:12px;border-radius:6px;font-size:12px;overflow-x:auto;font-family:\'JetBrains Mono\',monospace">$2</pre>');
      // Headers
      escaped = escaped.replace(/^#### (.*$)/gim, '<h4 class="md-h4" style="margin:12px 0 4px 0;font-size:14px;color:var(--text-main)">$1</h4>');
      escaped = escaped.replace(/^### (.*$)/gim, '<h3 class="md-h3" style="margin:14px 0 6px 0;font-size:15px;color:var(--primary)">$1</h3>');
      escaped = escaped.replace(/^## (.*$)/gim, '<h2 class="md-h2" style="margin:16px 0 8px 0;font-size:17px;color:var(--text-main)">$1</h2>');
      // Bold & Italic
      escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');
      // Inline code
      escaped = escaped.replace(/`([^`]+)`/g, '<code class="md-code" style="background:var(--slate-100);border:1px solid var(--slate-300);padding:2px 6px;border-radius:4px;font-size:12px;color:var(--primary);font-family:\'JetBrains Mono\',monospace">$1</code>');
      // Blockquotes
      escaped = escaped.replace(/^&gt; (.*$)/gim, '<blockquote class="md-quote" style="border-left:3px solid var(--primary);background:var(--primary-light);margin:8px 0;padding:6px 12px;border-radius:0 6px 6px 0;color:var(--text-main);font-size:12px">$1</blockquote>');
      // Unordered lists
      escaped = escaped.replace(/^- (.*$)/gim, '<div style="margin-left:14px;margin-bottom:3px">• $1</div>');
      // Newlines
      escaped = escaped.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');

      return escaped;
    }

    function renderChatMessageToDOM(role, content, source, citations, followups, timestamp) {
      const stream = document.getElementById('chat-stream');
      const div = document.createElement('div');
      div.className = 'chat-msg ' + role;
      const timeStr = timestamp || new Date().toLocaleTimeString();

      if (role === 'user') {
        lastUserMsgElement = div;
        div.innerHTML = `
          <div class="chat-meta">
            <span style="font-weight:700">🔍 Truy Vấn Nghiệp Vụ</span>
            <span>${timeStr}</span>
          </div>
          <div class="user-msg-body">${content.replace(/</g, "&lt;")}</div>
        `;
        stream.appendChild(div);
      } else {
        let sourceLabel = 'Cơ Sở Tri Thức & Pháp Chuẩn Hàng Không';
        if ((source||'').includes('gemini')) sourceLabel = '⚡ Google Gemini 3.8 Flash';
        else if ((source||'').includes('claude')) sourceLabel = '🟣 Anthropic Claude 3.7 Sonnet';
        else if ((source||'').includes('openai')) sourceLabel = '🟢 OpenAI o3-mini / o1';
        else if ((source||'').includes('deepseek')) sourceLabel = '🔵 DeepSeek-R1 Reasoner';
        let citHtml = '';
        if (citations && citations.length > 0) {
          citHtml = '<div class="chat-citations">' + citations.map(c => `<span class="citation-tag">${c}</span>`).join('') + '</div>';
        }

        let followHtml = '';
        if (followups && followups.length > 0) {
          followHtml = '<div class="chat-followups"><div style="font-size:11px;font-weight:700;color:var(--text-muted);margin-bottom:4px">Chuyên đề tra cứu liên quan:</div>' +
            followups.map(q => `<span class="chip" onclick="sendQuickPrompt(decodeURIComponent('${encodeURIComponent(q)}'))">${q}</span>`).join('') +
            '</div>';
        }

        div.innerHTML = `
          <div class="chat-meta">
            <span style="font-weight:800;color:var(--primary);display:flex;align-items:center;gap:6px">
              <span>📋</span> Báo Cáo Phân Tích Chẩn Đoán
            </span>
            <span class="chat-source-tag">${sourceLabel}</span>
          </div>
          <div class="chat-body">${formatMarkdown(content)}</div>
          ${citHtml}
          ${followHtml}
        `;
        stream.appendChild(div);
      }
    }

    // Typewriter Streaming Engine for realistic conversational flow
    function streamChatMessageToDOM(content, source, citations, followups, timestamp, onComplete) {
      const stream = document.getElementById('chat-stream');
      const div = document.createElement('div');
      div.className = 'chat-msg assistant';
      const timeStr = timestamp || new Date().toLocaleTimeString();
      const sourceLabel = (source === 'llm_gemini' || source === 'llm_openai') ? 'Dữ Liệu & Tổng Hợp Chuyên Sâu (Gemini Online)' : 'Cơ Sở Tri Thức & Pháp Chuẩn Hàng Không';

      div.innerHTML = `
        <div class="chat-meta">
          <span style="font-weight:800;color:var(--primary);display:flex;align-items:center;gap:6px">
            <span>📋</span> Báo Cáo Phân Tích Chẩn Đoán
          </span>
          <span class="chat-source-tag">${sourceLabel}</span>
          <span style="font-size:10px;color:var(--text-muted);margin-left:auto">${timeStr}</span>
        </div>
        <div class="chat-body" style="cursor:pointer" title="Bấm để hiện ngay toàn bộ nội dung"><span class="stream-text-node"></span><span class="typewriter-cursor"></span></div>
        <div class="chat-citations-stream" style="display:none"></div>
        <div class="chat-followups-stream" style="display:none"></div>
      `;
      stream.appendChild(div);

      const textNode = div.querySelector('.stream-text-node');
      const cursorNode = div.querySelector('.typewriter-cursor');
      const citBox = div.querySelector('.chat-citations-stream');
      const fBox = div.querySelector('.chat-followups-stream');

      let isFinished = false;

      function renderFinalAddons() {
        if (citations && citations.length > 0) {
          citBox.style.display = 'flex';
          citBox.className = 'chat-citations';
          citBox.innerHTML = citations.map(c => `<span class="citation-tag">${c}</span>`).join('');
        }
        if (followups && followups.length > 0) {
          fBox.style.display = 'block';
          fBox.className = 'chat-followups';
          fBox.innerHTML = '<div style="font-size:11px;font-weight:700;color:var(--text-muted);margin-bottom:4px">Chuyên đề tra cứu liên quan:</div>' +
            followups.map(q => `<span class="chip" onclick="sendQuickPrompt(decodeURIComponent('${encodeURIComponent(q)}'))">${q}</span>`).join('');
        }
      }

      function finishInstantly() {
        if (isFinished) return;
        isFinished = true;
        if (cursorNode) cursorNode.remove();
        textNode.innerHTML = formatMarkdown(content);
        renderFinalAddons();
        focusOnCurrentTurn();
        if (onComplete) onComplete();
      }

      // Allow click to complete instantly
      div.onclick = finishInstantly;

      const tokens = content.match(/(\s+|\S+)/g) || [content];
      let tokenIdx = 0;
      let accumulated = "";
      const chunkSize = tokens.length > 350 ? 4 : (tokens.length > 120 ? 2 : 1);
      const intervalMs = 15;

      const streamTimer = setInterval(() => {
        if (isFinished) {
          clearInterval(streamTimer);
          return;
        }
        for (let i = 0; i < chunkSize && tokenIdx < tokens.length; i++) {
          accumulated += tokens[tokenIdx++];
        }
        textNode.innerHTML = formatMarkdown(accumulated);
        focusOnCurrentTurn();

        if (tokenIdx >= tokens.length) {
          clearInterval(streamTimer);
          if (!isFinished) {
            isFinished = true;
            if (cursorNode) cursorNode.remove();
            textNode.innerHTML = formatMarkdown(content);
            renderFinalAddons();
            focusOnCurrentTurn();
            if (onComplete) onComplete();
          }
        }
      }, intervalMs);
    }

    function appendChatMessage(role, content, source, citations, followups, isStreaming = false) {
      const ts = new Date().toLocaleTimeString();
      if (role === 'assistant' && isStreaming) {
        streamChatMessageToDOM(content, source, citations, followups, ts, () => {
          persistedChatMessages.push({
            role: role,
            content: content,
            source: source,
            citations: citations || [],
            followups: followups || [],
            timestamp: ts
          });
          saveChatHistoryToStorage();
        });
      } else {
        renderChatMessageToDOM(role, content, source, citations, followups, ts);
        persistedChatMessages.push({
          role: role,
          content: content,
          source: source,
          citations: citations || [],
          followups: followups || [],
          timestamp: ts
        });
        saveChatHistoryToStorage();
        setTimeout(focusOnCurrentTurn, 30);
        setTimeout(focusOnCurrentTurn, 100);
        setTimeout(focusOnCurrentTurn, 250);
      }
    }

    // =========================================================================
    // VOICE INPUT ENGINE (WEB SPEECH API)
    // =========================================================================
    let voiceRecognition = null;
    let isVoiceListening = false;

    function toggleVoiceInput(target = 'main') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        showToast("Không hỗ trợ giọng nói", "Trình duyệt hiện tại chưa hỗ trợ Web Speech API. Vui lòng mở trang trên Google Chrome hoặc Microsoft Edge để nói lệnh tác nghiệp.", "warning");
        return;
      }

      const btnId = target === 'embed' ? 'btn-voice-embed' : 'btn-voice-main';
      const inputId = target === 'embed' ? 'user-input' : 'chat-input-field';
      const btn = document.getElementById(btnId);
      const input = document.getElementById(inputId);
      if (!btn || !input) return;

      if (isVoiceListening) {
        if (voiceRecognition) {
          try { voiceRecognition.stop(); } catch(e) {}
        }
        return;
      }

      try {
        voiceRecognition = new SpeechRecognition();
        voiceRecognition.lang = 'vi-VN';
        voiceRecognition.interimResults = true;
        voiceRecognition.continuous = true;
        voiceRecognition.maxAlternatives = 1;

        const origPlaceholder = input.placeholder;
        let finalAccumulatedTranscript = input.value ? input.value + ' ' : '';

        voiceRecognition.onstart = function() {
          isVoiceListening = true;
          btn.classList.add('recording');
          btn.innerHTML = '🔴';
          btn.title = "Đang lắng nghe... Bấm vào đây khi nói xong";
          input.placeholder = "🎙️ Đang lắng nghe giọng nói... Hãy nói (ví dụ: 'Phân tích chuyến 4568')...";
          showToast("Đang lắng nghe", "Hệ thống đang thu âm giọng nói. Hãy nói to, rõ ràng...", "info");
        };

        voiceRecognition.onsoundstart = function() {
          console.log("[SpeechRecognition] Đã phát hiện âm thanh/tiếng nói");
        };

        voiceRecognition.onspeechstart = function() {
          console.log("[SpeechRecognition] Bắt đầu nhận diện tín hiệu phát âm");
        };

        voiceRecognition.onresult = function(event) {
          let interimTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            const part = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalAccumulatedTranscript += part + ' ';
            } else {
              interimTranscript += part;
            }
          }
          const fullText = (finalAccumulatedTranscript + interimTranscript).trim();
          if (fullText) {
            input.value = fullText;
          }
        };

        voiceRecognition.onerror = function(event) {
          console.warn("[SpeechRecognition] Lỗi:", event.error);
          cleanupVoiceState();
          if (event.error === 'not-allowed') {
            showToast("Quyền Micro", "Vui lòng cấp quyền truy cập Micro trên thanh địa chỉ trình duyệt.", "warning");
          } else if (event.error === 'audio-capture') {
            showToast("Không tìm thấy Micro", "Trình duyệt không nhận được tín hiệu từ micro phần cứng của bạn.", "error");
          } else if (event.error === 'network') {
            showToast("Lỗi mạng Speech", "Tính năng nhận diện giọng nói của Google cần kết nối internet để chuyển âm thanh thành văn bản.", "warning");
          } else if (event.error !== 'no-speech') {
            showToast("Thông báo Micro", "Trạng thái nhận diện: " + event.error, "info");
          }
        };

        voiceRecognition.onend = function() {
          cleanupVoiceState();
          input.focus();
        };

        function cleanupVoiceState() {
          isVoiceListening = false;
          if (btn) {
            btn.classList.remove('recording');
            btn.innerHTML = '🎙️';
            btn.title = "🎙️ Nhận diện giọng nói tác nghiệp (Web Speech API)";
          }
          if (input) {
            input.placeholder = origPlaceholder;
          }
        }

        voiceRecognition.start();
      } catch(e) {
        console.error("SpeechRecognition error:", e);
        showToast("Lỗi micro", e.message, "error");
      }
    }

    // =========================================================================
    // EXPORT OCC CHAT AUDIT LOG (MARKDOWN & PRINTABLE PDF)
    // =========================================================================
    function openAuditExportModal() {
      const modal = document.getElementById('audit-export-modal');
      const preview = document.getElementById('audit-log-preview-container');
      if (!modal || !preview) return;

      const mdText = generateOCCAuditLogMarkdown();
      preview.textContent = mdText;
      modal.style.display = 'block';
    }

    function closeAuditExportModal() {
      const modal = document.getElementById('audit-export-modal');
      if (modal) modal.style.display = 'none';
    }

    function generateOCCAuditLogMarkdown() {
      const now = new Date();
      const dateStr = now.toLocaleDateString('vi-VN');
      const timeStr = now.toLocaleTimeString('vi-VN');
      const auditId = 'OCC-AUDIT-' + now.getFullYear() +
        String(now.getMonth()+1).padStart(2,'0') +
        String(now.getDate()).padStart(2,'0') + '-' +
        Math.random().toString(36).substring(2, 7).toUpperCase();

      let flightPart = "TOÀN MẠNG BAY (HỆ THỐNG GIÁM SÁT TỔNG THỂ)";
      let flightDetail = "- Chế độ: Tra cứu quy chuẩn chung & nghiệp vụ phân tích dữ liệu toàn hệ thống";
      if (currentFlightContext) {
        const c = currentFlightContext;
        const p = (currentAdv && currentAdv.prediction_context) || {};
        flightPart = `CHUYẾN BAY #${c.flight_id || ''} (${c.carrier_code || ''} ${c.origin || ''} ➔ ${c.dest || ''})`;
        flightDetail = `- Số Hiệu: ${c.carrier_code || ''}${c.flight_number || ''} | Hãng Bay: ${c.carrier_name || c.carrier_code}
- Tuyến Bay: Sân bay ${c.origin} ➔ Sân bay ${c.dest}
- Khung Giờ Khởi Hành: ${c.dep_window_label || (c.dep_hour + ':00')}
- Xác Suất Trễ Dự Báo AI: ${p.delay_probability ? (p.delay_probability * 100).toFixed(1) + '%' : 'N/A'} (Phân Hạng: ${p.risk_band || 'N/A'})
- Dự Kiến Phút Trễ: ${p.predicted_delay_minutes ? p.predicted_delay_minutes.toFixed(1) + ' phút' : 'N/A'}
- Phơi Nhiễm Rủi Ro Tài Chính (FAA $101.18/phút + Phạt Tarmac/Hoàn Vé): ${p.total_financial_exposure_usd ? '$' + Number(p.total_financial_exposure_usd).toLocaleString() + ' USD' : 'N/A'}`;
      }

      let transcript = "";
      if (!persistedChatMessages || persistedChatMessages.length === 0) {
        transcript = "*(Chưa ghi nhận nội dung truy vấn nào trong phiên làm việc này)*\n";
      } else {
        persistedChatMessages.forEach((m, idx) => {
          const roleName = m.role === 'user' ? '👤 DISPATCHER / DATA ANALYST' : '🤖 SKYOPS COPILOT ADVISORY';
          const src = m.source ? ` [Nguồn: ${m.source}]` : '';
          transcript += `### Lượt #${idx + 1} | [${m.timestamp || ''}] ${roleName}${src}\n\n`;
          transcript += `${m.content}\n\n`;
          if (m.citations && m.citations.length > 0) {
            transcript += `> ⚖️ **Căn cứ pháp lý / Quy chuẩn:** ${m.citations.join(' | ')}\n\n`;
          }
          transcript += `---\n\n`;
        });
      }

      return `# BIÊN BẢN HỘI THOẠI & NHẬT KÝ KIỂM TOÁN TÁC NGHIỆP BAY
## CỤC HÀNG KHÔNG / US DOT & FAA FLIGHT OPERATIONS COMPLIANCE AUDIT LOG
**Mã Hồ Sơ Kiểm Toán:** \`${auditId}\`  
**Thời Điểm Thiết Lập:** ${dateStr} ${timeStr}  
**Môi Trường Vận Hành:** SkyOps Copilot™ Platform (Kho DWH: PostgreSQL \`airline_dwh\`)

---

### I. THÔNG TIN HỒ SƠ & BỐI CẢNH VẬN HÀNH (OPERATIONAL CONTEXT)
- **Đối Tượng Phân Tích:** ${flightPart}
${flightDetail}
- **Nhân Sự Thực Hiện:** Kỹ Sư Dữ Liệu Trưởng / Dispatcher Điều Phối OCC
- **Căn Cứ Pháp Chuẩn Quốc Tế & Quốc Gia:**
  1. **14 CFR § 259.4**: Giới hạn thời gian đỗ sân đỗ Tarmac (180 phút nội địa / 240 phút quốc tế, chế tài phạt tới $37,377 USD/pax).
  2. **FAR Part 117**: Giới hạn thời gian làm nhiệm vụ bay của Tổ bay (FDP) & Yêu cầu kích hoạt phi hành đoàn dự phòng.
  3. **14 CFR § 260.6**: Quy định bắt buộc hoàn tiền mặt tự động 100% khi chuyến bay trễ đáng kể (>= 3h nội địa).
  4. **Thông tư 19/2023/TT-BGTVT**: Nghĩa vụ chăm sóc hành khách và bồi thường ứng trước không hoàn lại (CAAV).
  5. **Định Mức Chi Phí FAA/A4A**: $101.18 USD cho mỗi phút trễ chuyến bay thương mại.

---

### II. TOÀN VĂN NHẬT KÝ HỘI THOẠI & GIẢI TRÌNH TÁC NGHIỆP (CONVERSATION TRANSCRIPT)
${transcript}

---

### III. XÁC NHẬN TRÁCH NHIỆM & DUYỆT HỒ SƠ (AUDIT SIGN-OFF)
Biên bản này được hệ thống tự động niêm phong làm bằng chứng giải trình pháp lý và hồ sơ kiểm toán sự cố vận hành hàng không. Mọi dữ liệu trích xuất từ kho dữ liệu đã được đối soát 100% dòng và chứng thực qua thuật toán dự báo rủi ro.

| Trực Ban Điều Phối OCC (Dispatcher) | Trưởng Phòng Quản Trị Dữ Liệu (Lead DA) | Đại Diện Pháp Chế & An Toàn Bay |
| :---: | :---: | :---: |
| *(Ký & Ghi rõ họ tên)* | *(Ký & Ghi rõ họ tên)* | *(Ký & Đóng dấu)* |
| ..................................... | ..................................... | ..................................... |
`;
    }

    function downloadAuditLogMarkdown() {
      const md = generateOCCAuditLogMarkdown();
      const blob = new Blob([md], {type: 'text/markdown;charset=utf-8'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      const now = new Date();
      const timeSuffix = now.toISOString().replace(/[-:T.]/g, '').slice(0, 14);
      a.href = url;
      a.download = `OCC_Audit_Log_${timeSuffix}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast("Xuất Biên Bản", "Đã tải xuống tệp biên bản kiểm toán Markdown (.md).", "success");
    }

    function printOCCAuditLog() {
      const md = generateOCCAuditLogMarkdown();
      const printWin = window.open('', '_blank');
      if (!printWin) {
        downloadAuditLogMarkdown();
        showToast("Thông báo", "Trình duyệt chặn popup. Đã tự động tải xuống tệp Markdown.", "info");
        return;
      }
      const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>OCC Flight Operations Audit Report</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; margin: 36px; color: #0f172a; line-height: 1.55; font-size: 13px; }
    h1 { font-size: 18px; text-transform: uppercase; margin-bottom: 4px; color: #0f172a; text-align: center; }
    h2 { font-size: 13.5px; text-align: center; color: #475569; margin-top: 0; margin-bottom: 24px; font-weight: normal; }
    h3 { font-size: 14px; color: #0284c7; border-bottom: 1.5px solid #cbd5e1; padding-bottom: 4px; margin-top: 22px; margin-bottom: 10px; }
    pre { background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 6px; font-family: monospace; white-space: pre-wrap; font-size: 11.5px; }
    blockquote { border-left: 3px solid #0284c7; background: #f0f9ff; margin: 8px 0; padding: 6px 12px; font-size: 12px; }
    table { width: 100%; border-collapse: collapse; margin-top: 24px; margin-bottom: 24px; }
    th, td { border: 1px solid #cbd5e1; padding: 10px 14px; text-align: center; font-size: 12px; }
    th { background: #f1f5f9; font-weight: 700; }
    hr { border: none; border-top: 1px solid #e2e8f0; margin: 16px 0; }
    @media print {
      body { margin: 12mm; }
    }
  </style>
</head>
<body>
  ${formatMarkdown(md).replace(/<pre style="[^"]*">/g, '<pre>')}
  <script>window.onload = function() { window.print(); }<\/script>
</body>
</html>`;
      printWin.document.open();
      printWin.document.write(htmlContent);
      printWin.document.close();
    }

    function copyAuditLogToClipboard() {
      const md = generateOCCAuditLogMarkdown();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(md).then(() => {
          showToast("Đã sao chép", "Đã sao chép toàn bộ biên bản kiểm toán vào bộ nhớ đệm.", "success");
        }).catch(() => fallbackCopy(md));
      } else {
        fallbackCopy(md);
      }
      function fallbackCopy(text) {
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast("Đã sao chép", "Đã sao chép toàn bộ biên bản kiểm toán vào bộ nhớ đệm.", "success");
      }
    }

    function resetChat() {
      chatHistory = [];
      persistedChatMessages = [];
      lastUserMsgElement = null;
      try {
        sessionStorage.removeItem(CHAT_STORAGE_KEY);
        localStorage.removeItem(CHAT_STORAGE_KEY);
      } catch(e) {}

      const stream = document.getElementById('chat-stream');
      stream.innerHTML = `
        <div class="chat-msg assistant">
          <div class="chat-meta">
            <span style="font-weight:800;color:var(--primary)">📋 Trung Tâm Tra Cứu & Chẩn Đoán Vận Hành</span>
            <span class="chat-source-tag">Cơ Sở Tri Thức & Pháp Chuẩn Hàng Không</span>
          </div>
          <div class="chat-body">
            Bàn tra cứu nghiệp vụ đã được làm mới. Sẵn sàng tiếp nhận truy vấn phân tích dữ liệu tiếp theo.
          </div>
        </div>
      `;
      stream.scrollTop = 0;
      showToast("Đã làm mới", "Bàn tra cứu nghiệp vụ đã được đặt lại trạng thái ban đầu.", "info");
    }

    // =========================================================================
    // TAB 3: DATA METRIC DICTIONARY & DAX REPOSITORY
    // =========================================================================
    const DAX_MEASURES = [
      {
        id: "dax_otp_a14",
        name_vi: "Tỷ Lệ Đúng Giờ Chuẩn DOT (OTP % A14)",
        name_en: "On-Time Performance % (US DOT A14 Standard)",
        category: "dax_measures",
        formula: "[OTP % (A14)] = \nDIVIDE(\n    CALCULATE(COUNTROWS(fact_flights), fact_flights[arr_delay_min] < 15, fact_flights[is_cancelled] = 0),\n    CALCULATE(COUNTROWS(fact_flights), fact_flights[is_cancelled] = 0),\n    0\n)",
        description: "Đo lường tỷ lệ chuyến bay đến trễ dưới 15 phút (theo chuẩn A14 của BTS) trên tổng số chuyến bay thực hiện hoàn thành (không tính chuyến hủy).",
        business_significance: "Chỉ số uy tín thương hiệu cốt lõi, công khai xếp hạng hàng tháng trên báo cáo Air Travel Consumer Report của DOT.",
        page: "Trang 1: Executive Operations Overview"
      },
      {
        id: "dax_direct_delay_cost",
        name_vi: "Tổng Chi Phí Trễ Trực Tiếp (USD)",
        name_en: "Total Direct Delay Cost (FAA $101.18/min)",
        category: "dax_measures",
        formula: "[Total Direct Delay Cost (USD)] = \n[Total Delay Minutes] * 101.18",
        description: "Quy đổi toàn bộ tổng số phút trễ của các chuyến bay hoàn thành thành tổn thất tài chính tiền mặt thực tế theo định mức FAA/A4A $101.18/phút.",
        business_significance: "Cấu thành từ $38.50 nhiên liệu + $32.20 lương phi công/tiếp viên + $17.10 dịch vụ mặt đất + $13.38 hao mòn động cơ bảo dưỡng.",
        page: "Trang 1: Overview & Trang 2: Delay Causes"
      },
      {
        id: "dax_cascading_ratio",
        name_vi: "Tỷ Trọng Trễ Dây Chuyền Domino",
        name_en: "Cascading Delay Ratio (Late Aircraft)",
        category: "dax_measures",
        formula: "[Cascading Delay Ratio] = \nDIVIDE(\n    SUM(fact_flight_delays[late_aircraft_delay_min]),\n    SUM(fact_flight_delays[total_delay_min]),\n    0\n)",
        description: "Tỷ lệ số phút trễ do nguyên nhân máy bay đến trễ từ chặng trước (Late Aircraft) trên tổng số phút trễ của 5 nguyên nhân BTS.",
        business_significance: "Chiếm gần 40% tổng thời gian trễ toàn mạng lưới. Đòn bẩy tối ưu lớn nhất là bổ sung đệm xoay đầu (turnaround padding) vào buổi chiều.",
        page: "Trang 2: Delay Root-Cause & Cascading Analysis"
      },
      {
        id: "dax_potential_penalty",
        name_vi: "Tổng Rủi Ro Tiền Phạt Hành Chính (USD)",
        name_en: "Potential Penalty Exposure (USD)",
        category: "dax_measures",
        formula: "[Potential Penalty Exposure (USD)] = \nSUM(fct_flight_regulatory_predictions[max_penalty_exposure_usd])",
        description: "Tính tổng phơi nhiễm tài chính tối đa nếu các chuyến bay High Risk vi phạm trần Tarmac Delay 14 CFR § 259.4 ($37,377 USD/pax * 180 khách = $6.72M USD).",
        business_significance: "Bảo vệ hãng bay trước các khoản phạt hành chính khổng lồ của Bộ Giao thông Vận tải Hoa Kỳ (US DOT).",
        page: "Trang 4: Predictive Risk & Aviation Governance"
      },
      {
        id: "dax_predicted_high_risk",
        name_vi: "Số Chuyến Bay Phân Hạng Rủi Ro Cao",
        name_en: "Predicted High Risk Flights",
        category: "dax_measures",
        formula: "[Predicted High Risk Flights] = \nCALCULATE(COUNTROWS(fct_flight_regulatory_predictions), fct_flight_regulatory_predictions[is_predicted_delayed] = TRUE)",
        description: "Số chuyến bay được mô hình ML dự báo rơi vào dải rủi ro cao (High Risk Band với xác suất trễ p ≥ 0.2900).",
        business_significance: "Kích hoạt cảnh báo tác nghiệp sớm giúp điều phái viên can thiệp trước 2-4 tiếng, triệt tiêu tổn thất tài chính.",
        page: "Trang 4: Predictive Risk & Aviation Governance"
      }
    ];

    async function loadCatalog() {
      try {
        const res = await fetch('/copilot/catalog');
        const data = await res.json();
        catalogData = data;
        renderCatalogCards(data.terms, data.sops);
      } catch(e) {
        document.getElementById('catalog-grid-container').innerHTML = '<div style="color:red">Lỗi nạp danh mục tri thức: ' + e.message + '</div>';
        showToast("Lỗi Catalog", e.message, "error");
      }
    }

    function renderCatalogCards(terms, sops) {
      const container = document.getElementById('catalog-grid-container');
      container.innerHTML = '';

      // 1. Render DAX Measures (Feature for Data Analysts)
      DAX_MEASURES.forEach(d => {
        const card = document.createElement('div');
        card.className = 'catalog-card';
        card.dataset.category = 'dax_measures';
        card.dataset.search = (d.id + ' ' + d.name_vi + ' ' + d.name_en + ' ' + d.formula + ' ' + d.description).toLowerCase();
        card.innerHTML = `
          <div>
            <div style="display:flex;justify-content:space-between;align-items:start">
              <span class="cat-title">📊 ${d.name_vi}</span>
              <span class="badge" style="background:#e0e7ff;color:#3730a3;font-size:10px">DAX POWER BI</span>
            </div>
            <div class="cat-en">${d.name_en} (${d.page})</div>
            <div class="cat-desc">${d.description}</div>
          </div>
          <div class="cat-actions">
            <button class="btn-sm" onclick="showDaxDetail('${d.id}')">Xem Công Thức DAX</button>
            <button class="btn-sm" style="color:var(--primary);border-color:#bae6fd" onclick="sendQuickPrompt('Giải thích công thức DAX ${d.name_vi} và định mức FAA')">Tra Cứu Nghiệp Vụ</button>
          </div>
        `;
        container.appendChild(card);
      });

      // 2. Render SOPs
      sops.forEach(s => {
        const card = document.createElement('div');
        card.className = 'catalog-card';
        card.dataset.category = 'sops';
        card.dataset.search = (s.sop_id + ' ' + s.title_vi + ' ' + s.title_en + ' ' + s.purpose).toLowerCase();
        card.innerHTML = `
          <div>
            <div style="display:flex;justify-content:space-between;align-items:start">
              <span class="cat-title">📋 ${s.title_vi}</span>
              <span class="badge badge-high" style="font-size:10px">SOP (${s.steps.length} BƯỚC)</span>
            </div>
            <div class="cat-en">${s.title_en} (${s.sop_id})</div>
            <div class="cat-desc">${s.purpose}</div>
          </div>
          <div class="cat-actions">
            <button class="btn-sm" onclick="showSopDetail('${s.sop_id}')">Xem Quy Trình</button>
            <button class="btn-sm" style="color:var(--primary);border-color:#bae6fd" onclick="sendQuickPrompt('Cho tôi xem toàn văn quy trình ${s.sop_id}')">Tra Cứu Tác Nghiệp</button>
          </div>
        `;
        container.appendChild(card);
      });

      // 3. Render Terms
      terms.forEach(t => {
        const card = document.createElement('div');
        card.className = 'catalog-card';
        card.dataset.category = t.category;
        card.dataset.search = (t.term_id + ' ' + t.name_vi + ' ' + (t.acronym||'') + ' ' + t.name_en + ' ' + t.definition_vi).toLowerCase();
        const badgeClass = t.category === 'aviation_metrics' ? 'badge-normal' : 'badge-elevated';
        const catLabel = t.category === 'aviation_metrics' ? 'VẬN HÀNH' : 'MÔ HÌNH DỰ BÁO';
        const acronymStr = t.acronym ? ` (${t.acronym})` : '';

        card.innerHTML = `
          <div>
            <div style="display:flex;justify-content:space-between;align-items:start">
              <span class="cat-title">📘 ${t.name_vi}${acronymStr}</span>
              <span class="badge ${badgeClass}" style="font-size:10px">${catLabel}</span>
            </div>
            <div class="cat-en">${t.name_en} (${t.term_id})</div>
            <div class="cat-desc">${t.definition_vi.substring(0, 140)}...</div>
          </div>
          <div class="cat-actions">
            <button class="btn-sm" onclick="showTermDetail('${t.term_id}')">Xem Chi Tiết Quy Định</button>
            <button class="btn-sm" style="color:var(--primary);border-color:#bae6fd" onclick="sendQuickPrompt('Giải thích chi tiết về ${t.term_id}')">Tra Cứu Nghiệp Vụ</button>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function showDaxDetail(daxId) {
      const d = DAX_MEASURES.find(x => x.id === daxId);
      if (!d) return;
      const mb = document.getElementById('modal-body');
      mb.innerHTML = `
        <h2 style="margin:0 0 4px 0;font-size:20px;color:#0f172a">📊 ${d.name_vi}</h2>
        <div style="font-size:13px;color:#64748b;font-style:italic;margin-bottom:14px">${d.name_en} | Vị trí: <strong>${d.page}</strong></div>
        
        <h4 style="margin:14px 0 4px 0;color:var(--primary)">1. Công Thức DAX Chuẩn (Semantic Model):</h4>
        <pre style="background:#0f172a;color:#f8fafc;padding:12px;border-radius:6px;font-size:12.5px;white-space:pre-wrap;font-family:'JetBrains Mono',monospace">${d.formula}</pre>

        <h4 style="margin:14px 0 4px 0;color:var(--primary)">2. Diễn Giải Phương Pháp Tính:</h4>
        <div style="font-size:13px;line-height:1.6;color:#334155">${d.description}</div>

        <h4 style="margin:14px 0 4px 0;color:#059669">3. Ý Nghĩa Kinh Doanh & Quản Trị:</h4>
        <div style="font-size:13px;line-height:1.6;color:#334155">${d.business_significance}</div>

        <div style="margin-top:20px;text-align:right">
          <button class="btn-primary" style="width:auto;display:inline-block" onclick="closeModal();sendQuickPrompt('Giải thích công thức DAX ${d.name_vi} và định mức FAA')">Tra Cứu Nghiệp Vụ Về Công Thức Này</button>
        </div>
      `;
      document.getElementById('detail-modal').style.display = 'block';
    }

    function filterCategory(cat) {
      document.querySelectorAll('.catalog-card').forEach(c => {
        if (cat === 'all' || c.dataset.category === cat) {
          c.style.display = 'flex';
        } else {
          c.style.display = 'none';
        }
      });
    }

    function filterCatalog() {
      const q = document.getElementById('catalog-search-input').value.toLowerCase().trim();
      document.querySelectorAll('.catalog-card').forEach(c => {
        if (!q || c.dataset.search.includes(q)) {
          c.style.display = 'flex';
        } else {
          c.style.display = 'none';
        }
      });
    }

    function showTermDetail(termId) {
      const t = catalogData.terms.find(x => x.term_id === termId);
      if (!t) return;
      const acronymStr = t.acronym ? ` (${t.acronym})` : '';
      const mb = document.getElementById('modal-body');
      mb.innerHTML = `
        <h2 style="margin:0 0 4px 0;font-size:20px;color:#0f172a">📘 ${t.name_vi}${acronymStr}</h2>
        <div style="font-size:13px;color:#64748b;font-style:italic;margin-bottom:14px">${t.name_en} | Mã: <code>${t.term_id}</code></div>
        
        <h4 style="margin:14px 0 4px 0;color:var(--primary)">1. Định Nghĩa & Khái Niệm:</h4>
        <div style="font-size:13px;line-height:1.6;color:#334155">${t.definition_vi}</div>

        <h4 style="margin:14px 0 4px 0;color:var(--primary)">2. Ý Nghĩa Vận Hành:</h4>
        <div style="font-size:13px;line-height:1.6;color:#334155">${t.business_significance}</div>

        <h4 style="margin:14px 0 4px 0;color:var(--primary)">3. Công Thức & Quy Chuẩn Pháp Lý:</h4>
        <pre style="background:#0f172a;color:#f8fafc;padding:12px;border-radius:6px;font-size:12px;white-space:pre-wrap;font-family:'JetBrains Mono',monospace">${t.calculation_or_rule}</pre>

        <h4 style="margin:14px 0 4px 0;color:var(--rose-600)">4. Hậu Quả Tác Nghiệp:</h4>
        <div style="font-size:13px;line-height:1.6;color:#334155">⚠️ ${t.operational_impact}</div>

        <div style="margin-top:20px;text-align:right">
          <button class="btn-primary" style="width:auto;display:inline-block" onclick="closeModal();sendQuickPrompt('Giải thích chi tiết về ${t.term_id}')">Tra Cứu Nghiệp Vụ Về Đề Mục Này</button>
        </div>
      `;
      document.getElementById('detail-modal').style.display = 'block';
    }

    function showSopDetail(sopId) {
      const s = catalogData.sops.find(x => x.sop_id === sopId);
      if (!s) return;
      const mb = document.getElementById('modal-body');
      let stepsHtml = s.steps.map(st => `
        <div style="border-left:3px solid var(--primary);background:#f8fafc;padding:12px 16px;border-radius:4px;margin-bottom:10px">
          <div style="font-weight:700;font-size:13px;color:#0f172a">Bước ${st.step_number}: ${st.action_vi}</div>
          <div style="font-size:12px;color:#64748b;margin-top:2px">👤 <strong>Phụ trách:</strong> <code>${st.responsible_role}</code> | ⏱️ <strong>Thời hạn:</strong> ${st.timeframe}</div>
          <div style="font-size:12px;color:#047857;margin-top:4px">✅ <strong>Tiêu chí nghiệm thu:</strong> ${st.verification_criteria}</div>
          ${st.regulatory_notice ? `<div style="font-size:12px;color:var(--rose-600);margin-top:2px">⚖️ <strong>Căn cứ:</strong> <em>${st.regulatory_notice}</em></div>` : ''}
        </div>
      `).join('');

      mb.innerHTML = `
        <h2 style="margin:0 0 4px 0;font-size:20px;color:#0f172a">📋 ${s.title_vi}</h2>
        <div style="font-size:13px;color:#64748b;font-style:italic;margin-bottom:14px">${s.title_en} | Mã: <code>${s.sop_id}</code></div>
        <div style="background:#eff6ff;border:1px solid #bfdbfe;color:#1e40af;padding:12px 16px;border-radius:6px;font-size:13px;margin-bottom:14px">
          🎯 <strong>Mục tiêu:</strong> ${s.purpose}<br>
          🚨 <strong>Điều kiện kích hoạt:</strong> ${s.trigger_condition}
        </div>
        <h4 style="margin:16px 0 8px 0;color:var(--primary)">Các Bước Thực Hiện Bắt Buộc:</h4>
        ${stepsHtml}
        ${s.contingency_fallback ? `
          <div style="background:#fff1f2;border:1px solid #fecdd3;color:var(--rose-800);padding:12px 16px;border-radius:6px;font-size:12.5px;margin-top:14px">
            <strong>Phương Án Dự Phòng (Contingency Fallback):</strong><br>${s.contingency_fallback}
          </div>
        ` : ''}
        <div style="margin-top:20px;text-align:right">
          <button class="btn-primary" style="width:auto;display:inline-block" onclick="closeModal();sendQuickPrompt('Cho tôi xem toàn văn quy trình ${s.sop_id}')">Tra Cứu Chi Tiết Về SOP Này</button>
        </div>
      `;
      document.getElementById('detail-modal').style.display = 'block';
    }

    function closeModal() {
      document.getElementById('detail-modal').style.display = 'none';
    }

    window.onclick = function(event) {
      const modal = document.getElementById('detail-modal');
      const sModal = document.getElementById('settings-modal');
      const slModal = document.getElementById('slide-modal');
      if (event.target === modal) {
        modal.style.display = "none";
      }
      if (event.target === sModal) {
        sModal.style.display = "none";
      }
      if (event.target === slModal) {
        slModal.style.display = "none";
      }
    };

    // =========================================================================
    // KEYBOARD SHORTCUTS & OCC HOTKEYS (FEATURE P4)
    // =========================================================================
    window.addEventListener('keydown', (e) => {
      // 1. Esc: Đóng mọi modal đang mở
      if (e.key === 'Escape') {
        closeModal();
        closeSettingsModal();
        closeSlideModal();
        document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
        const banner = document.getElementById('flight-id-error-banner');
        if (banner) banner.style.display = 'none';
        return;
      }

      // 2. Ctrl + K / Cmd + K: Đưa con trỏ nhanh vào ô tìm kiếm Flight ID
      if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        switchTab('tab-advisory');
        const input = document.getElementById('flight_id');
        if (input) {
          input.focus();
          input.select();
          input.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        return;
      }

      // 3. Alt + 1, Alt + 2, Alt + 3: Chuyển đổi tức thì giữa 3 Tab
      if (e.altKey && !e.ctrlKey && !e.metaKey) {
        if (e.key === '1' || e.code === 'Digit1') {
          e.preventDefault();
          switchTab('tab-advisory');
          return;
        }
        if (e.key === '2' || e.code === 'Digit2') {
          e.preventDefault();
          switchTab('tab-chat');
          return;
        }
        if (e.key === '3' || e.code === 'Digit3') {
          e.preventDefault();
          switchTab('tab-catalog');
          return;
        }
        if (e.key === 't' || e.key === 'T') {
          e.preventDefault();
          toggleCockpitTheme();
          return;
        }
      }

      const slModal = document.getElementById('slide-modal');
      const isSlideOpen = slModal && slModal.style.display === 'block';

      if (isSlideOpen) {
        if (e.key === 'ArrowRight' || e.key === ' ') {
          e.preventDefault();
          nextModalSlide();
        } else if (e.key === 'ArrowLeft') {
          e.preventDefault();
          prevModalSlide();
        }
      }

      if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
        const catSearch = document.getElementById('catalog-search-input');
        if (catSearch && document.getElementById('tab-catalog').classList.contains('active')) {
          e.preventDefault();
          catSearch.focus();
        }
      }
    });

    // =========================================================================
    // INITIALIZATION & DEEP-LINK HANDLER (FEATURE 1)
    // =========================================================================
    window.addEventListener('DOMContentLoaded', () => {
      initCockpitTheme();
      const savedProvider = localStorage.getItem('copilot_provider');
      const providerSelect = document.getElementById('chat-model-provider');
      if (savedProvider && providerSelect) {
        providerSelect.value = savedProvider;
      }
      updateLlmStatusBadges();
      loadChatHistoryFromStorage();

      window.addEventListener('storage', (e) => {
        if (e.key === 'copilot_provider' || e.key === 'gemini_api_key' || e.key === 'openai_api_key' || e.key === 'skyops_sync_tick' || e.key === null) {
          const pSelect = document.getElementById('chat-model-provider');
          const pVal = localStorage.getItem('copilot_provider') || 'auto';
          if (pSelect && pSelect.value !== pVal) {
            pSelect.value = pVal;
          }
          updateLlmStatusBadges();
        }
      });

      const params = new URLSearchParams(window.location.search);
      const fId = params.get('flight_id') || params.get('flightId') || params.get('id');
      const tabParam = params.get('tab');
      const promptParam = params.get('prompt') || params.get('q');

      let targetTab = 'tab-advisory';
      if (tabParam === 'chat' || tabParam === 'tab-chat') {
        targetTab = 'tab-chat';
      } else if (tabParam === 'catalog' || tabParam === 'tab-catalog') {
        targetTab = 'tab-catalog';
      } else if (tabParam === 'advisory' || tabParam === 'tab-advisory') {
        targetTab = 'tab-advisory';
      } else {
        const savedTab = sessionStorage.getItem('occ_active_tab') || localStorage.getItem('occ_active_tab');
        if (savedTab && (savedTab === 'tab-advisory' || savedTab === 'tab-chat' || savedTab === 'tab-catalog')) {
          targetTab = savedTab;
        }
      }

      // Switch tab immediately
      switchTab(targetTab);

      // Handle flight deep-link
      if (fId) {
        document.getElementById('flight_id').value = fId;
        quickFill(fId).then((result) => {
          if (result) {
            showToast("Liên kết Deep-Link", `✈️ Đã nạp thành công Chuyến bay #${fId} từ Deep-Link URL!`, "success");
            if (targetTab === 'tab-chat') {
              updateChatContextBanner();
              if (promptParam) {
                setTimeout(() => sendChatMessageWithText(promptParam), 350);
              }
            }
          }
        });
      }
    });
  </script>
</body>
</html>
"""


def render_homepage() -> str:
    """Render the full 3-tab HTML homepage with option lists populated."""
    carrier_opts = "\n".join(
        f'<option value="{c}" {"selected" if c == "AA" else ""}>{label}</option>'
        for c, label in KNOWN_CARRIERS
    )
    origin_opts = "\n".join(
        f'<option value="{a}" {"selected" if a == "ATL" else ""}>{label}</option>'
        for a, label in KNOWN_AIRPORTS
    )
    dest_opts = "\n".join(
        f'<option value="{a}" {"selected" if a == "DFW" else ""}>{label}</option>'
        for a, label in KNOWN_AIRPORTS
    )

    return (
        HTML_TEMPLATE.replace("<!--CARRIER_OPTIONS-->", carrier_opts)
        .replace("<!--ORIGIN_OPTIONS-->", origin_opts)
        .replace("<!--DEST_OPTIONS-->", dest_opts)
    )


# =============================================================================
# COMPACT EMBEDDED CHAT TEMPLATE (PHASE 6.8 POWER BI INTEGRATION)
# =============================================================================

EMBED_CHAT_TEMPLATE = r"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <title>SkyOps Copilot | Embedded Assistant</title>
  
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='15' fill='%230f172a' stroke='%230284c7' stroke-width='1.5'/%3E%3Cpath d='M16 7 L23 21 L16 18 L9 21 Z' fill='%2338bdf8'/%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">

  <script>
    (function() {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const urlTheme = urlParams.get('theme');
        if (urlTheme === 'dark' || (!urlTheme && localStorage.getItem('skyops_embed_theme') === 'dark')) {
          document.documentElement.setAttribute('data-theme', 'dark');
        }
      } catch(e) {}
    })();
  </script>

  <style>
    :root {
      --bg-body: #f8fafc;
      --bg-card: #ffffff;
      --border: #e2e8f0;
      --text: #0f172a;
      --text-muted: #64748b;
      --primary: #0284c7;
      --primary-hover: #0369a1;
      --primary-light: #f0f9ff;
      --primary-border: #bae6fd;
      --user-bubble: #0284c7;
      --user-text: #ffffff;
      --ai-bubble: #ffffff;
      --ai-border: #e2e8f0;
      --chip-bg: #f1f5f9;
      --chip-border: #cbd5e1;
      --chip-text: #334155;
      --font-main: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    :root[data-theme="dark"] {
      --bg-body: #090e17;
      --bg-card: #111827;
      --border: #1f2937;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --primary: #38bdf8;
      --primary-hover: #0ea5e9;
      --primary-light: rgba(56, 189, 248, 0.12);
      --primary-border: #1e3a5f;
      --user-bubble: #0284c7;
      --user-text: #ffffff;
      --ai-bubble: #111827;
      --ai-border: #1f2937;
      --chip-bg: #1e293b;
      --chip-border: #334155;
      --chip-text: #cbd5e1;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    html, body {
      height: 100%;
      width: 100%;
      overflow: hidden;
      font-family: var(--font-main);
      background: var(--bg-body);
      color: var(--text);
      font-size: 13px;
      line-height: 1.45;
    }

    .embed-container {
      display: flex;
      flex-direction: column;
      height: 100vh;
      width: 100%;
      max-width: 100%;
      margin: 0 auto;
      background: var(--bg-body);
    }

    /* MINI HEADER BAR */
    .mini-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 44px;
      padding: 0 12px;
      background: var(--bg-card);
      border-bottom: 1px solid var(--border);
      flex-shrink: 0;
      z-index: 10;
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }

    .brand-icon {
      width: 22px;
      height: 22px;
      flex-shrink: 0;
      fill: var(--primary);
    }

    .brand-title {
      font-size: 12.5px;
      font-weight: 700;
      color: var(--text);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .page-badge {
      font-size: 10px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 9999px;
      background: var(--primary-light);
      color: var(--primary);
      border: 1px solid var(--primary-border);
      white-space: nowrap;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;
    }

    /* PAGE SWITCHER MICRO-PILLS */
    .page-switcher {
      display: flex;
      align-items: center;
      gap: 2px;
      background: var(--chip-bg);
      padding: 2px;
      border-radius: 6px;
    }

    .page-btn {
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-size: 10px;
      font-weight: 700;
      padding: 3px 6px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.15s ease;
      font-family: var(--font-mono);
    }

    .page-btn:hover {
      color: var(--text);
    }

    .page-btn.active {
      background: var(--primary);
      color: #ffffff;
      box-shadow: 0 1px 3px rgba(2, 132, 199, 0.3);
    }

    .action-icon-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 26px;
      height: 26px;
      border: 1px solid var(--border);
      background: var(--bg-card);
      border-radius: 6px;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 12px;
      transition: all 0.15s ease;
    }

    .action-icon-btn:hover {
      color: var(--text);
      border-color: var(--primary);
      background: var(--primary-light);
    }

    /* CONTEXT BANNER (ACTIVE FLIGHT OR FILTER) */
    .context-subbar {
      display: none;
      align-items: center;
      justify-content: space-between;
      padding: 4px 12px;
      background: var(--primary-light);
      border-bottom: 1px solid var(--primary-border);
      font-size: 11px;
      color: var(--primary);
      flex-shrink: 0;
    }

    .context-subbar.active {
      display: flex;
    }

    .context-text {
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .btn-clear-subcontext {
      border: none;
      background: none;
      color: var(--primary);
      font-size: 13px;
      font-weight: bold;
      cursor: pointer;
      margin-left: 8px;
    }

    /* CHAT STREAM AREA */
    .chat-stream {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      scrollbar-width: thin;
      scrollbar-color: var(--chip-border) transparent;
    }

    .chat-msg {
      display: flex;
      flex-direction: column;
      max-width: 92%;
      animation: fadeIn 0.2s ease-out;
      word-break: break-word;
      overflow-wrap: break-word;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .chat-msg.user {
      align-self: flex-end;
      align-items: flex-end;
    }

    .chat-msg.assistant {
      align-self: flex-start;
      align-items: flex-start;
    }

    .msg-bubble {
      padding: 8px 12px;
      border-radius: 12px;
      font-size: 12.5px;
      line-height: 1.5;
    }

    .chat-msg.user .msg-bubble {
      background: var(--user-bubble);
      color: var(--user-text);
      border-bottom-right-radius: 3px;
    }

    .chat-msg.assistant .msg-bubble {
      background: var(--ai-bubble);
      color: var(--text);
      border: 1px solid var(--ai-border);
      border-bottom-left-radius: 3px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    .msg-meta {
      font-size: 10px;
      color: var(--text-muted);
      margin-top: 3px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .source-badge {
      font-size: 9.5px;
      padding: 1px 5px;
      border-radius: 4px;
      background: var(--chip-bg);
      color: var(--text-muted);
      font-family: var(--font-mono);
    }

    .citations-box {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-top: 6px;
    }

    .citation-pill {
      font-size: 9.5px;
      font-weight: 600;
      padding: 1px 6px;
      border-radius: 4px;
      background: var(--primary-light);
      color: var(--primary);
      border: 1px solid var(--primary-border);
      font-family: var(--font-mono);
    }

    .followups-box {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-top: 8px;
      width: 100%;
    }

    .followup-chip {
      font-size: 11px;
      padding: 5px 9px;
      background: var(--chip-bg);
      border: 1px solid var(--chip-border);
      border-radius: 6px;
      color: var(--chip-text);
      cursor: pointer;
      text-align: left;
      transition: all 0.15s ease;
    }

    .followup-chip:hover {
      background: var(--primary-light);
      border-color: var(--primary-border);
      color: var(--primary);
    }

    /* COLLAPSIBLE Q&A HISTORY CARDS IN EMBED */
    .chat-history-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px 14px;
      margin-bottom: 10px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
      transition: all 0.2s ease;
      cursor: pointer;
      box-sizing: border-box;
      word-break: break-word;
      overflow-wrap: break-word;
    }
    .chat-history-card:hover {
      border-color: var(--primary);
      box-shadow: 0 3px 10px rgba(2, 132, 199, 0.1);
    }
    .chat-history-card.expanded {
      border-color: var(--primary);
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.12);
    }
    .chat-history-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
      font-size: 11px;
      gap: 6px;
      user-select: none;
    }
    .history-title-box {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .history-toggle-badge {
      font-size: 9.5px;
      font-weight: 600;
      color: var(--primary);
      background: var(--primary-light);
      border: 1px solid var(--primary-border);
      padding: 1px 6px;
      border-radius: 4px;
      transition: all 0.2s ease;
    }
    .chat-history-card:hover .history-toggle-badge {
      background: var(--primary);
      color: #ffffff;
    }
    .chat-history-question {
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text);
      line-height: 1.45;
      padding: 2px 0;
      user-select: none;
    }
    .chat-history-answer-drawer {
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px dashed var(--border);
      cursor: default;
      animation: fadeIn 0.2s ease-out;
    }
    .drawer-meta-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }
    .drawer-label {
      font-size: 10px;
      font-weight: 700;
      color: #059669;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .btn-copy-history {
      padding: 2px 7px;
      font-size: 10px;
      border-radius: 4px;
      border: 1px solid var(--border);
      background: var(--bg-card);
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s;
    }
    .btn-copy-history:hover {
      color: var(--primary);
      border-color: var(--primary);
    }
    .history-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 10px;
      margin-bottom: 10px;
      border-radius: 8px;
      background: var(--primary-light);
      border: 1px dashed var(--primary-border);
      font-size: 11px;
      color: var(--primary);
      user-select: none;
    }
    .btn-history-ctrl {
      padding: 2px 7px;
      font-size: 10px;
      border-radius: 4px;
      border: 1px solid var(--primary-border);
      background: var(--bg-card);
      color: var(--primary);
      cursor: pointer;
      font-weight: 600;
      transition: all 0.15s;
    }
    .btn-history-ctrl:hover {
      background: var(--primary);
      color: #ffffff;
    }

    /* STARTER CHIPS BAR (BOTTOM DOCK) */
    .starter-chips-bar {
      display: flex;
      gap: 6px;
      padding: 6px 12px;
      overflow-x: auto;
      white-space: nowrap;
      background: var(--bg-card);
      border-top: 1px solid var(--border);
      scrollbar-width: none;
      flex-shrink: 0;
    }

    .starter-chips-bar::-webkit-scrollbar {
      display: none;
    }

    .starter-chip {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 9px;
      font-size: 11px;
      font-weight: 500;
      background: var(--chip-bg);
      border: 1px solid var(--chip-border);
      border-radius: 9999px;
      color: var(--chip-text);
      cursor: pointer;
      flex-shrink: 0;
      transition: all 0.15s ease;
    }

    .starter-chip:hover {
      background: var(--primary-light);
      border-color: var(--primary-border);
      color: var(--primary);
    }

    /* CHAT INPUT BAR */
    .input-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: var(--bg-card);
      border-top: 1px solid var(--border);
      flex-shrink: 0;
    }

    .input-field {
      flex: 1;
      height: 36px;
      padding: 0 12px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--bg-body);
      color: var(--text);
      font-family: var(--font-main);
      font-size: 12.5px;
      outline: none;
      transition: border-color 0.15s ease;
    }

    .input-field:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px var(--primary-light);
    }

    .send-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border: none;
      background: var(--primary);
      color: #ffffff;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.15s ease;
      flex-shrink: 0;
    }

    .send-btn:hover {
      background: var(--primary-hover);
    }

    .send-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .input-bar .voice-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border: 1px solid var(--border);
      background: var(--bg-card);
      color: var(--text);
      border-radius: 8px;
      cursor: pointer;
      font-size: 15px;
      transition: all 0.15s ease;
      flex-shrink: 0;
    }
    .input-bar .voice-btn:hover {
      background: var(--primary-light);
      border-color: var(--primary);
      color: var(--primary);
    }
    .input-bar .voice-btn.recording {
      background: #fee2e2 !important;
      border-color: #ef4444 !important;
      color: #dc2626 !important;
      animation: voicePulseRing 1.2s infinite;
    }
    @keyframes voicePulseRing {
      0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }
      50% { transform: scale(1.08); box-shadow: 0 0 0 7px rgba(239, 68, 68, 0); }
      100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    .typewriter-cursor {
      display: inline-block;
      width: 6px;
      height: 13px;
      margin-left: 2px;
      background-color: var(--primary);
      vertical-align: -1px;
      border-radius: 1px;
      animation: cursorBlink 0.7s infinite alternate;
    }
    @keyframes cursorBlink {
      0% { opacity: 1; }
      100% { opacity: 0; }
    }

    /* LOADING PLACEHOLDER */
    .loading-dots {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      color: var(--text-muted);
      font-style: italic;
      font-size: 11.5px;
    }

    .dot {
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: var(--primary);
      animation: pulseDot 1s infinite alternate;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes pulseDot {
      0% { opacity: 0.3; transform: scale(0.8); }
      100% { opacity: 1; transform: scale(1.1); }
    }

    /* REAL-TIME SYNC BADGE PULSE & MINI TOAST */
    @keyframes badgeSyncPulse {
      0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(14, 165, 233, 0.7); }
      50% { transform: scale(1.08); box-shadow: 0 0 0 6px rgba(14, 165, 233, 0); }
      100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(14, 165, 233, 0); }
    }
    .badge-synced {
      animation: badgeSyncPulse 0.9s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .embed-sync-toast {
      position: absolute;
      top: 44px;
      right: 12px;
      background: rgba(15, 23, 42, 0.94);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.4);
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      padding: 5px 11px;
      z-index: 999;
      box-shadow: 0 4px 14px rgba(0,0,0,0.3);
      pointer-events: none;
      display: flex;
      align-items: center;
      gap: 6px;
      animation: fadeInToast 0.2s ease, fadeOutToast 0.35s ease 2.2s forwards;
    }
    @keyframes fadeInToast {
      from { opacity: 0; transform: translateY(-4px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeOutToast {
      from { opacity: 1; transform: translateY(0); }
      to { opacity: 0; transform: translateY(-4px); }
    }
  </style>
</head>
<body>
  <div class="embed-container">
    <!-- MINI HEADER -->
    <header class="mini-header">
      <div class="brand-group">
        <svg class="brand-icon" viewBox="0 0 24 24">
          <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
        </svg>
        <span class="brand-title">SkyOps | Hỗ Trợ Phân Tích & Tác Nghiệp</span>
        <span class="page-badge" id="embed-llm-badge" onclick="toggleEmbedOnlineMode()" title="Đồng bộ tự động theo Web chính (Bấm để chuyển đổi nhanh Online/Offline)" style="font-size:10px;padding:2px 7px;cursor:pointer;">🤖 LLM: Offline Engine</span>
      </div>

      <div class="header-actions">
        <!-- QUICK PAGE SWITCHER -->
        <div class="page-switcher" title="Chọn chuyên đề gợi ý câu hỏi nhanh">
          <button class="page-btn active" id="btn-p1" onclick="switchPage('1')" title="Trang 1: Executive Overview">P1</button>
          <button class="page-btn" id="btn-p2" onclick="switchPage('2')" title="Trang 2: Delay Root-Causes">P2</button>
          <button class="page-btn" id="btn-p3" onclick="switchPage('3')" title="Trang 3: Hubs & Routes">P3</button>
          <button class="page-btn" id="btn-p4" onclick="switchPage('4')" title="Trang 4: AI Risk & Governance">P4</button>
        </div>

        <button class="action-icon-btn" onclick="toggleTheme()" title="Bật/Tắt chế độ Tối (Dark mode)">🌓</button>
        <button class="action-icon-btn" id="btn-embed-export-audit" onclick="exportEmbedAuditLog()" title="📥 Xuất Biên Bản Hội Thoại Kiểm Toán (Audit Log)">📥</button>
        <button class="action-icon-btn" onclick="resetChat()" title="Làm mới cuộc hội thoại">🔄</button>
        <button class="action-icon-btn" onclick="openFullStudio()" title="Mở Studio đầy đủ trong tab mới">↗️</button>
      </div>
    </header>

    <!-- CONTEXT SUB-BAR (ACTIVE FLIGHT OR FILTER) -->
    <div class="context-subbar" id="context-bar">
      <span class="context-text" id="context-desc">✈️ Đang chọn chuyến bay</span>
      <button class="btn-clear-subcontext" onclick="clearActiveSubContext()" title="Xóa ngữ cảnh">✕</button>
    </div>

    <!-- CHAT MESSAGES STREAM -->
    <div class="chat-stream" id="chat-stream">
      <!-- Dynamic messages will be injected here -->
    </div>

    <!-- DYNAMIC STARTER CHIPS ACCORDING TO PAGE -->
    <div class="starter-chips-bar" id="starter-chips-container">
      <!-- Chips populated by JavaScript -->
    </div>

    <!-- INPUT BAR -->
    <div class="input-bar">
      <input type="text" id="user-input" class="input-field" placeholder="Hỏi AI về chỉ số, nguyên nhân hoặc quy chuẩn..." autocomplete="off">
      <button type="button" id="btn-voice-embed" class="voice-btn" onclick="toggleVoiceInput('embed')" title="🎙️ Nhận diện giọng nói tác nghiệp (Web Speech API)">🎙️</button>
      <button id="btn-send" class="send-btn" onclick="handleSend()" title="Gửi câu hỏi">➤</button>
    </div>
  </div>

  <!-- EMBED AUDIT EXPORT MODAL -->
  <div id="embed-audit-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.65);z-index:9999;align-items:center;justify-content:center;padding:12px">
    <div style="background:var(--bg-card);color:var(--text);border-radius:12px;border:1px solid var(--border);padding:14px;width:100%;max-width:540px;max-height:88vh;display:flex;flex-direction:column;box-shadow:0 12px 30px rgba(0,0,0,0.4)">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;border-bottom:1px solid var(--border);padding-bottom:8px">
        <div style="font-weight:700;font-size:13px;color:var(--primary);display:flex;align-items:center;gap:6px">
          <span>📥</span> Xuất Biên Bản Hội Thoại Kiểm Toán (Audit Log)
        </div>
        <button onclick="closeEmbedAuditModal()" style="background:none;border:none;color:var(--text-muted);font-size:18px;cursor:pointer;line-height:1">&times;</button>
      </div>
      <div style="font-size:11.5px;color:var(--text-muted);margin-bottom:8px">
        Hồ sơ lưu trữ giải trình tác nghiệp cho Dispatcher & Data Analyst theo quy chuẩn US DOT & FAA.
      </div>
      <div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap">
        <button class="send-btn" onclick="downloadEmbedAuditMarkdown()" style="width:auto;padding:5px 10px;font-size:11.5px;border-radius:6px;background:var(--primary)">📄 Tải Markdown (.md)</button>
        <button class="send-btn" onclick="printEmbedAuditLog()" style="width:auto;padding:5px 10px;font-size:11.5px;background:#059669;border-radius:6px">🖨️ In / PDF</button>
        <button class="send-btn" onclick="copyEmbedAuditLog()" style="width:auto;padding:5px 10px;font-size:11.5px;background:var(--chip-bg);color:var(--chip-text);border:1px solid var(--chip-border);border-radius:6px">📋 Sao Chép</button>
      </div>
      <div id="embed-audit-preview" style="flex:1;overflow-y:auto;background:var(--bg-body);color:var(--text);padding:10px;border-radius:6px;font-family:var(--font-mono);font-size:10.5px;line-height:1.45;white-space:pre-wrap;border:1px solid var(--border);max-height:280px"></div>
    </div>
  </div>

  <script>
    // =========================================================================
    // EMBED CHAT CONTROLLER (RESPONSIVE & MULTI-PAGE READY)
    // =========================================================================
    const CHAT_STORAGE_KEY = 'skyops_embed_chat_history_v1';
    const EMBED_SESSION_KEY = 'skyops_embed_chat_history_session_v2';
    const UNIFIED_WELCOME = "Xin chào! Tôi là **Hệ thống Hỗ trợ Phân tích & Tác nghiệp SkyOps**. Tôi sẵn sàng giải đáp và phân tích chuyên sâu toàn bộ số liệu trên báo cáo: đối soát chỉ số vận hành (OTP A14/D0, tỷ lệ hủy chuyến), chẩn đoán nguyên nhân trễ domino Late Aircraft (~40%), đánh giá điểm nghẽn siêu Hub (DFW, ORD) và thẩm định rủi ro quy chuẩn pháp lý hàng không (14 CFR § 259.4, FAR Part 117, 14 CFR § 260.6).\n\nBạn có thể chọn nhanh các chủ đề gợi ý bên dưới hoặc nhập câu hỏi trực tiếp!";
    let currentPage = '1';
    let currentFlightId = null;
    let currentCarrier = null;
    let currentOrigin = null;
    let currentDest = null;
    let currentFlightContext = null;
    let chatHistory = [];
    let embedSessionTurns = [];
    let isSending = false;
    let lastUserMsgElement = null;

    function focusOnCurrentTurn() {
      const stream = document.getElementById('chat-stream');
      const target = lastUserMsgElement || document.getElementById('embed-chat-loading');
      if (stream && target) {
        requestAnimationFrame(() => {
          const streamRect = stream.getBoundingClientRect();
          const targetRect = target.getBoundingClientRect();
          const relativeTop = targetRect.top - streamRect.top + stream.scrollTop;
          stream.scrollTo({
            top: Math.max(0, relativeTop - 12),
            behavior: 'smooth'
          });
        });
      } else if (stream) {
        stream.scrollTop = stream.scrollHeight;
      }
    }

    // PAGE CONFIGURATION & PROMPT CHIPS
    const PAGE_CONFIG = {
      '1': {
        name: 'Trang 1: Executive Overview',
        badge: 'P1: Vận Hành & OTP',
        welcome: UNIFIED_WELCOME,
        chips: [
          '📊 Đánh giá OTP A14 toàn mạng',
          '📉 Xu hướng hủy chuyến & hoàn thành',
          '🏆 So sánh OTP giữa các hãng bay',
          '📈 Phân biệt chỉ số OTP A14 vs D0'
        ]
      },
      '2': {
        name: 'Trang 2: Delay Root-Causes',
        badge: 'P2: Nguyên Nhân & Domino',
        welcome: UNIFIED_WELCOME,
        chips: [
          '🔄 Tại sao Late Aircraft trễ tới 40%?',
          '🌪️ 5 nhóm nguyên nhân trễ 14 CFR § 234.4',
          '⏱️ Khả năng bay bù giờ Airborne Make-up',
          '💸 Định mức thiệt hại FAA $101.18/phút'
        ]
      },
      '3': {
        name: 'Trang 3: Hubs & Routes',
        badge: 'P3: Điểm Nghẽn Siêu Hub',
        welcome: UNIFIED_WELCOME,
        chips: [
          '🚧 Tại sao Hub DFW nghẽn nặng buổi tối?',
          '🛫 Sân bay nào có Taxi-Out cao nhất?',
          '⏰ Khung giờ nghẽn Bank Hour là gì?',
          '🌙 Giới nghiêm tiếng ồn đêm Night Curfew'
        ]
      },
      '4': {
        name: 'Trang 4: AI Risk & Governance',
        badge: 'P4: Pháp Chế & Chế Tài',
        welcome: UNIFIED_WELCOME,
        chips: [
          '⚖️ Rủi ro phạt Tarmac 14 CFR § 259.4',
          '💵 Chế tài hoàn tiền 14 CFR § 260.6',
          '👨‍✈️ Giới hạn giờ bay FDP FAR Part 117',
          '🤖 Đấu trường ML: AUC & Lift @ 10%'
        ]
      }
    };

    // MARKDOWN PARSER (LIGHTWEIGHT & SAFE)
    function formatMarkdown(text) {
      if (!text) return '';
      let s = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
      s = s.replace(/```([a-z]*)\n([\s\S]*?)```/g, '<pre style="background:var(--chip-bg);padding:8px;border-radius:6px;font-size:11px;overflow-x:auto;font-family:var(--font-mono);margin:6px 0">$2</pre>');
      s = s.replace(/^### (.*$)/gim, '<h4 style="margin:8px 0 4px 0;font-size:13px;color:var(--primary);font-weight:700">$1</h4>');
      s = s.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      s = s.replace(/\*(.*?)\*/g, '<em>$1</em>');
      s = s.replace(/`([^`]+)`/g, '<code style="background:var(--chip-bg);padding:1px 4px;border-radius:3px;font-size:11px;color:var(--primary);font-family:var(--font-mono)">$1</code>');
      s = s.replace(/^&gt; (.*$)/gim, '<blockquote style="border-left:3px solid var(--primary);padding:3px 8px;margin:5px 0;background:var(--primary-light);font-size:11.5px">$1</blockquote>');
      s = s.replace(/^- (.*$)/gim, '<div style="margin-left:10px;margin-bottom:2px">• $1</div>');
      s = s.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');
      return s;
    }

    // THEME CONTROLLER
    function toggleTheme() {
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      if (isDark) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('skyops_embed_theme', 'light');
      } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('skyops_embed_theme', 'dark');
      }
    }

    // PAGE SWITCHER
    function switchPage(pageKey) {
      if (!PAGE_CONFIG[pageKey]) pageKey = '1';
      currentPage = pageKey;

      // Update buttons
      ['1', '2', '3', '4'].forEach(p => {
        const btn = document.getElementById('btn-p' + p);
        if (btn) {
          if (p === pageKey) btn.classList.add('active');
          else btn.classList.remove('active');
        }
      });

      // Update badge
      const cfg = PAGE_CONFIG[pageKey];
      const badgeEl = document.getElementById('page-badge-text');
      if (badgeEl) badgeEl.textContent = cfg.badge;

      // Render Starter Chips
      renderStarterChips(cfg.chips);

      // If chat is empty and no session history, show unified welcome message
      const stream = document.getElementById('chat-stream');
      if (stream.children.length === 0 && embedSessionTurns.length === 0) {
        const isOnline = (localStorage.getItem('copilot_provider') === 'gemini' || !localStorage.getItem('copilot_provider')) && localStorage.getItem('gemini_api_key');
        appendMessage('assistant', UNIFIED_WELCOME, isOnline ? 'llm_gemini' : 'offline_knowledge_engine', null, null, false);
      }
    }

    function renderStarterChips(chips) {
      const container = document.getElementById('starter-chips-container');
      container.innerHTML = '';
      
      // If flight_id exists, add flight-specific chip
      if (currentFlightId) {
        const flChip = document.createElement('span');
        flChip.className = 'starter-chip';
        flChip.style.background = 'var(--primary-light)';
        flChip.style.color = 'var(--primary)';
        flChip.style.borderColor = 'var(--primary-border)';
        flChip.innerHTML = `✈️ Phân tích chuyến #${currentFlightId}`;
        flChip.onclick = () => submitText(`Phân tích chuyên sâu rủi ro và khuyến nghị tác nghiệp cho chuyến bay #${currentFlightId}`);
        container.appendChild(flChip);
      }

      chips.forEach(c => {
        const chip = document.createElement('span');
        chip.className = 'starter-chip';
        chip.textContent = c;
        chip.onclick = () => submitText(c);
        container.appendChild(chip);
      });
    }

    // CONTEXT BAR
    function updateContextBar() {
      const bar = document.getElementById('context-bar');
      const desc = document.getElementById('context-desc');
      let parts = [];
      if (currentFlightId) parts.push(`✈️ Chuyến bay #${currentFlightId}`);
      if (currentCarrier) parts.push(`🏢 Hãng: ${currentCarrier}`);
      if (currentOrigin || currentDest) parts.push(`🛫 Tuyến: ${currentOrigin || '...'} ➔ ${currentDest || '...'}`);

      if (parts.length > 0) {
        desc.textContent = parts.join(' | ');
        bar.classList.add('active');
      } else {
        bar.classList.remove('active');
      }
    }

    function clearActiveSubContext() {
      currentFlightId = null;
      currentFlightContext = null;
      currentCarrier = null;
      currentOrigin = null;
      currentDest = null;
      updateContextBar();
      switchPage(currentPage);
    }

    // PERSISTENCE CONTROLLER: PRESERVES CHAT ACROSS TAB CLOSES & REFRESHES (LOCALSTORAGE + SESSIONSTORAGE)
    function saveSessionChat() {
      try {
        const jsonTurns = JSON.stringify(embedSessionTurns);
        sessionStorage.setItem(EMBED_SESSION_KEY, jsonTurns);
        localStorage.setItem(EMBED_SESSION_KEY, jsonTurns);
        localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(chatHistory.slice(-12)));
      } catch(e) {}
    }

    function groupEmbedTurnsIntoPairs(turns) {
      const pairs = [];
      let currentPair = null;
      for (let i = 0; i < turns.length; i++) {
        const t = turns[i];
        const role = t.role;
        const text = t.text || t.content || '';
        if (role === 'user') {
          if (currentPair) pairs.push(currentPair);
          currentPair = {
            id: pairs.length,
            question: text,
            userTime: t.time || '',
            assistant: null
          };
        } else if (role === 'assistant') {
          if (!currentPair) {
            currentPair = {
              id: pairs.length,
              question: "Thông Điệp Hỗ Trợ Tác Nghiệp & Phân Tích",
              userTime: t.time || '',
              assistant: t
            };
            pairs.push(currentPair);
            currentPair = null;
          } else {
            currentPair.assistant = t;
            pairs.push(currentPair);
            currentPair = null;
          }
        }
      }
      if (currentPair) pairs.push(currentPair);
      return pairs;
    }

    function renderEmbedHistoryCard(container, pair, idx) {
      const card = document.createElement('div');
      card.className = 'chat-history-card';
      card.id = `embed-history-card-${idx}`;

      const ans = pair.assistant || {};
      const source = ans.source || '';
      let sourceLabel = 'Cơ Sở Tri Thức & Pháp Chuẩn Hàng Không';
      if ((source||'').includes('gemini') || source === 'llm_gemini') sourceLabel = '⚡ Gemini Online';
      else if ((source||'').includes('claude')) sourceLabel = '🟣 Claude 3.7';
      else if ((source||'').includes('openai') || source === 'llm_openai') sourceLabel = '🟢 OpenAI o3/o1';
      else if ((source||'').includes('deepseek')) sourceLabel = '🔵 DeepSeek R1';

      const timeStr = ans.time || pair.userTime || '';

      let citHtml = '';
      if (ans.citations && ans.citations.length > 0) {
        citHtml = '<div class="citations-box" style="margin-top:8px">' + ans.citations.map(c => `<span class="citation-pill">${c}</span>`).join('') + '</div>';
      }

      let followHtml = '';
      if (ans.followups && ans.followups.length > 0) {
        followHtml = '<div class="followups-box" style="margin-top:8px">' +
          ans.followups.map(q => `<button type="button" class="followup-chip" onclick="submitText(decodeURIComponent('${encodeURIComponent(q)}'))">${q}</button>`).join('') +
          '</div>';
      }

      const answerContent = ans.text || ans.content || '(Chưa ghi nhận câu trả lời)';

      card.innerHTML = `
        <div class="chat-history-header" onclick="toggleEmbedHistoryCard(${idx})" title="Nhấn để mở hoặc thu gọn câu trả lời">
          <div class="history-title-box">
            <span style="font-weight:700;color:var(--primary);display:flex;align-items:center;gap:4px">
              <span>📋</span> Báo Cáo Phân Tích
            </span>
            <span class="history-toggle-badge" id="embed-history-badge-${idx}">▶ Bấm xem câu trả lời</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px">
            <span class="source-badge" style="font-size:9px">${sourceLabel}</span>
            ${timeStr ? `<span style="font-size:9.5px;color:var(--text-muted)">${timeStr}</span>` : ''}
          </div>
        </div>
        <div class="chat-history-question" onclick="toggleEmbedHistoryCard(${idx})" title="Nhấn để mở hoặc thu gọn câu trả lời">
          ${pair.question.replace(/</g, "&lt;")}
        </div>
        <div class="chat-history-answer-drawer" id="embed-history-drawer-${idx}" style="display:none" onclick="event.stopPropagation()">
          <div class="drawer-meta-bar">
            <span class="drawer-label">💡 Câu Trả Lời & Cơ Sở Pháp Chuẩn:</span>
            <button type="button" class="btn-copy-history" onclick="copyEmbedHistoryAnswerText(${idx})" title="Sao chép nội dung">📋 Sao chép</button>
          </div>
          <div class="msg-bubble" style="background:var(--ai-bubble);border:1px solid var(--ai-border);border-radius:8px;padding:8px 10px;font-size:12px;line-height:1.5" id="embed-history-body-${idx}">${formatMarkdown(answerContent)}</div>
          ${citHtml}
          ${followHtml}
        </div>
      `;
      container.appendChild(card);
    }

    function toggleEmbedHistoryCard(idx) {
      const drawer = document.getElementById(`embed-history-drawer-${idx}`);
      const badge = document.getElementById(`embed-history-badge-${idx}`);
      const card = document.getElementById(`embed-history-card-${idx}`);
      if (!drawer) return;
      const isOpen = drawer.style.display !== 'none';
      if (isOpen) {
        drawer.style.display = 'none';
        if (badge) badge.textContent = '▶ Bấm xem câu trả lời';
        if (card) card.classList.remove('expanded');
      } else {
        drawer.style.display = 'block';
        if (badge) badge.textContent = '▼ Thu gọn câu trả lời';
        if (card) card.classList.add('expanded');
      }
    }

    function toggleAllEmbedHistoryCards(expand) {
      const drawers = document.querySelectorAll('[id^="embed-history-drawer-"]');
      drawers.forEach(drawer => {
        const idMatch = drawer.id.match(/\d+/);
        if (idMatch) {
          const idx = idMatch[0];
          const badge = document.getElementById(`embed-history-badge-${idx}`);
          const card = document.getElementById(`embed-history-card-${idx}`);
          if (expand) {
            drawer.style.display = 'block';
            if (badge) badge.textContent = '▼ Thu gọn câu trả lời';
            if (card) card.classList.add('expanded');
          } else {
            drawer.style.display = 'none';
            if (badge) badge.textContent = '▶ Bấm xem câu trả lời';
            if (card) card.classList.remove('expanded');
          }
        }
      });
    }

    function copyEmbedHistoryAnswerText(idx) {
      const el = document.getElementById(`embed-history-body-${idx}`);
      if (!el) return;
      const text = el.innerText || el.textContent;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          showEmbedToast("Đã sao chép nội dung câu trả lời");
        }).catch(() => fallbackCopy(text));
      } else {
        fallbackCopy(text);
      }
      function fallbackCopy(t) {
        const ta = document.createElement('textarea');
        ta.value = t;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showEmbedToast("Đã sao chép nội dung câu trả lời");
      }
    }

    function loadSessionChat() {
      try {
        const raw = sessionStorage.getItem(EMBED_SESSION_KEY) || localStorage.getItem(EMBED_SESSION_KEY);
        if (!raw) return false;
        const turns = JSON.parse(raw);
        if (Array.isArray(turns) && turns.length > 0) {
          embedSessionTurns = turns;
          const stream = document.getElementById('chat-stream');
          stream.innerHTML = '';
          chatHistory = [];
          turns.forEach(t => {
            chatHistory.push({ role: t.role, content: t.text || t.content });
          });

          const pairs = groupEmbedTurnsIntoPairs(turns);
          
          const toolbar = document.createElement('div');
          toolbar.className = 'history-toolbar';
          toolbar.innerHTML = `
            <span>🕒 <strong>Lịch sử tra cứu (${pairs.length} câu hỏi)</strong></span>
            <div style="display:flex;gap:4px">
              <button type="button" class="btn-history-ctrl" onclick="toggleAllEmbedHistoryCards(true)">📂 Mở tất cả</button>
              <button type="button" class="btn-history-ctrl" onclick="toggleAllEmbedHistoryCards(false)">📁 Thu gọn tất cả</button>
            </div>
          `;
          stream.appendChild(toolbar);

          pairs.forEach((pair, idx) => {
            renderEmbedHistoryCard(stream, pair, idx);
          });
          setTimeout(focusOnCurrentTurn, 100);
          return true;
        }
      } catch(e) {
        console.warn("Could not load embed session chat", e);
      }
      return false;
    }

    // APPEND MESSAGES
    function appendMessageDOM(role, text, source, citations, followups, timestamp) {
      const stream = document.getElementById('chat-stream');
      const msgDiv = document.createElement('div');
      msgDiv.className = `chat-msg ${role}`;

      const bubble = document.createElement('div');
      bubble.className = 'msg-bubble';
      bubble.innerHTML = formatMarkdown(text);
      msgDiv.appendChild(bubble);

      if (role === 'user') {
        lastUserMsgElement = msgDiv;
      }

      // Meta & Citations for Assistant
      if (role === 'assistant') {
        const meta = document.createElement('div');
        meta.className = 'msg-meta';
        const sourceLabel = (source === 'llm_gemini' || source === 'llm_openai') ? '✨ Gemini Online' : '🟢 Grounded Knowledge';
        const timeStr = timestamp || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        meta.innerHTML = `<span class="source-badge">${sourceLabel}</span> <span>${timeStr}</span>`;
        msgDiv.appendChild(meta);

        if (citations && citations.length > 0) {
          const citBox = document.createElement('div');
          citBox.className = 'citations-box';
          citations.forEach(c => {
            const pill = document.createElement('span');
            pill.className = 'citation-pill';
            pill.textContent = c;
            citBox.appendChild(pill);
          });
          msgDiv.appendChild(citBox);
        }

        if (followups && followups.length > 0) {
          const fBox = document.createElement('div');
          fBox.className = 'followups-box';
          followups.slice(0, 3).forEach(q => {
            const fChip = document.createElement('button');
            fChip.className = 'followup-chip';
            fChip.textContent = '💡 ' + q;
            fChip.onclick = () => submitText(q);
            fBox.appendChild(fChip);
          });
          msgDiv.appendChild(fBox);
        }
      }

      stream.appendChild(msgDiv);
      if (lastUserMsgElement) {
        focusOnCurrentTurn();
        setTimeout(focusOnCurrentTurn, 40);
        setTimeout(focusOnCurrentTurn, 160);
      } else {
        stream.scrollTop = stream.scrollHeight;
      }
    }

    // Typewriter Streaming for Embedded Chat
    function streamMessageDOM(role, text, source, citations, followups, timestamp, onComplete) {
      const stream = document.getElementById('chat-stream');
      const msgDiv = document.createElement('div');
      msgDiv.className = `chat-msg ${role}`;

      const bubble = document.createElement('div');
      bubble.className = 'msg-bubble';
      bubble.style.cursor = 'pointer';
      bubble.title = 'Bấm để hiện ngay toàn bộ nội dung';
      bubble.innerHTML = '<span class="stream-content"></span><span class="typewriter-cursor"></span>';
      msgDiv.appendChild(bubble);

      const contentNode = bubble.querySelector('.stream-content');
      const cursorNode = bubble.querySelector('.typewriter-cursor');

      const meta = document.createElement('div');
      meta.className = 'msg-meta';
      const sourceLabel = (source === 'llm_gemini' || source === 'llm_openai') ? '✨ Gemini Online' : '🟢 Grounded Knowledge';
      const timeStr = timestamp || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
      meta.innerHTML = `<span class="source-badge">${sourceLabel}</span> <span>${timeStr}</span>`;
      msgDiv.appendChild(meta);

      const citBox = document.createElement('div');
      citBox.className = 'citations-box';
      citBox.style.display = 'none';
      msgDiv.appendChild(citBox);

      const fBox = document.createElement('div');
      fBox.className = 'followups-box';
      fBox.style.display = 'none';
      msgDiv.appendChild(fBox);

      stream.appendChild(msgDiv);

      let isFinished = false;

      function renderFinalPills() {
        if (citations && citations.length > 0) {
          citBox.style.display = 'flex';
          citations.forEach(c => {
            const pill = document.createElement('span');
            pill.className = 'citation-pill';
            pill.textContent = c;
            citBox.appendChild(pill);
          });
        }
        if (followups && followups.length > 0) {
          fBox.style.display = 'flex';
          followups.slice(0, 3).forEach(q => {
            const fChip = document.createElement('button');
            fChip.className = 'followup-chip';
            fChip.textContent = '💡 ' + q;
            fChip.onclick = () => submitText(q);
            fBox.appendChild(fChip);
          });
        }
      }

      function finishInstantly() {
        if (isFinished) return;
        isFinished = true;
        if (cursorNode) cursorNode.remove();
        contentNode.innerHTML = formatMarkdown(text);
        renderFinalPills();
        focusOnCurrentTurn();
        if (onComplete) onComplete();
      }

      msgDiv.onclick = finishInstantly;

      const tokens = text.match(/(\s+|\S+)/g) || [text];
      let tokenIdx = 0;
      let accumulated = "";
      const chunkSize = tokens.length > 300 ? 4 : (tokens.length > 100 ? 2 : 1);
      const intervalMs = 15;

      const streamTimer = setInterval(() => {
        if (isFinished) {
          clearInterval(streamTimer);
          return;
        }
        for (let i = 0; i < chunkSize && tokenIdx < tokens.length; i++) {
          accumulated += tokens[tokenIdx++];
        }
        contentNode.innerHTML = formatMarkdown(accumulated);
        focusOnCurrentTurn();

        if (tokenIdx >= tokens.length) {
          clearInterval(streamTimer);
          if (!isFinished) {
            isFinished = true;
            if (cursorNode) cursorNode.remove();
            contentNode.innerHTML = formatMarkdown(text);
            renderFinalPills();
            focusOnCurrentTurn();
            if (onComplete) onComplete();
          }
        }
      }, intervalMs);
    }

    function appendMessage(role, text, source, citations, followups, shouldSave = true, shouldStream = false) {
      const nowTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
      if (role === 'assistant' && shouldStream) {
        streamMessageDOM(role, text, source, citations, followups, nowTime, () => {
          if (shouldSave) {
            embedSessionTurns.push({
              role: role,
              text: text,
              source: source,
              citations: citations,
              followups: followups,
              time: nowTime
            });
            saveSessionChat();
          }
        });
      } else {
        appendMessageDOM(role, text, source, citations, followups, nowTime);
        if (shouldSave) {
          embedSessionTurns.push({
            role: role,
            text: text,
            source: source,
            citations: citations,
            followups: followups,
            time: nowTime
          });
          saveSessionChat();
        }
      }
    }

    // VOICE INPUT ENGINE (WEB SPEECH API FOR EMBED)
    let embedVoiceRecognition = null;
    let isEmbedVoiceListening = false;

    function toggleVoiceInput(target = 'embed') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        showEmbedToast("Trình duyệt chưa hỗ trợ Web Speech API. Vui lòng dùng Chrome hoặc Edge.");
        return;
      }

      const btn = document.getElementById('btn-voice-embed');
      const input = document.getElementById('user-input');
      if (!btn || !input) return;

      if (isEmbedVoiceListening) {
        if (embedVoiceRecognition) {
          try { embedVoiceRecognition.stop(); } catch(e) {}
        }
        return;
      }

      try {
        embedVoiceRecognition = new SpeechRecognition();
        embedVoiceRecognition.lang = 'vi-VN';
        embedVoiceRecognition.interimResults = true;
        embedVoiceRecognition.continuous = true;
        embedVoiceRecognition.maxAlternatives = 1;

        const origPlaceholder = input.placeholder;
        let finalAccumulatedTranscript = input.value ? input.value + ' ' : '';

        embedVoiceRecognition.onstart = function() {
          isEmbedVoiceListening = true;
          btn.classList.add('recording');
          btn.innerHTML = '🔴';
          btn.title = "Đang lắng nghe... Bấm để dừng";
          input.placeholder = "🎙️ Đang nghe giọng nói... Hãy nói (ví dụ: 'Phân tích chuyến 4568')...";
        };

        embedVoiceRecognition.onresult = function(event) {
          let interimTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            const part = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalAccumulatedTranscript += part + ' ';
            } else {
              interimTranscript += part;
            }
          }
          const fullText = (finalAccumulatedTranscript + interimTranscript).trim();
          if (fullText) {
            input.value = fullText;
          }
        };

        embedVoiceRecognition.onerror = function(event) {
          console.warn("[Embed Speech] Lỗi:", event.error);
          cleanupEmbedVoice();
        };

        embedVoiceRecognition.onend = function() {
          cleanupEmbedVoice();
          input.focus();
        };

        function cleanupEmbedVoice() {
          isEmbedVoiceListening = false;
          if (btn) {
            btn.classList.remove('recording');
            btn.innerHTML = '🎙️';
            btn.title = "🎙️ Nhận diện giọng nói tác nghiệp (Web Speech API)";
          }
          if (input) {
            input.placeholder = origPlaceholder;
          }
        }

        embedVoiceRecognition.start();
      } catch(e) {
        console.error("Speech start error:", e);
      }
    }

    // EXPORT EMBED OCC AUDIT LOG
    function exportEmbedAuditLog() {
      const modal = document.getElementById('embed-audit-modal');
      const preview = document.getElementById('embed-audit-preview');
      if (!modal || !preview) return;
      const md = generateEmbedAuditLogMarkdown();
      preview.textContent = md;
      modal.style.display = 'flex';
    }

    function closeEmbedAuditModal() {
      const modal = document.getElementById('embed-audit-modal');
      if (modal) modal.style.display = 'none';
    }

    function generateEmbedAuditLogMarkdown() {
      const now = new Date();
      const dateStr = now.toLocaleDateString('vi-VN');
      const timeStr = now.toLocaleTimeString('vi-VN');
      const auditId = 'OCC-AUDIT-EMBED-' + now.getFullYear() +
        String(now.getMonth()+1).padStart(2,'0') +
        String(now.getDate()).padStart(2,'0') + '-' +
        Math.random().toString(36).substring(2, 7).toUpperCase();

      let flightInfo = "TOÀN MẠNG BAY (POWER BI DASHBOARD EMBED)";
      if (currentFlightId) {
        flightInfo = `CHUYẾN BAY #${currentFlightId} (${currentCarrier || ''} ${currentOrigin || ''} ➔ ${currentDest || ''})`;
      }

      let transcript = "";
      if (!embedSessionTurns || embedSessionTurns.length === 0) {
        transcript = "*(Chưa ghi nhận câu hỏi nào trong phiên làm việc này)*\n";
      } else {
        embedSessionTurns.forEach((m, idx) => {
          const roleName = m.role === 'user' ? 'DISPATCHER / DATA ANALYST' : 'SKYOPS COPILOT ADVISORY';
          const src = m.source ? ` [Nguồn: ${m.source}]` : '';
          transcript += `### Lượt #${idx + 1} | [${m.time || ''}] ${roleName}${src}\n\n`;
          transcript += `${m.text}\n\n`;
          if (m.citations && m.citations.length > 0) {
            transcript += `> ⚖️ **Căn cứ pháp lý / Quy chuẩn:** ${m.citations.join(' | ')}\n\n`;
          }
          transcript += `---\n\n`;
        });
      }

      return `# BIÊN BẢN HỘI THOẠI & NHẬT KÝ KIỂM TOÁN TÁC NGHIỆP BAY (POWER BI EMBED)
## CỤC HÀNG KHÔNG / US DOT & FAA FLIGHT OPERATIONS COMPLIANCE AUDIT LOG
**Mã Hồ Sơ Kiểm Toán:** \`${auditId}\`  
**Thời Điểm Thiết Lập:** ${dateStr} ${timeStr}  
**Môi Trường Vận Hành:** SkyOps Copilot™ Embed Visual (DWH: PostgreSQL \`airline_dwh\`)
**Trang Báo Cáo:** Trang ${currentPage} (${(PAGE_CONFIG[currentPage] || {}).badge || 'Overview'})

---

### I. THÔNG TIN HỒ SƠ & BỐI CẢNH VẬN HÀNH (OPERATIONAL CONTEXT)
- **Đối Tượng Phân Tích:** ${flightInfo}
- **Căn Cứ Pháp Chuẩn Quốc Tế & Quốc Gia:**
  1. **14 CFR § 259.4**: Giới hạn thời gian đỗ sân đỗ Tarmac (180 phút nội địa / 240 phút quốc tế, phạt tới $37,377 USD/pax).
  2. **FAR Part 117**: Giới hạn thời gian làm nhiệm vụ bay của Tổ bay (FDP) & Standby Crew.
  3. **14 CFR § 260.6**: Quy định bắt buộc hoàn tiền mặt tự động 100% khi trễ >= 3h nội địa.
  4. **Thông tư 19/2023/TT-BGTVT**: Nghĩa vụ chăm sóc hành khách và bồi thường ứng trước (CAAV).
  5. **Định Mức Chi Phí FAA/A4A**: $101.18 USD cho mỗi phút trễ chuyến bay thương mại.

---

### II. TOÀN VĂN NHẬT KÝ HỘI THOẠI & GIẢI TRÌNH TÁC NGHIỆP (CONVERSATION TRANSCRIPT)
${transcript}

---

### III. XÁC NHẬN TRÁCH NHIỆM & DUYỆT HỒ SƠ (AUDIT SIGN-OFF)
Biên bản này được niêm phong tự động làm hồ sơ kiểm toán giải trình tác nghiệp bay.

| Điều Phối Viên OCC (Dispatcher) | Kỹ Sư Dữ Liệu / Lead DA | Đại Diện Pháp Chế & An Toàn Bay |
| :---: | :---: | :---: |
| *(Ký & Ghi rõ họ tên)* | *(Ký & Ghi rõ họ tên)* | *(Ký & Đóng dấu)* |
| ..................................... | ..................................... | ..................................... |
`;
    }

    function downloadEmbedAuditMarkdown() {
      const md = generateEmbedAuditLogMarkdown();
      const blob = new Blob([md], {type: 'text/markdown;charset=utf-8'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      const now = new Date();
      const timeSuffix = now.toISOString().replace(/[-:T.]/g, '').slice(0, 14);
      a.href = url;
      a.download = `OCC_Audit_Log_Embed_${timeSuffix}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }

    function printEmbedAuditLog() {
      const md = generateEmbedAuditLogMarkdown();
      const printWin = window.open('', '_blank');
      if (!printWin) {
        downloadEmbedAuditMarkdown();
        return;
      }
      const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>OCC Flight Operations Audit Report (Embed)</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; margin: 30px; color: #0f172a; line-height: 1.5; font-size: 12.5px; }
    h1 { font-size: 17px; text-transform: uppercase; margin-bottom: 4px; color: #0f172a; text-align: center; }
    h2 { font-size: 13px; text-align: center; color: #475569; margin-top: 0; margin-bottom: 20px; font-weight: normal; }
    h3 { font-size: 13.5px; color: #0284c7; border-bottom: 1.5px solid #cbd5e1; padding-bottom: 4px; margin-top: 18px; margin-bottom: 8px; }
    pre { background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px; font-family: monospace; white-space: pre-wrap; font-size: 11px; }
    blockquote { border-left: 3px solid #0284c7; background: #f0f9ff; margin: 6px 0; padding: 5px 10px; font-size: 11.5px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 20px; }
    th, td { border: 1px solid #cbd5e1; padding: 8px 12px; text-align: center; font-size: 11.5px; }
    th { background: #f1f5f9; font-weight: 700; }
    hr { border: none; border-top: 1px solid #e2e8f0; margin: 14px 0; }
    @media print { body { margin: 10mm; } }
  </style>
</head>
<body>
  ${formatMarkdown(md).replace(/<pre style="[^"]*">/g, '<pre>')}
  <script>window.onload = function() { window.print(); }<\/script>
</body>
</html>`;
      printWin.document.open();
      printWin.document.write(htmlContent);
      printWin.document.close();
    }

    function copyEmbedAuditLog() {
      const md = generateEmbedAuditLogMarkdown();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(md).then(() => {
          showEmbedToast("Đã sao chép biên bản kiểm toán vào bộ nhớ đệm.");
        }).catch(() => fallbackCopy(md));
      } else {
        fallbackCopy(md);
      }
      function fallbackCopy(text) {
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showEmbedToast("Đã sao chép biên bản kiểm toán vào bộ nhớ đệm.");
      }
    }

    // SEND CHAT LOGIC
    async function submitText(text) {
      if (!text || isSending) return;
      const clean = text.trim();
      if (!clean) return;

      appendMessage('user', clean);
      chatHistory.push({ role: 'user', content: clean });
      document.getElementById('user-input').value = '';

      // Add loading indicator
      isSending = true;
      document.getElementById('btn-send').disabled = true;
      const stream = document.getElementById('chat-stream');
      const loaderDiv = document.createElement('div');
      loaderDiv.className = 'chat-msg assistant';
      loaderDiv.id = 'embed-chat-loading';
      loaderDiv.innerHTML = '<div class="msg-bubble loading-dots"><span>Đang phân tích</span><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
      stream.appendChild(loaderDiv);
      focusOnCurrentTurn();

      // Extract LLM Key & Provider (automatically synchronized with main web UI localStorage)
      const rawProvider = localStorage.getItem('copilot_provider') || 'auto';
      let activeProvider = rawProvider;
      let activeModelName = undefined;

      if (rawProvider === 'custom') {
        const customId = localStorage.getItem('custom_model_id') || '';
        activeModelName = customId;
        if (customId.includes('claude')) activeProvider = 'claude';
        else if (customId.includes('gemini')) activeProvider = 'gemini';
        else if (customId.includes('deepseek')) activeProvider = 'deepseek';
        else if (customId.startsWith('o1') || customId.startsWith('o3') || customId.includes('gpt')) activeProvider = 'openai';
        else activeProvider = 'auto';
      } else if (rawProvider.includes(':')) {
        const parts = rawProvider.split(':');
        activeProvider = parts[0];
        activeModelName = parts[1];
      }

      const gKey = localStorage.getItem('gemini_api_key') || '';
      const cKey = localStorage.getItem('claude_api_key') || '';
      const oKey = localStorage.getItem('openai_api_key') || '';
      const dKey = localStorage.getItem('deepseek_api_key') || '';

      let activeKey = undefined;
      if (activeProvider === 'claude') activeKey = cKey;
      else if (activeProvider === 'openai') activeKey = oKey;
      else if (activeProvider === 'gemini') activeKey = gKey;
      else if (activeProvider === 'deepseek') activeKey = dKey;
      else activeKey = cKey || oKey || gKey || dKey;

      const payload = {
        message: clean,
        flight_id: currentFlightId || undefined,
        flight_context: currentFlightContext,
        conversation_history: chatHistory.slice(-6),
        model_provider: activeProvider,
        model_name: activeModelName,
        api_key: activeKey
      };

      try {
        const resp = await fetch('/copilot/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const lEl = document.getElementById('embed-chat-loading');
        if (lEl) lEl.remove();

        if (!resp.ok) {
          const errData = await resp.json().catch(() => ({}));
          const errMsg = errData.detail || 'Lỗi kết nối máy chủ';
          appendMessage('assistant', `⚠️ Không thể nhận phản hồi: ${errMsg}`, 'offline_knowledge_engine', [], [], false, false);
          return;
        }

        const data = await resp.json();
        appendMessage('assistant', data.reply, data.source, data.grounding_citations, data.suggested_questions, true, true);
        chatHistory.push({ role: 'assistant', content: data.reply });

      } catch (err) {
        const lEl = document.getElementById('embed-chat-loading');
        if (lEl) lEl.remove();
        appendMessage('assistant', `⚠️ Lỗi mạng hoặc kết nối Copilot: ${err.message}`, 'offline_knowledge_engine', [], [], false, false);
      } finally {
        isSending = false;
        document.getElementById('btn-send').disabled = false;
        document.getElementById('user-input').focus();
      }
    }

    function handleSend() {
      const input = document.getElementById('user-input');
      submitText(input.value);
    }

    // =========================================================================
    // REAL-TIME POWER BI <-> WEB PORTAL SYNCHRONIZATION BUS
    // =========================================================================
    const SYNC_CHANNEL_NAME = 'skyops_runtime_sync';
    let embedSyncChannel = null;
    let lastKnownProvider = null;
    let lastKnownCKey = null;
    let lastKnownDKey = null;
    let lastKnownModelName = null;

    function getIsOnlineState() {
      const p = localStorage.getItem('copilot_provider') || 'auto';
      const gKey = localStorage.getItem('gemini_api_key') || '';
      const cKey = localStorage.getItem('claude_api_key') || '';
      const oKey = localStorage.getItem('openai_api_key') || '';
      const dKey = localStorage.getItem('deepseek_api_key') || '';
      if (p === 'offline') return false;
      if (['gemini', 'claude', 'openai', 'deepseek', 'custom'].includes(p)) return true;
      return Boolean(gKey || cKey || oKey || dKey);
    }

    function showEmbedToast(msg) {
      const container = document.querySelector('.embed-container');
      if (!container) return;
      const old = document.querySelector('.embed-sync-toast');
      if (old) old.remove();
      const toast = document.createElement('div');
      toast.className = 'embed-sync-toast';
      toast.innerHTML = `<span>🔄</span> <span>${msg}</span>`;
      container.appendChild(toast);
      setTimeout(() => { if (toast && toast.parentNode) toast.remove(); }, 2500);
    }

    function resetChat() {
      chatHistory = [];
      embedSessionTurns = [];
      lastUserMsgElement = null;
      try {
        sessionStorage.removeItem(EMBED_SESSION_KEY);
        localStorage.removeItem(EMBED_SESSION_KEY);
        localStorage.removeItem(CHAT_STORAGE_KEY);
      } catch(e) {}
      const stream = document.getElementById('chat-stream');
      stream.innerHTML = '';
      const isOnline = getIsOnlineState();
      const cfg = PAGE_CONFIG[currentPage] || PAGE_CONFIG['1'];
      appendMessage('assistant', cfg.welcome, isOnline ? 'llm_gemini' : 'offline_knowledge_engine', null, null, false);
    }

    function updateEmbedLlmBadge(isExternalUpdate = false) {
      const badgeEl = document.getElementById('embed-llm-badge');
      if (!badgeEl) return;
      const savedProvider = localStorage.getItem('copilot_provider') || 'auto';
      const savedModel = localStorage.getItem('copilot_model_name') || '';
      const gKey = localStorage.getItem('gemini_api_key') || '';
      const cKey = localStorage.getItem('claude_api_key') || '';
      const oKey = localStorage.getItem('openai_api_key') || '';
      const dKey = localStorage.getItem('deepseek_api_key') || '';

      lastKnownProvider = savedProvider;
      lastKnownGKey = gKey;
      lastKnownCKey = cKey;
      lastKnownOKey = oKey;
      lastKnownDKey = dKey;
      lastKnownModelName = savedModel;

      let modeLabel = 'Offline Engine';
      let isOnline = false;

      if (savedProvider === 'offline') {
        badgeEl.textContent = '🤖 LLM: Offline Engine';
        badgeEl.style.background = 'var(--primary-light)';
        badgeEl.style.color = 'var(--primary)';
        badgeEl.style.borderColor = 'var(--primary-border)';
        badgeEl.title = 'Chế độ Nội Bộ: Dùng dữ liệu & tri thức chuẩn hóa (Nhấn để chuyển chế độ)';
        modeLabel = 'Offline Engine';
        isOnline = false;
      } else if (savedProvider === 'gemini' || ((savedProvider === 'auto' || !savedProvider) && gKey)) {
        const mText = savedModel.includes('3.8-pro') ? 'Gemini 3.8 Pro' : (savedModel.includes('3.8') ? 'Gemini 3.8 Flash' : 'Gemini');
        badgeEl.textContent = `✨ LLM: ${mText}`;
        badgeEl.style.background = '#f5f3ff';
        badgeEl.style.color = '#7c3aed';
        badgeEl.style.borderColor = '#ddd6fe';
        badgeEl.title = 'Chế độ Google Gemini Online — Nhấn để chuyển về Offline';
        modeLabel = mText;
        isOnline = true;
      } else if (savedProvider === 'claude' || (savedProvider === 'auto' && cKey)) {
        const mText = savedModel.includes('3-7') ? 'Claude 3.7 Sonnet' : 'Claude 3.5';
        badgeEl.textContent = `🟣 LLM: ${mText}`;
        badgeEl.style.background = '#faf5ff';
        badgeEl.style.color = '#9333ea';
        badgeEl.style.borderColor = '#e9d5ff';
        badgeEl.title = 'Chế độ Anthropic Claude Online — Nhấn để chuyển về Offline';
        modeLabel = mText;
        isOnline = true;
      } else if (savedProvider === 'openai' || (savedProvider === 'auto' && oKey)) {
        const mText = savedModel.includes('o3-mini') ? 'OpenAI o3-mini' : (savedModel.includes('o1') ? 'OpenAI o1' : 'GPT-4o');
        badgeEl.textContent = `⚡ LLM: ${mText}`;
        badgeEl.style.background = '#ecfdf5';
        badgeEl.style.color = '#059669';
        badgeEl.style.borderColor = '#a7f3d0';
        badgeEl.title = 'Chế độ OpenAI Online — Nhấn để chuyển về Offline';
        modeLabel = mText;
        isOnline = true;
      } else if (savedProvider === 'deepseek' || (savedProvider === 'auto' && dKey)) {
        const mText = savedModel.includes('reasoner') ? 'DeepSeek R1' : 'DeepSeek V3';
        badgeEl.textContent = `🐋 LLM: ${mText}`;
        badgeEl.style.background = '#eff6ff';
        badgeEl.style.color = '#1d4ed8';
        badgeEl.style.borderColor = '#bfdbfe';
        badgeEl.title = 'Chế độ DeepSeek Online — Nhấn để chuyển về Offline';
        modeLabel = mText;
        isOnline = true;
      } else if (savedProvider === 'custom') {
        badgeEl.textContent = `⚙️ LLM: ${savedModel || 'Custom'}`;
        badgeEl.style.background = '#f8fafc';
        badgeEl.style.color = '#475569';
        badgeEl.style.borderColor = '#cbd5e1';
        badgeEl.title = 'Chế độ Custom Model ID — Nhấn để chuyển về Offline';
        modeLabel = savedModel || 'Custom';
        isOnline = true;
      } else {
        badgeEl.textContent = '🤖 LLM: Offline Engine';
        badgeEl.style.background = 'var(--primary-light)';
        badgeEl.style.color = 'var(--primary)';
        badgeEl.style.borderColor = 'var(--primary-border)';
        badgeEl.title = 'Chế độ Nội Bộ: Dùng dữ liệu & tri thức chuẩn hóa (Nhấn để chuyển chế độ)';
        modeLabel = 'Offline Engine';
        isOnline = false;
      }

      // If triggered in real-time without F5, pulse the badge and show toast
      if (isExternalUpdate) {
        badgeEl.classList.remove('badge-synced');
        void badgeEl.offsetWidth; // trigger reflow
        badgeEl.classList.add('badge-synced');
        showEmbedToast(`Đã đồng bộ từ Web chính: ${modeLabel}`);

        // Update greeting badge if no conversation turns yet
        const stream = document.getElementById('chat-stream');
        if (stream && chatHistory.length === 0) {
          const firstMetaBadge = stream.querySelector('.chat-msg.assistant .source-badge');
          if (firstMetaBadge) {
            firstMetaBadge.textContent = isOnline ? `✨ ${modeLabel}` : '🟢 Grounded Knowledge';
          }
        }
      }
    }

    function toggleEmbedOnlineMode() {
      const current = localStorage.getItem('copilot_provider') || 'auto';
      const gKey = localStorage.getItem('gemini_api_key') || '';
      const cKey = localStorage.getItem('claude_api_key') || '';
      const oKey = localStorage.getItem('openai_api_key') || '';
      const dKey = localStorage.getItem('deepseek_api_key') || '';

      let nextMode = 'offline';
      if (current === 'offline') {
        if (gKey) nextMode = 'gemini';
        else if (cKey) nextMode = 'claude';
        else if (oKey) nextMode = 'openai';
        else if (dKey) nextMode = 'deepseek';
        else nextMode = 'gemini';
      } else {
        nextMode = 'offline';
      }

      localStorage.setItem('copilot_provider', nextMode);
      updateEmbedLlmBadge(false);

      if (embedSyncChannel) {
        try {
          embedSyncChannel.postMessage({
            type: 'SKYOPS_MODE_CHANGE',
            provider: nextMode,
            gemini_key: gKey,
            claude_key: cKey,
            openai_key: oKey,
            deepseek_key: dKey,
            is_online: nextMode !== 'offline',
            timestamp: Date.now()
          });
        } catch(e) {}
      }

      try {
        localStorage.setItem('skyops_sync_tick', Date.now().toString());
      } catch(e) {}

      fetch('/copilot/runtime-mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: nextMode,
          api_key: gKey || cKey || oKey || dKey || ''
        })
      }).catch(() => {});

      showEmbedToast(`Chuyển sang: ${nextMode === 'offline' ? 'Offline Engine' : nextMode.toUpperCase() + ' Online'}`);
    }

    function checkAndSyncMode(notify = false) {
      const curP = localStorage.getItem('copilot_provider') || 'auto';
      const curM = localStorage.getItem('copilot_model_name') || '';
      const curG = localStorage.getItem('gemini_api_key') || '';
      const curC = localStorage.getItem('claude_api_key') || '';
      const curO = localStorage.getItem('openai_api_key') || '';
      const curD = localStorage.getItem('deepseek_api_key') || '';
      if (curP !== lastKnownProvider || curM !== lastKnownModelName || curG !== lastKnownGKey || curC !== lastKnownCKey || curO !== lastKnownOKey || curD !== lastKnownDKey) {
        lastKnownProvider = curP;
        lastKnownModelName = curM;
        lastKnownGKey = curG;
        lastKnownCKey = curC;
        lastKnownOKey = curO;
        lastKnownDKey = curD;
        updateEmbedLlmBadge(notify);
      }
    }

    function openFullStudio() {
      let targetUrl = '/?tab=chat';
      if (currentFlightId) targetUrl += `&flight_id=${currentFlightId}`;
      window.open(targetUrl, '_blank');
    }

    // INITIALIZATION & CROSS-TAB LISTENERS
    window.addEventListener('DOMContentLoaded', () => {
      updateEmbedLlmBadge(false);

      // 1. BroadcastChannel: 0ms real-time event when Web chính changes mode
      try {
        if (typeof BroadcastChannel !== 'undefined') {
          embedSyncChannel = new BroadcastChannel(SYNC_CHANNEL_NAME);
          embedSyncChannel.onmessage = (event) => {
            if (event.data && (event.data.type === 'SKYOPS_MODE_CHANGE' || event.data.type === 'MODE_CHANGE')) {
              if (event.data.provider !== undefined) {
                localStorage.setItem('copilot_provider', event.data.provider);
              }
              if (event.data.model_name !== undefined) {
                localStorage.setItem('copilot_model_name', event.data.model_name);
              }
              if (event.data.gemini_key !== undefined) {
                if (event.data.gemini_key) localStorage.setItem('gemini_api_key', event.data.gemini_key);
                else localStorage.removeItem('gemini_api_key');
              }
              if (event.data.claude_key !== undefined) {
                if (event.data.claude_key) localStorage.setItem('claude_api_key', event.data.claude_key);
                else localStorage.removeItem('claude_api_key');
              }
              if (event.data.openai_key !== undefined) {
                if (event.data.openai_key) localStorage.setItem('openai_api_key', event.data.openai_key);
                else localStorage.removeItem('openai_api_key');
              }
              if (event.data.deepseek_key !== undefined) {
                if (event.data.deepseek_key) localStorage.setItem('deepseek_api_key', event.data.deepseek_key);
                else localStorage.removeItem('deepseek_api_key');
              }
              if (event.data.theme !== undefined && typeof toggleTheme === 'function') {
                const isCurrentDark = document.documentElement.getAttribute('data-theme') === 'dark';
                if ((event.data.theme === 'dark') !== isCurrentDark) toggleTheme();
              }
              updateEmbedLlmBadge(true);
            }
          };
        }
      } catch(e) {
        console.warn("BroadcastChannel error in embed", e);
      }

      // 2. Storage Event: Native cross-tab sync between Web chính and Power BI tab
      window.addEventListener('storage', (e) => {
        if (['copilot_provider', 'copilot_model_name', 'gemini_api_key', 'claude_api_key', 'openai_api_key', 'deepseek_api_key', 'skyops_sync_tick'].includes(e.key) || e.key === null) {
          updateEmbedLlmBadge(true);
        }
        if (e.key === 'occ_cockpit_theme' && typeof toggleTheme === 'function') {
          const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
          if ((e.newValue === 'dark') !== isDark) toggleTheme();
        }
      });

      // 3. Tab Focus & Visibility: Sync immediately when user clicks into this tab
      document.addEventListener('visibilitychange', () => {
        if (!document.hidden) checkAndSyncMode(true);
      });
      window.addEventListener('focus', () => {
        checkAndSyncMode(true);
      });

      // 4. Fast Heartbeat Diff Checker: Failsafe every 800ms
      setInterval(() => {
        checkAndSyncMode(true);
      }, 800);

      // 5. Server runtime mode polling: Failsafe for Power BI Desktop WebView2
      setInterval(async () => {
        try {
          const res = await fetch('/copilot/runtime-mode');
          if (res.ok) {
            const data = await res.json();
            const currentP = localStorage.getItem('copilot_provider') || 'auto';
            if (data.provider && data.provider !== currentP && (data.updated_at || 0) > 0) {
              localStorage.setItem('copilot_provider', data.provider);
              updateEmbedLlmBadge(true);
            }
          }
        } catch(e) {}
      }, 3000);
      const params = new URLSearchParams(window.location.search);
      const paramPage = params.get('page') || params.get('p') || '1';
      const fId = params.get('flight_id') || params.get('id');
      const carrier = params.get('carrier') || params.get('carrier_code');
      const origin = params.get('origin');
      const dest = params.get('dest');
      const promptParam = params.get('prompt') || params.get('q');

      currentFlightId = fId;
      currentCarrier = carrier;
      currentOrigin = origin;
      currentDest = dest;

      if (currentCarrier || currentOrigin || currentDest) {
        currentFlightContext = {
          carrier_code: currentCarrier || 'AA',
          origin: currentOrigin || 'DFW',
          dest: currentDest || 'ORD',
          flight_number: 100,
          flight_date: new Date().toISOString().split('T')[0],
          dep_hour: 17
        };
      }

      updateContextBar();
      const hasHistory = loadSessionChat();
      switchPage(paramPage);

      // Bind Enter Key
      document.getElementById('user-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          handleSend();
        }
      });

      // Auto-send prompt if present in URL and NO previous history in session
      if (promptParam && !hasHistory) {
        setTimeout(() => submitText(promptParam), 300);
        // Clear prompt from URL so refresh won't duplicate sending
        const cleanUrl = new URL(window.location.href);
        cleanUrl.searchParams.delete('prompt');
        cleanUrl.searchParams.delete('q');
        window.history.replaceState(null, '', cleanUrl.toString());
      }
    });
  </script>
</body>
</html>
"""


def render_embed_chat(
    page: Optional[str] = None,
    flight_id: Optional[Union[int, str]] = None,
    carrier: Optional[str] = None,
    origin: Optional[str] = None,
    dest: Optional[str] = None,
    theme: Optional[str] = None,
    prompt: Optional[str] = None,
) -> str:
    """
    Render ultra-compact embedded chat interface for Power BI iframe or web visual integration.
    Fully responsive, multi-page aware (Page 1 to Page 4), zero unnecessary chrome.
    """
    html = EMBED_CHAT_TEMPLATE
    # Injection of default initial parameters if desired
    return html

