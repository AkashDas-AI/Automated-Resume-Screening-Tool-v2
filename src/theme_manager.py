"""
Theme Manager Module for Streamlit Dashboard
Author: Akash Das
Project: Automated Resume Screening Tool

Responsible for providing centralized, maintainable Light Mode and Dark Mode styling
for the interactive Streamlit dashboard via carefully scoped CSS injection.
"""

from typing import Dict, Any


# --------------------------------------------------------------------------
# Centralized Color Palette Definitions
# --------------------------------------------------------------------------
THEME_PALETTES: Dict[str, Dict[str, str]] = {
    "light": {
        "app_bg": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "card_border": "#CBD5E1",
        "card_shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.04)",
        "sidebar_bg": "#F1F5F9",
        "sidebar_border": "#CBD5E1",
        "text_primary": "#0F172A",
        "text_secondary": "#334155",
        "text_muted": "#64748B",
        "brand_primary": "#1D4ED8",
        "brand_secondary": "#2563EB",
        "brand_accent": "#0284C7",
        "metric_val": "#1D4ED8",
        "metric_bg": "#F8FAFC",
        "metric_border": "#CBD5E1",
        "input_bg": "#FFFFFF",
        "input_border": "#CBD5E1",
        "input_text": "#0F172A",
        "table_header_bg": "#E2E8F0",
        "table_header_text": "#0F172A",
        "table_row_alt": "#F8FAFC",
        "tag_high_bg": "#DCFCE7",
        "tag_high_text": "#166534",
        "tag_mod_bg": "#DBEAFE",
        "tag_mod_text": "#1E40AF",
        "tag_low_bg": "#FEF3C7",
        "tag_low_text": "#92400E",
        "btn_primary_bg": "#1D4ED8",
        "btn_primary_text": "#FFFFFF",
        "btn_primary_hover": "#1E40AF",
        "btn_toggle_bg": "#E2E8F0",
        "btn_toggle_text": "#0F172A",
        "chart_bg": "#FFFFFF",
        "chart_grid": "#E2E8F0",
        "chart_text": "#0F172A",
    },
    "dark": {
        "app_bg": "#0B1120",
        "card_bg": "#1E293B",
        "card_border": "#334155",
        "card_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.3)",
        "sidebar_bg": "#070C18",
        "sidebar_border": "#1E293B",
        "text_primary": "#F8FAFC",
        "text_secondary": "#CBD5E1",
        "text_muted": "#94A3B8",
        "brand_primary": "#38BDF8",
        "brand_secondary": "#60A5FA",
        "brand_accent": "#38BDF8",
        "metric_val": "#38BDF8",
        "metric_bg": "#1E293B",
        "metric_border": "#334155",
        "input_bg": "#1E293B",
        "input_border": "#475569",
        "input_text": "#F8FAFC",
        "table_header_bg": "#0F172A",
        "table_header_text": "#38BDF8",
        "table_row_alt": "#162032",
        "tag_high_bg": "#14532D",
        "tag_high_text": "#86EFAC",
        "tag_mod_bg": "#1E3A8A",
        "tag_mod_text": "#93C5FD",
        "tag_low_bg": "#713F12",
        "tag_low_text": "#FDE047",
        "btn_primary_bg": "#0284C7",
        "btn_primary_text": "#FFFFFF",
        "btn_primary_hover": "#38BDF8",
        "btn_toggle_bg": "#334155",
        "btn_toggle_text": "#F8FAFC",
        "chart_bg": "#1E293B",
        "chart_grid": "#334155",
        "chart_text": "#F8FAFC",
    },
}


def get_theme_colors(theme: str) -> Dict[str, str]:
    """Retrieve color palette mapping for the designated theme ('light' or 'dark')."""
    normalized = theme.lower().strip() if isinstance(theme, str) else "light"
    return THEME_PALETTES.get(normalized, THEME_PALETTES["light"])


