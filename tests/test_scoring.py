"""
Unit Tests for Resume Scoring and Similarity Module
Author: Akash Das
Project: Automated Resume Screening Tool

Comprehensive automated test suite validating TF-IDF cosine similarity bounds,
required & preferred skill coverage ratios, composite scoring calculations,
custom weights, edge cases, and end-to-end scoring across all 10 synthetic resumes.
"""

from pathlib import Path
import pytest

from src.resume_parser import extract_text
from src.text_cleaner import clean_text, strip_personal_identifiers
from src.skill_extractor import match_skills, load_requirements
from src.similarity import (
    calculate_similarity,
    vectorize_documents,
    compute_corpus_similarities,
    TFIDFSimilarityEngine,
)
from src.scoring import (
    calculate_resume_score,
    validate_weights,
    DEFAULT_WEIGHTS,
    score_candidate_batch,
    score_candidate,
)

SAMPLE_RESUMES_DIR = Path(__file__).parent.parent / "data" / "sample_resumes"
JOB_DESC_PATH = Path(__file__).parent.parent / "data" / "job_descriptions" / "junior_data_analyst.txt"
REQUIREMENTS_PATH = (
    Path(__file__).parent.parent / "data" / "job_descriptions" / "junior_data_analyst_requirements.json"
)


@pytest.fixture
def sample_match_results():
    """Fixture providing mock skill match results."""
    return {
        "required": {
            "matched": [
                {"canonical_name": "Python"},
                {"canonical_name": "SQL"},
                {"canonical_name": "Pandas"},
            ],
            "missing": [
                {"canonical_name": "Data Cleaning"},
                {"canonical_name": "Data Analysis"},
                {"canonical_name": "Basic Statistics"},
            ],
        },
        "preferred": {
            "matched": [
                {"canonical_name": "NumPy"},
                {"canonical_name": "Excel"},
            ],
            "missing": [
                {"canonical_name": "Scikit-learn"},
                {"canonical_name": "Machine Learning"},
                {"canonical_name": "Power BI"},
                {"canonical_name": "Tableau"},
            ],
        },
    }


# --------------------------------------------------------------------------
# 1. Similarity Calculation Tests
# --------------------------------------------------------------------------
def test_similarity_identical_text():
    """Verify identical text produces a cosine similarity of 1.0."""
    text = "junior data analyst with python and sql expertise"
    sim = calculate_similarity(text, text)
    assert pytest.approx(sim, 0.0001) == 1.0


def test_similarity_empty_inputs():
    """Verify empty or whitespace-only inputs produce 0.0 similarity."""
    assert calculate_similarity("", "python sql") == 0.0
    assert calculate_similarity("python sql", "") == 0.0
    assert calculate_similarity("   \n\t ", "   ") == 0.0


def test_similarity_unrelated_text():
    """Verify completely disjoint vocabularies produce 0.0 similarity."""
    jd = "python sql pandas database data analytics"
    resume = "culinary chef baking pastry recipes kitchen cooking"
    assert calculate_similarity(jd, resume) == 0.0


def test_similarity_bounds_and_types():
    """Verify calculate_similarity strictly returns float in [0.0, 1.0]."""
    sim = calculate_similarity("python developer", "python machine learning")
    assert isinstance(sim, float)
    assert 0.0 <= sim <= 1.0

    with pytest.raises(TypeError):
        calculate_similarity(None, "text")  # type: ignore

    with pytest.raises(TypeError):
        calculate_similarity("text", 123)  # type: ignore


def test_vectorize_documents():
    """Verify vectorize_documents helper returns vectorizer and matrix."""
    docs = ["doc one python", "doc two sql"]
    vec, mat = vectorize_documents(docs)
    assert mat.shape == (2, len(vec.get_feature_names_out()))


