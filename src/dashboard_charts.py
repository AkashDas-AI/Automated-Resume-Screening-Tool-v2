"""
Dashboard Charts Module
Author: Akash Das
Project: Automated Resume Screening Tool

Provides theme-aware analytical visualizations (Light Mode and Dark Mode)
specifically rendered for the interactive Streamlit dashboard.
Preserves existing Phase 11 static figure files without modification.
"""

from typing import List, Dict, Any, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# Default 6 canonical required skills for Junior Data Analyst benchmark
DEFAULT_REQUIRED_SKILLS: List[str] = [
    "Python",
    "SQL",
    "Pandas",
    "Data Cleaning",
    "Data Analysis",
    "Basic Statistics",
]


def _get_chart_theme_colors(theme: str) -> Dict[str, str]:
    """Return styling parameters for the designated theme ('light' or 'dark')."""
    is_dark = (str(theme).lower().strip() == "dark")
    if is_dark:
        return {
            "fig_bg": "#1E293B",
            "ax_bg": "#1E293B",
            "text": "#F8FAFC",
            "text_muted": "#94A3B8",
            "grid": "#334155",
            "spine": "#475569",
            "high": "#22C55E",
            "moderate": "#38BDF8",
            "low": "#F59E0B",
            "bar_req": "#38BDF8",
            "bar_pref": "#A855F7",
        }
    return {
        "fig_bg": "#FFFFFF",
        "ax_bg": "#FFFFFF",
        "text": "#0F172A",
        "text_muted": "#64748B",
        "grid": "#E2E8F0",
        "spine": "#CBD5E1",
        "high": "#27AE60",
        "moderate": "#2980B9",
        "low": "#E67E22",
        "bar_req": "#1F4E78",
        "bar_pref": "#8E44AD",
    }


def _apply_axes_styling(ax: plt.Axes, c: Dict[str, str], title: str, xlabel: str = "", ylabel: str = "") -> None:
    """Apply consistent background, spine, and font styling to an axes object."""
    ax.set_facecolor(c["ax_bg"])
    ax.set_title(title, fontsize=13, weight="bold", color=c["text"], pad=14)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10.5, weight="bold", color=c["text"], labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10.5, weight="bold", color=c["text"], labelpad=8)

    ax.tick_params(colors=c["text"], labelsize=9.5)
    for spine in ax.spines.values():
        spine.set_color(c["spine"])
        spine.set_linewidth(0.8)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# --------------------------------------------------------------------------
# 1. Candidate Score Comparison Chart
# --------------------------------------------------------------------------
def render_score_comparison(ranked_candidates: List[Dict[str, Any]], theme: str = "light") -> plt.Figure:
    """Horizontal bar chart displaying composite scores in ranking order."""
    c = _get_chart_theme_colors(theme)
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
    fig.patch.set_facecolor(c["fig_bg"])

    if not ranked_candidates:
        ax.text(0.5, 0.5, "No Candidate Data to Display", ha="center", va="center", color=c["text_muted"], fontsize=12)
        _apply_axes_styling(ax, c, "Candidate Score Comparison")
        fig.tight_layout()
        return fig

    # Reverse so Rank 1 is at top
    cands = sorted(ranked_candidates, key=lambda x: x.get("rank", 999))[::-1]
    ids = [str(cand.get("candidate_id") or cand.get("id", "")) for cand in cands]
    scores = [float(cand.get("composite_score", 0.0)) for cand in cands]
    ranks = [cand.get("rank", idx + 1) for idx, cand in enumerate(cands)]
    categories = [cand.get("review_category", "Low Match") for cand in cands]

    y_labels = [f"Rank {r}: {cid}" for r, cid in zip(ranks, ids)]
    colors = [
        c["high"] if cat == "High Match" else (c["moderate"] if cat == "Moderate Match" else c["low"])
        for cat in categories
    ]

    bars = ax.barh(range(len(ids)), scores, color=colors, height=0.62, edgecolor="none")
    ax.set_yticks(range(len(ids)))
    ax.set_yticklabels(y_labels, fontsize=9.5, weight="bold", color=c["text"])
    ax.set_xlim(0, 105)

    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_width() + 1.2,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.2f}",
            va="center", ha="left", fontsize=9.5, weight="bold", color=c["text"]
        )

    ax.grid(axis="x", color=c["grid"], linestyle="--", linewidth=0.7, alpha=0.8)
    _apply_axes_styling(ax, c, "Candidate Composite Match Score Comparison", xlabel="Composite Match Score (0 – 100)")

    # Legend
    handles = [
        mpatches.Patch(color=c["high"], label="High Match (≥ 70)"),
        mpatches.Patch(color=c["moderate"], label="Moderate Match (40 – 69.9)"),
        mpatches.Patch(color=c["low"], label="Low Match (< 40)"),
    ]
    ax.legend(handles=handles, loc="lower right", facecolor=c["ax_bg"], edgecolor=c["spine"], labelcolor=c["text"], fontsize=8.5)

    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------
