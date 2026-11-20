"""
Unit Tests for Data Visualization Module
Author: Akash Das
Project: Automated Resume Screening Tool

Comprehensive automated test suite validating:
- Generation and saving of all 6 required charts and 1 optional chart
- Publication-grade 300 DPI resolution and valid PNG format
- Batch generation orchestrator with custom and default directories
- Strict ranking order preservation (Rank 1 at the top)
- Coverage and metric representation accuracy
- Skill heatmap binary values matching ground-truth skill detection
- Strict privacy enforcement: candidate IDs only, no names/emails/phones
- Graceful edge-case handling for empty cohort and missing/malformed metrics
- Full pipeline integration across all 10 synthetic resumes
"""

from pathlib import Path
import pytest
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from src.resume_parser import extract_text
from src.text_cleaner import clean_text
from src.skill_extractor import load_requirements
from src.scoring import score_candidate_batch
from src.ranking import rank_candidates
from src.visualization import (
    plot_candidate_score_comparison,
    plot_score_distribution,
    plot_skill_coverage_comparison,
    plot_similarity_vs_composite_score,
    plot_review_category_distribution,
    plot_candidate_skill_heatmap,
    plot_required_skill_frequency,
    generate_all_visualizations,
    _parse_float,
    _safe_float,
    DEFAULT_REQUIRED_SKILLS,
    DEFAULT_FIGURES_DIR,
)

SAMPLE_RESUMES_DIR = Path(__file__).parent.parent / "data" / "sample_resumes"
JOB_DESC_PATH = Path(__file__).parent.parent / "data" / "job_descriptions" / "junior_data_analyst.txt"
REQUIREMENTS_PATH = (
    Path(__file__).parent.parent / "data" / "job_descriptions" / "junior_data_analyst_requirements.json"
)


@pytest.fixture
def sample_ranked_candidates():
    """Synthetic ranked candidate cohort for isolated visualization unit tests."""
    return [
        {
            "rank": 1,
            "candidate_id": "CAND-001",
            "candidate_name": "Aarav Sharma",
            "email": "aarav.sharma@email.com",
            "phone": "+91 98765 43210",
            "composite_score": 65.83,
            "required_coverage": 0.8333,
            "preferred_coverage": 0.1667,
            "cosine_similarity": 0.2916,
            "review_category": "Moderate Match",
            "required_skills": {
                "coverage": 0.8333,
                "matched_names": ["Python", "SQL", "Pandas", "Data Cleaning", "Data Analysis"],
                "missing_names": ["Basic Statistics"],
            },
            "preferred_skills": {
                "coverage": 0.1667,
                "matched_names": ["NumPy"],
                "missing_names": ["Scikit-learn", "Machine Learning", "Power BI", "Tableau", "Excel"],
            },
            "similarity": {"cosine_similarity": 0.2916},
        },
        {
            "rank": 2,
            "candidate_id": "CAND-010",
            "candidate_name": "Divya Sengupta",
            "email": "divya.sengupta@email.com",
            "phone": "+91 98765 43219",
            "composite_score": 62.45,
            "required_coverage": 0.8333,
            "preferred_coverage": 0.0000,
            "cosine_similarity": 0.2078,
            "review_category": "Moderate Match",
            "required_skills": {
                "coverage": 0.8333,
                "matched_names": ["Python", "SQL", "Pandas", "Data Analysis", "Basic Statistics"],
                "missing_names": ["Data Cleaning"],
            },
            "preferred_skills": {
                "coverage": 0.0000,
                "matched_names": [],
                "missing_names": ["NumPy", "Scikit-learn", "Machine Learning", "Power BI", "Tableau", "Excel"],
            },
            "similarity": {"cosine_similarity": 0.2078},
        },
        {
            "rank": 3,
            "candidate_id": "CAND-006",
            "candidate_name": "Ananya Deshmukh",
            "email": "ananya.deshmukh@email.com",
            "phone": "+91 98765 43215",
            "composite_score": 41.20,
            "required_coverage": 0.5000,
            "preferred_coverage": 0.3333,
            "cosine_similarity": 0.1435,
            "review_category": "Moderate Match",
            "required_skills": {
                "coverage": 0.5000,
                "matched_names": ["Python", "Pandas", "Basic Statistics"],
                "missing_names": ["SQL", "Data Cleaning", "Data Analysis"],
            },
            "preferred_skills": {
                "coverage": 0.3333,
                "matched_names": ["NumPy", "Machine Learning"],
                "missing_names": ["Scikit-learn", "Power BI", "Tableau", "Excel"],
            },
            "similarity": {"cosine_similarity": 0.1435},
        },
        {
            "rank": 4,
            "candidate_id": "CAND-007",
            "candidate_name": "Karan Verma",
            "email": "karan.verma@email.com",
            "phone": "+91 98765 43216",
            "composite_score": 0.32,
            "required_coverage": 0.0000,
            "preferred_coverage": 0.0000,
            "cosine_similarity": 0.0162,
            "review_category": "Low Match",
            "required_skills": {
                "coverage": 0.0000,
                "matched_names": [],
                "missing_names": ["Python", "SQL", "Pandas", "Data Cleaning", "Data Analysis", "Basic Statistics"],
            },
            "preferred_skills": {
                "coverage": 0.0000,
                "matched_names": [],
                "missing_names": ["NumPy", "Scikit-learn", "Machine Learning", "Power BI", "Tableau", "Excel"],
            },
            "similarity": {"cosine_similarity": 0.0162},
        },
    ]


