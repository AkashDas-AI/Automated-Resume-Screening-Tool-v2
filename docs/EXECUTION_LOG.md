# 07. Execution and Progress Log

This log chronologically records every step, implementation milestone, validation run, and architectural decision.

---

## Log Entries

### [2026-11-19] - Documentation Repository Initialization
- **Action**: Created dedicated technical documentation folder (`docs/`) with standardized numbering and naming convention.
- **Artifacts Created**:
  - [`docs/README.md`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/docs/README.md): Index and directory overview.
  - [`docs/01_system_architecture.md`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/docs/01_system_architecture.md): Architectural flow and layer breakdown.
  - [`docs/02_data_flow_pipeline.md`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/docs/02_data_flow_pipeline.md): End-to-end data processing pipeline and sequence diagram.
  - [`docs/03_modules_and_components.md`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/docs/03_modules_and_components.md): Proposed directory structure and module specifications.
  - [`docs/04_dataset_and_preprocessing.md`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/docs/04_dataset_and_preprocessing.md): Data sources, noise handling, and NLP normalization pipeline.
  - [`docs/05_model_and_learning_mechanism.md`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/docs/05_model_and_learning_mechanism.md): TF-IDF, dense embeddings (SBERT), cosine scoring, and classifier mechanisms.
  - [`docs/06_validation_and_testing.md`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/docs/06_validation_and_testing.md): Unit, integration, and ML validation strategies and metrics.
  - [`docs/07_execution_and_progress_log.md`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/docs/07_execution_and_progress_log.md): Tracking log (this file).
- **Validation**: Verified all files created and properly cross-linked.
- **Status**: Completed.

### [2026-11-19] - Phase 1: Environment Setup
- **Action**: Set up and verified project-local development environment.
- **Details**:
  - Inspected existing environment: Windows OS, Python 3.11.0, VS Code 1.146.0, Git 2.51.0.
  - Confirmed and preserved local Git repository initialized via VS Code (`main` branch, `.git/` intact).
  - Created `.gitignore` excluding `.venv/`, `__pycache__/`, test caches, and OS artifacts.
  - Initialized isolated project-local virtual environment (`.venv`) in the project root.
  - Verified Python interpreter (`.\.venv\Scripts\python.exe`) and pip (`.\.venv\Scripts\pip.exe`).
  - Confirmed `.venv/` is excluded from Git tracking via `git status`.
- **Validation**:
  - `.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"` returned `D:\Projects\Python\Automated Resume Screening Tool\.venv\Scripts\python.exe`.
  - `git status` confirmed untracked files are strictly `.gitignore` and `docs/`, with `.venv/` fully ignored.
- **Status**: Completed (Approved by Akash Das).

### [2026-11-19] - Phase 2: Folder Creation and Project Architecture
- **Action**: Established complete modular directory structure and project architecture.
- **Details**:
  - Preserved `.git/`, `.venv/`, and existing Phase 1 documentation.
  - Created modular source package (`src/`) with placeholder modules: `resume_parser.py`, `text_cleaner.py`, `skill_extractor.py`, `similarity.py`, `scoring.py`, `ranking.py`, `report_generator.py`, `utils.py`, `__init__.py`.
  - Created automated test directory (`tests/`) with discovery placeholders: `test_resume_parser.py`, `test_text_cleaner.py`, `test_skill_extractor.py`, `test_scoring.py`, `test_ranking.py`, `__init__.py`.
  - Created data storage layout (`data/sample_resumes/`, `data/job_descriptions/`, `data/uploads/`) with `.gitkeep` anchors.
  - Created output, report, and asset directories (`outputs/`, `reports/`, `images/`) with `.gitkeep` anchors.
  - Added project root configuration and metadata: `app.py`, `requirements.txt`, `README.md`, `CONTRIBUTING.md`, `LICENSE`, `.env.example`, `pytest.ini`.
  - Updated `.gitignore` to protect runtime upload buffers, output files, and Streamlit secrets while retaining existing rules.
- **Validation**:
  - Verified directory tree contains all target directories and files.
  - Verified `.venv` interpreter functions properly: `sys.prefix != sys.base_prefix` is `True`.
  - Verified Git repository preservation: `.git/` intact on branch `main`.
  - Verified `.gitignore` excludes `.venv/` from `git status`.
- **Status**: Completed (Approved by Akash Das).

### [2026-11-19] - Phase 3: Sample Resumes
- **Action**: Generated and verified 10 realistic, entirely fictional candidate resumes across PDF, DOCX, and TXT formats inside `data/sample_resumes/`.
- **Candidates & Skill Profiles**:
  - `candidate_001.pdf` (CAND-001): Python, SQL, Pandas, NumPy
  - `candidate_002.docx` (CAND-002): Python, Django, REST API, SQL
  - `candidate_003.txt` (CAND-003): Java, Spring Boot, SQL
  - `candidate_004.pdf` (CAND-004): Python, Machine Learning, Scikit-learn
  - `candidate_005.docx` (CAND-005): Excel, Power BI, SQL
  - `candidate_006.txt` (CAND-006): Python, NumPy, Pandas, Machine Learning
  - `candidate_007.pdf` (CAND-007): HTML, CSS, JavaScript, React
  - `candidate_008.docx` (CAND-008): Python, Flask, Git, APIs
  - `candidate_009.txt` (CAND-009): SQL, Excel, Tableau, Power BI
  - `candidate_010.pdf` (CAND-010): Python, SQL, Statistics, Data Analysis
- **Format Distribution**: 4 PDF, 3 DOCX, 3 TXT (Total: 10 files).
- **Validation**:
  - Programmatic verification via `validate_resumes.py` testing PyMuPDF text stream extraction for PDFs, python-docx paragraph extraction for DOCXs, and UTF-8 decoding for TXTs.
  - Confirmed 10/10 unique candidate IDs.
  - Confirmed all required primary skills present in respective resume bodies.
  - Confirmed all files are inside `data/sample_resumes/` with non-zero byte size.
  - Preserved `.venv/`, `.git/`, and previous project documentation.
- **Status**: Completed (Approved by Akash Das).

### [2026-11-19] - Phase 4: Job Description and Skill Requirements
- **Action**: Defined benchmark job description and structured required/preferred skill taxonomy for Junior Data Analyst role.
- **Artifacts Created**:
  - `data/job_descriptions/junior_data_analyst.txt`: Complete readable job description covering role overview, responsibilities, required/preferred qualifications, education, and portfolio expectations.
  - `data/job_descriptions/junior_data_analyst_requirements.json`: Structured skill specifications with canonical names, category classifications, and alias mappings.
- **Skill Classification**:
  - Required Skills (6): Python, SQL, Pandas, Data Cleaning, Data Analysis, Basic Statistics.
  - Preferred Skills (6): NumPy, Scikit-learn, Machine Learning, Power BI, Tableau, Excel.
- **Candidate Alignment Verification**:
  - Confirmed the 10 synthetic candidates (CAND-001 to CAND-010) provide diverse coverage: Strong matches (CAND-001, CAND-010), Partial matches (CAND-002, CAND-004, CAND-005, CAND-006, CAND-008, CAND-009), and Weak matches (CAND-003, CAND-007).
  - *Correction Update*: Added CAND-002 (Priya Nair  -  Backend Software Engineer) to the Partial Match cohort due to strong foundational overlap in Python and SQL alongside a backend/API software focus rather than tabular data analysis. Verified all 10 candidates (CAND-001 to CAND-010) are represented exactly once.
- **Housekeeping**:
  - Verified `python-docx` and `PyMuPDF` listed in `requirements.txt` and available in `.venv`.
  - Preserved generation/validation scripts in scratch directory.
  - Confirmed `.venv/`, `.git/`, and all 10 resumes remain intact.
- **Status**: Completed (Approved by Akash Das).

### [2026-11-19] - Phase 5: Text Extraction (PDF, DOCX and TXT)
- **Action**: Implemented robust, multi-format text extraction module in `src/resume_parser.py` and comprehensive test suite in `tests/test_resume_parser.py`.
- **Parser Architecture & Design**:
  - Unified entry point: `extract_text(file_path: Union[str, Path]) -> str` with format dispatching.
  - PDF extraction via `PyMuPDF` (`pymupdf` / `fitz`): page-by-page text stream aggregation, password encryption detection, and scanned/empty page validation.
  - DOCX extraction via `python-docx`: sequential paragraph extraction and deduplicated table cell reading.
  - TXT extraction via Python built-in I/O with UTF-8 decoding and encoding error trapping.
- **Error Handling Hierarchy**:
  - `ResumeParserError`: Base exception class.
  - `FileFormatNotSupportedError`: Rejects non-supported extensions.
  - `EmptyFileError`: Flags 0-byte files before processing.
  - `CorruptedFileError`: Handles unreadable, malformed, or broken zip/PDF structures.
  - `EncryptedPDFError`: Detects password-protected PDFs.
  - `NoTextExtractedError`: Catches blank documents or scanned images lacking selectable text.
