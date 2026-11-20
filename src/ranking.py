"""
Candidate Ranking Module
Author: Akash Das
Project: Automated Resume Screening Tool

Responsible for sorting candidate score records produced by Phase 8 into a deterministic,
descending order based on composite match score, applying standardized tie-breaking rules,
and assigning configurable human-review categories (High Match, Moderate Match, Low Match).

Ethical Boundary & Disclaimer:
This module provides structured decision-support aids for human recruiters.
Thresholds and review categories are illustrative educational reference points,
NOT scientifically validated hiring cutoffs.
No candidate is ever automatically rejected, filtered out, or disqualified.
Human review remains mandatory for all candidates.
"""

import copy
from typing import List, Dict, Any, Optional, Tuple

# Default illustrative thresholds for human-review organization
DEFAULT_THRESHOLDS: Dict[str, float] = {
    "high": 70.0,
    "moderate": 40.0,
}

REVIEW_CATEGORY_HIGH = "High Match"
REVIEW_CATEGORY_MODERATE = "Moderate Match"
REVIEW_CATEGORY_LOW = "Low Match"


def validate_thresholds(thresholds: Dict[str, float]) -> None:
    """
    Validate threshold configuration dictionary.

    Args:
        thresholds (Dict[str, float]): Dictionary containing 'high' and 'moderate' keys.

    Raises:
        TypeError: If thresholds is not a dictionary or values are non-numeric.
        ValueError: If required keys are missing, values are out of bounds [0, 100],
            or moderate threshold is not strictly less than high threshold.
    """
    if not isinstance(thresholds, dict):
        raise TypeError(f"thresholds must be a dictionary, got {type(thresholds).__name__}.")

    expected_keys = {"high", "moderate"}
    missing = expected_keys - set(thresholds.keys())
    if missing:
        raise ValueError(f"thresholds dictionary missing required keys: {sorted(missing)}.")

    high = thresholds["high"]
    moderate = thresholds["moderate"]

    if not isinstance(high, (int, float)) or isinstance(high, bool):
        raise TypeError(f"Threshold 'high' must be numeric, got {type(high).__name__}.")
    if not isinstance(moderate, (int, float)) or isinstance(moderate, bool):
        raise TypeError(f"Threshold 'moderate' must be numeric, got {type(moderate).__name__}.")

    if not (0.0 <= moderate <= 100.0):
        raise ValueError(f"Threshold 'moderate' must be between 0.0 and 100.0, got {moderate}.")
    if not (0.0 <= high <= 100.0):
        raise ValueError(f"Threshold 'high' must be between 0.0 and 100.0, got {high}.")

    if moderate >= high:
        raise ValueError(
            f"Threshold 'moderate' ({moderate}) must be strictly less than 'high' ({high})."
        )


def assign_review_category(
    score: float,
    thresholds: Optional[Dict[str, float]] = None
) -> str:
    """
    Categorize a composite score into an illustrative human-review aid tier.

    Thresholds:
    - High Match: Score >= high threshold (default: >= 70.0)
    - Moderate Match: Score >= moderate threshold and < high threshold (default: >= 40.0 and < 70.0)
    - Low Match: Score < moderate threshold (default: < 40.0)

    Educational Reminder:
    'Low Match' is an organizational categorization for human review, NEVER an automated rejection.
    All candidates remain eligible for human recruiter review.

    Args:
        score (float): Composite match score bounded in [0.0, 100.0].
        thresholds (Optional[Dict[str, float]]): Custom thresholds. Defaults to DEFAULT_THRESHOLDS.

    Returns:
        str: Category name ('High Match', 'Moderate Match', or 'Low Match').

    Raises:
        TypeError: If score is non-numeric.
        ValueError: If score is out of [0.0, 100.0] range or thresholds are invalid.
    """
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        raise TypeError(f"score must be a numeric value, got {type(score).__name__}.")

    if score < 0.0 or score > 100.0:
        raise ValueError(f"score must be between 0.0 and 100.0, got {score}.")

    active_thresholds = dict(DEFAULT_THRESHOLDS) if thresholds is None else dict(thresholds)
    validate_thresholds(active_thresholds)

    high_cutoff = active_thresholds["high"]
    mod_cutoff = active_thresholds["moderate"]

    if score >= high_cutoff:
        return REVIEW_CATEGORY_HIGH
    elif score >= mod_cutoff:
        return REVIEW_CATEGORY_MODERATE
    else:
        return REVIEW_CATEGORY_LOW