def _verify_image_file(path: Path) -> None:
    """Helper to verify image file existence, non-emptiness, PNG format, and 300 DPI."""
    assert path.exists(), f"Image file {path} was not created."
    assert path.stat().st_size > 1000, f"Image file {path} is suspiciously small ({path.stat().st_size} bytes)."
    with Image.open(path) as img:
        assert img.format == "PNG", f"Expected PNG format, got {img.format}."
        dpi = img.info.get("dpi")
        if dpi is not None:
            # Pillow returns DPI as tuple of floats (e.g. (300.0, 300.0) or (299.9994, 299.9994))
            assert round(dpi[0]) == 300, f"Expected 300 DPI horizontal, got {dpi[0]}."
            assert round(dpi[1]) == 300, f"Expected 300 DPI vertical, got {dpi[1]}."


# --------------------------------------------------------------------------
# 1. Individual Plot Generation Tests
# --------------------------------------------------------------------------
def test_plot_candidate_score_comparison(tmp_path, sample_ranked_candidates):
    """Verify horizontal bar chart generates valid 300 DPI PNG with Rank 1 at top."""
    fig = plot_candidate_score_comparison(sample_ranked_candidates, output_dir=tmp_path)
    assert isinstance(fig, plt.Figure)
    assert fig.dpi == 300
    target_path = tmp_path / "candidate_score_comparison.png"
    _verify_image_file(target_path)
    plt.close(fig)


def test_plot_score_distribution(tmp_path, sample_ranked_candidates):
    """Verify composite score distribution histogram generates valid 300 DPI PNG."""
    fig = plot_score_distribution(sample_ranked_candidates, output_dir=tmp_path)
    assert isinstance(fig, plt.Figure)
    assert fig.dpi == 300
    target_path = tmp_path / "score_distribution.png"
    _verify_image_file(target_path)
    plt.close(fig)


def test_plot_skill_coverage_comparison(tmp_path, sample_ranked_candidates):
    """Verify grouped bar chart comparing required & preferred skill coverage generates valid 300 DPI PNG."""
    fig = plot_skill_coverage_comparison(sample_ranked_candidates, output_dir=tmp_path)
    assert isinstance(fig, plt.Figure)
    assert fig.dpi == 300
    target_path = tmp_path / "skill_coverage_comparison.png"
    _verify_image_file(target_path)
    plt.close(fig)


