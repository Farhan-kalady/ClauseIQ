from pathlib import Path
import sys
import joblib
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import GridSearchCV, StratifiedKFold
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


def train_naive_bayes(
    models_dir: Path | str = BASE_DIR / "models",
):
    models_dir = Path(models_dir)
    split_path = models_dir / "train_test_split.pkl"
    le_path = models_dir / "label_encoder.pkl"

    if not split_path.is_file() or not le_path.is_file():
        raise FileNotFoundError(f"Required split or label encoder missing in {models_dir}.")

    print(f"Loading train/test split from {split_path}...")
    X_train, X_test, y_train, y_test = joblib.load(split_path)
    le = joblib.load(le_path)

    print(f"Training dataset shape: X_train={X_train.shape}, y_train={len(y_train)}")
    print(f"Test dataset shape:     X_test={X_test.shape}, y_test={len(y_test)}")
    print(f"Number of classes:      {len(le.classes_)}")

    # Parameter grid for alpha tuning
    # Note: MultinomialNB does not support class_weight.
    # We use macro-F1 scoring in GridSearchCV with StratifiedKFold to optimize for class balance.
    param_grid = {
        "alpha": [0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
    }
    nb = MultinomialNB()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    print("\nTuning MultinomialNB with GridSearchCV (scoring='f1_macro', cv=5)...")
    grid = GridSearchCV(nb, param_grid, scoring="f1_macro", cv=cv, n_jobs=-1, verbose=1)
    grid.fit(X_train, y_train)

    best_alpha = grid.best_params_["alpha"]
    best_cv_f1 = grid.best_score_
    print(f"\nGridSearchCV Complete!")
    print(f"Best parameter (alpha):          {best_alpha}")
    print(f"Best CV Macro F1 (5-fold):       {best_cv_f1:.4f}")

    best_nb = grid.best_estimator_

    # Evaluation on the EXACT same held-out test set
    y_pred_nb = best_nb.predict(X_test)

    acc = accuracy_score(y_test, y_pred_nb)
    macro_prec = precision_score(y_test, y_pred_nb, average="macro", zero_division=0)
    macro_rec = recall_score(y_test, y_pred_nb, average="macro", zero_division=0)
    macro_f1 = f1_score(y_test, y_pred_nb, average="macro", zero_division=0)
    weighted_prec = precision_score(y_test, y_pred_nb, average="weighted", zero_division=0)
    weighted_rec = recall_score(y_test, y_pred_nb, average="weighted", zero_division=0)
    weighted_f1 = f1_score(y_test, y_pred_nb, average="weighted", zero_division=0)

    print("\n" + "=" * 55)
    print("MULTINOMIAL NAIVE BAYES TEST RESULTS")
    print("=" * 55)
    print(f"Best Parameter alpha: {best_alpha}")
    print(f"Best CV Macro F1:     {best_cv_f1:.4f}")
    print(f"Test Accuracy:        {acc:.4f} ({acc*100:.2f}%)")
    print(f"Macro Precision:      {macro_prec:.4f}")
    print(f"Macro Recall:         {macro_rec:.4f}")
    print(f"Macro F1:             {macro_f1:.4f} ({macro_f1*100:.2f}%)")
    print(f"Weighted Precision:   {weighted_prec:.4f}")
    print(f"Weighted Recall:      {weighted_rec:.4f}")
    print(f"Weighted F1:          {weighted_f1:.4f} ({weighted_f1*100:.2f}%)")
    print("=" * 55)
    print("\nClassification Report Preview (top classes):")
    report = classification_report(y_test, y_pred_nb, target_names=le.classes_, zero_division=0)
    print(report[:800] + "\n...")

    # Save trained model
    model_save_path = models_dir / "naive_bayes.pkl"
    joblib.dump(best_nb, model_save_path)
    print(f"\nSaved trained MultinomialNB model to {model_save_path}")

    # Also save metadata/results
    results = {
        "model": best_nb,
        "best_params": grid.best_params_,
        "best_cv_macro_f1": float(best_cv_f1),
        "accuracy": float(acc),
        "macro_precision": float(macro_prec),
        "macro_recall": float(macro_rec),
        "macro_f1": float(macro_f1),
        "weighted_precision": float(weighted_prec),
        "weighted_recall": float(weighted_rec),
        "weighted_f1": float(weighted_f1),
        "classification_report": report,
    }
    results_save_path = models_dir / "naive_bayes_results.pkl"
    joblib.dump(results, results_save_path)
    print(f"Saved MultinomialNB results to {results_save_path}")

    return results


if __name__ == "__main__":
    train_naive_bayes()
