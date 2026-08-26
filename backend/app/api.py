from backend.app.models import (
    SimulationRequest,
    SimulationResultResponse,
    SimulationStatusResponse,
)
from backend.app.services import SimulationService
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["simulation"])


@router.post("/simulations", response_model=SimulationStatusResponse)
async def create_simulation(request: SimulationRequest):
    """Start a new hydrodynamic simulation."""
    return await SimulationService.start_simulation(request)


@router.get("/simulations/{simulation_id}/status", response_model=SimulationStatusResponse)
async def get_simulation_status(simulation_id: str):
    """Check simulation progress status."""
    return await SimulationService.get_simulation_status(simulation_id)


@router.get("/simulations/{simulation_id}/result", response_model=SimulationResultResponse)
async def get_simulation_result(simulation_id: str):
    """Get full simulation result by ID."""
    return await SimulationService.get_simulation_result(simulation_id)


@router.get("/simulations/{simulation_id}/download/{format}")
async def download_simulation(simulation_id: str, format: str):
    """Download simulation results in specified format."""
    return await SimulationService.download_result(simulation_id, format.lower())