def test_plot_similarity_vs_composite_score(tmp_path, sample_ranked_candidates):
    """Verify annotated scatter plot comparing TF-IDF similarity to composite score generates valid 300 DPI PNG."""
    fig = plot_similarity_vs_composite_score(sample_ranked_candidates, output_dir=tmp_path)
    assert isinstance(fig, plt.Figure)
    assert fig.dpi == 300
    target_path = tmp_path / "similarity_vs_composite_score.png"
    _verify_image_file(target_path)
    plt.close(fig)


def test_plot_review_category_distribution(tmp_path, sample_ranked_candidates):
    """Verify donut chart of review categories generates valid 300 DPI PNG with category proportions."""
    fig = plot_review_category_distribution(sample_ranked_candidates, output_dir=tmp_path)
    assert isinstance(fig, plt.Figure)
    assert fig.dpi == 300
    target_path = tmp_path / "review_category_distribution.png"
    _verify_image_file(target_path)
    plt.close(fig)


def test_plot_candidate_skill_heatmap(tmp_path, sample_ranked_candidates):
    """Verify binary detection matrix heatmap generates valid 300 DPI PNG."""
    fig = plot_candidate_skill_heatmap(sample_ranked_candidates, output_dir=tmp_path)
    assert isinstance(fig, plt.Figure)
    assert fig.dpi == 300
    target_path = tmp_path / "candidate_skill_heatmap.png"
    _verify_image_file(target_path)
    plt.close(fig)


def test_plot_required_skill_frequency(tmp_path, sample_ranked_candidates):
    """Verify cohort skill prevalence horizontal bar chart generates valid 300 DPI PNG."""
    fig = plot_required_skill_frequency(sample_ranked_candidates, output_dir=tmp_path)
    assert isinstance(fig, plt.Figure)
    assert fig.dpi == 300
    target_path = tmp_path / "required_skill_frequency.png"
    _verify_image_file(target_path)
    plt.close(fig)


# --------------------------------------------------------------------------
# 2. Batch Orchestrator Tests
# --------------------------------------------------------------------------
def test_generate_all_visualizations_all_files(tmp_path, sample_ranked_candidates):
    """Verify batch orchestrator generates all 7 charts in the target directory."""
    results = generate_all_visualizations(
        sample_ranked_candidates, output_dir=tmp_path, include_optional=True
    )
    assert len(results) == 7
    expected_keys = [
        "candidate_score_comparison",
        "score_distribution",
        "skill_coverage_comparison",
        "similarity_vs_composite_score",
        "review_category_distribution",
        "candidate_skill_heatmap",
        "required_skill_frequency",
    ]
    for key in expected_keys:
        assert key in results
        _verify_image_file(results[key])


def test_generate_all_visualizations_exclude_optional(tmp_path, sample_ranked_candidates):
    """Verify batch orchestrator can omit the optional chart when requested."""
    results = generate_all_visualizations(
        sample_ranked_candidates, output_dir=tmp_path, include_optional=False
    )
    assert len(results) == 6
    assert "required_skill_frequency" not in results
    for key, path in results.items():
        _verify_image_file(path)


# --------------------------------------------------------------------------
# 3. Chart Content & Structural Precision Tests
# --------------------------------------------------------------------------
def test_candidate_score_comparison_ranking_order(sample_ranked_candidates):
    """Verify that horizontal bar chart presents Rank 1 at the top of the chart."""
    fig = plot_candidate_score_comparison(sample_ranked_candidates, output_dir=None)
    ax = fig.axes[0]
    # In Matplotlib barh, the top tick label corresponds to the last element in yticks
    y_labels = [label.get_text() for label in ax.get_yticklabels()]
    assert len(y_labels) == len(sample_ranked_candidates)
    # The top tick should be Rank 1
    assert "Rank 1: CAND-001" in y_labels[-1]
    # The bottom tick should be Rank 4
    assert "Rank 4: CAND-007" in y_labels[0]
    plt.close(fig)