# --------------------------------------------------------------------------
# 2. Coverage and Composite Scoring Tests
# --------------------------------------------------------------------------
def test_correct_coverage_and_score(sample_match_results):
    """
    Verify coverage ratios and composite score:
    - Required: 3 / 6 = 0.5 -> 0.5 * 70 = 35.0
    - Preferred: 2 / 6 = 0.333333 -> 0.333333 * 10 = 3.333333
    - Similarity: 0.25 -> 0.25 * 20 = 5.0
    - Total = 35.0 + 3.333333 + 5.0 = 43.333333
    """
    res = calculate_resume_score(sample_match_results, cosine_similarity=0.25)

    assert pytest.approx(res["required_skills"]["coverage"], 0.0001) == 0.5
    assert pytest.approx(res["required_skills"]["weighted_score"], 0.0001) == 35.0

    assert pytest.approx(res["preferred_skills"]["coverage"], 0.0001) == 2 / 6
    assert pytest.approx(res["preferred_skills"]["weighted_score"], 0.0001) == (2 / 6) * 10.0

    assert pytest.approx(res["similarity"]["weighted_score"], 0.0001) == 5.0
    expected_composite = 35.0 + ((2 / 6) * 10.0) + 5.0
    assert pytest.approx(res["composite_score"], 0.0001) == expected_composite


def test_all_skills_matched_and_perfect_similarity():
    """Verify 100% match produces 100.0 composite score."""
    perfect_results = {
        "required": {"matched": [{"canonical_name": f"R{i}"} for i in range(6)], "missing": []},
        "preferred": {"matched": [{"canonical_name": f"P{i}"} for i in range(6)], "missing": []},
    }
    res = calculate_resume_score(perfect_results, cosine_similarity=1.0)
    assert pytest.approx(res["composite_score"], 0.0001) == 100.0


def test_zero_skills_matched_and_zero_similarity():
    """Verify zero skills matched produces 0.0 composite score."""
    zero_results = {
        "required": {"matched": [], "missing": [{"canonical_name": f"R{i}"} for i in range(6)]},
        "preferred": {"matched": [], "missing": [{"canonical_name": f"P{i}"} for i in range(6)]},
    }
    res = calculate_resume_score(zero_results, cosine_similarity=0.0)
    assert pytest.approx(res["composite_score"], 0.0001) == 0.0


def test_custom_weight_configuration(sample_match_results):
    """Verify custom weights summing to 100 are applied correctly."""
    custom_weights = {"required": 50.0, "preferred": 20.0, "similarity": 30.0}
    res = calculate_resume_score(sample_match_results, cosine_similarity=0.5, weights=custom_weights)

    # Required: 0.5 * 50 = 25.0
    # Preferred: (2/6) * 20 = 6.6667
    # Similarity: 0.5 * 30 = 15.0
    # Composite: 25.0 + 6.6667 + 15.0 = 46.6667
    expected = 25.0 + ((2 / 6) * 20.0) + 15.0
    assert pytest.approx(res["composite_score"], 0.0001) == expected


def test_invalid_weights_validation():
    """Verify validate_weights raises ValueError on non-100 sum or negative weights."""
    # Sum != 100
    with pytest.raises(ValueError, match="Weights must sum to 100.0"):
        validate_weights({"required": 50.0, "preferred": 20.0, "similarity": 20.0})

    # Negative weight
    with pytest.raises(ValueError, match="cannot be negative"):
        validate_weights({"required": 110.0, "preferred": -10.0, "similarity": 0.0})

    # Missing key
    with pytest.raises(ValueError, match="missing required keys"):
        validate_weights({"required": 70.0, "preferred": 30.0})


def test_zero_required_or_preferred_skills_handled_safely():
    """Verify division by zero is safely avoided if no skills are defined in category."""
    empty_category_results = {
        "required": {"matched": [], "missing": []},
        "preferred": {"matched": [{"canonical_name": "Excel"}], "missing": []},
    }
    res = calculate_resume_score(empty_category_results, cosine_similarity=0.5)
    assert res["required_skills"]["coverage"] == 0.0
    assert res["preferred_skills"]["coverage"] == 1.0


