"""
Unit Tests for Resume Parser Module
Author: Akash Das
Project: Automated Resume Screening Tool

Comprehensive automated test suite validating text extraction from PDF, DOCX,
and TXT resumes, testing edge cases, corrupted files, unsupported formats,
and error handling.
"""

from pathlib import Path
import pytest
import pymupdf

from src.resume_parser import (
    extract_text,
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt,
    parse_resume,
    EmptyFileError,
    FileFormatNotSupportedError,
    CorruptedFileError,
    EncryptedPDFError,
    NoTextExtractedError,
)

SAMPLE_RESUMES_DIR = Path(__file__).parent.parent / "data" / "sample_resumes"


# --------------------------------------------------------------------------
# 1. Tests for Real Synthetic Resumes (10 Candidates)
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "filename, expected_id, expected_name, expected_skill",
    [
        ("candidate_001.pdf", "CAND-001", "Aarav Sharma", "Python"),
        ("candidate_004.pdf", "CAND-004", "Sneha Patel", "Machine Learning"),
        ("candidate_007.pdf", "CAND-007", "Karan Verma", "React"),
        ("candidate_010.pdf", "CAND-010", "Divya Sengupta", "Statistics"),
    ],
)
def test_extract_pdf_resumes(filename, expected_id, expected_name, expected_skill):
    """Test text extraction from all four real synthetic PDF resumes."""
    file_path = SAMPLE_RESUMES_DIR / filename
    assert file_path.exists(), f"Resume file {filename} does not exist."

    text = extract_text(file_path)

    assert isinstance(text, str)
    assert len(text.strip()) > 100
    assert expected_id in text
    assert expected_name.lower() in text.lower()
    assert expected_skill.lower() in text.lower()


@pytest.mark.parametrize(
    "filename, expected_id, expected_name, expected_skill",
    [
        ("candidate_002.docx", "CAND-002", "Priya Nair", "Django"),
        ("candidate_005.docx", "CAND-005", "Vikram Malhotra", "Power BI"),
        ("candidate_008.docx", "CAND-008", "Meera Iyer", "Flask"),
    ],
)
def test_extract_docx_resumes(filename, expected_id, expected_name, expected_skill):
    """Test text extraction from all three real synthetic DOCX resumes."""
    file_path = SAMPLE_RESUMES_DIR / filename
    assert file_path.exists(), f"Resume file {filename} does not exist."

    text = extract_text(file_path)

    assert isinstance(text, str)
    assert len(text.strip()) > 100
    assert expected_id in text
    assert expected_name.lower() in text.lower()
    assert expected_skill.lower() in text.lower()


@pytest.mark.parametrize(
    "filename, expected_id, expected_name, expected_skill",
    [
        ("candidate_003.txt", "CAND-003", "Rohan Kulkarni", "Spring Boot"),
        ("candidate_006.txt", "CAND-006", "Ananya Deshmukh", "NumPy"),
        ("candidate_009.txt", "CAND-009", "Arjun Reddy", "Tableau"),
    ],
)
def test_extract_txt_resumes(filename, expected_id, expected_name, expected_skill):
    """Test text extraction from all three real synthetic TXT resumes."""
    file_path = SAMPLE_RESUMES_DIR / filename
    assert file_path.exists(), f"Resume file {filename} does not exist."

    text = extract_text(file_path)

    assert isinstance(text, str)
    assert len(text.strip()) > 100
    assert expected_id in text
    assert expected_name.lower() in text.lower()
    assert expected_skill.lower() in text.lower()


def test_parse_resume_alias_consistency():
    """Verify parse_resume produces identical results to extract_text."""
    file_path = SAMPLE_RESUMES_DIR / "candidate_001.pdf"
    assert extract_text(file_path) == parse_resume(file_path)


def test_extract_text_accepts_string_path():
    """Verify extract_text accepts string representation of path."""
    file_path_str = str(SAMPLE_RESUMES_DIR / "candidate_003.txt")
    text = extract_text(file_path_str)
    assert "CAND-003" in text


# --------------------------------------------------------------------------
# 2. Edge Cases and Error Handling Tests
# --------------------------------------------------------------------------
def test_missing_file_raises_filenotfound():
    """Verify FileNotFoundError is raised for non-existent files."""
    missing_path = SAMPLE_RESUMES_DIR / "non_existent_resume.pdf"
    with pytest.raises(FileNotFoundError, match="Resume file not found"):
        extract_text(missing_path)


def test_directory_path_raises_isadirectoryerror():
    """Verify IsADirectoryError is raised when passing a folder path."""
    with pytest.raises(IsADirectoryError, match="received a directory"):
        extract_text(SAMPLE_RESUMES_DIR)


def test_unsupported_extension_raises_error(tmp_path):
    """Verify FileFormatNotSupportedError for unsupported formats like .jpg or .csv."""
    unsupported_file = tmp_path / "resume.jpg"
    unsupported_file.write_bytes(b"image data placeholder")

    with pytest.raises(FileFormatNotSupportedError, match="Unsupported file format '.jpg'"):
        extract_text(unsupported_file)


