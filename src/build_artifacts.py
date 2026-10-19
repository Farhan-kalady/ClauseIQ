"""Script to build, package, and verify runtime model artifacts for ClauseIQ.

Reproducibly generates:
- artifacts/best_model.joblib
- artifacts/tfidf_vectorizer.joblib
- artifacts/label_encoder.joblib
- artifacts/manifest.json
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from text_cleaner import clean_text

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


def get_hybrid_vectorizer(word_max=25000, char_max=15000):
    return FeatureUnion([
        (
            "word",
            TfidfVectorizer(
                max_features=word_max,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                sublinear_tf=True,
            ),
        ),
        (
            "char",
            TfidfVectorizer(
                max_features=char_max,
                analyzer="char_wb",
                ngram_range=(3, 5),
                min_df=3,
                sublinear_tf=True,
            ),
        ),
    ])


def build_artifacts(
    data_path: Path | str = BASE_DIR / "data" / "clauseiq_dataset_clean.csv",
    artifacts_dir: Path | str = BASE_DIR / "artifacts",
    use_hybrid_features: bool = True,
    model_override=None,
    model_name: str = "LogisticRegression-HybridWordChar",
):
    data_path = Path(data_path)
    artifacts_dir = Path(artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.is_file():
        raw_csv = BASE_DIR / "data" / "clauseiq_dataset.csv"
        if not raw_csv.is_file():
            raise FileNotFoundError(f"Neither {data_path} nor {raw_csv} exists.")
        from clean_dataset import clean_dataset
        clean_dataset(input_path=raw_csv, output_path=data_path)

    df = pd.read_csv(data_path)
    text_source = df["clause_text"].fillna("").astype(str)
    print("Preprocessing texts with clean_text_pipeline (regex + NLTK lemmatization)...")
    df["processed_text"] = text_source.apply(clean_text_pipeline)

    X_raw = df["processed_text"]
    y_raw = df["category"].astype(str)

    # 1. Label Encoder
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_raw)
    joblib.dump(le, artifacts_dir / "label_encoder.joblib")

    # 2. Stratified 80/20 Split (Split A standard)
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_raw,
        y_encoded,
        test_size=0.20,
        random_state=42,
        stratify=y_encoded,
    )

    # 3. Vectorizer (Hybrid FeatureUnion or single Word TF-IDF)
    if use_hybrid_features:
        vectorizer = get_hybrid_vectorizer(25000, 15000)
    else:
        vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
        )

    print("Fitting vectorizer strictly on training data...")
    X_train = vectorizer.fit_transform(X_train_text)
    X_test = vectorizer.transform(X_test_text)
    joblib.dump(vectorizer, artifacts_dir / "tfidf_vectorizer.joblib")

    # 4. Model fitting
    if model_override is None:
        clf = LogisticRegression(
            C=1.0,
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
            solver="lbfgs",
        )
        model_params = {
            "C": 1.0,
            "max_iter": 2000,
            "class_weight": "balanced",
            "random_state": 42,
            "solver": "lbfgs",
        }
    else:
        clf = model_override
        model_params = getattr(clf, "get_params", lambda: {})()

    print("Fitting model on training features...")
    clf.fit(X_train, y_train)
    joblib.dump(clf, artifacts_dir / "best_model.joblib")

    print("Fitting reproducible calibrated model on training features...")
    from sklearn.calibration import CalibratedClassifierCV
    calibrated_clf = CalibratedClassifierCV(
        estimator=LogisticRegression(C=1.0, max_iter=2000, class_weight="balanced", random_state=42),
        method="sigmoid",
        cv=3,
    )
    calibrated_clf.fit(X_train, y_train)
    joblib.dump(calibrated_clf, artifacts_dir / "calibrated_model.joblib")

    # 5. Evaluate on held-out test split
    y_pred = clf.predict(X_test)
    probs = clf.predict_proba(X_test) if hasattr(clf, "predict_proba") else None

    eval_metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "macro_precision": round(float(precision_score(y_test, y_pred, average="macro", zero_division=0)), 4),
        "macro_recall": round(float(recall_score(y_test, y_pred, average="macro", zero_division=0)), 4),
        "macro_f1": round(float(f1_score(y_test, y_pred, average="macro", zero_division=0)), 4),
        "weighted_precision": round(float(precision_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "weighted_recall": round(float(recall_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "weighted_f1": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
    }

    # 6. Generate Manifest
    manifest = {
        "manifest_version": "2.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_name": model_name,
        "model_class": clf.__class__.__name__,
        "model_parameters": model_params,
        "preprocessing": {
            "pipeline": "clean_text_pipeline",
            "lemmatizer": "NLTK WordNetLemmatizer",
            "regex_normalization": True,
        },
        "feature_pipeline": {
            "type": "FeatureUnion" if use_hybrid_features else "TfidfVectorizer",
            "word_features": 25000 if use_hybrid_features else 10000,
            "word_ngram_range": [1, 2],
            "char_features": 15000 if use_hybrid_features else 0,
            "char_analyzer": "char_wb" if use_hybrid_features else None,
            "char_ngram_range": [3, 5] if use_hybrid_features else None,
            "sublinear_tf": True,
        },
        "dataset": {
            "source": "CUAD v1 derived",
            "total_samples": len(df),
            "contracts_count": int(df["contract_id"].nunique()) if "contract_id" in df.columns else None,
            "num_classes": len(le.classes_),
            "train_samples": int(X_train.shape[0]),
            "test_samples": int(X_test.shape[0]),
            "split_method": "stratified_80_20",
            "split_random_state": 42,
        },
        "metrics_held_out_test_split_a": eval_metrics,
        "environment": {
            "python_version": sys.version.split()[0],
            "scikit_learn_version": sklearn.__version__,
            "joblib_version": joblib.__version__,
            "numpy_version": np.__version__,
            "pandas_version": pd.__version__,
        },
    }

    with open(artifacts_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("Successfully built artifacts:")
    print(f"  Model:            {artifacts_dir / 'best_model.joblib'}")
    print(f"  Vectorizer:       {artifacts_dir / 'tfidf_vectorizer.joblib'}")
    print(f"  Label Encoder:    {artifacts_dir / 'label_encoder.joblib'}")
    print(f"  Manifest:         {artifacts_dir / 'manifest.json'}")
    print(f"Test Metrics: {eval_metrics}")
    return manifest


if __name__ == "__main__":
    build_artifacts()
