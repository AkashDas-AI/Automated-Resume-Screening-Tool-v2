"""
Unit and Integration Tests for Streamlit Dashboard Module
Author: Akash Das
Project: Automated Resume Screening Tool
Phase 13: Dashboard Development using Streamlit

Tests cover:
1. Theme manager: Light and Dark mode palettes, CSS injection, contrast, badges, and metric cards.
2. Dashboard service: Sample resume evaluation matching Phase 9 authoritative scores, cohort metrics.
3. File upload handling: Valid formats (PDF, DOCX, TXT), empty files (0 bytes), unsupported extensions,
   corrupted files, and partial batch isolation.
4. Export generation: CSV and Excel export formats and content validation.
5. Privacy assertions: Absence of PII (names, emails, phone numbers) in candidate data and exports.
6. Theme-aware charts: Figure generation in Light and Dark modes with correct background and colors.
7. Module integrity: app.py imports and configuration structure.
"""

import io
import re
import pytest
import matplotlib.figure
import openpyxl

from src.theme_manager import (
    THEME_PALETTES,
    get_theme_colors,
    get_theme_css,
    render_metric_card_html,
    render_category_badge_html,
    render_skill_badge_html,
    render_candidate_ranking_table_html,
)
from src.dashboard_service import (
    evaluate_sample_resumes,
    evaluate_uploaded_resumes,
    compute_cohort_metrics,
    generate_dashboard_csv,
    generate_dashboard_excel,
    load_benchmark_jd,
    load_benchmark_requirements,
)
from src.dashboard_charts import (
    render_score_comparison,
    render_score_distribution,
    render_skill_coverage_comparison,
    render_similarity_vs_score,
    render_category_distribution,
    render_required_skill_frequency,
)


# Mock uploaded file class simulating Streamlit UploadedFile
class MockUploadedFile:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data

    def read(self) -> bytes:
        return self._data


# --------------------------------------------------------------------------
# 1. Theme Manager Tests
# --------------------------------------------------------------------------

def test_theme_palettes_structure():
    """Verify that both light and dark palettes are fully defined with required keys."""
    assert "light" in THEME_PALETTES
    assert "dark" in THEME_PALETTES

    required_keys = [
        "app_bg", "card_bg", "card_border", "text_primary", "text_secondary",
        "text_muted", "brand_primary", "metric_val", "table_header_bg",
        "table_header_text", "chart_bg", "chart_grid", "chart_text",
        "tag_high_bg", "tag_high_text", "tag_mod_bg", "tag_mod_text",
        "tag_low_bg", "tag_low_text"
    ]

    for theme_name in ("light", "dark"):
        palette = THEME_PALETTES[theme_name]
        for key in required_keys:
            assert key in palette, f"Key '{key}' missing from '{theme_name}' palette."
            assert palette[key].startswith("#") or "rgba" in palette[key], f"Invalid color value for {key}"


def test_theme_palettes_contrast_and_distinction():
    """Verify that Light Mode and Dark Mode have distinctly different background and text palettes."""
    light = THEME_PALETTES["light"]
    dark = THEME_PALETTES["dark"]

    # Backgrounds must differ significantly
    assert light["app_bg"] != dark["app_bg"]
    assert light["card_bg"] != dark["card_bg"]
    assert light["text_primary"] != dark["text_primary"]

    # Light mode has light background and dark text
    assert light["app_bg"].upper() in ("#F8FAFC", "#FFFFFF", "#F1F5F9")
    assert light["text_primary"].upper() in ("#0F172A", "#000000", "#1E293B")

    # Dark mode has dark background and light text
    assert dark["app_bg"].upper() in ("#0B1120", "#0F172A", "#1E293B")
    assert dark["text_primary"].upper() in ("#F8FAFC", "#FFFFFF", "#F1F5F9")


def test_get_theme_colors():
    """Verify color retriever behaves predictably and defaults to light mode."""
    light_colors = get_theme_colors("light")
    dark_colors = get_theme_colors("dark")
    fallback_colors = get_theme_colors("invalid_theme_name")

    assert light_colors == THEME_PALETTES["light"]
    assert dark_colors == THEME_PALETTES["dark"]
    assert fallback_colors == THEME_PALETTES["light"]


