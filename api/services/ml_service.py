from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional
import uuid
import joblib
import numpy as np
import pymupdf

from api.config import settings

logger = logging.getLogger("ClauseIQ.MLService")

# Ensure src/ is in sys.path
src_path = str(settings.SRC_DIR)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from text_cleaner import clean_text
from clause_splitter import split_into_clauses
from pdf_extractor import strip_headers_footers

# Global artifacts holders (loaded once at startup)
_model = None
_calibrated_model = None
_vectorizer = None
_label_encoder = None
_manifest = {}
_model_name = "LogisticRegression-HybridWordChar"

# In-memory index of uploaded contracts for instant scoped search
_uploaded_contracts: Dict[str, Dict[str, Any]] = {}

# Initialize NLTK lemmatizer for inference consistency with training
try:
    import nltk
    from nltk.stem import WordNetLemmatizer
    _lemmatizer = WordNetLemmatizer()

    def clean_text_pipeline(text: str) -> str:
        base = clean_text(text)
        if not base:
            return ""
        return " ".join([_lemmatizer.lemmatize(w) for w in base.split()])
except Exception:
    def clean_text_pipeline(text: str) -> str:
        return clean_text(text)


def load_artifacts():
    """Load machine learning model, vectorizer, and label encoder once at startup."""
    global _model, _calibrated_model, _vectorizer, _label_encoder, _manifest, _model_name
    if _model is not None and _vectorizer is not None and _label_encoder is not None:
        return

    art_dir = settings.ARTIFACTS_DIR
    if not (art_dir / "best_model.joblib").is_file():
        art_dir = settings.MODELS_DIR

    model_path = art_dir / "best_model.joblib" if (art_dir / "best_model.joblib").is_file() else art_dir / "logistic_regression.pkl"
    vec_path = art_dir / "tfidf_vectorizer.joblib" if (art_dir / "tfidf_vectorizer.joblib").is_file() else art_dir / "tfidf_vectorizer.pkl"
    le_path = art_dir / "label_encoder.joblib" if (art_dir / "label_encoder.joblib").is_file() else art_dir / "label_encoder.pkl"
    cal_path = art_dir / "calibrated_model.joblib"
    manifest_path = art_dir / "manifest.json"

    _model = joblib.load(model_path)
    _vectorizer = joblib.load(vec_path)
    _label_encoder = joblib.load(le_path)

    if manifest_path.is_file():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                _manifest = json.load(f)
                _model_name = _manifest.get("model_name", _model_name)
        except Exception as e:
            logger.warning(f"Could not load manifest.json: {e}")
            _model_name = _model.__class__.__name__

    if cal_path.is_file():
        try:
            _calibrated_model = joblib.load(cal_path)
        except Exception:
            _calibrated_model = None


def is_model_loaded() -> bool:
    return _model is not None


def get_model_name() -> str:
    load_artifacts()
    return _model_name


def get_categories_list() -> List[str]:
    load_artifacts()
    return list(_label_encoder.classes_)


def get_uploaded_contract(contract_id: str) -> Optional[Dict[str, Any]]:
    return _uploaded_contracts.get(contract_id)


def list_uploaded_contracts() -> List[Dict[str, Any]]:
    return [
        {
            "id": cid,
            "document_name": cdata["document_name"],
            "total_clauses": cdata["total_clauses"],
            "created_at": cdata.get("created_at", ""),
        }
        for cid, cdata in _uploaded_contracts.items()
    ]


