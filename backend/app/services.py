import asyncio
import datetime
import uuid
from typing import Dict

from backend.app.models import (
    DamageStatistics,
    FloodExtentResult,
    ModelType,
    SimulationMetadata,
    SimulationRequest,
    SimulationResultResponse,
    SimulationStatus,
    SimulationStatusResponse,
    WaterDepthResult,
)

# In-memory simulation state (replace with DB in production)
_simulation_store: Dict[str, Dict] = {}


class MockSPHExecution:
    """Mock SPH (Smoothed Particle Hydrodynamics) simulation execution."""

    @staticmethod
    async def execute(request: SimulationRequest) -> Dict:
        """Execute mock SPH simulation and return results."""
        await asyncio.sleep(1.0)  # Simulate computation time

        # Mock water depth result
        water_depth = WaterDepthResult(
            simulation_id=request.simulation_id,
            location={"lat": 6.2, "lon": 100.5},
            water_depth=3.85,
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        )

        # Mock flood extent polygon (GeoJSON-like)
        flood_extent = FloodExtentResult(
            simulation_id=request.simulation_id,
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

        # Mock metadata
        metadata = SimulationMetadata(
            terrain_reference="DEM: SRTM 30m",
            dam_location={"lat": 6.2, "lon": 100.5},
            initial_water_level=5.0,
        )

        return {
            "water_depth": water_depth,
            "flood_extent": flood_extent,
            "metadata": metadata,
            "model": "SPH",
            "source": "DualSPHysics v6.4",
        }


class MockDelft3DExecution:
    """Mock Delft3D FM flexible mesh simulation execution."""

    @staticmethod
    async def execute(request: SimulationRequest) -> Dict:
        """Execute mock Delft3D simulation and return results."""
        await asyncio.sleep(1.2)  # Simulate computation time

        # Mock water depth result
        water_depth = WaterDepthResult(
            simulation_id=request.simulation_id,
            location={"lat": 6.2, "lon": 100.5},
            water_depth=4.12,
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        )

        # Mock flood extent polygon (slightly different shape)
        flood_extent = FloodExtentResult(
            simulation_id=request.simulation_id,
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

        # Mock metadata
        metadata = SimulationMetadata(
            terrain_reference="DEM: SRTM 30m",
            dam_location={"lat": 6.2, "lon": 100.5},
            initial_water_level=5.0,
        )

        return {
            "water_depth": water_depth,
            "flood_extent": flood_extent,
            "metadata": metadata,
            "model": "Delft3D",
            "source": "Delft3D FM Flexible Mesh",
        }


class SimulationService:
    """Service layer for simulation orchestration."""

    @staticmethod
    def create_simulation_id() -> str:
        """Generate a unique simulation ID."""
        return f"sim_{uuid.uuid4().hex[:8]}"

    @staticmethod
    async def start_simulation(request: SimulationRequest) -> SimulationStatusResponse:
        """Start a new simulation.

        Validates the request, creates a simulation ID,
        and returns initial status.
        """
        # Validate request
        if not request.simulation_id or not request.simulation_id.strip():
            raise ValueError("simulation_id is required")

        if request.model not in [ModelType.SPH, ModelType.DELFT3D]:
            raise ValueError(
                f"Invalid model type: {request.model}. Must be SPH or Delft3D."
            )

        if not request.scenario_id or not request.scenario_id.strip():
            raise ValueError("scenario_id is required")

        # Create simulation ID if not provided
        sim_id = (
                    request.simulation_id
                    if request.simulation_id
                    else SimulationService.create_simulation_id()
                )

        # Store initial state
        _simulation_store[sim_id] = {
            "simulation_id": sim_id,
            "model": request.model,
            "scenario_id": request.scenario_id,
            "breach_width": request.breach_width,
            "breach_height": request.breach_height,
            "status": SimulationStatus.QUEUED,
            "progress": 0.0,
            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "request": request.dict(),
        }

        return SimulationStatusResponse(
            simulation_id=sim_id,
            status=SimulationStatus.QUEUED,
            progress=0.0,
            updated_at=_simulation_store[sim_id]["updated_at"],
        )

    @staticmethod
    async def get_simulation_status(simulation_id: str) -> SimulationStatusResponse:
        """Get simulation status by ID."""
        if simulation_id not in _simulation_store:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404, detail="Simulation not found"
            )

        state = _simulation_store[simulation_id]

        # Simulate progress update based on time
        # In production, this would check real computation progress
        progress = state["progress"]
        status = SimulationStatus(state["status"])

        # Simulate lifecycle if still queued/running
        if state["status"] == SimulationStatus.QUEUED.value:
            # 50% chance to move to running after check
            import random
            if random.random() > 0.5:
                state["status"] = SimulationStatus.RUNNING.value
                progress = 10.0
        elif state["status"] == SimulationStatus.RUNNING.value:
            # Simulate progress from 10% to 100% over "time"
            progress = min(progress + 15, 90.0)
            if progress >= 90.0:
                state["status"] = SimulationStatus.COMPLETED.value
                progress = 100.0

        state["progress"] = progress
        state["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"

        return SimulationStatusResponse(
            simulation_id=simulation_id,
            status=status,
            progress=progress,
            updated_at=state["updated_at"],
        )

    @staticmethod
    async def get_simulation_result(simulation_id: str) -> SimulationResultResponse:
        """Get full simulation result by ID."""
        if simulation_id not in _simulation_store:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404, detail="Simulation not found"
            )

        state = _simulation_store[simulation_id]
        from backend.app.models import Model as ModelEnum

        model = ModelEnum(state["model"])

        # Execute appropriate mock model
        if model == ModelType.SPH:
            result_data = await MockSPHExecution.execute(
                SimulationRequest(
                    simulation_id=simulation_id,
                    model=ModelType.SPH,
                    scenario_id=state["scenario_id"],
                    breach_width=state["breach_width"],
                    breach_height=state["breach_height"],
                )
            )
        elif model == ModelType.DELFT3D:
            result_data = await MockDelft3DExecution.execute(
                SimulationRequest(
                    simulation_id=simulation_id,
                    model=ModelType.DELFT3D,
                    scenario_id=state["scenario_id"],
                    breach_width=state["breach_width"],
                    breach_height=state["breach_height"],
                )
            )
        else:
            raise ValueError(f"Unknown model type: {model}")

        # Build comparison if both models available
        comparison = None
        if state.get("comparison_data"):
            from backend.app.models import (
                ComparisonMetric,
            )
            from backend.app.models import (
                ModelComparisonResult as MCR,
            )

            comparison = MCR(
                metric=ComparisonMetric.WATER_DEPTH,
                sph_data=result_data["water_depth"],
                delft3d_data=result_data.get("comparison_water_depth"),
                timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                overlap_area=state["comparison_data"].get("overlap_area"),
            )

        # Build damage statistics
        return DamageStatistics(
            population_affected=1250,
            population_at_risk=3400,
            residential_units_destroyed=89,
            residential_units_damaged=234,
            road_km_affected=15.3,
            bridge_count_affected=2,
            land_area_flooded_km2=8.7,
            evacuation_centers_needed=3,
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        )

        return SimulationResultResponse(
            simulation_id=simulation_id,
            model=model,
            scenario_id=state["scenario_id"],
            breach_width=state["breach_width"],
            breach_height=state["breach_height"],
            water_depth=result_data["water_depth"],
            flood_extent=result_data["flood_extent"],
            comparison=comparison,
            metadata=result_data["metadata"],
            created_at=state["created_at"],
            completed_at=datetime.datetime.utcnow().isoformat() + "Z",
        )

    @staticmethod
    async def download_result(
        simulation_id: str, format: str
    ) -> Dict:
        """Request download of simulation results."""
        if simulation_id not in _simulation_store:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404, detail="Simulation not found"
            )

        valid_formats = ["shp", "kml", "geojson"]
        if format.lower() not in valid_formats:
            raise ValueError(
                f"Invalid format: {format}. Must be one of {valid_formats}"
            )

        filename = f"{simulation_id}.{format}"

        return {
            "success": True,
            "simulation_id": simulation_id,
            "format": format,
            "filename": filename,
            "message": f"Download ready for {simulation_id} in {format} format",
        }


