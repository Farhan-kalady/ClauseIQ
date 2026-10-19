from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Automatically load variables from .env if present
_env_path = PROJECT_ROOT / ".env"
if _env_path.is_file():
    try:
        with open(_env_path, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    _k = _k.strip()
                    _v = _v.strip().strip("'\"")
                    if _k and _k not in os.environ:
                        os.environ[_k] = _v
    except Exception:
        pass


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
    
    # CORS: No wildcard '*' default when credentials are enabled
    _raw_cors = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
    )
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in _raw_cors.split(",")
        if origin.strip() and origin.strip() != "*"
    ]
    if not CORS_ORIGINS:
        CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]
    
    # Supabase configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_ANON_KEY", ""))

settings = Settings()
