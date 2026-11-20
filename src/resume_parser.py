"""
Resume Parser Module
Author: Akash Das
Project: Automated Resume Screening Tool

Responsible for extracting raw text from candidate resumes in multiple formats
(PDF, DOCX, TXT), handling unreadable, corrupted, or unsupported files gracefully.
"""

from pathlib import Path
from typing import Union
import zipfile
import docx
import pymupdf


# --------------------------------------------------------------------------
# Custom Exception Hierarchy
# --------------------------------------------------------------------------
class ResumeParserError(Exception):
    """Base exception for all resume parsing errors."""
    pass


class FileFormatNotSupportedError(ResumeParserError, ValueError):
    """Raised when an unsupported file format is encountered."""
    pass


class EmptyFileError(ResumeParserError, ValueError):
    """Raised when the input file has a size of 0 bytes or contains no text."""
    pass


class CorruptedFileError(ResumeParserError, ValueError):
    """Raised when a document cannot be opened or is corrupted."""
    pass


class EncryptedPDFError(ResumeParserError, ValueError):
    """Raised when attempting to read a password-protected PDF."""
    pass


class NoTextExtractedError(ResumeParserError, ValueError):
    """Raised when a document has pages or paragraphs but yields no extractable text."""
    pass


# --------------------------------------------------------------------------
# Format-Specific Extractors
# --------------------------------------------------------------------------
def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract selectable text from every page of a PDF document using PyMuPDF.

    Args:
        file_path (Path): Path to the target PDF file.

    Returns:
        str: Combined extracted text from all pages in order.

    Raises:
        EncryptedPDFError: If the PDF is password-protected.
        CorruptedFileError: If the PDF is invalid or corrupted.
        NoTextExtractedError: If no selectable text is found (e.g., scanned image).
    """
    try:
        doc = pymupdf.open(str(file_path))
    except Exception as exc:
        raise CorruptedFileError(f"Failed to open PDF '{file_path.name}': corrupted or invalid file.") from exc

    try:
        if doc.is_encrypted:
            raise EncryptedPDFError(f"PDF '{file_path.name}' is password-protected and cannot be parsed.")

        page_texts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text:
                page_texts.append(text.strip())

        combined_text = "\n\n".join(page_texts).strip()

        if not combined_text:
            raise NoTextExtractedError(
                f"PDF '{file_path.name}' contains no selectable text (may be an image or scanned document)."
            )

        return combined_text
    finally:
        doc.close()


def extract_text_from_docx(file_path: Path) -> str:
    """
    Extract text from paragraphs and tables of a DOCX document using python-docx.

    Behavior:
    - Extracts all non-empty paragraphs preserving sequence.
    - Extracts all table cell contents, joining cell text with spaces and row cells with newlines.

    Args:
        file_path (Path): Path to the target DOCX file.

    Returns:
        str: Combined text extracted from paragraphs and tables.

    Raises:
        CorruptedFileError: If the file is not a valid DOCX package.
        NoTextExtractedError: If the document contains no extractable text.
    """
    try:
        doc = docx.Document(str(file_path))
    except (zipfile.BadZipFile, docx.opc.exceptions.PackageNotFoundError, Exception) as exc:
        raise CorruptedFileError(f"Failed to open DOCX '{file_path.name}': corrupted or invalid package.") from exc

    extracted_parts = []

    # 1. Extract paragraphs
    for p in doc.paragraphs:
        cleaned = p.text.strip()
        if cleaned:
            extracted_parts.append(cleaned)

    # 2. Extract tables (if any)
    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_cells:
                # Deduplicate identical adjacent cells caused by merged columns
                deduped_cells = []
                for cell_text in row_cells:
                    if not deduped_cells or deduped_cells[-1] != cell_text:
                        deduped_cells.append(cell_text)
                extracted_parts.append(" | ".join(deduped_cells))

    combined_text = "\n\n".join(extracted_parts).strip()

    if not combined_text:
        raise NoTextExtractedError(f"DOCX '{file_path.name}' contains no extractable text.")

    return combined_text


def extract_text_from_txt(file_path: Path) -> str:
    """
    Extract raw text from a plain TXT file using UTF-8 encoding.

    Args:
        file_path (Path): Path to the target TXT file.

    Returns:
        str: Raw string content of the file.

    Raises:
        CorruptedFileError: If the file cannot be decoded using UTF-8.
        NoTextExtractedError: If the file content consists solely of whitespace.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError as exc:
        raise CorruptedFileError(f"Failed to decode TXT '{file_path.name}' using UTF-8 encoding.") from exc
    except Exception as exc:
        raise CorruptedFileError(f"Failed to read TXT '{file_path.name}': {str(exc)}") from exc

    cleaned = content.strip()
    if not cleaned:
        raise NoTextExtractedError(f"TXT '{file_path.name}' contains no text or only whitespace.")

    return content


# --------------------------------------------------------------------------
# Public Unified Interface
# --------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {
    ".pdf": extract_text_from_pdf,
    ".docx": extract_text_from_docx,
    ".txt": extract_text_from_txt,
}


def extract_text(file_path: Union[str, Path]) -> str:
    """
    Universal text extraction entry point for resumes in PDF, DOCX, or TXT formats.

    Validates file existence, non-zero file size, and extension compatibility,
    then dispatches extraction to the corresponding format handler.

    Args:
        file_path (Union[str, Path]): Path to the resume file.

    Returns:
        str: Extracted text content.

    Raises:
        FileNotFoundError: If the file does not exist.
        EmptyFileError: If the file size is 0 bytes.
        FileFormatNotSupportedError: If the file extension is not supported (.pdf, .docx, .txt).
        CorruptedFileError: If the file cannot be parsed or decoded.
        EncryptedPDFError: If a PDF is password protected.
        NoTextExtractedError: If no readable text can be extracted.
    """
    path = Path(file_path)

    # 1. Existence check
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {path}")

    if path.is_dir():
        raise IsADirectoryError(f"Expected a file path, but received a directory: {path}")

    # 2. Empty file check (0 bytes)
    if path.stat().st_size == 0:
        raise EmptyFileError(f"Resume file '{path.name}' is empty (0 bytes).")

    # 3. Format compatibility check
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        supported_list = ", ".join(SUPPORTED_EXTENSIONS.keys())
        raise FileFormatNotSupportedError(
            f"Unsupported file format '{ext}' for file '{path.name}'. Supported formats: {supported_list}."
        )

    # 4. Dispatch to handler
    handler = SUPPORTED_EXTENSIONS[ext]
    return handler(path)


def parse_resume(file_path: Union[str, Path]) -> str:
    """
    Alias for extract_text for backward compatibility with initial phase signatures.
    """
    return extract_text(file_path)
