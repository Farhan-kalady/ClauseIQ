# ClauseIQ — Architectural & Code Audit (Phase 0)

**Date:** October 19, 2026  
**Branch:** `feature/complete-clauseiq`  
**Purpose:** Reconcile specification documents (`PRD.md`, `TechStack.md`, `DesignDoc.md`) with the active codebase, establishing the source of truth before Phase 1-5 execution.

---

## 1. Executive Summary & Ground Truth Principle

The codebase is the source of truth. Where specification documents described idealized architectures (e.g., full NLTK NLP pipeline, atomic transactions, contract-level search, or multi-model runtime switching), this audit documents the exact gaps and defines the roadmap to align code, documentation, and performance.

---

## 2. Discrepancies Between Specifications and Implementation

### 2.1 NLP Preprocessing & Dependencies
* **Specification (`PRD.md` Section 5.2 FR-04):** Mandates an end-to-end NLP preprocessing pipeline with lowercasing, punctuation removal, stopword removal, NLTK tokenization, and NLTK lemmatization.
* **Current Codebase (`src/text_cleaner.py`):** Regex-only cleaner performing lowercasing, URL/email removal, symbol stripping while **retaining basic punctuation** (`.,;:()-`), and whitespace normalization. NLTK is pinned in `requirements.txt` (`3.10.3`) but never imported anywhere. No lemmatizer or explicit tokenization exists (scikit-learn `TfidfVectorizer` performs implicit whitespace/word boundary tokenization).
* **spaCy (`src/clause_splitter.py`):** `spacy.load("en_core_web_sm")` is initialized at module import into `_nlp`, but `_nlp` is never referenced or called in any function.

### 2.2 Dataset Splitting & Evaluation Leakage
* **Specification (`PRD.md` Section 10.4, 13.1 RSK-13):** Acknowledges the risk of clause-level train/test leakage when multiple clauses from the same contract appear in both training and test partitions.
* **Current Codebase (`src/feature_extraction.py`, `docs/model_card.md`):** Uses clause-level stratified 80/20 train/test split (`random_state=42`) across the 12,204 clauses from 510 contracts. Reported baseline numbers (Accuracy 0.7190, Macro F1 0.6474) represent this clause-stratified split (**Split A**).
* **Gap:** No grouped splitting protocol by `contract_id` (**Split B**) exists in the repository.

### 2.3 Artifact Generation & Packaging
* **Specification (`PRD.md` Section 10.5, `TechStack.md` Section 5.5):** Runtime relies on `artifacts/best_model.joblib`, `artifacts/tfidf_vectorizer.joblib`, `artifacts/label_encoder.joblib`, and `artifacts/calibrated_model.joblib`.
* **Current Codebase:** Existing training scripts (`src/train_baseline.py`, `src/train_svm.py`, `src/train_nb.py`, `src/train_random_forest.py`) write `.pkl` files to `models/`. `artifacts/calibrated_model.joblib` was created via ad-hoc scratch scripts. No unified, reproducible script exists in `src/` to produce `artifacts/*.joblib` alongside an `artifacts/manifest.json`.

### 2.4 Model Selection & Runtime Serving
* **Specification (`PRD.md` Section 5.2 FR-05.4, `TechStack.md` Section 5.5):** API reports `model_name` and serves the selected model.
* **Current Codebase (`api/services/ml_service.py`):** Serves `best_model.joblib` (or `calibrated_model.joblib` if present) with `model_name` hard-coded to `"LogisticRegression"`. The other models (Linear SVM, Multinomial Naive Bayes, Random Forest) are benchmarked only and not selectable.

### 2.5 Intelligent Search Corpus & Upload Scoping
* **Specification (`PRD.md` Section 5.2 FR-07.6):** Intelligent search should support searching user-uploaded contracts or stored contracts.
* **Current Codebase (`src/search.py`, `api/routers/search.py`):** `/search` only searches a static in-memory index of 12,204 pre-indexed CUAD clauses (`data/clauseiq_dataset_clean.csv`). It does not allow searching uploaded contract clauses by `contract_id`.

