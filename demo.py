"""ClauseIQ Sprint 2: End-to-End System Demonstration.

Demonstrates:
1. Loading saved model artifacts (artifacts/best_model.joblib & tfidf_vectorizer.joblib)
2. Live classification of 4 distinct contract clauses with confidence scores
3. Intelligent TF-IDF + Cosine Similarity search over the 12,204 clause corpus
4. Filtered search demonstration
"""
from pathlib import Path
import sys
import joblib
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent
src_path = str(PROJECT_ROOT / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from text_cleaner import clean_text
from search import get_search_engine


def run_demo():
    print("=" * 80)
    print("      CLAUSEIQ: ML CONTRACT CLAUSE CLASSIFICATION & INTELLIGENT SEARCH")
    print("                         SPRINT 2 END-TO-END DEMO")
    print("=" * 80)

    # 1. Load Artifacts
    art_dir = PROJECT_ROOT / "artifacts"
    if not (art_dir / "best_model.joblib").is_file():
        art_dir = PROJECT_ROOT / "models"

    print("\n[Step 1] Loading serialized artifacts...")
    model = joblib.load(art_dir / "best_model.joblib" if (art_dir / "best_model.joblib").is_file() else art_dir / "logistic_regression.pkl")
    vectorizer = joblib.load(art_dir / "tfidf_vectorizer.joblib" if (art_dir / "tfidf_vectorizer.joblib").is_file() else art_dir / "tfidf_vectorizer.pkl")
    le = joblib.load(art_dir / "label_encoder.joblib" if (art_dir / "label_encoder.joblib").is_file() else art_dir / "label_encoder.pkl")
    print(f"         Model Architecture: {type(model).__name__}")
    print(f"         Vocabulary Features: {len(vectorizer.get_feature_names_out()):,}")
    print(f"         Target Categories:   {len(le.classes_)}")

    # 2. Live Classification of Sample Clauses
    print("\n" + "=" * 80)
    print("[Step 2] LIVE CLAUSE CLASSIFICATION INFERENCE")
    print("=" * 80)

    sample_clauses = [
        (
            "Governing Law Clause",
            "This Agreement and all disputes arising hereunder shall be governed by, and construed in accordance with, the laws of the State of New York, without regard to its conflict of laws principles.",
        ),
        (
            "Termination Clause",
            "Either party may terminate this Agreement for convenience at any time upon giving sixty (60) days prior written notice to the other party.",
        ),
        (
            "Audit Rights Clause",
            "The Company shall maintain books and records relating to the Services, and Customer or its independent auditors shall have the right upon reasonable notice to audit such records during normal business hours.",
        ),
        (
            "Non-Compete Clause",
            "During the term of this Agreement and for a period of two (2) years thereafter, the Executive shall not directly or indirectly engage in or operate any business that competes with the Company.",
        ),
    ]

    for title, raw_text in sample_clauses:
        cleaned = clean_text(raw_text)
        vec = vectorizer.transform([cleaned])
        probs = model.predict_proba(vec)[0]
        pred_idx = int(np.argmax(probs))
        confidence = float(np.max(probs))
        pred_category = le.inverse_transform([pred_idx])[0]

        # Top 3 predicted classes
        top3_indices = np.argsort(-probs)[:3]
        top3_str = ", ".join([f"{le.inverse_transform([idx])[0]} ({probs[idx]*100:.1f}%)" for idx in top3_indices])

        print(f"\nSample: [{title}]")
        print(f"Raw Text:    \"{raw_text[:95]}...\"")
        print(f"Prediction:  [{pred_category}] (Confidence: {confidence*100:.2f}%)")
        print(f"Top-3 Probs: {top3_str}")

    # 3. Intelligent Cosine Similarity Search
    print("\n" + "=" * 80)
    print("[Step 3] INTELLIGENT TF-IDF + COSINE SIMILARITY SEARCH")
    print("=" * 80)

    search_queries = [
        "termination for convenience",
        "governing law of new york",
        "limitation of liability",
        "non-compete restriction",
    ]

    engine = get_search_engine()

    for q in search_queries:
        print(f"\nSearch Query: '{q}' (top_k=3)")
        print("-" * 75)
        results = engine.search(q, top_k=3)
        for r in results:
            preview = r["clause_text"].replace("\n", " ").strip()
            if len(preview) > 100:
                preview = preview[:97] + "..."
            print(f"  Rank #{r['rank']} | Cosine Similarity: {r['similarity_score']:.4f}")
            print(f"          Predicted: [{r['predicted_category']}] | True: [{r['true_category']}]")
            print(f"          Contract:  {r['source_contract']}")
            print(f"          Clause:    \"{preview}\"\n")

    # 4. Search with Category Filter
    print("=" * 80)
    print("[Step 4] FILTERED SEARCH: 'dispute settlement' with category_filter='Governing Law'")
    print("=" * 80)
    filtered_results = engine.search("dispute settlement", top_k=2, category_filter="Governing Law")
    for r in filtered_results:
        preview = r["clause_text"].replace("\n", " ").strip()[:95]
        print(f"  Rank #{r['rank']} | Score: {r['similarity_score']:.4f} | Category: [{r['true_category']}]")
        print(f"          Clause: \"{preview}...\"\n")

    print("=" * 80)
    print("DEMO COMPLETED SUCCESSFULLY: ALL INFERENCE EXECUTED WITH REAL ARTIFACTS!")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
