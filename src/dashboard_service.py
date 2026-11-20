"""
Dashboard Service & Pipeline Orchestration Module
Author: Akash Das
Project: Automated Resume Screening Tool

Integrates the multi-format extraction, cleaning, scoring, ranking, and reporting
pipeline specifically for the Streamlit dashboard.
"""

from pathlib import Path
import tempfile
from typing import List, Dict, Any, Optional, Tuple, Union

from src.resume_parser import extract_text, ResumeParserError
from src.text_cleaner import clean_text
from src.skill_extractor import load_requirements, match_skills
from src.scoring import score_candidate_batch
from src.ranking import rank_candidates
from src.report_generator import generate_csv_bytes, generate_excel_bytes

WORKSPACE_DIR = Path(__file__).parent.parent
SAMPLE_RESUMES_DIR = WORKSPACE_DIR / "data" / "sample_resumes"
DEFAULT_JD_PATH = WORKSPACE_DIR / "data" / "job_descriptions" / "junior_data_analyst.txt"
DEFAULT_REQS_PATH = WORKSPACE_DIR / "data" / "job_descriptions" / "junior_data_analyst_requirements.json"

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def load_default_benchmark() -> Tuple[str, dict]:
    """Load benchmark Junior Data Analyst job description and skill requirements."""
    if not DEFAULT_JD_PATH.exists():
        raise FileNotFoundError(f"Job description benchmark not found at: {DEFAULT_JD_PATH}")
    if not DEFAULT_REQS_PATH.exists():
        raise FileNotFoundError(f"Requirements configuration not found at: {DEFAULT_REQS_PATH}")

    jd_text = clean_text(DEFAULT_JD_PATH.read_text(encoding="utf-8"))
    requirements = load_requirements(DEFAULT_REQS_PATH)
    return jd_text, requirements


def load_benchmark_jd() -> str:
    """Load benchmark Junior Data Analyst clean job description text."""
    jd_clean, _ = load_default_benchmark()
    return jd_clean


def load_benchmark_requirements() -> dict:
    """Load benchmark Junior Data Analyst skill requirements dictionary."""
    _, reqs = load_default_benchmark()
    return reqs


def generate_dashboard_csv(ranked_candidates: List[Dict[str, Any]]) -> bytes:
    """Generate downloadable CSV bytes from dashboard candidate records."""
    return generate_csv_bytes(ranked_candidates)


def generate_dashboard_excel(ranked_candidates: List[Dict[str, Any]]) -> bytes:
    """Generate downloadable Excel XLSX bytes from dashboard candidate records."""
    return generate_excel_bytes(ranked_candidates)



def evaluate_sample_resumes() -> Dict[str, Any]:
    """
    Process all ten existing synthetic candidate resumes against the benchmark.

    Returns:
        Dict[str, Any]: Evaluation payload with:
            - 'ranked_candidates': List of ranked candidate cards.
            - 'failed_files': List of failed file error entries (empty for valid sample set).
            - 'total_submitted': Total candidate count (10).
            - 'success_count': Successfully scored count (10).
            - 'failed_count': Failed count (0).
    """
    jd_clean, requirements = load_default_benchmark()
    resume_files = sorted([f for f in SAMPLE_RESUMES_DIR.iterdir() if f.is_file() and f.name != ".gitkeep"])

    candidate_records = []
    failed_files = []

    for f in resume_files:
        cid = f.stem.replace("candidate_", "CAND-")
        try:
            raw_text = extract_text(f)
            c_text = clean_text(raw_text)
            candidate_records.append({
                "id": cid,
                "cleaned_text": c_text,
                "filename": f.name,
            })
        except Exception as exc:
            failed_files.append({
                "filename": f.name,
                "error": str(exc),
            })

    # Common-corpus scoring and deterministic ranking
    scored = score_candidate_batch(jd_clean, candidate_records, requirements=requirements, sanitize=True)
    ranked = rank_candidates(scored)

    return {
        "ranked_candidates": ranked,
        "failed_files": failed_files,
        "total_submitted": len(resume_files),
        "success_count": len(ranked),
        "failed_count": len(failed_files),
        "benchmark_role": "Junior Data Analyst",
    }