def test_heatmap_binary_matrix_ground_truth(sample_ranked_candidates):
    """Verify heatmap binary matrix values match candidate skill detection ground truth."""
    custom_skills = ["Python", "SQL", "Pandas"]
    fig = plot_candidate_skill_heatmap(
        sample_ranked_candidates, required_skills=custom_skills, output_dir=None
    )
    ax = fig.axes[0]
    # Check x-tick labels match custom_skills
    x_labels = [label.get_text() for label in ax.get_xticklabels()]
    assert x_labels == custom_skills
    # Check y-tick labels match candidates in rank order
    y_labels = [label.get_text() for label in ax.get_yticklabels()]
    assert "CAND-001" in y_labels[0]
    assert "CAND-010" in y_labels[1]
    assert "CAND-006" in y_labels[2]
    assert "CAND-007" in y_labels[3]
    plt.close(fig)


def test_custom_required_skills_support(sample_ranked_candidates):
    """Verify custom required skills list is accepted and displayed."""
    custom_skills = ["Data Mining", "Tableau", "AWS"]
    fig = plot_candidate_skill_heatmap(
        sample_ranked_candidates, required_skills=custom_skills, output_dir=None
    )
    ax = fig.axes[0]
    x_labels = [label.get_text() for label in ax.get_xticklabels()]
    assert x_labels == custom_skills
    plt.close(fig)


def test_heatmap_and_frequency_chart_skill_counts_consistency(sample_ranked_candidates):
    """
    Regression Test: Verify that for every required skill, the detection frequency count
    in the frequency bar chart strictly equals the column sum of the binary detection matrix
    in the candidate skill heatmap.

    Dynamically derives expected counts from candidate skill-matching records
    without hardcoding values.
    """
    required_skills = ["Python", "SQL", "Pandas", "Data Cleaning", "Data Analysis", "Basic Statistics"]

    # 1. Render heatmap
    fig_heatmap = plot_candidate_skill_heatmap(sample_ranked_candidates, required_skills=required_skills)
    ax_heatmap = fig_heatmap.axes[0]
    heatmap_matrix = ax_heatmap.images[0].get_array()
    assert heatmap_matrix.shape[1] == len(required_skills)

    # Calculate column sums for each skill from the heatmap matrix
    heatmap_column_sums = {}
    for col_idx, skill in enumerate(required_skills):
        heatmap_column_sums[skill] = int(np.sum(heatmap_matrix[:, col_idx] == 1))

    plt.close(fig_heatmap)

    # 2. Render required skill frequency chart
    fig_freq = plot_required_skill_frequency(sample_ranked_candidates, required_skills=required_skills)
    ax_freq = fig_freq.axes[0]

    freq_skill_labels = [tick.get_text() for tick in ax_freq.get_yticklabels()]
    freq_bars = [patch for patch in ax_freq.patches if patch.get_height() > 0]
    assert len(freq_skill_labels) == len(freq_bars)

    freq_chart_counts = {
        label: int(round(bar.get_width()))
        for label, bar in zip(freq_skill_labels, freq_bars)
    }

    plt.close(fig_freq)

    # 3. Derive ground truth dynamically from candidate records
    ground_truth_counts = {s: 0 for s in required_skills}
    for c in sample_ranked_candidates:
        req = c.get("required_skills", {})
        if isinstance(req, dict):
            matched_set = {str(m).lower() for m in req.get("matched_names", [])}
            for s in required_skills:
                if s.lower() in matched_set:
                    ground_truth_counts[s] += 1

    # 4. Strict assertions across all six required skills
    for skill in required_skills:
        expected = ground_truth_counts[skill]
        heatmap_val = heatmap_column_sums[skill]
        freq_val = freq_chart_counts[skill]

        # Heatmap column sum must match ground truth derived from records
        assert heatmap_val == expected, (
            f"Heatmap column sum for '{skill}' ({heatmap_val}) does not match ground truth ({expected})."
        )
        # Frequency chart count must match ground truth derived from records
        assert freq_val == expected, (
            f"Frequency chart bar for '{skill}' ({freq_val}) does not match ground truth ({expected})."
        )
        # Heatmap column sum must strictly equal frequency chart count
        assert heatmap_val == freq_val, (
            f"Discrepancy detected for '{skill}': heatmap has {heatmap_val} but frequency chart has {freq_val}."
        )


