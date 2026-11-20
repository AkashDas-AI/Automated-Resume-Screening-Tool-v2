# Automated Resume Screening Tool — Insights and Interpretation

**Project:** Automated Resume Screening Tool  
**Author:** Akash Das  
**Domain:** Natural Language Processing (NLP) / Data Analytics  
**Date:** November 19, 2026  
**Document Version:** 1.0.0  

---

## 1. Executive Summary

This report presents an evidence-based analytical interpretation of the automated resume screening experiment conducted as part of the **Automated Resume Screening Tool** portfolio project by **Akash Das**. 

The primary objective of this experiment is to evaluate how a deterministic, multi-stage Natural Language Processing (NLP) screening pipeline evaluates, scores, and ranks candidate resumes against a structured job description. Using a benchmark target role of **Junior Data Analyst** and a synthetic evaluation cohort of **10 fictional candidate resumes** spanning PDF, DOCX, and plain-text formats, the system parsed unstructured text, normalized technical tokens, performed deterministic skill matching against a canonical taxonomy, calculated corpus-level TF-IDF cosine similarities, and computed transparent composite relevance scores.

### Key Observations
1. **Bimodal Score Distribution:** Composite scores ranged from **0.32** to **65.83** (out of 100), with a cohort mean of **30.07** and a median of **24.19**. Candidates separated into two distinct clusters: a moderate-match group aligned with data analytics fundamentals, and a low-match group representing tangential software engineering or non-technical profiles.
2. **Dominance of Core Requirements:** The 70% scoring weight allocated to mandatory skills proved to be the primary rank determinant. Candidates with high preferred skill coverage but low required skill coverage (e.g., `CAND-004` and `CAND-009`) were appropriately placed below candidates who satisfied baseline requirements.
3. **Decisive Tie-Breaking at the Top:** The top two candidates, `CAND-001` (Score: 65.83) and `CAND-010` (Score: 64.01), shared identical required skill coverage (83.33%), with the final ranking decided by preferred skill coverage (16.67% vs. 0.00%) and TF-IDF similarity (0.2916 vs. 0.2839).
4. **Prevalence of Technical Tools over Process Keywords:** Database querying (`SQL` at 70%) and scripting (`Python` at 60%) were the most frequently detected skills, while methodology terms such as `Data Cleaning` (10%) and `Data Analysis` (20%) exhibited substantial detection gaps across resumes.

### Critical Limitations
This screening prototype was developed for **educational and portfolio demonstration purposes**. All evaluations were conducted on a synthetic cohort of ten fictional resumes evaluated against a single target job description. Composite scores reflect **surface-level lexical and textual overlap**, not actual candidate competence, practical problem-solving capability, or future job performance. Under no circumstances should this system be deployed for automated candidate rejection or autonomous hiring decisions.

---

## 2. Candidate Pool Analysis

The evaluation cohort comprises 10 synthetic candidate resumes (`CAND-001` through `CAND-010`) designed to represent diverse technical backgrounds, ranging from well-matched data analytics aspirants to web developers, backend engineers, and non-technical applicants.

### Cohort Summary Statistics

The table below outlines the descriptive statistics derived from the official Phase 10 CSV and Excel screening reports ([`screening_report_junior_data_analyst.csv`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/screening_report_junior_data_analyst.csv) and [`screening_report_junior_data_analyst.xlsx`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/screening_report_junior_data_analyst.xlsx)):

