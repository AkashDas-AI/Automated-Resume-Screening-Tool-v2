# Modules & Technical Reference

## Automated Resume Screening Tool
**Author:** Akash Das  
**Workspace:** `D:\Projects\Python\Automated Resume Screening Tool`  

---

## 1. Architectural Map of Source Modules

The project is structured with strict separation of concerns, isolating text extraction, feature engineering, statistical modeling, visualization, and presentation into dedicated, testable Python modules located in `src/`.

```text
src/
├── resume_parser.py        # Multi-format document ingestion (PDF, DOCX, TXT)
├── text_cleaner.py         # Noise reduction, case folding & token preservation
├── skill_extractor.py      # Dual-tier regex matching & contextual snippet extraction
├── similarity.py          # Unified single-corpus TF-IDF vectorization & cosine sim
├── scoring.py             # Multi-factor 70/10/20 composite score calculation
├── ranking.py             # Deterministic 4-tier tie-breaking & review tiering
├── report_generator.py     # CSV, Markdown & multi-sheet formatted Excel generation
├── visualization.py        # Static Matplotlib analytics figures for reporting
├── dashboard_service.py    # Service orchestrator for Streamlit application
├── dashboard_charts.py     # Dynamic theme-aware Matplotlib renderers for UI
└── theme_manager.py        # WCAG AA palettes, CSS injection & accessible HTML
app.py                      # Main Streamlit web application entry point
```

---

## 2. Source Module Specifications

### 2.1 `src/resume_parser.py`
Provides resilient document ingestion across multiple file formats.

- `extract_text_from_file(file_path: Union[str, Path, io.BytesIO], filename: Optional[str] = None) -> str`:
  - Dispatches to format-specific extractors based on file extension.
  - Validates file presence and rejects 0-byte files with `FileExtractionError`.
  - Supports both filesystem paths and in-memory byte streams for web uploads.
- `extract_text_from_pdf(stream: Union[Path, io.BytesIO]) -> str`:
  - Powered by `PyMuPDF` (`fitz.open()`).
  - Iterates through PDF pages, extracting clean text while filtering out font encoding anomalies.
- `extract_text_from_docx(stream: Union[Path, io.BytesIO]) -> str`:
  - Powered by `python-docx` (`docx.Document()`).
  - Extracts text across all document paragraphs and table cells.
- `extract_text_from_txt(stream: Union[Path, io.BytesIO]) -> str`:
  - Decodes plain text using UTF-8 with automatic Latin-1 fallback.
- `class FileExtractionError(Exception)`:
  - Custom exception raised for unsupported formats, empty buffers, or corrupted byte streams.

---

### 2.2 `src/text_cleaner.py`
Performs text normalization and linguistic hygiene while protecting critical technical tokens.

- `clean_text(raw_text: str) -> str`:
  - Converts text to lowercase for canonical matching.
  - Strips email addresses, URLs, and non-printable control characters.
  - Normalizes line endings (`\r\n` $\rightarrow$ `\n`) and collapses multiple consecutive newlines.
  - Replaces tabs and consecutive spaces with single spaces.
  - **Technical Token Preservation:** Uses lookahead/lookbehind patterns to prevent punctuation removal from corrupting technical keywords:
    - Programming languages & frameworks: `c++`, `c#`, `.net`, `asp.net`, `node.js`, `react.js`.
    - Tools & methodologies: `ci/cd`, `scikit-learn`, `power bi`.
- `tokenize_text(cleaned_text: str) -> List[str]`:
  - Splits normalized text into individual tokens for downstream analysis.

---

### 2.3 `src/skill_extractor.py`
Executes taxonomy-based keyword detection with word boundary enforcement and evidence extraction.

- `load_skills_taxonomy(taxonomy_path: Union[str, Path]) -> Tuple[List[str], List[str]]`:
  - Ingests `junior_data_analyst_requirements.json`.
  - Returns two distinct skill lists: `(required_skills, preferred_skills)`.
- `extract_skills(text: str, skills_list: List[str]) -> Tuple[List[str], float, List[Dict[str, str]]]`:
  - Compiles regex patterns with word boundaries (`\b<pattern>\b`) to prevent false-positive substring matches (e.g., "java" in "javascript").
  - Identifies detected canonical skills and computes coverage ratio:
    $$\text{coverage} = \frac{\text{count of unique detected skills}}{\text{total skills in category}}$$
  - Extracts contextual evidence snippets ($\pm 50$ characters around each detected occurrence).