# 2. Score Distribution Histogram
# --------------------------------------------------------------------------
def render_score_distribution(ranked_candidates: List[Dict[str, Any]], theme: str = "light") -> plt.Figure:
    """Histogram of candidate composite scores with benchmark markers."""
    c = _get_chart_theme_colors(theme)
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=150)
    fig.patch.set_facecolor(c["fig_bg"])

    if not ranked_candidates:
        ax.text(0.5, 0.5, "No Candidate Data to Display", ha="center", va="center", color=c["text_muted"], fontsize=12)
        _apply_axes_styling(ax, c, "Composite Score Distribution")
        fig.tight_layout()
        return fig

    scores = [float(cand.get("composite_score", 0.0)) for cand in ranked_candidates]
    bins = np.arange(0, 101, 10)
    n, _, patches = ax.hist(scores, bins=bins, color=c["moderate"], edgecolor=c["fig_bg"], linewidth=1.5, alpha=0.9)

    mean_val = float(np.mean(scores))
    median_val = float(np.median(scores))

    ax.axvline(mean_val, color="#EF4444", linestyle="--", linewidth=1.8, label=f"Mean: {mean_val:.2f}")
    ax.axvline(median_val, color="#10B981", linestyle="-.", linewidth=1.8, label=f"Median: {median_val:.2f}")

    ax.set_xticks(bins)
    ax.grid(axis="y", color=c["grid"], linestyle="--", linewidth=0.7, alpha=0.8)
    _apply_axes_styling(ax, c, "Candidate Score Distribution (10-Point Intervals)", xlabel="Score Range", ylabel="Number of Candidates")
    ax.legend(facecolor=c["ax_bg"], edgecolor=c["spine"], labelcolor=c["text"], fontsize=9)

    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------
# 3. Skill Coverage Comparison (Grouped Bar Chart)
# --------------------------------------------------------------------------
def render_skill_coverage_comparison(ranked_candidates: List[Dict[str, Any]], theme: str = "light") -> plt.Figure:
    """Grouped bar chart comparing required vs. preferred skill coverage."""
    c = _get_chart_theme_colors(theme)
    fig, ax = plt.subplots(figsize=(10.5, 5), dpi=150)
    fig.patch.set_facecolor(c["fig_bg"])

    if not ranked_candidates:
        ax.text(0.5, 0.5, "No Candidate Data to Display", ha="center", va="center", color=c["text_muted"], fontsize=12)
        _apply_axes_styling(ax, c, "Skill Coverage Comparison")
        fig.tight_layout()
        return fig

    cands = sorted(ranked_candidates, key=lambda x: x.get("rank", 999))
    ids = [str(cand.get("candidate_id") or cand.get("id", "")) for cand in cands]
    req_covs = [float(cand.get("required_coverage", 0.0)) * 100 for cand in cands]
    pref_covs = [float(cand.get("preferred_coverage", 0.0)) * 100 for cand in cands]

    x = np.arange(len(ids))
    width = 0.36

    rects1 = ax.bar(x - width/2, req_covs, width, label="Required Skills (70% Weight)", color=c["bar_req"], edgecolor="none")
    rects2 = ax.bar(x + width/2, pref_covs, width, label="Preferred Skills (10% Weight)", color=c["bar_pref"], edgecolor="none")

    ax.set_xticks(x)
    ax.set_xticklabels(ids, fontsize=9.5, weight="bold", color=c["text"])
    ax.set_ylim(0, 105)
    ax.grid(axis="y", color=c["grid"], linestyle="--", linewidth=0.7, alpha=0.8)
    _apply_axes_styling(ax, c, "Skill Coverage: Mandatory Required vs. Secondary Preferred", xlabel="Ranked Candidates", ylabel="Coverage Percentage (%)")
    ax.legend(facecolor=c["ax_bg"], edgecolor=c["spine"], labelcolor=c["text"], fontsize=9.5)

    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------
