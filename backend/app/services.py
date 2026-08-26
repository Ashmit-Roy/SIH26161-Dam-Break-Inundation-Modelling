import asyncio
import datetime
import uuid
from typing import Dict

from .models import (
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
        model = ModelType(state["model"])

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
            from .models import (
                ComparisonMetric,
                ModelComparisonResult as MCR,
            )

            comparison = MCR(
                metric=ComparisonMetric.WATER_DEPTH,
                sph_data=result_data["water_depth"],
                delft3d_data=result_data.get("comparison_water_depth"),
                timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                overlap_area=state["comparison_data"].get("overlap_area"),
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
    ):
        """Request download of simulation results in real file format."""
        if simulation_id not in _simulation_store:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404, detail="Simulation not found"
            )

        state = _simulation_store[simulation_id]
        valid_formats = ["shp", "kml", "geojson", "json"]
        if format.lower() not in valid_formats:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format: {format}. Must be one of {valid_formats}"
            )

        from fastapi.responses import Response
        import json

        model_name = state.get("model", "SPH")
        poly = [
            [100.42, 6.12],
            [100.38, 6.35],
            [100.55, 6.42],
            [100.62, 6.20],
            [100.42, 6.12],
        ]

        if format.lower() in ["geojson", "json"]:
            geojson_data = {
                "type": "FeatureCollection",
                "name": f"flood_inundation_{simulation_id}",
                "crs": {
                    "type": "name",
                    "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
                },
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [poly],
                        },
                        "properties": {
                            "simulation_id": simulation_id,
                            "model": model_name,
                            "scenario_id": state.get("scenario_id", "scenario_a"),
                            "breach_width_m": state.get("breach_width", 10.0),
                            "breach_height_m": state.get("breach_height", 2.0),
                            "max_water_depth_m": 3.85 if model_name == "SPH" else 4.12,
                            "arrival_time_min": 12.5 if model_name == "SPH" else 11.8,
                            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
                        },
                    }
                ],
            }
            content = json.dumps(geojson_data, indent=2)
            return Response(
                content=content,
                media_type="application/geo+json",
                headers={
                    "Content-Disposition": f"attachment; filename={simulation_id}.geojson",
                    "Access-Control-Expose-Headers": "Content-Disposition",
                },
            )

        elif format.lower() == "kml":
            kml_coords = " ".join([f"{lon},{lat},0" for lon, lat in poly])
            kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Dam Break Flood Inundation - {simulation_id}</name>
    <description>SIH26161 Dam Break Inundation Model Output ({model_name})</description>
    <Style id="floodPoly">
      <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>
      <PolyStyle><color>7f0000ff</color></PolyStyle>
    </Style>
    <Placemark>
      <name>Flood Extent ({model_name})</name>
      <styleUrl>#floodPoly</styleUrl>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>{kml_coords}</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>"""
            return Response(
                content=kml_content,
                media_type="application/vnd.google-earth.kml+xml",
                headers={
                    "Content-Disposition": f"attachment; filename={simulation_id}.kml",
                    "Access-Control-Expose-Headers": "Content-Disposition",
                },
            )

        else:  # shp
            meta_json = json.dumps({
                "message": "Shapefile bundle metadata. Use GeoJSON/KML for web GIS direct import.",
                "simulation_id": simulation_id,
                "format": "Shapefile (.shp)",
                "layers": ["inundation_extent", "depth_contours", "dam_location"],
                "crs": "EPSG:4326",
            }, indent=2)
            return Response(
                content=meta_json,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={simulation_id}_shp_meta.json",
                    "Access-Control-Expose-Headers": "Content-Disposition",
                },
            )


# Setup function to initialize sample data
def setup_sample_data():
    """Initialize sample simulations for testing."""
    now = datetime.datetime.utcnow().isoformat() + "Z"
    
    _simulation_store["sim_sph_001"] = {
        "simulation_id": "sim_sph_001",
        "model": ModelType.SPH.value,
        "scenario_id": "scenario_a",
        "breach_width": 10.0,
        "breach_height": 2.0,
        "status": SimulationStatus.COMPLETED.value,
        "progress": 100.0,
        "created_at": now,
        "updated_at": now,
        "request": {
            "simulation_id": "sim_sph_001",
            "model": ModelType.SPH.value,
            "scenario_id": "scenario_a",
            "breach_width": 10.0,
            "breach_height": 2.0,
        },
        "comparison_data": {
            "overlap_area": 9.5,
        },
    }

    _simulation_store["sim_delft3d_001"] = {
        "simulation_id": "sim_delft3d_001",
        "model": ModelType.DELFT3D.value,
        "scenario_id": "scenario_b",
        "breach_width": 15.0,
        "breach_height": 3.0,
        "status": SimulationStatus.COMPLETED.value,
        "progress": 100.0,
        "created_at": now,
        "updated_at": now,
        "request": {
            "simulation_id": "sim_delft3d_001",
            "model": ModelType.DELFT3D.value,
            "scenario_id": "scenario_b",
            "breach_width": 15.0,
            "breach_height": 3.0,
        },
        "comparison_data": {
            "overlap_area": 9.5,
        },
    }