- `extract_context_window(text: str, match_start: int, match_end: int, window: int = 50) -> str`:
  - Slices a context window around the matched keyword, stripping boundary whitespace and newlines for clean presentation.

---

### 2.4 `src/similarity.py`
Constructs single-corpus vector spaces and computes vocabulary-level cosine alignment.

- `build_unified_corpus(jd_text: str, resume_texts: List[str]) -> List[str]`:
  - Prepends the benchmark job description at index 0, followed by candidate resumes.
  - Establishes a shared corpus of size $N = 1 + M$.
- `compute_corpus_tfidf(corpus: List[str]) -> Tuple[TfidfVectorizer, scipy.sparse.csr_matrix]`:
  - Configures `TfidfVectorizer`:
    - `ngram_range=(1, 2)`: Captures unigrams and bigrams.
    - `sublinear_tf=True`: Dampens term frequency ($1 + \log(tf)$) to prevent keyword stuffing.
    - `norm="l2"`: Normalizes vectors to unit length.
  - Fits and transforms the unified corpus, producing a single sparse TF-IDF matrix.
- `calculate_cosine_similarity(tfidf_matrix: scipy.sparse.csr_matrix) -> np.ndarray`:
  - Computes the dot product between the JD vector (row 0) and all candidate vectors (rows 1..M).
  - Returns an array of cosine similarity floats bounded in $[0.0, 1.0]$.

---

### 2.5 `src/scoring.py`
Implements the multi-factor scoring model.

- `calculate_composite_score(req_coverage: float, pref_coverage: float, cosine_sim: float, weights: Optional[Dict[str, float]] = None) -> float`:
  - Applies authoritative weighting parameters:
    - Required Skills Weight: **70%** (0.70)
    - Preferred Skills Weight: **10%** (0.10)
    - Vocabulary Similarity Weight: **20%** (0.20)
  - Mathematical definition:
    $$\text{Score} = (70.0 \times \text{req\_coverage}) + (10.0 \times \text{pref\_coverage}) + (20.0 \times \text{cosine\_sim})$$
  - Clamps output strictly within $[0.0, 100.0]$ with full floating-point precision.

---

### 2.6 `src/ranking.py`
Implements deterministic sorting and administrative category assignment.

- `rank_candidates(candidate_records: List[Dict[str, Any]], thresholds: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]`:
  - Sorts candidate records using a 4-tier deterministic tie-breaking key:
    $$\text{Key} = \Big(-\text{score},\; -\text{req\_cov},\; -\text{pref\_cov},\; -\text{cosine\_sim},\; \text{candidate\_id}\Big)$$
  - Assigns sequential integer ranks: $1, 2, \dots, N$.
  - Assigns review category based on threshold boundaries.
- `assign_review_category(score: float, thresholds: Optional[Dict[str, float]] = None) -> str`:
  - Default thresholds:
    - $\text{Score} \ge 70.0 \rightarrow$ `"High Match"`
    - $40.0 \le \text{Score} < 70.0 \rightarrow$ `"Moderate Match"`
    - $\text{Score} < 40.0 \rightarrow$ `"Low Match"`

---

### 2.7 `src/report_generator.py`
Generates comprehensive screening reports in CSV, Markdown, and formatted Excel formats.

- `generate_csv_report(ranked_candidates: List[Dict], output_path: Union[str, Path]) -> Path`:
  - Writes audit-ready CSV file with complete candidate metrics, rankings, and timestamps.
- `generate_excel_report(ranked_candidates: List[Dict], cohort_summary: Dict, output_path: Union[str, Path]) -> Path`:
  - Powered by `openpyxl`.
  - Produces a multi-worksheet formatted Excel workbook:
    1. `Candidate Rankings`: Primary table with zebra striping, custom column widths, and cell formatting.
    2. `Cohort Summary`: Executive statistics (mean, median, std dev, review tier counts).
    3. `Skill Breakdown`: Binary detection matrix indicating presence/absence of all 12 skills per candidate.
    4. `Metadata & Parameters`: System configuration, algorithm weights, and execution timestamp.
- `generate_markdown_report(ranked_candidates: List[Dict], cohort_summary: Dict, output_path: Union[str, Path]) -> Path`:
  - Formats an executive summary markdown document suitable for repository documentation and recruiter memos.

---

### 2.8 `src/visualization.py`
Generates static analytical figures for reports and documentation.

