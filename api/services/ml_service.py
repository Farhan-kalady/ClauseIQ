from pathlib import Path
import sys
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pymupdf

from api.config import settings

# Ensure src/ is in sys.path
src_path = str(settings.SRC_DIR)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from text_cleaner import clean_text
from clause_splitter import split_into_clauses

# Global artifacts holders (loaded once at startup)
_model = None
_vectorizer = None
_label_encoder = None


def load_artifacts():
    """Load machine learning model, vectorizer, and label encoder once at startup."""
    global _model, _vectorizer, _label_encoder
    if _model is not None and _vectorizer is not None and _label_encoder is not None:
        return

    art_dir = settings.ARTIFACTS_DIR
    if not (art_dir / "best_model.joblib").is_file():
        art_dir = settings.MODELS_DIR

    model_path = art_dir / "best_model.joblib" if (art_dir / "best_model.joblib").is_file() else art_dir / "logistic_regression.pkl"
    vec_path = art_dir / "tfidf_vectorizer.joblib" if (art_dir / "tfidf_vectorizer.joblib").is_file() else art_dir / "tfidf_vectorizer.pkl"
    le_path = art_dir / "label_encoder.joblib" if (art_dir / "label_encoder.joblib").is_file() else art_dir / "label_encoder.pkl"

    _model = joblib.load(model_path)
    _vectorizer = joblib.load(vec_path)
    _label_encoder = joblib.load(le_path)


def is_model_loaded() -> bool:
    return _model is not None


def get_categories_list() -> List[str]:
    load_artifacts()
    return list(_label_encoder.classes_)


def classify_clause(clause_text: str) -> Dict[str, Any]:
    """Classify a single contract clause text using the loaded Sprint 2 ML model.
    
    Extracts true class probability via predict_proba() and retrieves top-3 alternative classes.
    """
    load_artifacts()

    raw_text = clause_text.strip()
    if not raw_text:
        raise ValueError("Clause text cannot be empty or solely whitespace.")

    cleaned = clean_text(raw_text)
    if not cleaned:
        raise ValueError("Clause text contains no valid alphanumeric or legal tokens.")

    # TF-IDF Feature Extraction
    vec = _vectorizer.transform([cleaned])

    # Model inference (Sprint 2 Logistic Regression)
    alternatives = []
    if hasattr(_model, "predict_proba"):
        probs = _model.predict_proba(vec)[0]
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

    return {
        "clause_text": raw_text,
        "cleaned_text": cleaned,
        "predicted_category": predicted_label,
        "confidence": conf_rounded,
        "confidence_score": conf_rounded,
        "confidence_type": conf_type,
        "model_name": type(_model).__name__,
        "alternatives": alternatives,
    }


def classify_document(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Process an uploaded contract document (PDF or TXT), split into clauses, and classify each."""
    load_artifacts()

    # 1. Text extraction
    extracted_text = ""
    if filename.lower().endswith(".pdf"):
        with pymupdf.open(stream=file_content, filetype="pdf") as doc:
            for page in doc:
                extracted_text += page.get_text() + "\n"
    else:
        # Plain text
        try:
            extracted_text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            extracted_text = file_content.decode("latin-1", errors="ignore")

    extracted_text = extracted_text.strip()
    if not extracted_text:
        raise ValueError(f"No readable text could be extracted from '{filename}'.")

    # 2. Clause splitting using existing splitter
    raw_clauses = split_into_clauses(extracted_text)
    if not raw_clauses:
        raise ValueError("No clauses could be identified in the extracted text.")

    # 3. Classify each extracted clause
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
                "alternatives": res["alternatives"],
            })
        except ValueError:
            # Skip very short fragments that cannot be cleaned
            continue

    if not clause_results:
        raise ValueError("None of the extracted clauses contained sufficient text for classification.")

    return {
        "document_name": filename,
        "total_clauses": len(clause_results),
        "clauses": clause_results,
    }