def get_theme_css(theme: str) -> str:
    """
    Generate complete, carefully scoped CSS for the Streamlit dashboard
    corresponding to the selected theme ('light' or 'dark').

    Ensures high contrast, proper element styling, readable fonts, and
    eliminates white-on-white or dark-on-dark text artifacts.
    """
    c = get_theme_colors(theme)
    is_dark = (theme.lower().strip() == "dark")

    return f"""
    <style>
    /* =====================================================================
       GLOBAL STYLES & APP CONTAINER
       ===================================================================== */
    .stApp {{
        background-color: {c["app_bg"]} !important;
        color: {c["text_primary"]} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}

    /* Main container block */
    .main .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1350px !important;
    }}

    /* Headings */
    h1, h2, h3, h4, h5, h6 {{
        color: {c["text_primary"]} !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }}
    .stApp p, .stApp label {{
        color: {c["text_primary"]};
    }}
    .stApp caption, .stApp small {{
        color: {c["text_muted"]} !important;
    }}

    /* =====================================================================
       SIDEBAR STYLING
       ===================================================================== */
    section[data-testid="stSidebar"] {{
        background-color: {c["sidebar_bg"]} !important;
        border-right: 1px solid {c["sidebar_border"]} !important;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {{
        color: {c["text_primary"]} !important;
        font-weight: 700 !important;
    }}
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {{
        color: {c["text_secondary"]} !important;
    }}
    section[data-testid="stSidebar"] strong,
    section[data-testid="stSidebar"] b {{
        color: {c["text_primary"]} !important;
        font-weight: 700 !important;
    }}
    section[data-testid="stSidebar"] ul,
    section[data-testid="stSidebar"] ol,
    section[data-testid="stSidebar"] li {{
        color: {c["text_secondary"]} !important;
    }}
    section[data-testid="stSidebar"] li::marker {{
        color: {c["brand_primary"]} !important;
    }}
    section[data-testid="stSidebar"] .katex,
    section[data-testid="stSidebar"] .katex * {{
        color: {c["text_secondary"]} !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {{
        color: {c["text_secondary"]} !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] b {{
        color: {c["text_primary"]} !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: {c["card_border"]} !important;
    }}

    /* =====================================================================
       HEADER BAR & TOGGLE
       ===================================================================== */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    
    .theme-toggle-container {{
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding: 0.5rem 0;
    }}

    /* =====================================================================
       CARD CONTAINERS & DETAIL PANELS
       ===================================================================== */
    .dashboard-card, .kpi-card {{
        background-color: {c["card_bg"]} !important;
        border: 1px solid {c["card_border"]} !important;
        border-radius: 10px !important;
        padding: 1.25rem 1.5rem !important;
        margin-bottom: 1.25rem !important;
        box-shadow: {c["card_shadow"]} !important;
    }}

    .card-header {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {c["brand_primary"]} !important;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .sub-card {{
        background-color: {c["table_row_alt"]} !important;
        border: 1px solid {c["card_border"]} !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin-top: 0.75rem !important;
    }}

    /* =====================================================================
       STREAMLIT METRICS
       ===================================================================== */
    [data-testid="stMetric"] {{
        background-color: {c["card_bg"]} !important;
        border: 1px solid {c["card_border"]} !important;
        border-radius: 8px !important;
        padding: 0.85rem 1rem !important;
        box-shadow: {c["card_shadow"]} !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {c["metric_val"]} !important;
        font-size: 1.75rem !important;
        font-weight: 800 !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {c["text_muted"]} !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }}

    /* =====================================================================
       BUTTONS & CONTROLS
       ===================================================================== */
    .stButton > button {{
        background-color: {c["btn_primary_bg"]} !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s ease-in-out !important;
    }}
    .stButton > button,
    .stButton > button * {{
        color: #FFFFFF !important;
    }}
    .stButton > button:hover {{
        background-color: {c["btn_primary_hover"]} !important;
        transform: translateY(-1px) !important;
    }}

    /* Download Buttons */
    .stDownloadButton > button {{
        background-color: {"#107C41" if not is_dark else "#15803D"} !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s ease-in-out !important;
    }}
    .stDownloadButton > button,
    .stDownloadButton > button * {{
        color: #FFFFFF !important;
    }}
    .stDownloadButton > button:hover {{
        background-color: {"#0B5C30" if not is_dark else "#166534"} !important;
        transform: translateY(-1px) !important;
    }}

    /* =====================================================================
       FILE UPLOADER (Theme-Aware Dropzone & Instructions)
       ===================================================================== */
    [data-testid="stFileUploader"] {{
        background-color: transparent !important;
    }}
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploadDropzone"],
    section[data-testid="stFileUploadDropzone"],
    [data-testid="stFileUploader"] > section {{
        background-color: {"#FFFFFF" if not is_dark else "#1E293B"} !important;
        border: 2px dashed {"#CBD5E1" if not is_dark else "#475569"} !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
    }}
    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stFileUploadDropzone"] * {{
        color: {"#0F172A" if not is_dark else "#F8FAFC"} !important;
    }}
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploaderDropzoneInstructions"] small {{
        color: {"#64748B" if not is_dark else "#94A3B8"} !important;
    }}
    [data-testid="stFileUploader"] button {{
        background-color: {"#F1F5F9" if not is_dark else "#334155"} !important;
        border: 1px solid {"#CBD5E1" if not is_dark else "#475569"} !important;
        border-radius: 6px !important;
    }}
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploader"] button * {{
        color: {"#0F172A" if not is_dark else "#F8FAFC"} !important;
        font-weight: 600 !important;
    }}

    /* =====================================================================
       INPUTS, SELECTBOXES & RADIOS
       ===================================================================== */
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background-color: {c["input_bg"]} !important;
        color: {c["input_text"]} !important;
        border-color: {c["input_border"]} !important;
    }}
    [data-testid="stSelectbox"] div[data-baseweb="select"] * {{
        color: {c["input_text"]} !important;
    }}
    [data-testid="stSelectbox"] svg {{
        fill: {c["text_secondary"]} !important;
    }}

    /* =====================================================================
       TABS STYLING
       ===================================================================== */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {c["card_bg"]} !important;
        border-radius: 8px !important;
        padding: 0.35rem !important;
        border: 1px solid {c["card_border"]} !important;
        gap: 0.5rem !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        border: none !important;
    }}
    .stTabs [aria-selected="true"],
    .stTabs [aria-selected="true"] * {{
        background-color: {c["brand_primary"]} !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}
    .stTabs [aria-selected="false"] {{
        background-color: transparent !important;
    }}
    .stTabs [aria-selected="false"],
    .stTabs [aria-selected="false"] * {{
        color: {c["text_secondary"]} !important;
        font-weight: 600 !important;
    }}
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {{
        background-color: transparent !important;
        display: none !important;
    }}

    /* =====================================================================
       ALERTS & NOTICES (Ethical Safeguards & Disclaimers)
       ===================================================================== */
    [data-testid="stAlert"],
    [data-testid="stAlert"] > div,
    [data-testid="stAlert"] [role="alert"],
    section[data-testid="stSidebar"] [data-testid="stAlert"],
    section[data-testid="stSidebar"] [data-testid="stAlert"] > div,
    section[data-testid="stSidebar"] [data-testid="stAlert"] [role="alert"] {{
        background-color: {"#EFF6FF" if not is_dark else "#1E293B"} !important;
        border: 1px solid {"#BFDBFE" if not is_dark else "#3B82F6"} !important;
        border-radius: 8px !important;
    }}
    [data-testid="stAlert"] *,
    section[data-testid="stSidebar"] [data-testid="stAlert"] * {{
        color: {"#1E3A8A" if not is_dark else "#93C5FD"} !important;
    }}

    /* =====================================================================
       EXPANDERS (Global & Sidebar)
       ===================================================================== */
    [data-testid="stExpander"] {{
        background-color: {c["card_bg"]} !important;
        border: 1px solid {c["card_border"]} !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }}
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details summary {{
        background-color: {"#FFFFFF" if not is_dark else "#1E293B"} !important;
        color: {c["text_primary"]} !important;
        border-radius: 7px !important;
    }}
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] details summary:hover {{
        background-color: {"#F1F5F9" if not is_dark else "#334155"} !important;
        color: {c["text_primary"]} !important;
    }}
    [data-testid="stExpander"] summary svg {{
        fill: {c["text_primary"]} !important;
        color: {c["text_primary"]} !important;
    }}
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {{
        color: {c["text_primary"]} !important;
        font-weight: 600 !important;
    }}
    [data-testid="stExpander"] [data-testid="stExpanderDetails"],
    [data-testid="stExpander"] details > div:last-child {{
        background-color: {c["card_bg"]} !important;
        border-top: 1px solid {c["card_border"]} !important;
    }}
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] ul,
    [data-testid="stExpander"] ol,
    [data-testid="stExpander"] li,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] p,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] span,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] ul,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] ol,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] li {{
        color: {c["text_secondary"]} !important;
    }}
    [data-testid="stExpander"] strong,
    [data-testid="stExpander"] b,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] strong,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] b {{
        color: {c["text_primary"]} !important;
        font-weight: 700 !important;
    }}
    [data-testid="stExpander"] li::marker {{
        color: {c["brand_primary"]} !important;
    }}
    .katex, .katex * {{
        color: {c["text_primary"]} !important;
    }}

    /* =====================================================================
       REVIEW CATEGORY BADGES
       ===================================================================== */
    .badge-high {{
        background-color: {c["tag_high_bg"]};
        color: {c["tag_high_text"]};
        padding: 0.25rem 0.65rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
    }}
    .badge-mod {{
        background-color: {c["tag_mod_bg"]};
        color: {c["tag_mod_text"]};
        padding: 0.25rem 0.65rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
    }}
    .badge-low {{
        background-color: {c["tag_low_bg"]};
        color: {c["tag_low_text"]};
        padding: 0.25rem 0.65rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
    }}

    /* Skill tags */
    .skill-tag-matched {{
        background-color: {"#DCFCE7" if not is_dark else "#064E3B"};
        color: {"#166534" if not is_dark else "#6EE7B7"};
        padding: 0.25rem 0.65rem;
        border-radius: 16px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.2rem;
        border: 1px solid {"#BBF7D0" if not is_dark else "#047857"};
    }}
    .skill-tag-missing {{
        background-color: {"#FEE2E2" if not is_dark else "#7F1D1D"};
        color: {"#991B1B" if not is_dark else "#FCA5A5"};
        padding: 0.25rem 0.65rem;
        border-radius: 16px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.2rem;
        border: 1px solid {"#FECACA" if not is_dark else "#991B1B"};
    }}
    .skill-tag-pref {{
        background-color: {"#E0F2FE" if not is_dark else "#0C4A6E"};
        color: {"#0369A1" if not is_dark else "#7DD3FC"};
        padding: 0.25rem 0.65rem;
        border-radius: 16px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.2rem;
        border: 1px solid {"#BAE6FD" if not is_dark else "#0284C7"};
    }}

    /* =====================================================================
       CANDIDATE RANKING TABLE (Theme-Aware HTML Table)
       ===================================================================== */
    .candidate-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 0;
    }}
    .candidate-table th {{
        background-color: {c["table_header_bg"]} !important;
        color: {c["table_header_text"]} !important;
        padding: 0.75rem 1rem;
        text-align: left;
        font-weight: 700;
        font-size: 0.9rem;
        border-bottom: 2px solid {c["card_border"]};
    }}
    .candidate-table td {{
        padding: 0.75rem 1rem;
        border-bottom: 1px solid {c["card_border"]};
        color: {c["text_primary"]};
        font-size: 0.9rem;
    }}
    .candidate-table tr:nth-child(even) td {{
        background-color: {c["table_row_alt"]};
    }}
    .candidate-table tr:nth-child(odd) td {{
        background-color: {c["card_bg"]};
    }}
    .candidate-table tr:hover td {{
        background-color: {"#E2E8F0" if not is_dark else "#334155"} !important;
    }}

    /* Fallback Streamlit native table */
    [data-testid="stTable"] table {{
        background-color: {c["card_bg"]} !important;
        color: {c["text_primary"]} !important;
        border: 1px solid {c["card_border"]} !important;
    }}
    [data-testid="stTable"] th {{
        background-color: {c["table_header_bg"]} !important;
        color: {c["table_header_text"]} !important;
    }}
    [data-testid="stTable"] td {{
        color: {c["text_primary"]} !important;
        border-bottom: 1px solid {c["card_border"]} !important;
    }}

    /* Code & pre blocks */
    pre, code {{
        background-color: {c["table_row_alt"]} !important;
        color: {c["text_primary"]} !important;
        border: 1px solid {c["card_border"]} !important;
        border-radius: 6px !important;
    }}
    </style>
    """


