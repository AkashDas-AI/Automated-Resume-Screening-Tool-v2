"""
Unit Tests for Report Generator Module
Author: Akash Das
Project: Automated Resume Screening Tool

Comprehensive automated test suite validating:
- CSV file generation, expected columns, and ranking order preservation
- Excel workbook generation, 3 required sheets, formatting, filters, frozen panes
- Numeric precision preservation
- Privacy enforcement: strict exclusion of personal contact details (names, emails, phones)
- Low Match candidate inclusion (zero automated rejection)
- Edge cases: empty candidate input, malformed records, missing optional details
- Disclaimer presence and educational metadata
- Full pipeline integration across all 10 synthetic candidates
"""

import io
from pathlib import Path
import pytest
import pandas as pd
import openpyxl

from src.resume_parser import extract_text
from src.text_cleaner import clean_text
from src.skill_extractor import load_requirements
from src.scoring import score_candidate_batch
from src.ranking import rank_candidates
from src.report_generator import (
    generate_ranking_dataframe,
    generate_details_dataframe,
    export_to_csv,
    generate_csv_bytes,
    export_to_excel,
    generate_excel_bytes,
    RANKING_COLUMNS,
    DETAILS_COLUMNS,
    DEFAULT_DISCLAIMER,
)

SAMPLE_RESUMES_DIR = Path(__file__).parent.parent / "data" / "sample_resumes"
JOB_DESC_PATH = Path(__file__).parent.parent / "data" / "job_descriptions" / "junior_data_analyst.txt"
REQUIREMENTS_PATH = (
    Path(__file__).parent.parent / "data" / "job_descriptions" / "junior_data_analyst_requirements.json"
)


@pytest.fixture
def sample_ranked_candidates():
    """Synthetic ranked candidate cohort for isolated unit testing."""
    return [
        {
            "rank": 1,
            "candidate_id": "CAND-001",
            "composite_score": 65.83,
            "required_coverage": 0.8333,
            "preferred_coverage": 0.1667,
            "cosine_similarity": 0.2916,
            "review_category": "Moderate Match",
            "required_skills": {
                "coverage": 0.8333,
                "matched_names": ["Python", "SQL", "Pandas", "Data Cleaning", "Data Analysis"],
                "missing_names": ["Basic Statistics"],
            },
            "preferred_skills": {
                "coverage": 0.1667,
                "matched_names": ["NumPy"],
                "missing_names": ["Scikit-learn", "Machine Learning", "Power BI", "Tableau", "Excel"],
            },
            "similarity": {"cosine_similarity": 0.2916},
        },
        {
            "rank": 2,
            "candidate_id": "CAND-006",
            "composite_score": 41.20,
            "required_coverage": 0.5000,
            "preferred_coverage": 0.3333,
            "cosine_similarity": 0.1435,
            "review_category": "Moderate Match",
            "required_skills": {
                "coverage": 0.5000,
                "matched_names": ["Python", "Pandas", "Data Cleaning"],
                "missing_names": ["SQL", "Data Analysis", "Basic Statistics"],
            },
            "preferred_skills": {
                "coverage": 0.3333,
                "matched_names": ["NumPy", "Machine Learning"],
                "missing_names": ["Scikit-learn", "Power BI", "Tableau", "Excel"],
            },
            "similarity": {"cosine_similarity": 0.1435},
        },
        {
            "rank": 3,
            "candidate_id": "CAND-007",
            "composite_score": 0.32,
            "required_coverage": 0.0000,
            "preferred_coverage": 0.0000,
            "cosine_similarity": 0.0162,
            "review_category": "Low Match",
            "required_skills": {
                "coverage": 0.0000,
                "matched_names": [],
                "missing_names": ["Python", "SQL", "Pandas", "Data Cleaning", "Data Analysis", "Basic Statistics"],
            },
            "preferred_skills": {
                "coverage": 0.0000,
                "matched_names": [],
                "missing_names": ["NumPy", "Scikit-learn", "Machine Learning", "Power BI", "Tableau", "Excel"],
            },
            "similarity": {"cosine_similarity": 0.0162},
        },
    ]


# --------------------------------------------------------------------------
# 1. CSV Report Generation Tests
# --------------------------------------------------------------------------
def test_csv_file_generation(tmp_path, sample_ranked_candidates):
    """Verify export_to_csv writes a valid CSV file to disk and returns Path."""
    csv_file = tmp_path / "test_report.csv"
    res_path = export_to_csv(sample_ranked_candidates, output_path=csv_file)

    assert res_path == csv_file
    assert csv_file.exists()
    assert csv_file.stat().st_size > 0


