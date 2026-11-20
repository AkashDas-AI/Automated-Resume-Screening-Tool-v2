"""
Unit Tests for Text Cleaner Module
Author: Akash Das
Project: Automated Resume Screening Tool

Comprehensive automated test suite validating text normalization, case folding,
noise removal, critical technical token preservation (C, C++, C#, .NET, Node.js,
CI/CD, Scikit-learn, etc.), word boundary protection, and integration across
all 10 synthetic resumes.
"""

from pathlib import Path
import pytest

from src.resume_parser import extract_text
from src.text_cleaner import clean_text, tokenize_text

SAMPLE_RESUMES_DIR = Path(__file__).parent.parent / "data" / "sample_resumes"


# --------------------------------------------------------------------------
# 1. Fundamental Normalization Tests
# --------------------------------------------------------------------------
def test_normal_text_cleaning():
    """Verify standard narrative text is cleaned, lowercased, and trimmed."""
    raw = "Experienced Software Engineer with a Bachelor of Science in Computer Science."
    expected = "experienced software engineer with a bachelor of science in computer science"
    assert clean_text(raw) == expected


def test_case_normalization():
    """Verify mixed case is uniformly converted to lowercase."""
    raw = "DATA ANALYST specializing in Python, SQL, and MACHINE LEARNING."
    cleaned = clean_text(raw)
    assert cleaned == "data analyst specializing in python sql and machine learning"


def test_repeated_spaces_and_tabs():
    """Verify multiple spaces and tabs within lines are collapsed to single spaces."""
    raw = "Python \t\t  Developer   \t with    3+ years   experience."
    cleaned = clean_text(raw)
    assert cleaned == "python developer with 3 years experience"


def test_multiple_blank_lines():
    """Verify excessive consecutive blank lines are collapsed."""
    raw = "Section 1: Summary\n\n\n\n\nSection 2: Experience\n\n\nSection 3: Education"
    cleaned = clean_text(raw)
    assert cleaned == "section 1 summary\nsection 2 experience\nsection 3 education"


def test_windows_and_unix_line_endings():
    """Verify consistent behavior across Windows (CRLF) and Unix (LF) line endings."""
    windows_text = "Header Line\r\n\r\nBody Line 1\r\nBody Line 2"
    unix_text = "Header Line\n\nBody Line 1\nBody Line 2"

    cleaned_win = clean_text(windows_text)
    cleaned_unix = clean_text(unix_text)

    assert cleaned_win == cleaned_unix
    assert cleaned_win == "header line\nbody line 1\nbody line 2"


# --------------------------------------------------------------------------
# 2. Input Validation and Boundary Tests
# --------------------------------------------------------------------------
def test_empty_string():
    """Verify empty string returns empty string."""
    assert clean_text("") == ""


def test_whitespace_only_strings():
    """Verify strings containing only spaces, tabs, or newlines return empty string."""
    assert clean_text("     ") == ""
    assert clean_text("\t\t\n\n   \r\n") == ""


def test_non_string_input_raises_typeerror():
    """Verify TypeError is raised when input is not a string."""
    with pytest.raises(TypeError, match="clean_text expected input of type str"):
        clean_text(None)  # type: ignore

    with pytest.raises(TypeError, match="clean_text expected input of type str"):
        clean_text(12345)  # type: ignore

    with pytest.raises(TypeError, match="clean_text expected input of type str"):
        clean_text(["Python", "SQL"])  # type: ignore


# --------------------------------------------------------------------------
# 3. Punctuation and Noise Handling
# --------------------------------------------------------------------------
def test_punctuation_and_bullet_handling():
    """Verify bullets, brackets, commas, colons, and symbols are replaced with space."""
    raw = "• Skills: [Python], (SQL), {Pandas}; *NumPy* & 'Docker' ~ $100%!"
    cleaned = clean_text(raw)
    assert cleaned == "skills python sql pandas numpy docker 100"


def test_decimal_numbers_preserved():
    """Verify GPA and version numbers like 3.8 and 4.0 retain decimal period."""
    raw = "Graduated with 3.8/4.0 GPA using Python 3.11."
    cleaned = clean_text(raw)
    assert "3.8 4.0" in cleaned
    assert "3.11" in cleaned


