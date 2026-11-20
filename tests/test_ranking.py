"""
Unit Tests for Candidate Ranking Module
Author: Akash Das
Project: Automated Resume Screening Tool

Comprehensive automated test suite validating:
- Descending composite-score ordering
- Sequential 1-based rank positions
- Standardized 4-level tie-breaking hierarchy (Required -> Preferred -> Similarity -> Candidate ID)
- Deterministic output across repeated runs
- Threshold boundaries (High Match, Moderate Match, Low Match)
- Custom threshold configuration and validation
- Error handling (empty list, malformed records, missing scores, out-of-bounds)
- Preservation of input records (immutability)
- End-to-end integration ranking across all 10 synthetic candidates
"""

import copy
from pathlib import Path
import pytest

from src.resume_parser import extract_text
from src.text_cleaner import clean_text
from src.scoring import score_candidate_batch
from src.skill_extractor import load_requirements
from src.ranking import (
    rank_candidates,
    assign_review_category,
    validate_thresholds,
    DEFAULT_THRESHOLDS,
    REVIEW_CATEGORY_HIGH,
    REVIEW_CATEGORY_MODERATE,
    REVIEW_CATEGORY_LOW,
)

SAMPLE_RESUMES_DIR = Path(__file__).parent.parent / "data" / "sample_resumes"
JOB_DESC_PATH = Path(__file__).parent.parent / "data" / "job_descriptions" / "junior_data_analyst.txt"
REQUIREMENTS_PATH = (
    Path(__file__).parent.parent / "data" / "job_descriptions" / "junior_data_analyst_requirements.json"
)


# --------------------------------------------------------------------------
# 1. Review Category Threshold Validation and Assignment
# --------------------------------------------------------------------------
def test_default_threshold_boundaries():
    """Verify exact boundary classifications with default thresholds (High >= 70, Mod >= 40, Low < 40)."""
    # High Match boundary
    assert assign_review_category(100.0) == REVIEW_CATEGORY_HIGH
    assert assign_review_category(70.0) == REVIEW_CATEGORY_HIGH
    assert assign_review_category(69.9999) == REVIEW_CATEGORY_MODERATE

    # Moderate Match boundaries
    assert assign_review_category(55.0) == REVIEW_CATEGORY_MODERATE
    assert assign_review_category(40.0) == REVIEW_CATEGORY_MODERATE
    assert assign_review_category(39.9999) == REVIEW_CATEGORY_LOW

    # Low Match boundary
    assert assign_review_category(20.0) == REVIEW_CATEGORY_LOW
    assert assign_review_category(0.0) == REVIEW_CATEGORY_LOW


def test_custom_threshold_configuration():
    """Verify custom thresholds correctly re-partition categories."""
    custom = {"high": 80.0, "moderate": 50.0}
    assert assign_review_category(85.0, thresholds=custom) == REVIEW_CATEGORY_HIGH
    assert assign_review_category(80.0, thresholds=custom) == REVIEW_CATEGORY_HIGH
    assert assign_review_category(79.9, thresholds=custom) == REVIEW_CATEGORY_MODERATE
    assert assign_review_category(50.0, thresholds=custom) == REVIEW_CATEGORY_MODERATE
    assert assign_review_category(49.9, thresholds=custom) == REVIEW_CATEGORY_LOW


def test_invalid_threshold_configurations():
    """Verify validate_thresholds rejects inverted, negative, out-of-range, or malformed configs."""
    # Moderate >= High
    with pytest.raises(ValueError, match="must be strictly less than 'high'"):
        validate_thresholds({"high": 60.0, "moderate": 60.0})

    with pytest.raises(ValueError, match="must be strictly less than 'high'"):
        validate_thresholds({"high": 50.0, "moderate": 70.0})

    # Out of bounds [0, 100]
    with pytest.raises(ValueError, match="between 0.0 and 100.0"):
        validate_thresholds({"high": 105.0, "moderate": 40.0})

    with pytest.raises(ValueError, match="between 0.0 and 100.0"):
        validate_thresholds({"high": 70.0, "moderate": -5.0})

    # Missing keys
    with pytest.raises(ValueError, match="missing required keys"):
        validate_thresholds({"high": 70.0})

    # Non-dict
    with pytest.raises(TypeError, match="must be a dictionary"):
        validate_thresholds(["high", 70.0])  # type: ignore

    # Non-numeric
    with pytest.raises(TypeError, match="must be numeric"):
        validate_thresholds({"high": "70", "moderate": 40.0})  # type: ignore


