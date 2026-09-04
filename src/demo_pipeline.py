from pathlib import Path
import sys
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from pdf_extractor import extract_text_from_pdf
from clause_splitter import split_into_clauses
from text_cleaner import clean_text


def run_pipeline(pdf_path: Path | str = BASE_DIR / "data" / "raw_pdfs" / "sample_contract.pdf"):
    pdf_path = Path(pdf_path)
    models_dir = BASE_DIR / "models"

    print("=" * 70)
    print("CLAUSEIQ SPRINT 1: END-TO-END PIPELINE DEMONSTRATION")
    print("=" * 70)

    # 1. PDF Text Extraction
    print(f"\n[Step 1] Extracting raw text from PDF: {pdf_path.name}")
    raw_text = extract_text_from_pdf(pdf_path)
    print(f"         Total characters extracted: {len(raw_text)}")

    # 2. spaCy Clause Splitting
    print("\n[Step 2] Splitting text into clauses using spaCy (en_core_web_sm)...")
    clauses = split_into_clauses(raw_text)
    print(f"         Total clauses identified: {len(clauses)}")

    # 3. Text Cleaning
    print("\n[Step 3] Cleaning and normalizing clauses...")
    cleaned_clauses = [clean_text(c) for c in clauses]

    # Filter out empty or extremely short segments
    valid_pairs = [(orig, clean) for orig, clean in zip(clauses, cleaned_clauses) if len(clean) > 5]
    print(f"         Valid non-trivial clauses to classify: {len(valid_pairs)}")

    # 4. Load Trained Model Artifacts
    print("\n[Step 4] Loading trained vectorizer and SVM classifier...")
    vectorizer = joblib.load(models_dir / "tfidf_vectorizer.pkl")
    svm_model = joblib.load(models_dir / "svm_classifier.pkl")
    le = joblib.load(models_dir / "label_encoder.pkl")
    print(f"         Loaded TF-IDF ({len(vectorizer.get_feature_names_out())} features) and Linear SVM.")

    # 5. Feature Extraction and Inference
    print("\n[Step 5] Classifying sample contract clauses:\n" + "-" * 70)
    for idx, (orig, clean) in enumerate(valid_pairs[:8], 1):
        vec = vectorizer.transform([clean])
        pred_idx = svm_model.predict(vec)[0]
        category = le.inverse_transform([pred_idx])[0]
        preview = orig.replace("\n", " ").strip()
        if len(preview) > 90:
            preview = preview[:87] + "..."
        print(f"Clause {idx:02d} | Classified Category: [{category}]")
        print(f"          Text: \"{preview}\"\n")

    print("=" * 70)
    print("END-TO-END PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_pipeline()
