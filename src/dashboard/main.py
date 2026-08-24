"""
Dashboard backend — FastAPI entry point.

"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Dam Break Inundation Dashboard API",
    description="Backend for SIH26161 flood simulation dashboard",
    version="0.1.0",
)

# Allow the frontend (running on a different port) to call this API during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before final submission
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """Basic health check so we know the server is alive."""
    return {"status": "ok", "service": "dam-break-dashboard-backend"}


@app.get("/api/scenarios")
def list_scenarios():
    """
    Returns available demo dam/river scenarios for the dropdown.
    DEMO DATA — replace with real scenario list once Data Agent
    finalizes available datasets.
    """
    return {
        "scenarios": [
            {"id": "rishi-ganga", "name": "Rishi Ganga (Uttarakhand, 2021 GLOF)"},
            {"id": "kosi", "name": "Kosi River (Bihar, 2008 breach)"},
        ]
    }


@app.post("/api/simulate")
def run_simulation(scenario_id: str, engine: str = "both"):
    """
    Triggers a simulation run. Currently returns placeholder status.
    DEMO DATA — real version should call SPH/Delft3D pipeline via
    the common simulation output contract (see docs/api-contract.md).
    """
    return {
        "status": "queued",
        "scenario_id": scenario_id,
        "engine": engine,
        "note": "DEMO DATA: real orchestration not yet connected",
    }


@app.get("/api/results/{scenario_id}")
def get_results(scenario_id: str):
    """
    Returns flood extent + damage stats for a completed simulation.
    DEMO DATA — replace with real GeoJSON from GIS Agent's output
    once available.
    """
    return {
        "scenario_id": scenario_id,
        "flood_extent_geojson": {
            "type": "FeatureCollection",
            "features": [],  # placeholder — real polygons come from src/gis/
        },
        "damage_summary": {
            "population_affected": None,
            "area_flooded_km2": None,
            "roads_affected_km": None,
            "note": "DEMO DATA: not yet computed",
        },
    }