def register_uploaded_contract(contract_id: str, document_name: str, clauses: List[Dict[str, Any]]):
    """Store uploaded document clauses and their TF-IDF vectors in-memory for scoped search."""
    load_artifacts()
    cleaned_texts = [c["cleaned_text"] for c in clauses]
    try:
        vectors = _vectorizer.transform(cleaned_texts) if cleaned_texts else None
    except Exception as e:
        logger.warning(f"Failed to vectorize uploaded contract clauses: {e}")
        vectors = None

    _uploaded_contracts[contract_id] = {
        "id": contract_id,
        "document_name": document_name,
        "total_clauses": len(clauses),
        "clauses": clauses,
        "vectors": vectors,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def classify_clause(clause_text: str) -> Dict[str, Any]:
    """Classify a single contract clause text using the loaded classical ML model."""
    load_artifacts()

    raw_text = clause_text.strip()
    if not raw_text:
        raise ValueError("Clause text cannot be empty or solely whitespace.")

    cleaned = clean_text_pipeline(raw_text)
    if not cleaned or not any(c.isalnum() for c in cleaned):
        raise ValueError("Clause text contains no valid alphanumeric or legal tokens.")

    # TF-IDF Feature Extraction (hybrid word+char or standard word)
    vec = _vectorizer.transform([cleaned])

    # Model inference
    predictor = _calibrated_model if (_calibrated_model is not None and hasattr(_calibrated_model, "predict_proba")) else _model

    alternatives = []
    if hasattr(predictor, "predict_proba"):
        probs = predictor.predict_proba(vec)[0]
        sorted_indices = np.argsort(-probs)
        pred_idx = int(sorted_indices[0])
        confidence = float(probs[pred_idx])
        conf_type = "probability"

        # Extract top-3 alternative classes
        for alt_idx in sorted_indices[1:4]:
            alt_label = str(_label_encoder.inverse_transform([alt_idx])[0])
            alt_prob = float(probs[alt_idx])
            alternatives.append({
                "category": alt_label,
                "confidence": round(alt_prob, 4),
            })
    else:
        # Fallback for models without predict_proba (e.g. LinearSVC)
        pred_idx = int(_model.predict(vec)[0])
        confidence = None
        conf_type = "not_available"
        if hasattr(_model, "decision_function"):
            decision = _model.decision_function(vec)[0]
            sorted_indices = np.argsort(-decision)
            pred_idx = int(sorted_indices[0])
            confidence = float(decision[pred_idx])
            conf_type = "decision_score"
            for alt_idx in sorted_indices[1:4]:
                alt_label = str(_label_encoder.inverse_transform([alt_idx])[0])
                alternatives.append({
                    "category": alt_label,
                    "confidence": round(float(decision[alt_idx]), 4),
                })

    predicted_label = str(_label_encoder.inverse_transform([pred_idx])[0])
    conf_rounded = round(confidence, 4) if confidence is not None else None

    # Determine mathematically evaluated confidence status based on documented test thresholds
    sec_prob = alternatives[0]["confidence"] if alternatives else 0.0
    margin = (confidence - sec_prob) if confidence is not None else 0.0

    if conf_rounded is None:
        status_label = "Not Available"
        is_out = False
    elif conf_rounded >= 0.50:
        status_label = "High confidence"
        is_out = False
    elif conf_rounded >= 0.25:
        status_label = "Moderate confidence"
        is_out = False
    elif conf_rounded >= 0.10 or (margin >= 0.05 and conf_rounded >= 0.07):
        status_label = "Low confidence – Review Required"
        is_out = False
    else:
        status_label = "Out of supported category scope"
        is_out = True

    return {
        "clause_text": raw_text,
        "cleaned_text": cleaned,
        "predicted_category": predicted_label,
        "confidence": conf_rounded,
        "confidence_score": conf_rounded,
        "confidence_type": conf_type,
        "confidence_status": status_label,
        "confidence_explanation": "Confidence represents the model's estimated probability for the predicted category. It does not represent guaranteed classification accuracy or legal certainty.",
        "is_out_of_scope": is_out,
        "model_name": _model_name,
        "alternatives": alternatives,
    }


def classify_document(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Process an uploaded contract document (PDF or TXT), split into clauses, and classify each.
    
    Hardening:
    - Maximum file size 10 MB
    - PDF magic signature check (%PDF)
    - PDF page limit (100 pages)
    """
    load_artifacts()

    # 1. Size constraint check (10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError("File size exceeds maximum limit of 10 MB.")

    # 2. Extension validation
    fn_lower = filename.lower()
    if not (fn_lower.endswith(".pdf") or fn_lower.endswith(".txt")):
        ext = Path(filename).suffix or "unknown"
        raise ValueError(f"Unsupported file format '{ext}'. Please upload a PDF (.pdf) or plain text (.txt) file.")

    # 3. PDF Signature and Text Extraction
    extracted_text = ""
    if fn_lower.endswith(".pdf"):
        if len(file_content) < 4 or not file_content.startswith(b"%PDF"):
            raise ValueError(f"Corrupted or invalid PDF file '{filename}': Missing %PDF file signature.")

        try:
            with pymupdf.open(stream=file_content, filetype="pdf") as doc:
                if len(doc) > 100:
                    raise ValueError(f"PDF document '{filename}' exceeds the maximum limit of 100 pages (found {len(doc)} pages).")
                pages = [page.get_text() for page in doc]
            extracted_text = "\n".join(strip_headers_footers(pages))
        except ValueError:
            raise
        except Exception as e:
            logger.warning(f"PyMuPDF failed on {filename}: {e}")
            raise ValueError(f"Corrupted or invalid PDF file '{filename}': Failed to read PDF streams.")
    else:
        # Plain text
        try:
            extracted_text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            extracted_text = file_content.decode("latin-1", errors="ignore")

    extracted_text = extracted_text.strip()
    if not extracted_text:
        raise ValueError(f"No readable text could be extracted from '{filename}'. Scanned image-only PDFs are not supported.")

    # 4. Clause splitting using generalized splitter
    raw_clauses = split_into_clauses(extracted_text)
    if not raw_clauses:
        raise ValueError("No clauses could be identified in the extracted text.")

    # 5. Classify each extracted clause
    clause_results = []
    for idx, c_text in enumerate(raw_clauses, start=1):
        try:
            res = classify_clause(c_text)
            clause_results.append({
                "clause_index": idx,
                "clause_text": res["clause_text"],
                "cleaned_text": res["cleaned_text"],
                "predicted_category": res["predicted_category"],
                "confidence": res["confidence"],
                "confidence_score": res["confidence_score"],
                "confidence_status": res["confidence_status"],
                "is_out_of_scope": res["is_out_of_scope"],
                "alternatives": res["alternatives"],
            })
        except ValueError:
            continue

    if not clause_results:
        raise ValueError("None of the extracted clauses contained sufficient text for classification.")

    contract_id = str(uuid.uuid4())
    register_uploaded_contract(contract_id, filename, clause_results)

    return {
        "contract_id": contract_id,
        "document_name": filename,
        "total_clauses": len(clause_results),
        "clauses": clause_results,
    }
