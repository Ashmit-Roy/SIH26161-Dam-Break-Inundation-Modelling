import asyncio
import datetime
from typing import Dict

from fastapi import APIRouter, HTTPException

from ..models import (
    DashboardState,
    FloodExtentResult,
    ModelType,
    SimulationRequest,
    WaterDepthResult,
)

router = APIRouter(prefix="/simulation", tags=["simulation"])

# In-memory state for dashboard (replace with DB in production)
_dashboard_state = DashboardState()
_simulation_results: Dict[str, Dict] = {}


@router.post("/start", response_model=SimulationRequest)
async def start_simulation(request: SimulationRequest):
    """Start a hydrodynamic simulation (SPH or Delft3D)."""
    _dashboard_state.current_simulation = request.simulation_id
    _dashboard_state.simulation_progress = 0.0

    # TODO: Integrate with actual SPH/Delft3D execution (DualSPHysics / Delft3D FM)
    # For now, simulate simulation pipeline with realistic timing
    _simulation_results[request.simulation_id] = {
        "model": request.model,
        "status": "running",
        "request": request.dict(),
        "progress": 0.0,
    }

    # Simulate asynchronous execution

    asyncio.create_task(_run_simulation_async(request.simulation_id, request.model))

    return request


async def _run_simulation_async(simulation_id: str, model: ModelType):
    """Simulate the hydrodynamic simulation execution."""
    await asyncio.sleep(1.0)  # Simulate computation time

    _simulation_results[simulation_id]["status"] = "completed"
    _simulation_results[simulation_id]["progress"] = 100.0

    # Generate mock results based on model type

    now = datetime.datetime.utcnow().isoformat() + "Z"

    if model == ModelType.SPH:
        _simulation_results[simulation_id]["water_depth"] = WaterDepthResult(
            simulation_id=simulation_id,
            location={"lat": 6.2, "lon": 100.5},
            water_depth=3.85,
            timestamp=now,
        )
        _simulation_results[simulation_id]["flood_extent"] = FloodExtentResult(
            simulation_id=simulation_id,
            polygon={
                "type": "Polygon",
                "coordinates": [
                    [6.12, 100.42],
                    [6.35, 100.38],
                    [6.42, 100.55],
                    [6.20, 100.62],
                    [6.12, 100.42],
                ],
            },
            arrival_time=12.5,
        )
    elif model == ModelType.DELFT3D:
        _simulation_results[simulation_id]["water_depth"] = WaterDepthResult(
            simulation_id=simulation_id,
            location={"lat": 6.2, "lon": 100.5},
            water_depth=4.12,
            timestamp=now,
        )
        _simulation_results[simulation_id]["flood_extent"] = FloodExtentResult(
            simulation_id=simulation_id,
            polygon={
                "type": "Polygon",
                "coordinates": [
                    [6.10, 100.40],
                    [6.40, 100.35],
                    [6.48, 100.58],
                    [6.18, 100.65],
                    [6.10, 100.40],
                ],
            },
            arrival_time=11.8,
        )
    else:
        _simulation_results[simulation_id]["water_depth"] = WaterDepthResult(
            simulation_id=simulation_id,
            location={"lat": 6.2, "lon": 100.5},
            water_depth=3.95,
            timestamp=now,
        )
        _simulation_results[simulation_id]["flood_extent"] = FloodExtentResult(
            simulation_id=simulation_id,
            polygon={
                "type": "Polygon",
                "coordinates": [
                    [6.15, 100.43],
                    [6.30, 100.40],
                    [6.35, 100.50],
                    [6.18, 100.55],
                    [6.15, 100.43],
                ],
            },
            arrival_time=12.1,
        )


@router.post("/status/{simulation_id}")
async def simulation_status(simulation_id: str):
    """Check simulation progress status."""
    if simulation_id not in _simulation_results:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return _simulation_results[simulation_id]


@router.get("/state", response_model=DashboardState)
async def dashboard_state():
    """Get current dashboard state."""
    return _dashboard_state


@router.post("/state", response_model=DashboardState)
async def update_dashboard_state(state: DashboardState):
    """Update dashboard state."""
    _dashboard_state.__dict__.update(state.dict(exclude_unset=True))
    return _dashboard_state
