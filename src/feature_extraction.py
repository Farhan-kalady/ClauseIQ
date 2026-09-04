from pathlib import Path
import sys
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from clean_dataset import clean_dataset


def extract_features(
    data_path: Path | str = BASE_DIR / "data" / "clauseiq_dataset_clean.csv",
    models_dir: Path | str = BASE_DIR / "models",
):
    data_path = Path(data_path)
    models_dir = Path(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load cleaned dataset (or generate if clean file is missing)
    if not data_path.is_file():
        print(f"Cleaned dataset not found at {data_path}. Running clean_dataset()...")
        clean_dataset(output_path=data_path)

    df = pd.read_csv(data_path)
    print(f"Loaded dataset shape: {df.shape}")

    # Determine text and target columns
    text_col = "clean_text" if "clean_text" in df.columns else "clause_text"
    target_col = "category" if "category" in df.columns else df.columns[-1]

    X_raw = df[text_col].fillna("").astype(str)
    y_raw = df[target_col].astype(str)

    # 2. Label Encoding (fit on entire known category list or train split)
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_raw)
    joblib.dump(le, models_dir / "label_encoder.pkl")
    print(f"Label encoder saved with {len(le.classes_)} classes.")

    # 3. Train/Test Split BEFORE TF-IDF fitting to prevent data leakage
    # Stratified 80/20 split with random_state=42
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_raw,
        y_encoded,
        test_size=0.20,
        random_state=42,
        stratify=y_encoded,
    )
    print(f"Train text count: {len(X_train_text)}, Test text count: {len(X_test_text)}")

    # 4. TF-IDF Feature Extraction
    # Fit ONLY on training data, then transform both train and test
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
    )

    print("Fitting TF-IDF vectorizer strictly on training data...")
    X_train = vectorizer.fit_transform(X_train_text)
    print(f"X_train TF-IDF shape: {X_train.shape}")

    print("Transforming test data using fitted vectorizer...")
    X_test = vectorizer.transform(X_test_text)
    print(f"X_test TF-IDF shape: {X_test.shape}")

    # 5. Save artifacts
    joblib.dump(vectorizer, models_dir / "tfidf_vectorizer.pkl")
    print(f"Saved TF-IDF vectorizer to {models_dir / 'tfidf_vectorizer.pkl'}")

    joblib.dump((X_train, X_test, y_train, y_test), models_dir / "train_test_split.pkl")
    print(f"Saved train/test split to {models_dir / 'train_test_split.pkl'}")

    return X_train, X_test, y_train, y_test, vectorizer, le


if __name__ == "__main__":
    extract_features()