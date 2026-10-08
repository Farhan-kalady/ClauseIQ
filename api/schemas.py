from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ClassifyRequest(BaseModel):
    clause_text: str = Field(..., min_length=1, description="Raw contract clause text to classify")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "clause_text": "This Agreement shall be governed by, and construed in accordance with, the laws of the State of Delaware."
            }
        }
    )


class AlternativeCategory(BaseModel):
    category: str
    confidence: float


class ClassifyResponse(BaseModel):
    clause_text: str
    cleaned_text: str
    predicted_category: str
    confidence: Optional[float] = None
    confidence_score: Optional[float] = None
    confidence_type: str = "probability"
    model_name: str
    alternatives: List[AlternativeCategory] = Field(default_factory=list)


class DocumentClauseItem(BaseModel):
    clause_index: int
    clause_text: str
    cleaned_text: str
    predicted_category: str
    confidence: Optional[float] = None
    confidence_score: Optional[float] = None
    alternatives: List[AlternativeCategory] = Field(default_factory=list)


class DocumentClassifyResponse(BaseModel):
    document_name: str
    total_clauses: int
    clauses: List[DocumentClauseItem]


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    top_k: int = Field(5, ge=1, le=50, description="Number of top ranked clauses to retrieve (1-50)")
    category_filter: Optional[str] = Field(None, description="Optional category filter (e.g., 'Governing Law')")
    min_score: float = Field(0.0, ge=0.0, le=1.0, description="Minimum cosine similarity score threshold")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "termination for convenience",
                "top_k": 3,
                "category_filter": None,
                "min_score": 0.0,
            }
        }
    )


class SearchResultItem(BaseModel):
    rank: int
    clause_text: str
    predicted_category: str
    true_category: Optional[str] = None
    similarity_score: float
    source_contract: str


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    model_loaded: bool
    search_engine_loaded: bool
    supabase_connected: bool
