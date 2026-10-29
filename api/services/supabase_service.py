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
            "input_text": input_text[:4000],
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
    contract_id: Optional[str] = None,
) -> Optional[str]:
    """Store contract metadata and extracted classified clauses in Supabase atomically.
    
    If clause insertion fails, the created contract record is rolled back to prevent orphans.
    """
    client = get_supabase_client()
    if not client:
        return None

    try:
        contract_payload = {"document_name": document_name}
        if contract_id:
            contract_payload["id"] = contract_id

        contract_res = client.table("contracts").insert(contract_payload).execute()
        if not contract_res.data:
            return None
        saved_id = contract_res.data[0]["id"]

        clause_records = [
            {
                "contract_id": saved_id,
                "clause_text": c.get("clause_text", "")[:4000],
                "category": c.get("predicted_category", "Unknown"),
                "confidence_score": c.get("confidence"),
            }
            for c in clauses
        ]

        if clause_records:
            try:
                client.table("clauses").insert(clause_records).execute()
            except Exception as clause_err:
                logger.error(f"Failed to insert clauses, rolling back contract {saved_id}: {clause_err}")
                try:
                    client.table("contracts").delete().eq("id", saved_id).execute()
                except Exception as rb_err:
                    logger.critical(f"Rollback failed for contract {saved_id}: {rb_err}")
                return None

        return saved_id
    except Exception as e:
        logger.warning(f"Supabase save_contract_and_clauses failed: {e}")
        return None


def fetch_contracts(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve saved contracts list from Supabase or fallback to in-memory uploads."""
    client = get_supabase_client()
    if client:
        try:
            # Embedded aggregate returns clause counts in the same request (no per-contract queries)
            res = client.table("contracts").select("id, document_name, created_at, clauses(count)").order("created_at", desc=True).limit(limit).execute()
            if res.data:
                return [
                    {
                        "id": row["id"],
                        "document_name": row["document_name"],
                        "total_clauses": (row.get("clauses") or [{}])[0].get("count", 0),
                        "created_at": row["created_at"],
                    }
                    for row in res.data
                ]
        except Exception as e:
            logger.warning(f"Failed to query contracts from Supabase: {e}")

    # Offline in-memory fallback
    from api.services.ml_service import list_uploaded_contracts
    return list_uploaded_contracts()


def fetch_contract_clauses(contract_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve clauses for a given contract ID from Supabase or fallback to in-memory uploads."""
    client = get_supabase_client()
    if client:
        try:
            c_res = client.table("contracts").select("id, document_name, created_at").eq("id", contract_id).execute()
            if c_res.data:
                c_row = c_res.data[0]
                cl_res = client.table("clauses").select("id, clause_text, category, confidence_score").eq("contract_id", contract_id).order("created_at").execute()
                clauses = [
                    {
                        "clause_index": idx,
                        "clause_text": row["clause_text"],
                        "cleaned_text": row["clause_text"].lower(),
                        "predicted_category": row["category"],
                        "confidence": row["confidence_score"],
                        "confidence_score": row["confidence_score"],
                        "confidence_status": "High confidence" if (row["confidence_score"] or 0) >= 0.50 else "Moderate confidence",
                        "is_out_of_scope": False,
                        "alternatives": [],
                    }
                    for idx, row in enumerate(cl_res.data or [], start=1)
                ]
                return {
                    "contract_id": contract_id,
                    "document_name": c_row["document_name"],
                    "total_clauses": len(clauses),
                    "clauses": clauses,
                }
        except Exception as e:
            logger.warning(f"Failed to query contract clauses from Supabase: {e}")

    # Offline in-memory fallback
    from api.services.ml_service import get_uploaded_contract
    uploaded = get_uploaded_contract(contract_id)
    if uploaded:
        return {
            "contract_id": contract_id,
            "document_name": uploaded["document_name"],
            "total_clauses": uploaded["total_clauses"],
            "clauses": uploaded["clauses"],
        }

    return None