def render_metric_card_html(label: str, value: str, theme: str = "light", delta: str = None) -> str:
    """Generate HTML snippet for a KPI metric card."""
    c = get_theme_colors(theme)
    delta_html = f'<div style="font-size: 0.8rem; color: {c["text_muted"]}; margin-top: 0.25rem;">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card" style="background-color: {c['card_bg']}; border: 1px solid {c['card_border']}; border-radius: 8px; padding: 1rem; box-shadow: {c['card_shadow']}; margin-bottom: 0.75rem;">
        <div style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: {c['text_muted']}; letter-spacing: 0.04em;">{label}</div>
        <div style="font-size: 1.8rem; font-weight: 800; color: {c['metric_val']}; line-height: 1.2; margin-top: 0.25rem;">{value}</div>
        {delta_html}
    </div>
    """


def render_category_badge_html(category: str) -> str:
    """Generate HTML snippet for a candidate review category badge."""
    normalized = category.strip().lower() if category else ""
    if "high" in normalized:
        return f'<span class="badge-high">High Match</span>'
    elif "moderate" in normalized:
        return f'<span class="badge-mod">Moderate Match</span>'
    else:
        return f'<span class="badge-low">Low Match</span>'


def render_skill_badge_html(skill: str, is_matched: bool = True, is_preferred: bool = False) -> str:
    """Generate HTML snippet for a skill badge indicating detection status."""
    if is_preferred:
        return f'<span class="skill-tag-pref badge-skill-pref">★ {skill}</span>'
    elif is_matched:
        return f'<span class="skill-tag-matched badge-skill-matched">✓ {skill}</span>'
    else:
        return f'<span class="skill-tag-missing badge-skill-missing">✗ {skill}</span>'


def render_candidate_ranking_table_html(ranked_candidates: list, theme: str = "dark") -> str:
    """
    Generate accessible, responsive, theme-aware HTML table for candidate rankings.
    Preserves full visual contrast, zebra striping, and colored review category badges
    in both Light Mode and Dark Mode without canvas rendering artifacts.
    """
    c = get_theme_colors(theme)
    rows_html = []
    for cand in ranked_candidates:
        rank = cand.get("rank", 0)
        cid = cand.get("candidate_id", "")
        score = float(cand.get("composite_score", 0.0))
        req_cov = float(cand.get("required_coverage", 0.0))
        pref_cov = float(cand.get("preferred_coverage", 0.0))
        sim = float(cand.get("cosine_similarity", 0.0))
        cat = cand.get("review_category", "Low Match")

        cat_badge = render_category_badge_html(cat)
        req_count = cand.get("required_skills", {}).get("matched_count", int(round(req_cov * 6)))
        pref_count = cand.get("preferred_skills", {}).get("matched_count", int(round(pref_cov * 6)))

        row = (
            f"<tr>"
            f"<td style=\"text-align: center; font-weight: 700; width: 6%;\">{rank}</td>"
            f"<td style=\"font-weight: 600; width: 14%;\"><span style=\"font-family: monospace; font-size: 0.95rem;\">{cid}</span></td>"
            f"<td style=\"font-weight: 800; color: {c['brand_primary']}; width: 14%;\">{score:.2f}</td>"
            f"<td style=\"width: 18%;\">{req_cov*100:.1f}% <span style=\"font-size: 0.8rem; color: {c['text_muted']};\">({req_count}/6)</span></td>"
            f"<td style=\"width: 18%;\">{pref_cov*100:.1f}% <span style=\"font-size: 0.8rem; color: {c['text_muted']};\">({pref_count}/6)</span></td>"
            f"<td style=\"width: 14%; font-family: monospace;\">{sim:.4f}</td>"
            f"<td style=\"width: 16%;\">{cat_badge}</td>"
            f"</tr>"
        )
        rows_html.append(row)

    tbody = "".join(rows_html)
    return (
        f"<div style=\"overflow-x: auto; margin: 1rem 0; border: 1px solid {c['card_border']}; border-radius: 8px;\">"
        f"<table class=\"candidate-table\" style=\"margin: 0; width: 100%; border-collapse: collapse;\">"
        f"<thead><tr>"
        f"<th style=\"text-align: center; width: 6%;\">Rank</th>"
        f"<th style=\"width: 14%;\">Candidate ID</th>"
        f"<th style=\"width: 14%;\">Composite Score</th>"
        f"<th style=\"width: 18%;\">Required Coverage (70%)</th>"
        f"<th style=\"width: 18%;\">Preferred Coverage (10%)</th>"
        f"<th style=\"width: 14%;\">TF-IDF Cosine Sim (20%)</th>"
        f"<th style=\"width: 16%;\">Review Category</th>"
        f"</tr></thead>"
        f"<tbody>{tbody}</tbody>"
        f"</table>"
        f"</div>"
    )


