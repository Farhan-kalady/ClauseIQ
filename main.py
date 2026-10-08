"""ClauseIQ FastAPI Application Entrypoint.

This file exposes the FastAPI application instance for running with:
    uvicorn main:app --reload
"""
from api.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