def test_invalid_similarity_bounds_raises_valueerror(sample_match_results):
    """Verify ValueError is raised if similarity < 0 or > 1."""
    with pytest.raises(ValueError, match="cosine_similarity must be between 0.0 and 1.0"):
        calculate_resume_score(sample_match_results, cosine_similarity=-0.1)

    with pytest.raises(ValueError, match="cosine_similarity must be between 0.0 and 1.0"):
        calculate_resume_score(sample_match_results, cosine_similarity=1.1)


# --------------------------------------------------------------------------
# 3. End-to-End Pipeline Scoring Across All 10 Resumes
# --------------------------------------------------------------------------
def test_end_to_end_scoring_all_ten_resumes():
    """
    Verify complete pipeline (extraction -> cleaning -> matching -> similarity -> scoring)
    runs cleanly across all 10 synthetic candidate resumes.
    """
    assert JOB_DESC_PATH.exists()
    assert REQUIREMENTS_PATH.exists()

    raw_jd = JOB_DESC_PATH.read_text(encoding="utf-8")
    cleaned_jd = clean_text(raw_jd)
    requirements = load_requirements(REQUIREMENTS_PATH)

    resume_files = sorted([f for f in SAMPLE_RESUMES_DIR.iterdir() if f.is_file() and f.name != ".gitkeep"])
    assert len(resume_files) == 10

    scores = []
    for f in resume_files:
        raw_resume = extract_text(f)
        cleaned_resume = clean_text(raw_resume)

        # Phase 7: Match skills
        match_result = match_skills(cleaned_resume, requirements)

        # Phase 8: Compute similarity & score
        sim = calculate_similarity(cleaned_jd, cleaned_resume)
        score_card = calculate_resume_score(match_result, sim)

        score = score_card["composite_score"]
        assert 0.0 <= score <= 100.0
        assert 0.0 <= sim <= 1.0
        scores.append(score)

    # Confirm candidate diversity: scores must not all be identical
    assert len(set(scores)) > 5


# --------------------------------------------------------------------------
# 4. TF-IDF Common Corpus Consistency Regression Tests
# --------------------------------------------------------------------------
def test_tfidf_common_corpus_fitted_once():
    """
    Verify TF-IDF vectorizer is fitted once across the shared corpus [JD + All Resumes]
    and computes consistent similarities using the exact same vocabulary & IDF weights.
    """
    jd = "junior data analyst with python sql pandas data cleaning"
    resumes = [
        "data analyst proficient in python and sql",
        "backend developer skilled in django and rest api",
        "business intelligence reporting with power bi and excel",
    ]

    engine = TFIDFSimilarityEngine(jd, resumes)
    sims = engine.get_similarities()

    assert len(sims) == len(resumes)
    for s in sims:
        assert 0.0 <= s <= 1.0

    # Ensure all resumes are represented in the same feature space
    feature_count = len(engine.vectorizer.get_feature_names_out())
    assert engine.jd_vector.shape == (1, feature_count)
    assert engine.resume_vectors.shape == (len(resumes), feature_count)


def test_tfidf_deterministic_results():
    """Verify repeated runs on the same corpus produce identical similarity values."""
    jd = "junior data analyst python sql pandas"
    resumes = ["candidate one python sql", "candidate two java spring"]

    sims_run1 = compute_corpus_similarities(jd, resumes)
    sims_run2 = compute_corpus_similarities(jd, resumes)

    assert sims_run1 == sims_run2


def test_score_candidate_batch_utility():
    """Verify score_candidate_batch scores all candidates using the common corpus."""
    jd = "data analyst python sql pandas"
    candidates = [
        {
            "id": "CAND-001",
            "cleaned_text": "data analyst with python and sql",
            "skill_match_results": {
                "required": {"matched": [{"canonical_name": "Python"}, {"canonical_name": "SQL"}], "missing": []},
                "preferred": {"matched": [], "missing": []},
            },
        },
        {
            "id": "CAND-002",
            "cleaned_text": "frontend developer react javascript",
            "skill_match_results": {
                "required": {"matched": [], "missing": [{"canonical_name": "Python"}]},
                "preferred": {"matched": [], "missing": []},
            },
        },
    ]

    scored = score_candidate_batch(jd, candidates)
    assert len(scored) == 2
    assert scored[0]["candidate_id"] == "CAND-001"
    assert scored[1]["candidate_id"] == "CAND-002"
    assert scored[0]["composite_score"] > scored[1]["composite_score"]


