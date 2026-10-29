from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pandas as pd
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from text_cleaner import clean_text

_stemmer = PorterStemmer()


def _stem_tokens(text: str) -> List[str]:
    """Tokenize, drop stop words, and stem so 'governing'/'governed' and 'law'/'laws' match."""
    return [_stemmer.stem(t) for t in re.findall(r"[a-z0-9]+", clean_text(text))
            if t not in ENGLISH_STOP_WORDS]


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

        # Retrieval uses its own word-level TF-IDF index: the classifier's character
        # n-grams match fragments of short keyword queries against unrelated clauses.
        self.search_vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
        )
        self.search_tfidf = self.search_vectorizer.fit_transform(self.df["clean_text"].fillna("").astype(str))
        print(f"Search index built: {self.search_tfidf.shape[1]} word features.")
        print("Corpus search engine initialization complete.")

    def search(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        min_score: float = 0.0,
        contract_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search clauses by query using cosine similarity across CUAD corpus.
        
        Args:
            query: The search text query.
            top_k: Number of ranked results to return (default: 5).
            category_filter: Optional category to filter results by.
            min_score: Optional minimum cosine similarity threshold.
            contract_id: Optional CUAD contract ID to restrict corpus search.

        Returns:
            List of ranked result dictionaries.
        """
        if not query or not isinstance(query, str) or not query.strip():
            return []

        cleaned_query = clean_text(query)
        if not cleaned_query:
            return []

        query_vec = self.search_vectorizer.transform([cleaned_query])
        if query_vec.nnz == 0:
            return []

        # Filter by contract_id if specified in CUAD corpus
        if contract_id:
            c_mask = self.df["contract_id"].astype(str) == str(contract_id)
            if not c_mask.any():
                return []
            candidate_indices = np.where(c_mask)[0]
        else:
            candidate_indices = np.arange(len(self.df))

        # Filter by category if specified
        if category_filter:
            category_filter_lower = category_filter.strip().lower()
            cat_series = self.df["category"].iloc[candidate_indices].astype(str).str.lower()
            match_mask = cat_series == category_filter_lower
            if not match_mask.any():
                match_mask = cat_series.str.contains(category_filter_lower, regex=False)
            candidate_indices = candidate_indices[np.where(match_mask)[0]]

        if len(candidate_indices) == 0:
            return []

        # Compute cosine similarity
        candidate_tfidf = self.search_tfidf[candidate_indices]
        sim_scores = cosine_similarity(query_vec, candidate_tfidf).flatten()

        # Filter by min_score; a zero score means no shared terms, so it is never a match
        valid_mask = (sim_scores >= min_score) & (sim_scores > 0)
        if not np.any(valid_mask):
            return []

        valid_indices = candidate_indices[valid_mask]
        valid_scores = sim_scores[valid_mask]

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

    def search_custom_clauses(
        self,
        clauses: List[Dict[str, Any]],
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        min_score: float = 0.0,
        document_name: str = "Uploaded Contract",
    ) -> List[Dict[str, Any]]:
        """Search an ad-hoc or uploaded list of clauses using the fitted vectorizer."""
        if not query or not isinstance(query, str) or not query.strip() or not clauses:
            return []

        if not _stem_tokens(query):
            return []

        # Filter by category if requested
        if category_filter:
            cat_lower = category_filter.strip().lower()
            filtered_clauses = [c for c in clauses if c.get("predicted_category", "").lower() == cat_lower]
        else:
            filtered_clauses = list(clauses)

        if not filtered_clauses:
            return []

        # A single contract gets its own stemmed index: the CUAD vocabulary has no stemming,
        # so 'governing law' would miss 'governed by the laws', and CUAD-wide IDF
        # under-weights terms that are distinctive within this one document.
        clause_texts = [c.get("clause_text", "") for c in filtered_clauses]
        doc_vectorizer = TfidfVectorizer(
            tokenizer=_stem_tokens,
            lowercase=False,
            token_pattern=None,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        try:
            clause_vecs = doc_vectorizer.fit_transform(clause_texts)
        except ValueError:  # every clause was empty after stop-word removal
            return []
        query_vec = doc_vectorizer.transform([query])
        if query_vec.nnz == 0:
            return []

        sim_scores = cosine_similarity(query_vec, clause_vecs).flatten()

        valid_items = []
        for c, score in zip(filtered_clauses, sim_scores):
            if score >= min_score and score > 0:
                valid_items.append((c, float(score)))

        if not valid_items:
            return []

        valid_items.sort(key=lambda x: x[1], reverse=True)
        top_items = valid_items[:top_k]

        results = []
        for rank, (c, score) in enumerate(top_items, start=1):
            results.append({
                "rank": rank,
                "clause_text": c.get("clause_text", ""),
                "predicted_category": c.get("predicted_category", "Unknown"),
                "true_category": None,
                "similarity_score": round(float(score), 4),
                "source_contract": document_name,
                "classification_confidence": c.get("confidence"),
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
    contract_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Convenience functional wrapper for searching clauses."""
    engine = get_search_engine()
    return engine.search(
        query=query,
        top_k=top_k,
        category_filter=category_filter,
        min_score=min_score,
        contract_id=contract_id,
    )
