from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings:
    PROJECT_NAME: str = "ClauseIQ API"
    VERSION: str = "3.0.0"
    DESCRIPTION: str = "Machine Learning-Based Contract Clause Classification and Intelligent Search System"
    
    # Paths
    PROJECT_ROOT: Path = PROJECT_ROOT
    SRC_DIR: Path = PROJECT_ROOT / "src"
    DATA_DIR: Path = PROJECT_ROOT / "data"
    ARTIFACTS_DIR: Path = PROJECT_ROOT / "artifacts"
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    
    # CORS
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,*"
        ).split(",")
        if origin.strip()
    ]
    
    # Supabase configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_ANON_KEY", ""))

settings = Settings()