# --------------------------------------------------------------------------
# 4. Critical Technical Token Preservation Tests
# --------------------------------------------------------------------------
def test_preservation_of_c_cpp_csharp_and_dotnet():
    """
    Verify C, C++, C#, and .NET are preserved distinctly.
    Crucially ensures C++ does not become C and .NET does not become NET.
    """
    raw = "Core programming languages: C, C++, C#, and Microsoft .NET framework."
    cleaned = clean_text(raw)

    tokens = tokenize_text(raw)

    assert "c" in tokens
    assert "c++" in tokens
    assert "c#" in tokens
    assert ".net" in tokens
    # Verify C++ didn't collapse into C
    assert "c++" in cleaned
    assert "c#" in cleaned
    assert ".net" in cleaned


def test_preservation_of_aspnet_nodejs_reactjs_and_cicd():
    """Verify ASP.NET, Node.js, React.js, and CI/CD maintain exact token structure."""
    raw = "Built microservices using ASP.NET, Node.js backends, React.js frontends, and CI/CD pipelines."
    cleaned = clean_text(raw)

    tokens = tokenize_text(raw)

    assert "asp.net" in tokens
    assert "node.js" in tokens
    assert "react.js" in tokens
    assert "ci/cd" in tokens

    assert "asp.net" in cleaned
    assert "node.js" in cleaned
    assert "react.js" in cleaned
    assert "ci/cd" in cleaned


def test_preservation_of_multiword_and_hyphenated_skills():
    """Verify Power BI, Machine Learning, Scikit-learn, REST API, GitHub, HTML5, CSS3."""
    raw = "Stack: Power BI, Machine Learning, Scikit-learn, REST API, GitHub, HTML5, CSS3, SQL."
    cleaned = clean_text(raw)

    assert "power bi" in cleaned
    assert "machine learning" in cleaned
    assert "scikit-learn" in cleaned
    assert "rest api" in cleaned
    assert "github" in cleaned
    assert "html5" in cleaned
    assert "css3" in cleaned
    assert "sql" in cleaned


def test_prevention_of_accidental_word_merging():
    """
    Verify words separated by slashes, dashes, or bullet points do not merge together.
    For example: Python/Django -> python django (not pythondjango).
    """
    raw = "Specialized in Python/Django, FastAPI/Flask, CI/CD, and Backend-Frontend systems."
    cleaned = clean_text(raw)

    assert "python django" in cleaned
    assert "pythondjango" not in cleaned
    assert "fastapi flask" in cleaned
    assert "fastapiflask" not in cleaned
    assert "ci/cd" in cleaned


# --------------------------------------------------------------------------
# 5. Integration Test: Cleaning All 10 Real Synthetic Resumes
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "filename, expected_id, expected_tokens",
    [
        ("candidate_001.pdf", "cand-001", ["python", "sql", "pandas", "numpy"]),
        ("candidate_002.docx", "cand-002", ["python", "django", "rest api", "sql"]),
        ("candidate_003.txt", "cand-003", ["java", "spring boot", "sql"]),
        ("candidate_004.pdf", "cand-004", ["python", "machine learning", "scikit-learn"]),
        ("candidate_005.docx", "cand-005", ["excel", "power bi", "sql"]),
        ("candidate_006.txt", "cand-006", ["python", "numpy", "pandas", "machine learning"]),
        ("candidate_007.pdf", "cand-007", ["html", "css", "javascript", "react"]),
        ("candidate_008.docx", "cand-008", ["python", "flask", "git"]),
        ("candidate_009.txt", "cand-009", ["sql", "excel", "tableau", "power bi"]),
        ("candidate_010.pdf", "cand-010", ["python", "sql", "statistics", "data analysis"]),
    ],
)
def test_clean_real_synthetic_resumes(filename, expected_id, expected_tokens):
    """Verify that extract_text and clean_text work seamlessly on all 10 candidate resumes."""
    file_path = SAMPLE_RESUMES_DIR / filename
    assert file_path.exists()

    raw_text = extract_text(file_path)
    cleaned_text = clean_text(raw_text)

    # 1. Must produce a non-empty string shorter than or equal to raw text
    assert isinstance(cleaned_text, str)
    assert len(cleaned_text) > 0
    assert len(cleaned_text) <= len(raw_text)

    # 2. Must contain lowercased candidate ID
    assert expected_id in cleaned_text

    # 3. Must preserve all required technical tokens in normalized form
    for token in expected_tokens:
        assert token in cleaned_text, f"Token '{token}' missing from cleaned {filename}"
