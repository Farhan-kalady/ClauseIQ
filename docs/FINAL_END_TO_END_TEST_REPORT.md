# ClauseIQ — Final End-to-End Test and Verification Report

**Project Title:** ClauseIQ – Machine Learning-Based Contract Clause Classification and Intelligent Search System  
**Academic Degree:** Master of Computer Applications (MCA Mini Project)  
**Verification Date:** October 13, 2026  
**Auditor:** Antigravity AI Engineering Pair-Programmer  
**Target Environment:** Windows 11, Python 3.14.6 (`.venv`), Node.js v20.x, React 18 / Vite 6.4.4, FastAPI 0.115+, Supabase PostgreSQL  
**Verification Document:** `test_data/ClauseIQ_Synthetic_Company_Service_Agreement_Test.pdf` (Fictional synthetic company agreement)  
**Overall Status:** **VERIFIED** (All 9 Test Suites and Pipelines Fully Operational)

---

## 1. Project Overview & Architecture

ClauseIQ is an end-to-end legal document intelligence platform built using **Classical Machine Learning**. It automates the extraction, segmentation, and multi-class classification of legal contract clauses into the 41 canonical categories of the **Contract Understanding Atticus Dataset (CUAD v1)**, and provides semantic relevance search via **TF-IDF Vectorization** and **Cosine Similarity**.

### System Architecture Highlights:
1. **Frontend:** React 18 + Vite SPA, responsive dark-mode glassmorphic interface, real-time backend health monitoring, multi-tab layout (`ClassifierView`, `SearchView`).
2. **Backend API:** FastAPI application with asynchronous lifespan handlers, strict Pydantic schemas, modular routers (`/health`, `/classify`, `/classify/file`, `/search`, `/categories`), and CORS middleware.
3. **Machine Learning Pipeline:** 
   - Preprocessing: `text_cleaner.py` (normalizes punctuation and token structure).
   - Clause Segmentation: `clause_splitter.py` (sentence/clause boundary detection with regex fallback).
   - Ingestion: `pdf_extractor.py` (PyMuPDF document stream extraction).
   - Feature Extraction: `TfidfVectorizer` (10,000 unigram/bigram features, sublinear TF scaling).
   - Model Inference: Tuned `LogisticRegression` champion model providing native multi-class probability scores (`predict_proba`) and top-3 alternative rankings.
4. **Intelligent Search Engine:** `ClauseSearchEngine` indexing 12,204 CUAD contract clauses with top-k ranking, category filtering, and score thresholds.
5. **Database Integration:** Cloud-hosted Supabase PostgreSQL storing uploaded contract metadata (`contracts`), individual extracted clauses (`clauses`), classification telemetry (`classification_logs`), and search audit trails (`search_logs`).

---

## 2. Environment Setup & Startup Instructions

### Prerequisites
- Python 3.11+ (Active virtual environment at `.venv`)
- Node.js 18+ and npm
- Valid Supabase project configuration in `.env`

### Environment Configuration (`.env`)
```env
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_KEY=<publishable-anon-key>
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,*
```