# --------------------------------------------------------------------------
# 5. Personal-Identifier Invariance Regression Tests
# --------------------------------------------------------------------------
def test_name_change_invariance():
    """Verify that changing a candidate's name does not alter their similarity score."""
    jd = "junior data analyst with python and sql data cleaning"
    resume_template = """{name}
candidate id cand-001 data analyst
email test.user@example.com phone 1-555-0101 location fictional city
professional summary
experienced data analyst proficient in python sql pandas and data cleaning
work experience
built data pipelines in python and sql"""

    resume_alex = resume_template.format(name="aarav sharma")
    resume_john = resume_template.format(name="johnathan doe")
    resume_mary = resume_template.format(name="mary jane watson")

    sim_alex = calculate_similarity(jd, resume_alex, sanitize=True)
    sim_john = calculate_similarity(jd, resume_john, sanitize=True)
    sim_mary = calculate_similarity(jd, resume_mary, sanitize=True)

    assert pytest.approx(sim_alex, 1e-6) == sim_john
    assert pytest.approx(sim_john, 1e-6) == sim_mary


def test_email_and_phone_change_invariance():
    """Verify that changing email, phone number, or location does not alter similarity."""
    jd = "junior data analyst with python sql pandas"
    base_resume = """candidate id cand-001 data analyst
email {email} phone {phone} location {location}
professional summary
proficient in python sql and pandas data manipulation"""

    resume_1 = base_resume.format(email="user1@alpha.com", phone="1-555-0101", location="city one")
    resume_2 = base_resume.format(email="candidate99@beta.org", phone="+1 (800) 555-9999", location="metro two")

    sim_1 = calculate_similarity(jd, resume_1, sanitize=True)
    sim_2 = calculate_similarity(jd, resume_2, sanitize=True)

    assert pytest.approx(sim_1, 1e-6) == sim_2


def test_technical_content_preserved_after_sanitization():
    """Verify strip_personal_identifiers retains technical skills and experience."""
    raw = """aarav sharma
candidate id cand-001 data analyst
email aarav.sharma@example.com phone 1-555-0101 location fictional city
professional summary
proficient in python, sql, pandas, numpy, and scikit-learn.
experience
built etl pipelines with postgresql and docker."""

    cleaned = clean_text(raw)
    sanitized = strip_personal_identifiers(cleaned, "aarav sharma")

    # Personal identifiers removed
    assert "aarav" not in sanitized
    assert "sharma" not in sanitized
    assert "example" not in sanitized
    assert "555" not in sanitized
    assert "cand-001" not in sanitized

    # Technical content preserved
    for token in ["python", "sql", "pandas", "numpy", "scikit-learn", "postgresql", "docker"]:
        assert token in sanitized, f"Technical token '{token}' unexpectedly removed by sanitization"