def test_csv_expected_columns_and_content(sample_ranked_candidates):
    """Verify CSV contains exact required column names and rows."""
    csv_str = export_to_csv(sample_ranked_candidates)
    assert isinstance(csv_str, str)

    df = pd.read_csv(io.StringIO(csv_str))
    assert list(df.columns) == RANKING_COLUMNS
    assert len(df) == 3


def test_csv_ranking_order_preservation(sample_ranked_candidates):
    """Verify CSV preserves exact Phase 9 descending rank order."""
    csv_str = export_to_csv(sample_ranked_candidates)
    df = pd.read_csv(io.StringIO(csv_str))

    assert list(df["Rank"]) == [1, 2, 3]
    assert list(df["Candidate ID"]) == ["CAND-001", "CAND-006", "CAND-007"]
    assert list(df["Composite Match Score"]) == [65.83, 41.20, 0.32]


def test_csv_in_memory_bytes_stream(sample_ranked_candidates):
    """Verify generate_csv_bytes produces valid UTF-8 downloadable bytes."""
    data_bytes = generate_csv_bytes(sample_ranked_candidates)
    assert isinstance(data_bytes, bytes)
    assert len(data_bytes) > 0

    decoded = data_bytes.decode("utf-8")
    assert "Candidate ID" in decoded
    assert "CAND-001" in decoded


# --------------------------------------------------------------------------
# 2. Excel Report Generation Tests
# --------------------------------------------------------------------------
def test_excel_workbook_generation(tmp_path, sample_ranked_candidates):
    """Verify export_to_excel creates valid .xlsx workbook on disk."""
    xlsx_file = tmp_path / "test_report.xlsx"
    res_path = export_to_excel(sample_ranked_candidates, output_path=xlsx_file)

    assert res_path == xlsx_file
    assert xlsx_file.exists()
    assert xlsx_file.stat().st_size > 0


def test_excel_sheet_names_and_structure(tmp_path, sample_ranked_candidates):
    """Verify Excel workbook contains exactly the three specified sheets."""
    xlsx_file = tmp_path / "test_sheets.xlsx"
    export_to_excel(sample_ranked_candidates, output_path=xlsx_file)

    wb = openpyxl.load_workbook(xlsx_file)
    expected_sheets = ["Candidate Ranking", "Detailed Results", "Report Information"]
    assert wb.sheetnames == expected_sheets


def test_excel_sheet_1_ranking_order_and_columns(tmp_path, sample_ranked_candidates):
    """Verify Sheet 1 headers and row ordering match Phase 9 ranking."""
    xlsx_file = tmp_path / "test_sheet1.xlsx"
    export_to_excel(sample_ranked_candidates, output_path=xlsx_file)

    wb = openpyxl.load_workbook(xlsx_file)
    ws = wb["Candidate Ranking"]

    # Header check
    headers = [cell.value for cell in ws[1]]
    assert headers == RANKING_COLUMNS

    # Row 2 (Rank 1): CAND-001
    assert ws.cell(row=2, column=1).value == 1
    assert ws.cell(row=2, column=2).value == "CAND-001"
    assert ws.cell(row=2, column=3).value == 65.83

    # Row 3 (Rank 2): CAND-006
    assert ws.cell(row=3, column=1).value == 2
    assert ws.cell(row=3, column=2).value == "CAND-006"

    # Row 4 (Rank 3): CAND-007
    assert ws.cell(row=4, column=1).value == 3
    assert ws.cell(row=4, column=2).value == "CAND-007"


def test_excel_sheet_2_detailed_results(tmp_path, sample_ranked_candidates):
    """Verify Sheet 2 contains matched and missing skills breakdown."""
    xlsx_file = tmp_path / "test_sheet2.xlsx"
    export_to_excel(sample_ranked_candidates, output_path=xlsx_file)

    wb = openpyxl.load_workbook(xlsx_file)
    ws = wb["Detailed Results"]

    headers = [cell.value for cell in ws[1]]
    assert headers == DETAILS_COLUMNS

    # Row 2 (CAND-001) details
    assert ws.cell(row=2, column=1).value == "CAND-001"
    req_matched = ws.cell(row=2, column=2).value
    assert "Python" in req_matched
    assert "SQL" in req_matched
    req_missing = ws.cell(row=2, column=3).value
    assert "Basic Statistics" in req_missing


