from pathlib import Path
import sys
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def train_baseline(
    models_dir: Path | str = BASE_DIR / "models",
):
    models_dir = Path(models_dir)
    split_path = models_dir / "train_test_split.pkl"
    le_path = models_dir / "label_encoder.pkl"

    if not split_path.is_file() or not le_path.is_file():
        from feature_extraction import extract_features

        print("Saved splits/encoder not found. Running feature extraction...")
        extract_features()

    print(f"Loading train/test split from {split_path}...")
    X_train, X_test, y_train, y_test = joblib.load(split_path)
    le = joblib.load(le_path)

    print(f"Training Logistic Regression baseline (max_iter=2000, class_weight='balanced', random_state=42)...")
    clf = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )
    clf.fit(X_train, y_train)

    # Predictions
    y_pred = clf.predict(X_test)

    # Metrics calculation
    acc = accuracy_score(y_test, y_pred)
    macro_prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
    macro_rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
    macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
    weighted_prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    weighted_rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    weighted_f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    print("\n" + "=" * 50)
    print("LOGISTIC REGRESSION BASELINE RESULTS")
    print("=" * 50)
    print(f"Accuracy:         {acc:.4f}")
    print(f"Macro Precision:  {macro_prec:.4f}")
    print(f"Macro Recall:     {macro_rec:.4f}")
    print(f"Macro F1:         {macro_f1:.4f}")
    print(f"Weighted F1:      {weighted_f1:.4f}")
    print("=" * 50)
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0))

    # Save model
    model_save_path = models_dir / "logistic_regression.pkl"
    joblib.dump(clf, model_save_path)
    print(f"Saved Logistic Regression model to {model_save_path}")

    return {
        "model": clf,
        "accuracy": acc,
        "macro_precision": macro_prec,
        "macro_recall": macro_rec,
        "macro_f1": macro_f1,
        "weighted_precision": weighted_prec,
        "weighted_recall": weighted_rec,
        "weighted_f1": weighted_f1,
    }


if __name__ == "__main__":
    train_baseline()