def _extract_metric_values(record: Dict[str, Any]) -> Tuple[str, float, float, float, float]:
    """
    Safely extract candidate ID and numerical score components from a candidate record.
    Supports both nested Phase 8 scorecard format and flattened candidate dictionaries.

    Returns:
        Tuple[str, float, float, float, float]:
            (candidate_id, composite_score, required_coverage, preferred_coverage, cosine_similarity)
    """
    if not isinstance(record, dict):
        raise TypeError(f"Candidate card must be a dict, got {type(record).__name__}.")

    # 1. Candidate ID
    cid = record.get("candidate_id") or record.get("id")
    if cid is None or not str(cid).strip():
        raise ValueError("Candidate card missing valid 'candidate_id' or 'id'.")
    candidate_id = str(cid).strip()

    # 2. Composite score
    if "composite_score" not in record:
        raise ValueError(f"Candidate '{candidate_id}' missing required 'composite_score'.")
    c_score = record["composite_score"]
    if not isinstance(c_score, (int, float)) or isinstance(c_score, bool):
        raise TypeError(f"Candidate '{candidate_id}' composite_score must be numeric, got {type(c_score).__name__}.")
    if c_score < 0.0 or c_score > 100.0:
        raise ValueError(f"Candidate '{candidate_id}' composite_score out of range [0, 100]: {c_score}.")
    composite_score = float(c_score)

    # 3. Required skill coverage
    if "required_skills" in record and isinstance(record["required_skills"], dict):
        req_cov = record["required_skills"].get("coverage", 0.0)
    else:
        req_cov = record.get("required_coverage", 0.0)
    if not isinstance(req_cov, (int, float)) or isinstance(req_cov, bool):
        raise TypeError(f"Candidate '{candidate_id}' required coverage must be numeric.")
    required_coverage = float(req_cov)

    # 4. Preferred skill coverage
    if "preferred_skills" in record and isinstance(record["preferred_skills"], dict):
        pref_cov = record["preferred_skills"].get("coverage", 0.0)
    else:
        pref_cov = record.get("preferred_coverage", 0.0)
    if not isinstance(pref_cov, (int, float)) or isinstance(pref_cov, bool):
        raise TypeError(f"Candidate '{candidate_id}' preferred coverage must be numeric.")
    preferred_coverage = float(pref_cov)

    # 5. TF-IDF cosine similarity
    if "similarity" in record and isinstance(record["similarity"], dict):
        sim = record["similarity"].get("cosine_similarity", 0.0)
    else:
        sim = record.get("cosine_similarity", 0.0)
    if not isinstance(sim, (int, float)) or isinstance(sim, bool):
        raise TypeError(f"Candidate '{candidate_id}' cosine_similarity must be numeric.")
    cosine_similarity = float(sim)

    return candidate_id, composite_score, required_coverage, preferred_coverage, cosine_similarity


def _compute_sort_key(record: Dict[str, Any]) -> Tuple[float, float, float, float, str]:
    """
    Compute a deterministic sort key implementing the exact tie-breaking specification:
    1. Higher actual composite score (descending)
    2. Higher required skill coverage (descending)
    3. Higher preferred skill coverage (descending)
    4. Higher TF-IDF cosine similarity (descending)
    5. Candidate ID in ascending alphabetical/numerical order (ascending)

    Uses original unrounded numerical values for comparisons to ensure that a candidate
    with a genuinely higher composite score is never placed below a candidate with a lower
    composite score due to rounding.
    """
    cid, comp, req_cov, pref_cov, sim = _extract_metric_values(record)
    return (
        -float(comp),
        -float(req_cov),
        -float(pref_cov),
        -float(sim),
        str(cid),
    )


def rank_candidates(
    candidate_cards: List[Dict[str, Any]],
    thresholds: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Rank candidate scoring records descending by composite score with standardized tie-breaking
    and assign configurable human-review categories.

    Tie-breaking Hierarchy (applied when composite scores are equal):
    1. Higher required skill coverage
    2. Higher preferred skill coverage
    3. Higher TF-IDF cosine similarity
    4. Candidate ID in ascending order (alphabetical / numerical)

    Immutability Guarantee:
    Original input records are never modified. A deep copy is returned with rank annotations.

    Args:
        candidate_cards (List[Dict[str, Any]]): List of scoring records produced by Phase 8.
        thresholds (Optional[Dict[str, float]]): Custom review tier thresholds.
            Defaults to {'high': 70.0, 'moderate': 40.0}.

    Returns:
        List[Dict[str, Any]]: Deterministically sorted candidate list with sequential ranks (1-indexed)
            and normalized summary fields:
            - 'rank': int
            - 'candidate_id': str
            - 'composite_score': float
            - 'required_coverage': float
            - 'preferred_coverage': float
            - 'cosine_similarity': float
            - 'review_category': str ('High Match' | 'Moderate Match' | 'Low Match')
            - All original Phase 8 score breakdowns preserved.

    Raises:
        TypeError: If candidate_cards is not a list or records are invalid types.
        ValueError: If records contain invalid or missing required metrics.
    """
    if not isinstance(candidate_cards, list):
        raise TypeError(f"candidate_cards must be a list, got {type(candidate_cards).__name__}.")

    if not candidate_cards:
        return []

    # Validate thresholds early
    active_thresholds = dict(DEFAULT_THRESHOLDS) if thresholds is None else dict(thresholds)
    validate_thresholds(active_thresholds)

    # Validate all records before sorting to guarantee complete failure atomicity on malformed data
    seen_ids = set()
    for idx, card in enumerate(candidate_cards):
        if not isinstance(card, dict):
            raise TypeError(f"Item at index {idx} is not a dictionary: {type(card).__name__}.")
        cid, _, _, _, _ = _extract_metric_values(card)
        if cid in seen_ids:
            raise ValueError(f"Duplicate candidate ID detected in ranking input: '{cid}'. Candidate IDs must be unique.")
        seen_ids.add(cid)

    # Sort deterministically using the specified tie-breaking hierarchy
    sorted_cards = sorted(candidate_cards, key=_compute_sort_key)

    # Construct immutable ranked output records
    ranked_results: List[Dict[str, Any]] = []
    for rank_idx, card in enumerate(sorted_cards, start=1):
        ranked_card = copy.deepcopy(card)

        cid, comp, req_cov, pref_cov, sim = _extract_metric_values(card)
        review_category = assign_review_category(comp, thresholds=active_thresholds)

        # Populate standardized ranking summary fields
        ranked_card["rank"] = rank_idx
        ranked_card["candidate_id"] = cid
        ranked_card["composite_score"] = comp
        ranked_card["required_coverage"] = req_cov
        ranked_card["preferred_coverage"] = pref_cov
        ranked_card["cosine_similarity"] = sim
        ranked_card["review_category"] = review_category

        ranked_results.append(ranked_card)

    return ranked_results
