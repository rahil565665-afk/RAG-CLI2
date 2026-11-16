from fastapi.testclient import TestClient

from app.main import app, service

client = TestClient(app)


def test_health_reports_full_knowledge_base():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["knowledge_base_chunks"] == 31


def test_api_rejects_blank_query():
    response = client.post("/api/v1/query", json={"query": "   "})
    assert response.status_code == 422


def test_api_requires_gemini_even_when_no_knowledge_base_passage_matches(monkeypatch):
    monkeypatch.setattr(service, "generator", None)
    response = client.post("/api/v1/query", json={"query": "What is the clinic's annual revenue?"})
    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]


def test_api_returns_safe_configuration_error_without_key(monkeypatch):
    monkeypatch.setattr(service, "generator", None)
    response = client.post("/api/v1/query", json={"query": "How much does a routine cleaning cost?"})
    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]