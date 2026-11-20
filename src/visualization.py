"""
Data Visualization Module
Author: Akash Das
Project: Automated Resume Screening Tool

Responsible for generating publication-quality static analytical charts, plots,
and heatmaps from Phase 9 candidate ranking records.

Visualizations:
1. Candidate Score Comparison (Horizontal Bar Chart)
2. Score Distribution (Histogram)
3. Skill Coverage Comparison (Grouped Bar Chart)
4. Similarity vs. Composite Score (Annotated Scatter Plot)
5. Human-Review Category Distribution (Donut Chart)
6. Candidate Skill Heatmap (Binary Detection Matrix)
7. Required Skill Frequency (Cohort Prevalence Bar Chart)

Ethical & Privacy Principles:
1. Strict Personal-Identifier Exclusion:
   Charts strictly display anonymized Candidate IDs (e.g. 'CAND-001') and aggregate metrics.
   Candidate names, email addresses, phone numbers, and physical locations are never displayed.
2. Complete Cohort Transparency (Zero Automated Rejection):
   All candidates—including those categorized as 'Low Match'—are represented.
   'Low Match' is an organizational prioritization aid, NEVER an automated rejection.
3. Educational Prototype Disclaimers:
   Charts document that scores represent lexical and TF-IDF text similarity against the
   benchmark job description, NOT validated measures of candidate competence or job performance.
   Missing keywords reflect automated detection results, not proof of missing competence.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import matplotlib
# Use non-interactive Agg backend suitable for headless PNG rendering and automated environments
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

DEFAULT_FIGURES_DIR: Path = Path(__file__).parent.parent / "reports" / "figures"

# Standard Junior Data Analyst Required Skills from benchmark specification
DEFAULT_REQUIRED_SKILLS: List[str] = [
    "Python",
    "SQL",
    "Pandas",
    "Data Cleaning",
    "Data Analysis",
    "Basic Statistics",
]

# Color Palette for Corporate / Analytical Presentation
COLOR_NAVY: str = "#1F4E78"
COLOR_BLUE: str = "#2980B9"
COLOR_LIGHT_BLUE: str = "#5DADE2"
COLOR_AMBER: str = "#E67E22"
COLOR_GREEN: str = "#27AE60"
COLOR_GRAY: str = "#7F8C8D"
COLOR_LIGHT_GRAY: str = "#EAEDED"
COLOR_SLATE: str = "#34495E"
COLOR_SILVER: str = "#D5D8DC"

CATEGORY_COLORS: Dict[str, str] = {
    "High Match": COLOR_GREEN,
    "Moderate Match": COLOR_BLUE,
    "Low Match": COLOR_GRAY,
}


def _parse_float(val: Any) -> Optional[float]:
    """
    Parse a numeric value to float, strictly distinguishing genuine numerical zero
    from missing (None, empty) or malformed values.

    Returns:
        float: If val is a valid number or numeric string (including 0, 0.0, '0', '0.0').
        None: If val is None, missing, non-numeric string, or unconvertible object.
    """
    if val is None:
        return None
    try:
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return None
        return f
    except (ValueError, TypeError):
        return None


def _safe_float(val: Any, default: Optional[float] = None) -> Optional[float]:
    """
    Safely convert value to float, returning default if missing or invalid.
    Preserves genuine zero.
    """
    parsed = _parse_float(val)
    return parsed if parsed is not None else default


def _resolve_review_category(c: Dict[str, Any]) -> Optional[str]:
    """
    Resolve or infer human-review category (High Match, Moderate Match, Low Match)
    from candidate record or composite score.
    Returns None if category cannot be resolved and score is unavailable.
    """
    cat = c.get("review_category")
    if cat in ("High Match", "Moderate Match", "Low Match"):
        return str(cat)
    score = _parse_float(c.get("composite_score"))
    if score is not None:
        if score >= 70.0:
            return "High Match"
        elif score >= 40.0:
            return "Moderate Match"
        return "Low Match"
    return None


def _validate_candidates(candidates: List[Dict[str, Any]]) -> None:
    """Validate candidate input list type and structure."""
    if not isinstance(candidates, list):
        raise TypeError(f"candidates must be a list of dicts, got {type(candidates).__name__}.")
    for idx, c in enumerate(candidates):
        if not isinstance(c, dict):
            raise TypeError(f"Item at index {idx} is not a dictionary: {type(c).__name__}.")


def _create_empty_placeholder_figure(chart_title: str) -> plt.Figure:
    """Create a graceful, informative figure when input candidate data is empty."""
    fig, ax = plt.subplots(figsize=(8, 4), dpi=300)
    ax.text(
        0.5, 0.5,
        "No Candidate Data Available to Display\n(Empty Cohort Input)",
        ha="center", va="center", fontsize=14, color=COLOR_GRAY,
        weight="bold"
    )
    ax.set_title(chart_title, fontsize=14, weight="bold", pad=15)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    fig.tight_layout()
    return fig


def _save_figure(fig: plt.Figure, output_dir: Optional[Union[str, Path]], filename: str) -> Path:
    """Save a figure at 300 DPI to the destination directory."""
    out_dir = Path(output_dir) if output_dir is not None else DEFAULT_FIGURES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    return out_path


# --------------------------------------------------------------------------
# 1. Candidate Score Comparison (Horizontal Bar Chart)
# --------------------------------------------------------------------------
def plot_candidate_score_comparison(
    ranked_candidates: List[Dict[str, Any]],
    output_dir: Optional[Union[str, Path]] = None,
    filename: str = "candidate_score_comparison.png"
) -> plt.Figure:
    """
    Generate horizontal bar chart comparing composite match scores across all candidates
    in Phase 9 ranking order.

    Args:
        ranked_candidates (List[Dict[str, Any]]): Ranked candidate records.
        output_dir (Optional[Union[str, Path]]): Directory to save PNG. Defaults to 'reports/figures/'.
        filename (str): Target filename.

    Returns:
        plt.Figure: The Matplotlib Figure object.
    """
    _validate_candidates(ranked_candidates)
    title = "Candidate Composite Match Score Comparison"

    if not ranked_candidates:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    # Preserve ranking order (Rank 1 at top: invert list for barh)
    cands_ordered = sorted(ranked_candidates, key=lambda x: x.get("rank", 999))
    cands_display = cands_ordered[::-1]

    ids = [str(c.get("candidate_id") or c.get("id", "")) for c in cands_display]
    parsed_scores = [_parse_float(c.get("composite_score")) for c in cands_display]
    ranks = [c.get("rank", idx + 1) for idx, c in enumerate(cands_display)]
    categories = [_resolve_review_category(c) for c in cands_display]

    y_labels = [f"Rank {r}: {cid}" for r, cid in zip(ranks, ids)]
    bar_widths = [s if s is not None else 0.0 for s in parsed_scores]
    bar_colors = [
        CATEGORY_COLORS.get(cat, COLOR_GRAY) if cat is not None else COLOR_SILVER
        for cat in categories
    ]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    bars = ax.barh(range(len(ids)), bar_widths, color=bar_colors, height=0.62, edgecolor="none")

    # Add numeric score annotations or explicit unavailable indicators
    for bar, score in zip(bars, parsed_scores):
        if score is not None:
            label_text = f"{score:.2f}"
            text_color = COLOR_SLATE
            font_style = "normal"
        else:
            label_text = "N/A (Score Unavailable)"
            text_color = COLOR_GRAY
            font_style = "italic"

        ax.text(
            bar.get_width() + 1.2,
            bar.get_y() + bar.get_height() / 2,
            label_text,
            va="center", ha="left", fontsize=9.5, weight="bold", color=text_color, style=font_style
        )

    ax.set_yticks(range(len(ids)))
    ax.set_yticklabels(y_labels, fontsize=10, weight="normal")
    ax.set_xlabel("Composite Match Score (0 – 100)", fontsize=11, weight="bold", labelpad=8)
    ax.set_xlim(0, 100)
    ax.grid(axis="x", linestyle="--", alpha=0.4, color=COLOR_GRAY)
    ax.set_axisbelow(True)

    # Clean borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Title and Metadata
    ax.set_title(title, fontsize=13, weight="bold", pad=14, color=COLOR_NAVY)

    # Legend for Review Categories
    legend_elements = [
        mpatches.Patch(facecolor=COLOR_GREEN, label="High Match (Score >= 70)"),
        mpatches.Patch(facecolor=COLOR_BLUE, label="Moderate Match (40 <= Score < 70)"),
        mpatches.Patch(facecolor=COLOR_GRAY, label="Low Match (Score < 40)"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", framealpha=0.9, fontsize=9)

    fig.tight_layout()
    _save_figure(fig, output_dir, filename)
    return fig


# --------------------------------------------------------------------------
# 2. Score Distribution (Histogram)
# --------------------------------------------------------------------------
def plot_score_distribution(
    ranked_candidates: List[Dict[str, Any]],
    output_dir: Optional[Union[str, Path]] = None,
    filename: str = "score_distribution.png"
) -> plt.Figure:
    """
    Generate histogram of composite match scores across the candidate cohort.

    Args:
        ranked_candidates (List[Dict[str, Any]]): Candidate records.
        output_dir (Optional[Union[str, Path]]): Save directory.
        filename (str): Target filename.

    Returns:
        plt.Figure: The Matplotlib Figure object.
    """
    _validate_candidates(ranked_candidates)
    title = "Distribution of Candidate Composite Match Scores"

    if not ranked_candidates:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    parsed_scores = [_parse_float(c.get("composite_score")) for c in ranked_candidates]
    valid_scores = [s for s in parsed_scores if s is not None]
    omitted_count = len(parsed_scores) - len(valid_scores)

    if not valid_scores:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    mean_score = float(np.mean(valid_scores))
    median_score = float(np.median(valid_scores))

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    # 10-point bin intervals from 0 to 100
    bins = list(range(0, 105, 10))
    n, bin_edges, patches = ax.hist(
        valid_scores, bins=bins, color=COLOR_BLUE, edgecolor="white", linewidth=1.5, rwidth=0.92
    )

    # Value counts on top of non-empty bars
    for count, edge in zip(n, bin_edges):
        if count > 0:
            ax.text(
                edge + 5, count + 0.08, str(int(count)),
                ha="center", va="bottom", fontsize=10, weight="bold", color=COLOR_SLATE
            )

    # Summary statistic reference lines
    ax.axvline(mean_score, color="#C0392B", linestyle="--", linewidth=1.8, label=f"Mean Score ({mean_score:.2f})")
    ax.axvline(median_score, color=COLOR_AMBER, linestyle=":", linewidth=2.0, label=f"Median Score ({median_score:.2f})")

    ax.set_xlabel("Composite Match Score Bins", fontsize=11, weight="bold", labelpad=8)
    ax.set_ylabel("Candidate Count (Frequency)", fontsize=11, weight="bold", labelpad=8)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, max(n) + 1.2 if len(n) > 0 else 5)
    ax.set_xticks(bins)
    ax.grid(axis="y", linestyle="--", alpha=0.4, color=COLOR_GRAY)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_title(title, fontsize=13, weight="bold", pad=14, color=COLOR_NAVY)
    ax.legend(loc="upper right", framealpha=0.95, fontsize=9.5)

    # Educational disclaimer footnote
    footnote_text = (
        f"Note: {omitted_count} candidate(s) omitted due to unavailable scores. Cohort of {len(valid_scores)} evaluated candidates."
        if omitted_count > 0
        else "Note: Cohort of 10 synthetic candidates for educational demonstration. Does not represent a general population distribution."
    )
    fig.text(
        0.5, -0.04,
        footnote_text,
        ha="center", fontsize=8.5, style="italic", color=COLOR_GRAY
    )

    fig.tight_layout()
    _save_figure(fig, output_dir, filename)
    return fig


# --------------------------------------------------------------------------
# 3. Skill Coverage Comparison (Grouped Bar Chart)
# --------------------------------------------------------------------------
def plot_skill_coverage_comparison(
    ranked_candidates: List[Dict[str, Any]],
    output_dir: Optional[Union[str, Path]] = None,
    filename: str = "skill_coverage_comparison.png"
) -> plt.Figure:
    """
    Generate grouped bar chart comparing required and preferred skill coverage
    for all candidates in Phase 9 ranking order.

    Args:
        ranked_candidates (List[Dict[str, Any]]): Candidate records.
        output_dir (Optional[Union[str, Path]]): Save directory.
        filename (str): Target filename.

    Returns:
        plt.Figure: The Matplotlib Figure object.
    """
    _validate_candidates(ranked_candidates)
    title = "Required vs. Preferred Skill Coverage by Candidate"

    if not ranked_candidates:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    cands_ordered = sorted(ranked_candidates, key=lambda x: x.get("rank", 999))
    ids = [str(c.get("candidate_id") or c.get("id", "")) for c in cands_ordered]

    req_covs = []
    pref_covs = []
    req_labels = []
    pref_labels = []

    for c in cands_ordered:
        raw_req = None
        if "required_skills" in c and isinstance(c["required_skills"], dict):
            raw_req = _parse_float(c["required_skills"].get("coverage"))
        if raw_req is None:
            raw_req = _parse_float(c.get("required_coverage"))

        if raw_req is not None:
            req_covs.append(raw_req * 100)
            req_labels.append(f"{raw_req * 100:.0f}%")
        else:
            req_covs.append(0.0)
            req_labels.append("N/A")

        raw_pref = None
        if "preferred_skills" in c and isinstance(c["preferred_skills"], dict):
            raw_pref = _parse_float(c["preferred_skills"].get("coverage"))
        if raw_pref is None:
            raw_pref = _parse_float(c.get("preferred_coverage"))

        if raw_pref is not None:
            pref_covs.append(raw_pref * 100)
            pref_labels.append(f"{raw_pref * 100:.0f}%")
        else:
            pref_covs.append(0.0)
            pref_labels.append("N/A")

    x = np.arange(len(ids))
    width = 0.38

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)

    rects1 = ax.bar(x - width / 2, req_covs, width, label="Required Skills Coverage (70% Weight)", color=COLOR_NAVY)
    rects2 = ax.bar(x + width / 2, pref_covs, width, label="Preferred Skills Coverage (10% Weight)", color=COLOR_AMBER)

    # Value percentage labels: explicitly distinguish genuine 0% from N/A
    for rect, lbl in zip(rects1, req_labels):
        h = rect.get_height()
        if lbl == "N/A":
            ax.text(rect.get_x() + rect.get_width() / 2, 2.0, "N/A", ha="center", va="bottom", fontsize=8.0, style="italic", color=COLOR_GRAY)
        elif h > 0:
            ax.text(rect.get_x() + rect.get_width() / 2, h + 1.5, lbl, ha="center", va="bottom", fontsize=8.5, weight="bold", color=COLOR_NAVY)
        else:
            # Genuine 0%
            ax.text(rect.get_x() + rect.get_width() / 2, 1.5, "0%", ha="center", va="bottom", fontsize=8.5, weight="bold", color=COLOR_NAVY)

    for rect, lbl in zip(rects2, pref_labels):
        h = rect.get_height()
        if lbl == "N/A":
            ax.text(rect.get_x() + rect.get_width() / 2, 2.0, "N/A", ha="center", va="bottom", fontsize=8.0, style="italic", color=COLOR_GRAY)
        elif h > 0:
            ax.text(rect.get_x() + rect.get_width() / 2, h + 1.5, lbl, ha="center", va="bottom", fontsize=8.5, weight="bold", color=COLOR_AMBER)
        else:
            # Genuine 0%
            ax.text(rect.get_x() + rect.get_width() / 2, 1.5, "0%", ha="center", va="bottom", fontsize=8.5, weight="bold", color=COLOR_AMBER)

    ax.set_xlabel("Candidate ID (Ranked Order)", fontsize=11, weight="bold", labelpad=8)
    ax.set_ylabel("Skill Coverage Percentage (0 – 100%)", fontsize=11, weight="bold", labelpad=8)
    ax.set_ylim(0, 105)
    ax.set_xticks(x)
    ax.set_xticklabels(ids, fontsize=9.5, rotation=15)
    ax.grid(axis="y", linestyle="--", alpha=0.4, color=COLOR_GRAY)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_title(title, fontsize=13, weight="bold", pad=14, color=COLOR_NAVY)
    ax.legend(loc="upper right", framealpha=0.95, fontsize=9.5)

    fig.tight_layout()
    _save_figure(fig, output_dir, filename)
    return fig


# --------------------------------------------------------------------------
# 4. Similarity vs. Composite Score (Scatter Plot)
# --------------------------------------------------------------------------
def plot_similarity_vs_composite_score(
    ranked_candidates: List[Dict[str, Any]],
    output_dir: Optional[Union[str, Path]] = None,
    filename: str = "similarity_vs_composite_score.png"
) -> plt.Figure:
    """
    Generate scatter plot evaluating the relationship between TF-IDF cosine similarity
    and overall composite match score.

    Args:
        ranked_candidates (List[Dict[str, Any]]): Candidate records.
        output_dir (Optional[Union[str, Path]]): Save directory.
        filename (str): Target filename.

    Returns:
        plt.Figure: The Matplotlib Figure object.
    """
    _validate_candidates(ranked_candidates)
    title = "TF-IDF Textual Similarity vs. Composite Match Score"

    if not ranked_candidates:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    sims = []
    scores = []
    ids = []
    colors = []
    omitted_cands = []

    for c in ranked_candidates:
        cid = str(c.get("candidate_id") or c.get("id", ""))
        comp = _parse_float(c.get("composite_score"))
        if "similarity" in c and isinstance(c["similarity"], dict):
            sim = _parse_float(c["similarity"].get("cosine_similarity"))
        else:
            sim = _parse_float(c.get("cosine_similarity"))

        # If either metric is unavailable, omit observation from scatter coordinate plane
        if comp is None or sim is None:
            omitted_cands.append(cid)
            continue

        cat = _resolve_review_category(c) or "Low Match"
        sims.append(sim)
        scores.append(comp)
        ids.append(cid)
        colors.append(CATEGORY_COLORS.get(cat, COLOR_GRAY))

    if not sims:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)

    scatter = ax.scatter(sims, scores, c=colors, s=140, edgecolors="black", linewidth=1.2, zorder=4)

    # Annotate each candidate ID next to its marker
    for cid, x_val, y_val in zip(ids, sims, scores):
        ax.annotate(
            cid, (x_val, y_val),
            xytext=(7, 4), textcoords="offset points",
            fontsize=9, weight="bold", color=COLOR_SLATE
        )

    ax.set_xlabel("TF-IDF Cosine Similarity (0.0 – 1.0)", fontsize=11, weight="bold", labelpad=8)
    ax.set_ylabel("Composite Match Score (0 – 100)", fontsize=11, weight="bold", labelpad=8)
    ax.set_ylim(-2, 102)
    ax.set_xlim(min(0.0, min(sims) - 0.02) if sims else 0.0, max(sims) + 0.05 if sims else 1.0)
    ax.grid(True, linestyle="--", alpha=0.4, color=COLOR_GRAY)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_title(title, fontsize=13, weight="bold", pad=14, color=COLOR_NAVY)

    legend_elements = [
        mpatches.Patch(facecolor=COLOR_GREEN, label="High Match (>= 70)"),
        mpatches.Patch(facecolor=COLOR_BLUE, label="Moderate Match (40 – 70)"),
        mpatches.Patch(facecolor=COLOR_GRAY, label="Low Match (< 40)"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", framealpha=0.95, fontsize=9.5)

    # Footnote on correlation vs competence & omitted candidates if any
    footnote_text = (
        f"Ethical Reminder: Cosine similarity captures lexical n-gram co-occurrence. Correlation does not imply candidate competence.\n"
        f"Note: {len(omitted_cands)} candidate(s) omitted due to unavailable similarity/score metrics."
        if omitted_cands
        else "Ethical Reminder: Cosine similarity captures lexical n-gram co-occurrence. Correlation does not imply candidate competence or performance."
    )
    fig.text(
        0.5, -0.06 if omitted_cands else -0.04,
        footnote_text,
        ha="center", fontsize=8.5, style="italic", color=COLOR_GRAY
    )

    fig.tight_layout()
    _save_figure(fig, output_dir, filename)
    return fig


# --------------------------------------------------------------------------
# 5. Human-Review Category Distribution (Donut Chart)
# --------------------------------------------------------------------------
def plot_review_category_distribution(
    ranked_candidates: List[Dict[str, Any]],
    output_dir: Optional[Union[str, Path]] = None,
    filename: str = "review_category_distribution.png"
) -> plt.Figure:
    """
    Generate donut chart illustrating candidate cohort distribution across
    human-review categories (High Match, Moderate Match, Low Match).

    Args:
        ranked_candidates (List[Dict[str, Any]]): Candidate records.
        output_dir (Optional[Union[str, Path]]): Save directory.
        filename (str): Target filename.

    Returns:
        plt.Figure: The Matplotlib Figure object.
    """
    _validate_candidates(ranked_candidates)
    title = "Candidate Human-Review Category Distribution"

    if not ranked_candidates:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    resolved_cats = [_resolve_review_category(c) for c in ranked_candidates]
    available_cats = [cat for cat in resolved_cats if cat is not None]
    omitted_count = len(ranked_candidates) - len(available_cats)

    if not available_cats:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    total_count = len(available_cats)
    high_count = sum(1 for cat in available_cats if cat == "High Match")
    mod_count = sum(1 for cat in available_cats if cat == "Moderate Match")
    low_count = sum(1 for cat in available_cats if cat == "Low Match")

    counts = [high_count, mod_count, low_count]
    categories = ["High Match", "Moderate Match", "Low Match"]
    colors = [COLOR_GREEN, COLOR_BLUE, COLOR_GRAY]

    # Filter non-zero slices for pie chart rendering
    pie_counts = []
    pie_labels = []
    pie_colors = []
    for cnt, cat, col in zip(counts, categories, colors):
        if cnt > 0:
            pie_counts.append(cnt)
            pie_labels.append(f"{cat}\n({cnt})")
            pie_colors.append(col)

    if not pie_counts:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    wedges, texts, autotexts = ax.pie(
        pie_counts,
        labels=pie_labels,
        colors=pie_colors,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.75,
        wedgeprops=dict(width=0.42, edgecolor="white", linewidth=2.5),
        textprops=dict(fontsize=10.5, weight="bold", color=COLOR_SLATE)
    )

    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontsize(10)
        autotext.set_weight("bold")

    # Center label for Donut
    ax.text(
        0, 0, f"Total\nN = {total_count}\nCandidates",
        ha="center", va="center", fontsize=11.5, weight="bold", color=COLOR_NAVY
    )

    ax.set_title(title, fontsize=13, weight="bold", pad=14, color=COLOR_NAVY)

    # Comprehensive legend including zero-count categories
    legend_labels = [
        f"High Match (>= 70): {high_count} ({high_count / total_count * 100:.1f}%)",
        f"Moderate Match (40–70): {mod_count} ({mod_count / total_count * 100:.1f}%)",
        f"Low Match (< 40): {low_count} ({low_count / total_count * 100:.1f}%)",
    ]
    legend_patches = [
        mpatches.Patch(facecolor=COLOR_GREEN, label=legend_labels[0]),
        mpatches.Patch(facecolor=COLOR_BLUE, label=legend_labels[1]),
        mpatches.Patch(facecolor=COLOR_GRAY, label=legend_labels[2]),
    ]
    ax.legend(handles=legend_patches, loc="lower center", bbox_to_anchor=(0.5, -0.08), ncol=1, fontsize=9.5, framealpha=0.9)

    if omitted_count > 0:
        fig.text(
            0.5, -0.14,
            f"Note: {omitted_count} candidate(s) omitted due to unavailable review category / score metrics.",
            ha="center", fontsize=8.0, style="italic", color=COLOR_GRAY
        )

    fig.tight_layout()
    _save_figure(fig, output_dir, filename)
    return fig


# --------------------------------------------------------------------------
# 6. Candidate Skill Heatmap (Binary Detection Matrix)
# --------------------------------------------------------------------------
def plot_candidate_skill_heatmap(
    ranked_candidates: List[Dict[str, Any]],
    required_skills: Optional[List[str]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    filename: str = "candidate_skill_heatmap.png"
) -> plt.Figure:
    """
    Generate binary skill detection heatmap across all candidates in Phase 9 ranking order.

    Rows: Candidates ordered by rank (Rank 1 at top).
    Columns: The six canonical required skills.
    Values: 1 = Skill detected in resume, 0 = Skill not detected in resume.

    Args:
        ranked_candidates (List[Dict[str, Any]]): Candidate records.
        required_skills (Optional[List[str]]): Canonical required skill names.
        output_dir (Optional[Union[str, Path]]): Save directory.
        filename (str): Target filename.

    Returns:
        plt.Figure: The Matplotlib Figure object.
    """
    _validate_candidates(ranked_candidates)
    title = "Required Technical Skill Detection Heatmap (by Candidate Rank)"

    if not ranked_candidates:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    skills = list(required_skills) if required_skills is not None else list(DEFAULT_REQUIRED_SKILLS)
    cands_ordered = sorted(ranked_candidates, key=lambda x: x.get("rank", 999))

    candidate_labels = []
    matrix = []
    has_unavailable = False

    for idx, c in enumerate(cands_ordered):
        cid = str(c.get("candidate_id") or c.get("id", ""))
        rank = c.get("rank", idx + 1)
        req_data = c.get("required_skills")

        if isinstance(req_data, dict) and isinstance(req_data.get("matched_names"), (list, tuple, set)):
            matched_lower = {str(s).lower() for s in req_data["matched_names"]}
            row = [1 if s.lower() in matched_lower else 0 for s in skills]
            candidate_labels.append(f"Rank {rank}: {cid}")
        else:
            # Skill data unavailable for this candidate
            row = [-1 for _ in skills]
            candidate_labels.append(f"Rank {rank}: {cid} (Skills N/A)")
            has_unavailable = True

        matrix.append(row)

    matrix_np = np.array(matrix)

    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)

    if has_unavailable:
        cmap = matplotlib.colors.ListedColormap([COLOR_SILVER, COLOR_LIGHT_GRAY, COLOR_NAVY])
        bounds = [-1.5, -0.5, 0.5, 1.5]
    else:
        cmap = matplotlib.colors.ListedColormap([COLOR_LIGHT_GRAY, COLOR_NAVY])
        bounds = [-0.5, 0.5, 1.5]

    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    im = ax.imshow(matrix_np, cmap=cmap, norm=norm, aspect="auto")

    # Add text annotations in each cell (✓ vs — vs N/A)
    for i in range(len(cands_ordered)):
        for j in range(len(skills)):
            val = matrix_np[i, j]
            if val == 1:
                symbol = "✓"
                text_color = "white"
            elif val == 0:
                symbol = "—"
                text_color = COLOR_GRAY
            else:  # -1
                symbol = "N/A"
                text_color = COLOR_SLATE

            ax.text(
                j, i, symbol,
                ha="center", va="center",
                fontsize=10 if val == -1 else 13,
                weight="bold", color=text_color
            )

    ax.set_xticks(range(len(skills)))
    ax.set_xticklabels(skills, fontsize=10.5, weight="bold", rotation=20, ha="right")
    ax.set_yticks(range(len(cands_ordered)))
    ax.set_yticklabels(candidate_labels, fontsize=10, weight="normal")

    # Gridlines separating matrix cells
    ax.set_xticks(np.arange(-0.5, len(skills), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(cands_ordered), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=2.0)
    ax.tick_params(which="minor", size=0)

    ax.set_title(title, fontsize=13, weight="bold", pad=14, color=COLOR_NAVY)

    # Legend for Binary Status
    legend_elements = [
        mpatches.Patch(facecolor=COLOR_NAVY, label="✓ Detected in Resume Text"),
        mpatches.Patch(facecolor=COLOR_LIGHT_GRAY, label="— Not Detected in Resume Text"),
    ]
    if has_unavailable:
        legend_elements.append(mpatches.Patch(facecolor=COLOR_SILVER, label="N/A Data Unavailable"))
    ax.legend(handles=legend_elements, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3 if has_unavailable else 2, fontsize=10, framealpha=0.95)

    # Ethical Footnote
    fig.text(
        0.5, -0.06,
        "Ethical Notice: Binary indicators reflect automated keyword detection in resume text. Absence of a mention does not prove candidate lacks the skill.",
        ha="center", fontsize=8.5, style="italic", color=COLOR_GRAY
    )

    fig.tight_layout()
    _save_figure(fig, output_dir, filename)
    return fig


# --------------------------------------------------------------------------
# 7. Optional: Required Skill Frequency Across Cohort
# --------------------------------------------------------------------------
def plot_required_skill_frequency(
    ranked_candidates: List[Dict[str, Any]],
    required_skills: Optional[List[str]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    filename: str = "required_skill_frequency.png"
) -> plt.Figure:
    """
    Generate horizontal bar chart showing detection frequency of each required skill
    across the candidate cohort.

    Args:
        ranked_candidates (List[Dict[str, Any]]): Candidate records.
        required_skills (Optional[List[str]]): Canonical required skill names.
        output_dir (Optional[Union[str, Path]]): Save directory.
        filename (str): Target filename.

    Returns:
        plt.Figure: The Matplotlib Figure object.
    """
    _validate_candidates(ranked_candidates)
    title = "Prevalence of Required Skills Across Candidate Cohort"

    if not ranked_candidates:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    skills = list(required_skills) if required_skills is not None else list(DEFAULT_REQUIRED_SKILLS)

    # Only evaluate candidates with available required skill data
    valid_cands = [
        c for c in ranked_candidates
        if isinstance(c.get("required_skills"), dict) and isinstance(c.get("required_skills", {}).get("matched_names"), (list, tuple, set))
    ]
    omitted_count = len(ranked_candidates) - len(valid_cands)

    if not valid_cands:
        fig = _create_empty_placeholder_figure(title)
        _save_figure(fig, output_dir, filename)
        return fig

    total_cands = len(valid_cands)

    counts = {s: 0 for s in skills}
    for c in valid_cands:
        req_data = c["required_skills"]
        matched = req_data.get("matched_names", [])
        matched_lower = {str(s).lower() for s in matched}
        for s in skills:
            if s.lower() in matched_lower:
                counts[s] += 1

    # Sort skills by frequency ascending for horizontal bar chart (highest on top)
    sorted_skills = sorted(skills, key=lambda s: counts[s])
    sorted_counts = [counts[s] for s in sorted_skills]
    sorted_percentages = [counts[s] / total_cands * 100 for s in sorted_skills]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    bars = ax.barh(range(len(sorted_skills)), sorted_counts, color=COLOR_BLUE, height=0.6, edgecolor="none")

    # Annotate counts and percentages
    for bar, count, pct in zip(bars, sorted_counts, sorted_percentages):
        ax.text(
            bar.get_width() + 0.15,
            bar.get_y() + bar.get_height() / 2,
            f"{count}/{total_cands} ({pct:.0f}%)",
            va="center", ha="left", fontsize=9.5, weight="bold", color=COLOR_SLATE
        )

    ax.set_yticks(range(len(sorted_skills)))
    ax.set_yticklabels(sorted_skills, fontsize=10, weight="bold")
    ax.set_xlabel(f"Candidate Count (out of {total_cands})", fontsize=11, weight="bold", labelpad=8)
    ax.set_xlim(0, total_cands + 1.5)
    ax.set_xticks(range(0, total_cands + 2))
    ax.grid(axis="x", linestyle="--", alpha=0.4, color=COLOR_GRAY)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_title(title, fontsize=13, weight="bold", pad=14, color=COLOR_NAVY)

    if omitted_count > 0:
        fig.text(
            0.5, -0.04,
            f"Note: {omitted_count} candidate(s) omitted due to unavailable skill data. Evaluated cohort: {total_cands}.",
            ha="center", fontsize=8.5, style="italic", color=COLOR_GRAY
        )

    fig.tight_layout()
    _save_figure(fig, output_dir, filename)
    return fig


# --------------------------------------------------------------------------
# 8. Batch Orchestrator: Generate All Visualizations
# --------------------------------------------------------------------------
def generate_all_visualizations(
    ranked_candidates: List[Dict[str, Any]],
    required_skills: Optional[List[str]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    include_optional: bool = True
) -> Dict[str, Path]:
    """
    Generate and save all required and optional analytical visualizations.

    Closes each Matplotlib figure after saving to prevent memory leaks during batch execution.

    Args:
        ranked_candidates (List[Dict[str, Any]]): Phase 9 ranked candidate records.
        required_skills (Optional[List[str]]): Canonical required skill names.
        output_dir (Optional[Union[str, Path]]): Destination directory. Defaults to 'reports/figures/'.
        include_optional (bool): Whether to generate optional required skill frequency chart. Defaults to True.

    Returns:
        Dict[str, Path]: Mapping of chart identifiers to generated file Paths.
    """
    _validate_candidates(ranked_candidates)
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_FIGURES_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    saved_files: Dict[str, Path] = {}

    # 1. Candidate Score Comparison
    fig1 = plot_candidate_score_comparison(ranked_candidates, output_dir=target_dir)
    saved_files["candidate_score_comparison"] = target_dir / "candidate_score_comparison.png"
    plt.close(fig1)

    # 2. Score Distribution
    fig2 = plot_score_distribution(ranked_candidates, output_dir=target_dir)
    saved_files["score_distribution"] = target_dir / "score_distribution.png"
    plt.close(fig2)

    # 3. Skill Coverage Comparison
    fig3 = plot_skill_coverage_comparison(ranked_candidates, output_dir=target_dir)
    saved_files["skill_coverage_comparison"] = target_dir / "skill_coverage_comparison.png"
    plt.close(fig3)

    # 4. Similarity vs. Composite Score
    fig4 = plot_similarity_vs_composite_score(ranked_candidates, output_dir=target_dir)
    saved_files["similarity_vs_composite_score"] = target_dir / "similarity_vs_composite_score.png"
    plt.close(fig4)

    # 5. Human-Review Category Distribution
    fig5 = plot_review_category_distribution(ranked_candidates, output_dir=target_dir)
    saved_files["review_category_distribution"] = target_dir / "review_category_distribution.png"
    plt.close(fig5)

    # 6. Candidate Skill Heatmap
    fig6 = plot_candidate_skill_heatmap(ranked_candidates, required_skills=required_skills, output_dir=target_dir)
    saved_files["candidate_skill_heatmap"] = target_dir / "candidate_skill_heatmap.png"
    plt.close(fig6)

    # 7. Optional: Required Skill Frequency
    if include_optional:
        fig7 = plot_required_skill_frequency(ranked_candidates, required_skills=required_skills, output_dir=target_dir)
        saved_files["required_skill_frequency"] = target_dir / "required_skill_frequency.png"
        plt.close(fig7)

    return saved_files