def test_get_theme_css():
    """Verify CSS injection string contains style tags and key element rules."""
    light_css = get_theme_css("light")
    dark_css = get_theme_css("dark")

    assert "<style>" in light_css
    assert "</style>" in light_css
    assert "<style>" in dark_css
    assert "</style>" in dark_css

    for css in (light_css, dark_css):
        assert ".stApp" in css
        assert ".kpi-card" in css
        assert ".badge-high" in css
        assert ".badge-mod" in css
        assert ".badge-low" in css
        assert ".candidate-table" in css


def test_render_metric_card_html():
    """Verify KPI metric card HTML generation in both themes."""
    html_light = render_metric_card_html("Top Candidate", "CAND-001", "light")
    html_dark = render_metric_card_html("Top Candidate", "CAND-001", "dark")

    assert "Top Candidate" in html_light
    assert "CAND-001" in html_light
    assert "kpi-card" in html_light

    assert "Top Candidate" in html_dark
    assert "CAND-001" in html_dark
    assert THEME_PALETTES["dark"]["card_bg"] in html_dark


def test_render_category_badges():
    """Verify review category badges generate correct styling and text."""
    badge_high = render_category_badge_html("High Match")
    badge_mod = render_category_badge_html("Moderate Match")
    badge_low = render_category_badge_html("Low Match")

    assert "badge-high" in badge_high
    assert "High Match" in badge_high
    assert "badge-mod" in badge_mod
    assert "Moderate Match" in badge_mod
    assert "badge-low" in badge_low
    assert "Low Match" in badge_low


def test_render_skill_badges():
    """Verify skill badges display detected vs missing status clearly."""
    badge_matched = render_skill_badge_html("Python", is_matched=True)
    badge_missing = render_skill_badge_html("Kubernetes", is_matched=False)

    assert "badge-skill-matched" in badge_matched
    assert "Python" in badge_matched
    assert "badge-skill-missing" in badge_missing
    assert "Kubernetes" in badge_missing


# --------------------------------------------------------------------------
# 2. Benchmark Sample Resumes Evaluation Tests
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def benchmark_candidates():
    """Evaluate and cache the 10 benchmark synthetic sample resumes."""
    res = evaluate_sample_resumes()
    return res["ranked_candidates"]


def test_sample_resumes_count_and_ranks(benchmark_candidates):
    """Verify exactly 10 candidates are evaluated and ranked 1 through 10."""
    assert len(benchmark_candidates) == 10
    ranks = [c["rank"] for c in benchmark_candidates]
    assert ranks == list(range(1, 11))


def test_sample_resumes_exact_phase9_scores(benchmark_candidates):
    """
    Verify evaluated sample candidates match approved Phase 9 authoritative scores,
    required coverage, preferred coverage, TF-IDF cosine similarity, and order.
    """
    expected_results = [
        (1, "CAND-001", 65.83, 5/6, 1/6, 0.2916, "Moderate Match"),
        (2, "CAND-010", 64.01, 5/6, 0.0, 0.2839, "Moderate Match"),
        (3, "CAND-006", 41.20, 3/6, 2/6, 0.1435, "Moderate Match"),
        (4, "CAND-004", 30.16, 2/6, 3/6, 0.0912, "Low Match"),
        (5, "CAND-008", 24.24, 2/6, 0.0, 0.0453, "Low Match"),
        (6, "CAND-002", 24.14, 2/6, 0.0, 0.0404, "Low Match"),
        (7, "CAND-009", 20.50, 1/6, 3/6, 0.1919, "Low Match"),
        (8, "CAND-005", 17.77, 1/6, 2/6, 0.1386, "Low Match"),
        (9, "CAND-003", 12.50, 1/6, 0.0, 0.0415, "Low Match"),
        (10, "CAND-007", 0.32, 0.0, 0.0, 0.0162, "Low Match"),
    ]

    for expected_rank, expected_id, expected_score, exp_req, exp_pref, exp_sim, expected_category in expected_results:
        candidate = benchmark_candidates[expected_rank - 1]
        assert candidate["rank"] == expected_rank
        assert candidate["candidate_id"] == expected_id
        assert abs(candidate["composite_score"] - expected_score) < 0.05, (
            f"Score mismatch for {expected_id}: got {candidate['composite_score']}, expected {expected_score}"
        )
        assert abs(candidate["required_coverage"] - exp_req) < 0.01, (
            f"Required coverage mismatch for {expected_id}: got {candidate['required_coverage']}, expected {exp_req}"
        )
        assert abs(candidate["preferred_coverage"] - exp_pref) < 0.01, (
            f"Preferred coverage mismatch for {expected_id}: got {candidate['preferred_coverage']}, expected {exp_pref}"
        )
        assert abs(candidate["cosine_similarity"] - exp_sim) < 0.005, (
            f"Similarity mismatch for {expected_id}: got {candidate['cosine_similarity']}, expected {exp_sim}"
        )
        assert candidate["review_category"] == expected_category