def test_invalid_score_input_raises_error():
    """Verify assign_review_category rejects non-numeric or out-of-bounds scores."""
    with pytest.raises(TypeError, match="must be a numeric value"):
        assign_review_category("85.0")  # type: ignore

    with pytest.raises(TypeError, match="must be a numeric value"):
        assign_review_category(True)  # bool is subclass of int

    with pytest.raises(ValueError, match="between 0.0 and 100.0"):
        assign_review_category(-1.0)

    with pytest.raises(ValueError, match="between 0.0 and 100.0"):
        assign_review_category(100.1)


# --------------------------------------------------------------------------
# 2. Basic Candidate Ranking and Ordering
# --------------------------------------------------------------------------
def test_descending_composite_score_ordering():
    """Verify candidates are sorted strictly descending by composite score."""
    candidates = [
        {"candidate_id": "CAND-001", "composite_score": 45.0, "required_coverage": 0.5, "preferred_coverage": 0.0, "cosine_similarity": 0.1},
        {"candidate_id": "CAND-002", "composite_score": 85.0, "required_coverage": 0.9, "preferred_coverage": 0.5, "cosine_similarity": 0.3},
        {"candidate_id": "CAND-003", "composite_score": 25.0, "required_coverage": 0.2, "preferred_coverage": 0.0, "cosine_similarity": 0.05},
        {"candidate_id": "CAND-004", "composite_score": 65.0, "required_coverage": 0.6, "preferred_coverage": 0.3, "cosine_similarity": 0.2},
    ]

    ranked = rank_candidates(candidates)
    assert len(ranked) == 4

    scores = [c["composite_score"] for c in ranked]
    assert scores == [85.0, 65.0, 45.0, 25.0]

    ids = [c["candidate_id"] for c in ranked]
    assert ids == ["CAND-002", "CAND-004", "CAND-001", "CAND-003"]


def test_sequential_rank_positions():
    """Verify sequential, 1-indexed rank numbers are assigned."""
    candidates = [
        {"candidate_id": "CAND-A", "composite_score": 60.0},
        {"candidate_id": "CAND-B", "composite_score": 80.0},
        {"candidate_id": "CAND-C", "composite_score": 40.0},
    ]

    ranked = rank_candidates(candidates)
    assert [c["rank"] for c in ranked] == [1, 2, 3]


def test_deterministic_results_across_repeated_runs():
    """Verify ranking produces identical output across multiple runs."""
    candidates = [
        {"candidate_id": "CAND-001", "composite_score": 50.0, "required_coverage": 0.5},
        {"candidate_id": "CAND-002", "composite_score": 75.0, "required_coverage": 0.8},
        {"candidate_id": "CAND-003", "composite_score": 50.0, "required_coverage": 0.5},
    ]

    run1 = rank_candidates(candidates)
    run2 = rank_candidates(candidates)
    run3 = rank_candidates(candidates)

    assert run1 == run2 == run3


# --------------------------------------------------------------------------
# 3. Standardized Tie-Breaking Hierarchy Tests
# --------------------------------------------------------------------------
def test_tie_breaking_level_1_required_coverage():
    """
    Tie-breaker 1: When composite scores are equal,
    the candidate with higher required skill coverage ranks higher.
    """
    candidates = [
        {
            "candidate_id": "CAND-LOW-REQ",
            "composite_score": 50.0,
            "required_coverage": 0.40,
            "preferred_coverage": 0.80,
            "cosine_similarity": 0.20,
        },
        {
            "candidate_id": "CAND-HIGH-REQ",
            "composite_score": 50.0,
            "required_coverage": 0.60,
            "preferred_coverage": 0.20,
            "cosine_similarity": 0.10,
        },
    ]

    ranked = rank_candidates(candidates)
    assert ranked[0]["candidate_id"] == "CAND-HIGH-REQ"
    assert ranked[1]["candidate_id"] == "CAND-LOW-REQ"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2