# 4. TF-IDF Similarity vs. Composite Score (Scatter Plot)
# --------------------------------------------------------------------------
def render_similarity_vs_score(ranked_candidates: List[Dict[str, Any]], theme: str = "light") -> plt.Figure:
    """Scatter plot correlating TF-IDF cosine similarity with composite scores."""
    c = _get_chart_theme_colors(theme)
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=150)
    fig.patch.set_facecolor(c["fig_bg"])

    if not ranked_candidates:
        ax.text(0.5, 0.5, "No Candidate Data to Display", ha="center", va="center", color=c["text_muted"], fontsize=12)
        _apply_axes_styling(ax, c, "Similarity vs. Composite Score")
        fig.tight_layout()
        return fig

    sims = [float(cand.get("cosine_similarity", 0.0)) for cand in ranked_candidates]
    scores = [float(cand.get("composite_score", 0.0)) for cand in ranked_candidates]
    ids = [str(cand.get("candidate_id") or cand.get("id", "")) for cand in ranked_candidates]
    categories = [cand.get("review_category", "Low Match") for cand in ranked_candidates]

    dot_colors = [
        c["high"] if cat == "High Match" else (c["moderate"] if cat == "Moderate Match" else c["low"])
        for cat in categories
    ]

    ax.scatter(sims, scores, c=dot_colors, s=120, edgecolors=c["fig_bg"], linewidth=1.5, zorder=3)

    for cid, x_pos, y_pos in zip(ids, sims, scores):
        ax.annotate(
            cid, (x_pos, y_pos),
            textcoords="offset points", xytext=(6, 4),
            fontsize=8.5, weight="bold", color=c["text"]
        )

    ax.set_xlim(-0.02, max(max(sims) * 1.15, 0.35))
    ax.set_ylim(-2, 105)
    ax.grid(color=c["grid"], linestyle="--", linewidth=0.7, alpha=0.8)
    _apply_axes_styling(ax, c, "TF-IDF Cosine Similarity vs. Composite Match Score", xlabel="TF-IDF Cosine Similarity (0.0 – 1.0)", ylabel="Composite Match Score (0 – 100)")

    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------
