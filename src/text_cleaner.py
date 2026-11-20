"""
Text Cleaner Module
Author: Akash Das
Project: Automated Resume Screening Tool

Responsible for normalizing raw extracted resume text into consistent,
NLP-ready text while strictly preserving meaningful technical terms, programming
languages (e.g., C, C++, C#, .NET), frameworks (e.g., Node.js, React.js), and
tools (e.g., CI/CD, Scikit-learn, Power BI, REST API).
"""

import re
from typing import List, Tuple

# Mapping of complex technical tokens containing punctuation to temporary alphanumeric placeholders
# to prevent destruction during general punctuation and noise removal.
PROTECTED_TECHNICAL_PATTERNS: List[Tuple[str, str, str]] = [
    # (regex_pattern, temporary_placeholder, restored_token)
    (r"\basp\.net\b", "xxxtokaspnetxxx", "asp.net"),
    (r"(?<![a-z0-9])\.net\b", "xxxtokdotnetxxx", ".net"),
    (r"\bc\+\+", "xxxtokcppxxx", "c++"),
    (r"\bc\#", "xxxtokcsharpxxx", "c#"),
    (r"\bnode\.js\b", "xxxtoknodejsxxx", "node.js"),
    (r"\breact\.js\b", "xxxtokreactjsxxx", "react.js"),
    (r"\bvue\.js\b", "xxxtokvuejsxxx", "vue.js"),
    (r"\bci/cd\b", "xxxtokcicdxxx", "ci/cd"),
    (r"\bpl/sql\b", "xxxtokplsqlxxx", "pl/sql"),
    (r"\btcp/ip\b", "xxxtoktcpipxxx", "tcp/ip"),
]


def clean_text(text: str) -> str:
    """
    Transform raw extracted resume text into standardized, normalized text.

    Preserves critical technical tokens (C, C++, C#, .NET, Node.js, CI/CD, etc.),
    removes formatting noise, handles line breaks and repeated whitespace,
    and applies lowercasing.

    Args:
        text (str): Raw text extracted from document.

    Returns:
        str: Normalized, cleaned text.

    Raises:
        TypeError: If the input is not a string.
    """
    # 1. Type validation
    if not isinstance(text, str):
        raise TypeError(f"clean_text expected input of type str, but received {type(text).__name__}.")

    # 2. Check for empty or whitespace-only input
    if not text.strip():
        return ""

    # 3. Normalize line endings (Windows \r\n and old Mac \r to standard \n)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    # 4. Standardize unicode spaces and quotes
    normalized = normalized.replace("\xa0", " ").replace("\u200b", "")
    normalized = re.sub(r"[“”]", '"', normalized)
    normalized = re.sub(r"[‘’`]", "'", normalized)

    # 5. Case normalization (convert to lowercase)
    normalized = normalized.lower()

    # 6. Mask critical technical tokens containing symbols
    for pattern, placeholder, _ in PROTECTED_TECHNICAL_PATTERNS:
        normalized = re.sub(pattern, f" {placeholder} ", normalized)

    # 7. Convert slashes to space to prevent accidental word merging (e.g. Python/Django -> python django)
    normalized = normalized.replace("/", " ")

    # 8. Remove formatting noise, bullet points, and non-alphanumeric symbols
    # Exclude hyphens and periods here because they may belong to decimal numbers or hyphenated terms
    noise_symbols = r"[•●▪■◆►–—_\\|~=+*#&^%$@!?;:,()\[\]{}\"\']"
    normalized = re.sub(noise_symbols, " ", normalized)

    # 9. Clean periods: preserve periods only when strictly between digits (e.g. 3.8, 4.0, 3.11)
    normalized = re.sub(r"(?<!\d)\.|\.(?!\d)", " ", normalized)

    # 10. Clean hyphens: preserve hyphens only when between alphanumeric characters (e.g. scikit-learn, end-to-end)
    normalized = re.sub(r"(?<![a-z0-9])-(?![a-z0-9])", " ", normalized)

    # 11. Restore protected technical tokens
    for _, placeholder, original_token in PROTECTED_TECHNICAL_PATTERNS:
        normalized = normalized.replace(placeholder, original_token)

    # 12. Normalize whitespace across lines:
    # - Collapse tabs and multiple spaces on each line to a single space
    # - Eliminate redundant blank lines
    cleaned_lines = []
    for line in normalized.split("\n"):
        line_clean = re.sub(r"[ \t]+", " ", line).strip()
        if line_clean:
            cleaned_lines.append(line_clean)

    return "\n".join(cleaned_lines)