def evaluate_uploaded_resumes(
    uploaded_files: List[Any],
    custom_jd_text: Optional[str] = None,
    custom_requirements: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Process custom uploaded resume buffers (PDF, DOCX, TXT) gracefully.
    Handles corrupt, empty, or unsupported files individually without terminating the batch.

    Args:
        uploaded_files (List[Any]): Streamlit UploadedFile objects or file-like buffers.
        custom_jd_text (Optional[str]): Optional custom job description.
        custom_requirements (Optional[dict]): Optional custom requirements dictionary.

    Returns:
        Dict[str, Any]: Evaluation payload with ranked candidates, failures, and metrics.
    """
    if custom_jd_text and custom_jd_text.strip():
        jd_clean = clean_text(custom_jd_text)
    else:
        jd_clean, default_reqs = load_default_benchmark()

    requirements = custom_requirements or load_requirements(DEFAULT_REQS_PATH)

    candidate_records = []
    failed_files = []

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        for idx, up_file in enumerate(uploaded_files):
            orig_name = getattr(up_file, "name", f"upload_{idx+1}")
            ext = Path(orig_name).suffix.lower()

            # 1. Extension validation
            if ext not in SUPPORTED_EXTENSIONS:
                failed_files.append({
                    "filename": orig_name,
                    "error": f"Unsupported file extension '{ext}'. Only .pdf, .docx, and .txt files are supported.",
                })
                continue

            # 2. Check for empty buffer
            try:
                content_bytes = up_file.getvalue() if hasattr(up_file, "getvalue") else up_file.read()
            except Exception as e:
                failed_files.append({
                    "filename": orig_name,
                    "error": f"Could not read uploaded stream: {str(e)}",
                })
                continue

            if len(content_bytes) == 0:
                failed_files.append({
                    "filename": orig_name,
                    "error": "File is empty (0 bytes).",
                })
                continue

            # 3. Write to temporary path for format-specific parsing
            temp_file_path = temp_dir_path / f"temp_{idx}_{orig_name}"
            try:
                temp_file_path.write_bytes(content_bytes)
            except Exception as e:
                failed_files.append({
                    "filename": orig_name,
                    "error": f"Failed to buffer temporary file: {str(e)}",
                })
                continue

            # 4. Extract and clean text
            try:
                raw_text = extract_text(temp_file_path)
                c_text = clean_text(raw_text)
                if not c_text.strip():
                    failed_files.append({
                        "filename": orig_name,
                        "error": "Extracted text contains no readable or printable content.",
                    })
                    continue

                # Generate clean synthetic Candidate ID from filename or index
                stem = Path(orig_name).stem
                if stem.lower().startswith("candidate_") or stem.lower().startswith("cand-"):
                    cid = stem.upper().replace("CANDIDATE_", "CAND-")
                else:
                    cid = f"CAND-U{idx+1:03d}"

                candidate_records.append({
                    "id": cid,
                    "cleaned_text": c_text,
                    "filename": orig_name,
                })

            except ResumeParserError as exc:
                failed_files.append({
                    "filename": orig_name,
                    "error": f"Parsing Error: {str(exc)}",
                })
            except Exception as exc:
                failed_files.append({
                    "filename": orig_name,
                    "error": f"Unexpected Error: {str(exc)}",
                })

    # Score and rank if at least one candidate succeeded
    if candidate_records:
        scored = score_candidate_batch(jd_clean, candidate_records, requirements=requirements, sanitize=True)
        ranked = rank_candidates(scored)
    else:
        ranked = []

    return {
        "ranked_candidates": ranked,
        "failed_files": failed_files,
        "total_submitted": len(uploaded_files),
        "success_count": len(ranked),
        "failed_count": len(failed_files),
        "benchmark_role": "Junior Data Analyst",
    }


def compute_cohort_metrics(ranked_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute summary statistics across successfully evaluated candidates."""
    if not ranked_candidates:
        return {
            "total_candidates": 0,
            "max_score": 0.0,
            "top_score": 0.0,
            "lowest_score": 0.0,
            "min_score": 0.0,
            "mean_score": 0.0,
            "median_score": 0.0,
            "high_match_count": 0,
            "mod_match_count": 0,
            "moderate_match_count": 0,
            "low_match_count": 0,
            "top_candidate_id": "N/A",
        }

    scores = [float(c.get("composite_score", 0.0)) for c in ranked_candidates]
    high_count = sum(1 for c in ranked_candidates if c.get("review_category") == "High Match")
    mod_count = sum(1 for c in ranked_candidates if c.get("review_category") == "Moderate Match")
    low_count = sum(1 for c in ranked_candidates if c.get("review_category") == "Low Match")

    sorted_scores = sorted(scores)
    n = len(sorted_scores)
    if n % 2 == 1:
        median = sorted_scores[n // 2]
    else:
        median = (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2.0

    top_candidate = ranked_candidates[0].get("candidate_id", "N/A") if ranked_candidates else "N/A"

    return {
        "total_candidates": len(ranked_candidates),
        "max_score": round(max(scores), 2),
        "top_score": round(max(scores), 2),
        "lowest_score": round(min(scores), 2),
        "min_score": round(min(scores), 2),
        "mean_score": round(sum(scores) / len(scores), 2),
        "median_score": round(median, 2),
        "high_match_count": high_count,
        "mod_match_count": mod_count,
        "moderate_match_count": mod_count,
        "low_match_count": low_count,
        "top_candidate_id": top_candidate,
    }
