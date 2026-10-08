from pathlib import Path
import sys
from typing import Any, Dict, List, Optional
from api.config import settings
from api.services.supabase_service import log_search

# Ensure src/ is in sys.path
src_path = str(settings.SRC_DIR)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from search import get_search_engine


def execute_search(
    query: str,
    top_k: int = 5,
    category_filter: Optional[str] = None,
    min_score: float = 0.0,
) -> List[Dict[str, Any]]:
    """Execute cosine similarity search over the CUAD clause corpus.
    
    Reuses the existing Sprint 2 search engine and already-loaded TF-IDF vectorizer.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        raise ValueError("Search query cannot be empty or solely whitespace.")

    # Guard bounds on top_k
    k = max(1, min(int(top_k), 50))

    # Guard bounds on min_score
    score_threshold = max(0.0, min(float(min_score), 1.0))

    engine = get_search_engine()
    results = engine.search(
        query=cleaned_query,
        top_k=k,
        category_filter=category_filter,
        min_score=score_threshold,
    )

    # Asynchronously / best-effort log search event to Supabase
    log_search(
        query=cleaned_query,
        category_filter=category_filter,
        top_k=k,
        results_count=len(results),
    )

    return results
