from pathlib import Path
import sys
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def evaluate_all_models(
    models_dir: Path | str = BASE_DIR / "models",
    results_dir: Path | str = BASE_DIR / "results",
):
    models_dir = Path(models_dir)
    results_dir = Path(results_dir)
    reports_dir = results_dir / "classification_reports"
    cm_dir = results_dir / "confusion_matrices"

    results_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    cm_dir.mkdir(parents=True, exist_ok=True)

    split_path = models_dir / "train_test_split.pkl"
    le_path = models_dir / "label_encoder.pkl"

    if not split_path.is_file() or not le_path.is_file():
        raise FileNotFoundError("Missing train_test_split.pkl or label_encoder.pkl")

    _, X_test, _, y_test = joblib.load(split_path)
    le = joblib.load(le_path)
    classes = list(le.classes_)

    model_files = {
        "Logistic Regression": models_dir / "logistic_regression.pkl",
        "Linear SVM": models_dir / "svm_classifier.pkl",
        "Multinomial Naive Bayes": models_dir / "naive_bayes.pkl",
        "Random Forest": models_dir / "random_forest.pkl",
    }

    comparison_records = []
    predictions = {}

    print("=" * 70)
    print("EVALUATING ALL 4 MODELS ON THE EXACT SAME HELD-OUT TEST SET (N=2441)")
    print("=" * 70)

    for name, file_path in model_files.items():
        if not file_path.is_file():
            raise FileNotFoundError(f"Missing model artifact: {file_path}")

        print(f"\nEvaluating: {name} (loading from {file_path.name})...")
        model = joblib.load(file_path)
        y_pred = model.predict(X_test)
        predictions[name] = y_pred

        acc = accuracy_score(y_test, y_pred)
        m_prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
        m_rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
        m_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
        w_prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        w_rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        w_f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        record = {
            "Model": name,
            "Accuracy": round(float(acc), 4),
            "Macro Precision": round(float(m_prec), 4),
            "Macro Recall": round(float(m_rec), 4),
            "Macro F1": round(float(m_f1), 4),
            "Weighted Precision": round(float(w_prec), 4),
            "Weighted Recall": round(float(w_rec), 4),
            "Weighted F1": round(float(w_f1), 4),
        }
        comparison_records.append(record)

        # 1. Save Per-Class Classification Report
        clf_dict = classification_report(y_test, y_pred, target_names=classes, output_dict=True, zero_division=0)
        clf_df = pd.DataFrame(clf_dict).transpose()
        safe_name = name.lower().replace(" ", "_")
        clf_df.to_csv(reports_dir / f"{safe_name}_report.csv")

        with open(reports_dir / f"{safe_name}_report.txt", "w", encoding="utf-8") as f:
            f.write(f"Classification Report - {name}\n")
            f.write("=" * 60 + "\n")
            f.write(classification_report(y_test, y_pred, target_names=classes, zero_division=0))

        # 2. Confusion Matrix (300 DPI)
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(16, 14), dpi=300)
        sns.heatmap(
            cm,
            annot=False,
            cmap="Blues",
            xticklabels=classes,
            yticklabels=classes,
            cbar=True,
        )
        plt.title(f"Confusion Matrix: {name} (Held-out Test Set, N=2441)", fontsize=14, fontweight="bold", pad=15)
        plt.xlabel("Predicted Label", fontsize=12, labelpad=10)
        plt.ylabel("True Label", fontsize=12, labelpad=10)
        plt.xticks(rotation=90, fontsize=8)
        plt.yticks(rotation=0, fontsize=8)
        plt.tight_layout()
        cm_path = cm_dir / f"{safe_name}_cm.png"
        plt.savefig(cm_path, dpi=300)
        plt.close()
        print(f"  -> Saved confusion matrix plot to {cm_path.name}")

    # Build Comparison DataFrame
    comp_df = pd.DataFrame(comparison_records)
    print("\n" + "=" * 80)
    print("FINAL MODEL COMPARISON TABLE")
    print("=" * 80)
    print(comp_df.to_string(index=False))
    print("=" * 80)

    # Save comparison table as CSV and JSON
    csv_path = results_dir / "model_comparison.csv"
    json_path = results_dir / "model_comparison.json"
    comp_df.to_csv(csv_path, index=False)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(comparison_records, f, indent=4)
    print(f"\nSaved comparison records to:\n  - {csv_path}\n  - {json_path}")

    # 3. Overall Comparison Bar Chart (300 DPI)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)

    metrics_to_plot = ["Accuracy", "Macro F1", "Weighted F1"]
    x = np.arange(len(comp_df))
    width = 0.25

    colors = ["#2b5c8f", "#d95f02", "#7570b3"]
    for i, metric in enumerate(metrics_to_plot):
        bars = ax.bar(
            x + (i - 1) * width,
            comp_df[metric],
            width,
            label=metric,
            color=colors[i],
            alpha=0.9,
            edgecolor="black",
            linewidth=0.8,
        )
        for bar in bars:
            yval = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                yval + 0.008,
                f"{yval:.3f}",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

    ax.set_ylabel("Score", fontsize=12, fontweight="bold")
    ax.set_title("ClauseIQ: Comprehensive Model Performance Comparison (CUAD Test Split, N=2441)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(comp_df["Model"], fontsize=11, fontweight="bold")
    ax.set_ylim(0.45, 0.82)
    ax.legend(loc="lower right", frameon=True, fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    plt.tight_layout()
    chart_path = results_dir / "model_comparison.png"
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Saved comparison bar chart to {chart_path}")

    return comp_df


if __name__ == "__main__":
    evaluate_all_models()