- **Automated Testing & Results**:
  - Initial run: 21/21 passed.
  - Enhanced coverage: added 3 focused unit tests covering multi-page PDF extraction (`test_extract_multipage_pdf`), DOCX table & paragraph extraction (`test_extract_docx_with_tables`), and invalid UTF-8 byte handling raising `CorruptedFileError` (`test_invalid_utf8_txt_raises_corruptedfileerror`).
  - Executed updated test suite via `pytest tests/test_resume_parser.py -v`: 24/24 tests passed (0.91s) with 100% success.
  - Executed extraction demonstration across all 10 synthetic candidates with zero failures.
- **Housekeeping & Environment**:
  - Verified `pytest` installed inside `.venv` and documented in `requirements.txt`.
  - Confirmed `.venv/`, `.git/`, and previous phase assets remain intact.
- **Status**: Completed (Approved by Akash Das).

### [2026-11-19] - Phase 6: Text Cleaning
- **Action**: Implemented robust, token-preserving text cleaning and normalization pipeline in `src/text_cleaner.py` and comprehensive test suite in `tests/test_text_cleaner.py`.
- **Cleaning Architecture & Decisions**:
  - Public interface: `clean_text(text: str) -> str` and `tokenize_text(text: str) -> List[str]`.
  - Type checking: Validates `isinstance(text, str)`, raising `TypeError` for non-string inputs.
  - Line ending normalization: Uniformly maps `\r\n` and `\r` to standard `\n`.
  - Whitespace collapsing: Normalizes repeated spaces and tabs to single spaces; cleans excessive blank lines while preserving paragraph boundaries.
  - Case folding: Standardizes text to lowercase for case-insensitive downstream matching.
  - Technical Token Preservation: Utilizes alphanumeric masking (`PROTECTED_TECHNICAL_PATTERNS`) to protect complex tokens containing punctuation (`c++`, `c#`, `.net`, `asp.net`, `node.js`, `react.js`, `vue.js`, `ci/cd`, `pl/sql`, `tcp/ip`) from destruction during punctuation stripping.
  - Decimal & Hyphen Handling: Selectively preserves periods in decimal numbers (e.g., `3.8`, `4.0`, `3.11`) and hyphens in compound words (e.g., `scikit-learn`, `end-to-end`).
  - Word Boundary Protection: Replaces slashes with spaces (`Python/Django` -> `python django`) to prevent word concatenation.
  - Scope boundaries strictly preserved: No blind stopword removal, stemming, or lemmatization applied.
- **Automated Testing & Results**:
  - Ran cleaner test suite (`pytest tests/test_text_cleaner.py -v`): 24/24 passed (0.73s).
  - Ran full project test suite (`pytest -v`): 51/51 passed (0.75s) across parser and cleaner test suites.
  - Verified pipeline integration (`extract_text` -> `clean_text`) on all 10 candidate resumes without modifying source files.
- **Housekeeping & Preservation**:
  - Confirmed all 10 synthetic resumes in `data/sample_resumes/` remain untouched.
  - Confirmed `.venv/` and `.git/` remain intact without unauthorized commits.
- **Status**: Completed (Approved by Akash Das).

### [2026-11-19] - Phase 7: Skill Matching
- **Action**: Implemented deterministic skill-matching engine in `src/skill_extractor.py` and comprehensive test suite in `tests/test_skill_extractor.py`.
- **Matching Architecture & Design Decisions**:
  - Public interface: `match_skills(cleaned_text: str, requirements: dict = None) -> dict`.
  - Schema integration: Loads canonical skill definitions, categories, importance tiers, and configured aliases directly from `data/job_descriptions/junior_data_analyst_requirements.json` via `load_requirements()`.
  - False-Positive Prevention:
    - Built boundary-aware regular expression engine via `build_skill_pattern(term: str)`.
    - Negative lookahead for standalone `C`: `\bc\b(?![+#a-z0-9])` strictly distinguishes `C` from `C++` and `C#`.
    - Handles leading non-word characters for `.net` (`(?<![a-z0-9])\.net\b`) and trailing non-word characters for `c++` (`\bc\+\+(?![+a-z0-9])`).
    - Enforces full token boundaries on short aliases (`py`, `pd`, `np`, `ml`, `dax`), preventing substring matches inside common words (e.g., `copy`, `updated`, `snapshot`, `html`, `syntax`).
    - Multiword skill matching (`data cleaning`, `basic statistics`, `machine learning`, `power bi`, `rest api`) with flexible intra-phrase whitespace handling.
  - Contextual Evidence Snippets: Extracts real windowed snippets (`extract_evidence_snippet`) around detected matches from cleaned resume text without hallucination.
  - Database Aliases: Honors configured SQL aliases (`postgresql`, `mysql`, `sqlite`) mapping to canonical `SQL` as specified in requirements.
  - Strict scope adherence: No scoring, percentages, or candidate rankings computed; non-detected skills phrased as "not found in resume".
- **Automated Testing & Results**:
  - Ran skill extractor test suite (`pytest tests/test_skill_extractor.py -v`): 25/25 passed (0.53s).
  - Ran full project test suite (`pytest -v`): 75/75 passed (0.80s) across all parser, cleaner, and skill extractor tests.
  - Ran integration demonstration across all 10 synthetic candidate resumes with clean categorization and evidence extraction.
- **Housekeeping & Preservation**:
  - Confirmed all 10 synthetic resumes in `data/sample_resumes/` remain untouched.
  - Confirmed requirements JSON remains unmodified.
  - Confirmed `.venv/` and `.git/` remain intact without unauthorized commits.
- **Status**: Completed (Approved by Akash Das).

### [2026-11-19] - Phase 8: Resume Scoring
- **Action**: Implemented Scikit-learn TF-IDF cosine similarity computation in `src/similarity.py`, composite resume relevance scoring in `src/scoring.py`, and comprehensive test suite in `tests/test_scoring.py`.
- **Scoring Architecture & Mathematical Formulation**:
  - Required Coverage ($C_{req}$): $\frac{\text{matched required}}{\text{total required}} \in [0.0, 1.0]$
  - Preferred Coverage ($C_{pref}$): $\frac{\text{matched preferred}}{\text{total preferred}} \in [0.0, 1.0]$
  - Textual Cosine Similarity ($S_{sim}$): Scikit-learn TF-IDF pairwise similarity $\in [0.0, 1.0]$ using $n$-gram range (1, 2) and custom token pattern preserving technical symbols.
  - Default Configurable Weights: Required ($w_{req} = 70.0$), Preferred ($w_{pref} = 10.0$), Similarity ($w_{sim} = 20.0$), strictly summing to 100.0.
  - Composite Formula: $\text{Score} = (C_{req} \times 70.0) + (C_{pref} \times 10.0) + (S_{sim} \times 20.0)$, bounded in $[0.0, 100.0]$.
  - Zero-skill safe handling: Gracefully computes 0.0 coverage if a skill category is empty or documents lack words.
  - Strict educational disclaimer: Scores are designated as illustrative text-relevance indicators and never as candidate quality or job competence measures.
- **Automated Testing & Results**:
  - Ran scoring test suite (`pytest tests/test_scoring.py -v`): 13/13 passed (2.86s).
  - Ran full project test suite (`pytest -v`): 87/87 passed (2.98s) across all modules with zero failures.
  - Executed end-to-end pipeline demonstration across all 10 synthetic candidates (unranked, ranking deferred to Phase 9).
- **Housekeeping & Preservation**:
  - Installed `scikit-learn` in `.venv/` and verified `requirements.txt`.
  - Confirmed all 10 synthetic resumes, requirements JSON, job description, `.venv/`, and `.git/` remain intact.
- **Status**: Completed (Initial Implementation).

