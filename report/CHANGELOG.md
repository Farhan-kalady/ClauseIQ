# ClauseIQ Final Report Revision Changelog

This document maps all planned revisions in the LaTeX report codebase (`report/`) to the specific requirements outlined in the prompt.

---

## 1. Heading Structure Restructuring
- In `main.tex`, ensure `\setcounter{secnumdepth}{2}` (Chapters, Sections, Subsections numbered; Subsubsections unnumbered).
- Strictly enforce the authorized numbered heading tree:
  - **Chapter 1**: No numbered sections at all. Remove `1.1` to `1.6` and `1.3.1` to `1.3.3`. Convert to continuous prose (900–1,150 words).
  - **Chapter 2**: Only `2.1 Literature Review`, `2.2 Literature Review Summary`, `2.3 Findings and Proposals`. Remove `2.1.1` to `2.1.3`; replace with unnumbered bold run-in labels (`\paragraph*{Paper 1: ...}`).
  - **Chapter 3**: Remove `3.6.1` to `3.6.3` (Feasibility sections become unnumbered run-in labels).
  - **Chapter 5**: Remove `5.1.1`, `5.2.1`, `5.3.1`, `5.4.1`, `5.5.1` to `5.5.3`. Fold `5.6 Intelligent Search Evaluation` into `5.5 Prediction Statistics of Unseen Data` under an unnumbered label (`\paragraph*{Intelligent Search Retrieval Evaluation}`). Renumber Discussion to `5.6 Discussion of Findings and Conclusions`.
  - **Chapter 6**: Remove `6.1.1` to `6.1.4`, `6.2.1`, `6.2.2`. Use `6.1 Model Implementation` and `6.2 UI Design`.
  - **Chapters 7, 8, 9**: No numbered subsections.
  - **Chapter 10**: `10.1 Minimum Software Requirements`, `10.2 Minimum Hardware Requirements`.
  - **Chapter 11**: `11 REFERENCES` (unnumbered sections).
- Build automated heading validator script `report/scripts/check_headings.py` to ensure zero disallowed headings exist in the document.

---

## 2. Introduction Rewrite (2–3 Pages)
- Rewrite Chapter 1 (`report/chapters/ch01_introduction.tex`) as continuous prose of ~900–1,150 words (2.5 pages, ending cleanly before page 4).
- Structure:
  1. Commercial and legal friction of manual contract review.
  2. Failure of legacy keyword search (concrete contract example: "assignment" vs "transfer").
  3. NLP and Machine Learning assistance (clause-level classification and semantic search).
  4. ClauseIQ overview (CUAD corpus: 510 contracts, 41 categories, 12,204 clauses).
  5. System implementation described as a functional **prototype**.
  6. Compact numbered list of primary objectives ($\le 6$ lines).
  7. Scope and limitations (classical ML, no legal advice, text-layer PDFs, prototype deployment).
  8. Report structural organization.
- Remove uncited claims ("tens of thousands of billable hours", "empirical studies indicate reviewer accuracy declines", invented numbers).

---

## 3. Real UI Screenshots & UI Design Rewrite
- Capture 8 real application screenshots into `report/figures/ui/`:
  - `ui_01_classify_text_result.png`: single clause prediction with confidence ring and alternative classes.
  - `ui_02_classify_upload_dropzone.png`: document classification upload dropzone.
  - `ui_03_classify_document_results.png`: extracted PDF clauses with status summary, filters, and pagination.
  - `ui_04_search_results.png`: query search with highlighted terms and category filter.
  - `ui_05_dark_mode.png`: full interface in dark theme.
  - `ui_06_mobile_view.png`: responsive mobile viewport (390px) showing bottom navigation.
  - `ui_07_offline_banner.png`: offline notification banner when backend is stopped.
  - `ui_08_api_docs.png`: FastAPI Swagger UI documentation at `/docs`.
- Rewrite `report/chapters/ch06_model_deployment.tex` (Section 6.2) to accurately document actual frontend components:
  - `App.jsx`, `Header.jsx`, `ClassifierView.jsx`, `SearchView.jsx`, `ConfidenceRing.jsx`, `StatusBadge.jsx`, `OfflineBanner.jsx`, `Footer.jsx`.
- Remove fictitious names (`Navbar`, `ClassifyTab`, `SearchTab`, `ContractsTab`).

---

## 4. Substantive Expansion to 62–70 Pages (No Padding)
- **Section 3.3 (Data Visualization)**: Add 4 publication figures:
  1. Category word count distribution across clauses.
  2. Top discriminative bigrams in legal categories.
  3. Cumulative class frequency curve (Pareto inequality).
  4. Correlation between clause length and category complexity.
