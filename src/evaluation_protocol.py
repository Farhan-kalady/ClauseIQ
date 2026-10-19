"""Comprehensive evaluation protocol for ClauseIQ.

Provides:
- Split A (comparable clause-level stratified 80/20)
- Split B (leakage-safe grouped split by contract_id)
- Multi-model evaluation (Logistic Regression, Linear SVM, Multinomial NB, Random Forest)
- Precision, Recall, F1 (macro and weighted), per-class report, confusion matrix, top 15 confused pairs
- Confidence calibration (ECE, reliability table, precision at High/Moderate/Low/Out-of-scope status)
- Real-document verification against test PDFs and synthetic ground truth
"""

import json
from pathlib import Path
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from text_cleaner import clean_text


def load_dataset(data_path: Path = BASE_DIR / "data" / "clauseiq_dataset_clean.csv"):
    df = pd.read_csv(data_path)
    text_col = "clean_text" if "clean_text" in df.columns else "clause_text"
    X = df[text_col].fillna("").astype(str)
    y = df["category"].astype(str)
    groups = df["contract_id"].astype(str) if "contract_id" in df.columns else None
    return df, X, y, groups


def compute_calibration_metrics(y_true, probs, n_bins=10):
    """Compute reliability diagram bins, ECE, and status-level precision."""
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    correctness = (predictions == y_true).astype(int)

    # 1. Binned Reliability Table & ECE
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bins = []
    ece = 0.0
    total_samples = len(y_true)

    for i in range(n_bins):
        bin_lower = bin_edges[i]
        bin_upper = bin_edges[i + 1]
        mask = (confidences > bin_lower) & (confidences <= bin_upper) if i > 0 else (confidences >= bin_lower) & (confidences <= bin_upper)
        bin_count = int(np.sum(mask))
        if bin_count > 0:
            bin_acc = float(np.mean(correctness[mask]))
            bin_conf = float(np.mean(confidences[mask]))
            abs_err = abs(bin_acc - bin_conf)
            ece += (bin_count / total_samples) * abs_err
        else:
            bin_acc = 0.0
            bin_conf = 0.0
            abs_err = 0.0

        bins.append({
            "bin_index": i + 1,
            "bin_lower": round(bin_lower, 2),
            "bin_upper": round(bin_upper, 2),
            "sample_count": bin_count,
            "mean_confidence": round(bin_conf, 4),
            "empirical_accuracy": round(bin_acc, 4),
            "calibration_gap": round(abs_err, 4),
        })

    # 2. Precision by Status Level (matching UI / API thresholds)
    # High: >= 0.50; Moderate: 0.25 - 0.50; Low: 0.10 - 0.25; Out of scope: < 0.10
    status_defs = [
        ("High confidence", confidences >= 0.50),
        ("Moderate confidence", (confidences >= 0.25) & (confidences < 0.50)),
        ("Low confidence", (confidences >= 0.10) & (confidences < 0.25)),
        ("Out of scope", confidences < 0.10),
    ]

    status_metrics = {}
    for name, s_mask in status_defs:
        s_count = int(np.sum(s_mask))
        if s_count > 0:
            s_acc = float(np.mean(correctness[s_mask]))
            s_mean_conf = float(np.mean(confidences[s_mask]))
        else:
            s_acc = 0.0
            s_mean_conf = 0.0
        status_metrics[name] = {
            "count": s_count,
            "percentage_of_total": round((s_count / total_samples) * 100, 2),
            "precision": round(s_acc, 4),
            "mean_confidence": round(s_mean_conf, 4),
        }

    return {
        "expected_calibration_error": round(float(ece), 4),
        "reliability_bins": bins,
        "confidence_status_precision": status_metrics,
    }


def find_top_confused_pairs(cm, class_names, top_n=15):
    """Extract top N off-diagonal confused pairs."""
    confused = []
    n_classes = len(class_names)
    for i in range(n_classes):
        for j in range(n_classes):
            if i != j and cm[i, j] > 0:
                confused.append({
                    "true_category": class_names[i],
                    "predicted_category": class_names[j],
                    "count": int(cm[i, j]),
                })
    confused.sort(key=lambda x: x["count"], reverse=True)
    return confused[:top_n]


