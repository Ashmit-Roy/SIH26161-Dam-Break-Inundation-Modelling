from fastapi.testclient import TestClient
from backend.app.main import app


def test_backend_root_endpoint():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data


def test_backend_simulation_endpoints():
    client = TestClient(app)

    # 1. Start simulation
    payload = {
        "simulation_id": "test_sim_001",
        "model": "SPH",
        "scenario_id": "scenario_a",
        "breach_width": 10.0,
        "breach_height": 2.0,
    }
    res_start = client.post("/api/simulations", json=payload)
    assert res_start.status_code == 200
    assert res_start.json()["simulation_id"] == "test_sim_001"

    # 2. Check status
    res_status = client.get("/api/simulations/test_sim_001/status")
    assert res_status.status_code == 200

    # 3. Retrieve result
    res_result = client.get("/api/simulations/test_sim_001/result")
    assert res_result.status_code == 200
    data = res_result.json()
    assert data["simulation_id"] == "test_sim_001"
    assert "water_depth" in data
    assert "flood_extent" in data

    # 4. Download result format
    res_dl = client.get("/api/simulations/test_sim_001/download/geojson")
    assert res_dl.status_code == 200
    assert res_dl.json()["type"] == "FeatureCollection"
    assert len(res_dl.json()["features"]) > 0