| Metric | Numerical Value | Description & Calculation Method |
|---|:---:|---|
| **Total Candidates Evaluated ($N$)** | 10 | 100% synthetic cohort across PDF (4), DOCX (3), and TXT (3) formats |
| **Maximum Composite Score** | 65.83 | Candidate `CAND-001` (Rank 1, unrounded: $65.831385$) |
| **Minimum Composite Score** | 0.32 | Candidate `CAND-007` (Rank 10, unrounded: $0.323861$) |
| **Mean Composite Score ($\mu$)** | 30.07 | Arithmetic mean across cohort (unrounded: $30.068322$) |
| **Median Composite Score ($M$)** | 24.19 | 50th percentile midpoint between `CAND-008` and `CAND-002` (unrounded: $24.190608$) |
| **Sample Standard Deviation ($s$)** | 21.24 | Sample convention with Bessel's correction ($ddof=1$, unrounded: $21.240409$) |
| **Population Standard Deviation ($\sigma$)** | 20.15 | Population convention ($ddof=0$, unrounded: $20.150421$) |
| **First Quartile ($Q_1$)** | 18.46 | 25th percentile via linear interpolation (or $17.77$ via Tukey's lower-half median) |
| **Third Quartile ($Q_3$)** | 38.44 | 75th percentile via linear interpolation (or $41.20$ via Tukey's upper-half median) |
| **Interquartile Range ($IQR$)** | 19.99 | $Q_3 - Q_1 = 38.44 - 18.46 = 19.99$ (or $23.43$ via Tukey's hinges: $41.20 - 17.77$) |

### Score Distribution Patterns

As visualized in the cohort histogram ([`score_distribution.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/score_distribution.png)), the composite match scores exhibit a right-skewed, multimodal distribution characterized by two primary clusters:

1. **The Core Match Cluster ($40 - 70$ points):** Comprising three candidates (`CAND-001`, `CAND-010`, `CAND-006`) who demonstrated direct alignment with data analysis competencies.
2. **The Low Match Cluster ($0 - 35$ points):** Comprising seven candidates who either possessed tangential development experience (e.g., Java/Spring Boot in `CAND-003`, Flask/web in `CAND-008`) or completely lacked quantitative skills (e.g., front-end React in `CAND-007`).

The mean score ($30.07$) sits notably higher than the median ($24.19$) due to the upward pull exerted by the top two high-scoring candidates (`CAND-001` at 65.83 and `CAND-010` at 64.01).

### Human-Review Category Breakdown

Candidate categorization is determined by predefined, transparent threshold boundaries:
- **High Match:** Composite Score $\ge 70.0$
- **Moderate Match:** $40.0 \le$ Composite Score $< 70.0$
- **Low Match:** Composite Score $< 40.0$

As illustrated in the donut chart ([`review_category_distribution.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/review_category_distribution.png)), the candidate cohort breakdown is as follows:

| Human-Review Category | Score Threshold | Candidate Count | Cohort Proportion | Candidates Included |
|---|:---:|:---:|:---:|---|
| **High Match** | $\ge 70.0$ | 0 | 0.0% | *None* |
| **Moderate Match** | $40.0 - 69.99$ | 3 | 30.0% | `CAND-001`, `CAND-010`, `CAND-006` |
| **Low Match** | $< 40.0$ | 7 | 70.0% | `CAND-004`, `CAND-008`, `CAND-002`, `CAND-009`, `CAND-005`, `CAND-003`, `CAND-007` |

#### Analytical Insight on Zero "High Match" Candidates
No candidate achieved the "High Match" tier ($\ge 70.0$). This outcome occurs because no synthetic resume achieved 100% coverage across both required and preferred skill sets while simultaneously generating a near-perfect TF-IDF similarity. The highest score reached was **65.83**. This demonstrates that the 70.0 threshold functions as a rigorous bar, preventing premature automated overconfidence and ensuring that human recruiters review all top contenders.

---

## 3. Candidate Ranking Analysis

Phase 9 established a deterministic, full-precision candidate ranking policy utilizing a standardized four-level tie-breaking hierarchy:
1. Higher Composite Match Score
2. Higher Required Skill Coverage
3. Higher Preferred Skill Coverage
4. Higher TF-IDF Cosine Similarity
5. Ascending Candidate ID (deterministic fallback)

### Comprehensive Candidate Ranking Table

The table below summarizes the full evaluation results for all 10 synthetic candidates, verified against [`screening_report_junior_data_analyst.csv`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/screening_report_junior_data_analyst.csv) and [`candidate_score_comparison.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/candidate_score_comparison.png):

| Rank | Candidate ID | Composite Match Score | Required Skill Coverage | Preferred Skill Coverage | TF-IDF Cosine Similarity | Human-Review Category | Primary Differentiating Factors |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **1** | `CAND-001` | **65.83** | 83.33% (5/6) | 16.67% (1/6) | 0.2916 | `Moderate Match` | Top overall score; matched 5 required skills + NumPy; highest TF-IDF similarity. |
| **2** | `CAND-010` | **64.01** | 83.33% (5/6) | 0.00% (0/6) | 0.2839 | `Moderate Match` | Matched 5 required skills (including Basic Statistics); 0 preferred skills. |
| **3** | `CAND-006` | **41.20** | 50.00% (3/6) | 33.33% (2/6) | 0.1435 | `Moderate Match` | Python + Pandas + Statistics; preferred NumPy and Machine Learning. |
| **4** | `CAND-004` | **30.16** | 33.33% (2/6) | 50.00% (3/6) | 0.0912 | `Low Match` | Strong preferred ML skills (50%), but missing core SQL and Statistics. |
| **5** | `CAND-008` | **24.24** | 33.33% (2/6) | 0.00% (0/6) | 0.0453 | `Low Match` | Matched Python and SQL; web/Flask orientation yielded low TF-IDF. |
| **6** | `CAND-002` | **24.14** | 33.33% (2/6) | 0.00% (0/6) | 0.0404 | `Low Match` | Matched Python and SQL; separated from `CAND-008` by 0.0049 TF-IDF similarity. |
| **7** | `CAND-009` | **20.50** | 16.67% (1/6) | 50.00% (3/6) | 0.1919 | `Low Match` | BI specialist (Power BI, Tableau, Excel); missing Python and Pandas. |
| **8** | `CAND-005` | **17.77** | 16.67% (1/6) | 33.33% (2/6) | 0.1386 | `Low Match` | Business analyst profile; matched SQL, Power BI, Excel; no Python. |
| **9** | `CAND-003` | **12.50** | 16.67% (1/6) | 0.00% (0/6) | 0.0415 | `Low Match` | Enterprise Java/Spring engineer; only matched database querying (SQL). |
| **10** | `CAND-007` | **0.32** | 0.00% (0/6) | 0.00% (0/6) | 0.0162 | `Low Match` | Front-end web developer (React/Node.js); zero target domain skill matches. |

### Deep-Dive: Comparative Analysis of Top Candidates

#### `CAND-001` (Rank 1) vs. `CAND-010` (Rank 2)
The contest between the top two candidates provides a clear demonstration of multi-criteria scoring:
- **Required Skill Parity:** Both candidates matched exactly 5 of the 6 required skills (83.33% coverage), contributing an identical $58.33$ points ($0.8333 \times 70$) to their composite scores.
- **Skill Profile Differences:** `CAND-001` matched `Data Cleaning` but lacked `Basic Statistics`, whereas `CAND-010` matched `Basic Statistics` but lacked explicit keyword evidence for `Data Cleaning`.
- **The Deciding Margin:** The difference of **1.82 points** was determined entirely by secondary factors:
  1. `CAND-001` possessed one preferred skill (`NumPy`), adding $1.67$ points ($0.1667 \times 10$), whereas `CAND-010` had zero preferred skills ($0.00$ points).
  2. `CAND-001` achieved slightly higher TF-IDF cosine similarity ($0.2916$ vs. $0.2839$), adding $5.83$ points vs. $5.68$ points.

#### Precision Tie-Breaking: `CAND-008` (Rank 5) vs. `CAND-002` (Rank 6)
Candidates `CAND-008` and `CAND-002` demonstrated identical skill-matching profiles:
- Both matched 2 of 6 required skills (`Python` and `SQL` $\rightarrow 33.33\%$ coverage $\rightarrow 23.33$ points).
- Both matched 0 preferred skills ($0.00\%$ coverage $\rightarrow 0.00$ points).
- The tie was resolved at **Tie-Breaking Level 3 (TF-IDF Cosine Similarity)**: `CAND-008` achieved a similarity of **0.0453** ($0.91$ points) compared to `CAND-002`'s **0.0404** ($0.81$ points). The resulting composite score difference of **0.10 points** ($24.24$ vs. $24.14$) broke the tie without resorting to arbitrary candidate ID sorting.

---

## 4. Required Skill Gap Analysis

The benchmark Junior Data Analyst requirements document ([`junior_data_analyst_requirements.json`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/data/job_descriptions/junior_data_analyst_requirements.json)) designates six mandatory technical competencies.

### Cohort Prevalence of Required Skills

The table below summarizes the audited detection frequencies, verified against the candidate skill heatmap ([`candidate_skill_heatmap.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/candidate_skill_heatmap.png)) and the skill prevalence bar chart ([`required_skill_frequency.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/required_skill_frequency.png)):

| Required Technical Skill | Canonical Category | Detected Candidates | Cohort Prevalence | Matched Candidate Identifiers | Unmatched Candidate Identifiers |
|---|---|:---:|:---:|---|---|
| **SQL** | Database Querying | **7 / 10** | **70.0%** | `CAND-001`, `CAND-010`, `CAND-008`, `CAND-002`, `CAND-009`, `CAND-005`, `CAND-003` | `CAND-006`, `CAND-004`, `CAND-007` |
| **Python** | Programming Language | **6 / 10** | **60.0%** | `CAND-001`, `CAND-010`, `CAND-006`, `CAND-004`, `CAND-008`, `CAND-002` | `CAND-009`, `CAND-005`, `CAND-003`, `CAND-007` |
| **Pandas** | Data Manipulation Library | **4 / 10** | **40.0%** | `CAND-001`, `CAND-010`, `CAND-006`, `CAND-004` | `CAND-008`, `CAND-002`, `CAND-009`, `CAND-005`, `CAND-003`, `CAND-007` |
| **Data Analysis** | Core Domain Competency | **2 / 10** | **20.0%** | `CAND-001`, `CAND-010` | `CAND-006`, `CAND-004`, `CAND-008`, `CAND-002`, `CAND-009`, `CAND-005`, `CAND-003`, `CAND-007` |
| **Basic Statistics** | Analytical Foundation | **2 / 10** | **20.0%** | `CAND-010`, `CAND-006` | `CAND-001`, `CAND-004`, `CAND-008`, `CAND-002`, `CAND-009`, `CAND-005`, `CAND-003`, `CAND-007` |
| **Data Cleaning** | Data Preparation Methodology | **1 / 10** | **10.0%** | `CAND-001` | `CAND-010`, `CAND-006`, `CAND-004`, `CAND-008`, `CAND-002`, `CAND-009`, `CAND-005`, `CAND-003`, `CAND-007` |

```
Required Technical Skill Detection Prevalence Across Cohort:
SQL               [##############################] 70% (7/10)
Python            [#########################     ] 60% (6/10)
Pandas            [#################             ] 40% (4/10)
Data Analysis     [########                      ] 20% (2/10)
Basic Statistics  [########                      ] 20% (2/10)
Data Cleaning     [####                          ] 10% (1/10)
```

### Analysis of Detection Disparities

1. **High Tool Prevalence (`SQL` and `Python`):**
   SQL and Python were the most widely detected skills. SQL appeared in 70% of resumes because it is shared across data analytics, business intelligence (`CAND-009`, `CAND-005`), backend web development (`CAND-002`, `CAND-008`), and enterprise Java development (`CAND-003`). Python was present in 60% of resumes across both data science applicants and general software engineers.
2. **Severe Process and Concept Gaps (`Data Cleaning`, `Basic Statistics`):**
   Only a single candidate (`CAND-001`) matched `Data Cleaning` (via the phrase "data cleaning"), and only two candidates matched `Basic Statistics` (`CAND-010` and `CAND-006`).
3. **The Keyword Phrasing Dilemma:**
   In automated keyword screening, applicants often describe methodologies narrative-style (e.g., *"scrubbed dirty datasets"*, *"removed null records"*, *"handled outliers"*) rather than using the canonical phrase *"data cleaning"*. Unless such phrasing maps to configured aliases, automated regex matchers report a skill absence. **Crucially, the absence of a keyword mention does not prove that a candidate lacks the underlying competency.**

---

## 5. Required vs. Preferred Skill Coverage

The Phase 8 scoring engine combines candidate metrics using a policy-driven linear weighting formula:

$$\text{Composite Score} = (0.70 \times \text{Required Coverage}) + (0.10 \times \text{Preferred Coverage}) + (0.20 \times \text{TF-IDF Cosine Similarity}) \times 100$$

### Weighting Architecture Rationale
- **70% Required Skills:** Ensures that non-negotiable core competencies dominate candidate ranking. A candidate who lacks foundational skills cannot compensate through secondary bonuses.
- **10% Preferred Skills:** Provides positive differentiation among candidates who meet core requirements, without penalizing candidates who lack optional tools.
- **20% TF-IDF Cosine Similarity:** Rewards broader domain context, industry vocabulary, and project narrative alignment.

### Impact of Weighting on Candidate Rankings

As illustrated in [`skill_coverage_comparison.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/skill_coverage_comparison.png), the 70/10 weighting policy decisively separated candidates:

```
Candidate Coverage Comparison: Required (70%) vs Preferred (10%)
Rank 1: CAND-001 | Required: [########  ] 83% | Preferred: [##        ] 17% -> Score: 65.83
Rank 2: CAND-010 | Required: [########  ] 83% | Preferred: [          ]  0% -> Score: 64.01
Rank 3: CAND-006 | Required: [#####     ] 50% | Preferred: [###       ] 33% -> Score: 41.20
Rank 4: CAND-004 | Required: [###       ] 33% | Preferred: [#####     ] 50% -> Score: 30.16
Rank 7: CAND-009 | Required: [#         ] 17% | Preferred: [#####     ] 50% -> Score: 20.50
```

#### Illustrative Case Study: `CAND-004` (Rank 4) vs. `CAND-010` (Rank 2)
- `CAND-004` presented an impressive data science profile featuring **50.0% preferred skill coverage** (`NumPy`, `Scikit-learn`, `Machine Learning`), whereas `CAND-010` possessed **0.0% preferred coverage**.
- Despite `CAND-004`'s machine learning skills, `CAND-010` outranked `CAND-004` by **33.85 points** ($64.01$ vs. $30.16$).
- **Explanation:** `CAND-004` only matched 2 of 6 required skills (`Python`, `Pandas`), missing `SQL`, `Data Cleaning`, `Data Analysis`, and `Basic Statistics`. `CAND-010` matched 5 of 6 required skills. Because required skills carry seven times the weight of preferred skills, `CAND-010`'s core readiness properly elevated them above an applicant with advanced but non-essential specializations.

#### Illustrative Case Study: `CAND-009` (Rank 7)
- `CAND-009` showcased an enterprise Business Intelligence profile with **50.0% preferred skill coverage** (`Power BI`, `Tableau`, `Excel`).
- However, with only 1 required skill matched (`SQL` $\rightarrow 16.67\%$), their score remained capped at **20.50** (`Low Match`). For a Junior Data Analyst role requiring Python scripting and statistical manipulation, business intelligence dashboarding alone could not overcome the absence of core data science programming skills.

---

## 6. TF-IDF Similarity and Composite Score Analysis

TF-IDF (Term Frequency-Inverse Document Frequency) cosine similarity provides an automated measure of overall textual vocabulary overlap between each candidate resume and the target job description.

### Technical Formulation in This System
To guarantee equitable vocabulary weighting across all applicants, the vectorizer was fitted on a **unified, consistent 11-document corpus**:
$$\text{Corpus} = \{1 \text{ Job Description}\} \cup \{10 \text{ Candidate Resumes}\}$$
All personal identifiers (candidate names, emails, phone numbers) were sanitized prior to vectorization, ensuring that candidate contact details could not artificially alter similarity metrics.

### Observed Relationship

As plotted in the annotated scatter plot ([`similarity_vs_composite_score.png`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/figures/similarity_vs_composite_score.png)), candidate similarity values range from **0.0162** (`CAND-007`) to **0.2916** (`CAND-001`).

```
Scatter Overview: TF-IDF Cosine Similarity vs. Composite Match Score
100 |
    |
 75 |
    |             * CAND-001 (0.2916, 65.83)
    |             * CAND-010 (0.2839, 64.01)
 50 |
    |       * CAND-006 (0.1435, 41.20)
 25 |   * CAND-004 (0.0912, 30.16)
    |   * CAND-008 (0.0453, 24.24)
    |   * CAND-002 (0.0404, 24.14)   * CAND-009 (0.1919, 20.50)
    |   * CAND-005 (0.1386, 17.77)
    | * CAND-003 (0.0415, 12.50)
  0 | * CAND-007 (0.0162, 0.32)
----+---------------------------------------------------------------
  0 |    0.05    0.10    0.15    0.20    0.25    0.30
                     TF-IDF Cosine Similarity (0.0 – 1.0)
```

### Statistical Correlation Analysis

To evaluate the mathematical relationship between statistical vocabulary overlap and the overall evaluation results, bivariate correlation metrics were computed using the authoritative Phase 10 CSV screening records ([`screening_report_junior_data_analyst.csv`](file:///d:/Projects/Python/Automated%20Resume%20Screening%20Tool/reports/screening_report_junior_data_analyst.csv)):

- **Source Dataset:** `reports/screening_report_junior_data_analyst.csv` (and `.xlsx`)
- **Independent Variable ($x$):** `TF-IDF Cosine Similarity` (single-corpus transform)
- **Dependent Variable ($y$):** `Composite Match Score` (full-precision composite relevance)
- **Sample Size ($N$):** 10 paired observations
- **Correlation Metrics:**
  - **Pearson Product-Moment Correlation Coefficient ($r$):**
    $$r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}} = 0.852462 \approx \mathbf{0.8525}$$
    (Measures linear association; rounded to four decimal places for reporting).
  - **Spearman Rank Correlation Coefficient ($\rho$):**
    $$\rho = 1 - \frac{6 \sum d_i^2}{N(N^2 - 1)} = 0.733333 \approx \mathbf{0.7333}$$
    (Measures monotonic ordinal rank association; rounded to four decimal places for reporting).

#### Methodological Interpretation
1. **Strong Positive Linear Alignment ($r = 0.8525$):**
   There is a strong positive correlation between lexical similarity and composite score. This is partly structural (similarity accounts for 20% of the formula) and partly natural (resumes describing data analysis, SQL queries, and Python projects naturally contain the unigrams and bigrams prevalent in the job description).
2. **Notable Deviations (The `CAND-009` Anomaly):**
   Candidate `CAND-009` achieved a relatively high TF-IDF similarity of **0.1919** (higher than `CAND-006`'s 0.1435), yet ranked 7th with a composite score of only **20.50**. 
   - *Why?* `CAND-009`'s resume contained abundant analytical terms ("dashboards", "business intelligence", "reporting", "KPIs"), which elevated their TF-IDF cosine score. However, because they lacked 5 of the 6 required skills (missing Python, Pandas, Data Cleaning, Data Analysis, and Statistics), their composite score was severely bounded by the 70% required skills weight.
3. **Correlation Does Not Establish Causation or Competence:**
   TF-IDF measures vocabulary co-occurrence frequencies between documents. A candidate who repeats domain keywords or mirrors phrases from the job description can elevate their lexical similarity without demonstrating practical analytical competence, critical thinking, or real-world problem-solving ability. Strong statistical correlation between text similarity and composite match scores must not be interpreted as evidence of candidate quality or predictive validity for job performance. Therefore, TF-IDF serves strictly as an assistive text-relevance signal within a human-in-the-loop screening workflow.

---

## 7. Key Findings

The following six core findings emerge directly from the empirical screening data:

1. **Deterministic Separation of Role Alignment:**
   The screening engine clearly separated relevant data analytics resumes from non-aligned technical profiles. The top three candidates (`CAND-001`, `CAND-010`, `CAND-006`) averaged a composite score of **57.01**, whereas the seven lower-ranked candidates averaged **18.52**, reflecting an average separation of **38.49 points**.
2. **Core Requirement Dominance Over Secondary Skills:**
   The 70% required skill weighting prevented candidate over-ranking based solely on preferred tools. Despite possessing 50% preferred skill coverage, `CAND-004` and `CAND-009` finished 4th and 7th respectively, demonstrating that specialized tools cannot substitute for foundational competencies.
3. **High Prevalence of Programming and Database Tools:**
   Technical tools exhibited the highest cohort prevalence (`SQL` at 70%, `Python` at 60%, `Pandas` at 40%), while conceptual and process-oriented terms (`Data Cleaning` at 10%, `Basic Statistics` at 20%) showed the lowest automated keyword match rates.
4. **Resolution of Complex Scoring Ties:**
   The multi-tiered ranking policy resolved exact numerical ties without manual intervention or arbitrary ordering. Candidates `CAND-008` and `CAND-002`, who had identical required coverage (33.33%) and preferred coverage (0.00%), were cleanly separated by a 0.0049 difference in corpus-level TF-IDF similarity.
5. **Absence of High-Match Automation Bias:**
   Zero candidates achieved the $\ge 70.0$ "High Match" category, demonstrating that the system does not inflate scores or create artificial certainty. Every top candidate was categorized as "Moderate Match," signaling to recruiters that human evaluation remains essential.
6. **Robust Lexical Correlation with Meaningful Exceptions:**
   While TF-IDF cosine similarity correlated strongly with overall scores ($r = 0.8525$), exceptions like `CAND-009` (high text similarity, low skill coverage) proved that dual-representation scoring (combining deterministic skill extraction with statistical text similarity) prevents keyword-stuffing from bypassing structural skill requirements.

---

## 8. Limitations

To ensure responsible interpretation and avoid algorithmic over-reliance, the following technical and methodological limitations must be acknowledged:

1. **Small Synthetic Dataset ($N=10$):**
   The experiment evaluated exactly 10 fictional candidate resumes. While ideal for validating algorithmic mechanics, edge-case handling, and precision sorting, this cohort does not represent the demographic or experiential diversity of an authentic applicant pool.
2. **Single Benchmark Role:**
   Evaluations were restricted to a single entry-level Junior Data Analyst specification. Screening dynamics, vocabulary overlap, and weighting effectiveness may behave differently across senior leadership, creative, or specialized engineering domains.
3. **Keyword-Level Extraction Constraints:**
   Skill matching relies on regular expressions, word boundaries, and predefined alias dictionaries. The parser cannot infer skills described through varied narrative prose or unconventional synonyms that are not cataloged in the JSON requirements taxonomy.
4. **Lack of Proficiency Verification:**
   The presence of a keyword (e.g., "Python") confirms only that the term appears in the document text. It provides no verification of candidate depth, years of experience, coding quality, or practical problem-solving capability.
5. **False Negatives in Skill Detection:**
   An applicant who performed extensive data cleaning but described it as *"scrubbed legacy database tables"* was marked as missing `Data Cleaning`. Automated keyword absence must never be conflated with applicant incompetence.
6. **Surface Text Overlap of TF-IDF:**
   TF-IDF measures lexical co-occurrence. It cannot evaluate semantic depth, reasoning, or contextual coherence, and may reward resumes that match the vocabulary of the job posting over resumes that articulate equivalent experience using alternative phrasing.
7. **Empirically Unvalidated Scoring Weights:**
   The 70/10/20 scoring formula was chosen as an illustrative, pedagogical design. These weights have not been calibrated or empirically validated against real-world hiring outcomes or long-term job performance.
8. **Organizational Nature of Review Thresholds:**
   The thresholds ($\ge 70$, $\ge 40$, $< 40$) are administrative prioritization aids designed to structure recruiter workloads. They do not constitute objective dividing lines between "qualified" and "unqualified" individuals.
9. **Impact of Document Layout and Formatting:**
   Multi-column layouts, visual callouts, complex tables, and non-standard fonts can affect optical character recognition and text extraction accuracy, potentially introducing noise prior to cleaning and matching.

---

## 9. Recommendations and Future Improvements

Based on the findings and limitations of this experiment, the following enhancements are recommended for future iterations of the screening architecture:

1. **Expansion of Synthetic Benchmark Datasets:**
   Develop and evaluate a larger synthetic cohort ($N \ge 100$) spanning diverse experience levels, career transitioners, international resume conventions, and multi-page formats to stress-test parsing robustness and statistical distributions.
2. **Integration of Semantic Embeddings (Dense Retrieval):**
   Augment lexical TF-IDF with pre-trained dense sentence transformers (e.g., SBERT) to capture semantic relationships. This would enable the pipeline to recognize that *"handling missing values and outliers"* is conceptually synonymous with *"data cleaning"*.
3. **Taxonomy Enrichment via Standardized Frameworks:**
   Expand the canonical skill dictionary using recognized open-source labor market taxonomies (such as O*NET or ESCO) to improve alias coverage while strictly avoiding the collection of real candidate personal data.
4. **Contextual Skill Validation:**
   Enhance the extraction engine to evaluate the grammatical context of matched skills—distinguishing skills applied in professional projects from skills merely listed in an introductory interest section or course syllabus.
5. **Empirical Weight Calibration:**
   Conduct sensitivity analyses across alternative weighting schemes (e.g., 60/20/20 vs. 50/30/20) to evaluate how different formula configurations impact candidate rank stability.
6. **Enhanced Recruiter Explainability Dashboards:**
   Provide recruiter-facing evidence cards displaying exact source sentences and paragraph contexts for every detected skill, ensuring complete visibility into automated scoring logic.
7. **Firm Retention of Human-in-the-Loop Governance:**
   Maintain the policy that automated screening scores serve strictly as assistive organizational aids. Final decisions regarding candidate progression, interviewing, and hiring must always remain with human talent acquisition professionals.

---

## 10. Conclusion

The Phase 12 analytical investigation confirms that the **Automated Resume Screening Tool** achieves its educational design goals. By uniting deterministic skill extraction, corpus-wide TF-IDF similarity computation, and transparent composite scoring, the system successfully categorizes and ranks candidate resumes with mathematical precision and auditability.

### What This Experiment Demonstrates
- Multi-stage NLP pipelines can process multi-format resumes, sanitize personal contact details, and compute objective relevance scores against structured job criteria.
- Full-precision tie-breaking prevents arbitrary ranking decisions when candidates possess identical skill coverages.
- Publication-quality visualizations and multi-sheet reporting provide stakeholders with transparent visibility into screening decisions.

### What This Experiment Does Not Establish
- This prototype does **not** provide an autonomous hiring engine.
- Match scores do **not** reflect candidate talent, intelligence, dedication, or professional competence.
- Low match scores do **not** warrant automated candidate disqualification.

When utilized responsibly as an assistive workflow tool under human oversight, automated screening can streamline initial resume review while preserving fairness, privacy, and transparency.

---

*Report authored by **Akash Das** as part of the Automated Resume Screening Tool portfolio project.*