def test_composite_score_identifier_invariance_synthetic_candidate():
    """
    Verify changing candidate name, email, and phone produces identical:
    - Required skill coverage
    - Preferred skill coverage
    - Matched and missing skill sets
    - TF-IDF textual similarity
    - Final composite score
    while preserving original cleaned text for human review.
    """
    raw_jd = JOB_DESC_PATH.read_text(encoding="utf-8")
    requirements = load_requirements(REQUIREMENTS_PATH)

    # Base candidate resume template preserving identical technical narrative
    resume_body = """candidate id cand-001 data analyst junior data scientist
professional summary
analytical and detail-oriented data analyst with 2 years of experience in data preprocessing exploratory data analysis
and relational databases proficient in python sql pandas and numpy for transforming raw data into actionable
business insights demonstrated ability to perform data cleaning statistical analysis and reporting
technical skills
programming python sql
libraries pandas numpy scikit-learn matplotlib seaborn
databases postgresql mysql
tools git jupyter notebook excel
work experience
junior data analyst fictional retail corp
performed data cleaning and data wrangling on large transaction datasets using pandas reducing missing value anomalies by 35%
executed complex sql queries in postgresql for sales trend aggregation and customer cohort analysis
applied basic statistics hypothesis testing and correlation analysis to identify product purchase patterns
projects
customer churn analysis python pandas sql
developed an exploratory data analysis workflow analyzing customer retention metrics across 50000 records
built data cleaning scripts in python to handle outliers and standardize categorical features
education
bachelor of science in statistics university of data science"""

    variant_original = f"aarav sharma\nemail aarav sharma sample example com phone 1-555-0101 location fictional city fc\n{resume_body}"
    variant_name = f"johnathan alexander doe\nemail aarav sharma sample example com phone 1-555-0101 location fictional city fc\n{resume_body}"
    variant_email = f"aarav sharma\nemail jdoe.different.analytics example org phone 1-555-0101 location fictional city fc\n{resume_body}"
    variant_phone = f"aarav sharma\nemail aarav sharma sample example com phone 1-800-555-9876 location fictional city fc\n{resume_body}"
    variant_tricky = f"dr dan py\nemail dan sql py sample example com phone 1-555-9999 location silicon valley ca\n{resume_body}"

    # Build similarity engine on corpus
    engine = TFIDFSimilarityEngine(raw_jd, [variant_original, variant_name, variant_email, variant_phone, variant_tricky], sanitize=True)

    score_orig = score_candidate(raw_jd, variant_original, candidate_id="CAND-001", candidate_name="aarav sharma", requirements=requirements, similarity_engine=engine)
    score_name = score_candidate(raw_jd, variant_name, candidate_id="CAND-001", candidate_name="johnathan alexander doe", requirements=requirements, similarity_engine=engine)
    score_email = score_candidate(raw_jd, variant_email, candidate_id="CAND-001", candidate_name="aarav sharma", requirements=requirements, similarity_engine=engine)
    score_phone = score_candidate(raw_jd, variant_phone, candidate_id="CAND-001", candidate_name="aarav sharma", requirements=requirements, similarity_engine=engine)
    score_tricky = score_candidate(raw_jd, variant_tricky, candidate_id="CAND-001", candidate_name="dr dan py", requirements=requirements, similarity_engine=engine)

    variants = [score_name, score_email, score_phone, score_tricky]

    for v in variants:
        # 1. Required coverage identical
        assert v["required_skills"]["coverage"] == score_orig["required_skills"]["coverage"]
        assert v["required_skills"]["matched_names"] == score_orig["required_skills"]["matched_names"]
        assert v["required_skills"]["missing_names"] == score_orig["required_skills"]["missing_names"]

        # 2. Preferred coverage identical
        assert v["preferred_skills"]["coverage"] == score_orig["preferred_skills"]["coverage"]
        assert v["preferred_skills"]["matched_names"] == score_orig["preferred_skills"]["matched_names"]
        assert v["preferred_skills"]["missing_names"] == score_orig["preferred_skills"]["missing_names"]

        # 3. TF-IDF similarity identical
        assert pytest.approx(v["similarity"]["cosine_similarity"], 1e-6) == score_orig["similarity"]["cosine_similarity"]

        # 4. Final composite score identical
        assert pytest.approx(v["composite_score"], 1e-6) == score_orig["composite_score"]

        # 5. Sanitized scoring text identical
        assert v["scoring_text"] == score_orig["scoring_text"]

    # 6. Verify original cleaned text is preserved and distinct for human review
    assert "johnathan alexander doe" in score_name["cleaned_text"]
    assert "dr dan py" in score_tricky["cleaned_text"]
    assert "aarav sharma" in score_orig["cleaned_text"]