- **Section 3.4.1 (Algorithm Study)**:
  - Provide flow diagram and step-by-step numbered breakdown for ALL 6 algorithms:
    1. Hybrid Word + Character TF-IDF feature union.
    2. Multinomial / OvR Logistic Regression.
    3. Linear Support Vector Classifier (LinearSVC).
    4. Multinomial Naive Bayes.
    5. Random Forest Ensemble.
    6. Cosine Similarity Vector Space Retrieval.
- **Section 3.5 (Project Pipeline)**:
  - Comprehensive architectural diagram detailing document ingestion, regex cleaning, lemmatization, sparse feature extraction, classification, confidence tiering, and vector search.
- **Section 4.1.1 & 4.1.3 (Model Building & Training)**:
  - Include both baseline 10,000-feature vectorizer and final 40,000-feature hybrid vectorizer from `src/build_artifacts.py`.
  - Full `results/experiments.csv` table detailing 19 systematic experimental rounds.
- **Section 5.x (Results and Discussion)**:
  - Per-class F1 comparison bar charts for Split A and Split B.
  - Split B top confused pairs table.
  - Confidence-band calibration precision curve.
  - Full table of clauses extracted from real-world contract PDF checks (29 from `sample_contract.pdf` and 69 from synthetic contract).
- **Section 6.1 (Deployment)**:
  - End-to-end request sequence diagram.
  - Automated test suite summary table (45/45 passing tests).

---

## 5. Accuracy & Data Consistency Fixes
1. **API Endpoints (Table 6.1)**: Rewrite from actual routers: `/health`, `/categories`, `/classify`, `/classify/file`, `/search`, `/contracts`, `/contracts/{id}/clauses`.
2. **Per-Class Metrics**: Ensure all per-class numbers in text match generated tables (Governing Law F1 = 0.989, Parties = 0.965, Audit Rights = 0.946).
3. **Random Forest Discrepancy**: Document difference between initial sprint evaluation (`results/model_comparison.json`, Acc=0.6546, F1=0.5634) and re-evaluation protocol (`results/baseline_model_comparison.json`, Acc=0.6436, F1=0.5486).
4. **Hyperparameter Grids**: Document exact grids from `src/train_*.py` and verify RF trees = 200 (not 100).
5. **Software Table 3.3**: Update Vite to lockfile resolved version `6.4.4` (specifier `^6.0.7`), and verify all python libraries against `pip list`.
6. **Hardware Table 3.4**: Record verified host machine specifications: Windows 11, Intel 16 physical / 22 logical cores, 31.4 GB RAM, NVMe SSD.
7. **Measured Performance Claims**: Replace unverified claims with empirical benchmark measurements:
   - Single clause classification latency: Mean 6.58 ms, p50 6.13 ms, p95 8.93 ms.
   - Search query latency (12,204 clauses): Mean 100.68 ms, p50 99.83 ms, p95 109.84 ms.
   - Process Resident Memory (RSS): 464.62 MB.
8. **Database Claims**: Remove claims of latency columns or client metadata; describe exact columns in `database/schema.sql`. Label database as "PostgreSQL / Supabase (Local or Hosted Prototype)".
9. **Real-PDF Results**: Accurately report 29 clauses from `sample_contract.pdf` and 69 clauses from `ClauseIQ_Synthetic_Company_Service_Agreement_Test.pdf`.
10. **Softened Overclaims**: Clarify that Split B is not definitive proof of universal generalization; high-confidence precision dropped from 0.9024 to 0.8655; say "prioritise for review" rather than "safely automate".
11. **ECE Drop Explanation**: Explain that balanced weights, sublinear TF, and regularized softmax produced well-calibrated probabilities without the macro-F1 penalty of post-hoc `CalibratedClassifierCV`.
12. **Illustrative Confusion Samples**: Ground all confusion examples in verified held-out misclassifications from `docs/ERROR_ANALYSIS.md`.
13. **Literature Review**: Rename gap row to "Gap addressed by ClauseIQ", soften claims to "indicate", cite CUAD imbalance ratio 46.33:1.
14. **Figure Formatting**: Make confusion matrix titles visible, y-axis of search curves start at 0, remove "TikZ" from captions.
15. **Git History**: Regenerate Table 7.1 from `git log` at conclusion.
16. **Header**: "ClauseIQ – Machine Learning-Based Contract Clause Classification and Intelligent Search System" in running header.