# --------------------------------------------------------------------------
# 4. Privacy & Anonymization Tests
# --------------------------------------------------------------------------
def test_strict_candidate_privacy_enforcement(sample_ranked_candidates):
    """
    Verify that candidate personal identifiers (full names, email addresses, phone numbers)
    NEVER appear anywhere in the rendered charts, labels, titles, or annotations.
    """
    private_strings = [
        "Aarav Sharma",
        "aarav.sharma@email.com",
        "+91 98765 43210",
        "Divya Sengupta",
        "divya.sengupta@email.com",
        "Ananya Deshmukh",
        "Karan Verma",
    ]

    for plot_fn in [
        plot_candidate_score_comparison,
        plot_score_distribution,
        plot_skill_coverage_comparison,
        plot_similarity_vs_composite_score,
        plot_review_category_distribution,
        plot_candidate_skill_heatmap,
        plot_required_skill_frequency,
    ]:
        fig = plot_fn(sample_ranked_candidates, output_dir=None)

        # Collect all text in figure and axes
        rendered_texts = []
        for text in fig.texts:
            rendered_texts.append(text.get_text())
        for ax in fig.axes:
            rendered_texts.append(ax.get_title())
            rendered_texts.append(ax.get_xlabel())
            rendered_texts.append(ax.get_ylabel())
            for tick in ax.get_xticklabels() + ax.get_yticklabels():
                rendered_texts.append(tick.get_text())
            for child in ax.get_children():
                if isinstance(child, plt.Text):
                    rendered_texts.append(child.get_text())

        all_rendered_content = " ".join(rendered_texts)
        for private_info in private_strings:
            assert private_info not in all_rendered_content, (
                f"Privacy violation: Personal identifier '{private_info}' found in {plot_fn.__name__}."
            )

        plt.close(fig)


# --------------------------------------------------------------------------
# 5. Robustness & Edge Case Tests
# --------------------------------------------------------------------------
def test_empty_candidate_input_graceful_handling(tmp_path):
    """Verify all plotting functions handle empty candidate cohorts without raising errors."""
    for plot_fn in [
        plot_candidate_score_comparison,
        plot_score_distribution,
        plot_skill_coverage_comparison,
        plot_similarity_vs_composite_score,
        plot_review_category_distribution,
        plot_candidate_skill_heatmap,
        plot_required_skill_frequency,
    ]:
        fig = plot_fn([], output_dir=tmp_path)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    results = generate_all_visualizations([], output_dir=tmp_path)
    assert len(results) == 7
    for path in results.values():
        assert path.exists()


def test_invalid_candidate_input_types():
    """Verify invalid input types raise appropriate TypeError."""
    invalid_inputs = [None, 42, "not a list", {"key": "val"}, [None], [{"candidate_id": "CAND-001"}, 123]]
    for plot_fn in [
        plot_candidate_score_comparison,
        plot_score_distribution,
        plot_skill_coverage_comparison,
        plot_similarity_vs_composite_score,
        plot_review_category_distribution,
        plot_candidate_skill_heatmap,
        plot_required_skill_frequency,
        generate_all_visualizations,
    ]:
        for bad_input in invalid_inputs:
            with pytest.raises(TypeError):
                plot_fn(bad_input)