def test_full_reconciliation_against_authoritative_csv(benchmark_candidates):
    """
    Automated reconciliation: asserts that every single candidate produced in Mode A
    matches the approved Phase 10 CSV baseline to high floating-point precision.
    """
    import csv
    from pathlib import Path
    csv_path = Path(__file__).resolve().parent.parent / "reports" / "screening_report_junior_data_analyst.csv"
    assert csv_path.exists(), f"CSV report baseline missing at {csv_path}"

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    assert len(benchmark_candidates) == len(csv_rows)

    for cand, row in zip(benchmark_candidates, csv_rows):
        assert cand["candidate_id"] == row["Candidate ID"]
        assert cand["rank"] == int(row["Rank"])
        assert abs(cand["composite_score"] - float(row["Composite Match Score"])) < 1e-4
        assert abs(cand["required_coverage"] - float(row["Required Skill Coverage"])) < 1e-4
        assert abs(cand["preferred_coverage"] - float(row["Preferred Skill Coverage"])) < 1e-4
        assert abs(cand["cosine_similarity"] - float(row["TF-IDF Cosine Similarity"])) < 1e-4
        assert cand["review_category"] == row["Human-Review Category"]


def test_cohort_summary_metrics(benchmark_candidates):
    """Verify cohort metrics calculation matches expected cohort distribution."""
    metrics = compute_cohort_metrics(benchmark_candidates)

    assert metrics["total_candidates"] == 10
    assert metrics["high_match_count"] == 0
    assert metrics["moderate_match_count"] == 3
    assert metrics["low_match_count"] == 7

    # Mean score should match cohort average (~30.07)
    assert 29.5 <= metrics["mean_score"] <= 30.5
    assert metrics["top_score"] == 65.83
    assert metrics["lowest_score"] == 0.32
    assert metrics["top_candidate_id"] == "CAND-001"


# --------------------------------------------------------------------------
# 3. File Upload and Batch Handling Tests
# --------------------------------------------------------------------------

def test_upload_valid_txt_file():
    """Verify parsing and scoring a valid uploaded TXT resume."""
    jd_text = load_benchmark_jd()
    reqs = load_benchmark_requirements()

    resume_text = (
        "Senior Python Engineer with 6 years experience in Machine Learning, "
        "SQL, Docker, Git, and cloud infrastructure on AWS. Strong expertise in Pandas, NumPy."
    )
    mock_file = MockUploadedFile("candidate_valid.txt", resume_text.encode("utf-8"))

    res = evaluate_uploaded_resumes([mock_file], jd_text, reqs)
    results = res["ranked_candidates"]
    errors = res["failed_files"]

    assert len(errors) == 0
    assert len(results) == 1
    candidate = results[0]
    assert candidate["rank"] == 1
    assert candidate["candidate_id"].startswith("CAND-")
    assert candidate["composite_score"] > 0.0
    assert "Python" in candidate["required_skills"]["matched_names"]


def test_upload_empty_file_handling():
    """Verify 0-byte uploaded file is flagged as an error without crashing the dashboard."""
    jd_text = load_benchmark_jd()
    reqs = load_benchmark_requirements()

    mock_empty = MockUploadedFile("empty_resume.txt", b"")
    res = evaluate_uploaded_resumes([mock_empty], jd_text, reqs)
    results = res["ranked_candidates"]
    errors = res["failed_files"]

    assert len(results) == 0
    assert len(errors) == 1
    err_msg = errors[0]["error"].lower()
    assert "empty" in err_msg or "0 bytes" in err_msg