def test_tie_breaking_level_2_preferred_coverage():
    """
    Tie-breaker 2: When composite score and required coverage are equal,
    the candidate with higher preferred skill coverage ranks higher.
    """
    candidates = [
        {
            "candidate_id": "CAND-LOW-PREF",
            "composite_score": 50.0,
            "required_coverage": 0.50,
            "preferred_coverage": 0.20,
            "cosine_similarity": 0.30,
        },
        {
            "candidate_id": "CAND-HIGH-PREF",
            "composite_score": 50.0,
            "required_coverage": 0.50,
            "preferred_coverage": 0.60,
            "cosine_similarity": 0.10,
        },
    ]

    ranked = rank_candidates(candidates)
    assert ranked[0]["candidate_id"] == "CAND-HIGH-PREF"
    assert ranked[1]["candidate_id"] == "CAND-LOW-PREF"


def test_tie_breaking_level_3_cosine_similarity():
    """
    Tie-breaker 3: When composite score, required coverage, and preferred coverage are equal,
    the candidate with higher TF-IDF cosine similarity ranks higher.
    """
    candidates = [
        {
            "candidate_id": "CAND-LOW-SIM",
            "composite_score": 50.0,
            "required_coverage": 0.50,
            "preferred_coverage": 0.30,
            "cosine_similarity": 0.15,
        },
        {
            "candidate_id": "CAND-HIGH-SIM",
            "composite_score": 50.0,
            "required_coverage": 0.50,
            "preferred_coverage": 0.30,
            "cosine_similarity": 0.28,
        },
    ]

    ranked = rank_candidates(candidates)
    assert ranked[0]["candidate_id"] == "CAND-HIGH-SIM"
    assert ranked[1]["candidate_id"] == "CAND-LOW-SIM"


def test_tie_breaking_level_4_candidate_id_ascending():
    """
    Tie-breaker 4: When all score metrics are equal,
    candidate ID in ascending alphabetical / numerical order determines order.
    """
    candidates = [
        {
            "candidate_id": "CAND-005",
            "composite_score": 50.0,
            "required_coverage": 0.50,
            "preferred_coverage": 0.30,
            "cosine_similarity": 0.20,
        },
        {
            "candidate_id": "CAND-001",
            "composite_score": 50.0,
            "required_coverage": 0.50,
            "preferred_coverage": 0.30,
            "cosine_similarity": 0.20,
        },
        {
            "candidate_id": "CAND-003",
            "composite_score": 50.0,
            "required_coverage": 0.50,
            "preferred_coverage": 0.30,
            "cosine_similarity": 0.20,
        },
    ]

    ranked = rank_candidates(candidates)
    assert [c["candidate_id"] for c in ranked] == ["CAND-001", "CAND-003", "CAND-005"]


def test_sorting_precision_difference_less_than_one_millionth():
    """
    Verify that candidates differing in composite score by < 0.000001
    are ranked strictly by their actual composite score, without rounding.
    The candidate with the genuinely higher composite score must rank first,
    even when lower-level tie-breakers favor the lower-scoring candidate.
    """
    candidates = [
        {
            "candidate_id": "CAND-LOWER-SCORE",
            "composite_score": 50.0000001,
            "required_coverage": 0.90,  # Favors lower score candidate
            "preferred_coverage": 0.80,
            "cosine_similarity": 0.50,
        },
        {
            "candidate_id": "CAND-HIGHER-SCORE",
            "composite_score": 50.0000004,
            "required_coverage": 0.20,
            "preferred_coverage": 0.10,
            "cosine_similarity": 0.05,
        },
    ]
    ranked = rank_candidates(candidates)
    assert ranked[0]["candidate_id"] == "CAND-HIGHER-SCORE"
    assert ranked[1]["candidate_id"] == "CAND-LOWER-SCORE"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2


