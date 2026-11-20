"""
Unit Tests for Skill Extractor Module
Author: Akash Das
Project: Automated Resume Screening Tool

Comprehensive automated test suite validating canonical skill matching,
configured alias resolution, required vs preferred separation, false-positive
prevention on short aliases (py, pd, np, ml, dax), C/C++/C# differentiation,
evidence extraction, and integration across all 10 synthetic resumes.
"""

from pathlib import Path
import pytest

from src.resume_parser import extract_text
from src.text_cleaner import clean_text
from src.skill_extractor import (
    load_requirements,
    match_skills,
    extract_skills,
    build_skill_pattern,
)

SAMPLE_RESUMES_DIR = Path(__file__).parent.parent / "data" / "sample_resumes"
REQUIREMENTS_PATH = (
    Path(__file__).parent.parent / "data" / "job_descriptions" / "junior_data_analyst_requirements.json"
)


@pytest.fixture
def requirements():
    """Load default requirements JSON."""
    return load_requirements(REQUIREMENTS_PATH)


# --------------------------------------------------------------------------
# 1. Canonical and Alias Matching
# --------------------------------------------------------------------------
def test_exact_canonical_skill_matching(requirements):
    """Verify that exact canonical skill names match correctly."""
    text = "Candidate has strong knowledge of Python, SQL, and Pandas."
    cleaned = clean_text(text)
    res = match_skills(cleaned, requirements)

    matched_req_names = [s["canonical_name"] for s in res["required"]["matched"]]
    assert "Python" in matched_req_names
    assert "SQL" in matched_req_names
    assert "Pandas" in matched_req_names


def test_configured_alias_matching(requirements):
    """Verify configured aliases (e.g. postgresql for SQL, sklearn for Scikit-learn) match."""
    text = "Experience with postgresql databases and sklearn predictive models."
    cleaned = clean_text(text)
    res = match_skills(cleaned, requirements)

    matched_req = {s["canonical_name"]: s for s in res["required"]["matched"]}
    matched_pref = {s["canonical_name"]: s for s in res["preferred"]["matched"]}

    assert "SQL" in matched_req
    assert matched_req["SQL"]["matched_term"] == "postgresql"

    assert "Scikit-learn" in matched_pref
    assert matched_pref["Scikit-learn"]["matched_term"] == "sklearn"


def test_required_and_preferred_separation(requirements):
    """Verify skills are properly partitioned into required and preferred buckets."""
    text = "Proficient in Python and Tableau."
    cleaned = clean_text(text)
    res = match_skills(cleaned, requirements)

    req_matched = [s["canonical_name"] for s in res["required"]["matched"]]
    pref_matched = [s["canonical_name"] for s in res["preferred"]["matched"]]

    assert "Python" in req_matched
    assert "Tableau" not in req_matched
    assert "Tableau" in pref_matched
    assert "Python" not in pref_matched


def test_missing_skill_identification(requirements):
    """Verify unmentioned skills are correctly identified in the missing list."""
    text = "Only Python is mentioned here."
    cleaned = clean_text(text)
    res = match_skills(cleaned, requirements)

    missing_req = [s["canonical_name"] for s in res["required"]["missing"]]
    assert "SQL" in missing_req
    assert "Pandas" in missing_req
    assert "Data Cleaning" in missing_req
    assert "Python" not in missing_req


def test_case_insensitive_matching(requirements):
    """Verify matching functions identically regardless of input casing."""
    text1 = clean_text("PYTHON and SQL")
    text2 = clean_text("python and sql")
    res1 = match_skills(text1, requirements)
    res2 = match_skills(text2, requirements)

    assert [s["canonical_name"] for s in res1["required"]["matched"]] == [
        s["canonical_name"] for s in res2["required"]["matched"]
    ]


