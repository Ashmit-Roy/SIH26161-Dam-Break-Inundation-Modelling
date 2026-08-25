from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..models import (
    SimulationRequest,
    SimulationMetadata,
    WaterDepthResult,
    FloodExtentResult,
    ComparisonResult,
    DownloadRequest,
    DashboardState,
    ModelType,
    ComparisonMetric,
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

    # TODO: Integrate with actual SPH/Delft3D execution
    # For now, simulate immediate completion
    _simulation_results[request.simulation_id] = {
        "model": request.model,
        "status": "completed",
        "request": request.dict(),
    }

    return request


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