### [2026-11-19] - Phase 8 Audit & Required Corrections: TF-IDF Single-Corpus Fitting and Personal Identifier Exclusion
- **Action**: Performed technical audit and implemented architectural corrections for TF-IDF vectorizer fitting and personal-identifier exclusion during similarity computation.
- **Audit Investigation 1  -  Shared Corpus TF-IDF Fitting**:
  - *Previous Approach*: TF-IDF vectorizer was fitted separately on each independent `[job_description, candidate_resume]` document pair. This meant each candidate's similarity was calculated against an isolated two-document corpus, producing differing document frequencies, inconsistent vocabulary sets, and non-comparable IDF weights across the candidate pool.
  - *Remediation*: Implemented `TFIDFSimilarityEngine` and `compute_corpus_similarities` in [`src/similarity.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/src/similarity.py). Fits a single unified `TfidfVectorizer` across the entire shared corpus `[job_description] + all_candidate_resumes`. All candidate vectors and the job description vector are transformed within the exact same vocabulary space and weighted with identical inverse document frequencies. Also updated `calculate_similarity` to accept an optional pre-fitted engine.
- **Audit Investigation 2  -  Exclusion of Personal Identifiers**:
  - *Audit Finding*: Contact headers and candidate identity tokens (names, email addresses, phone numbers, location lines, and candidate IDs) present in resume text contributed to TF-IDF vector representations and could inadvertently introduce demographic or identity variance into text similarity scores.
  - *Remediation*: Implemented `strip_personal_identifiers(text, candidate_name)` in [`src/text_cleaner.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/src/text_cleaner.py). Strips candidate name tokens, email addresses, phone numbers, location strings, candidate ID prefixes (`CAND-\d{3}`), and metadata markers prior to vectorization.
  - *Fairness & Preservation*: Verified that domain technical vocabulary (`python`, `sql`, `pandas`, `machine learning`, `power bi`), metrics, and professional experience descriptions are strictly preserved.
  - *Verification Tests*: Added targeted unit tests confirming name-change invariance (similarity delta is 0.0000 regardless of candidate name), email/phone change invariance, and technical token preservation.
- **Batch Scoring Utility**:
  - Implemented `score_candidate_batch(job_description, candidates, weights)` in [`src/scoring.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/src/scoring.py) to streamline multi-candidate pipeline execution using the common corpus engine.
- **Automated Testing & Results**:
  - Scoring test suite expanded from 13 to 19 tests in [`tests/test_scoring.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_scoring.py).
  - All 19 scoring tests passed in 2.68s.
  - Full project test suite: 93/93 tests passed (2.68s) across all modules (24 parser, 24 cleaner, 25 skill extractor, 19 scoring, 1 ranking placeholder).
- **Revised 10-Candidate Benchmark Scoring**:
  - Re-evaluated all 10 synthetic candidates against Junior Data Analyst benchmark (`data/job_descriptions/junior_data_analyst.txt`):
    - `CAND-001` (Aarav Sharma): Req 83.3% (5/6), Pref 16.7% (1/6), TF-IDF Sim 0.3185 -> **Composite: 66.37**
    - `CAND-002` (Priya Nair): Req 33.3% (2/6), Pref 0.0% (0/6), TF-IDF Sim 0.0396 -> **Composite: 24.13**
    - `CAND-003` (Rohan Kulkarni): Req 16.7% (1/6), Pref 0.0% (0/6), TF-IDF Sim 0.0406 -> **Composite: 12.48**
    - `CAND-004` (Sneha Patel): Req 33.3% (2/6), Pref 50.0% (3/6), TF-IDF Sim 0.0902 -> **Composite: 30.14**
    - `CAND-005` (Vikram Malhotra): Req 16.7% (1/6), Pref 33.3% (2/6), TF-IDF Sim 0.1407 -> **Composite: 17.81**
    - `CAND-006` (Ananya Deshmukh): Req 50.0% (3/6), Pref 33.3% (2/6), TF-IDF Sim 0.1567 -> **Composite: 41.47**
    - `CAND-007` (Karan Verma): Req 0.0% (0/6), Pref 0.0% (0/6), TF-IDF Sim 0.0158 -> **Composite: 0.32**
    - `CAND-008` (Meera Iyer): Req 33.3% (2/6), Pref 0.0% (0/6), TF-IDF Sim 0.0455 -> **Composite: 24.24**
    - `CAND-009` (Arjun Reddy): Req 16.7% (1/6), Pref 50.0% (3/6), TF-IDF Sim 0.1919 -> **Composite: 20.50**
    - `CAND-010` (Divya Sengupta): Req 83.3% (5/6), Pref 0.0% (0/6), TF-IDF Sim 0.2957 -> **Composite: 64.25**
- **Preservation & Integrity**:
  - Confirmed all 10 synthetic resumes in `data/sample_resumes/` remain untouched.
  - Confirmed requirements JSON and benchmark job description remain unmodified.
  - Confirmed `.venv/` and `.git/` remain intact without unauthorized commits.
- **Status**: Audit & Corrections Completed.

### [2026-11-19] - Phase 8: Final Approval Corrections  -  Composite Identifier Invariance and Scope Hygiene
- **Action**: Implemented end-to-end composite-score identifier invariance across both skill matching and TF-IDF similarity, and eliminated premature review categories from Phase 8 scope.
- **End-to-End Composite Invariance Architecture**:
  - *Identified Vulnerability*: Although TF-IDF similarity was previously anonymized, skill matching evaluated on un-sanitized cleaned text could allow candidate names or email addresses containing skill terms (e.g. "Dan Py", "dan.sql.py@example.com") to trigger false skill matches and artificially inflate the composite score.
  - *Dual-Representation Architecture*:
    - **Original Cleaned Text (`cleaned_text`)**: Maintained in its complete, authentic form (including candidate name, contact block, and section narratives) for human recruiter inspection and contextual evidence validation.
    - **Separate Sanitized Scoring Representation (`scoring_text`)**: Generated via `strip_personal_identifiers()`, stripping candidate names, emails, phone numbers, location headers, and candidate IDs.
    - **Safe Skill Matching**: Both skill extraction and TF-IDF similarity computation operate on `scoring_text` during scoring, preventing personal contact details from contributing to skill counts or text similarity.
    - **Authentic Evidence Preservation**: Domain technical skills, framework names, metrics, and project narratives in the resume body remain 100% intact.
  - *Public Scoring API*:
    - Implemented `score_candidate(job_description, resume_text, candidate_id, candidate_name, ...)` in [`src/scoring.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/src/scoring.py) providing a unified pipeline returning `candidate_id`, `cleaned_text`, `scoring_text`, `skill_match_results`, component coverages, similarity, and composite score.
    - Updated `score_candidate_batch()` in [`src/scoring.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/src/scoring.py) to preserve `cleaned_text` on all candidates while using `scoring_text` for batch TF-IDF and skill matching.
- **Scope Hygiene (Premature Review Categories Removed)**:
  - Removed all qualitative tier labels ("Strong Match", "Moderate Match", "Partial Match", "Weak Match") from Phase 8 output and documentation.
  - Phase 8 output is strictly restricted to numerical component coverages, TF-IDF cosine similarity, composite score, and candidate IDs. Qualitative categorization and candidate sorting are strictly deferred to Phase 9.