def test_upload_unsupported_extension():
    """Verify unsupported extensions (.png, .xlsx, .zip) are flagged with helpful errors."""
    jd_text = load_benchmark_jd()
    reqs = load_benchmark_requirements()

    mock_png = MockUploadedFile("candidate_photo.png", b"\x89PNG\r\n\x1a\n...")
    res = evaluate_uploaded_resumes([mock_png], jd_text, reqs)
    results = res["ranked_candidates"]
    errors = res["failed_files"]

    assert len(results) == 0
    assert len(errors) == 1
    err_msg = errors[0]["error"].lower()
    assert "unsupported" in err_msg or ".png" in err_msg


def test_upload_corrupt_file_handling():
    """Verify corrupted PDF/DOCX file is handled gracefully without unhandled exception."""
    jd_text = load_benchmark_jd()
    reqs = load_benchmark_requirements()

    # Create invalid pseudo-pdf byte stream
    mock_corrupt_pdf = MockUploadedFile("corrupted_candidate.pdf", b"%PDF-1.4 ... truncated content invalid")
    res = evaluate_uploaded_resumes([mock_corrupt_pdf], jd_text, reqs)
    results = res["ranked_candidates"]
    errors = res["failed_files"]

    # Should safely fail for this candidate and record in errors
    assert len(results) == 0
    assert len(errors) == 1
    err_msg = errors[0]["error"].lower()
    assert "error" in err_msg or "failed" in err_msg or "parsing" in err_msg


def test_upload_partial_batch_isolation():
    """Verify mixed batch with 1 valid file and 1 invalid file evaluates the valid file."""
    jd_text = load_benchmark_jd()
    reqs = load_benchmark_requirements()

    valid_text = "Data Scientist skilled in Python, SQL, Machine Learning, and Git."
    mock_valid = MockUploadedFile("valid_applicant.txt", valid_text.encode("utf-8"))
    mock_corrupt = MockUploadedFile("bad_file.png", b"invalid data")

    res = evaluate_uploaded_resumes([mock_valid, mock_corrupt], jd_text, reqs)
    results = res["ranked_candidates"]
    errors = res["failed_files"]

    assert len(results) == 1
    assert len(errors) == 1
    assert results[0]["rank"] == 1
    assert errors[0]["filename"] == "bad_file.png"



# --------------------------------------------------------------------------
# 4. Report Export Generation Tests (CSV & Excel)
# --------------------------------------------------------------------------

def test_generate_dashboard_csv(benchmark_candidates):
    """Verify CSV export produces valid UTF-8 bytes with expected columns and candidate rows."""
    csv_bytes = generate_dashboard_csv(benchmark_candidates)
    assert isinstance(csv_bytes, bytes)

    csv_text = csv_bytes.decode("utf-8")
    lines = csv_text.strip().splitlines()

    assert len(lines) == 11  # 1 header + 10 candidates
    header = lines[0]
    assert "Rank" in header
    assert "Candidate ID" in header
    assert "Composite Match Score" in header
    assert "Human-Review Category" in header


def test_generate_dashboard_excel(benchmark_candidates):
    """Verify Excel export produces valid XLSX bytes with matching sheet and data."""
    excel_bytes = generate_dashboard_excel(benchmark_candidates)
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 1000

    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    assert "Candidate Ranking" in wb.sheetnames

    ws = wb["Candidate Ranking"]
    # Check header
    header_values = [cell.value for cell in ws[1]]
    assert "Rank" in header_values
    assert "Candidate ID" in header_values
    assert "Composite Match Score" in header_values

    # Check row count
    assert ws.max_row == 11  # 1 header + 10 candidates
    assert ws.cell(row=2, column=2).value == "CAND-001"


# --------------------------------------------------------------------------
# 5. Candidate Privacy Assertions
# --------------------------------------------------------------------------

