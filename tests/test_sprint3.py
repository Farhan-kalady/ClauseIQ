import io
from pathlib import Path
import sys
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
root_path = str(PROJECT_ROOT)
src_path = str(PROJECT_ROOT / "src")

if root_path not in sys.path:
    sys.path.insert(0, root_path)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from api.main import app
from api.services.supabase_service import is_connected, log_classification, log_search


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# ==============================================================================
# 1. Health Endpoint Tests
# ==============================================================================

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ClauseIQ API"
    assert data["version"] == "3.0.0"
    assert data["model_loaded"] is True
    assert data["search_engine_loaded"] is True
    assert isinstance(data["supabase_connected"], bool)


# ==============================================================================
# 2. /classify Endpoint Tests (Direct Text)
# ==============================================================================

def test_classify_valid_clause(client):
    clause = "This Agreement and all claims arising out of it shall be governed by Delaware law."
    res = client.post("/classify", json={"clause_text": clause})
    assert res.status_code == 200
    data = res.json()
    assert data["clause_text"] == clause
    assert "cleaned_text" in data
    assert data["predicted_category"] == "Governing Law"
    assert data["confidence"] is not None
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["confidence_type"] == "probability"
    assert data["model_name"] == "LogisticRegression"
    assert "alternatives" in data
    assert isinstance(data["alternatives"], list)
    assert len(data["alternatives"]) <= 3
    if len(data["alternatives"]) > 0:
        first_alt = data["alternatives"][0]
        assert "category" in first_alt
        assert "confidence" in first_alt
        assert 0.0 <= first_alt["confidence"] <= 1.0


def test_classify_empty_and_whitespace_input(client):
    # Empty string
    res_empty = client.post("/classify", json={"clause_text": ""})
    assert res_empty.status_code in (400, 422)

    # Whitespace only
    res_spaces = client.post("/classify", json={"clause_text": "     \n\t  "})
    assert res_spaces.status_code == 400


def test_classify_gibberish_input(client):
    # Input with no valid legal or alphanumeric tokens
    res_gibberish = client.post("/classify", json={"clause_text": "@@@ ### $$$ %%%"})
    assert res_gibberish.status_code == 400


def test_classify_very_long_input(client):
    # Long repetitive legal clause
    long_clause = ("The Service Provider agrees to maintain strict confidentiality of all data. " * 50)
    res = client.post("/classify", json={"clause_text": long_clause})
    assert res.status_code == 200
    data = res.json()
    assert "predicted_category" in data
    assert data["confidence"] is not None


# ==============================================================================
# 3. /classify/file Endpoint Tests (Document PDF & Text Upload)
# ==============================================================================

def test_classify_pdf_document_upload(client):
    pdf_path = PROJECT_ROOT / "data" / "raw_pdfs" / "sample_contract.pdf"
    assert pdf_path.is_file(), f"Sample PDF missing at {pdf_path}"

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/classify/file",
        files={"file": ("sample_contract.pdf", file_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["document_name"] == "sample_contract.pdf"
    assert data["total_clauses"] > 0
    assert len(data["clauses"]) == data["total_clauses"]

    # Verify individual clause structure
    first_clause = data["clauses"][0]
    assert "clause_index" in first_clause
    assert "clause_text" in first_clause
    assert "predicted_category" in first_clause
    assert "confidence" in first_clause


def test_classify_text_document_upload(client):
    txt_content = (
        "This Agreement shall be governed by New York law.\n\n"
        "Either party may terminate this agreement upon thirty days written notice.\n\n"
        "Confidential information shall be protected for three years."
    ).encode("utf-8")

    response = client.post(
        "/classify/file",
        files={"file": ("contract.txt", txt_content, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["document_name"] == "contract.txt"
    assert data["total_clauses"] >= 2


def test_classify_empty_file_upload(client):
    response = client.post(
        "/classify/file",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400


# ==============================================================================
# 4. /search Endpoint Tests
# ==============================================================================

def test_search_valid_query(client):
    payload = {
        "query": "termination for convenience",
        "top_k": 5,
        "category_filter": None,
        "min_score": 0.0,
    }
    res = client.post("/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == payload["query"]
    assert len(data["results"]) <= 5
    assert data["total_results"] == len(data["results"])
    if len(data["results"]) > 0:
        first = data["results"][0]
        assert "rank" in first
        assert "similarity_score" in first
        assert "clause_text" in first
        assert "predicted_category" in first
        assert "source_contract" in first


def test_search_empty_query(client):
    res = client.post("/search", json={"query": "   ", "top_k": 5})
    assert res.status_code == 400


def test_search_invalid_top_k(client):
    # top_k below min (ge=1)
    res_zero = client.post("/search", json={"query": "governing law", "top_k": 0})
    assert res_zero.status_code == 422

    # top_k above max (le=50)
    res_excessive = client.post("/search", json={"query": "governing law", "top_k": 100})
    assert res_excessive.status_code == 422


def test_search_unknown_category_filter(client):
    payload = {
        "query": "liability limitation",
        "top_k": 5,
        "category_filter": "UnknownFictionalCategory_XYZ",
    }
    res = client.post("/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_results"] == 0
    assert data["results"] == []


def test_search_special_characters(client):
    res = client.post("/search", json={"query": "!@#$%^&*()_+{}[]:;<>?", "top_k": 3})
    assert res.status_code == 200
    # Should handle cleanly without crashing, returning 0 results for non-matching tokens
    assert "results" in res.json()


def test_search_very_long_query(client):
    long_q = "indemnification and hold harmless clause " * 40
    res = client.post("/search", json={"query": long_q, "top_k": 3})
    assert res.status_code == 200
    assert "results" in res.json()


# ==============================================================================
# 5. Metadata and Categories Endpoint Tests
# ==============================================================================

def test_categories_endpoint(client):
    res = client.get("/categories")
    assert res.status_code == 200
    data = res.json()
    assert data["total_categories"] == 41
    assert "Governing Law" in data["categories"]
    assert "Termination For Convenience" in data["categories"]
    assert "Cap On Liability" in data["categories"]


# ==============================================================================
# 6. CORS Configuration Tests
# ==============================================================================

def test_cors_headers(client):
    res = client.options(
        "/classify",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert res.status_code == 200
    assert "access-control-allow-origin" in res.headers


# ==============================================================================
# 7. Supabase Service Graceful Degradation Tests
# ==============================================================================

def test_supabase_service_graceful_handling():
    # If credentials are not set, logging operations must gracefully return None without raising
    if not is_connected():
        res_class = log_classification("sample text", "Governing Law", 0.95)
        assert res_class is None

        res_search = log_search("sample query", None, 5, 3)
        assert res_search is None
