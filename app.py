"""
Automated Resume Screening Tool - Interactive Streamlit Dashboard
Author: Akash Das
Project: Automated Resume Screening Tool
Phase 13: Dashboard Development using Streamlit

A professional, interactive recruitment analytics dashboard that integrates the complete
screening pipeline: multi-format extraction (PDF, DOCX, TXT), token-safe text cleaning,
deterministic skill matching, single-corpus TF-IDF cosine similarity, full-precision
composite scoring, 4-tier tie-breaking, downloadable CSV/Excel reports, and dynamic Light/Dark mode.
"""

from datetime import datetime
import io
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional

import streamlit as st
import pandas as pd

# Add project root to path
WORKSPACE_ROOT = Path(__file__).parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from src.theme_manager import get_theme_css, get_theme_colors, render_candidate_ranking_table_html
from src.dashboard_service import (
    evaluate_sample_resumes,
    evaluate_uploaded_resumes,
    compute_cohort_metrics,
    load_default_benchmark,
    SAMPLE_RESUMES_DIR,
)
from src.dashboard_charts import (
    render_score_comparison,
    render_score_distribution,
    render_skill_coverage_comparison,
    render_similarity_vs_score,
    render_category_distribution,
    render_required_skill_frequency,
)
from src.report_generator import generate_csv_bytes, generate_excel_bytes


# --------------------------------------------------------------------------
# Streamlit Page Configuration
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Automated Resume Screening Tool | Akash Das",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------------------------------
# Session State & Theme Initialization
# --------------------------------------------------------------------------
# Check query parameters for initial theme override (useful for automation/screenshots)
query_theme = st.query_params.get("theme", None)
if "theme" not in st.session_state:
    if query_theme in ("light", "dark"):
        st.session_state["theme"] = query_theme
    else:
        st.session_state["theme"] = "dark"
elif query_theme in ("light", "dark") and query_theme != st.session_state["theme"]:
    st.session_state["theme"] = query_theme

if "ranked_candidates" not in st.session_state or st.session_state["ranked_candidates"] is None:
    try:
        sample_res = evaluate_sample_resumes()
        st.session_state["ranked_candidates"] = sample_res["ranked_candidates"]
        st.session_state["pipeline_metadata"] = {
            "source": "Benchmark Sample Resumes (10 Files)",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_submitted": sample_res["total_submitted"],
            "success_count": sample_res["success_count"],
            "failed_count": sample_res["failed_count"],
            "failed_files": sample_res["failed_files"],
        }
        if sample_res["ranked_candidates"]:
            st.session_state["selected_candidate_id"] = sample_res["ranked_candidates"][0]["candidate_id"]
    except Exception:
        st.session_state["ranked_candidates"] = None

if "pipeline_metadata" not in st.session_state:
    st.session_state["pipeline_metadata"] = None

if "selected_candidate_id" not in st.session_state:
    st.session_state["selected_candidate_id"] = None

