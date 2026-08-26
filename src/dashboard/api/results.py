from fastapi import APIRouter, HTTPException

from ..models import (
    ComparisonMetric,
    ComparisonResult,
    DownloadRequest,
    FloodExtentResult,
    ModelType,
    WaterDepthResult,
)
from ..simulation import _simulation_results

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


@router.get("/comparison/{simulation_id}", response_model=ComparisonResult)
async def get_comparison_metrics(simulation_id: str):
    """Get comparison metrics between SPH and Delft3D results."""
    if simulation_id not in _simulation_results:
        raise HTTPException(status_code=404, detail="Simulation not found")
    result = _simulation_results[simulation_id]
    model = result.get("model", ModelType.SPH)
    sph_data = None
    delft3d_data = None
    if model == ModelType.SPH or model.value == "both":
        sph_data = WaterDepthResult(
            simulation_id=simulation_id,
            location={"lat": 6.2, "lon": 100.5},
            water_depth=3.85,
        )
    if model == ModelType.DELFT3D or model.value == "both":
        delft3d_data = WaterDepthResult(
            simulation_id=simulation_id,
            location={"lat": 6.2, "lon": 100.5},
            water_depth=4.12,
        )
    if sph_data is None and delft3d_data is None:
        sph_data = WaterDepthResult(
            simulation_id=simulation_id,
            location={"lat": 6.2, "lon": 100.5},
            water_depth=0.0,
        )
    return ComparisonResult(
        metric=ComparisonMetric.WATER_DEPTH,
        sph_data=sph_data,
        delft3d_data=delft3d_data,
        timestamp=result.get("request", {}).get("timestamp", ""),
    )
