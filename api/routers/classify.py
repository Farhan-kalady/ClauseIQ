from fastapi import APIRouter, File, HTTPException, UploadFile, status
from api.schemas import ClassifyRequest, ClassifyResponse, DocumentClassifyResponse
from api.services.ml_service import classify_clause, classify_document
from api.services.supabase_service import log_classification, save_contract_and_clauses

router = APIRouter(tags=["Classification"])


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Classify a single contract clause",
)
def classify_single(payload: ClassifyRequest):
    """Classify a single contract clause into one of 41 legal categories with actual probability scores."""
    try:
        res = classify_clause(payload.clause_text)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Best-effort Supabase logging
    log_classification(
        input_text=payload.clause_text,
        predicted_category=res["predicted_category"],
        confidence_score=res["confidence"],
    )

    return ClassifyResponse(**res)


@router.post(
    "/classify/file",
    response_model=DocumentClassifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload contract PDF or TXT, split into clauses, and classify each",
)
async def classify_file_upload(file: UploadFile = File(...)):
    """Extract text from an uploaded contract file (PDF or text), split into clauses, and classify each clause."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        result = classify_document(content, file.filename)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}",
        )

    # Best-effort Supabase persistence
    save_contract_and_clauses(file.filename, result["clauses"])

    return DocumentClassifyResponse(**result)