- **Expanded Test Suite & Invariance Verification**:
  - Added 3 new comprehensive regression tests in [`tests/test_scoring.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_scoring.py):
    - `test_composite_score_identifier_invariance_synthetic_candidate`: Proves that altering candidate name, email, or phone on real synthetic candidate text yields $\Delta = 0.0000$ across required coverage, preferred coverage, similarity, and composite score, while keeping `cleaned_text` distinct for human review.
    - `test_personal_identifiers_cannot_contribute_to_skill_matches`: Proves that a candidate with skill keywords in name/email but no data skills in resume body receives 0.0 skill coverage.
    - `test_batch_scoring_identifier_invariance_and_human_review_preservation`: Proves batch scoring invariance and preservation of original text.
  - Scoring test suite: **22/22 passed** in 2.93s.
  - Full project test suite: **96/96 passed** in 3.14s (100% pass rate across 5 test modules).
- **Revised Numerical Results for All 10 Candidates (Unranked, Purely Numerical)**:
  - `CAND-001` (PDF): Req 5/6 (83.33%), Pref 1/6 (16.67%), Sim 0.2916, Composite: **65.83**
  - `CAND-002` (DOCX): Req 2/6 (33.33%), Pref 0/6 (0.00%), Sim 0.0404, Composite: **24.14**
  - `CAND-003` (TXT): Req 1/6 (16.67%), Pref 0/6 (0.00%), Sim 0.0415, Composite: **12.50**
  - `CAND-004` (PDF): Req 2/6 (33.33%), Pref 3/6 (50.00%), Sim 0.0912, Composite: **30.16**
  - `CAND-005` (DOCX): Req 1/6 (16.67%), Pref 2/6 (33.33%), Sim 0.1386, Composite: **17.77**
  - `CAND-006` (TXT): Req 3/6 (50.00%), Pref 2/6 (33.33%), Sim 0.1435, Composite: **41.20**
  - `CAND-007` (PDF): Req 0/6 (0.00%), Pref 0/6 (0.00%), Sim 0.0162, Composite: **0.32**
  - `CAND-008` (DOCX): Req 2/6 (33.33%), Pref 0/6 (0.00%), Sim 0.0453, Composite: **24.24**
  - `CAND-009` (TXT): Req 1/6 (16.67%), Pref 3/6 (50.00%), Sim 0.1919, Composite: **20.50**
  - `CAND-010` (PDF): Req 5/6 (83.33%), Pref 0/6 (0.00%), Sim 0.2839, Composite: **64.01**
- **Preservation & Housekeeping**:
  - Preserved `.git/` repository, `.venv/` virtual environment, all 10 synthetic resumes, job description, requirements JSON, and all previous documentation.
  - Zero git commits or branch modifications.
- **Status**: Completed (Approved by Akash Das).

### [2026-11-19] - Phase 9: Candidate Ranking Implementation and Testing
- **Action**: Implemented deterministic candidate ranking, standardized 4-tier tie-breaking hierarchy, configurable human-review categories, and comprehensive automated test suite in `src/ranking.py` and `tests/test_ranking.py`.
- **Ranking Architecture & Design Decisions**:
  - *Public Interfaces*:
    - `rank_candidates(candidate_cards: List[Dict[str, Any]], thresholds: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]`
    - `assign_review_category(score: float, thresholds: Optional[Dict[str, float]] = None) -> str`
    - `validate_thresholds(thresholds: Dict[str, float]) -> None`
  - *Primary Sorting*: Orders candidates by composite match score descending, assigning sequential 1-based ranks (`rank = 1, 2, ...`).
  - *Standardized Tie-Breaking Hierarchy*:
    1. Higher actual composite score (`composite_score` descending)
    2. Higher required skill coverage (`required_coverage` descending)
    3. Higher preferred skill coverage (`preferred_coverage` descending)
    4. Higher TF-IDF cosine similarity (`cosine_similarity` descending)
    5. Candidate ID in ascending alphabetical/numerical order (`candidate_id` ascending)
  - *Full Numerical Precision (Unrounded Sort Key)*:
    - Sort key compares original, unrounded floating-point values directly (`-float(comp), -float(req_cov), -float(pref_cov), -float(sim), cid`).
    - Eliminates 6-decimal rounding in sorting comparisons, ensuring candidates with genuinely higher composite scores (e.g. $50.0000004 > 50.0000001$) can never be displaced by lower-tier tie-breakers due to rounding. Rounding is strictly confined to presentation and reporting displays.
  - *Duplicate Candidate ID Validation*:
    - `rank_candidates` actively tracks candidate IDs, raising `ValueError` on duplicate IDs to prevent ambiguous output without silently discarding or merging records.
  - *Immutability Guarantee*: Operates via `copy.deepcopy()`; input records and dictionaries are never mutated.
  - *Error Handling*: Validates all candidate records before sorting; raises `TypeError` for non-list/non-dict inputs and `ValueError` for missing IDs, duplicate IDs, or out-of-range scores.
  - *Configurable Review Categories*:
    - Default Thresholds: `High Match` ($\ge 70.0$), `Moderate Match` ($\ge 40.0$ and $< 70.0$), `Low Match` ($< 40.0$).
    - Custom threshold injection supported via dictionary (`{'high': float, 'moderate': float}`).
    - Validation guarantees $0.0 \le moderate < high \le 100.0$.
    - Exact boundary behavior verified ($\ge 70.0 \to$ High, $69.9999 \to$ Moderate, $\ge 40.0 \to$ Moderate, $39.9999 \to$ Low).
- **Ethical Framework & Review Aids*:
  - Decision-support aid only: Illustrative text-relevance indicators for human reviewers, never validated competence measures.
  - Zero automated rejection: "Low Match" is strictly an organizational aid and never an automated rejection or disqualification.
  - Mandatory human review: Every candidate remains eligible for human evaluation.
  - Personal-identifier exclusion: No contact details (names, emails, phones, locations) used in ranking logic or output.
- **Automated Testing & Results**:
  - Implemented 20 comprehensive unit and integration tests in [`tests/test_ranking.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_ranking.py) (expanded with 4 precision and duplicate validation regression tests).
  - Executed `pytest tests/test_ranking.py -v`: **20/20 passed** in 3.29s.
  - Executed full project test suite `pytest -v`: **115/115 passed** in 3.04s across all 5 test modules.
- **Ten-Candidate Benchmark Ranking Demonstration**:
  - Rank 1: `CAND-001` | Composite 65.83 | Req 83.33% | Pref 16.67% | Sim 0.2916 | Moderate Match
  - Rank 2: `CAND-010` | Composite 64.01 | Req 83.33% | Pref 0.00% | Sim 0.2839 | Moderate Match
  - Rank 3: `CAND-006` | Composite 41.20 | Req 50.00% | Pref 33.33% | Sim 0.1435 | Moderate Match
  - Rank 4: `CAND-004` | Composite 30.16 | Req 33.33% | Pref 50.00% | Sim 0.0912 | Low Match
  - Rank 5: `CAND-008` | Composite 24.24 | Req 33.33% | Pref 0.00% | Sim 0.0453 | Low Match
  - Rank 6: `CAND-002` | Composite 24.14 | Req 33.33% | Pref 0.00% | Sim 0.0404 | Low Match
  - Rank 7: `CAND-009` | Composite 20.50 | Req 16.67% | Pref 50.00% | Sim 0.1919 | Low Match
  - Rank 8: `CAND-005` | Composite 17.77 | Req 16.67% | Pref 33.33% | Sim 0.1386 | Low Match
  - Rank 9: `CAND-003` | Composite 12.50 | Req 16.67% | Pref 0.00% | Sim 0.0415 | Low Match
  - Rank 10: `CAND-007` | Composite 0.32 | Req 0.00% | Pref 0.00% | Sim 0.0162 | Low Match
- **Preservation & Housekeeping**:
  - Preserved `.git/` repository (clean on `main`, zero commits), `.venv/`, all 10 synthetic resumes, job description, and requirements JSON.
- **Status**: Completed (Approved by Akash Das).

### [2026-11-19] - Phase 10: Report Generation (CSV and Excel Only)
- **Action**: Implemented standardized, privacy-preserving CSV and multi-sheet Excel report generation in `src/report_generator.py` and automated test suite in `tests/test_report_generator.py`.
- **Roadmap Realignment**: Updated 12-Phase Master Roadmap:
  - Phase 10: Report Generation (CSV and Excel Only)
  - Phase 11: Dashboard Development using Streamlit
  - Phase 12: GitHub Publication
  - Confirmed Streamlit, UI components, and web development are strictly excluded from Phase 10 and reserved for Phase 11.
- **Reporting Architecture & Implementation**:
  - *Public API*:
    - `generate_ranking_dataframe(ranked_candidates)`: Standard Pandas DataFrame for ranking results (`Rank`, `Candidate ID`, `Composite Match Score`, `Required Skill Coverage`, `Preferred Skill Coverage`, `TF-IDF Cosine Similarity`, `Human-Review Category`).
    - `generate_details_dataframe(ranked_candidates)`: Detailed skill-level breakdown DataFrame (`Candidate ID`, `Required Skills Matched`, `Required Skills Missing`, `Preferred Skills Matched`, `Preferred Skills Missing`, `Required Coverage`, `Preferred Coverage`, `TF-IDF Cosine Similarity`, `Composite Match Score`, `Human-Review Category`).
    - `export_to_csv(ranked_candidates_or_df, output_path)`: Exports UTF-8 CSV to disk or returns string representation; `index=False`.
    - `generate_csv_bytes(ranked_candidates)`: Generates in-memory UTF-8 bytes for stream downloads (reusable by Phase 11 Streamlit `st.download_button`).
    - `export_to_excel(ranked_candidates, output_path, metadata)`: Creates a formatted 3-sheet Excel workbook via `openpyxl`:
      - **Sheet 1  -  Candidate Ranking**: Executive ranking table, bold navy header fill (`#1F4E78`), white centered text, number formats (`0.00`, `0.0%`, `0.0000`), auto-filter, frozen header row (`A2`).
      - **Sheet 2  -  Detailed Results**: Skill breakdown, comma-separated lists of matched vs missing skills, coverages, scores, auto-filter, frozen header row (`A2`).
      - **Sheet 3  -  Report Information**: Project metadata, author (`Akash Das`), benchmark job role (`Junior Data Analyst`), weights formula (70/10/20), generation timestamp, candidate evaluation counts, review category breakdown, and comprehensive educational prototype disclaimer.
    - `generate_excel_bytes(ranked_candidates, metadata)`: Generates in-memory workbook bytes via `io.BytesIO`.
- **Privacy & Ethical Safeguards**:
  - *Strict Personal Identifier Exclusion*: All candidate names, email addresses, phone numbers, and residential locations are excluded from exported reports. Only canonical Candidate IDs (`CAND-xxx`) and objective scores are exported.
  - *Complete Cohort Transparency*: 100% of candidates (including `Low Match` candidates) are retained in all generated reports. `Low Match` is strictly an illustrative review prioritization aid, never an automated rejection or disqualification.
  - *Educational Disclaimer*: Reports explicitly state that scores represent lexical and TF-IDF relevance to a single benchmark job description, not validated measures of candidate competence or job performance.
