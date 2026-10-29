# ClauseIQ Final Project Report — Detailed Implementation Plan

**Project Title:** ClauseIQ – Machine Learning-Based Contract Clause Classification and Intelligent Search System  
**Document Target:** Overleaf-ready LaTeX Project (A4, 1-inch margins, Times New Roman look, 12pt body, 1.5 line spacing, 60–75 pages)  
**Execution Date:** October 20, 2026

---

## 1. Source Document and Artifact Mapping

| Chapter | Required Title & Numbering | Primary Source Files in Repository | What to Generate / Recompute |
| :--- | :--- | :--- | :--- |
| **1** | **Introduction** | `docs/reference/Interim_Report.pdf`, `PRD.md`, `README.md`, `DesignDoc.md` | Rewrite for completed state (include React UI, FastAPI, Supabase, PDF ingestion). |
| **2** | **Supporting Literature**<br>2.1 Literature Review<br>2.2 Literature Review Summary<br>2.3 Findings and Proposals | `docs/reference/Interim_Report.pdf`, 3 IEEE Access papers (Quevedo Caballero 2024, Siino 2025, Kutbi 2023), `docs/reference/Sulfath_report.pdf` (format reference only) | Verified summaries and two-column specification tables for each paper; comprehensive synthesis table; rigorous gap analysis. |
| **3** | **System Analysis**<br>3.1 Analysis of the Dataset<br>  3.1.1 About the Dataset<br>  3.1.2 Explore the Dataset<br>3.2 Data Preprocessing<br>  3.2.1 Data Cleaning<br>  3.2.2 Analysis of Feature Variables<br>  3.2.3 Analysis of Class Variables<br>3.3 Data Visualization<br>3.4 Analysis of Architecture & Algorithms<br>  3.4.1 Detailed Study Report of Proposed Algorithms<br>3.5 Project Pipeline<br>3.6 Feasibility Analysis<br>3.7 System Environment<br>  3.7.1 Software Environment<br>  3.7.2 Hardware Environment | `data/clauseiq_dataset_clean.csv`, `src/text_cleaner.py`, `src/build_artifacts.py`, `results/experiments.csv`, `requirements.txt`, `.venv` pip list, `frontend/package.json` | `scripts/make_numbers.py` recomputes all dataset stats (token counts, character counts, 41-class frequencies, contracts). `scripts/make_figures.py` generates 300-dpi publication charts. TikZ architecture & algorithm flows. Live pip list versions. |
| **4** | **System Design**<br>4.1 Model(s) Building<br>  4.1.1 Implementation Code<br>  4.1.2 Model Planning (Train/Test Split)<br>  4.1.3 Training<br>  4.1.4 Testing | `src/feature_extraction.py`, `src/train_baseline.py`, `src/train_svm.py`, `src/train_nb.py`, `src/train_random_forest.py`, `src/build_artifacts.py`, `src/clause_splitter.py`, `src/search.py` | Abridged, authentic code listings from `src/` with file paths. Split A (Stratified 80/20, 9763/2441) and Split B (Grouped by contract_id, 9718/2486 across 408/102 contracts). |
| **5** | **Results and Discussion**<br>- Comparison of Models<br>- Evaluation Metrics<br>- Confusion Matrix<br>- Relevant Metrics from CM<br>- Prediction Statistics on Unseen Data<br>- Discussion of Findings and Conclusions | `results/baseline_model_comparison.json`, `results/final_model_comparison.json`, `results/final_classification_report_split_a.json`, `results/final_classification_report_split_b.json`, `results/final_cm_split_a.npy`, `results/final_cm_split_b.npy`, `results/search_evaluation.json`, `results/search_refinement_experiments.json`, `results/baseline_real_document_check.json`, `docs/ERROR_ANALYSIS.md`, `docs/BASELINE.md` | Recomputed TP, FP, FN, TN, Precision, Recall, Specificity, F1 for all 41 classes via `scripts/make_numbers.py`. High-res readable 41x41 confusion matrix. Confidence band breakdowns (High >=0.50, Moderate 0.25-0.50, Low 0.10-0.25, Out-of-scope <0.10). Real PDF evaluation on 2 documents. Search retrieval metrics (P@k, R@k). |
| **6** | **Model Deployment**<br>6.1 Model Implementation<br>6.2 UI Design | `api/main.py`, `api/routers/`, `api/services/ml_service.py`, `api/schemas.py`, `database/schema.sql`, `tests/`, `frontend/src/` | REST endpoint specifications table. Supabase database schema table. Real pytest run outputs. UI structure with `\IfFileExists` wrappers pointing to `figures/ui/*.png`. |
| **7** | **Git History** | `.git/config`, `git log` output | Automated Git history table (hash, author, date, message) on current branch `main`. |
| **8** | **Conclusions** | PRD, DesignDoc, Results | Honest summary of deliverables achieved vs initial goals, operational boundaries, and classical ML trade-offs. |
| **9** | **Future Scope** | PRD, DesignDoc | Clear roadmap: OCR for scanned PDFs, transformer/fine-tuned architectures, user auth/multi-tenancy, vector DB integration. |
| **10** | **Appendix**<br>10.1 Minimum Software Requirements<br>10.2 Minimum Hardware Requirements | System specifications | Detailed hardware and software tables for developer and client deployment. |
| **11** | **References** | `docs/reference/Interim_Report.pdf`, IEEE Xplore DOIs, NeurIPS CUAD citation, scikit-learn citation | Formatted IEEE bibliography entries in `references.bib` with verified DOIs. |