def test_near_equal_sub_metric_tie_breaking_precision():
    """
    Verify that when composite scores are exactly equal:
    1. Near-equal required coverage (< 0.000001 diff) breaks ties by actual value.
    2. Near-equal preferred coverage (< 0.000001 diff) breaks ties by actual value.
    3. Near-equal cosine similarity (< 0.000001 diff) breaks ties by actual value.
    """
    # 1. Required coverage sub-millionth diff
    req_candidates = [
        {"candidate_id": "CAND-REQ-B", "composite_score": 50.0, "required_coverage": 0.5000001, "preferred_coverage": 0.9, "cosine_similarity": 0.9},
        {"candidate_id": "CAND-REQ-A", "composite_score": 50.0, "required_coverage": 0.5000004, "preferred_coverage": 0.1, "cosine_similarity": 0.1},
    ]
    ranked_req = rank_candidates(req_candidates)
    assert ranked_req[0]["candidate_id"] == "CAND-REQ-A"
    assert ranked_req[1]["candidate_id"] == "CAND-REQ-B"

    # 2. Preferred coverage sub-millionth diff
    pref_candidates = [
        {"candidate_id": "CAND-PREF-B", "composite_score": 50.0, "required_coverage": 0.5, "preferred_coverage": 0.3000001, "cosine_similarity": 0.9},
        {"candidate_id": "CAND-PREF-A", "composite_score": 50.0, "required_coverage": 0.5, "preferred_coverage": 0.3000004, "cosine_similarity": 0.1},
    ]
    ranked_pref = rank_candidates(pref_candidates)
    assert ranked_pref[0]["candidate_id"] == "CAND-PREF-A"
    assert ranked_pref[1]["candidate_id"] == "CAND-PREF-B"

    # 3. Cosine similarity sub-millionth diff
    sim_candidates = [
        {"candidate_id": "CAND-SIM-B", "composite_score": 50.0, "required_coverage": 0.5, "preferred_coverage": 0.3, "cosine_similarity": 0.2000001},
        {"candidate_id": "CAND-SIM-A", "composite_score": 50.0, "required_coverage": 0.5, "preferred_coverage": 0.3, "cosine_similarity": 0.2000004},
    ]
    ranked_sim = rank_candidates(sim_candidates)
    assert ranked_sim[0]["candidate_id"] == "CAND-SIM-A"
    assert ranked_sim[1]["candidate_id"] == "CAND-SIM-B"


def test_exact_equality_all_numerical_metrics_invokes_candidate_id_tie_break():
    """
    Verify that exact equality across all numerical metrics invokes
    candidate ID in ascending order as the definitive tie-breaker.
    """
    candidates = [
        {"candidate_id": "CAND-009", "composite_score": 50.0, "required_coverage": 0.5, "preferred_coverage": 0.3, "cosine_similarity": 0.2},
        {"candidate_id": "CAND-002", "composite_score": 50.0, "required_coverage": 0.5, "preferred_coverage": 0.3, "cosine_similarity": 0.2},
        {"candidate_id": "CAND-004", "composite_score": 50.0, "required_coverage": 0.5, "preferred_coverage": 0.3, "cosine_similarity": 0.2},
    ]
    ranked = rank_candidates(candidates)
    assert [c["candidate_id"] for c in ranked] == ["CAND-002", "CAND-004", "CAND-009"]


# --------------------------------------------------------------------------
# 4. Input Immutability and Error Handling
# --------------------------------------------------------------------------
def test_preservation_of_input_records():
    """Verify ranking function does not mutate or modify original input dictionaries."""
    original_cards = [
        {"candidate_id": "CAND-001", "composite_score": 60.0},
        {"candidate_id": "CAND-002", "composite_score": 80.0},
    ]
    cards_snapshot = copy.deepcopy(original_cards)

    ranked = rank_candidates(original_cards)

    # Input dictionaries must remain unchanged
    assert original_cards == cards_snapshot
    assert "rank" not in original_cards[0]
    assert "review_category" not in original_cards[0]

    # Output records contain rank annotations
    assert "rank" in ranked[0]
    assert "review_category" in ranked[0]


