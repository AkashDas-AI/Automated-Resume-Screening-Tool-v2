"""
Skill Extractor and Matching Engine
Author: Akash Das
Project: Automated Resume Screening Tool

Responsible for deterministically detecting required and preferred technical skills
from cleaned resume text against the benchmark job requirements configuration,
employing boundary-safe token regexes, preventing false positives on short aliases,
and providing contextual evidence snippets.
"""

import json
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple, Union

DEFAULT_REQUIREMENTS_PATH = (
    Path(__file__).parent.parent / "data" / "job_descriptions" / "junior_data_analyst_requirements.json"
)


def load_requirements(json_path: Optional[Union[str, Path]] = None) -> dict:
    """
    Load structured job skill requirements from a JSON file.

    Args:
        json_path (Optional[Union[str, Path]]): Path to the requirements JSON.
            Defaults to the Junior Data Analyst requirements file.

    Returns:
        dict: Parsed skill requirements specification.

    Raises:
        FileNotFoundError: If the requirements file does not exist.
        ValueError: If the file is not valid JSON or lacks the skill_requirements structure.
    """
    path = Path(json_path) if json_path is not None else DEFAULT_REQUIREMENTS_PATH

    if not path.exists():
        raise FileNotFoundError(f"Skill requirements configuration file not found at: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to decode skill requirements JSON '{path.name}': {exc}") from exc

    if "skill_requirements" not in data:
        raise ValueError(f"Invalid schema: 'skill_requirements' key missing in {path.name}.")

    return data


def build_skill_pattern(term: str) -> re.Pattern:
    """
    Construct a boundary-aware regular expression pattern for a skill or alias.

    Safeguards:
    - Distinguishes 'c' from 'c++' and 'c#' using negative lookahead: \bc\b(?![+#]).
    - Accurately matches 'c++' and 'c#' where standard \b fails on trailing symbols.
    - Accurately matches leading dot terms like '.net' without word boundary failure.
    - Prevents false-positive substring matches on short aliases ('py', 'pd', 'np', 'ml', 'dax').
    - Handles multiword terms ('data cleaning', 'machine learning', 'power bi') with flexible spacing.

    Args:
        term (str): Canonical skill name or alias.

    Returns:
        re.Pattern: Compiled case-insensitive regular expression pattern.
    """
    t = term.lower().strip()

    if t == "c":
        # Matches standalone 'c' but NOT 'c++' or 'c#'
        pattern = r"\bc\b(?![+#a-z0-9])"
    elif t == "c++":
        # Trailing '+' is non-word, so \b fails; use lookahead to ensure end of token
        pattern = r"\bc\+\+(?![+a-z0-9])"
    elif t == "c#":
        # Trailing '#' is non-word, so \b fails; use lookahead to ensure end of token
        pattern = r"\bc\#(?![#a-z0-9])"
    elif t.startswith("."):
        # Leading '.' is non-word, so \b at start fails; ensure not preceded by alphanumeric
        escaped = re.escape(t)
        pattern = rf"(?<![a-z0-9]){escaped}\b"
    else:
        # Standard words, hyphenated terms (scikit-learn), or multiword terms (power bi)
        escaped = re.escape(t)
        # Allow flexible whitespace between words in multiword terms
        escaped = re.sub(r"\\\s+", r"\\s+", escaped)
        pattern = rf"\b{escaped}\b"

    return re.compile(pattern, re.IGNORECASE)


def extract_evidence_snippet(text: str, start: int, end: int, window: int = 35) -> str:
    """
    Extract a contextual snippet surrounding a matched skill in the cleaned resume text.

    Args:
        text (str): Source text where match occurred.
        start (int): Start index of the matched substring.
        end (int): End index of the matched substring.
        window (int): Number of context characters before and after the match.

    Returns:
        str: Contextual snippet formatted with ellipses if truncated.
    """
    s_start = max(0, start - window)
    s_end = min(len(text), end + window)

    # Expand outward to avoid splitting words at snippet boundaries
    while s_start > 0 and not text[s_start].isspace():
        s_start -= 1
    while s_end < len(text) and not text[s_end].isspace():
        s_end += 1

    snippet = text[s_start:s_end].strip()
    # Normalize internal newlines to spaces for clean single-line reporting
    snippet = re.sub(r"\s+", " ", snippet)

    prefix = "..." if s_start > 0 else ""
    suffix = "..." if s_end < len(text) else ""
    return f"{prefix}{snippet}{suffix}"


