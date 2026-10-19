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
    confidence_status: str = "Moderate confidence"
    confidence_explanation: str = "Confidence represents the model's estimated probability for the predicted category. It does not represent guaranteed classification accuracy or legal certainty."
    is_out_of_scope: bool = False
    model_name: str
    alternatives: List[AlternativeCategory] = Field(default_factory=list)


class DocumentClauseItem(BaseModel):
    clause_index: int
    clause_text: str
    cleaned_text: str
    predicted_category: str
    confidence: Optional[float] = None
    confidence_score: Optional[float] = None
    confidence_status: str = "Moderate confidence"
    is_out_of_scope: bool = False
    alternatives: List[AlternativeCategory] = Field(default_factory=list)


class DocumentClassifyResponse(BaseModel):
    contract_id: str
    document_name: str
    total_clauses: int
    clauses: List[DocumentClauseItem]


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    top_k: int = Field(5, ge=1, le=50, description="Number of top ranked clauses to retrieve (1-50)")
    category_filter: Optional[str] = Field(None, description="Optional category filter (e.g., 'Governing Law')")
    min_score: float = Field(0.0, ge=0.0, le=1.0, description="Minimum cosine similarity score threshold")
    contract_id: Optional[str] = Field(None, description="Optional contract ID to restrict search to a specific uploaded contract")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "termination for convenience",
                "top_k": 3,
                "category_filter": None,
                "min_score": 0.0,
                "contract_id": None,
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
    search_scope: str = "CUAD Clause Library (12,204 clauses)"
    contract_id: Optional[str] = None
    total_results: int
    results: List[SearchResultItem]


class ContractSummary(BaseModel):
    id: str
    document_name: str
    total_clauses: int
    created_at: str


class ContractClausesResponse(BaseModel):
    contract_id: str
    document_name: str
    total_clauses: int
    clauses: List[DocumentClauseItem]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    model_loaded: bool
    model_name: Optional[str] = None
    search_engine_loaded: bool
    supabase_connected: bool
