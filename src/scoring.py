"""
Scoring Engine Module
Author: Akash Das
Project: Automated Resume Screening Tool

Responsible for calculating composite match scores combining required skill coverage,
preferred skill coverage, and TF-IDF cosine similarity into transparent,
deterministic relevance metrics.
"""

from typing import Dict, Any, Optional

DEFAULT_WEIGHTS: Dict[str, float] = {
    "required": 70.0,
    "preferred": 10.0,
    "similarity": 20.0,
}


def validate_weights(weights: Dict[str, float]) -> None:
    """
    Validate that scoring weights dictionary contains required keys, non-negative values,
    and sums to exactly 100.0 within floating point tolerance.

    Raises:
        ValueError: If weights are missing, negative, or do not sum to 100.0.
    """
    expected_keys = {"required", "preferred", "similarity"}
    if not isinstance(weights, dict):
        raise TypeError(f"weights must be a dictionary, got {type(weights).__name__}.")

    missing = expected_keys - set(weights.keys())
    if missing:
        raise ValueError(f"weights dictionary missing required keys: {sorted(missing)}.")

    for k, v in weights.items():
        if not isinstance(v, (int, float)):
            raise TypeError(f"Weight '{k}' must be numeric, got {type(v).__name__}.")
        if v < 0:
            raise ValueError(f"Weight '{k}' cannot be negative, got {v}.")

    total = sum(weights.values())
    if abs(total - 100.0) > 1e-4:
        raise ValueError(f"Weights must sum to 100.0, but sum was {total:.4f}.")