def test_excel_sheet_3_report_metadata_and_disclaimer(tmp_path, sample_ranked_candidates):
    """Verify Sheet 3 contains project metadata, author Akash Das, and disclaimer."""
    xlsx_file = tmp_path / "test_sheet3.xlsx"
    export_to_excel(sample_ranked_candidates, output_path=xlsx_file)

    wb = openpyxl.load_workbook(xlsx_file)
    ws = wb["Report Information"]

    content_map = {}
    for row in ws.iter_rows(values_only=True):
        if row[0]:
            content_map[str(row[0])] = str(row[1])

    assert content_map["Project Name"] == "Automated Resume Screening Tool"
    assert content_map["Author"] == "Akash Das"
    assert content_map["Benchmark Job Role"] == "Junior Data Analyst"
    assert "70% required skills" in content_map["Scoring Weights"]
    assert "educational prototype" in content_map["Notice"]


def test_excel_formatting_frozen_panes_and_filters(tmp_path, sample_ranked_candidates):
    """Verify bold headers, freeze panes, auto filters, and number formatting in Excel."""
    xlsx_file = tmp_path / "test_formatting.xlsx"
    export_to_excel(sample_ranked_candidates, output_path=xlsx_file)

    wb = openpyxl.load_workbook(xlsx_file)
    ws_ranking = wb["Candidate Ranking"]
    ws_details = wb["Detailed Results"]

    # Frozen header check
    assert ws_ranking.freeze_panes == "A2"
    assert ws_details.freeze_panes == "A2"

    # Auto-filter check
    assert ws_ranking.auto_filter.ref is not None
    assert ws_details.auto_filter.ref is not None

    # Header bold font check
    assert ws_ranking["A1"].font.bold is True
    assert ws_details["A1"].font.bold is True

    # Number formats
    assert ws_ranking.cell(row=2, column=3).number_format == "0.00"   # Composite score
    assert ws_ranking.cell(row=2, column=4).number_format == "0.0%"   # Req coverage
    assert ws_ranking.cell(row=2, column=6).number_format == "0.0000" # Cosine sim


def test_excel_in_memory_bytes_stream(sample_ranked_candidates):
    """Verify generate_excel_bytes produces valid downloadable workbook bytes."""
    data_bytes = generate_excel_bytes(sample_ranked_candidates)
    assert isinstance(data_bytes, bytes)
    assert len(data_bytes) > 0

    # Load from in-memory stream to confirm validity
    wb = openpyxl.load_workbook(io.BytesIO(data_bytes))
    assert "Candidate Ranking" in wb.sheetnames


# --------------------------------------------------------------------------
# 3. Privacy, Inclusion, and Ethical Compliance
# --------------------------------------------------------------------------
def test_privacy_no_personal_contact_details_exported(sample_ranked_candidates):
    """
    Verify report output never leaks candidate names, emails, phone numbers,
    or residential addresses.
    """
    # Inject contact details into candidate objects to verify they are excluded from export
    dirty_candidates = [dict(c) for c in sample_ranked_candidates]
    dirty_candidates[0]["name"] = "Aarav Sharma"
    dirty_candidates[0]["email"] = "aarav.sharma@example.com"
    dirty_candidates[0]["phone"] = "+91 98765 43210"
    dirty_candidates[0]["address"] = "123 Tech Street, Bangalore"

    csv_str = export_to_csv(dirty_candidates)
    excel_bytes = generate_excel_bytes(dirty_candidates)

    for private_token in ["Aarav Sharma", "aarav.sharma@example.com", "98765", "Tech Street", "Bangalore"]:
        assert private_token not in csv_str

    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    for sheetname in wb.sheetnames:
        ws = wb[sheetname]
        for row in ws.iter_rows(values_only=True):
            for cell_val in row:
                if cell_val:
                    for private_token in ["Aarav Sharma", "aarav.sharma@example.com", "98765", "Tech Street", "Bangalore"]:
                        assert private_token not in str(cell_val)


def test_low_match_candidates_retained_in_reports(sample_ranked_candidates):
    """Verify Low Match candidates are never dropped, filtered, or excluded."""
    csv_str = export_to_csv(sample_ranked_candidates)
    assert "CAND-007" in csv_str
    assert "Low Match" in csv_str

    df = pd.read_csv(io.StringIO(csv_str))
    low_match_candidates = df[df["Human-Review Category"] == "Low Match"]
    assert len(low_match_candidates) == 1
    assert low_match_candidates.iloc[0]["Candidate ID"] == "CAND-007"


