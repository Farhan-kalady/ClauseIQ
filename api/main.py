from contextlib import asynccontextmanager
from pathlib import Path
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root and src/ are in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
src_path = str(PROJECT_ROOT / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from api.config import settings
from api.services.ml_service import load_artifacts
from api.services.supabase_service import get_supabase_client
from search import get_search_engine

# Import modular routers
from api.routers import health, classify, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: Load ML artifacts, pre-index search corpus, and init DB once on startup."""
    load_artifacts()
    get_search_engine()
    get_supabase_client()
    yield


# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(classify.router)
app.include_router(search.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
