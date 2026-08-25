from fastapi import APIRouter, HTTPException, Response
from ..models import DownloadRequest, WaterDepthResult, FloodExtentResult

router = APIRouter(prefix="/results", tags=["results"])


@router.post("/download")
async def download_results(request: DownloadRequest):
    """Download simulation results in specified format."""
    # TODO: Actually generate and return file in requested format
    # For now, return placeholder JSON
    return {
        "status": "placeholder",
        "message": f"Download in {request.format} format for {request.simulation_id}",
        "format": request.format,
        "simulation_id": request.simulation_id,
        "crs": request.crs,
    }


@router.get("/{simulation_id}/depth", response_model=WaterDepthResult)
async def get_water_depth(simulation_id: str):
    """Get water depth result for a simulation."""
    if simulation_id not in _simulation_results:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return WaterDepthResult(
        simulation_id=simulation_id,
        location={"lat": 0, "lon": 0},
        water_depth=0.0,
    )


@router.get("/{simulation_id}/extent", response_model=FloodExtentResult)
async def get_flood_extent(simulation_id: str):
    """Get flood extent result for a simulation."""
    if simulation_id not in _simulation_results:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return FloodExtentResult(
        simulation_id=simulation_id,
        polygon={"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]},
    )