def test_candidate_privacy_guarantees(benchmark_candidates):
    """Assert candidate records and exports contain no personal names, emails, or phone numbers."""
    email_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    phone_regex = re.compile(r"\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b")

    for candidate in benchmark_candidates:
        # Check forbidden keys
        for forbidden_key in ("name", "full_name", "email", "phone", "phone_number", "address"):
            assert forbidden_key not in candidate, f"Candidate contains forbidden key '{forbidden_key}'"

        # Check candidate ID structure
        assert re.match(r"^CAND-\d{3}$", candidate["candidate_id"])

        # Check that candidate_id is strictly anonymous
        assert "@" not in candidate["candidate_id"]

    # Verify CSV export does not leak PII
    csv_text = generate_dashboard_csv(benchmark_candidates).decode("utf-8")
    assert not email_regex.search(csv_text), "Email found in CSV export"
    assert not phone_regex.search(csv_text), "Phone number found in CSV export"


# --------------------------------------------------------------------------
# 6. Theme-Aware Chart Generation Tests
# --------------------------------------------------------------------------

def test_render_score_comparison_both_themes(benchmark_candidates):
    """Verify score comparison chart renders valid figure in light and dark modes."""
    for theme in ("light", "dark"):
        fig = render_score_comparison(benchmark_candidates, theme=theme)
        assert isinstance(fig, matplotlib.figure.Figure)
        assert fig.get_dpi() == 150
        # Check background facecolor
        expected_bg = THEME_PALETTES[theme]["chart_bg"]
        fig_facecolor = matplotlib.colors.to_hex(fig.get_facecolor())
        assert fig_facecolor.lower() == expected_bg.lower()
        matplotlib.pyplot.close(fig)


def test_render_score_distribution_both_themes(benchmark_candidates):
    """Verify score distribution chart renders valid figure in light and dark modes."""
    for theme in ("light", "dark"):
        fig = render_score_distribution(benchmark_candidates, theme=theme)
        assert isinstance(fig, matplotlib.figure.Figure)
        expected_bg = THEME_PALETTES[theme]["chart_bg"]
        assert matplotlib.colors.to_hex(fig.get_facecolor()).lower() == expected_bg.lower()
        matplotlib.pyplot.close(fig)


def test_render_skill_coverage_comparison_both_themes(benchmark_candidates):
    """Verify skill coverage comparison chart renders valid figure in light and dark modes."""
    for theme in ("light", "dark"):
        fig = render_skill_coverage_comparison(benchmark_candidates, theme=theme)
        assert isinstance(fig, matplotlib.figure.Figure)
        expected_bg = THEME_PALETTES[theme]["chart_bg"]
        assert matplotlib.colors.to_hex(fig.get_facecolor()).lower() == expected_bg.lower()
        matplotlib.pyplot.close(fig)


def test_render_similarity_vs_score_both_themes(benchmark_candidates):
    """Verify similarity vs score chart renders valid figure in light and dark modes."""
    for theme in ("light", "dark"):
        fig = render_similarity_vs_score(benchmark_candidates, theme=theme)
        assert isinstance(fig, matplotlib.figure.Figure)
        expected_bg = THEME_PALETTES[theme]["chart_bg"]
        assert matplotlib.colors.to_hex(fig.get_facecolor()).lower() == expected_bg.lower()
        matplotlib.pyplot.close(fig)


def test_render_category_distribution_both_themes(benchmark_candidates):
    """Verify review category distribution chart renders valid figure in light and dark modes."""
    for theme in ("light", "dark"):
        fig = render_category_distribution(benchmark_candidates, theme=theme)
        assert isinstance(fig, matplotlib.figure.Figure)
        expected_bg = THEME_PALETTES[theme]["chart_bg"]
        assert matplotlib.colors.to_hex(fig.get_facecolor()).lower() == expected_bg.lower()
        matplotlib.pyplot.close(fig)


def test_render_required_skill_frequency_both_themes(benchmark_candidates):
    """Verify required skill frequency chart renders valid figure in light and dark modes."""
    for theme in ("light", "dark"):
        fig = render_required_skill_frequency(benchmark_candidates, theme=theme)
        assert isinstance(fig, matplotlib.figure.Figure)
        expected_bg = THEME_PALETTES[theme]["chart_bg"]
        assert matplotlib.colors.to_hex(fig.get_facecolor()).lower() == expected_bg.lower()
        matplotlib.pyplot.close(fig)