- Generates 6 core Matplotlib figures saved to `reports/figures/`:
  1. `candidate_score_comparison.png`: Horizontal bar chart of composite scores in ranked order.
  2. `score_distribution.png`: Histogram with cohort mean and median indicator lines.
  3. `skill_coverage_comparison.png`: Grouped bar chart comparing required vs preferred coverage.
  4. `similarity_vs_score.png`: Scatter plot correlating TF-IDF cosine similarity against composite score.
  5. `review_category_distribution.png`: Donut chart showing review tier breakdown.
  6. `candidate_skill_heatmap.png`: Binary detection matrix ($10 \times 12$) showing exact candidate-by-skill matches.
- `plot_required_skill_frequency(...)`: Optional frequency chart illustrating cohort detection counts for mandatory skills.

---

### 2.9 `src/dashboard_service.py`
Orchestrator connecting the core NLP engine with the interactive Streamlit user interface.

- `load_default_benchmark() -> Tuple[str, List[str], List[str]]`:
  - Loads benchmark job description text and skills taxonomy.
- `evaluate_sample_resumes() -> Tuple[List[Dict], Dict]`:
  - Executes batch screening over the 10 pre-configured synthetic sample resumes, producing results that strictly match approved Phase 9 benchmark scores.
- `evaluate_uploaded_resumes(uploaded_files: List[Any]) -> Tuple[List[Dict], Dict]`:
  - Handles dynamic multi-file uploads from Streamlit.
  - Implements extension validation, 0-byte checks, corrupt file isolation, and partial batch success handling.
- `compute_cohort_metrics(ranked_candidates: List[Dict]) -> Dict[str, Any]`:
  - Computes executive metrics: total submitted, scored, errors, top score, cohort mean, median, and category counts.
- `generate_dashboard_csv(ranked_candidates: List[Dict]) -> bytes`:
  - In-memory CSV byte stream exporter.
- `generate_dashboard_excel(ranked_candidates: List[Dict], cohort_metrics: Dict) -> bytes`:
  - In-memory formatted Excel byte stream exporter.

---

### 2.10 `src/dashboard_charts.py`
Provides dynamic, theme-aware Matplotlib chart renderers for the Streamlit dashboard.

- Functions:
  - `render_score_comparison(candidates, theme="dark")`
  - `render_score_distribution(candidates, theme="dark")`
  - `render_skill_coverage_comparison(candidates, theme="dark")`
  - `render_similarity_vs_score(candidates, theme="dark")`
  - `render_category_distribution(candidates, theme="dark")`
  - `render_required_skill_frequency(candidates, theme="dark")`
- Dynamic theming:
  - Backgrounds, axes, gridlines, tick labels, and fonts adapt automatically to active theme (`dark` vs `light`).
  - Strict memory cleanup using `plt.close(fig)` after every rendering operation.

---

### 2.11 `src/theme_manager.py`
Manages color palettes, dynamic CSS injection, and accessible HTML rendering components.

- `THEME_PALETTES`: Color definition dictionary for Light Mode (`Clean Slate`) and Dark Mode (`Deep Midnight`).
- `get_theme_css(theme: str) -> str`: Generates complete scoped CSS stylesheet for `.stApp`, sidebar, expanders, KPI cards, tables, buttons, and alert boxes.
- `render_metric_card_html(label, value, delta, theme)`: Renders custom responsive KPI card.
- `render_category_badges(category)`: Renders colored badge pills (`High Match`, `Moderate Match`, `Low Match`).
- `render_skill_badges(skill_name, status)`: Renders matched (`green`), missing (`red`), and preferred (`purple`) tags.
- `render_candidate_ranking_table_html(candidates, theme)`: Renders full accessible HTML table with zebra striping and theme-aware contrast.

---

### 2.12 `app.py`
The main web application orchestrating the entire user experience.

- Configures Streamlit page metadata, layout, and initial session state.
- Features prominent Light/Dark mode toggle button in header.
- Implements two evaluation tabs:
  - Mode A: Benchmark Sample Resumes.
  - Mode B: Upload Custom Resumes.
- Displays 6 executive KPI metric cards.
- Presents four organized inspection tabs:
  1. *Candidate Rankings & Reports*: Custom accessible ranking table and one-click CSV/Excel downloads.
  2. *Candidate Deep-Dive & Skills*: Candidate selectbox, skill badges, context evidence snippets, anonymized resume text.
  3. *Analytical Visualizations*: Six responsive, theme-aware charts.
  4. *System Architecture & Governance*: Architecture diagrams, algorithm descriptions, and ethical disclosures.
