from pathlib import Path
import sys
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from text_cleaner import clean_text


class ClauseSearchEngine:
    """Intelligent search engine using classical TF-IDF and Cosine Similarity."""

    def __init__(
        self,
        data_path: Path | str = BASE_DIR / "data" / "clauseiq_dataset_clean.csv",
        models_dir: Path | str = BASE_DIR / "artifacts",
    ):
        self.data_path = Path(data_path)
        self.models_dir = Path(models_dir)

        # Fallback to models/ if artifacts/ is missing files
        if not (self.models_dir / "best_model.joblib").is_file():
            self.models_dir = BASE_DIR / "models"

        self._load_corpus_and_models()

    def _load_corpus_and_models(self):
        print(f"Loading search corpus from {self.data_path}...")
        self.df = pd.read_csv(self.data_path)

        # Ensure clean_text column exists
        if "clean_text" not in self.df.columns:
            text_col = "clause_text" if "clause_text" in self.df.columns else self.df.columns[1]
            self.df["clean_text"] = self.df[text_col].fillna("").astype(str).apply(clean_text)

        # Load vectorizer and classification model
        vec_path = (
            self.models_dir / "tfidf_vectorizer.joblib"
            if (self.models_dir / "tfidf_vectorizer.joblib").is_file()
            else self.models_dir / "tfidf_vectorizer.pkl"
        )
        model_path = (
            self.models_dir / "best_model.joblib"
            if (self.models_dir / "best_model.joblib").is_file()
            else self.models_dir / "logistic_regression.pkl"
        )
        le_path = (
            self.models_dir / "label_encoder.joblib"
            if (self.models_dir / "label_encoder.joblib").is_file()
            else self.models_dir / "label_encoder.pkl"
        )

        print(f"Loading vectorizer from {vec_path}...")
        self.vectorizer = joblib.load(vec_path)
        print(f"Loading classifier from {model_path}...")
        self.classifier = joblib.load(model_path)
        print(f"Loading label encoder from {le_path}...")
        self.label_encoder = joblib.load(le_path)

        # Vectorize corpus using the fitted TF-IDF vectorizer
        print("Pre-indexing corpus clauses using TF-IDF representation...")
        self.corpus_tfidf = self.vectorizer.transform(self.df["clean_text"].fillna("").astype(str))
        print(f"Corpus indexed: {self.corpus_tfidf.shape[0]} clauses, {self.corpus_tfidf.shape[1]} features.")

        # Precompute predicted categories for all corpus items for fast retrieval
        preds_idx = self.classifier.predict(self.corpus_tfidf)
        self.df["predicted_category"] = self.label_encoder.inverse_transform(preds_idx)
        print("Corpus search engine initialization complete.")

    def search(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search clauses by query using cosine similarity.
        
        Args:
            query: The search text query.
            top_k: Number of ranked results to return (default: 5).
            category_filter: Optional category to filter results by.
            min_score: Optional minimum cosine similarity threshold.

        Returns:
            List of ranked result dictionaries.
        """
        if not query or not isinstance(query, str) or not query.strip():
            return []

        cleaned_query = clean_text(query)
        if not cleaned_query:
            return []

        query_vec = self.vectorizer.transform([cleaned_query])

        # If query contains only out-of-vocabulary words
        if query_vec.nnz == 0:
            return []

        # Cosine similarity against all corpus clauses
        # Both query_vec and corpus_tfidf are L2-normalized by TfidfVectorizer
        sim_scores = cosine_similarity(query_vec, self.corpus_tfidf).flatten()

        # Apply category filter if provided
        if category_filter:
            category_filter_lower = category_filter.strip().lower()
            mask = self.df["category"].astype(str).str.lower() == category_filter_lower
            if not mask.any():
                # Try matching without exact case
                mask = self.df["category"].astype(str).str.lower().str.contains(category_filter_lower, regex=False)
            filtered_indices = np.where(mask)[0]
        else:
            filtered_indices = np.arange(len(self.df))

        if len(filtered_indices) == 0:
            return []

        filtered_scores = sim_scores[filtered_indices]

        # Filter by min_score
        valid_mask = filtered_scores >= min_score
        if not np.any(valid_mask):
            return []

        valid_indices = filtered_indices[valid_mask]
        valid_scores = filtered_scores[valid_mask]

        # Top-K sorting (descending similarity)
        if len(valid_scores) > top_k:
            top_k_partition = np.argpartition(-valid_scores, top_k)[:top_k]
            sorted_order = top_k_partition[np.argsort(-valid_scores[top_k_partition])]
        else:
            sorted_order = np.argsort(-valid_scores)

        ranked_indices = valid_indices[sorted_order]
        ranked_scores = valid_scores[sorted_order]

        results = []
        for rank, (idx, score) in enumerate(zip(ranked_indices, ranked_scores), start=1):
            row = self.df.iloc[idx]
            results.append({
                "rank": rank,
                "clause_text": str(row["clause_text"]),
                "predicted_category": str(row["predicted_category"]),
                "true_category": str(row["category"]) if "category" in row else None,
                "similarity_score": round(float(score), 4),
                "source_contract": str(row["contract_id"]) if "contract_id" in row else "unknown",
            })

        return results


# Global singleton instance for application reuse
_search_engine_instance: Optional[ClauseSearchEngine] = None


def get_search_engine() -> ClauseSearchEngine:
    global _search_engine_instance
    if _search_engine_instance is None:
        _search_engine_instance = ClauseSearchEngine()
    return _search_engine_instance


def search(
    query: str,
    top_k: int = 5,
    category_filter: Optional[str] = None,
    min_score: float = 0.0,
) -> List[Dict[str, Any]]:
    """Convenience functional wrapper for searching clauses."""
    engine = get_search_engine()
    return engine.search(query=query, top_k=top_k, category_filter=category_filter, min_score=min_score)


if __name__ == "__main__":
    test_queries = [
        "termination for convenience",
        "governing law of new york",
        "non-compete restriction",
        "limitation of liability",
    ]

    engine = get_search_engine()
    for q in test_queries:
        print("\n" + "=" * 60)
        print(f"QUERY: '{q}'")
        print("=" * 60)
        res = engine.search(q, top_k=3)
        for r in res:
            preview = r["clause_text"].replace("\n", " ").strip()[:85]
            print(f"Rank {r['rank']} | Sim: {r['similarity_score']:.4f} | True: [{r['true_category']}] | Pred: [{r['predicted_category']}]")
            print(f"       Text: \"{preview}...\"\n")
