from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ModelType(str, Enum):
    SPH = "SPH"
    HECRAS = "HEC-RAS"


class ComparisonMetric(str, Enum):
    FLOOD_EXTENT = "flood_extent"
    WATER_DEPTH = "water_depth"
    ARRIVAL_TIME = "arrival_time"
    COMPUTATIONAL_TIME = "computational_time"


class SimulationRequest(BaseModel):
    simulation_id: str = Field(..., description="Unique simulation identifier")
    model: ModelType = Field(..., description="Hydraulic model: SPH or HEC-RAS")
    scenario_id: str = Field(..., description="Scenario identifier")
    breach_width: Optional[float] = Field(None, description="Breach width in meters")
    breach_height: Optional[float] = Field(None, description="Breach height in meters")
    simulation_time: Optional[float] = Field(None, description="Simulation time in seconds")
    crs: Optional[str] = Field("EPSG:4326", description="Coordinate reference system")


class SimulationMetadata(BaseModel):
    terrain_reference: Optional[str] = Field(None, description="DEM reference")
    dam_location: Optional[Dict[str, float]] = Field(None, description="Dam location lat/lon")
    initial_water_level: Optional[float] = Field(None, description="Initial water level in meters")


class WaterDepthResult(BaseModel):
    simulation_id: str
    location: Dict[str, float] = Field(..., description="Location lat/lon")
    water_depth: float = Field(..., description="Water depth in meters")
    timestamp: Optional[str] = Field(None, description="ISO8601 timestamp")


class FloodExtentResult(BaseModel):
    simulation_id: str
    polygon: Dict[str, Any] = Field(..., description="GeoJSON polygon geometry")
    arrival_time: Optional[float] = Field(None, description="Arrival time in seconds")


class ComparisonResult(BaseModel):
    metric: ComparisonMetric
    sph_data: Optional[WaterDepthResult] = Field(None, description="SPH result data")
    delft3d_data: Optional[WaterDepthResult] = Field(None, description="Delft3D result data")
    timestamp: str = Field(..., description="Comparison timestamp")


class DownloadRequest(BaseModel):
    format: str = Field(..., description="Output format: shp, kml, geojson")
    simulation_id: str = Field(..., description="Simulation to download")
    crs: Optional[str] = Field("EPSG:4326", description="Target CRS")


class DashboardState(BaseModel):
    current_simulation: Optional[str] = Field(None, description="Active simulation ID")
    simulation_progress: float = Field(0.0, description="Progress 0-100%")
    comparison_active: bool = Field(False, description="Whether comparison is running")
    last_update: str = Field(
        default_factory=lambda: __import__("datetime").datetime.utcnow().isoformat() + "Z"
    )
