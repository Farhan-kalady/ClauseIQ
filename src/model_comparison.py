from pathlib import Path
import sys
import joblib
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def compare_models(models_dir: Path | str = BASE_DIR / "models"):
    models_dir = Path(models_dir)
    split_path = models_dir / "train_test_split.pkl"
    lr_path = models_dir / "logistic_regression.pkl"
    svm_path = models_dir / "svm_classifier.pkl"
    le_path = models_dir / "label_encoder.pkl"

    if not all(p.is_file() for p in [split_path, lr_path, svm_path, le_path]):
        raise FileNotFoundError("One or more model/data files are missing in models/. Please run training scripts first.")

    _, X_test, _, y_test = joblib.load(split_path)
    lr_model = joblib.load(lr_path)
    svm_model = joblib.load(svm_path)

    # Evaluate Logistic Regression
    y_pred_lr = lr_model.predict(X_test)
    lr_acc = accuracy_score(y_test, y_pred_lr)
    lr_macro_prec = precision_score(y_test, y_pred_lr, average="macro", zero_division=0)
    lr_macro_rec = recall_score(y_test, y_pred_lr, average="macro", zero_division=0)
    lr_macro_f1 = f1_score(y_test, y_pred_lr, average="macro", zero_division=0)
    lr_weighted_f1 = f1_score(y_test, y_pred_lr, average="weighted", zero_division=0)

    # Evaluate Tuned Linear SVM
    y_pred_svm = svm_model.predict(X_test)
    svm_acc = accuracy_score(y_test, y_pred_svm)
    svm_macro_prec = precision_score(y_test, y_pred_svm, average="macro", zero_division=0)
    svm_macro_rec = recall_score(y_test, y_pred_svm, average="macro", zero_division=0)
    svm_macro_f1 = f1_score(y_test, y_pred_svm, average="macro", zero_division=0)
    svm_weighted_f1 = f1_score(y_test, y_pred_svm, average="weighted", zero_division=0)

    print("=" * 60)
    print("MODEL COMPARISON: LOGISTIC REGRESSION vs TUNED LINEAR SVM")
    print("=" * 60)
    print("\nLogistic Regression Baseline:")
    print(f"  Accuracy:         {lr_acc:.4f} ({lr_acc*100:.2f}%)")
    print(f"  Macro Precision:  {lr_macro_prec:.4f}")
    print(f"  Macro Recall:     {lr_macro_rec:.4f}")
    print(f"  Macro F1:         {lr_macro_f1:.4f} ({lr_macro_f1*100:.2f}%)")
    print(f"  Weighted F1:      {lr_weighted_f1:.4f} ({lr_weighted_f1*100:.2f}%)")

    print("\nTuned Linear SVM (C=0.1):")
    print(f"  Accuracy:         {svm_acc:.4f} ({svm_acc*100:.2f}%)")
    print(f"  Macro Precision:  {svm_macro_prec:.4f}")
    print(f"  Macro Recall:     {svm_macro_rec:.4f}")
    print(f"  Macro F1:         {svm_macro_f1:.4f} ({svm_macro_f1*100:.2f}%)")
    print(f"  Weighted F1:      {svm_weighted_f1:.4f} ({svm_weighted_f1*100:.2f}%)")

    print("\n" + "-" * 60)
    print("METRIC DELTA (SVM - LR):")
    print(f"  Accuracy Delta:     {svm_acc - lr_acc:+.4f} (SVM {'higher' if svm_acc > lr_acc else 'lower'})")
    print(f"  Macro F1 Delta:     {svm_macro_f1 - lr_macro_f1:+.4f} (LR {'higher' if lr_macro_f1 > svm_macro_f1 else 'lower'})")
    print(f"  Weighted F1 Delta:  {svm_weighted_f1 - lr_weighted_f1:+.4f} (SVM {'higher' if svm_weighted_f1 > lr_weighted_f1 else 'lower'})")
    print("=" * 60)


if __name__ == "__main__":
    compare_models()