### 2.6 Database Schema, Operations & API Endpoints
* **Specification (`PRD.md` Section 10.6, `database/schema.sql`):** 
  - Table column is `document_name` in `contracts` (not `contract_name`).
  - Writes in `api/services/supabase_service.py` are non-atomic: `contracts` row is inserted first, followed by `clauses`. A failure during clause insertion leaves an empty contract row.
  - No read endpoints exist (`GET /contracts`, `GET /contracts/{id}/clauses`).
  - `/classify/file` does not return `contract_id` to the client.
  - RLS policies currently allow public `SELECT` and `INSERT` (`USING (true)`).

### 2.7 Clause Segmentation Hardcoding
* **Specification (`PRD.md` Section 5.2 FR-03, `TechStack.md` Section 7.1):** Clause segmentation should be general-purpose.
* **Current Codebase (`src/clause_splitter.py`):** Lines 37-56 contain explicit string filters tailored to the synthetic demo document (`"ClauseIQ Synthetic Test Document"`, `"SYNTHETIC COMPANY SERVICE AGREEMENT"`, `"ClauseIQ Test Document | Fictional Parties"`).

### 2.8 Upload Hardening & CORS
* **Specification (`PRD.md` Section 5.2 FR-01.5, FR-10; `TechStack.md` Section 18):** File uploads should be validated for size, page count, and magic header (`%PDF`).
* **Current Codebase (`api/routers/classify.py`, `api/services/ml_service.py`):** Only filename extension (`.pdf`, `.txt`) and non-empty content checks are enforced. CORS defaults allow wildcard `*` with credentials.

### 2.9 Frontend UI/UX Design System
* **Specification (`DesignDoc.md`):** Complete design system specifying:
  - Header status pill with tooltip details, theme toggle, and offline banner with Retry.
  - Confidence ring (SVG circular gauge) on single results with mandatory "estimate, not a guarantee" notice.
  - Deterministic 8-hue category tag palette.
  - Document results summary strip (High/Moderate/Low counts), client-side category filter, and sorting.
  - Search view with explicit CUAD library scope label and query-word `<mark>` highlighting.
  - Dark mode and WCAG AA accessibility.
* **Current Codebase (`frontend/src/`):** Baseline linear styling with partial status badges, basic pagination, and no dark theme, circular ring, or document summary strip.

---

## 3. Test Suite Baseline Execution

* **Command Executed:** `pytest tests/` (via `.venv\Scripts\pytest`)
* **Result:** **43 passed in 11.62s** (100% pass rate across `test_sprint1.py`, `test_sprint2.py`, `test_sprint3.py`).
* **Note on root `pytest`:** Running unconstrained `pytest` without path filters triggers collection in `scratch/test_*.py` which are ad-hoc development scripts. `pytest.ini` will be configured to target `tests/` explicitly.

---

## 4. Action Plan Summary by Phase

| Phase | Core Objective |
| :--- | :--- |
| **Phase 1** | Build reproducible `src/build_artifacts.py`, implement `src/evaluation_protocol.py` (Split A + Split B), compute calibration & reliability tables, real-document check, write `docs/BASELINE.md`. |
| **Phase 2** | Controlled ML experimentation rounds in `results/experiments.csv` (text ablations, n-grams, models, class weights, CV tuning, calibration, out-of-scope), produce error analysis in `docs/ERROR_ANALYSIS.md`, select optimal model and update artifacts. |
| **Phase 3** | Backend completion: dynamic `model_name` from manifest, uploaded contract search indexing (`contract_id`), read endpoints (`GET /contracts`, `GET /contracts/{id}/clauses`), atomic Supabase persistence, upload hardening, clean `clause_splitter.py` and `requirements.txt`. |
| **Phase 4** | Frontend overhaul per `DesignDoc.md`: design tokens, dark mode, confidence ring, status badges, deterministic tag colors, summary strip, filter/sort, query highlight, a11y, browser verification & screenshots. |
| **Phase 5** | End-to-end integration test, documentation updates, security/leak checks, and final report. |