def test_parse_float_helper_numeric_precision_and_none():
    """
    Verify _parse_float strictly distinguishes genuine numerical zero from
    missing (None) or malformed values.
    """
    import numpy as np

    # Genuine zeros (numeric and string formats)
    assert _parse_float(0) == 0.0
    assert _parse_float(0.0) == 0.0
    assert _parse_float("0") == 0.0
    assert _parse_float("0.0") == 0.0

    # Genuine positive floats
    assert _parse_float(65.83) == 65.83
    assert _parse_float("41.20") == 41.20

    # Missing values
    assert _parse_float(None) is None

    # Invalid string values
    assert _parse_float("N/A") is None
    assert _parse_float("invalid") is None
    assert _parse_float("") is None
    assert _parse_float("   ") is None

    # Invalid non-numeric types
    assert _parse_float([]) is None
    assert _parse_float({}) is None
    assert _parse_float(np.nan) is None
    assert _parse_float(np.inf) is None


def test_genuine_zero_preservation_across_visualizations(tmp_path):
    """
    Verify genuine zero values in candidate metrics are accurately preserved
    and explicitly displayed rather than being treated as missing or unavailable.
    """
    zero_candidates = [
        {
            "rank": 1,
            "candidate_id": "CAND-ZERO",
            "composite_score": 0.0,
            "required_coverage": 0.0,
            "preferred_coverage": 0.0,
            "cosine_similarity": 0.0,
            "review_category": "Low Match",
            "required_skills": {
                "coverage": 0.0,
                "matched_names": [],
                "missing_names": ["Python", "SQL", "Pandas", "Data Cleaning", "Data Analysis", "Basic Statistics"],
            },
            "preferred_skills": {
                "coverage": 0.0,
                "matched_names": [],
                "missing_names": ["NumPy", "Scikit-learn"],
            },
            "similarity": {"cosine_similarity": 0.0},
        }
    ]

    # 1. Score comparison chart: must show "0.00" label, not "N/A"
    fig1 = plot_candidate_score_comparison(zero_candidates, output_dir=tmp_path)
    ax1 = fig1.axes[0]
    texts1 = [child.get_text() for child in ax1.get_children() if isinstance(child, plt.Text)]
    assert "0.00" in texts1
    assert "N/A (Score Unavailable)" not in texts1
    plt.close(fig1)

    # 2. Score distribution: candidate with 0.0 must be counted in the 0-10 bin
    fig2 = plot_score_distribution(zero_candidates, output_dir=tmp_path)
    ax2 = fig2.axes[0]
    # Check that non-empty bin count text '1' exists
    texts2 = [child.get_text() for child in ax2.get_children() if isinstance(child, plt.Text)]
    assert "1" in texts2
    plt.close(fig2)

    # 3. Skill coverage comparison: must show "0%" labels, not "N/A"
    fig3 = plot_skill_coverage_comparison(zero_candidates, output_dir=tmp_path)
    ax3 = fig3.axes[0]
    texts3 = [child.get_text() for child in ax3.get_children() if isinstance(child, plt.Text)]
    assert "0%" in texts3
    assert "N/A" not in texts3
    plt.close(fig3)

    # 4. Similarity vs composite score: point (0.0, 0.0) must be plotted
    fig4 = plot_similarity_vs_composite_score(zero_candidates, output_dir=tmp_path)
    ax4 = fig4.axes[0]
    collections = ax4.collections
    assert len(collections) > 0  # scatter collection exists
    offsets = collections[0].get_offsets()
    assert len(offsets) == 1
    assert offsets[0][0] == 0.0  # x = sim = 0.0
    assert offsets[0][1] == 0.0  # y = score = 0.0
    plt.close(fig4)

    # 5. Heatmap: cells must show "—" (not detected), not "N/A"
    fig6 = plot_candidate_skill_heatmap(zero_candidates, output_dir=tmp_path)
    ax6 = fig6.axes[0]
    texts6 = [child.get_text() for child in ax6.get_children() if isinstance(child, plt.Text)]
    assert "—" in texts6
    assert "N/A" not in texts6
    plt.close(fig6)


