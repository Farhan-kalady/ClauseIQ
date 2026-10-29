# Antigravity Prompt – Build the Final ClauseIQ Project Report (Overleaf / LaTeX)

Before pasting this prompt, put these in the repository under `docs/reference/`:
- `Interim_Report.pdf` (your ClauseIQ interim report: content source)
- `Sulfath_report.pdf` (reference for **structure and formatting only**)

Then paste everything below the line into Antigravity with the ClauseIQ repository open.

---

## ROLE

You are a technical writer and LaTeX typesetter with strong machine learning knowledge. Build the **complete final project report** for **ClauseIQ – Machine Learning-Based Contract Clause Classification and Intelligent Search System** as an **Overleaf-ready LaTeX project**.

## INPUTS AND HOW TO USE THEM

1. **`docs/reference/Interim_Report.pdf`** – the content source. It covers Chapters 1 to 5.6 (introduction through model comparison). Reuse its structure, wording, and argument, but **update and correct** it against the final repository (see "Known issues in the interim report").
2. **The ClauseIQ repository** – the source of truth for every fact and number: `src/`, `api/`, `frontend/src/`, `database/schema.sql`, `data/`, `results/`, `artifacts/manifest.json`, `docs/model_card.md`, `docs/BASELINE.md`, `docs/ERROR_ANALYSIS.md`, `tests/`, `requirements.txt`, `frontend/package.json`, and `git log`.
3. **`docs/reference/Sulfath_report.pdf`** – **layout and structure reference only**. You may copy its *formatting ideas* (heading style, per-paper literature table layout, caption placement, table styling, code listing style, Git history table, references style). **Do not copy any text, numbers, sentences, tables, figures, or topics from it.** It is about a different project. Treat any overlap in wording as a defect.

## OUTPUT

Create a folder `report/` in the repo root containing an Overleaf-ready project:

```
report/
  main.tex
  chapters/ch01_introduction.tex ... ch11_references.tex   (one file per chapter)
  references.bib   (or a thebibliography block, IEEE numeric style)
  figures/         (generated figures, PDF or 300-dpi PNG)
  generated/       (auto-generated numbers and tables, see below)
  scripts/make_figures.py, scripts/make_numbers.py
  TODO_FOR_USER.md (only items you could not complete)
  ClauseIQ_Report.zip (the whole project, ready to upload to Overleaf)
```

Do **not** modify application source code, install new packages, or touch `.env`. Use only the existing `.venv` and, for compiling, an installed LaTeX or the `artifacts/tools/tectonic.exe` already in the repo. If you cannot compile, say so clearly and perform the static checks below.

## REQUIRED CHAPTER ORDER AND NUMBERING (must match exactly)

```
1  Introduction
2  Supporting Literature
   2.1 Literature Review
   2.2 Literature Review Summary
   2.3 Findings and Proposals
3  System Analysis
   3.1 Analysis of the Dataset
       3.1.1 About the Dataset
       3.1.2 Explore the Dataset
   3.2 Data Preprocessing
       3.2.1 Data Cleaning
       3.2.2 Analysis of Feature Variables
       3.2.3 Analysis of Class Variables
   3.3 Data Visualization
   3.4 Analysis of Architecture and Algorithms
       3.4.1 Detailed Study Report of the Proposed Algorithm(s)
   3.5 Project Pipeline
   3.6 Feasibility Analysis
   3.7 System Environment
       3.7.1 Software Environment
       3.7.2 Hardware Environment
4  System Design
   4.1 Model(s) Building
       4.1.1 Implementation Code
       4.1.2 Model Planning (Training/Testing Split of the Dataset)
       4.1.3 Training
       4.1.4 Testing
5  Results and Discussion
6  Model Deployment
   6.1 Model Implementation
   6.2 UI Design
7  Git History
8  Conclusions
9  Future Scope
10 Appendix
   10.1 Minimum Software Requirements
   10.2 Minimum Hardware Requirements
11 References
```

Do not add, remove, merge, or renumber any of these. Extra levels (for example 3.4.1 subsections per algorithm, or 5.1, 5.2 inside Chapter 5) are allowed only below the listed headings. **Chapter 5 must contain these parts, in this order:** Comparison of Models; Evaluation Metrics; Confusion Matrix; Relevant Metrics Calculated from the Confusion Matrix; Prediction Statistics on Unseen Data; Discussion of Findings and Conclusions.

## FORMATTING SPECIFICATION (follow exactly)