# --------------------------------------------------------------------------
# 4. Input Validation and Error Handling
# --------------------------------------------------------------------------
def test_empty_candidate_input():
    """Verify empty input generates empty table with standard headers."""
    csv_str = export_to_csv([])
    df = pd.read_csv(io.StringIO(csv_str))
    assert list(df.columns) == RANKING_COLUMNS
    assert len(df) == 0

    excel_bytes = generate_excel_bytes([])
    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    assert len(wb.sheetnames) == 3


def test_invalid_input_types():
    """Verify TypeError raised for non-list inputs."""
    with pytest.raises(TypeError, match="must be a list"):
        generate_ranking_dataframe("not a list")  # type: ignore

    with pytest.raises(TypeError, match="Item at index 0 is not a dictionary"):
        generate_ranking_dataframe(["not a dict"])  # type: ignore


def test_missing_candidate_id_raises_error():
    """Verify ValueError raised if a record lacks candidate_id."""
    with pytest.raises(ValueError, match="missing a valid 'candidate_id'"):
        generate_ranking_dataframe([{"composite_score": 50.0}])


def test_missing_optional_skill_breakdown_handled_safely():
    """Verify candidates lacking required_skills dict are still safely exported."""
    minimal_candidates = [
        {
            "rank": 1,
            "candidate_id": "CAND-MINIMAL",
            "composite_score": 50.0,
            "required_coverage": 0.5,
            "preferred_coverage": 0.2,
            "cosine_similarity": 0.1,
            "review_category": "Moderate Match",
        }
    ]

    csv_str = export_to_csv(minimal_candidates)
    assert "CAND-MINIMAL" in csv_str

    excel_bytes = generate_excel_bytes(minimal_candidates)
    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    ws_details = wb["Detailed Results"]
    assert ws_details.cell(row=2, column=1).value == "CAND-MINIMAL"
    assert ws_details.cell(row=2, column=2).value == "None"


# --------------------------------------------------------------------------
# 5. Full Pipeline Integration: All 10 Real Synthetic Resumes
# --------------------------------------------------------------------------
def test_full_pipeline_report_generation(tmp_path):
    """
    Score all 10 synthetic resumes, rank them, export to CSV and Excel,
    and verify complete integrity across all candidates.
    """
    raw_jd = JOB_DESC_PATH.read_text(encoding="utf-8")
    cleaned_jd = clean_text(raw_jd)
    requirements = load_requirements(REQUIREMENTS_PATH)

    files = sorted([f for f in SAMPLE_RESUMES_DIR.iterdir() if f.is_file() and f.name != ".gitkeep"])
    assert len(files) == 10

    candidate_records = []
    for f in files:
        cid = f.stem.replace("candidate_", "CAND-")
        raw = extract_text(f)
        cleaned = clean_text(raw)
        candidate_records.append({
            "id": cid,
            "cleaned_text": cleaned,
        })

    # Phase 8: Score
    scored = score_candidate_batch(cleaned_jd, candidate_records, requirements=requirements, sanitize=True)

    # Phase 9: Rank
    ranked = rank_candidates(scored)

    # Phase 10: Export CSV
    csv_file = tmp_path / "screening_results.csv"
    export_to_csv(ranked, output_path=csv_file)
    assert csv_file.exists()

    df_csv = pd.read_csv(csv_file)
    assert len(df_csv) == 10
    assert list(df_csv["Rank"]) == list(range(1, 11))
    assert set(df_csv["Candidate ID"]) == {f"CAND-{i:03d}" for i in range(1, 11)}

    # Phase 10: Export Excel
    excel_file = tmp_path / "screening_results.xlsx"
    export_to_excel(ranked, output_path=excel_file, metadata={"job_title": "Junior Data Analyst"})
    assert excel_file.exists()

    wb = openpyxl.load_workbook(excel_file)
    assert wb.sheetnames == ["Candidate Ranking", "Detailed Results", "Report Information"]

    ws_ranking = wb["Candidate Ranking"]
    assert ws_ranking.max_row == 11  # 1 header + 10 data rows
    assert ws_ranking.cell(row=2, column=2).value == "CAND-001"
    assert ws_ranking.cell(row=11, column=2).value == "CAND-007"
