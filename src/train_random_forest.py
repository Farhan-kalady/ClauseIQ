from pathlib import Path
import sys
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
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


def train_random_forest(
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

    # Parameter distribution for RandomizedSearchCV
    # Pragmatic search space designed to prevent excessive training time while tuning key hyperparameters
    param_dist = {
        "n_estimators": [100, 150, 200],
        "max_depth": [30, 50, None],
        "min_samples_split": [2, 5, 10],
        "class_weight": ["balanced", "balanced_subsample"],
    }

    rf = RandomForestClassifier(random_state=42)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    print("\nTuning RandomForestClassifier with RandomizedSearchCV (8 iterations, 3-fold CV, scoring='f1_macro', n_jobs=-1)...")
    search = RandomizedSearchCV(
        estimator=rf,
        param_distributions=param_dist,
        n_iter=8,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        random_state=42,
        verbose=1,
    )

    search.fit(X_train, y_train)

    best_params = search.best_params_
    best_cv_f1 = search.best_score_
    print(f"\nRandomizedSearchCV Complete!")
    print(f"Best parameters:                 {best_params}")
    print(f"Best CV Macro F1 (3-fold):       {best_cv_f1:.4f}")

    best_rf = search.best_estimator_

    # Single held-out test set evaluation
    y_pred_rf = best_rf.predict(X_test)

    acc = accuracy_score(y_test, y_pred_rf)
    macro_prec = precision_score(y_test, y_pred_rf, average="macro", zero_division=0)
    macro_rec = recall_score(y_test, y_pred_rf, average="macro", zero_division=0)
    macro_f1 = f1_score(y_test, y_pred_rf, average="macro", zero_division=0)
    weighted_prec = precision_score(y_test, y_pred_rf, average="weighted", zero_division=0)
    weighted_rec = recall_score(y_test, y_pred_rf, average="weighted", zero_division=0)
    weighted_f1 = f1_score(y_test, y_pred_rf, average="weighted", zero_division=0)

    print("\n" + "=" * 55)
    print("RANDOM FOREST TEST RESULTS")
    print("=" * 55)
    print(f"Best Parameters:    {best_params}")
    print(f"Best CV Macro F1:   {best_cv_f1:.4f}")
    print(f"Test Accuracy:      {acc:.4f} ({acc*100:.2f}%)")
    print(f"Macro Precision:    {macro_prec:.4f}")
    print(f"Macro Recall:       {macro_rec:.4f}")
    print(f"Macro F1:           {macro_f1:.4f} ({macro_f1*100:.2f}%)")
    print(f"Weighted Precision: {weighted_prec:.4f}")
    print(f"Weighted Recall:    {weighted_rec:.4f}")
    print(f"Weighted F1:        {weighted_f1:.4f} ({weighted_f1*100:.2f}%)")
    print("=" * 55)
    print("\nClassification Report Preview (top classes):")
    report = classification_report(y_test, y_pred_rf, target_names=le.classes_, zero_division=0)
    print(report[:800] + "\n...")

    # Save trained model
    model_save_path = models_dir / "random_forest.pkl"
    joblib.dump(best_rf, model_save_path)
    print(f"\nSaved trained Random Forest model to {model_save_path}")

    # Also save metadata/results
    results = {
        "model": best_rf,
        "best_params": best_params,
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
    results_save_path = models_dir / "random_forest_results.pkl"
    joblib.dump(results, results_save_path)
    print(f"Saved Random Forest results to {results_save_path}")

    return results


if __name__ == "__main__":
    train_random_forest()
