from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple
from api.config import settings
from api.services.supabase_service import log_search, get_supabase_client
from api.services.ml_service import get_uploaded_contract

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
    contract_id: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """Execute cosine similarity search over either CUAD corpus or a specific uploaded contract.
    
    Returns:
        (results, search_scope)
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        raise ValueError("Search query cannot be empty or solely whitespace.")

    # Guard bounds on top_k
    k = max(1, min(int(top_k), 50))

    # Guard bounds on min_score
    score_threshold = max(0.0, min(float(min_score), 1.0))

    engine = get_search_engine()

    # Case 1: Scoped search for a specific uploaded contract
    if contract_id:
        uploaded = get_uploaded_contract(contract_id)
        if uploaded:
            results = engine.search_custom_clauses(
                clauses=uploaded["clauses"],
                query=cleaned_query,
                top_k=k,
                category_filter=category_filter,
                min_score=score_threshold,
                document_name=uploaded["document_name"],
            )
            scope = f"Uploaded Contract: {uploaded['document_name']}"
        else:
            # Check Supabase database if connected
            db_client = get_supabase_client()
            db_clauses = None
            doc_name = "Database Contract"
            if db_client:
                try:
                    c_res = db_client.table("contracts").select("document_name").eq("id", contract_id).execute()
                    if c_res.data:
                        doc_name = c_res.data[0]["document_name"]
                        cl_res = db_client.table("clauses").select("clause_text, category, confidence_score").eq("contract_id", contract_id).execute()
                        if cl_res.data:
                            db_clauses = [
                                {
                                    "clause_text": row["clause_text"],
                                    "predicted_category": row["category"],
                                    "confidence": row["confidence_score"],
                                }
                                for row in cl_res.data
                            ]
                except Exception:
                    db_clauses = None

            if db_clauses:
                results = engine.search_custom_clauses(
                    clauses=db_clauses,
                    query=cleaned_query,
                    top_k=k,
                    category_filter=category_filter,
                    min_score=score_threshold,
                    document_name=doc_name,
                )
                scope = f"Stored Contract: {doc_name}"
            else:
                # Check if it's a CUAD contract_id
                cuad_results = engine.search(
                    query=cleaned_query,
                    top_k=k,
                    category_filter=category_filter,
                    min_score=score_threshold,
                    contract_id=contract_id,
                )
                if cuad_results:
                    results = cuad_results
                    scope = f"CUAD Contract: {contract_id}"
                else:
                    raise ValueError(f"Contract ID '{contract_id}' was not found in active uploads or database.")
    else:
        # Case 2: Global pre-indexed CUAD clause library
        results = engine.search(
            query=cleaned_query,
            top_k=k,
            category_filter=category_filter,
            min_score=score_threshold,
        )
        scope = "CUAD Clause Library (12,204 clauses)"

    # Asynchronously / best-effort log search event to Supabase
    log_search(
        query=cleaned_query,
        category_filter=category_filter,
        top_k=k,
        results_count=len(results),
    )

    return results, scope
