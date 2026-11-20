# Visual Assets & Screenshot Guide

## Automated Resume Screening Tool
**Author:** Akash Das  
**Workspace:** `D:\Projects\Python\Automated Resume Screening Tool`  

---

## 1. Overview of Visual Assets

The project maintains two distinct suites of high-resolution visual assets:
1. **Interactive Dashboard Screenshots** (`images/dashboard/`): Full-resolution $1920\times 1080$ captures of the running Streamlit web application in both Dark Mode and Light Mode.
2. **Analytical Screening Visualizations** (`reports/figures/`): Publication-grade static Matplotlib charts illustrating cohort statistical properties, skill distributions, and correlation dynamics.

---

## 2. Interactive Dashboard Screenshots (`images/dashboard/`)

All interface screenshots were captured at full $1920\times 1080$ resolution using automated headless Chrome CDP (Chrome DevTools Protocol) scripts with exact viewport emulation:

| Asset Name | Theme | Mode / View | File Size | Description |
|---|---|---|---:|---|
| [`dashboard_dark_mode.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/dashboard_dark_mode.png) | **Dark Mode** (Default) | Mode A (Benchmark Cohort) | 204.95 KB | Displays the default Deep Midnight interface (`#0B1120`), expanded Benchmark Requirements sidebar, executive KPI metric cards, and the custom accessible candidate ranking table. |
| [`dashboard_light_mode.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/dashboard_light_mode.png) | **Light Mode** | Mode A (Benchmark Cohort) | 201.44 KB | Displays the redesigned Clean Slate interface (`#F8FAFC`), expanded Benchmark Requirements sidebar with crisp dark slate text (`#334155`), white button text, and high-contrast table styling. |
| [`dashboard_dark_mode_upload.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/dashboard_dark_mode_upload.png) | **Dark Mode** | Mode B (Upload Custom Resumes) | 200.88 KB | Illustrates the multi-file drag-and-drop uploader interface in Dark Mode, showing file type tags, dropzone border, and evaluation action controls. |
| [`dashboard_light_mode_upload.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/images/dashboard/dashboard_light_mode_upload.png) | **Light Mode** | Mode B (Upload Custom Resumes) | 194.84 KB | Illustrates the multi-file drag-and-drop uploader in Light Mode, showing pure white dropzone cards (`#FFFFFF`) with accessible dashed borders (`#CBD5E1`). |

### Key UI Component Breakdown
- **Theme Toggle Header:** Located in top-right header; updates dynamically (`☀️ Switch to Light Mode` / ` Switch to Dark Mode`).
- **Sidebar Benchmark Panel:** Collapsible expander displaying Mandatory Skills (70% weight), Preferred Skills (10% weight), and Vocabulary Context (20% weight) with blue bullet markers.
- **Review Tier Boundaries:** Visual legend detailing High Match ($\ge 70.0$), Moderate Match ($40.0 \le \text{Score} < 70.0$), and Low Match ($< 40.0$).
- **Ethical Safeguards Alert:** High-contrast notification banner reinforcing mandatory human-in-the-loop review.
- **Executive Metric Cards:** Multi-column KPI cards displaying Total Submitted, Successfully Scored, Errors, Top Score ($65.83$), Cohort Mean ($30.07$), and Review Tier breakdown.
- **Ranking Table:** Striped, high-contrast HTML table featuring color-coded review badges and full precision metrics.

---

## 3. Analytical Screening Visualizations (`reports/figures/`)

Generated via `src/visualization.py` using non-interactive Matplotlib Agg rendering:

| Figure File | Chart Type | Dimensions | Key Analytical Finding Illustrated |
|---|---|---:|---|
| [`candidate_score_comparison.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/candidate_score_comparison.png) | Horizontal Bar Chart | $10 \times 6$ in | Displays all 10 candidates in strictly descending rank order, showing CAND-001 at $65.83$ down to CAND-007 at $0.32$. |
| [`score_distribution.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/score_distribution.png) | 10-Point Histogram | $8 \times 5$ in | Shows cohort score dispersion with vertical dashed lines marking Cohort Mean ($30.07$) and Median ($24.19$). |
| [`skill_coverage_comparison.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/skill_coverage_comparison.png) | Grouped Bar Chart | $10 \times 6$ in | Contrasts 70% Mandatory Required Coverage (Navy) against 10% Secondary Preferred Coverage (Sky Blue) per candidate. |
| [`similarity_vs_score.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/similarity_vs_score.png) | Scatter Plot with Annotations | $8 \times 6$ in | Illustrates strong linear correlation ($r = 0.887$) between TF-IDF Cosine Similarity and Composite Score. |
| [`review_category_distribution.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/review_category_distribution.png) | High-Contrast Donut Chart | $7 \times 7$ in | Displays cohort review tier proportions: 0% High Match, 30% Moderate Match (3 candidates), 70% Low Match (7 candidates). |
| [`candidate_skill_heatmap.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/candidate_skill_heatmap.png) | Binary Matrix Heatmap | $12 \times 7$ in | $10 \times 12$ matrix displaying exact presence (1, Dark Slate) or absence (0, Light Gray) of each skill per candidate. |
| [`required_skill_frequency.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/required_skill_frequency.png) | Horizontal Frequency Chart | $8 \times 5$ in | Shows detection frequencies across mandatory skills: Python ($8/10$), SQL ($7/10$), Pandas ($6/10$), Data Analysis ($6/10$), Data Cleaning ($5/10$), Statistics ($4/10$). |

---

## 4. Visual Verification Standards

Every visual asset in the repository adheres to strict production criteria:
1. **Resolution & Density:** Interface screenshots are captured at full $1920\times 1080$ resolution; static figures are rendered at 300 DPI for print and display clarity.
2. **WCAG 2.2 AA Contrast:** All typography and chart annotations maintain a minimum 4.5:1 contrast ratio against their respective backgrounds in both Light and Dark themes.
3. **Zero Layout Cutoffs:** Text labels, chart axes, legends, and table cells are dynamically padded to prevent clipping.
