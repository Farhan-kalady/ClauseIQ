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

from search import get_search_engine, search
from api.main import app


@pytest.fixture(scope="module")
def search_engine():
    return get_search_engine()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# ==============================================================================
# 1. Search Function Tests
# ==============================================================================

def test_search_function_basic(search_engine):
    query = "termination for convenience"
    results = search_engine.search(query, top_k=5)
    assert isinstance(results, list)
    assert len(results) > 0

    first = results[0]
    assert "rank" in first
    assert "clause_text" in first
    assert "predicted_category" in first
    assert "similarity_score" in first
    assert "source_contract" in first
    assert isinstance(first["similarity_score"], float)
    assert 0.0 <= first["similarity_score"] <= 1.0


# ==============================================================================
# 2. Search Ranking Tests
# ==============================================================================

def test_search_ranking_order(search_engine):
    query = "governing law of the state of new york"
    results = search_engine.search(query, top_k=10)
    assert len(results) > 1

    scores = [r["similarity_score"] for r in results]
    # Check strictly monotonic non-increasing order
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], f"Ranking order violated: {scores[i]} < {scores[i+1]}"


# ==============================================================================
# 3. top_k Behavior Tests
# ==============================================================================

@pytest.mark.parametrize("k", [1, 3, 5, 10])
def test_search_top_k_behavior(search_engine, k):
    query = "confidentiality obligation"
    results = search_engine.search(query, top_k=k)
    assert len(results) <= k
    if len(results) > 0:
        assert results[0]["rank"] == 1
        assert results[-1]["rank"] == len(results)


# ==============================================================================
# 4. Category Filtering Tests
# ==============================================================================

def test_search_category_filter_valid(search_engine):
    query = "disputes shall be settled under new york law"
    results = search_engine.search(query, top_k=5, category_filter="Governing Law")
    assert len(results) > 0
    for r in results:
        assert r["true_category"].lower() == "governing law"


def test_search_category_filter_nonexistent(search_engine):
    query = "liability limitation"
    results = search_engine.search(query, top_k=5, category_filter="NonExistentCategory_XYZ")
    assert results == []


# ==============================================================================
# 5. Empty and Invalid Query Handling
# ==============================================================================

def test_search_empty_and_invalid_queries(search_engine):
    assert search_engine.search("") == []
    assert search_engine.search("     ") == []
    assert search_engine.search(None) == []
    # Out of vocabulary gibberish
    assert search_engine.search("zzzyyyxxxwwvuuuttt12345") == []


# ==============================================================================
# 6. /search API Tests
# ==============================================================================

def test_api_search_endpoint_success(client):
    payload = {
        "query": "termination for convenience",
        "top_k": 3,
    }
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == payload["query"]
    assert "results" in data
    assert len(data["results"]) <= 3
    assert data["total_results"] == len(data["results"])


def test_api_search_endpoint_with_category_filter(client):
    payload = {
        "query": "this agreement shall be governed by new york law",
        "top_k": 4,
        "category_filter": "Governing Law",
    }
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0
    for item in data["results"]:
        assert item["true_category"].lower() == "governing law"


def test_api_search_endpoint_empty_query(client):
    response = client.post("/search", json={"query": "   ", "top_k": 5})
    assert response.status_code == 400


# ==============================================================================
# 7. /classify API Tests
# ==============================================================================

def test_api_classify_endpoint_success(client):
    clause = "This Agreement shall be governed by and construed in accordance with the laws of Delaware."
    response = client.post("/classify", json={"clause_text": clause})
    assert response.status_code == 200
    data = response.json()
    assert data["clause_text"] == clause
    assert "cleaned_text" in data
    assert data["predicted_category"] == "Governing Law"
    assert data["confidence_score"] is not None
    assert 0.0 <= data["confidence_score"] <= 1.0
    assert data["model_name"] == "LogisticRegression"


def test_api_classify_endpoint_empty_text(client):
    response = client.post("/classify", json={"clause_text": "    "})
    assert response.status_code == 400


def test_api_health_and_categories(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    cats = client.get("/categories")
    assert cats.status_code == 200
    assert cats.json()["total_categories"] == 41
    assert "Governing Law" in cats.json()["categories"]