| Item | Requirement |
|---|---|
| Tool | LaTeX, compilable on Overleaf (pdfLaTeX preferred) |
| Font | Times New Roman look. On Overleaf use a Times-compatible package (`newtxtext` + `newtxmath`, or `mathptmx`), which is what the reference report uses. If the user needs the literal font "Times New Roman", offer an XeLaTeX/`fontspec` variant in `TODO_FOR_USER.md` |
| Page | A4, margins **1 inch on all sides** (`geometry`) |
| Main heading (chapter) | **16 pt**, bold, numbered like "1 INTRODUCTION", new page for each chapter |
| Sub heading (x.y) | **14 pt**, bold |
| Sub-sub heading (x.y.z) | **12 pt**, bold |
| Body text | **12 pt**, justified |
| Line spacing | **1.5** (`setspace`, `\onehalfspacing`) |
| Header | Project name **top right**, then a **full-length line** across the text width. Must also appear on chapter-opening pages (redefine the `plain` page style) |
| Footer | **Full-length line**, then "Department of Computer Applications" **bottom left** and the **page number bottom right** |
| Page numbering | Arabic **1, 2, 3 …**, starting with page 1 on the first page of Chapter 1 and continuing to the end. Do not generate a cover page, certificate, acknowledgement, abstract, or contents pages (the college supplies those); the PDF starts at Introduction |
| Tables and code | Tables at least 10 pt, code listings at least 9 pt, captions 11 pt (a deliberate readability allowance; all running text stays 12 pt) |
| Captions | Below figures and tables, numbered by chapter: "Figure 3.2: …", "Table 5.1: …", and every figure and table is referenced in the text with `\ref` |
| Equations | Typeset with `amsmath`, numbered by chapter, for example (3.4). The PDF text of the interim report is garbled for equations, so retype them cleanly |
| Code | `listings` or `minted`-free `listings`, with a file path caption such as "src/feature_extraction.py (abridged)" |
| Language | Formal academic English, consistent spelling, no first-person marketing tone |
| Length | About 60 to 75 pages (the reference is about 65) |

Use `fancyhdr`, `titlesec`, `setspace`, `geometry`, `graphicx`, `booktabs`, `longtable`, `listings`, `amsmath`, `caption`, `tikz`, `hyperref`, `cite`/`natbib` as needed. Ensure there are no overfull boxes that run into the margins, and no empty pages before chapters.

## CONTENT PLAN PER CHAPTER

**1 Introduction.** Rewrite the interim introduction for the **completed** system: problem, dataset (CUAD, 510 contracts, 41 categories, 12,204 clause records), the two capabilities (classification and TF-IDF/Cosine search), objectives, scope and limitations (not legal advice; classical ML only), and an "organisation of the report" paragraph. The interim says the React UI, PDF ingestion, and Supabase persistence were remaining work; they are now implemented, so update this. State only what the repository shows.

**2 Supporting Literature.** Keep the three IEEE Access papers from the interim report. For each paper, write a concise paragraph plus a two-column details table (Title, Area of Work, Dataset, Methodology/Strategy, Algorithm(s), Result), following the reference's layout idea. Then a summary table (2.2) and findings/gaps/proposals (2.3). **Verify every claim against the papers where you can. If you cannot verify a number or statement (for example latency figures or "more than 40%" statistics), soften or remove it and list it in `TODO_FOR_USER.md`.** Never add a reference you cannot verify exists, and use DOIs.

**3 System Analysis.**
- 3.1 Dataset: **recompute every statistic from `data/clauseiq_dataset_clean.csv`** (completeness, duplicates, per-category counts, clauses per contract, length statistics). Do not copy numbers from the interim report.
- 3.2 Preprocessing: describe the **actual** final pipeline in `src/text_cleaner.py` and `src/build_artifacts.py` (regex cleaning, lemmatization, hybrid features, whatever the code and manifest show). Include the experiment evidence from `results/experiments.csv` (what helped, what did not, including that stopword removal did not help).
- 3.3 Visualization: regenerate figures with `scripts/make_figures.py` (category distribution, clauses per contract, word-count distributions, top bigrams, and so on). Large labels, readable at print size.
- 3.4.1 Algorithms: for **each** algorithm (TF-IDF and the hybrid word plus character features, Logistic Regression, Linear SVM, Multinomial Naive Bayes, Random Forest, Cosine Similarity search), give a **TikZ flow diagram** and a step-by-step explanation, with equations. Include only what the project uses.
- 3.5 Pipeline: a TikZ pipeline diagram of the real, final system (data to preprocessing to features to models to selection to API to React UI to Supabase), with an explanation of each level.
- 3.6 Feasibility (technical, economic, operational) and 3.7 environment (software table with **versions read from the `.venv` via `pip list` and `package.json`/lockfile**, hardware table). Do not invent versions.

**4 System Design.**
- 4.1.1: abridged, real code listings from `src/` and `api/` (feature extraction, a training script, the clause splitter, the classify/search services), each with its file path. Never write code that is not in the repo.
- 4.1.2: split design. Describe both **Split A** (stratified 80/20, comparable with the interim) and **Split B** (grouped by `contract_id`, leakage-safe) exactly as implemented, with sample counts from the scripts.
- 4.1.3 Training and 4.1.4 Testing: hyperparameters and search spaces from the training scripts and `results/experiments.csv`; the selection rule; test set used only for final reporting.

