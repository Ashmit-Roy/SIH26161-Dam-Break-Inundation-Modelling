"""Basic smoke tests for the dashboard backend."""
from fastapi.testclient import TestClient
from src.dashboard.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_scenarios():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    assert "scenarios" in response.json()