def test_personal_identifiers_cannot_contribute_to_skill_matches():
    """
    Verify that names, emails, and contact details containing skill names
    (e.g., 'Dan Py', 'dan.sql.py@example.com') do not trigger false skill matches.
    """
    raw_jd = JOB_DESC_PATH.read_text(encoding="utf-8")
    requirements = load_requirements(REQUIREMENTS_PATH)

    # Resume has NO data analyst skills in the body (strictly Java backend)
    tricky_resume = """dr dan py
candidate id cand-999 backend developer
email dan sql py pandas sample example com phone 1-555-0199 location tech park tp
professional summary
experienced backend engineer specializing in enterprise systems using java and spring boot architecture
work experience
developed high-throughput microservices in java with spring boot framework
education
bachelor of technology in computer science"""

    score = score_candidate(
        job_description=raw_jd,
        resume_text=tricky_resume,
        candidate_id="CAND-999",
        candidate_name="dr dan py",
        requirements=requirements,
        sanitize=True
    )

    # Python, SQL, and Pandas from the header MUST NOT be matched
    matched_req = score["required_skills"]["matched_names"]
    matched_pref = score["preferred_skills"]["matched_names"]

    assert "Python" not in matched_req
    assert "SQL" not in matched_req
    assert "Pandas" not in matched_req
    assert len(matched_req) == 0
    assert len(matched_pref) == 0
    assert score["required_skills"]["coverage"] == 0.0

    # Genuine technical narrative is preserved in scoring text
    assert "java" in score["scoring_text"]
    assert "spring boot" in score["scoring_text"]


def test_batch_scoring_identifier_invariance_and_human_review_preservation():
    """
    Verify score_candidate_batch preserves original cleaned text for human review
    and produces invariant composite scores under identifier modifications.
    """
    raw_jd = JOB_DESC_PATH.read_text(encoding="utf-8")
    requirements = load_requirements(REQUIREMENTS_PATH)

    candidates_group_a = [
        {
            "id": "CAND-001",
            "name": "Aarav Sharma",
            "cleaned_text": """aarav sharma
email aarav.sharma@example.com phone 1-555-0101
professional summary
data analyst proficient in python sql pandas data cleaning and basic statistics""",
        },
        {
            "id": "CAND-002",
            "name": "Priya Nair",
            "cleaned_text": """priya nair
email priya.nair@example.com phone 1-555-0102
professional summary
backend engineer proficient in python and django""",
        },
    ]

    candidates_group_b = [
        {
            "id": "CAND-001",
            "name": "Alexander Montgomery",
            "cleaned_text": """alexander montgomery
email alex.montgomery.py.sql@corporate.org phone +44 20 7946 0999
professional summary
data analyst proficient in python sql pandas data cleaning and basic statistics""",
        },
        {
            "id": "CAND-002",
            "name": "Dan Py",
            "cleaned_text": """dan py
email dan.py.sql@test.org phone +1 (800) 555-0199
professional summary
backend engineer proficient in python and django""",
        },
    ]

    scored_a = score_candidate_batch(raw_jd, candidates_group_a, requirements=requirements, sanitize=True)
    scored_b = score_candidate_batch(raw_jd, candidates_group_b, requirements=requirements, sanitize=True)

    # Scores must match identically
    for a, b in zip(scored_a, scored_b):
        assert pytest.approx(a["composite_score"], 1e-6) == b["composite_score"]
        assert a["required_skills"]["coverage"] == b["required_skills"]["coverage"]
        assert a["preferred_skills"]["coverage"] == b["preferred_skills"]["coverage"]
        assert pytest.approx(a["similarity"]["cosine_similarity"], 1e-6) == b["similarity"]["cosine_similarity"]

        # Original cleaned text is preserved for human review
        assert a["cleaned_text"] != b["cleaned_text"]
        assert "aarav" in a["cleaned_text"] or "priya" in a["cleaned_text"]
        assert "alexander" in b["cleaned_text"] or "dan" in b["cleaned_text"]