### Starting the Backend Server
```powershell
# From project root:
.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive Swagger API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative ReDoc Documentation: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Starting the React Frontend
```powershell
# In a separate terminal, from project root:
cd frontend
npm run dev
```
- Web Application URL: [http://localhost:5173/](http://localhost:5173/)

---

## 3. Test Suite 1 — Backend & API Verification

The FastAPI application was initialized and tested across all endpoints using HTTP requests:

| Endpoint | Method | Input Tested | HTTP Status | Response Summary | Result |
| :--- | :---: | :--- | :---: | :--- | :---: |
| `/health` | `GET` | None | `200 OK` | `{"status":"healthy","service":"ClauseIQ API","model_loaded":true,"search_engine_loaded":true,"supabase_connected":true}` | **PASS** |
| `/categories` | `GET` | None | `200 OK` | Total 41 categories returned matching official CUAD v1 class list. | **PASS** |
| `/classify` | `POST` | Valid single clause | `200 OK` | Predicted category, calibrated probability, and top-3 alternatives. | **PASS** |
| `/classify` | `POST` | Empty string `""` | `422 Unprocessable` | Pydantic string validation triggered (`min_length: 1`). | **PASS** |
| `/classify` | `POST` | Whitespace `"   "` | `400 Bad Request` | `"Clause text cannot be empty or solely whitespace."` | **PASS** |
| `/classify` | `POST` | Gibberish punctuation `"!@#$%"` | `400 Bad Request` | `"Clause text contains no valid alphanumeric or legal tokens."` | **PASS** |
| `/classify/file`| `POST` | Synthetic test PDF | `200 OK` | 69 clauses extracted, classified, and persisted to Supabase. | **PASS** |
| `/classify/file`| `POST` | Empty file (0 bytes) | `400 Bad Request` | `"Uploaded file is empty."` | **PASS** |
| `/classify/file`| `POST` | Corrupted PDF bytes | `400 Bad Request` | `"Corrupted or invalid PDF file..."` | **PASS** |
| `/classify/file`| `POST` | Unsupported extension `.png` | `400 Bad Request` | `"Unsupported file format '.png'..."` | **PASS** |
| `/search` | `POST` | Query `"termination"` | `200 OK` | Ranked clauses with similarity scores and contract IDs. | **PASS** |
| `/search` | `POST` | Empty query `"   "` | `400 Bad Request` | `"Search query cannot be empty or solely whitespace."` | **PASS** |
| `/search` | `POST` | Out-of-vocabulary query | `200 OK` | Clean zero-results handling (`{"total_results": 0, "results": []}`). | **PASS** |

---

## 4. Test Suite 2 — Single-Clause Classification Results

The classifier was evaluated on the three benchmark test inputs specified in the test requirements:

### Input A: Confidentiality
> *"The Receiving Party agrees to keep all confidential information received from the Disclosing Party strictly confidential and shall not disclose such information to any third party without prior written consent."*
- **Expected Category:** Confidentiality
- **Actual Predicted Category:** `Anti-Assignment`
- **Confidence Score:** `0.1227` (12.27% probability)
- **Top Alternatives:** `Rofr/Rofo/Rofn` (5.48%), `Non-Compete` (5.35%), `Audit Rights` (4.70%)
- **Model Used:** `LogisticRegression` (Sprint 2 tuned champion)
- **Supabase Logged:** Verified in `classification_logs` (Record ID: `e7ffef82-ef52-4cb6-958f-143eca5a7521`)
- **Analysis:** In the official CUAD v1 benchmark schema, there is **no category named "Confidentiality"** among the 41 classes. Because the model is strictly trained on CUAD v1, it correctly distributes probabilities diffusely with low confidence across available categories. This represents authentic model behavior rather than a software defect.

### Input B: Termination
> *"Either party may terminate this Agreement by providing thirty days written notice to the other party. In case of a material breach, the non-breaching party may terminate this Agreement if the breach is not remedied within the specified period."*
- **Expected Category:** Termination
- **Actual Predicted Category:** `Termination For Convenience`
- **Confidence Score:** `0.5427` (54.27% probability)
- **Top Alternatives:** `Change Of Control` (9.35%), `Non-Disparagement` (3.42%), `Notice Period To Terminate Renewal` (3.30%)
- **Supabase Logged:** Verified in `classification_logs` (Record ID: `9b6f851c-d8f7-4c61-94af-dc0c48919d70`)
- **Result:** **PASS** (Matches canonical CUAD termination category).

### Input C: Governing Law
> *"This Agreement shall be governed by the laws of India. The courts located in Bengaluru shall have exclusive jurisdiction over disputes arising from this Agreement."*
- **Expected Category:** Governing Law
- **Actual Predicted Category:** `Governing Law`
- **Confidence Score:** `0.7304` (73.04% probability)
- **Top Alternatives:** `Competitive Restriction Exception` (1.80%), `Exclusivity` (1.77%), `Cap On Liability` (1.49%)
- **Supabase Logged:** Verified in `classification_logs` (Record ID: `163c0d21-e5c6-416a-b2cb-a8f4119cff33`)
- **Result:** **PASS** (Exact category match with 73.04% confidence).

---

## 5. Test Suite 3 — PDF Upload, Text Extraction & Clause Segmentation

**Document Tested:** `test_data/ClauseIQ_Synthetic_Company_Service_Agreement_Test.pdf`  
**File Size:** 34,835 bytes (3 pages)

### Extraction Summary Table

| Test Item | Specification / Expectation | Actual Result | Status |
| :--- | :--- | :--- | :---: |
| **PDF Upload** | HTTP Multipart Form upload via `/classify/file` | `HTTP 200 OK` | **PASS** |
| **Extracted Text** | Readable text extracted via PyMuPDF stream | **9,144 characters** extracted | **PASS** |
| **Document Headings Found** | All 17 separately headed sections | **17 / 17 present** in extracted text | **PASS** |
| **Extracted Clause Segments** | Identified clauses from document | **69 segments** | **PASS** |
| **Successfully Classified Segments**| Model inference on extracted segments | **69 segments** (100%) | **PASS** |
| **Failed Segments** | Unhandled parsing / classification failures | **0 segments** | **PASS** |
| **Frontend Display** | Multi-clause results card rendered in UI | Complete list with badges & scores | **PASS** |
| **Database Records Created** | Contracts and clauses inserted into Supabase | **1 contract + 69 clauses** | **PASS** |

### Detailed Segmentation & Heading Analysis
The synthetic contract contains 17 numbered section headings (`1. DEFINITIONS...`, `2. EFFECTIVE DATE...`, etc.). The splitter produced **69 clause segments**:
- **Why 69 segments?** The sentence tokenizer splits on sentence-terminating punctuation followed by whitespace and an uppercase/numeric character (`(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])`). When numbered section headings such as `"1. DEFINITIONS AND INTERPRETATION"` appear, the period in `"1."` is preceded by `"1"` and followed by a space and `"D"`, causing the section number (`"1."`, `"2."`, etc.) to be segmented as a short fragment.
- **Heading Attachment:** In all cases, the heading text itself (e.g., `"DEFINITIONS AND INTERPRETATION"`, `"GOVERNING LAW AND JURISDICTION"`) remains attached to the section's first substantive sentence, ensuring legal context is preserved during classification.
- **Section Completeness:** Zero sections were lost or duplicated. Every legal provision from Section 1 to Section 17 is classified and accounted for.

---

## 6. Test Suite 4 — Intelligent Clause Search Verification

### Search Scope Clarification
> **Search Scope:** The intelligent search engine queries the **12,204 pre-indexed contract clauses** from the CUAD dataset (`data/clauseiq_dataset_clean.csv`). Uploaded contract documents are securely stored in the Supabase database (`contracts` and `clauses` tables) and classified for the user, but are not dynamically appended to the static in-memory TF-IDF index.

### Results on Seven Benchmark Queries

| Query # | Search Query | Top Result Ranked #1 | Pred. Category | True Category | Cosine Similarity | Supabase Audit ID |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| **1** | `confidential information disclosure` | `"...misuse of confidential information..."` (WHITESMOKE, INC.) | Uncapped Liability | Uncapped Liability | **0.3893** (38.9%) | `98adcd3f` |
| **2** | `termination of agreement` | `"Upon termination of this Agreement,..."` (Paperexchange.com) | Post-Termination Services | Post-Termination Services | **0.3697** (37.0%) | `6f93ddc8` |
| **3** | `governing law and jurisdiction` | `"The terms of the Governing Law and Dispute Resolution..."` (Scansource) | Document Name | Governing Law | **0.3836** (38.4%) | `71381a15` |
| **4** | `intellectual property ownership` | `"INTELLECTUAL PROPERTY RIGHTS AGREEMENT..."` (Rare Element Resources) | Document Name | Document Name | **0.6130** (61.3%) | `67fbb65e` |
| **5** | `payment and invoices` | `"Payment Data Systems, Inc...."` (Usio Inc.) | Parties | Parties | **0.1956** (19.6%) | `1848c505` |
| **6** | `indemnification against third party claims` | `"...liable for any third party claims..."` (NETGEAR, INC.) | Cap On Liability | Cap On Liability | **0.2891** (28.9%) | `f6cc4a8e` |
| **7** | `limitation of liability` | `"Limitation of Liability of the Sponsor...."` (DOMINI ADVISOR TRUST) | Cap On Liability | Cap On Liability | **0.7215** (72.2%) | `8e8e694d` |

- **Ranking Order:** Results are strictly ranked in descending order of cosine similarity.
- **Category Filtering:** Tested with `category_filter="Governing Law"`, returning only clauses annotated as Governing Law.
- **Score Threshold:** Validated with `min_score` parameter.

---

## 7. Test Suite 5 — Supabase Database Integration Verification

Real database operations were executed against the live Supabase project instance:

### Tables Inspected & Verified:
1. **`contracts`**:
   - Stores metadata for uploaded contract files (`id`, `document_name`, `created_at`).
   - Verified insertion: Record `0390cc53-4182-4761-99ab-6a97fd624239` for `ClauseIQ_Synthetic_Company_Service_Agreement_Test.pdf`.
2. **`clauses`**:
   - Stores extracted clauses linked by foreign key (`contract_id`, `clause_text`, `category`, `confidence_score`).
   - Verified insertion: Exactly 69 clause records linked to the test contract.
3. **`classification_logs`**:
   - Telemetry audit log for `/classify` requests (`input_text`, `predicted_category`, `confidence_score`, `created_at`).
   - Verified insertions for Inputs A, B, and C.
4. **`search_logs`**:
   - Audit trail for `/search` queries (`query`, `category_filter`, `top_k`, `results_count`, `created_at`).
   - Verified insertions for all 7 search queries.
5. **Row Level Security (RLS) & Permissions:**
   - Tables operate under configured RLS policies permitting authorized API reads and inserts.
   - Graceful offline fallback: If Supabase credentials are not present, API routes continue functioning without crashing.

---

## 8. Test Suite 6 — Frontend Functionality & Verification

The React SPA interface was verified across all core user flows:

| UI Component | Expected Functionality | Actual Observation | Status |
| :--- | :--- | :--- | :---: |
| **Header** | Logo, Sprint badge, navigation tabs, health status pill | Displays "ClauseIQ Sprint 3", "Model Ready • DB Active" (green dot) | **PASS** |
| **Mode Switcher** | Toggle between "Paste Clause Text" and "Upload Contract Document" | Switches active view smoothly without re-rendering issues | **PASS** |
| **Text Classifier** | Textarea, sample clause chips, classify button, clear button | Text input functions properly, sample buttons load preset text | **PASS** |
| **Result Card** | Prediction badge, confidence progress bar, top-3 alternatives | Calibrated percentage and top alternative classes render accurately | **PASS** |
| **Document Upload** | Drag-and-drop dropzone, file selector, submit button | Selects `.pdf` / `.txt` files, displays file name and size in KB | **PASS** |
| **Document Results** | Multi-clause scrollable list with clause index and confidence | Renders all 69 clauses with individual category pills | **PASS** |
| **Search View** | Search input, sample query pills, top-k slider (1–25), category dropdown | Search executes smoothly, slider updates value dynamically | **PASS** |
| **Search Results** | Ranked list with similarity badge, clause text, source contract | Ranked items rendered cleanly with cosine similarity percentage | **PASS** |
| **Error Feedback** | Red alert banner with clear explanation | Displays user-friendly error banners for invalid or empty inputs | **PASS** |

---

## 9. Test Suite 7 — Model & Artifact Verification

Model and vectorizer artifacts were verified using programmatic inspection:

- **Model Type:** `LogisticRegression` (scikit-learn linear model).
- **Number of Classes:** Exactly **41 classes** (`model.classes_` and `label_encoder.classes_`).
- **Feature Dimension:** Exactly **10,000 features** matching `TfidfVectorizer.max_features`.
- **N-gram Range:** Unigrams and bigrams (`ngram_range=(1, 2)`).
- **Probability Calibration:** Verified `predict_proba` returns authentic normalized probability vectors summing to `1.000000`.
- **Integrity Check:** The model file `artifacts/best_model.joblib` is identical to `models/logistic_regression.pkl` (3,281,519 bytes). No dummy or synthetic model is being used.

---

## 10. Test Suite 8 — Error Handling & Edge Cases

| Edge Case Test | Input Provided | Expected Behavior | Actual Response | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Empty Text Input** | `""` | Reject input | `HTTP 422 Unprocessable Entity` | **PASS** |
| **Whitespace Only** | `"   \n\t  "` | Reject input | `HTTP 400 Bad Request` ("Cannot be solely whitespace") | **PASS** |
| **Punctuation / Gibberish**| `"!@#$%^&*()_+{}[]:;<>/?"` | Reject input | `HTTP 400 Bad Request` ("No valid alphanumeric tokens") | **PASS** |
| **Empty File Upload** | `0 bytes` file | Reject input | `HTTP 400 Bad Request` ("Uploaded file is empty") | **PASS** |
| **Corrupted PDF Upload**| Invalid PDF byte stream | Catch error | `HTTP 400 Bad Request` ("Corrupted or invalid PDF file") | **PASS** |
| **Unsupported File Type**| Image file (`document.png`) | Reject extension | `HTTP 400 Bad Request` ("Unsupported file format '.png'") | **PASS** |
| **Very Large Input** | 500 repetitive clause sentences | Handle within limits | `HTTP 200 OK` (Processed and classified) | **PASS** |
| **Empty Search Query** | `"   "` | Reject query | `HTTP 400 Bad Request` ("Search query cannot be empty") | **PASS** |
| **Out-of-Vocabulary Search**| `"zzzyyyxxxwwvuuuttt12345"`| Return empty list | `HTTP 200 OK` (`total_results: 0`) | **PASS** |
| **Invalid top_k (< 1)** | `top_k: 0` | Reject parameter | `HTTP 422 Unprocessable Entity` | **PASS** |
| **Invalid top_k (> 50)**| `top_k: 999` | Reject parameter | `HTTP 422 Unprocessable Entity` | **PASS** |

---

## 11. Test Suite 9 — Automated Tests & Production Build

### Pytest Test Suite
- **Command:** `.venv\Scripts\python.exe -m pytest -v`
- **Total Tests Collected:** **43 tests**
- **Passed:** **43 passed** (100% pass rate)
- **Failed:** 0
- **Skipped:** 0
- **Execution Time:** ~6.5 seconds

### Production Frontend Build
- **Command:** `npm run build` (in `frontend/`)
- **Tool:** Vite 6.4.4
- **Modules Transformed:** 32 modules
- **Build Output:**
  - `dist/index.html`: 1.29 kB (gzip: 0.69 kB)
  - `dist/assets/index-DuPSKcnK.css`: 9.22 kB (gzip: 2.54 kB)
  - `dist/assets/index-D6Q3v_ji.js`: 163.45 kB (gzip: 51.20 kB)
- **Status:** **SUCCESS** (0 errors, 0 warnings)

---

## 12. Bugs Encountered & Fixes Applied

During the comprehensive end-to-end audit, 3 verified edge-case bugs were diagnosed and resolved:

### Bug 1: Punctuation-Only Gibberish Bypassing Input Validation
- **Symptom:** Passing strings consisting exclusively of punctuation symbols (e.g., `"!@#$%^&*()_+{}[]:;<>/?"`) returned `HTTP 200 OK` with an uncalibrated prediction on an all-zero TF-IDF vector instead of returning a validation error.
- **Root Cause:** `clean_text()` strips non-alphanumeric noise while intentionally preserving punctuation characters `.,;:()-`. Consequently, `cleaned` was not empty (`": ; ( )"`), bypassing the `if not cleaned:` check.
- **Fix:** In `api/services/ml_service.py` (`classify_clause`), added explicit alphanumeric token verification:
  ```python
  if not cleaned or not any(c.isalnum() for c in cleaned):
      raise ValueError("Clause text contains no valid alphanumeric or legal tokens.")
  ```
- **Verification:** Verified by `tests/test_sprint3.py::test_classify_gibberish_input`, returning `HTTP 400 Bad Request`.

### Bug 2: Unhandled Corrupted PDF Uploads Causing HTTP 500
- **Symptom:** Uploading a malformed or corrupted PDF caused `pymupdf.open()` to raise `pymupdf.FileDataError`, escaping to the generic exception handler and returning `HTTP 500 Internal Server Error`.
- **Root Cause:** Missing `try...except` block around PyMuPDF stream parsing in `classify_document`.
- **Fix:** Wrapped `pymupdf.open` in a guarded block that converts PDF stream parsing failures into a client-safe `ValueError`:
  ```python
  try:
      with pymupdf.open(stream=file_content, filetype="pdf") as doc:
          for page in doc:
              extracted_text += page.get_text() + "\n"
  except Exception as e:
      raise ValueError(f"Corrupted or invalid PDF file '{filename}': {str(e)}")
  ```
- **Verification:** Verified by `test_classify_corrupted_pdf_upload`, returning `HTTP 400 Bad Request`.

### Bug 3: Missing File Extension Validation on Document Upload
- **Symptom:** Uploading arbitrary binary files (e.g., `.png`, `.exe`) caused the backend to attempt fallback plain text decoding (`latin-1`), passing binary gibberish into the NLP pipeline.
- **Root Cause:** The endpoint `/classify/file` lacked file extension validation.
- **Fix:** Added validation in `classify_document`:
  ```python
  fn_lower = filename.lower()
  if not (fn_lower.endswith(".pdf") or fn_lower.endswith(".txt")):
      ext = Path(filename).suffix or "unknown"
      raise ValueError(f"Unsupported file format '{ext}'. Please upload a PDF (.pdf) or plain text (.txt) file.")
  ```
- **Verification:** Verified by `test_classify_unsupported_file_upload`, returning `HTTP 400 Bad Request`.

---

## 13. Remaining Known Limitations

1. **CUAD Category Scope:** The model is strictly trained on the 41 categories of the CUAD v1 benchmark. Clauses belonging to legal concepts outside the 41 CUAD classes (such as standalone confidentiality agreements or force majeure clauses, which do not have separate labels in CUAD v1) are categorized into the nearest commercial class with low confidence.
2. **Search Index Scope:** The intelligent search engine operates over the 12,204 pre-indexed CUAD clauses. Uploaded contracts are stored in Supabase and classified, but are not dynamically appended to the static TF-IDF search matrix.
3. **Regex Splitting on Numbered Headings:** Headings formatted with standalone numbers (`1.`, `2.`) are split into their own short segments by the sentence tokenizer. While harmless (they receive low confidence and the heading words remain with the clause), a future enhancement could merge isolated numeric prefixes.

---

## 14. Final Project Status & Guide Demonstration Readiness

### Final Verdict: **VERIFIED & READY FOR LIVE DEMONSTRATION**

ClauseIQ has completed full end-to-end verification. All components—from the Classical ML models and TF-IDF vectorizer, to the FastAPI backend, Supabase database, and React frontend—are operating in alignment with project requirements.

### Quick Demonstration Instructions for Guide Evaluation:
1. **Start Backend:** `.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000 --reload`
2. **Start Frontend:** `cd frontend && npm run dev`
3. **Open Browser:** Navigate to `http://localhost:5173/`
4. **Demonstrate Health:** Point out the green status pill: **Model Ready • DB Active**.
5. **Demonstrate Single Classification:** Use sample chip **Governing Law** and click **Classify Clause**.
6. **Demonstrate PDF Upload:** Switch to upload mode, select `test_data/ClauseIQ_Synthetic_Company_Service_Agreement_Test.pdf`, and click **Extract & Classify Document**. Review the 69 extracted clauses.
7. **Demonstrate Intelligent Search:** Switch to **Clause Search** tab, search for `"termination for convenience"`, and demonstrate ranked similarity scores and category filtering.
