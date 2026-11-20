# Dataset & Benchmark Specification

## Automated Resume Screening Tool
**Author:** Akash Das  
**Benchmark Role:** Junior Data Analyst  
**Workspace:** `D:\Projects\Python\Automated Resume Screening Tool`  

---

## 1. Benchmark Role & Requirements Taxonomy

The screening benchmark is modeled on an entry-level **Junior Data Analyst** role. All candidate resumes are evaluated against the authoritative job description and skill taxonomy maintained in `data/job_description/`.

### 1.1 Dual-Tier Skill Taxonomy (`junior_data_analyst_requirements.json`)

The job taxonomy splits candidate evaluation into three weighted components totaling 100%:

| Evaluation Component | Weight | Criteria Count | Criteria Description |
|---|---:|---:|---|
| **Mandatory Required Skills** | **70%** | 6 Skills | Python, SQL, Pandas, Data Cleaning, Data Analysis, Basic Statistics |
| **Secondary Preferred Skills** | **10%** | 6 Skills | NumPy, Scikit-learn, Machine Learning, Power BI, Tableau, Excel |
| **Vocabulary Context** | **20%** | Full Corpus | Unified Corpus TF-IDF Cosine Similarity against Job Description |

---

## 2. Synthetic Benchmark Candidate Dataset

### 2.1 Rationale for Synthetic Resumes
To comply with global data privacy regulations (GDPR, CCPA) and prevent the exposure of real Personally Identifiable Information (PII), the benchmark evaluation dataset consists of **10 carefully engineered synthetic resumes** (`data/resumes/`).

Synthetic engineering provides several key technical advantages:
1. **Zero PII Exposure:** Guarantees candidate confidentiality while allowing public portfolio demonstration.
2. **Controlled Test Profiles:** Resumes were crafted to systematically evaluate specific scoring edge cases, tie-breakers, and format-handling resilience.
3. **Format Diversity:** Spans the three dominant industry document formats: Adobe PDF (`.pdf`), Microsoft Word (`.docx`), and Plain Text (`.txt`).

### 2.2 Format & Profile Distribution

| Candidate ID | File Name | Format | Profile Archetype | Targeted Test Scenario |
|---|---|---|---|---|
| **CAND-001** | `candidate_001.pdf` | PDF | Junior Data Analyst | Strongest candidate; high required coverage ($5/6$), solid similarity ($0.2916$). |
| **CAND-002** | `candidate_002.docx` | DOCX | Business / Data Enthusiast | Partial required match ($2/6$); exercises subtle TF-IDF tie-breaking against CAND-008. |
| **CAND-003** | `candidate_003.txt` | TXT | Entry-Level Intern | Minimal required coverage ($1/6$), tests low-score tier assignment. |
| **CAND-004** | `candidate_004.pdf` | PDF | Junior BI Specialist | High preferred coverage ($3/6$), moderate required coverage ($2/6$). |
| **CAND-005** | `candidate_005.docx` | DOCX | Data Operations Assistant | Low required ($1/6$), moderate preferred ($2/6$). |
| **CAND-006** | `candidate_006.txt` | TXT | Python / ML Developer | Balanced candidate ($3/6$ required, $2/6$ preferred); rank 3 baseline ($41.20$). |
| **CAND-007** | `candidate_007.pdf` | PDF | Sales & Marketing Specialist | **Negative Control:** Completely irrelevant background ($0/6$ required, $0/6$ preferred). |
| **CAND-008** | `candidate_008.docx` | DOCX | SQL Database Junior | Exact required tie ($2/6$) with CAND-002; exercises fourth-decimal TF-IDF resolution. |
| **CAND-009** | `candidate_009.txt` | TXT | Academic Researcher | Low required ($1/6$), high preferred ($3/6$); tests preferred weighting impact. |
| **CAND-010** | `candidate_010.pdf` | PDF | Junior Quantitative Analyst | Near-top candidate ($5/6$ required); tests tie-breaking against CAND-001. |

---

## 3. Authoritative Benchmark Results

All components of the screening engine produce mathematically verified results that strictly match the approved Phase 9 baseline:

| Rank | Candidate ID | Format | Required Coverage (70%) | Preferred Coverage (10%) | TF-IDF Cosine Sim (20%) | Composite Score | Review Category |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **CAND-001** | PDF | 83.33% (5/6) | 16.67% (1/6) | 0.2916 | **65.83** |  Moderate Match |
| **2** | **CAND-010** | PDF | 83.33% (5/6) | 0.00% (0/6) | 0.2839 | **64.01** |  Moderate Match |
| **3** | **CAND-006** | TXT | 50.00% (3/6) | 33.33% (2/6) | 0.1435 | **41.20** |  Moderate Match |
| **4** | **CAND-004** | PDF | 33.33% (2/6) | 50.00% (3/6) | 0.0912 | **30.16** |  Low Match |
| **5** | **CAND-008** | DOCX | 33.33% (2/6) | 0.00% (0/6) | 0.0453 | **24.24** |  Low Match |
| **6** | **CAND-002** | DOCX | 33.33% (2/6) | 0.00% (0/6) | 0.0404 | **24.14** |  Low Match |
| **7** | **CAND-009** | TXT | 16.67% (1/6) | 50.00% (3/6) | 0.1919 | **20.50** |  Low Match |
| **8** | **CAND-005** | DOCX | 16.67% (1/6) | 33.33% (2/6) | 0.1386 | **17.77** |  Low Match |
| **9** | **CAND-003** | TXT | 16.67% (1/6) | 0.00% (0/6) | 0.0415 | **12.50** |  Low Match |
| **10** | **CAND-007** | PDF | 0.00% (0/6) | 0.00% (0/6) | 0.0162 | **0.32** |  Low Match |

---

## 4. Cohort Statistical Distribution

The benchmark evaluation cohort exhibits healthy statistical dispersion, demonstrating that the multi-factor scoring model effectively differentiates between candidates across the qualification spectrum:

- **Cohort Size ($N$):** 10 candidates
- **Mean Composite Score:** $30.07$
- **Median Composite Score:** $24.19$
- **Standard Deviation ($\sigma$):** $20.89$
- **Minimum Score:** $0.32$ (`CAND-007`: Negative Control)
- **Maximum Score:** $65.83$ (`CAND-001`: Top Candidate)
- **Review Category Breakdown:**
  -  **High Match ($\ge 70.0$):** 0 candidates (Reflects entry-level realistic resumes where no single junior candidate possesses 100% of all criteria)
  -  **Moderate Match ($40.0 \le \text{Score} < 70.0$):** 3 candidates (`CAND-001`, `CAND-010`, `CAND-006`)
  -  **Low Match ($< 40.0$):** 7 candidates (`CAND-004`, `CAND-008`, `CAND-002`, `CAND-009`, `CAND-005`, `CAND-003`, `CAND-007`)