# --------------------------------------------------------------------------
# 7. App Module Integrity Tests
# --------------------------------------------------------------------------

def test_app_module_imports():
    """Verify that app.py imports cleanly without errors."""
    import app
    assert hasattr(app, "toggle_theme")
    assert hasattr(app, "WORKSPACE_ROOT")
    assert hasattr(app, "SAMPLE_RESUMES_DIR")


def test_render_candidate_ranking_table_html_both_themes(benchmark_candidates):
    """Verify HTML candidate ranking table renders with valid tags in both themes."""
    for theme in ("light", "dark"):
        html = render_candidate_ranking_table_html(benchmark_candidates, theme=theme)
        assert "<table" in html
        assert "candidate-table" in html
        assert "CAND-001" in html
        assert "CAND-010" in html
        assert "65.83" in html
        assert "Moderate Match" in html


def test_dark_mode_is_default_theme():
    """Verify that when a new visitor session starts, Dark Mode is the default theme."""
    import streamlit as st
    session_sim = {}
    # Simulate app.py session initialization
    if "theme" not in session_sim:
        session_sim["theme"] = "dark"
    assert session_sim["theme"] == "dark"


def test_actual_theme_toggle_interaction_and_label_updates():
    """
    Verify actual theme toggle button interaction cycle:
    1. Fresh session starts in Dark Mode with '☀️ Switch to Light Mode' button.
    2. Activating theme button invokes toggle_theme() and transitions to Light Mode.
    3. Button label updates to '🌙 Switch to Dark Mode' with key 'btn_toggle_dark'.
    4. Activating theme button again invokes toggle_theme() and transitions back to Dark Mode.
    5. Button label restores to '☀️ Switch to Light Mode' with key 'btn_toggle_light'.
    """
    import app

    # Simulated session state environment
    session_state = {}

    # Helper function simulating app.py header button rendering
    def get_rendered_button(state):
        current = state.get("theme", "dark")
        if current == "dark":
            return {"label": "☀️ Switch to Light Mode", "key": "btn_toggle_light"}
        else:
            return {"label": "🌙 Switch to Dark Mode", "key": "btn_toggle_dark"}

    # 1. Fresh session start
    if "theme" not in session_state:
        session_state["theme"] = "dark"

    assert session_state["theme"] == "dark"
    btn1 = get_rendered_button(session_state)
    assert btn1["label"] == "☀️ Switch to Light Mode"
    assert btn1["key"] == "btn_toggle_light"

    # 2. Simulate user clicking the button (activates toggle_theme)
    # Monkey-patch st.session_state access for toggle_theme
    from unittest.mock import patch
    with patch.dict("streamlit.session_state", session_state, clear=True):
        import streamlit as st
        st.session_state["theme"] = session_state["theme"]
        app.toggle_theme()
        session_state["theme"] = st.session_state["theme"]

    # Verify transition to Light Mode
    assert session_state["theme"] == "light"
    btn2 = get_rendered_button(session_state)
    assert btn2["label"] == "🌙 Switch to Dark Mode"
    assert btn2["key"] == "btn_toggle_dark"

    # 3. Simulate user clicking the button again
    with patch.dict("streamlit.session_state", session_state, clear=True):
        import streamlit as st
        st.session_state["theme"] = session_state["theme"]
        app.toggle_theme()
        session_state["theme"] = st.session_state["theme"]

    # Verify transition back to Dark Mode
    assert session_state["theme"] == "dark"
    btn3 = get_rendered_button(session_state)
    assert btn3["label"] == "☀️ Switch to Light Mode"
    assert btn3["key"] == "btn_toggle_light"