# 5. Review Category Donut Chart
# --------------------------------------------------------------------------
def render_category_distribution(ranked_candidates: List[Dict[str, Any]], theme: str = "light") -> plt.Figure:
    """Donut chart illustrating cohort proportions across review categories."""
    c = _get_chart_theme_colors(theme)
    fig, ax = plt.subplots(figsize=(6.5, 5), dpi=150)
    fig.patch.set_facecolor(c["fig_bg"])

    if not ranked_candidates:
        ax.text(0.5, 0.5, "No Candidate Data to Display", ha="center", va="center", color=c["text_muted"], fontsize=12)
        fig.tight_layout()
        return fig

    high_cnt = sum(1 for cand in ranked_candidates if cand.get("review_category") == "High Match")
    mod_cnt = sum(1 for cand in ranked_candidates if cand.get("review_category") == "Moderate Match")
    low_cnt = sum(1 for cand in ranked_candidates if cand.get("review_category") == "Low Match")

    counts = [high_cnt, mod_cnt, low_cnt]
    labels = ["High Match", "Moderate Match", "Low Match"]
    colors = [c["high"], c["moderate"], c["low"]]

    # Filter zero wedges
    filtered_data = [(cnt, lbl, col) for cnt, lbl, col in zip(counts, labels, colors) if cnt > 0]

    if not filtered_data:
        ax.text(0.5, 0.5, "No Observations", ha="center", va="center", color=c["text_muted"])
    else:
        f_counts = [d[0] for d in filtered_data]
        f_labels = [f"{d[1]} ({d[0]})" for d in filtered_data]
        f_colors = [d[2] for d in filtered_data]

        wedges, texts, autotexts = ax.pie(
            f_counts,
            labels=f_labels,
            colors=f_colors,
            autopct="%1.1f%%",
            startangle=140,
            pctdistance=0.75,
            wedgeprops={"edgecolor": c["fig_bg"], "linewidth": 2, "width": 0.42}
        )
        for t in texts:
            t.set_color(c["text"])
            t.set_fontsize(9.5)
            t.set_weight("bold")
        for at in autotexts:
            at.set_color("#FFFFFF")
            at.set_fontsize(9)
            at.set_weight("bold")

    ax.text(0, 0, f"Total\n{len(ranked_candidates)}", ha="center", va="center", fontsize=11, weight="bold", color=c["text"])
    ax.set_title("Human-Review Category Breakdown", fontsize=12.5, weight="bold", color=c["text"], pad=14)

    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------
# 6. Required Skill Frequency Chart
# --------------------------------------------------------------------------
def render_required_skill_frequency(
    ranked_candidates: List[Dict[str, Any]],
    required_skills: Optional[List[str]] = None,
    theme: str = "light"
) -> plt.Figure:
    """Horizontal bar chart showing detection frequency of mandatory skills."""
    c = _get_chart_theme_colors(theme)
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    fig.patch.set_facecolor(c["fig_bg"])

    skills_list = required_skills or DEFAULT_REQUIRED_SKILLS
    if not ranked_candidates:
        ax.text(0.5, 0.5, "No Candidate Data to Display", ha="center", va="center", color=c["text_muted"], fontsize=12)
        _apply_axes_styling(ax, c, "Required Skill Prevalence")
        fig.tight_layout()
        return fig

    total_cands = len(ranked_candidates)
    skill_counts = {s: 0 for s in skills_list}

    for cand in ranked_candidates:
        req_skills = cand.get("required_skills", {})
        matched_names = [m.lower() for m in req_skills.get("matched_names", [])]
        for s in skills_list:
            if s.lower() in matched_names:
                skill_counts[s] += 1

    sorted_skills = sorted(skills_list, key=lambda s: skill_counts[s])
    counts = [skill_counts[s] for s in sorted_skills]
    percentages = [(cnt / total_cands) * 100 if total_cands > 0 else 0.0 for cnt in counts]

    bars = ax.barh(range(len(sorted_skills)), percentages, color=c["bar_req"], height=0.55, edgecolor="none")
    ax.set_yticks(range(len(sorted_skills)))
    ax.set_yticklabels(sorted_skills, fontsize=9.5, weight="bold", color=c["text"])
    ax.set_xlim(0, 105)

    for bar, cnt, pct in zip(bars, counts, percentages):
        ax.text(
            bar.get_width() + 1.5,
            bar.get_y() + bar.get_height() / 2,
            f"{cnt}/{total_cands} ({pct:.1f}%)",
            va="center", ha="left", fontsize=9, weight="bold", color=c["text"]
        )

    ax.grid(axis="x", color=c["grid"], linestyle="--", linewidth=0.7, alpha=0.8)
    _apply_axes_styling(ax, c, "Cohort Prevalence of Mandatory Required Skills", xlabel="Prevalence Percentage across Evaluated Candidates (%)")

    fig.tight_layout()
    return fig
