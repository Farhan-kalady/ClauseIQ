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
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from text_cleaner import clean_text


def build_artifacts(
    data_path: Path | str = BASE_DIR / "data" / "clauseiq_dataset_clean.csv",
    artifacts_dir: Path | str = BASE_DIR / "artifacts",
    model_override=None,
    model_name: str = "LogisticRegression",
    model_params: dict = None,
    calibrated_model=None,
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
    text_col = "clean_text" if "clean_text" in df.columns else "clause_text"
    target_col = "category"

    X_raw = df[text_col].fillna("").astype(str)
    y_raw = df[target_col].astype(str)

    # 1. Label Encoder
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_raw)
    joblib.dump(le, artifacts_dir / "label_encoder.joblib")

    # 2. Stratified 80/20 Split (Split A baseline standard)
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_raw,
        y_encoded,
        test_size=0.20,
        random_state=42,
        stratify=y_encoded,
    )

    # 3. TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
    )
    X_train = vectorizer.fit_transform(X_train_text)
    X_test = vectorizer.transform(X_test_text)
    joblib.dump(vectorizer, artifacts_dir / "tfidf_vectorizer.joblib")

    # 4. Model fitting
    if model_override is None:
        clf = LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
            solver="lbfgs",
        )
        model_name = "LogisticRegression"
        model_params = {
            "max_iter": 2000,
            "class_weight": "balanced",
            "random_state": 42,
            "solver": "lbfgs",
        }
    else:
        clf = model_override

    clf.fit(X_train, y_train)
    joblib.dump(clf, artifacts_dir / "best_model.joblib")

    if calibrated_model is not None:
        joblib.dump(calibrated_model, artifacts_dir / "calibrated_model.joblib")

    # 5. Evaluate on held-out test split
    y_pred = clf.predict(X_test)
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
        "manifest_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_name": model_name,
        "model_class": clf.__class__.__name__,
        "model_parameters": model_params if model_params else {},
        "calibrated_model_present": (artifacts_dir / "calibrated_model.joblib").is_file(),
        "vectorizer": {
            "type": "TfidfVectorizer",
            "max_features": 10000,
            "ngram_range": [1, 2],
            "min_df": 2,
            "max_df": 0.95,
            "sublinear_tf": True,
            "vocabulary_size": len(vectorizer.vocabulary_),
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
    print(f"Baseline Test Metrics (Split A): {eval_metrics}")
    return manifest


if __name__ == "__main__":
    build_artifacts()