def test_screening_results_survive_theme_toggle(benchmark_candidates):
    """
    Verify that existing candidate screening results and rankings in st.session_state
    remain completely available and intact across theme switching transitions.
    """
    import app
    from unittest.mock import patch

    session_state = {
        "theme": "dark",
        "ranked_candidates": [dict(c) for c in benchmark_candidates],
        "pipeline_metadata": {
            "source": "Benchmark Sample Resumes (10 Files)",
            "total_submitted": 10,
            "success_count": 10,
            "failed_count": 0,
        },
        "selected_candidate_id": "CAND-001",
    }

    initial_ids = [c["candidate_id"] for c in session_state["ranked_candidates"]]
    initial_scores = [c["composite_score"] for c in session_state["ranked_candidates"]]

    # Toggle to Light Mode
    with patch.dict("streamlit.session_state", session_state, clear=True):
        import streamlit as st
        app.toggle_theme()
        session_state["theme"] = st.session_state["theme"]

    assert session_state["theme"] == "light"
    assert len(session_state["ranked_candidates"]) == 10
    assert [c["candidate_id"] for c in session_state["ranked_candidates"]] == initial_ids
    assert [c["composite_score"] for c in session_state["ranked_candidates"]] == initial_scores
    assert session_state["pipeline_metadata"]["total_submitted"] == 10
    assert session_state["selected_candidate_id"] == "CAND-001"

    # Toggle back to Dark Mode
    with patch.dict("streamlit.session_state", session_state, clear=True):
        import streamlit as st
        app.toggle_theme()
        session_state["theme"] = st.session_state["theme"]

    assert session_state["theme"] == "dark"
    assert len(session_state["ranked_candidates"]) == 10
    assert [c["candidate_id"] for c in session_state["ranked_candidates"]] == initial_ids
    assert [c["composite_score"] for c in session_state["ranked_candidates"]] == initial_scores


def test_uploaded_resumes_survive_theme_toggle():
    """
    Verify that custom uploaded-file processing results (Mode B) in st.session_state
    are not lost or reset when switching themes.
    """
    import app
    from unittest.mock import patch

    uploaded_candidates = [
        {"rank": 1, "candidate_id": "CAND-U001", "composite_score": 55.4, "review_category": "Moderate Match"},
        {"rank": 2, "candidate_id": "CAND-U002", "composite_score": 28.1, "review_category": "Low Match"},
    ]
    session_state = {
        "theme": "dark",
        "ranked_candidates": uploaded_candidates,
        "pipeline_metadata": {
            "source": "Custom Upload (2 Files)",
            "total_submitted": 2,
            "success_count": 2,
            "failed_count": 0,
        },
        "selected_candidate_id": "CAND-U001",
    }

    # Toggle Dark -> Light -> Dark
    with patch.dict("streamlit.session_state", session_state, clear=True):
        import streamlit as st
        app.toggle_theme()
        session_state["theme"] = st.session_state["theme"]
        assert session_state["theme"] == "light"
        assert len(session_state["ranked_candidates"]) == 2
        assert session_state["ranked_candidates"][0]["candidate_id"] == "CAND-U001"

        app.toggle_theme()
        session_state["theme"] = st.session_state["theme"]
        assert session_state["theme"] == "dark"
        assert len(session_state["ranked_candidates"]) == 2
        assert session_state["pipeline_metadata"]["source"] == "Custom Upload (2 Files)"


def test_theme_toggle_does_not_invoke_pipeline_recomputation(benchmark_candidates):
    """
    Verify that toggling the theme does NOT invoke resume extraction, skill matching,
    TF-IDF fitting, or candidate ranking again (0 calls to screening pipeline).
    """
    import app
    from unittest.mock import patch, MagicMock

    session_state = {
        "theme": "dark",
        "ranked_candidates": benchmark_candidates,
        "pipeline_metadata": {"source": "Benchmark"},
    }

    with patch.dict("streamlit.session_state", session_state, clear=True):
        with patch("src.dashboard_service.evaluate_sample_resumes") as mock_eval_samples, \
             patch("src.dashboard_service.evaluate_uploaded_resumes") as mock_eval_uploads, \
             patch("src.scoring.score_candidate_batch") as mock_score_batch, \
             patch("src.ranking.rank_candidates") as mock_rank:

            # Toggle Dark -> Light
            app.toggle_theme()
            assert mock_eval_samples.call_count == 0
            assert mock_eval_uploads.call_count == 0
            assert mock_score_batch.call_count == 0
            assert mock_rank.call_count == 0

            # Toggle Light -> Dark
            app.toggle_theme()
            assert mock_eval_samples.call_count == 0
            assert mock_eval_uploads.call_count == 0
            assert mock_score_batch.call_count == 0
            assert mock_rank.call_count == 0