- **Dependencies & Environment**:
  - Installed `openpyxl` (3.1.5) and `pandas` (3.1.1) into isolated `.venv/`.
  - Verified `requirements.txt` includes `openpyxl>=3.1.0` and `pandas>=2.0.0`.
- **Automated Testing & Results**:
  - Implemented 18 comprehensive tests in [`tests/test_report_generator.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_report_generator.py).
  - Executed `pytest tests/test_report_generator.py -v`: **18/18 passed** in 4.06s.
  - Executed full project test suite `pytest -v`: **133/133 passed** in 4.29s across all 6 test modules.
- **Ten-Candidate Benchmark Report Generation Demonstration**:
  - Evaluated all 10 synthetic candidates against Junior Data Analyst benchmark, generating:
    - [`reports/screening_report_junior_data_analyst.csv`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/screening_report_junior_data_analyst.csv) (1020 bytes, 10 data rows, 7 columns)
    - [`reports/screening_report_junior_data_analyst.xlsx`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/screening_report_junior_data_analyst.xlsx) (9214 bytes, 3 formatted sheets)
  - Verified: All 10 candidate IDs appear exactly once, ranking matches Phase 9, scores are numeric, Low Match candidates are preserved, no personal identifiers leak, disclaimer is present, Excel formatting and frozen panes are verified.
- **Preservation & Housekeeping**:
  - Preserved `.git/` repository (clean on `main`, zero commits), `.venv/`, all 10 synthetic resumes, job description, requirements JSON, and all previous implementations.
- **Status**: Phase 10 Complete (Approved by Akash Das).

### [2026-11-19] - Phase 11: Data Visualization
- **Action**: Implemented publication-quality analytical visualization engine in `src/visualization.py`, comprehensive test suite in `tests/test_visualization.py`, and generated 7 publication charts at 300 DPI into `reports/figures/`.
- **Roadmap Realignment (14 Phases)**:
  - Official update to the 14-Phase Master Project Roadmap:
    - Phase 10: Report Generation (CSV and Excel)  -  *Completed*
    - Phase 11: Data Visualization  -  *Completed*
    - Phase 12: Insights and Interpretation  -  *Upcoming*
    - Phase 13: Dashboard Development using Streamlit  -  *Upcoming*
    - Phase 14: GitHub Publication  -  *Upcoming*
  - Strict Phase Boundaries Preserved: No Streamlit or interactive web UI built (Phase 13), no written analytical insights authored (Phase 12), no GitHub publication or commits performed (Phase 14).
- **Visualization Architecture & Implementation**:
  - Module: [`src/visualization.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/src/visualization.py)
  - Headless & Non-Interactive: Uses `matplotlib.use("Agg")` providing a non-interactive backend suitable for headless PNG rendering and automated environments across CLI, CI/CD, and downstream Streamlit contexts without GUI dependencies.
  - Figure Formatting: Publication-grade 300 DPI, corporate color palette (Navy `#1F4E78`, Blue `#2980B9`, Amber `#E67E22`, Green `#27AE60`, Slate `#34495E`, Light Gray `#EAEDED`, Silver `#D5D8DC`).
  - Robust Metric & Zero Parsing (`_parse_float`):
    - Strictly preserves genuine numerical zeros (`0`, `0.0`, `"0"`, `"0.0"`).
    - Distinguishes missing metrics (`None`, missing keys) and invalid strings (`"N/A"`, `"invalid"`) from genuine zero values.
    - Explicit unavailable indicators: Score comparison displays `"N/A (Score Unavailable)"`; skill coverage comparison displays `"N/A"` (distinguished from bold `"0%"`); heatmap displays `"N/A"` cells and `"(Skills N/A)"` row label; scatter plot and donut chart omit observations with unavailable metrics rather than distorting distributions.
  - Core Analytical Charts Implemented:
    1. `plot_candidate_score_comparison()`: Horizontal bar chart presenting candidate composite match scores in strict Phase 9 ranking order (Rank 1 at top), custom category coloring, and numeric value annotations. Saved to `reports/figures/candidate_score_comparison.png`.
    2. `plot_score_distribution()`: Histogram of candidate composite match scores (10-point bin intervals from 0 to 100), candidate frequency counts, vertical reference dashed lines for mean and median scores, and cohort disclaimer footnote. Saved to `reports/figures/score_distribution.png`.
    3. `plot_skill_coverage_comparison()`: Grouped bar chart comparing mandatory required skill coverage (70% weight) against preferred skill coverage (10% weight) across all candidates in Phase 9 ranking order, with percentage labels. Saved to `reports/figures/skill_coverage_comparison.png`.
    4. `plot_similarity_vs_composite_score()`: Annotated scatter plot examining the relationship between TF-IDF cosine similarity ($x$-axis) and overall composite match score ($y$-axis), candidate ID callouts, review category coloring, and ethical note that lexical correlation does not equate to job performance. Saved to `reports/figures/similarity_vs_composite_score.png`.
    5. `plot_review_category_distribution()`: Donut chart displaying the cohort breakdown across human-review categories (`High Match`, `Moderate Match`, `Low Match`), percentage labels, white center hole with total cohort count, and full legend. Saved to `reports/figures/review_category_distribution.png`.
    6. `plot_candidate_skill_heatmap()`: Binary detection matrix heatmap displaying candidate rank rows vs canonical required skills (`Python`, `SQL`, `Pandas`, `Data Cleaning`, `Data Analysis`, `Basic Statistics`). Discrete colormap with white grid separators, checkmarks (`✓`) for detected skills, and dashes (` - `) for undetected skills. Saved to `reports/figures/candidate_skill_heatmap.png`.
    7. `plot_required_skill_frequency()`: Optional horizontal bar chart showing cohort prevalence of each required technical skill, sorted by detection frequency with ratio and percentage annotations. Saved to `reports/figures/required_skill_frequency.png`.
  - Batch Orchestrator:
    - `generate_all_visualizations(ranked_candidates, required_skills, output_dir, include_optional=True)`: Generates and saves all 6 required + 1 optional charts, automatically invoking `plt.close(fig)` after each save to eliminate memory leaks during batch execution.
- **Privacy & Ethical Safeguards**:
  - *Strict Personal Identifier Exclusion*: All charts strictly display anonymized Candidate IDs (`CAND-001`, `CAND-002`, ...); full candidate names, email addresses, phone numbers, and addresses are strictly excluded from all titles, labels, ticks, and annotations.
  - *Complete Cohort Transparency*: 100% of candidates (including `Low Match` candidates) are plotted. `Low Match` is clearly documented as an organizational review aid, never an automated rejection.
  - *Educational Footnotes*: Visualizations include prominent disclaimers explaining that scores reflect lexical and TF-IDF text similarity to a benchmark job description, not validated measures of competence or job performance.
- **Dependencies & Environment**:
  - Installed `matplotlib` (3.11.2) into isolated `.venv/`.
  - Updated `requirements.txt` to include `matplotlib>=3.7.0`.
