from fastapi import APIRouter
from api.schemas import HealthResponse
from api.services.ml_service import is_model_loaded
from api.services.supabase_service import is_connected
from api.config import settings

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint confirming API status, ML model loading, and Supabase connectivity."""
    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        model_loaded=is_model_loaded(),
        search_engine_loaded=True,
        supabase_connected=is_connected(),
    )
