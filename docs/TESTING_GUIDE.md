# Testing & Quality Assurance Guide

## Automated Resume Screening Tool
**Author:** Akash Das  
**Test Framework:** `pytest` (v9.2.0)  
**Workspace:** `D:\Projects\Python\Automated Resume Screening Tool`  

---

## 1. Test Suite Architecture

The system is validated by an extensive automated test suite comprising **188 unit, integration, and regression tests** organized across 8 test modules in `tests/` (plus `tests/__init__.py`). Every pipeline stage is covered by deterministic assertions with zero test flakiness.

```text
tests/
├── __init__.py                 # Test package initialization
├── test_dashboard.py           # 34 tests: Service layer, uploads, theme toggles & WCAG
├── test_ranking.py             # 20 tests: Deterministic 4-tier tie-breaking & review tiers
├── test_report_generator.py    # 18 tests: CSV, Excel (openpyxl) & Markdown exports
├── test_resume_parser.py       # 24 tests: PDF, DOCX, TXT extraction & error isolation
├── test_scoring.py             # 22 tests: Multi-factor composite scoring & TF-IDF similarity
├── test_skill_extractor.py     # 25 tests: Regex boundary matching, aliases & context snippets
├── test_text_cleaner.py        # 24 tests: Normalization, cleaning & tech token preservation
└── test_visualization.py       # 21 tests: Static Matplotlib analytics figure generation
```

---

## 2. Test Module Breakdown

| Module | Test Count | Scope & Verification Objective |
|---|---:|---|
| [`tests/test_dashboard.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_dashboard.py) | 34 | Streamlit dashboard service orchestration; Mode A exact Phase 9 score parity; Mode B multi-file uploads; corrupt file isolation; theme state persistence; WCAG 2.2 AA contrast compliance; sidebar CSS rules. |
| [`tests/test_ranking.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_ranking.py) | 20 | Strict descending score ordering; 4-tier tie-breaking resolution; precision down to $10^{-6}$; review tier thresholds (`High`, `Moderate`, `Low`); candidate ID stability. |
| [`tests/test_report_generator.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_report_generator.py) | 18 | UTF-8 CSV report generation; multi-worksheet formatted Excel generation via `openpyxl`; cell formatting; executive Markdown memo generation. |
| [`tests/test_resume_parser.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_resume_parser.py) | 24 | Ingestion of PDF, DOCX, and TXT files; validation of file existence; 0-byte file rejection; corrupted byte stream handling; `FileExtractionError` propagation. |
| [`tests/test_scoring.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_scoring.py) | 22 | Linear composite score weighting ($70\% \text{Req} + 10\% \text{Pref} + 20\% \text{Sim}$); single-corpus TF-IDF cosine similarity bounds $[0.0, 1.0]$; parameter validation; score bounds $[0.0, 100.0]$. |
| [`tests/test_skill_extractor.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_skill_extractor.py) | 25 | Loading of JSON skill taxonomy; word-boundary pattern matching (`\b<skill>\b`); false-positive avoidance; technical aliases; contextual snippet extraction ($\pm 50$ chars). |
| [`tests/test_text_cleaner.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_text_cleaner.py) | 24 | Case folding; newline normalization; whitespace collapsing; preservation of technical keywords (`C++`, `C#`, `.NET`, `CI/CD`, `Node.js`, `scikit-learn`, `Power BI`). |
| [`tests/test_visualization.py`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/tests/test_visualization.py) | 21 | Generation of 6 static Matplotlib figures; ranking order preservation; heatmap ground-truth verification; data consistency; candidate privacy enforcement. |
| **Total** | **188** | **Full project coverage across all 14 phases.** |

---

## 3. How to Run the Tests

Ensure your virtual environment is activated before running pytest:

### 3.1 Run the Full Test Suite
To execute all 188 tests with verbose reporting:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Expected output:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.2.0, pluggy-1.7.0
rootdir: D:\Projects\Python\Automated Resume Screening Tool
configfile: pytest.ini
collected 188 items

tests/test_dashboard.py ..................................              [ 18%]
tests/test_ranking.py ....................                              [ 28%]
tests/test_report_generator.py ..................                       [ 38%]
tests/test_resume_parser.py ........................                    [ 51%]
tests/test_scoring.py ......................                            [ 62%]
tests/test_skill_extractor.py .........................                 [ 76%]
tests/test_text_cleaner.py ........................                     [ 88%]
tests/test_visualization.py .....................                       [100%]

============================ 188 passed in 30.30s =============================
```

### 3.2 Run a Specific Test Module
To execute tests for a single module:

```powershell
# Run dashboard and theme tests
.\.venv\Scripts\python.exe -m pytest tests/test_dashboard.py -v

# Run ranking and tie-breaking tests
.\.venv\Scripts\python.exe -m pytest tests/test_ranking.py -v

# Run parser tests
.\.venv\Scripts\python.exe -m pytest tests/test_resume_parser.py -v
```

### 3.3 Run a Targeted Test Function
To execute an individual test function using the `-k` pattern matching flag:

```powershell
# Run authoritative Phase 9 reconciliation test
.\.venv\Scripts\python.exe -m pytest -k test_sample_resumes_exact_phase9_scores -v

# Run WCAG contrast verification test
.\.venv\Scripts\python.exe -m pytest -k test_wcag_contrast_ratios -v

# Run sidebar CSS rule verification
.\.venv\Scripts\python.exe -m pytest -k test_sidebar_and_expander_css_rules -v
```

---

## 4. Key Quality Assurance Guarantees

### 4.1 Authoritative Numerical Parity
The test suite enforces exact mathematical alignment between the dashboard service (`src/dashboard_service.py`) and the approved Phase 9 authoritative scores (`reports/screening_report_junior_data_analyst.csv`). Candidate scores, coverage percentages, and cosine similarities are validated to multiple decimal places.

### 4.2 WCAG 2.2 AA Contrast Compliance
The test `test_wcag_contrast_ratios` computes relative luminance according to the W3C WCAG 2.2 algorithm:
$$L = 0.2126 R_{sRGB} + 0.7152 G_{sRGB} + 0.0722 B_{sRGB}$$
$$\text{Contrast Ratio} = \frac{L_1 + 0.05}{L_2 + 0.05}$$
Every text, button, card, header, and badge combination in both Light Mode and Dark Mode is strictly asserted to meet or exceed the **4.5:1** contrast threshold (with several elements achieving $> 14:1$).

### 4.3 Candidate Privacy Enforcement
The test `test_candidate_privacy_guarantees` scans all dashboard output tables, metric cards, exported CSV strings, and Excel cell values to ensure that Personally Identifiable Information (candidate names, emails, phone numbers, street addresses) is strictly absent.