# --------------------------------------------------------------------------
# 2. Multiword and Hyphenated Skill Matching
# --------------------------------------------------------------------------
def test_multiword_skill_matching(requirements):
    """Verify multiword skills match seamlessly (Data Cleaning, Basic Statistics, Power BI)."""
    text = "Performed data cleaning, basic statistics, and built power bi dashboards."
    cleaned = clean_text(text)
    res = match_skills(cleaned, requirements)

    matched_req = [s["canonical_name"] for s in res["required"]["matched"]]
    matched_pref = [s["canonical_name"] for s in res["preferred"]["matched"]]

    assert "Data Cleaning" in matched_req
    assert "Basic Statistics" in matched_req
    assert "Power BI" in matched_pref


def test_hyphenated_skill_matching(requirements):
    """Verify hyphenated skills like Scikit-learn match properly."""
    text = "Trained regression models using scikit-learn in Python."
    cleaned = clean_text(text)
    res = match_skills(cleaned, requirements)

    matched_pref = [s["canonical_name"] for s in res["preferred"]["matched"]]
    assert "Scikit-learn" in matched_pref


# --------------------------------------------------------------------------
# 3. False-Positive Safeguards & Short Aliases
# --------------------------------------------------------------------------
def test_short_alias_false_positive_prevention(requirements):
    """
    Verify short aliases (py, pd, np, ml, dax) do NOT trigger false positives
    when appearing as substrings inside normal words.
    """
    # Text contains substrings: copy (py), updated (pd), snapshot (np), html (ml), syntax (dax)
    negative_text = "I sent a copy of the updated snapshot with html syntax."
    cleaned = clean_text(negative_text)
    res = match_skills(cleaned, requirements)

    matched_req = [s["canonical_name"] for s in res["required"]["matched"]]
    matched_pref = [s["canonical_name"] for s in res["preferred"]["matched"]]

    assert "Python" not in matched_req
    assert "Pandas" not in matched_req
    assert "NumPy" not in matched_pref
    assert "Machine Learning" not in matched_pref
    assert "Power BI" not in matched_pref


def test_standalone_short_alias_triggers_match(requirements):
    """Verify that legitimate standalone uses of short aliases DO trigger matches."""
    positive_text = "Imported pandas as pd and numpy as np to build ml models."
    cleaned = clean_text(positive_text)
    res = match_skills(cleaned, requirements)

    matched_req = {s["canonical_name"]: s for s in res["required"]["matched"]}
    matched_pref = {s["canonical_name"]: s for s in res["preferred"]["matched"]}

    assert "Pandas" in matched_req
    assert "NumPy" in matched_pref
    assert "Machine Learning" in matched_pref


def test_c_cpp_csharp_differentiation():
    """Verify that C, C++, and C# are distinctly differentiated without cross-matching."""
    pat_c = build_skill_pattern("c")
    pat_cpp = build_skill_pattern("c++")
    pat_csharp = build_skill_pattern("c#")

    text_cpp = "backend written in c++"
    text_csharp = "enterprise services in c#"
    text_c = "systems programming in c and assembly"

    # In C++ text:
    assert pat_cpp.search(text_cpp) is not None
    assert pat_c.search(text_cpp) is None  # C must NOT match C++

    # In C# text:
    assert pat_csharp.search(text_csharp) is not None
    assert pat_c.search(text_csharp) is None  # C must NOT match C#

    # In C text:
    assert pat_c.search(text_c) is not None
    assert pat_cpp.search(text_c) is None
    assert pat_csharp.search(text_c) is None


def test_sql_database_technology_aliases(requirements):
    """
    Verify that configured SQL database aliases (MySQL, PostgreSQL, SQLite)
    resolve to canonical SQL as defined in project requirements.
    """
    for db in ["postgresql", "mysql", "sqlite"]:
        text = clean_text(f"Administered {db} relational clusters.")
        res = match_skills(text, requirements)
        matched_req = {s["canonical_name"]: s for s in res["required"]["matched"]}
        assert "SQL" in matched_req
        assert matched_req["SQL"]["matched_term"] == db