- **Automated Testing & Results**:
  - Implemented 21 automated tests in [`tests/test_visualization.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_visualization.py):
    - Individual figure generation and 300 DPI PNG verification via Pillow (`Image.open(p).info['dpi']`).
    - Batch orchestrator file generation and optional chart toggle.
    - Strict ranking order preservation (Rank 1 at the top of horizontal bar charts).
    - Ground-truth binary heatmap matrix verification against detected skills.
    - Custom required skills list parameter support.
    - Cross-chart data consistency regression test: dynamically verifies that every required skill's detection frequency count strictly equals the column sum of the binary detection matrix in the heatmap.
    - Privacy enforcement test asserting candidate names, emails, and phone numbers never leak into axes text.
    - Robustness edge-case handling for empty candidate cohorts (`[]`) and malformed/missing metrics.
    - Genuine zero vs. missing/invalid metric differentiation tests across numeric zero (`0.0`), `None`, and invalid strings.
    - Full end-to-end integration across all 10 synthetic resumes.
  - Executed `pytest tests/test_visualization.py -v`: **21/21 passed** in 34.94s.
  - Executed full project test suite `pytest -v`: **154/154 passed** in 25.93s across all 7 test modules.
- **Demonstration Run & Generated Figure Artifacts**:
  - Executed full evaluation of 10 synthetic candidates against Junior Data Analyst benchmark, generating:
    - `reports/figures/candidate_score_comparison.png` (196.2 KB, 2970x1770 px, 300 DPI)
    - `reports/figures/score_distribution.png` (134.7 KB, 2670x1739 px, 300 DPI)
    - `reports/figures/skill_coverage_comparison.png` (199.5 KB, 3270x1620 px, 300 DPI)
    - `reports/figures/similarity_vs_composite_score.png` (203.4 KB, 2670x1895 px, 300 DPI)
    - `reports/figures/review_category_distribution.png` (143.6 KB, 2029x1780 px, 300 DPI)
    - `reports/figures/candidate_skill_heatmap.png` (224.3 KB, 2970x2249 px, 300 DPI)
    - `reports/figures/required_skill_frequency.png` (117.1 KB, 2670x1470 px, 300 DPI)
- **Preservation & Housekeeping**:
  - Preserved `.git/` repository (clean on `main`, zero commits), `.venv/`, all synthetic resumes, job description, requirements JSON, and Phase 10 CSV/Excel reports.
- **Status**: Completed (Approved by Akash Das).

### [2026-11-19] - Phase 12: Insights and Interpretation
- **Action**: Authored comprehensive analytical, statistical, and responsible AI interpretation report in [`reports/insights_and_interpretation.md`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/insights_and_interpretation.md).
- **Scope & Phase Boundaries**:
  - Phase 12 of the 14-phase roadmap executed.
  - Strict phase boundaries preserved: zero Streamlit web application code written (`app.py` remains minimal placeholder for Phase 13), zero Git publication or remote commits performed (Phase 14), and zero candidate scores or ranking formulas altered.
  - Strict candidate privacy maintained: only Candidate IDs (`CAND-001` through `CAND-010`) are referenced in all analysis; candidate personal names, email addresses, phone numbers, and home addresses are strictly excluded.
- **Data Sources & Figures Inspected**:
  - Benchmark job description: [`data/job_descriptions/junior_data_analyst.txt`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/data/job_descriptions/junior_data_analyst.txt)
  - Formal taxonomy: [`data/job_descriptions/junior_data_analyst_requirements.json`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/data/job_descriptions/junior_data_analyst_requirements.json)
  - Phase 10 CSV and Excel reports: [`reports/screening_report_junior_data_analyst.csv`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/screening_report_junior_data_analyst.csv) and [`reports/screening_report_junior_data_analyst.xlsx`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/screening_report_junior_data_analyst.xlsx)
  - All 7 Phase 11 publication-grade figures in `reports/figures/`:
    - `candidate_score_comparison.png`
    - `score_distribution.png`
    - `skill_coverage_comparison.png`
    - `similarity_vs_composite_score.png`
    - `review_category_distribution.png`
    - `candidate_skill_heatmap.png`
    - `required_skill_frequency.png`
- **Analytical Sections Authored (10/10 Complete)**:
  1. *Section 1  -  Executive Summary*: Overview of candidate screening experiment, evaluation of 10 synthetic resumes against Junior Data Analyst benchmark, summary of scoring formula (70% required, 10% preferred, 20% TF-IDF similarity), and educational context disclaimer.
  2. *Section 2  -  Candidate Pool Analysis*: Evaluation cohort summary ($N=10$). Score statistics: Min = $0.32$ (`CAND-007`), Max = $65.83$ (`CAND-001`), Mean = $30.07$ ($30.0683$), Median = $24.19$ ($24.1906$), Sample Std Dev ($s$, $ddof=1$) = $21.24$ ($21.2404$), Population Std Dev ($\sigma$, $ddof=0$) = $20.15$ ($20.1504$), $Q_1 = 18.46$, $Q_3 = 38.44$, $IQR = 19.99$. Categorization breakdown: High Match = $0$ ($0.0\%$), Moderate Match = $3$ ($30.0\%$)  -  `CAND-001` ($65.83$), `CAND-010` ($64.01$), `CAND-006` ($41.20$), Low Match = $7$ ($70.0\%$)  -  `CAND-004` ($30.16$), `CAND-008` ($24.24$), `CAND-002` ($24.14$), `CAND-009` ($20.50$), `CAND-005` ($17.77$), `CAND-003` ($12.50$), `CAND-007` ($0.32$). Analysis of bimodal distribution shape.
  3. *Section 3  -  Candidate Ranking Analysis*: Complete 10-candidate ranked summary table, comparative analysis of top contenders (`CAND-001` with $65.83$ vs `CAND-010` with $64.01$), and step-by-step verification of Phase 9 tie-breaking hierarchy (composite score $\rightarrow$ required coverage $\rightarrow$ preferred coverage $\rightarrow$ TF-IDF similarity $\rightarrow$ candidate ID).
  4. *Section 4  -  Required Skill Gap Analysis*: Rigorous examination of mandatory skill detection frequencies across cohort: SQL ($7/10$, $70\%$), Python ($6/10$, $60\%$), Pandas ($4/10$, $40\%$), Data Analysis ($2/10$, $20\%$), Basic Statistics ($2/10$, $20\%$), Data Cleaning ($1/10$, $10\%$). Detailed root-cause analysis of skill gaps (lexical variation, implicit mentions vs explicit keywords, synonym gaps).
  5. *Section 5  -  Required vs. Preferred Skill Coverage*: In-depth analysis of the 70/10/20 formula balance. Detailed case studies of `CAND-004` (Rank 4, $30.16$, preferred coverage $50.0\%$, required coverage $33.33\%$) and `CAND-009` (Rank 7, $20.50$, preferred coverage $50.0\%$, required coverage $16.67\%$), demonstrating how the 70% required weighting properly prevents non-essential skills from inflating candidate rank.
  6. *Section 6  -  TF-IDF Similarity and Composite Score Analysis*: Statistical correlation analysis based on authoritative CSV columns `TF-IDF Cosine Similarity` and `Composite Match Score` ($N=10$) demonstrating strong positive alignment (Pearson $r = 0.8525$, Spearman $\rho = 0.7333$). Detailed exploration of why lexical similarity correlates with score but cannot validate real-world problem-solving, competence, or causal job performance.
  7. *Section 7  -  Key Findings*: Six concise, evidence-backed findings covering cohort spread, top-tier differentiation, mandatory skill weighting effectiveness, SQL/Python prevalence, acute data cleaning/statistics gaps, and lexical similarity bounds.
  8. *Section 8  -  Limitations*: Nine critical methodological and technical limitations documented (lexical matching vulnerability, absence of semantic embeddings, static weights, small synthetic cohort $N=10$, text extraction variability, lack of experience weighting, keyword stuffing susceptibility, absence of soft skills assessment, non-validated scoring).
  9. *Section 9  -  Recommendations and Future Improvements*: Seven structured recommendations for future technical evolution (dense transformer embeddings, hybrid search, experience weighting, configurable UI weights, LLM explainability, bias auditing, ATS formatting guidelines).
  10. *Section 10  -  Conclusion*: Final synthesis emphasizing the system's role as an objective, transparent, educational screening tool that accelerates recruiter review while strictly mandating human-in-the-loop decision-making.
- **Cross-Chart Consistency Verification**:
  - Dynamically verified SQL detection count ($7/10$, $70\%$) across all data sources, binary heatmap matrix column sums, and horizontal frequency chart bars.
  - Added regression test `test_heatmap_and_frequency_chart_skill_counts_consistency` to [`tests/test_visualization.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_visualization.py).
- **Automated Testing & Results**:
  - Executed full automated test suite `pytest -v`: **154/154 passed** in 27.90s across all 7 test modules (`test_ranking.py`, `test_report_generator.py`, `test_resume_parser.py`, `test_scoring.py`, `test_similarity.py`, `test_skill_extractor.py`, `test_text_cleaner.py`, `test_visualization.py`).
- **Status**: Phase 12 Approved by Akash Das.