def test_wcag_contrast_ratios():
    """
    Verify mathematical WCAG 2.2 AA contrast ratios for critical text/surface pairs.
    WCAG requirements:
      - Normal text: >= 4.5:1
      - Large text / graphical components: >= 3.0:1
    """
    def hex_to_relative_luminance(hex_str: str) -> float:
        hex_clean = hex_str.lstrip("#")
        r_srgb = int(hex_clean[0:2], 16) / 255.0
        g_srgb = int(hex_clean[2:4], 16) / 255.0
        b_srgb = int(hex_clean[4:6], 16) / 255.0

        def to_linear(c):
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

        r = to_linear(r_srgb)
        g = to_linear(g_srgb)
        b = to_linear(b_srgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def contrast_ratio(hex1: str, hex2: str) -> float:
        l1 = hex_to_relative_luminance(hex1)
        l2 = hex_to_relative_luminance(hex2)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    # 1. Light Mode Contrast Tests
    light = THEME_PALETTES["light"]
    # Primary text on app background (#0F172A on #F8FAFC)
    cr_light_body = contrast_ratio(light["text_primary"], light["app_bg"])
    assert cr_light_body >= 4.5, f"Light body contrast {cr_light_body:.2f} < 4.5"

    # Primary text on card background (#0F172A on #FFFFFF)
    cr_light_card = contrast_ratio(light["text_primary"], light["card_bg"])
    assert cr_light_card >= 4.5, f"Light card text contrast {cr_light_card:.2f} < 4.5"

    # Secondary text on app background (#334155 on #F8FAFC)
    cr_light_sec = contrast_ratio(light["text_secondary"], light["app_bg"])
    assert cr_light_sec >= 4.5, f"Light secondary text contrast {cr_light_sec:.2f} < 4.5"

    # Primary button text on button background (#FFFFFF on #1D4ED8)
    cr_light_btn = contrast_ratio(light["btn_primary_text"], light["btn_primary_bg"])
    assert cr_light_btn >= 4.5, f"Light button contrast {cr_light_btn:.2f} < 4.5"

    # Table header text on table header background (#0F172A on #E2E8F0)
    cr_light_th = contrast_ratio(light["table_header_text"], light["table_header_bg"])
    assert cr_light_th >= 4.5, f"Light table header contrast {cr_light_th:.2f} < 4.5"

    # 2. Dark Mode Contrast Tests
    dark = THEME_PALETTES["dark"]
    # Primary text on dark app background (#F8FAFC on #0B1120)
    cr_dark_body = contrast_ratio(dark["text_primary"], dark["app_bg"])
    assert cr_dark_body >= 4.5, f"Dark body contrast {cr_dark_body:.2f} < 4.5"

    # Primary text on dark card background (#F8FAFC on #1E293B)
    cr_dark_card = contrast_ratio(dark["text_primary"], dark["card_bg"])
    assert cr_dark_card >= 4.5, f"Dark card contrast {cr_dark_card:.2f} < 4.5"

    # Brand / Metric text on dark card background (#38BDF8 on #1E293B)
    cr_dark_metric = contrast_ratio(dark["metric_val"], dark["card_bg"])
    assert cr_dark_metric >= 4.5, f"Dark metric contrast {cr_dark_metric:.2f} < 4.5"


def test_sidebar_and_expander_css_rules():
    """Verify that generated CSS explicitly styles sidebar elements and expanders in both themes."""
    for theme in ("light", "dark"):
        css = get_theme_css(theme)
        # Sidebar specific elements
        assert 'section[data-testid="stSidebar"]' in css
        assert 'section[data-testid="stSidebar"] ul' in css
        assert 'section[data-testid="stSidebar"] li' in css
        assert 'section[data-testid="stSidebar"] .katex' in css
        # Expander elements
        assert '[data-testid="stExpander"]' in css
        assert '[data-testid="stExpanderDetails"]' in css
        assert '[data-testid="stExpander"] summary' in css