def tokenize_text(text: str) -> List[str]:
    """
    Tokenize normalized text into clean individual tokens.

    Splits the cleaned text while keeping technical multi-character tokens
    (e.g., 'c++', 'c#', '.net', 'node.js', 'scikit-learn') intact.

    Args:
        text (str): Input text to tokenize (can be raw or cleaned).

    Returns:
        List[str]: List of normalized tokens.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []
    return cleaned.split()


def strip_personal_identifiers(text: str, candidate_name: str = None) -> str:
    """
    Sanitize cleaned text for scoring by removing personal identifiers.

    Excludes:
    - Candidate name (from header line or explicitly passed).
    - Email addresses and email domain remnants.
    - Phone numbers and standard phone formatting patterns.
    - Physical and fictional location markers.
    - Candidate IDs (e.g. cand-001) and author/benchmark metadata.

    Preserves:
    - All technical skills, tools, frameworks, and programming languages.
    - Work experience, project narratives, education descriptions, and certifications.

    Args:
        text (str): Cleaned resume or job description text.
        candidate_name (Optional[str]): Explicit candidate name to strip if known.

    Returns:
        str: Anonymized text suitable for fair, objective TF-IDF vectorization and scoring.
    """
    if not isinstance(text, str):
        raise TypeError(f"strip_personal_identifiers expected str, got {type(text).__name__}.")

    if not text.strip():
        return ""

    lines = text.split("\n")
    cleaned_lines = []

    # Section keywords that indicate the start of substantive resume sections
    section_keywords = {
        "summary", "professional", "experience", "education",
        "skills", "projects", "certifications", "overview", "responsibilities"
    }

    # Only treat the first line as a candidate name header if the document has multiple lines
    start_idx = 0
    if len(lines) > 1:
        first_words = set(lines[0].split())
        if not first_words.intersection(section_keywords) and len(first_words) <= 4:
            start_idx = 1  # Skip first line if it's candidate name

    for line in lines[start_idx:]:
        l = line.strip()
        if not l:
            continue

        # 1. Remove Candidate IDs and Author markers
        l = re.sub(r"\bcandidate\s+id\s*[:\s]*cand[-_]?\d+\b", "", l, flags=re.IGNORECASE)
        l = re.sub(r"\bcand[-_]?\d+\b", "", l, flags=re.IGNORECASE)
        l = re.sub(r"\bauthor\s*[:/]\s*akash\s+das\b", "", l, flags=re.IGNORECASE)
        l = re.sub(r"\bakash\s+das\b", "", l, flags=re.IGNORECASE)

        # 2. Remove email patterns (both raw formatted and clean text variants)
        l = re.sub(r"\bemail\s+[^\s]+(?:\s+[^\s]+)*\b", "", l, flags=re.IGNORECASE)
        l = re.sub(r"\bcontact\s+[^\s]+(?:\s+[^\s]+)*\b", "", l, flags=re.IGNORECASE)
        l = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "", l)
        l = re.sub(r"\b[a-z0-9._%+-]+\s+(?:gmail|yahoo|hotmail|outlook|example|sample|domain)\s+(?:com|org|edu|net|io|in|gov|co)\b", "", l, flags=re.IGNORECASE)

        # 3. Remove phone patterns
        l = re.sub(r"\bphone\s+[^\s]+\b", "", l, flags=re.IGNORECASE)
        l = re.sub(r"(?:\+?\d{1,3}[-.\s]*)?\(?\d{3}\)?[-.\s]*\d{3}[-.\s]*\d{4}\b", "", l)
        l = re.sub(r"\b\d{1,2}-\d{3}-\d{4}\b", "", l)

        # 4. Remove location and address headers / markers
        l = re.sub(r"\blocation\s+[^\s]+(?:\s+[^\s]+)*\b", "", l, flags=re.IGNORECASE)
        l = re.sub(r"\baddress\s+[^\s]+(?:\s+[^\s]+)*\b", "", l, flags=re.IGNORECASE)

        # 5. If explicit candidate_name provided, remove its component name parts
        if candidate_name:
            for part in candidate_name.lower().split():
                if len(part) > 2:
                    l = re.sub(rf"\b{re.escape(part)}\b", "", l, flags=re.IGNORECASE)

        l = re.sub(r"[ \t]+", " ", l).strip()
        if l:
            cleaned_lines.append(l)

    return "\n".join(cleaned_lines)