def test_missing_and_invalid_metrics_explicit_unavailable_indicators(tmp_path):
    """
    Verify candidates with missing (None) or invalid string metrics display
    explicit unavailable indicators ("N/A") and are NOT silently converted to zero.
    """
    unavailable_candidates = [
        {
            "rank": 1,
            "candidate_id": "CAND-MISSING",
            "composite_score": None,          # Missing score
            "required_coverage": "invalid",   # Invalid string
            "preferred_coverage": None,       # Missing preferred coverage
            "cosine_similarity": "N/A",       # Invalid similarity
            "review_category": None,          # Unresolved category
            "required_skills": None,          # Missing skill breakdown
        }
    ]

    # 1. Score comparison chart: must show "N/A (Score Unavailable)", not "0.00"
    fig1 = plot_candidate_score_comparison(unavailable_candidates, output_dir=tmp_path)
    ax1 = fig1.axes[0]
    texts1 = [child.get_text() for child in ax1.get_children() if isinstance(child, plt.Text)]
    assert "N/A (Score Unavailable)" in texts1
    assert "0.00" not in texts1
    plt.close(fig1)

    # 2. Skill coverage comparison: must show "N/A" label, not "0%"
    fig3 = plot_skill_coverage_comparison(unavailable_candidates, output_dir=tmp_path)
    ax3 = fig3.axes[0]
    texts3 = [child.get_text() for child in ax3.get_children() if isinstance(child, plt.Text)]
    assert "N/A" in texts3
    assert "0%" not in texts3
    plt.close(fig3)

    # 3. Similarity vs composite score: candidate with None score/sim is omitted
    fig4 = plot_similarity_vs_composite_score(unavailable_candidates, output_dir=tmp_path)
    # Check that scatter points are empty (placeholder created or 0 points plotted)
    plt.close(fig4)

    # 4. Heatmap: cells must show "N/A" and candidate label must note (Skills N/A)
    fig6 = plot_candidate_skill_heatmap(unavailable_candidates, output_dir=tmp_path)
    ax6 = fig6.axes[0]
    texts6 = [child.get_text() for child in ax6.get_children() if isinstance(child, plt.Text)]
    assert "N/A" in texts6
    y_labels = [label.get_text() for label in ax6.get_yticklabels()]
    assert any("Skills N/A" in lbl for lbl in y_labels)
    plt.close(fig6)


def test_malformed_or_missing_candidate_metrics(tmp_path):
    """Verify records with missing optional sub-metrics default safely."""
    malformed_candidates = [
        {
            "rank": 1,
            "candidate_id": "CAND-999",
            # Missing composite_score, required_skills, preferred_skills, similarity
        },
        {
            "candidate_id": "CAND-998",
            # Missing rank, review_category
            "composite_score": "50.0",  # String number handled
        },
    ]

    results = generate_all_visualizations(malformed_candidates, output_dir=tmp_path)
    assert len(results) == 7
    for path in results.values():
        assert path.exists()


