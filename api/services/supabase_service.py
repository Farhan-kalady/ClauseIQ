import logging
from typing import Any, Dict, List, Optional
from api.config import settings

logger = logging.getLogger("ClauseIQ.Supabase")

_supabase_client = None
_client_initialized = False


def get_supabase_client():
    """Lazily initialize and return Supabase client if credentials are configured."""
    global _supabase_client, _client_initialized
    if not _client_initialized:
        _client_initialized = True
        url = settings.SUPABASE_URL.strip()
        key = settings.SUPABASE_KEY.strip()
        if url and key:
            try:
                from supabase import create_client
                _supabase_client = create_client(url, key)
                logger.info(f"Supabase client successfully initialized for URL: {url}")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}")
                _supabase_client = None
        else:
            logger.info("Supabase credentials not configured. Running in local/offline mode.")
    return _supabase_client


def is_connected() -> bool:
    """Check if Supabase client is configured and initialized."""
    return get_supabase_client() is not None


def log_classification(
    input_text: str,
    predicted_category: str,
    confidence_score: Optional[float],
    document_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Log a single clause classification record to Supabase classification_logs table."""
    client = get_supabase_client()
    if not client:
        return None

    try:
        record = {
            "input_text": input_text[:4000],  # Bound text length
            "predicted_category": predicted_category,
            "confidence_score": confidence_score,
            "document_name": document_name,
        }
        res = client.table("classification_logs").insert(record).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        logger.warning(f"Supabase log_classification failed: {e}")
        return None


def log_search(
    query: str,
    category_filter: Optional[str],
    top_k: int,
    results_count: int,
) -> Optional[Dict[str, Any]]:
    """Log a search query to Supabase search_logs table."""
    client = get_supabase_client()
    if not client:
        return None

    try:
        record = {
            "query": query[:1000],
            "category_filter": category_filter,
            "top_k": top_k,
            "results_count": results_count,
        }
        res = client.table("search_logs").insert(record).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        logger.warning(f"Supabase log_search failed: {e}")
        return None


def save_contract_and_clauses(
    document_name: str,
    clauses: List[Dict[str, Any]],
) -> Optional[str]:
    """Store contract metadata and extracted classified clauses in Supabase."""
    client = get_supabase_client()
    if not client:
        return None

    try:
        contract_res = client.table("contracts").insert({"document_name": document_name}).execute()
        if not contract_res.data:
            return None
        contract_id = contract_res.data[0]["id"]

        clause_records = [
            {
                "contract_id": contract_id,
                "clause_text": c.get("clause_text", "")[:4000],
                "category": c.get("predicted_category", "Unknown"),
                "confidence_score": c.get("confidence"),
            }
            for c in clauses
        ]
        if clause_records:
            client.table("clauses").insert(clause_records).execute()

        return contract_id
    except Exception as e:
        logger.warning(f"Supabase save_contract_and_clauses failed: {e}")
        return None