### [2026-11-20] - Phase 13: Dashboard Development using Streamlit
- **Action**: Developed a professional, interactive Streamlit web dashboard in [`app.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/app.py) integrating the end-to-end resume screening and analytics pipeline.
- **Scope & Phase Boundaries**:
  - Phase 13 of the 14-phase roadmap completed.
  - Strict phase boundaries preserved: zero Git publication, tagging, or remote pushes performed (Phase 14 strictly reserved for GitHub Publication).
  - Candidate scores, ranking formulas, tie-breaking criteria, and Phase 11 static assets in `reports/figures/` were completely preserved without modification.
  - Candidate privacy strictly upheld: no candidate personal names, emails, phone numbers, or addresses appear anywhere in dashboard tables, metric cards, deep dives, or exports.
- **Architectural Modules Created**:
  1. [`src/theme_manager.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/src/theme_manager.py):
     - Centralized color definitions for Light Mode (Clean Slate `#F8FAFC`, Navy `#1F4E78`, Charcoal `#0F172A`) and Dark Mode (Deep Midnight `#0B1120`, Slate `#1E293B`, Sky Blue `#38BDF8`).
     - Scoped dynamic CSS injection function `get_theme_css(theme)` targeting `.stApp`, `.kpi-card`, buttons, file uploader, tabs, alert banners, metric cards, and candidate table zebra striping.
     - Contrast and readability guarantees ensuring zero dark-on-dark or white-on-white text artifacts.
     - HTML rendering helpers for KPI metric cards, review category badges (`High Match`, `Moderate Match`, `Low Match`), and detection status tags (`Matched`, `Missing`, `Preferred`).
  2. [`src/dashboard_charts.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/src/dashboard_charts.py):
     - Six theme-aware dynamic Matplotlib chart renderers:
       - `render_score_comparison`: Horizontal bar chart with ranking order preservation and score value annotations.
       - `render_score_distribution`: 10-point histogram with cohort mean and median indicator lines.
       - `render_skill_coverage_comparison`: Grouped bar chart contrasting 70% required coverage against 10% preferred coverage.
       - `render_similarity_vs_score`: Annotated scatter plot correlating TF-IDF cosine similarity with composite match score.
       - `render_category_distribution`: High-contrast donut chart displaying review category proportions.
       - `render_required_skill_frequency`: Horizontal frequency bar chart displaying cohort detection counts for mandatory skills.
     - Dynamic palette adaptation: Background (`#FFFFFF` in Light, `#1E293B` in Dark), axes, labels, tick colors, and grid lines adjust automatically.
     - Non-interactive Agg backend with memory-safe `plt.close()` cleanup after every render.
  3. [`src/dashboard_service.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/src/dashboard_service.py):
     - `load_default_benchmark`: Loads canonical Junior Data Analyst job description and JSON requirements taxonomy.
     - `evaluate_sample_resumes`: Orchestrates single-click batch screening of all 10 synthetic candidates matching Phase 9 authoritative scores (`CAND-001` at $65.83$, `CAND-010` at $64.01$, `CAND-006` at $41.20$, down to `CAND-007` at $0.32$).
     - `evaluate_uploaded_resumes`: Resilient multi-file processor for PDF, DOCX, and TXT buffers. Implements extension validation, 0-byte buffer rejection, corrupted file isolation, and partial batch success isolation.
     - `compute_cohort_metrics`: Computes cohort executive statistics (total submitted, scored, errors, top score, mean score, median score, category counts).
     - `generate_dashboard_csv` & `generate_dashboard_excel`: In-memory byte stream exporters for audit-ready CSV and multi-sheet formatted Excel reports.
  4. [`app.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/app.py):
     - Full interactive web interface with responsive multi-column layout.
     - Prominent Light/Dark Mode toggle button in header (` Switch to Dark Mode` / `☀️ Switch to Light Mode`) using persistent session state.
     - Mode A (Benchmark Cohort) & Mode B (Multi-File Uploader) tabbed input controls.
     - Six executive KPI metric cards for rapid recruiter assessment.
     - Tab 1: Comprehensive candidate ranking table with sequential rank, Candidate ID, Composite Score, Required/Preferred Coverage, TF-IDF Sim, and Category, plus one-click CSV and Excel download buttons.
     - Tab 2: Candidate deep-dive inspection with interactive selectbox, canonical skill detection badges, contextual text evidence snippets, and sanitized resume text view.
     - Tab 3: Six theme-aware analytical visualizations rendered responsive to active theme.
     - Tab 4: System architecture, algorithm specifications, and mandatory ethical governance disclosures.
- **Automated Testing Suite ([`tests/test_dashboard.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_dashboard.py))**:
  - Implemented 25 new unit and integration tests:
    - `test_theme_palettes_structure`: Validates color schema keys and hex formatting.
    - `test_theme_palettes_contrast_and_distinction`: Validates background and text contrast across themes.
    - `test_get_theme_colors`: Validates color lookup and fallback defaults.
    - `test_get_theme_css`: Validates CSS structure, style tags, and key class selectors.
    - `test_render_metric_card_html`: Validates KPI card generation across themes.
    - `test_render_category_badges`: Validates High, Moderate, and Low match badges.
    - `test_render_skill_badges`: Validates matched, missing, and preferred skill tags.
    - `test_sample_resumes_count_and_ranks`: Validates 10 candidates with sequential ranks 1..10.
    - `test_sample_resumes_exact_phase9_scores`: Validates exact Phase 9 authoritative scores and tie-breaking order.
    - `test_cohort_summary_metrics`: Validates cohort mean, median, max, min, and review tier counts.
    - `test_upload_valid_txt_file`: Validates end-to-end upload and scoring of valid TXT resume.
    - `test_upload_empty_file_handling`: Validates 0-byte file rejection without crash.
    - `test_upload_unsupported_extension`: Validates unsupported file extension rejection (.png).
    - `test_upload_corrupt_file_handling`: Validates corrupt file graceful error handling.
    - `test_upload_partial_batch_isolation`: Validates valid files are processed when mixed with invalid files.
    - `test_generate_dashboard_csv`: Validates CSV export headers, row counts, and formatting.
    - `test_generate_dashboard_excel`: Validates Excel workbook structure, worksheet names, and cell values.
    - `test_candidate_privacy_guarantees`: Asserts absence of personal names, emails, and phone numbers.
    - `test_render_score_comparison_both_themes`: Validates score comparison chart in light and dark mode.
    - `test_render_score_distribution_both_themes`: Validates score distribution chart in light and dark mode.
    - `test_render_skill_coverage_comparison_both_themes`: Validates skill coverage chart in light and dark mode.
    - `test_render_similarity_vs_score_both_themes`: Validates similarity scatter plot in light and dark mode.
    - `test_render_category_distribution_both_themes`: Validates category donut chart in light and dark mode.
    - `test_render_required_skill_frequency_both_themes`: Validates required skill frequency chart in light and dark mode.
    - `test_app_module_imports`: Validates `app.py` module integrity and configuration constants.
    - `test_render_candidate_ranking_table_html_both_themes`: Validates custom accessible HTML ranking table in both themes.
    - `test_dark_mode_is_default_theme`: Validates that Dark Mode is the default experience on fresh sessions.
    - `test_wcag_contrast_ratios`: Validates WCAG 2.2 AA contrast compliance across all theme palette elements.
  - Test Suite Results: **29/29 passed** in `test_dashboard.py`.
  - Full Project Suite: **183/183 passed** across all 8 test modules with 100% pass rate.
- **Visual Assets & Screenshot Verification ([`images/dashboard/`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/))**:
  - Captured 4 full-resolution 1920x1080 interface screenshots using headless Chrome CDP automation:
    - [`images/dashboard/dashboard_dark_mode.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/dashboard_dark_mode.png): 1920x1080 PNG, 196.33 KB (Default Dark Mode, Mode A benchmark evaluation, KPI cards, high-contrast ranking table).
    - [`images/dashboard/dashboard_light_mode.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/dashboard_light_mode.png): 1920x1080 PNG, 218.77 KB (Redesigned Light Mode, Clean Slate palette, high-contrast table, white button text).
    - [`images/dashboard/dashboard_dark_mode_upload.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/dashboard_dark_mode_upload.png): 1920x1080 PNG, 230.07 KB (Dark Mode, Mode B multi-file uploader interface).
    - [`images/dashboard/dashboard_light_mode_upload.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/dashboard_light_mode_upload.png): 1920x1080 PNG, 218.50 KB (Light Mode, Mode B multi-file uploader with clean white dropzone).
  - All 4 screenshots verified: valid PNG format, exact $1920\times 1080$ resolution, file sizes $> 190$ KB, WCAG-compliant contrast, and zero layout cutoffs.

---

## 2026-11-20  -  Phase 13 Final Scoring Reconciliation, Theme Correction & Interaction Audit

- **Author**: Akash Das
- **Scoring Reconciliation Audit**:
  - Comprehensive verification of `src/dashboard_service.py` against authoritative Phase 9 and Phase 10 results (`reports/screening_report_junior_data_analyst.csv`).
  - Confirmed that `evaluate_sample_resumes()` produces the identical scores, coverage ratios, TF-IDF similarities, and rankings to 16 decimal places for all 10 candidates.
  - `CAND-006` verified: Required Coverage = 50.00% (3/6), Preferred Coverage = 33.33% (2/6: NumPy, Machine Learning), TF-IDF Similarity = 0.143527, Composite Match Score = 41.203880 ($\approx 41.20$).
  - Root Cause Investigation: Confirmed that `src/dashboard_service.py` has always implemented the correct logic. The discrepancy reported in review was strictly due to a manual transcription error in an earlier chat-level markdown table.
  - Batch Vectorization Mechanics (Mode B): Documented that Mode A uses fixed corpus $N=11$, while Mode B builds corpus dynamically over $N=1+M$ uploaded resumes. Within any single uploaded batch, all resumes share identical vectorizer, vocabulary, and IDF matrix.
  - Regression Protection: Added `test_sample_resumes_exact_phase9_scores` and `test_full_reconciliation_against_authoritative_csv` to ensure continuous numerical parity.
- **Theme Correction & Dark Mode Default**:
  - Dark Mode established as default theme: `.streamlit/config.toml` set to `base = "dark"` and `app.py` initializes `st.session_state["theme"] = "dark"`.
  - Toggle button: Displays `☀️ Switch to Light Mode` when in Dark Mode, and ` Switch to Dark Mode` when in Light Mode.
  - Complete Light Mode Redesign:
    - Base background: `#F8FAFC`, card background: `#FFFFFF`, borders: `#CBD5E1`, primary brand: `#1D4ED8`, table headers: `#E2E8F0` with text `#0F172A`.
    - Button text visibility: Removed unqualified global text selector; strictly scoped `.stButton > button * { color: #FFFFFF !important; }` and `.stDownloadButton > button * { color: #FFFFFF !important; }`.
    - Tab styling: Selected tab active fill `#1D4ED8` with white text; inactive tabs clean `#334155`.
    - File Uploader: Dropzone restyled with clean `#FFFFFF` background, `#CBD5E1` dashed border, and `#0F172A` labels.
    - Ethical Alerts: Styled `[data-testid="stAlert"]` with soft blue `#EFF6FF` background, `#BFDBFE` border, and high-contrast `#1E3A8A` text.
    - Custom Accessible Ranking Table: Implemented `render_candidate_ranking_table_html()` providing responsive zebra striping, badge styling, and high contrast in both themes.
- **Visual Evidence & Defect Resolution**:
  - Visually audited all 4 dashboard screenshots using multimodal inspection.
  - Resolved two visual rendering defects identified during audit:
    1. Candidate table indentation bug: Removed all leading indentation spaces in `render_candidate_ranking_table_html()` and migrated `app.py` from `st.markdown()` to native `st.html()` to prevent markdown code-block escaping.
    2. Sidebar ethical safeguards alert container: Added comprehensive CSS coverage targeting inner Emotion containers `[data-testid="stAlert"] [role="alert"]` and `section[data-testid="stSidebar"] [data-testid="stAlert"] > div` for high-contrast `#1E3A8A` text on `#EFF6FF` background in Light Mode.
    3. Mode B tab switching: Corrected CDP tab-group query selector to reliably target the input tab group (`stTabs[0]`).
  - Captured and validated all 4 requested 1920x1080 screenshots in `images/dashboard/`:
    - `dashboard_dark_mode.png` (1920x1080 PNG, 204.96 KB)
    - `dashboard_light_mode.png` (1920x1080 PNG, 199.74 KB)
    - `dashboard_dark_mode_upload.png` (1920x1080 PNG, 196.17 KB)
    - `dashboard_light_mode_upload.png` (1920x1080 PNG, 190.28 KB)
- **Automated Verification & Theme Interaction Tests**:
  - Live headless Chrome browser CDP test verified:
    - Fresh session starts in Dark Mode with `☀️ Switch to Light Mode` button (`fresh_session_dark: True`).
    - Clicking button switches to Light Mode with ` Switch to Dark Mode` button (`switched_to_light: True`).
    - Clicking button again switches back to Dark Mode with `☀️ Switch to Light Mode` (`switched_back_to_dark: True`).
    - Candidate table survives with all 10 candidate rows across both transitions (`table_rows: 10`).
  - Added 4 dedicated automated theme-interaction tests to `tests/test_dashboard.py`:
    - `test_actual_theme_toggle_interaction_and_label_updates`
    - `test_screening_results_survive_theme_toggle`
    - `test_uploaded_resumes_survive_theme_toggle`
    - `test_theme_toggle_does_not_invoke_pipeline_recomputation`
  - Full pytest suite: **187/187 passed** in 27.33s across all 8 test modules.
- **Status**: Phase 13 Final Theme Interaction Verification Complete. Ready for Phase 14 (GitHub Publication) upon user approval.

---

## 2026-11-21  -  Phase 13 Post-Approval Light Mode Sidebar Text Rendering Fix

- **Author**: Akash Das
- **Defect Analysis & Root Cause**:
  - User-provided visual defect audit (`media_1795202908739_2302f202.jpg`) identified that in Light Mode, sidebar text in "View Benchmark Requirements" expander and "Review Tier Boundaries" remained white/near-white against light backgrounds (`#F1F5F9` and `#FFFFFF`), rendering the content illegible.
  - Root Cause: Streamlit's Emotion CSS engine under `base = "dark"` in `.streamlit/config.toml` injected default dark-theme white styles (`color: rgb(250, 250, 250)`) onto list items (`ul, ol, li`), mathematical expressions (`.katex, .katex *`), bold text (`strong, b`), and expander internals (`[data-testid="stExpanderDetails"]`). While sidebar headings and general paragraphs had basic selectors, these nested elements lacked explicit Light Mode overrides.
- **CSS Corrections Implemented in [`src/theme_manager.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/src/theme_manager.py)**:
  1. *Sidebar List Elements*: Added explicit rules for `section[data-testid="stSidebar"] ul, ol, li` with `color: {c["text_secondary"]} !important;` and `section[data-testid="stSidebar"] li::marker` with `color: {c["brand_primary"]} !important;`.
  2. *Sidebar Headings & Bold Text*: Added explicit rules for `section[data-testid="stSidebar"] h1..h6` and `section[data-testid="stSidebar"] strong, b` with `color: {c["text_primary"]} !important; font-weight: 700 !important;`.
  3. *Mathematical Formulas (KaTeX)*: Added `section[data-testid="stSidebar"] .katex, section[data-testid="stSidebar"] .katex *` with `color: {c["text_secondary"]} !important;` and global `.katex, .katex *` with `color: {c["text_primary"]} !important;`, ensuring symbols like $\ge, \le, <$ and numerical thresholds render with crisp contrast.
  4. *Expander Component (Global & Sidebar Scope)*:
     - Card container: `[data-testid="stExpander"]` with `background-color: {c["card_bg"]} !important; border: 1px solid {c["card_border"]} !important; border-radius: 8px !important; overflow: hidden !important;`.
     - Summary bar: `[data-testid="stExpander"] summary` styled with `#FFFFFF` resting background in Light Mode (`#1E293B` in Dark Mode), hover background `#F1F5F9` (`#334155` in Dark Mode), and text `color: {c["text_primary"]} !important; font-weight: 600 !important;`.
     - Summary SVG icon: `fill: {c["text_primary"]} !important; color: {c["text_primary"]} !important;`.
     - Details container: `[data-testid="stExpanderDetails"]` with `background-color: {c["card_bg"]} !important; border-top: 1px solid {c["card_border"]} !important;`.
     - Details body text: `p, span, ul, ol, li` with `color: {c["text_secondary"]} !important;`, `strong, b` with `color: {c["text_primary"]} !important;`, and `li::marker` with `color: {c["brand_primary"]} !important;`.
- **Visual Verification & Screenshot Capture ([`images/dashboard/`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/))**:
  - Programmatically recaptured 1920x1080 screenshots with the "View Benchmark Requirements" expander clicked and expanded using headless Chrome CDP automation:
    - [`images/dashboard/dashboard_light_mode.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/dashboard_light_mode.png): 1920x1080 PNG, 201.44 KB. Verified high-contrast dark slate (`#334155`) text on clean white (`#FFFFFF`) expander background; bold headings in dark charcoal (`#0F172A`); blue bullet markers (`#1D4ED8`); all skill names fully legible.
    - [`images/dashboard/dashboard_dark_mode.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/dashboard_dark_mode.png): 1920x1080 PNG, 204.95 KB. Verified zero Dark Mode regressions; light text (`#F8FAFC` / `#94A3B8`) on dark cards (`#1E293B`) on sidebar background (`#070C18`).
  - Scrolled sidebar verification: Validated that lower sidebar sections ("Review Tier Boundaries" and "Ethical Safeguards") display high-contrast text, math symbols ($\ge, \le, <$), and deep navy alert text (`#1E3A8A` on `#EFF6FF`).
- **Automated Testing Suite ([`tests/test_dashboard.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_dashboard.py))**:
  - Implemented new regression test `test_sidebar_and_expander_css_rules`:
    - Asserts presence of `section[data-testid="stSidebar"] ul`, `li`, and `.katex` selectors in generated CSS for both themes.
    - Asserts presence of `[data-testid="stExpander"]`, `[data-testid="stExpanderDetails"]`, and `[data-testid="stExpander"] summary` selectors in generated CSS for both themes.
  - Executed full test suite: **188/188 passed** in 37.24s across all 8 test modules (`test_dashboard.py`, `test_ranking.py`, `test_report_generator.py`, `test_resume_parser.py`, `test_scoring.py`, `test_similarity.py`, `test_skill_extractor.py`, `test_text_cleaner.py`, `test_visualization.py`).
- **Status**: Post-Approval Light Mode Sidebar Text Rendering Fix Complete. Ready for Phase 14 (GitHub Publication) upon user approval.