def test_empty_file_raises_emptyfileerror(tmp_path):
    """Verify EmptyFileError is raised when file size is 0 bytes."""
    empty_pdf = tmp_path / "empty_candidate.pdf"
    empty_pdf.touch()  # Creates a 0-byte file

    with pytest.raises(EmptyFileError, match="empty \\(0 bytes\\)"):
        extract_text(empty_pdf)


def test_corrupted_pdf_raises_corruptedfileerror(tmp_path):
    """Verify CorruptedFileError is raised for corrupted PDF files."""
    corrupted_pdf = tmp_path / "corrupted.pdf"
    corrupted_pdf.write_bytes(b"%PDF-1.4 non-valid-pdf-header-and-garbage-data")

    with pytest.raises(CorruptedFileError, match="corrupted or invalid file"):
        extract_text(corrupted_pdf)


def test_corrupted_docx_raises_corruptedfileerror(tmp_path):
    """Verify CorruptedFileError is raised for non-zip or corrupted DOCX files."""
    corrupted_docx = tmp_path / "corrupted.docx"
    corrupted_docx.write_bytes(b"PK\x03\x04 fake corrupted zip header")

    with pytest.raises(CorruptedFileError, match="corrupted or invalid package"):
        extract_text(corrupted_docx)


def test_pdf_no_selectable_text_raises_notextextractederror(tmp_path):
    """Verify NoTextExtractedError when a PDF has pages but zero text (e.g. image-only)."""
    blank_pdf = tmp_path / "blank_page.pdf"
    doc = pymupdf.open()
    doc.new_page(width=595, height=842)  # Empty blank page
    doc.save(str(blank_pdf))
    doc.close()

    with pytest.raises(NoTextExtractedError, match="contains no selectable text"):
        extract_text(blank_pdf)


def test_encrypted_pdf_raises_encryptedpdferror(tmp_path):
    """Verify EncryptedPDFError when opening a password-protected PDF."""
    encrypted_pdf = tmp_path / "protected.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text(pymupdf.Point(50, 50), "Confidential resume data")
    doc.save(
        str(encrypted_pdf),
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        user_pw="secretpassword",
        owner_pw="ownerpassword",
    )
    doc.close()

    with pytest.raises(EncryptedPDFError, match="is password-protected"):
        extract_text(encrypted_pdf)


def test_txt_with_only_whitespace_raises_notextextractederror(tmp_path):
    """Verify NoTextExtractedError when a TXT file only has whitespace."""
    whitespace_txt = tmp_path / "spaces.txt"
    whitespace_txt.write_text("   \n\n\t   \n", encoding="utf-8")

    with pytest.raises(NoTextExtractedError, match="contains no text or only whitespace"):
        extract_text(whitespace_txt)


def test_extract_multipage_pdf(tmp_path):
    """Verify extract_text extracts text across all pages of a multi-page PDF."""
    multipage_pdf = tmp_path / "multipage_candidate.pdf"
    doc = pymupdf.open()

    p1 = doc.new_page(width=595, height=842)
    p1.insert_text(pymupdf.Point(50, 50), "PAGE 1: Candidate Overview and Skills: Python, SQL")

    p2 = doc.new_page(width=595, height=842)
    p2.insert_text(pymupdf.Point(50, 50), "PAGE 2: Experience and Publications: Lead Data Scientist")

    doc.save(str(multipage_pdf))
    doc.close()

    extracted = extract_text(multipage_pdf)
    assert "PAGE 1: Candidate Overview and Skills" in extracted
    assert "PAGE 2: Experience and Publications" in extracted
    assert "Lead Data Scientist" in extracted


def test_extract_docx_with_tables(tmp_path):
    """Verify extract_text extracts both paragraphs and table cell contents from DOCX."""
    import docx

    docx_path = tmp_path / "table_resume.docx"
    doc = docx.Document()
    doc.add_paragraph("Introductory Candidate Summary: Senior Software Engineer")

    table = doc.add_table(rows=2, cols=3)
    table.cell(0, 0).text = "Skill Name"
    table.cell(0, 1).text = "Proficiency"
    table.cell(0, 2).text = "Years Experience"

    table.cell(1, 0).text = "Python Programming"
    table.cell(1, 1).text = "Expert"
    table.cell(1, 2).text = "5 Years"

    doc.add_paragraph("Concluding Section: Available immediately for hire.")
    doc.save(str(docx_path))

    extracted = extract_text(docx_path)
    assert "Introductory Candidate Summary" in extracted
    assert "Skill Name" in extracted
    assert "Proficiency" in extracted
    assert "Python Programming" in extracted
    assert "Expert" in extracted
    assert "Concluding Section" in extracted


def test_invalid_utf8_txt_raises_corruptedfileerror(tmp_path):
    """Verify parser raises CorruptedFileError when encountering invalid UTF-8 bytes."""
    bad_txt = tmp_path / "invalid_utf8.txt"
    bad_txt.write_bytes(b"Candidate Name: Invalid\n\xff\xfe\x80\x81 Corrupted Bytes")

    with pytest.raises(CorruptedFileError, match="Failed to decode TXT .* using UTF-8 encoding"):
        extract_text(bad_txt)

