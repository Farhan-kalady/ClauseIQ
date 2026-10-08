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