---

## 2. Quantitative Ground Truth Generation Strategy

To ensure zero fabrication and strict reproducibility:
1. `report/scripts/make_numbers.py`:
   - Inspects `data/clauseiq_dataset_clean.csv` to calculate exact row counts, contract counts, class frequencies, min/max/mean/std of clause word and character lengths.
   - Loads `results/final_cm_split_a.npy` and `results/final_cm_split_b.npy` to compute per-class confusion metrics (TP, FP, FN, TN, Sensitivity/Recall, Specificity, Precision, F1).
   - Generates `report/generated/numbers.tex` containing LaTeX macros (e.g. `\newcommand{\TotalClauses}{12,204}`) and ready-to-input LaTeX tables (`report/generated/*.tex`).
   - Generates `report/numbers_sources.md` auditing each macro back to its source file.
2. `report/scripts/make_figures.py`:
   - Produces high-resolution 300-DPI publication figures in `report/figures/`:
     - `dataset_category_distribution.pdf` and `.png`
     - `clauses_per_contract_distribution.pdf` and `.png`
     - `clause_length_histogram.pdf` and `.png`
     - `model_comparison_barchart.pdf` and `.png`
     - `confusion_matrix_41x41_split_a.pdf` and `.png` (clean, rotated, readable labels)
     - `confusion_matrix_41x41_split_b.pdf` and `.png`
     - `calibration_curve.pdf` and `.png`
     - `search_metrics_p_at_k.pdf` and `.png`
     - `top_confused_pairs.pdf` and `.png`

---

## 3. Typesetting and Style Compliance

- **Document Class**: `\documentclass[12pt,a4paper]{report}`
- **Font**: `mathptmx` (or `newtxtext,newtxmath`) for Times New Roman font.
- **Margins**: Exactly 1 inch (72pt) all around using `\usepackage[margin=1in]{geometry}`.
- **Spacing**: `\onehalfspacing` via `setspace`.
- **Headings**:
  - Chapter: 16pt bold uppercase, starting on a fresh page.
  - Section (x.y): 14pt bold.
  - Subsection (x.y.z): 12pt bold.
  - Body: 12pt justified.
- **Running Headers & Footers**:
  - Implemented using `fancyhdr`.
  - Header: Right-aligned "ClauseIQ – Contract Clause Classification and Intelligent Search System" with full-width horizontal rule below.
  - Footer: Left-aligned "Department of Computer Applications", right-aligned page number `\thepage`, with full-width horizontal rule above.
  - Redefined `\fancypagestyle{plain}` so that every chapter-opening page carries the exact same header and footer.
  - Page numbering: Arabic `1, 2, 3 ...` starting at page 1 on Chapter 1.
- **Overleaf Readiness**:
  - All paths relative to `report/`.
  - Compilable via pdfLaTeX and tectonic.
  - Packages used: standard TeX Live / Overleaf packages (`graphicx`, `amsmath`, `booktabs`, `longtable`, `listings`, `tikz`, `xcolor`, `caption`, `fancyhdr`, `titlesec`, `setspace`, `hyperref`, `cite`, `pdfpages`).
