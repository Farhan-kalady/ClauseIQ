from fastapi import APIRouter, HTTPException, status
from api.schemas import SearchRequest, SearchResponse, SearchResultItem
from api.services.search_service import execute_search
from api.services.ml_service import get_categories_list

router = APIRouter(tags=["Search & Metadata"])


@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search clause corpus using cosine similarity",
)
def search_clauses(payload: SearchRequest):
    """Search 12,204 pre-indexed contract clauses using TF-IDF and Cosine Similarity."""
    try:
        results = execute_search(
            query=payload.query,
            top_k=payload.top_k,
            category_filter=payload.category_filter,
            min_score=payload.min_score,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    items = [
        SearchResultItem(
            rank=r["rank"],
            clause_text=r["clause_text"],
            predicted_category=r["predicted_category"],
            true_category=r.get("true_category"),
            similarity_score=r["similarity_score"],
            source_contract=r["source_contract"],
        )
        for r in results
    ]

    return SearchResponse(
        query=payload.query,
        total_results=len(items),
        results=items,
    )


@router.get(
    "/categories",
    summary="Get list of supported legal clause categories",
)
def list_categories():
    """Return the 41 supported legal clause categories from CUAD v1."""
    categories = get_categories_list()
    return {
        "total_categories": len(categories),
        "categories": categories,
    }