def calculate_resume_score(
    skill_match_results: dict,
    cosine_similarity: float,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Calculate composite resume relevance score combining required skill coverage,
    preferred skill coverage, and TF-IDF textual cosine similarity.

    Formula:
        composite_score = (required_coverage * w_req) + (preferred_coverage * w_pref) + (cosine_similarity * w_sim)

    Args:
        skill_match_results (dict): Structured result from Phase 7 match_skills.
        cosine_similarity (float): Cosine similarity value bounded in [0.0, 1.0].
        weights (Optional[Dict[str, float]]): Custom weights summing to 100.0.
            Defaults to {'required': 70.0, 'preferred': 10.0, 'similarity': 20.0}.

    Returns:
        dict: Detailed score breakdown including coverage ratios, individual
            weighted contributions, and composite score out of 100.

    Raises:
        TypeError: If skill_match_results is not a dict or cosine_similarity is not numeric.
        ValueError: If cosine_similarity is out of bounds or skill_match_results is invalid.
    """
    # 1. Validate inputs
    if not isinstance(skill_match_results, dict):
        raise TypeError(f"skill_match_results must be a dict, got {type(skill_match_results).__name__}.")

    if not isinstance(cosine_similarity, (int, float)):
        raise TypeError(f"cosine_similarity must be numeric, got {type(cosine_similarity).__name__}.")

    if cosine_similarity < 0.0 or cosine_similarity > 1.0:
        raise ValueError(f"cosine_similarity must be between 0.0 and 1.0, got {cosine_similarity}.")

    if "required" not in skill_match_results or "preferred" not in skill_match_results:
        raise ValueError("skill_match_results missing 'required' or 'preferred' keys.")

    # 2. Validate weights
    applied_weights = dict(DEFAULT_WEIGHTS) if weights is None else dict(weights)
    validate_weights(applied_weights)

    w_req = applied_weights["required"]
    w_pref = applied_weights["preferred"]
    w_sim = applied_weights["similarity"]

    # 3. Calculate Required Coverage
    req_data = skill_match_results["required"]
    matched_req = req_data.get("matched", [])
    missing_req = req_data.get("missing", [])
    matched_req_count = len(matched_req)
    total_req_count = matched_req_count + len(missing_req)
    required_coverage = (
        matched_req_count / total_req_count if total_req_count > 0 else 0.0
    )

    # 4. Calculate Preferred Coverage
    pref_data = skill_match_results["preferred"]
    matched_pref = pref_data.get("matched", [])
    missing_pref = pref_data.get("missing", [])
    matched_pref_count = len(matched_pref)
    total_pref_count = matched_pref_count + len(missing_pref)
    preferred_coverage = (
        matched_pref_count / total_pref_count if total_pref_count > 0 else 0.0
    )

    # 5. Calculate Weighted Contributions
    required_contribution = required_coverage * w_req
    preferred_contribution = preferred_coverage * w_pref
    similarity_contribution = float(cosine_similarity) * w_sim

    composite_score = required_contribution + preferred_contribution + similarity_contribution
    # Clamp composite score strictly in [0.0, 100.0]
    composite_score = max(0.0, min(100.0, composite_score))

    return {
        "required_skills": {
            "matched_count": matched_req_count,
            "total_count": total_req_count,
            "coverage": required_coverage,
            "weight": w_req,
            "weighted_score": required_contribution,
            "matched_names": [s["canonical_name"] for s in matched_req],
            "missing_names": [s["canonical_name"] for s in missing_req],
        },
        "preferred_skills": {
            "matched_count": matched_pref_count,
            "total_count": total_pref_count,
            "coverage": preferred_coverage,
            "weight": w_pref,
            "weighted_score": preferred_contribution,
            "matched_names": [s["canonical_name"] for s in matched_pref],
            "missing_names": [s["canonical_name"] for s in missing_pref],
        },
        "similarity": {
            "cosine_similarity": float(cosine_similarity),
            "weight": w_sim,
            "weighted_score": similarity_contribution,
        },
        "composite_score": composite_score,
        "weights_applied": applied_weights,
        "disclaimer": (
            "Illustrative text-relevance indicator for educational prototype demonstration. "
            "Scores reflect keyword coverage and textual similarity, not candidate competence or future job performance."
        ),
    }


def calculate_composite_score(
    text_similarity: float,
    skill_coverage: float,
    similarity_weight: float = 0.5,
    skill_weight: float = 0.5
) -> float:
    """
    Simplified composite score utility for two-factor blending.
    Maintained for backwards compatibility.
    """
    return (text_similarity * similarity_weight) + (skill_coverage * skill_weight)


def score_candidate(
    job_description: str,
    resume_text: str,
    candidate_id: Optional[str] = None,
    candidate_name: Optional[str] = None,
    weights: Optional[Dict[str, float]] = None,
    requirements: Optional[dict] = None,
    similarity_engine: Optional[Any] = None,
    sanitize: bool = True
) -> Dict[str, Any]:
    """
    Score a single candidate against a target job description through the full scoring pipeline.

    Preserves the original cleaned resume text for human review while utilizing a separate
    sanitized scoring representation (free of names, emails, phones, and contact headers)
    for both skill matching and TF-IDF similarity.

    Args:
        job_description (str): Target job description text.
        resume_text (str): Raw or cleaned candidate resume text.
        candidate_id (Optional[str]): Unique candidate identifier.
        candidate_name (Optional[str]): Candidate name for identifier stripping.
        weights (Optional[Dict[str, float]]): Custom weights dictionary.
        requirements (Optional[dict]): Requirements dictionary.
        similarity_engine (Optional[Any]): Pre-fitted TFIDFSimilarityEngine.
        sanitize (bool): Whether to strip personal identifiers for scoring. Defaults to True.

    Returns:
        Dict[str, Any]: Complete score breakdown, including:
            - candidate_id: Identifier
            - cleaned_text: Original normalized text (preserved for human review)
            - scoring_text: Sanitized text used for scoring
            - skill_match_results: Skill match output
            - composite_score: Composite score out of 100
    """
    from src.text_cleaner import clean_text, strip_personal_identifiers
    from src.skill_extractor import match_skills
    from src.similarity import calculate_similarity

    # 1. Clean text (preserving full narrative for human review)
    cleaned = clean_text(resume_text)

    # 2. Separate sanitized scoring representation (excluding personal identifiers)
    scoring_text = strip_personal_identifiers(cleaned, candidate_name=candidate_name) if sanitize else cleaned

    # 3. Match skills on the scoring representation to prevent identifier false positives
    match_results = match_skills(scoring_text if sanitize else cleaned, requirements=requirements)

    # 4. Compute similarity
    if similarity_engine is not None:
        sim = similarity_engine.transform_text_similarity(scoring_text if sanitize else cleaned)
    else:
        cleaned_jd = clean_text(job_description)
        sim = calculate_similarity(cleaned_jd, scoring_text if sanitize else cleaned, sanitize=False)

    # 5. Calculate composite score
    score_card = calculate_resume_score(match_results, sim, weights=weights)
    score_card["candidate_id"] = candidate_id or ""
    score_card["cleaned_text"] = cleaned  # Original cleaned text preserved for human review
    score_card["scoring_text"] = scoring_text  # Sanitized scoring representation
    score_card["skill_match_results"] = match_results

    return score_card


def score_candidate_batch(
    job_description: str,
    candidates: list,
    weights: Optional[Dict[str, float]] = None,
    requirements: Optional[dict] = None,
    sanitize: bool = True
) -> list:
    """
    Score a batch of candidates using a shared corpus TF-IDF vectorizer.

    Guarantees that all candidate similarity values use the same vocabulary
    and IDF weights across the entire batch, and that personal identifiers
    cannot influence skill matching or similarity scores.

    Preserves the original cleaned resume text for human review on each candidate.

    Args:
        job_description (str): Cleaned job description text.
        candidates (list): List of candidate dictionaries, each containing:
            - 'id': Candidate ID string
            - 'cleaned_text': Normalized resume text
            - 'name': Candidate name (optional)
            - 'skill_match_results': Output from Phase 7 match_skills (optional)
        weights (Optional[Dict[str, float]]): Custom weights dictionary.
        requirements (Optional[dict]): Requirements dictionary for skill matching.
        sanitize (bool): Whether to strip personal identifiers for scoring. Defaults to True.

    Returns:
        list: List of detailed score dictionaries corresponding to each candidate.
    """
    from src.similarity import TFIDFSimilarityEngine
    from src.skill_extractor import match_skills
    from src.text_cleaner import strip_personal_identifiers

    if not candidates:
        return []

    # Prepare scoring texts for all candidates
    prepared_candidates = []
    for c in candidates:
        c_copy = dict(c)
        cleaned = c_copy.get("cleaned_text", "")
        name = c_copy.get("name")
        if sanitize:
            c_copy["scoring_text"] = c_copy.get("scoring_text") or strip_personal_identifiers(cleaned, candidate_name=name)
        else:
            c_copy["scoring_text"] = cleaned
        prepared_candidates.append(c_copy)

    # Compute similarities across the entire shared corpus [JD + Resumes]
    scoring_resumes = [c["scoring_text"] for c in prepared_candidates]
    engine = TFIDFSimilarityEngine(job_description, scoring_resumes, sanitize=sanitize)
    similarities = engine.get_similarities()

    scored_candidates = []
    for candidate, sim in zip(prepared_candidates, similarities):
        # Determine skill match results:
        if "skill_match_results" in candidate and not (requirements is not None and sanitize):
            skill_results = candidate["skill_match_results"]
        else:
            skill_results = match_skills(
                candidate["scoring_text"] if sanitize else candidate["cleaned_text"],
                requirements=requirements
            )

        score_card = calculate_resume_score(
            skill_match_results=skill_results,
            cosine_similarity=sim,
            weights=weights
        )
        score_card["candidate_id"] = candidate.get("id", "")
        score_card["cleaned_text"] = candidate.get("cleaned_text", "")  # Preserved original text for human review
        score_card["scoring_text"] = candidate.get("scoring_text", "")  # Separate sanitized representation
        score_card["skill_match_results"] = skill_results
        scored_candidates.append(score_card)

    return scored_candidates