def evaluate_split(
    X_train_text,
    X_test_text,
    y_train,
    y_test,
    le,
    split_name: str,
    results_dir: Path,
):
    results_dir = Path(results_dir)
    reports_dir = results_dir / "classification_reports"
    cm_dir = results_dir / "confusion_matrices"
    reports_dir.mkdir(parents=True, exist_ok=True)
    cm_dir.mkdir(parents=True, exist_ok=True)

    # Fit TF-IDF on training only
    vec = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
    )
    X_train = vec.fit_transform(X_train_text)
    X_test = vec.transform(X_test_text)

    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
            solver="lbfgs",
        ),
        "Linear SVM": LinearSVC(
            C=0.1,
            class_weight="balanced",
            random_state=42,
        ),
        "Multinomial Naive Bayes": MultinomialNB(
            alpha=0.01,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=50,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }

    split_results = []
    class_names = list(le.classes_)

    for name, model in models.items():
        print(f"  Training {name} on {split_name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = float(accuracy_score(y_test, y_pred))
        macro_p = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
        macro_r = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
        macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
        weighted_p = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
        weighted_r = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
        weighted_f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

        cm = confusion_matrix(y_test, y_pred)
        top_confused = find_top_confused_pairs(cm, class_names, top_n=15)

        # Classification report dict
        cr_dict = classification_report(y_test, y_pred, target_names=class_names, zero_division=0, output_dict=True)
        slug = name.lower().replace(" ", "_")
        split_slug = split_name.lower().replace(" ", "_")

        with open(reports_dir / f"{slug}_{split_slug}.json", "w", encoding="utf-8") as f:
            json.dump(cr_dict, f, indent=2)

        np.save(cm_dir / f"{slug}_{split_slug}_cm.npy", cm)

        model_res = {
            "model": name,
            "split": split_name,
            "accuracy": round(acc, 4),
            "macro_precision": round(macro_p, 4),
            "macro_recall": round(macro_r, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_precision": round(weighted_p, 4),
            "weighted_recall": round(weighted_r, 4),
            "weighted_f1": round(weighted_f1, 4),
            "top_15_confused_pairs": top_confused,
        }

        # Calibration for served model (Logistic Regression)
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X_test)
            cal_metrics = compute_calibration_metrics(y_test, probs)
            model_res["calibration"] = cal_metrics

        split_results.append(model_res)

    return split_results


def run_real_document_check():
    """Classify test PDFs using live API service logic and compare with reference results."""
    from api.services.ml_service import classify_document

    sample_pdf = BASE_DIR / "data" / "raw_pdfs" / "sample_contract.pdf"
    test_pdf = BASE_DIR / "test_data" / "ClauseIQ_Synthetic_Company_Service_Agreement_Test.pdf"
    ref_json = BASE_DIR / "docs" / "synthetic_pdf_classification_results.json"

    results = {}

    if test_pdf.is_file():
        with open(test_pdf, "rb") as f:
            pdf_bytes = f.read()
        res_test = classify_document(pdf_bytes, test_pdf.name)

        # Compare with reference expected labels
        agreement_count = 0
        total_compared = 0
        discrepancies = []

        if ref_json.is_file():
            with open(ref_json, "r", encoding="utf-8") as rf:
                ref_data = json.load(rf)
            ref_clauses = {c["clause_index"]: c["predicted_category"] for c in ref_data.get("clauses", [])}

            for c in res_test.get("clauses", []):
                idx = c["clause_index"]
                if idx in ref_clauses:
                    total_compared += 1
                    if c["predicted_category"] == ref_clauses[idx]:
                        agreement_count += 1
                    else:
                        discrepancies.append({
                            "clause_index": idx,
                            "actual_pred": c["predicted_category"],
                            "reference_pred": ref_clauses[idx],
                            "confidence": c["confidence"],
                        })

        agreement_rate = (agreement_count / total_compared) if total_compared > 0 else 0.0
        results["synthetic_test_contract"] = {
            "document_name": test_pdf.name,
            "total_clauses_extracted": res_test["total_clauses"],
            "compared_against_reference": total_compared,
            "agreement_count": agreement_count,
            "agreement_rate": round(agreement_rate, 4),
            "discrepancies_count": len(discrepancies),
            "first_5_predictions": [
                {
                    "idx": c["clause_index"],
                    "category": c["predicted_category"],
                    "confidence": c["confidence"],
                    "status": c["confidence_status"],
                }
                for c in res_test["clauses"][:5]
            ],
            "evaluation_note": "Synthetic contract check evaluates pipeline extraction & segmentation on a small 69-clause contract.",
        }

    if sample_pdf.is_file():
        with open(sample_pdf, "rb") as f:
            pdf_bytes = f.read()
        res_sample = classify_document(pdf_bytes, sample_pdf.name)
        results["sample_contract"] = {
            "document_name": sample_pdf.name,
            "total_clauses_extracted": res_sample["total_clauses"],
            "first_5_predictions": [
                {
                    "idx": c["clause_index"],
                    "category": c["predicted_category"],
                    "confidence": c["confidence"],
                    "status": c["confidence_status"],
                }
                for c in res_sample["clauses"][:5]
            ],
            "status_distribution": {
                "high": sum(1 for c in res_sample["clauses"] if c["confidence_status"] == "High confidence"),
                "moderate": sum(1 for c in res_sample["clauses"] if c["confidence_status"] == "Moderate confidence"),
                "low": sum(1 for c in res_sample["clauses"] if "Low" in c["confidence_status"]),
                "out_of_scope": sum(1 for c in res_sample["clauses"] if "Out of" in c["confidence_status"]),
            },
        }

    return results


def run_full_baseline_evaluation(
    data_path: Path = BASE_DIR / "data" / "clauseiq_dataset_clean.csv",
    results_dir: Path = BASE_DIR / "results",
):
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    print("Loading dataset for baseline evaluation...")
    df, X, y, groups = load_dataset(data_path)

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # 1. Split A: Stratified 80/20 at clause level (random_state=42)
    print("\n--- Running Evaluation on Split A (Comparable Stratified 80/20) ---")
    X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(
        X,
        y_encoded,
        test_size=0.20,
        random_state=42,
        stratify=y_encoded,
    )
    split_a_results = evaluate_split(
        X_train_a, X_test_a, y_train_a, y_test_a, le, "Split A (Stratified)", results_dir
    )

    # 2. Split B: Grouped 80/20 by contract_id (random_state=42)
    print("\n--- Running Evaluation on Split B (Leakage-Safe Grouped by Contract ID) ---")
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx_b, test_idx_b = next(gss.split(X, y_encoded, groups=groups))
    X_train_b = X.iloc[train_idx_b]
    X_test_b = X.iloc[test_idx_b]
    y_train_b = y_encoded[train_idx_b]
    y_test_b = y_encoded[test_idx_b]

    print(f"Split B counts: Train clauses={len(train_idx_b)}, Test clauses={len(test_idx_b)}")
    print(f"Train contracts={groups.iloc[train_idx_b].nunique()}, Test contracts={groups.iloc[test_idx_b].nunique()}")

    split_b_results = evaluate_split(
        X_train_b, X_test_b, y_train_b, y_test_b, le, "Split B (Grouped)", results_dir
    )

    # 3. Real Document Check
    print("\n--- Running Real-Document Pipeline Check ---")
    doc_check_results = run_real_document_check()
    with open(results_dir / "baseline_real_document_check.json", "w", encoding="utf-8") as f:
        json.dump(doc_check_results, f, indent=2)

    # 4. Consolidate and Save Results
    all_comparison = split_a_results + split_b_results
    with open(results_dir / "baseline_model_comparison.json", "w", encoding="utf-8") as f:
        json.dump(all_comparison, f, indent=2)

    # Create summary CSV table
    csv_rows = []
    for r in all_comparison:
        row = {
            "Model": r["model"],
            "Split": r["split"],
            "Accuracy": r["accuracy"],
            "Macro F1": r["macro_f1"],
            "Weighted F1": r["weighted_f1"],
            "Macro Precision": r["macro_precision"],
            "Macro Recall": r["macro_recall"],
            "ECE": r.get("calibration", {}).get("expected_calibration_error"),
            "High Conf Precision": r.get("calibration", {}).get("confidence_status_precision", {}).get("High confidence", {}).get("precision"),
            "Mod Conf Precision": r.get("calibration", {}).get("confidence_status_precision", {}).get("Moderate confidence", {}).get("precision"),
            "Low Conf Precision": r.get("calibration", {}).get("confidence_status_precision", {}).get("Low confidence", {}).get("precision"),
        }
        csv_rows.append(row)

    df_comp = pd.DataFrame(csv_rows)
    df_comp.to_csv(results_dir / "baseline_model_comparison.csv", index=False)
    print("\n=== BASELINE EVALUATION SUMMARY TABLE ===")
    print(df_comp.to_string(index=False))

    return all_comparison, doc_check_results


if __name__ == "__main__":
    run_full_baseline_evaluation()