# --------------------------------------------------------------------------
# 6. Full Pipeline Integration Across All 10 Synthetic Resumes
# --------------------------------------------------------------------------
def test_full_pipeline_visualizations_generation(tmp_path):
    """
    Run full end-to-end pipeline:
    1. Parse and clean all 10 synthetic resumes.
    2. Extract skills using junior_data_analyst_requirements.json.
    3. Fit TF-IDF on corpus of 10 resumes + job description.
    4. Compute Phase 8 composite scores.
    5. Rank candidates in Phase 9 order.
    6. Generate Phase 11 visualizations.
    7. Validate output files, 300 DPI, rankings, and ground-truth heatmap detections.
    """
    resume_files = sorted(list(SAMPLE_RESUMES_DIR.glob("candidate_*.*")))
    assert len(resume_files) == 10

    with open(JOB_DESC_PATH, "r", encoding="utf-8") as f:
        job_desc_raw = f.read()
    cleaned_jd = clean_text(job_desc_raw)
    requirements = load_requirements(REQUIREMENTS_PATH)

    candidate_records = []
    for rf in resume_files:
        cid = rf.stem.replace("candidate_", "CAND-")
        raw_text = extract_text(rf)
        c_text = clean_text(raw_text)
        candidate_records.append({
            "id": cid,
            "cleaned_text": c_text,
        })

    # Phase 8: Score batch
    scored = score_candidate_batch(cleaned_jd, candidate_records, requirements=requirements, sanitize=True)

    # Phase 9: Rank candidates
    ranked = rank_candidates(scored)

    assert len(ranked) == 10
    assert ranked[0]["candidate_id"] == "CAND-001"
    assert ranked[1]["candidate_id"] == "CAND-010"
    assert ranked[-1]["candidate_id"] == "CAND-007"

    # Generate all visualizations into temporary directory
    figures_out = tmp_path / "figures"
    results = generate_all_visualizations(ranked, output_dir=figures_out, include_optional=True)

    assert len(results) == 7
    for key, path in results.items():
        _verify_image_file(path)

    # Verify candidate heatmap against actual ground truth
    # CAND-001 (Rank 1): Python, SQL, Pandas, Data Cleaning, Data Analysis -> 5 skills
    cand_001_req = next(c["required_skills"] for c in ranked if c["candidate_id"] == "CAND-001")
    assert set(cand_001_req["matched_names"]) == {
        "Python", "SQL", "Pandas", "Data Cleaning", "Data Analysis"
    }

    # CAND-010 (Rank 2): Python, SQL, Pandas, Data Analysis, Basic Statistics -> 5 skills
    cand_010_req = next(c["required_skills"] for c in ranked if c["candidate_id"] == "CAND-010")
    assert set(cand_010_req["matched_names"]) == {
        "Python", "SQL", "Pandas", "Data Analysis", "Basic Statistics"
    }

    # CAND-007 (Rank 10): 0 required skills
    cand_007_req = next(c["required_skills"] for c in ranked if c["candidate_id"] == "CAND-007")
    assert cand_007_req["matched_names"] == []

    # Regression Verification: Heatmap column sum strictly equals Frequency Chart count for all 6 skills
    req_skills = [s["canonical_name"] for s in requirements["skill_requirements"]["required"]]
    fig_h = plot_candidate_skill_heatmap(ranked, required_skills=req_skills)
    fig_f = plot_required_skill_frequency(ranked, required_skills=req_skills)

    matrix_h = fig_h.axes[0].images[0].get_array()
    ax_f = fig_f.axes[0]
    f_labels = [t.get_text() for t in ax_f.get_yticklabels()]
    f_bars = [p for p in ax_f.patches if p.get_height() > 0]
    f_counts = {lbl: int(round(b.get_width())) for lbl, b in zip(f_labels, f_bars)}

    plt.close(fig_h)
    plt.close(fig_f)

    # Derive expected counts dynamically from ranked candidate records
    derived_counts = {s: 0 for s in req_skills}
    for c in ranked:
        matched_lower = {str(m).lower() for m in c["required_skills"]["matched_names"]}
        for s in req_skills:
            if s.lower() in matched_lower:
                derived_counts[s] += 1

    for col_idx, s in enumerate(req_skills):
        col_sum = int(np.sum(matrix_h[:, col_idx] == 1))
        # 1. Heatmap column sum equals derived count
        assert col_sum == derived_counts[s], f"Heatmap sum for {s} ({col_sum}) != derived ({derived_counts[s]})"
        # 2. Frequency chart count equals derived count
        assert f_counts[s] == derived_counts[s], f"Frequency count for {s} ({f_counts[s]}) != derived ({derived_counts[s]})"
        # 3. Heatmap column sum equals frequency chart count
        assert col_sum == f_counts[s], f"Heatmap sum ({col_sum}) != Frequency count ({f_counts[s]}) for {s}"

    # Specifically verify SQL detection is 7/10 (70%)
    assert derived_counts["SQL"] == 7
    assert f_counts["SQL"] == 7
