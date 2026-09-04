from pathlib import Path
import sys
import joblib
from sklearn.svm import LinearSVC
from sklearn.model_selection import GridSearchCV
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


def train_svm(
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

    print("Setting up LinearSVC with GridSearchCV (C in [0.1, 1, 10], cv=3, scoring='f1_macro')...")
    param_grid = {"C": [0.1, 1, 10]}
    svm = LinearSVC(class_weight="balanced", max_iter=5000, random_state=42)

    grid = GridSearchCV(svm, param_grid, scoring="f1_macro", cv=3, n_jobs=-1, verbose=1)
    grid.fit(X_train, y_train)

    best_c = grid.best_params_["C"]
    best_cv_f1 = grid.best_score_
    print(f"\nGridSearchCV Complete!")
    print(f"Best C parameter:                {best_c}")
    print(f"Best CV Macro F1 (3-fold):       {best_cv_f1:.4f}")

    best_svm = grid.best_estimator_

    # Single held-out test set evaluation
    y_pred_svm = best_svm.predict(X_test)

    acc = accuracy_score(y_test, y_pred_svm)
    macro_prec = precision_score(y_test, y_pred_svm, average="macro", zero_division=0)
    macro_rec = recall_score(y_test, y_pred_svm, average="macro", zero_division=0)
    macro_f1 = f1_score(y_test, y_pred_svm, average="macro", zero_division=0)
    weighted_prec = precision_score(y_test, y_pred_svm, average="weighted", zero_division=0)
    weighted_rec = recall_score(y_test, y_pred_svm, average="weighted", zero_division=0)
    weighted_f1 = f1_score(y_test, y_pred_svm, average="weighted", zero_division=0)

    print("\n" + "=" * 50)
    print("TUNED LINEAR SVM TEST RESULTS")
    print("=" * 50)
    print(f"Best Parameter C: {best_c}")
    print(f"Best CV Macro F1: {best_cv_f1:.4f}")
    print(f"Test Accuracy:    {acc:.4f}")
    print(f"Macro Precision:  {macro_prec:.4f}")
    print(f"Macro Recall:     {macro_rec:.4f}")
    print(f"Macro F1:         {macro_f1:.4f}")
    print(f"Weighted F1:      {weighted_f1:.4f}")
    print("=" * 50)
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred_svm, target_names=le.classes_, zero_division=0))

    # Save best model
    model_save_path = models_dir / "svm_classifier.pkl"
    joblib.dump(best_svm, model_save_path)
    print(f"Saved best Linear SVM model to {model_save_path}")

    return {
        "model": best_svm,
        "best_c": best_c,
        "best_cv_macro_f1": best_cv_f1,
        "accuracy": acc,
        "macro_precision": macro_prec,
        "macro_recall": macro_rec,
        "macro_f1": macro_f1,
        "weighted_precision": weighted_prec,
        "weighted_recall": weighted_rec,
        "weighted_f1": weighted_f1,
    }


if __name__ == "__main__":
    train_svm()