**5 Results and Discussion.** All numbers come from `results/` and the evaluation scripts. Include, on both splits where available:
- Comparison of models: the four-model benchmark from the interim plus the **final improved model**, with a baseline-versus-final table.
- Evaluation metrics: accuracy, macro and weighted precision, recall, F1, ECE, and precision by confidence band.
- Confusion matrix: a readable 41 by 41 figure (large, possibly a landscape page) plus a table of the most confused category pairs.
- Relevant metrics calculated from the confusion matrix: per-class TP, FP, FN, TN, precision, recall, F1, and specificity computed by `scripts/make_numbers.py` directly from the saved confusion matrix; show formulas and two or three worked examples; macro and weighted averages.
- Prediction statistics on unseen data: (a) the held-out test results, (b) the grouped-split held-out contracts, (c) the real PDF checks (`test_data/` and `data/raw_pdfs/`) with expected versus predicted labels and confidence. **State plainly that the real-PDF sample is small.**
- Discussion: what worked, what did not, ceilings (confusable category pairs, rare classes), calibration findings, limitations. Do not overclaim.

**6 Model Deployment.** 6.1: the FastAPI service (endpoint table, request/response, startup loading of artifacts, Supabase persistence, test results from a real `pytest` run). 6.2: UI Design with the screenshots. **You cannot take screenshots, so use `\IfFileExists` placeholders pointing to `figures/ui/*.png` and list exactly which screenshots the user must add in `TODO_FOR_USER.md` (Classify text, Classify upload and results, Search results, dark mode, mobile view, offline banner).**

**7 Git History.** A real table (date, short hash, message) generated from `git log`, plus the repository URL from `.git/config`. Include all commits on the current branch and say which branch.

**8 Conclusions** and **9 Future Scope.** Honest summary of achieved results against objectives, limitations, and realistic next steps (for example authentication, OCR, deployment, better segmentation, more labeled data). Do not mention deep learning or LLMs as part of the system; they may appear only as out-of-scope future directions if clearly labeled so.

**10 Appendix.** 10.1 minimum software and 10.2 minimum hardware as tables, consistent with 3.7.

**11 References.** IEEE numeric style, real references only (the three interim papers, the CUAD paper, scikit-learn, and other works you actually cite in the text). Every entry must be cited at least once.

## KNOWN ISSUES IN THE INTERIM REPORT (fix them; do not copy them)

1. Table 3.2 category counts disagree with Figure 3.2 and with the rank order (for example Anti-Assignment 652 is listed below Audit Rights 642; Cap On Liability 742 vs 672 in the figure; License Grant is missing). **Recompute all dataset statistics from the CSV.**
2. The pipeline figure says "Contract-Level Train/Test Split", but the interim split was a stratified clause-level split. Describe exactly what was done (Split A and Split B).
3. The interim says Logistic Regression has "natively calibrated" probabilities. The final evaluation measured calibration (ECE, precision by confidence band). Report the measured behaviour, not the claim.
4. Software versions in the interim (for example FastAPI and uvicorn) and claims such as "training under three minutes" and "sub-10 ms retrieval" are unverified. Read the versions from the environment, and either measure the timings with a small script or remove the claims.
5. The interim describes tokenization and stopword filtering; the final code does not necessarily do that. Describe the real final preprocessing.
6. Several literature statements (latency, percentages) may not be verbatim from the papers. Verify, soften, or remove them.
7. The interim figures have tiny labels, especially the 41 by 41 confusion matrix. Regenerate them at a readable size.

## HARD RULES

- **No fabricated numbers, versions, citations, screenshots, or results.** Every number in the report must come from a repository file or a script you ran. Generate `generated/numbers.tex` (LaTeX macros) and the results tables from `results/*.json|csv` with `scripts/make_numbers.py`, so values cannot drift from the source. Keep a `report/numbers_sources.md` mapping each reported number to its source file.
- Mark anything you cannot verify as **To Be Confirmed** in the text and list it in `TODO_FOR_USER.md`.
- No plagiarism: all text must be original or adapted from the interim report; nothing from the Sulfath reference.
- Describe the system truthfully: classical ML only; no authentication; no cloud hosting configured; not legal advice.
- Never print or include secrets from `.env`.

## PROCESS (report after each step)

1. **Plan:** read the three inputs and write `report/PLAN.md` mapping each chapter to its source files and listing the data you must regenerate. Wait for no input; continue.
2. **Data and figures:** write and run `scripts/make_numbers.py` and `scripts/make_figures.py`; check that the regenerated baseline numbers match `results/`.
3. **Write chapters 1 to 5**, compile after each.
4. **Write chapters 6 to 11**, compile.
5. **QA:** compile cleanly with no errors; check page count, that margins and fonts are as specified, that the header and footer appear on every page including chapter openers, that page 1 is the first page of Chapter 1, that the heading numbers match the required list exactly, that every figure, table, and citation is referenced, and that no text overlaps the margins.
6. **Package:** create `ClauseIQ_Report.zip`.

## FINAL MESSAGE

Print: the page count; the list of chapters and sections with their page numbers; a table of the main numbers and their source files; which items are placeholders (screenshots and so on); anything unverified; how to upload the zip to Overleaf and set the compiler (pdfLaTeX); and any deviation from the formatting spec with the reason.