# Setup function to initialize sample data
def setup_sample_data():
    """Initialize sample simulations for testing."""

    # Create a SPH simulation
    from backend.app.models import ModelType, SimulationRequest

    sph_request = SimulationRequest(
        simulation_id="sim_sph_001",
        model=ModelType.SPH,
        scenario_id="scenario_a",
        breach_width=10.0,
        breach_height=2.0,
    )

    sph_status = asyncio.run(SimulationService.start_simulation(sph_request))

    # Advance to completed status
    for _ in range(10):
        status = asyncio.run(SimulationService.get_simulation_status(sph_status.simulation_id))
        if status.status.name == "COMPLETED":
            break

    # Create a Delft3D simulation
    delft_request = SimulationRequest(
        simulation_id="sim_delft3d_001",
        model=ModelType.DELFT3D,
        scenario_id="scenario_b",
        breach_width=15.0,
        breach_height=3.0,
    )

    delft_status = asyncio.run(SimulationService.start_simulation(delft_request))

    # Advance to completed status
    for _ in range(10):
        status = asyncio.run(SimulationService.get_simulation_status(delft_status.simulation_id))
        if status.status.name == "COMPLETED":
            break

    # Add comparison data
    _simulation_store[sph_status.simulation_id]["comparison_data"] = {
        "overlap_area": 9.5,
    }
    _simulation_store[delft_status.simulation_id]["comparison_data"] = {
        "overlap_area": 9.5,
    }