def _match_category_skills(cleaned_text: str, skill_definitions: List[dict]) -> Tuple[List[dict], List[dict]]:
    """
    Match a list of skill definitions against cleaned text.

    Args:
        cleaned_text (str): Preprocessed resume text.
        skill_definitions (List[dict]): List of skill requirement objects.

    Returns:
        Tuple[List[dict], List[dict]]: (matched_skills, missing_skills)
    """
    matched: List[dict] = []
    missing: List[dict] = []

    for skill in skill_definitions:
        canonical_name = skill.get("canonical_name", "")
        category = skill.get("category", "General")
        importance = skill.get("importance", "")
        skill_id = skill.get("id", "")

        # Candidates terms to test: canonical name followed by aliases
        terms_to_test = [canonical_name]
        terms_to_test.extend(skill.get("aliases", []))

        # Deduplicate while preserving order
        unique_terms = []
        for term in terms_to_test:
            if term and term.lower() not in [u.lower() for u in unique_terms]:
                unique_terms.append(term)

        skill_matched = False
        for term in unique_terms:
            pattern = build_skill_pattern(term)
            match = pattern.search(cleaned_text)
            if match:
                evidence = extract_evidence_snippet(cleaned_text, match.start(), match.end())
                matched.append({
                    "id": skill_id,
                    "canonical_name": canonical_name,
                    "category": category,
                    "importance": importance,
                    "matched_term": term,
                    "evidence": evidence
                })
                skill_matched = True
                break  # Record skill once per candidate

        if not skill_matched:
            missing.append({
                "id": skill_id,
                "canonical_name": canonical_name,
                "category": category,
                "importance": importance
            })

    return matched, missing


def match_skills(
    cleaned_text: str,
    requirements: Optional[dict] = None,
    sanitize_identifiers: bool = False,
    candidate_name: Optional[str] = None
) -> dict:
    """
    Public entry point to match candidate resume text against required and preferred skills.

    Args:
        cleaned_text (str): Normalized text produced by Phase 6 text cleaner.
        requirements (Optional[dict]): Requirements specification loaded from JSON.
            If None, automatically loaded from the default project requirements file.
        sanitize_identifiers (bool): If True, strips personal identifiers (candidate names,
            emails, phones, location headers) before matching, preventing demographic or contact
            data from contributing false skill matches. Defaults to False.
        candidate_name (Optional[str]): Explicit candidate name to strip when sanitize_identifiers=True.

    Returns:
        dict: Deterministic dictionary structured as:
            {
                "required": {
                    "matched": [ {"canonical_name": ..., "matched_term": ..., "evidence": ...}, ... ],
                    "missing": [ {"canonical_name": ...}, ... ]
                },
                "preferred": {
                    "matched": [ {"canonical_name": ..., "matched_term": ..., "evidence": ...}, ... ],
                    "missing": [ {"canonical_name": ...}, ... ]
                }
            }

    Raises:
        TypeError: If cleaned_text is not a string.
        ValueError: If requirements structure is missing expected keys.
    """
    if not isinstance(cleaned_text, str):
        raise TypeError(f"match_skills expected cleaned_text to be of type str, but received {type(cleaned_text).__name__}.")

    if sanitize_identifiers:
        from src.text_cleaner import strip_personal_identifiers
        target_text = strip_personal_identifiers(cleaned_text, candidate_name=candidate_name)
    else:
        target_text = cleaned_text

    if requirements is None:
        requirements = load_requirements()

    if not isinstance(requirements, dict) or "skill_requirements" not in requirements:
        raise ValueError("Invalid requirements object: missing 'skill_requirements' dictionary.")

    skills_spec = requirements["skill_requirements"]
    required_spec = skills_spec.get("required", [])
    preferred_spec = skills_spec.get("preferred", [])

    matched_req, missing_req = _match_category_skills(target_text, required_spec)
    matched_pref, missing_pref = _match_category_skills(target_text, preferred_spec)

    return {
        "required": {
            "matched": matched_req,
            "missing": missing_req
        },
        "preferred": {
            "matched": matched_pref,
            "missing": missing_pref
        }
    }


def extract_skills(text: str, requirements: Optional[dict] = None) -> List[str]:
    """
    Extract a simple flat list of all matched canonical skill names from text.
    Maintained for backward compatibility and quick querying.

    Args:
        text (str): Cleaned or raw text.
        requirements (Optional[dict]): Requirements dictionary.

    Returns:
        List[str]: List of matched canonical skill names.
    """
    match_result = match_skills(text, requirements=requirements)
    all_matched = []
    for item in match_result["required"]["matched"]:
        all_matched.append(item["canonical_name"])
    for item in match_result["preferred"]["matched"]:
        all_matched.append(item["canonical_name"])
    return all_matched