def test_empty_candidate_input():
    """Verify empty candidate list returns empty list cleanly."""
    assert rank_candidates([]) == []


def test_invalid_candidate_list_type():
    """Verify TypeError raised if candidate_cards is not a list."""
    with pytest.raises(TypeError, match="candidate_cards must be a list"):
        rank_candidates("not a list")  # type: ignore

    with pytest.raises(TypeError, match="Item at index 0 is not a dictionary"):
        rank_candidates(["not a dict"])  # type: ignore


def test_missing_or_invalid_candidate_metrics():
    """Verify ValueError or TypeError raised for missing or corrupt candidate metrics."""
    # Missing candidate_id
    with pytest.raises(ValueError, match="missing valid 'candidate_id'"):
        rank_candidates([{"composite_score": 50.0}])

    # Missing composite_score
    with pytest.raises(ValueError, match="missing required 'composite_score'"):
        rank_candidates([{"candidate_id": "CAND-001"}])

    # Non-numeric composite_score
    with pytest.raises(TypeError, match="composite_score must be numeric"):
        rank_candidates([{"candidate_id": "CAND-001", "composite_score": "75.0"}])

    # Out of range composite_score
    with pytest.raises(ValueError, match="out of range"):
        rank_candidates([{"candidate_id": "CAND-001", "composite_score": 105.0}])


def test_duplicate_candidate_id_validation_raises_error():
    """
    Verify that duplicate candidate IDs in the ranking input raise ValueError
    to prevent ambiguous ranking output, rather than silently merging or dropping.
    """
    candidates = [
        {"candidate_id": "CAND-001", "composite_score": 60.0},
        {"candidate_id": "CAND-001", "composite_score": 75.0},
    ]
    with pytest.raises(ValueError, match="Duplicate candidate ID detected"):
        rank_candidates(candidates)


# --------------------------------------------------------------------------
# 5. Integration: Ranking All 10 Real Synthetic Resumes
# --------------------------------------------------------------------------
def test_ranking_all_ten_synthetic_candidates():
    """
    Verify complete pipeline integration:
    Score all 10 synthetic candidates against Junior Data Analyst benchmark,
    pass records into rank_candidates, and verify complete, valid ranking.
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

    # Score candidates using Phase 8 shared-corpus scoring
    scored = score_candidate_batch(cleaned_jd, candidate_records, requirements=requirements, sanitize=True)
    assert len(scored) == 10

    # Rank candidates using Phase 9 ranking
    ranked = rank_candidates(scored)
    assert len(ranked) == 10

    # Verify ranks are sequential 1..10
    assert [c["rank"] for c in ranked] == list(range(1, 11))

    # Verify all candidate IDs appear exactly once
    ranked_ids = [c["candidate_id"] for c in ranked]
    assert len(set(ranked_ids)) == 10
    expected_ids = {f"CAND-{i:03d}" for i in range(1, 11)}
    assert set(ranked_ids) == expected_ids

    # Verify descending score order
    scores = [c["composite_score"] for c in ranked]
    assert scores == sorted(scores, reverse=True)

    # Verify review categories assigned properly
    for c in ranked:
        assert c["review_category"] in {
            REVIEW_CATEGORY_HIGH,
            REVIEW_CATEGORY_MODERATE,
            REVIEW_CATEGORY_LOW,
        }
        if c["composite_score"] >= 70.0:
            assert c["review_category"] == REVIEW_CATEGORY_HIGH
        elif c["composite_score"] >= 40.0:
            assert c["review_category"] == REVIEW_CATEGORY_MODERATE
        else:
            assert c["review_category"] == REVIEW_CATEGORY_LOW