# Inject active theme stylesheet
current_theme = st.session_state["theme"]
theme_colors = get_theme_colors(current_theme)
st.markdown(get_theme_css(current_theme), unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Helper Callbacks
# --------------------------------------------------------------------------
def toggle_theme():
    """Toggle between Dark Mode and Light Mode without resetting screening results."""
    if st.session_state.get("theme") == "dark":
        st.session_state["theme"] = "light"
    else:
        st.session_state["theme"] = "dark"


# --------------------------------------------------------------------------
# Application Header
# --------------------------------------------------------------------------
col_header_title, col_header_toggle = st.columns([0.78, 0.22])

with col_header_title:
    st.markdown(
        """
        <div style="margin-bottom: 0.25rem;">
            <h1 style="margin: 0; font-size: 2.1rem; display: flex; align-items: center; gap: 0.6rem;">
                <span>📄</span> Automated Resume Screening Tool
            </h1>
            <p style="margin: 0.2rem 0 0.5rem 0; font-size: 0.95rem; opacity: 0.85;">
                <strong>Author:</strong> Akash Das &nbsp;|&nbsp; <strong>Domain:</strong> NLP & Recruitment Analytics &nbsp;|&nbsp; <strong>Benchmark Role:</strong> Junior Data Analyst
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_header_toggle:
    st.markdown('<div class="theme-toggle-container">', unsafe_allow_html=True)
    if current_theme == "dark":
        st.button("☀️ Switch to Light Mode", on_click=toggle_theme, key="btn_toggle_light", use_container_width=True)
    else:
        st.button("🌙 Switch to Dark Mode", on_click=toggle_theme, key="btn_toggle_dark", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Sidebar Configuration
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📋 System Overview")
    st.markdown(
        """
        **Author:** Akash Das  
        **Project:** Automated Resume Screening Tool  
        **Architecture:** Multi-Format Parsing, Regex Skill Matching, TF-IDF Cosine Similarity, Deterministic Ranking.
        """
    )

    st.markdown("---")
    st.markdown("### 🎯 Benchmark Job Role")
    st.markdown("**Junior Data Analyst**")
    with st.expander("View Benchmark Requirements", expanded=False):
        st.markdown(
            """
            **Mandatory Required Skills (70% Weight):**
            - Python, SQL, Pandas, Data Cleaning, Data Analysis, Basic Statistics
            
            **Secondary Preferred Skills (10% Weight):**
            - NumPy, Scikit-learn, Machine Learning, Power BI, Tableau, Excel
            
            **Vocabulary Context (20% Weight):**
            - Unified Corpus TF-IDF Cosine Similarity
            """
        )

    st.markdown("---")
    st.markdown("### ⚖️ Review Tier Boundaries")
    st.markdown(
        r"""
        - 🟢 **High Match:** Score $\ge 70.0$
        - 🔵 **Moderate Match:** $40.0 \le$ Score $< 70.0$
        - 🟡 **Low Match:** Score $< 40.0$
        """
    )

    st.markdown("---")
    st.markdown("### 🛡️ Ethical Safeguards")
    st.info(
        "**Mandatory Human-in-the-Loop:** Scores represent text-relevance indicators for an educational prototype. "
        "Low Match serves strictly as an organizational review tier, NEVER as an automated candidate rejection. "
        "Final hiring decisions require human evaluation."
    )


# --------------------------------------------------------------------------
# Main Content: Resume Input Section
# --------------------------------------------------------------------------
st.markdown("---")

input_tab1, input_tab2 = st.tabs(["📁 Mode A: Benchmark Sample Resumes (10 Synthetic Resumes)", "📤 Mode B: Upload Custom Resumes"])

with input_tab1:
    st.markdown(
        """
        Evaluate the 10 pre-configured synthetic candidate resumes (`CAND-001` through `CAND-010`) 
        spanning **PDF**, **DOCX**, and **TXT** formats against the benchmark Junior Data Analyst requirements.
        """
    )
    col_run_sample, col_sample_info = st.columns([0.32, 0.68])
    with col_run_sample:
        if st.button("🚀 Evaluate 10 Sample Resumes", key="btn_run_sample", use_container_width=True):
            with st.spinner("Processing synthetic resumes through screening pipeline..."):
                result = evaluate_sample_resumes()
                st.session_state["ranked_candidates"] = result["ranked_candidates"]
                st.session_state["pipeline_metadata"] = {
                    "source": "Benchmark Sample Resumes (10 Files)",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_submitted": result["total_submitted"],
                    "success_count": result["success_count"],
                    "failed_count": result["failed_count"],
                    "failed_files": result["failed_files"],
                }
                if result["ranked_candidates"]:
                    st.session_state["selected_candidate_id"] = result["ranked_candidates"][0]["candidate_id"]
                st.success("Screening pipeline completed successfully for all 10 synthetic candidates!")
                st.rerun()

    with col_sample_info:
        st.caption(
            "Uses single-corpus TF-IDF vectorization and 4-tier tie-breaking. "
            "Results strictly match approved Phase 9 rankings and Phase 10 reports."
        )

with input_tab2:
    st.markdown(
        """
        Upload one or more candidate resumes in **PDF (.pdf)**, **Microsoft Word (.docx)**, or **Plain Text (.txt)** formats.
        The system validates extensions, handles unreadable files gracefully without crashing, and computes objective match metrics.
        """
    )
    uploaded_files = st.file_uploader(
        "Select candidate resumes to evaluate",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Upload candidate resume files (PDF, DOCX, TXT). Multiple files supported."
    )

    if uploaded_files:
        st.write(f"📂 **{len(uploaded_files)} file(s) selected for processing.**")
        if st.button(f"🚀 Screen {len(uploaded_files)} Uploaded Resume(s)", key="btn_run_uploaded"):
            with st.spinner(f"Evaluating {len(uploaded_files)} candidate resume(s)..."):
                result = evaluate_uploaded_resumes(uploaded_files)
                st.session_state["ranked_candidates"] = result["ranked_candidates"]
                st.session_state["pipeline_metadata"] = {
                    "source": f"Custom Upload ({len(uploaded_files)} Files)",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_submitted": result["total_submitted"],
                    "success_count": result["success_count"],
                    "failed_count": result["failed_count"],
                    "failed_files": result["failed_files"],
                }
                if result["ranked_candidates"]:
                    st.session_state["selected_candidate_id"] = result["ranked_candidates"][0]["candidate_id"]

                if result["failed_count"] > 0 and result["success_count"] > 0:
                    st.warning(f"Screening complete: {result['success_count']} candidate(s) successfully scored, {result['failed_count']} file(s) encountered errors.")
                elif result["failed_count"] > 0 and result["success_count"] == 0:
                    st.error(f"All {result['failed_count']} uploaded file(s) failed processing. See failure details below.")
                else:
                    st.success(f"All {result['success_count']} uploaded candidate(s) successfully evaluated!")
                st.rerun()


# --------------------------------------------------------------------------
# Pipeline Error Reporting (if any)
# --------------------------------------------------------------------------
meta = st.session_state["pipeline_metadata"]
if meta and meta.get("failed_files"):
    with st.expander(f"⚠️ Processing Failures ({len(meta['failed_files'])} file(s) failed)", expanded=True):
        st.error("The following files could not be processed and were safely excluded from candidate scoring:")
        failed_df = pd.DataFrame(meta["failed_files"])
        st.dataframe(failed_df, use_container_width=True)


# --------------------------------------------------------------------------
# Main Dashboard Results
# --------------------------------------------------------------------------
ranked_candidates = st.session_state["ranked_candidates"]

if ranked_candidates is not None and len(ranked_candidates) > 0:
    st.markdown("---")
    metrics = compute_cohort_metrics(ranked_candidates)

    # Executive KPI Metric Cards
    col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
    with col_m1:
        st.metric("Total Submitted", meta.get("total_submitted", len(ranked_candidates)))
    with col_m2:
        st.metric("Successfully Scored", metrics["total_candidates"])
    with col_m3:
        st.metric("Failed / Errors", meta.get("failed_count", 0))
    with col_m4:
        st.metric("Top Match Score", f"{metrics['max_score']:.2f}")
    with col_m5:
        st.metric("Cohort Mean Score", f"{metrics['mean_score']:.2f}")
    with col_m6:
        st.metric("Review Tiers", f"{metrics['mod_match_count']} Mod / {metrics['low_match_count']} Low")

    # Main Presentation Sections
    dash_tab1, dash_tab2, dash_tab3, dash_tab4 = st.tabs([
        "🏆 Candidate Rankings & Reports",
        "🔍 Candidate Deep-Dive & Skills",
        "📈 Analytical Visualizations",
        "ℹ️ System Architecture & Governance",
    ])

    # ----------------------------------------------------------------------
    # TAB 1: Candidate Rankings & Download Reports
    # ----------------------------------------------------------------------
    with dash_tab1:
        st.markdown("### 🏆 Candidate Evaluation Rankings")
        st.markdown(
            "Ranked deterministically using full floating-point precision: **Higher Composite Score** $\\rightarrow$ "
            "**Higher Required Coverage** $\\rightarrow$ **Higher Preferred Coverage** $\\rightarrow$ "
            "**Higher TF-IDF Cosine Similarity** $\\rightarrow$ **Ascending Candidate ID**."
        )

        # 1. Primary theme-aware presentation table (accessible, high-contrast in both Light & Dark modes)
        st.html(render_candidate_ranking_table_html(ranked_candidates, current_theme))

        # 2. Interactive searchable/sortable dataframe view
        table_rows = []
        for c in ranked_candidates:
            table_rows.append({
                "Rank": int(c.get("rank", 0)),
                "Candidate ID": str(c.get("candidate_id", "")),
                "Composite Score": f"{float(c.get('composite_score', 0.0)):.2f}",
                "Required Coverage (70%)": f"{float(c.get('required_coverage', 0.0))*100:.1f}%",
                "Preferred Coverage (10%)": f"{float(c.get('preferred_coverage', 0.0))*100:.1f}%",
                "TF-IDF Cosine Sim (20%)": f"{float(c.get('cosine_similarity', 0.0)):.4f}",
                "Review Category": str(c.get("review_category", "Low Match")),
            })
        df_rankings = pd.DataFrame(table_rows)

        with st.expander("🔍 Interactive Dataframe (Sort, Filter & Search)", expanded=False):
            st.dataframe(df_rankings, use_container_width=True, hide_index=True)

        st.markdown("#### 📥 Export Audit-Ready Screening Reports")
        st.markdown("Download standardized, privacy-preserving reports with zero personal candidate identifiers:")

        col_dl_csv, col_dl_xlsx, _ = st.columns([0.28, 0.32, 0.40])
        with col_dl_csv:
            csv_bytes = generate_csv_bytes(ranked_candidates)
            st.download_button(
                label="📥 Download CSV Report (.csv)",
                data=csv_bytes,
                file_name="screening_report_junior_data_analyst.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_dl_xlsx:
            excel_bytes = generate_excel_bytes(
                ranked_candidates,
                metadata={
                    "job_title": "Junior Data Analyst",
                    "weights_desc": "70% required skills, 10% preferred skills, 20% TF-IDF similarity",
                }
            )
            st.download_button(
                label="📥 Download Formatted Excel Workbook (.xlsx)",
                data=excel_bytes,
                file_name="screening_report_junior_data_analyst.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    # ----------------------------------------------------------------------
    # TAB 2: Candidate Deep-Dive & Skills Breakdown
    # ----------------------------------------------------------------------
    with dash_tab2:
        st.markdown("### 🔍 Candidate Profile & Skill Evidence Inspection")
        candidate_ids = [c["candidate_id"] for c in ranked_candidates]

        default_idx = 0
        if st.session_state["selected_candidate_id"] in candidate_ids:
            default_idx = candidate_ids.index(st.session_state["selected_candidate_id"])

        selected_cid = st.selectbox(
            "Select Candidate to Inspect:",
            options=candidate_ids,
            index=default_idx,
            key="candidate_selector"
        )
        st.session_state["selected_candidate_id"] = selected_cid

        selected_cand = next((c for c in ranked_candidates if c["candidate_id"] == selected_cid), ranked_candidates[0])

        col_card1, col_card2 = st.columns([0.35, 0.65])
        with col_card1:
            cat_str = selected_cand.get("review_category", "Low Match")
            cat_badge_class = "badge-high" if cat_str == "High Match" else ("badge-mod" if cat_str == "Moderate Match" else "badge-low")

            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-header">
                        <span>🎖️</span> {selected_cand['candidate_id']} (Rank {selected_cand.get('rank', 1)})
                    </div>
                    <p style="margin: 0.2rem 0;"><strong>Review Category:</strong> <span class="{cat_badge_class}">{cat_str}</span></p>
                    <p style="margin: 0.2rem 0;"><strong>Composite Score:</strong> <span style="font-size: 1.4rem; font-weight: 800; color: {theme_colors['metric_val']};">{float(selected_cand.get('composite_score', 0.0)):.2f} / 100</span></p>
                    <hr style="margin: 0.75rem 0; border: none; border-top: 1px solid {theme_colors['card_border']};">
                    <p style="margin: 0.2rem 0;"><strong>Required Coverage (70%):</strong> {float(selected_cand.get('required_coverage', 0.0))*100:.1f}%</p>
                    <p style="margin: 0.2rem 0;"><strong>Preferred Coverage (10%):</strong> {float(selected_cand.get('preferred_coverage', 0.0))*100:.1f}%</p>
                    <p style="margin: 0.2rem 0;"><strong>TF-IDF Cosine Sim (20%):</strong> {float(selected_cand.get('cosine_similarity', 0.0)):.4f}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Component Score Breakdown
            score_data = selected_cand.get("score_breakdown", {})
            w_req_pts = float(score_data.get("required_points", float(selected_cand.get("required_coverage", 0.0)) * 70.0))
            w_pref_pts = float(score_data.get("preferred_points", float(selected_cand.get("preferred_coverage", 0.0)) * 10.0))
            w_sim_pts = float(score_data.get("similarity_points", float(selected_cand.get("cosine_similarity", 0.0)) * 20.0))

            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-header"><span>📊</span> Component Score Breakdown</div>
                    <ul style="padding-left: 1.2rem; margin: 0.5rem 0;">
                        <li><strong>Required Skills:</strong> {w_req_pts:.2f} / 70.0 pts</li>
                        <li><strong>Preferred Skills:</strong> {w_pref_pts:.2f} / 10.0 pts</li>
                        <li><strong>TF-IDF Text Overlap:</strong> {w_sim_pts:.2f} / 20.0 pts</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_card2:
            req_info = selected_cand.get("required_skills", {})
            pref_info = selected_cand.get("preferred_skills", {})
            matched_req = req_info.get("matched_names", [])
            missing_req = req_info.get("missing_names", [])
            matched_pref = pref_info.get("matched_names", [])
            missing_pref = pref_info.get("missing_names", [])

            st.markdown(f"#### 🎯 Mandatory Required Skills ({len(matched_req)} Matched, {len(missing_req)} Missing)")
            if matched_req:
                tags_html = "".join([f'<span class="skill-tag-matched">✓ {s}</span>' for s in matched_req])
                st.markdown(f"**Detected:** {tags_html}", unsafe_allow_html=True)
            if missing_req:
                tags_html = "".join([f'<span class="skill-tag-missing">✗ {s}</span>' for s in missing_req])
                st.markdown(f"**Missing:** {tags_html}", unsafe_allow_html=True)

            st.markdown(f"#### ⭐ Secondary Preferred Skills ({len(matched_pref)} Matched, {len(missing_pref)} Missing)")
            if matched_pref:
                tags_html = "".join([f'<span class="skill-tag-pref">★ {s}</span>' for s in matched_pref])
                st.markdown(f"**Detected:** {tags_html}", unsafe_allow_html=True)
            else:
                st.caption("No secondary preferred skills detected in this candidate profile.")

            # Contextual Evidence Snippets
            skill_results = selected_cand.get("skill_match_results", {})
            all_evidence = []
            for item in skill_results.get("required", {}).get("matched", []):
                all_evidence.append((item.get("canonical_name", ""), item.get("evidence", ""), "Required"))
            for item in skill_results.get("preferred", {}).get("matched", []):
                all_evidence.append((item.get("canonical_name", ""), item.get("evidence", ""), "Preferred"))

            if all_evidence:
                with st.expander("🔎 View Contextual Evidence Snippets", expanded=False):
                    for skill_name, snippet, importance in all_evidence:
                        st.markdown(f"**{skill_name}** *({importance})*:")
                        st.markdown(f"> *\"{snippet}\"*")

            # Sanitized Resume Text Preview
            with st.expander("📄 View Anonymized Resume Text (Personal Details Sanitized)", expanded=False):
                scoring_txt = selected_cand.get("scoring_text") or selected_cand.get("cleaned_text", "")
                st.code(scoring_txt, language="text")

    # ----------------------------------------------------------------------
    # TAB 3: Analytical Visualizations (Theme-Aware)
    # ----------------------------------------------------------------------
    with dash_tab3:
        st.markdown(f"### 📈 Analytical Screening Visualizations (*Rendering in {current_theme.capitalize()} Mode*)")
        st.caption("All dashboard charts dynamically adjust background, axes, gridlines, fonts, and colors to match your selected theme.")

        chart_row1_col1, chart_row1_col2 = st.columns(2)
        with chart_row1_col1:
            fig1 = render_score_comparison(ranked_candidates, theme=current_theme)
            st.pyplot(fig1, use_container_width=True)

        with chart_row1_col2:
            fig2 = render_score_distribution(ranked_candidates, theme=current_theme)
            st.pyplot(fig2, use_container_width=True)

        chart_row2_col1, chart_row2_col2 = st.columns(2)
        with chart_row2_col1:
            fig3 = render_skill_coverage_comparison(ranked_candidates, theme=current_theme)
            st.pyplot(fig3, use_container_width=True)

        with chart_row2_col2:
            fig4 = render_similarity_vs_score(ranked_candidates, theme=current_theme)
            st.pyplot(fig4, use_container_width=True)

        chart_row3_col1, chart_row3_col2 = st.columns(2)
        with chart_row3_col1:
            fig5 = render_category_distribution(ranked_candidates, theme=current_theme)
            st.pyplot(fig5, use_container_width=True)

        with chart_row3_col2:
            fig6 = render_required_skill_frequency(ranked_candidates, theme=current_theme)
            st.pyplot(fig6, use_container_width=True)

    # ----------------------------------------------------------------------
    # TAB 4: System Architecture & Governance
    # ----------------------------------------------------------------------
    with dash_tab4:
        st.markdown("### ℹ️ System Architecture & Responsible AI Governance")
        st.markdown(
            """
            #### 1. Screening Pipeline Architecture
            The system executes a deterministic 8-step pipeline:
            1. **Multi-Format Extraction:** PyMuPDF (PDF), python-docx (DOCX), and built-in UTF-8 (TXT).
            2. **Token-Safe Text Cleaning:** Preserves critical symbols (`C++`, `C#`, `.NET`, `Node.js`, `CI/CD`).
            3. **Personal-Identifier Sanitization:** Strips candidate names, emails, phone numbers, and location headers.
            4. **Deterministic Skill Matching:** Boundary-safe regexes prevent false positives (`C` vs `C++`/`C#`).
            5. **Corpus-Wide TF-IDF Cosine Similarity:** Single-corpus vectorization across JD and all candidate resumes.
            6. **Composite Relevance Scoring:** 70% Required Skills, 10% Preferred Skills, 20% TF-IDF Cosine Similarity.
            7. **Deterministic Ranking:** Full floating-point precision tie-breaking hierarchy.
            8. **Standardized Reporting:** Downloadable CSV and multi-sheet formatted Excel workbooks.

            #### 2. Ethical Principles & Governance
            - **Illustrative Text-Relevance Indicators:** All match scores represent surface-level lexical similarity to the benchmark document, NOT candidate intelligence, talent, or job competence.
            - **Zero Automated Disqualification:** Low Match serves strictly as an organizational review aid for recruiters, **never** as an automated filter.
            - **Mandatory Human-in-the-Loop:** Final interviewing and hiring decisions require human evaluation.
            """
        )

else:
    st.info("👆 Click **'🚀 Evaluate 10 Sample Resumes'** above or upload custom candidate resumes to view rankings and analytical visualizations.")


# --------------------------------------------------------------------------
# Footer
# --------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; font-size: 0.85rem; color: {theme_colors['text_muted']}; margin-top: 1rem;">
        <strong>Automated Resume Screening Tool</strong> &nbsp;|&nbsp; 
        Authored by <strong>Akash Das</strong> (Academic & Portfolio Project) &nbsp;|&nbsp; 
        Active Theme: <strong>{current_theme.capitalize()} Mode</strong> &nbsp;|&nbsp; 
        MIT License
    </div>
    """,
    unsafe_allow_html=True,
)
