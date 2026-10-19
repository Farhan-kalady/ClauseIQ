from typing import List
from fastapi import APIRouter, HTTPException, status
from api.schemas import ContractClausesResponse, ContractSummary
from api.services.supabase_service import fetch_contract_clauses, fetch_contracts

router = APIRouter(prefix="/contracts", tags=["Contracts Management"])


@router.get(
    "",
    response_model=List[ContractSummary],
    status_code=status.HTTP_200_OK,
    summary="List saved or processed contracts",
)
def list_saved_contracts():
    """Retrieve list of processed contracts and their metadata from storage."""
    contracts = fetch_contracts()
    return [
        ContractSummary(
            id=c["id"],
            document_name=c["document_name"],
            total_clauses=c["total_clauses"],
            created_at=c.get("created_at") or "",
        )
        for c in contracts
    ]


@router.get(
    "/{contract_id}/clauses",
    response_model=ContractClausesResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve extracted and classified clauses for a specific contract",
)
def get_contract_clauses(contract_id: str):
    """Retrieve the full clause breakdown and predictions for a contract by ID."""
    result = fetch_contract_clauses(contract_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID '{contract_id}' not found.",
        )
    return ContractClausesResponse(**result)