# --------------------------------------------------------------------------
# 4. Evidence Extraction & Edge Cases
# --------------------------------------------------------------------------
def test_evidence_snippet_correctness(requirements):
    """Verify evidence snippet is non-empty, contains the matched term, and has context."""
    text = clean_text("Candidate has extensive hands-on experience in Python scripting.")
    res = match_skills(text, requirements)

    matched_req = {s["canonical_name"]: s for s in res["required"]["matched"]}
    assert "Python" in matched_req
    evidence = matched_req["Python"]["evidence"]

    assert isinstance(evidence, str)
    assert "python" in evidence.lower()
    assert len(evidence) > 10


def test_empty_resume_text(requirements):
    """Verify empty text produces 0 matched and all 12 missing skills."""
    res = match_skills("", requirements)

    assert len(res["required"]["matched"]) == 0
    assert len(res["required"]["missing"]) == 6
    assert len(res["preferred"]["matched"]) == 0
    assert len(res["preferred"]["missing"]) == 6


def test_invalid_input_handling(requirements):
    """Verify appropriate exceptions for invalid input types."""
    with pytest.raises(TypeError, match="match_skills expected cleaned_text to be of type str"):
        match_skills(12345, requirements)  # type: ignore

    with pytest.raises(ValueError, match="Invalid requirements object"):
        match_skills("Some text", {"invalid": "dict"})


def test_extract_skills_flat_list_utility(requirements):
    """Verify extract_skills helper returns flat list of canonical names."""
    text = clean_text("Proficient in Python, SQL, and NumPy.")
    skills = extract_skills(text, requirements)
    assert sorted(skills) == ["NumPy", "Python", "SQL"]


# --------------------------------------------------------------------------
# 5. Integration Across All 10 Real Synthetic Resumes
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "filename, expected_req_skills, expected_pref_skills",
    [
        (
            "candidate_001.pdf",
            ["Python", "SQL", "Pandas", "Data Cleaning"],
            ["NumPy"],
        ),
        (
            "candidate_002.docx",
            ["Python", "SQL"],
            [],
        ),
        (
            "candidate_003.txt",
            ["SQL"],
            [],
        ),
        (
            "candidate_004.pdf",
            ["Python"],
            ["Machine Learning", "Scikit-learn", "Pandas" if False else None],  # Pandas is required
        ),
        (
            "candidate_005.docx",
            ["SQL"],
            ["Excel", "Power BI"],
        ),
        (
            "candidate_006.txt",
            ["Python", "Pandas"],
            ["NumPy", "Machine Learning"],
        ),
        (
            "candidate_007.pdf",
            [],
            [],
        ),
        (
            "candidate_008.docx",
            ["Python"],
            [],
        ),
        (
            "candidate_009.txt",
            ["SQL"],
            ["Excel", "Tableau", "Power BI"],
        ),
        (
            "candidate_010.pdf",
            ["Python", "SQL", "Data Analysis", "Basic Statistics"],
            [],
        ),
    ],
)
def test_all_synthetic_resumes_skill_matching(filename, expected_req_skills, expected_pref_skills, requirements):
    """Verify deterministic skill matching against the 10 real synthetic resumes."""
    file_path = SAMPLE_RESUMES_DIR / filename
    raw_text = extract_text(file_path)
    cleaned_text = clean_text(raw_text)

    res = match_skills(cleaned_text, requirements)

    matched_req = [s["canonical_name"] for s in res["required"]["matched"]]
    matched_pref = [s["canonical_name"] for s in res["preferred"]["matched"]]

    # Verify expected required skills are detected
    for expected in expected_req_skills:
        assert expected in matched_req, f"Expected required skill '{expected}' not found in {filename}"

    # Verify expected preferred skills are detected
    for expected in expected_pref_skills:
        if expected is not None:
            assert expected in matched_pref, f"Expected preferred skill '{expected}' not found in {filename}"
