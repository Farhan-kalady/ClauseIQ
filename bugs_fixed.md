# ClauseIQ - Bugs Fixed (Sprint 3)

This document records the real bugs encountered, diagnosed, and resolved during the Sprint 3 integration and deployment phase.

---

## Bug 1
**Symptom:**  
`tests/test_sprint1.py` crashed during test collection with the error:  
`ImportError: DLL load failed while importing token: An Application Control policy has blocked this file.`

**Cause:**  
`src/clause_splitter.py` unconditionally imported `spacy` and loaded `en_core_web_sm` at the module level. On Windows environments governed by Windows Defender Application Control (WDAC) or AppLocker policies, unsigned Cython C-extension DLLs (specifically `spacy.tokens.token`) residing in local virtual environments are blocked from execution.

**Fix:**  
Modified `src/clause_splitter.py` to wrap the spaCy import and model loading in a `try...except` block. Implemented a fallback sentence-boundary regex tokenizer tailored for legal document clauses (`re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])", clean_input)`). If spaCy cannot be loaded, the system seamlessly uses the fallback without throwing unhandled exceptions.

**Verification:**  
Executed `python -m pytest tests/test_sprint1.py` and `python src/clause_splitter.py`. All 9 Sprint 1 unit tests passed with 100% success rate, successfully extracting 29 clauses from `data/raw_pdfs/sample_contract.pdf`.

---

## Bug 2
**Symptom:**  
FastAPI failed during route registration with:  
`RuntimeError: Form data requires "python-multipart" to be installed.`

**Cause:**  
The newly introduced `/classify/file` endpoint utilizes FastAPI's `UploadFile = File(...)` parameter to accept contract PDF and text uploads. Starlette/FastAPI requires the `python-multipart` library to process multipart/form-data payloads, which was not present in the original repository `requirements.txt`.

**Fix:**  
Installed `python-multipart>=0.0.12` in the project virtual environment and appended it directly to `requirements.txt`.

**Verification:**  
Executed `python -m pytest tests/test_sprint3.py`. Both `test_classify_pdf_document_upload` and `test_classify_text_document_upload` executed successfully, returning HTTP 200 with extracted clauses and classification probabilities.

---

## Bug 3
**Symptom:**  
Category metadata test in `tests/test_sprint3.py` raised:  
`AssertionError: assert 'Termination' in data["categories"]`

**Cause:**  
The test initially checked for a generic category name `'Termination'`, whereas the official 41-class CUAD v1 annotation schema designates the category as `'Termination For Convenience'`.

**Fix:**  
Updated the test assertion in `tests/test_sprint3.py` to match the exact canonical CUAD category label `'Termination For Convenience'`.

**Verification:**  
Executed `python -m pytest tests/test_sprint3.py::test_categories_endpoint`, which passed immediately and confirmed all 41 CUAD classes are served accurately.

---

## Bug 4
**Symptom:**  
Sending punctuation-only or non-word symbols (e.g. `"!@#$%^&*()_+{}[]:;<>/?"`) to `POST /classify` returned `HTTP 200 OK` with an uncalibrated prediction on an all-zero TF-IDF feature vector instead of a validation error.

**Cause:**  
`clean_text()` stripped non-alphanumeric noise while intentionally preserving punctuation characters `.,;:()-`. Consequently, `cleaned` contained punctuation characters (`": ; ( )"`), which passed the `if not cleaned:` check despite having zero alphanumeric or legal word tokens.

**Fix:**  
Updated `classify_clause` in `api/services/ml_service.py` to check `if not cleaned or not any(c.isalnum() for c in cleaned): raise ValueError("Clause text contains no valid alphanumeric or legal tokens.")`.

**Verification:**  
Executed `tests/test_sprint3.py::test_classify_gibberish_input`, which passed and confirmed `HTTP 400 Bad Request` is returned with a clear error message.

---

## Bug 5
**Symptom:**  
Uploading corrupted or unparseable PDF byte streams to `POST /classify/file` raised an unhandled `pymupdf.FileDataError`, causing the server to return `HTTP 500 Internal Server Error`.

**Cause:**  
`classify_document` opened the PDF byte stream without a guarded `try...except` block to intercept PyMuPDF document parsing exceptions.

**Fix:**  
Wrapped `pymupdf.open()` in a `try...except` block in `api/services/ml_service.py`, converting parsing errors into a structured client-safe `ValueError(f"Corrupted or invalid PDF file '{filename}': {str(e)}")` which FastAPI returns as `HTTP 400 Bad Request`.

**Verification:**  
Executed `tests/test_sprint3.py::test_classify_corrupted_pdf_upload`, returning `HTTP 400 Bad Request`.

---

## Bug 6
**Symptom:**  
Uploading unsupported binary file formats (e.g., `.png`, `.exe`) to `POST /classify/file` caused the backend to attempt fallback plain text decoding (`latin-1`), passing binary noise into the NLP pipeline.

**Cause:**  
The file upload endpoint did not validate file extensions, assuming any non-PDF was plain text.

**Fix:**  
Added file extension validation in `classify_document` (`api/services/ml_service.py`) ensuring only `.pdf` and `.txt` files are accepted, raising a `ValueError` for unsupported extensions.

**Verification:**  
Executed `tests/test_sprint3.py::test_classify_unsupported_file_upload`, confirming `HTTP 400 Bad Request`.
