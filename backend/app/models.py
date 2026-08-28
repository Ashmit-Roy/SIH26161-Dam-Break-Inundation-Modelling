from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ModelType(str, Enum):
    SPH = "SPH"
    HECRAS = "HEC-RAS"
    HECRAS_2D = "HEC-RAS 2D"
    DELFT3D = "Delft3D"
    BOTH = "both"


class ComparisonMetric(str, Enum):
    FLOOD_EXTENT = "flood_extent"
    WATER_DEPTH = "water_depth"
    ARRIVAL_TIME = "arrival_time"
    COMPUTATIONAL_TIME = "computational_time"


class SimulationStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


# Request/Response Models

class SimulationRequest(BaseModel):
    simulation_id: Optional[str] = Field(None, description="Unique simulation identifier")
    model: Optional[ModelType] = Field(None, description="Hydraulic model: SPH or HEC-RAS")
    model_type: Optional[str] = Field(None, description="Model type alias string")
    scenario_id: Optional[str] = Field("scenario_a", description="Scenario identifier")
    river_dam: Optional[str] = Field("rishiganga", description="River or dam reach key (rishiganga, chamoli, tehri, mullaperiyar)")
    breach_width: Optional[float] = Field(15.0, description="Breach width in meters")
    breach_height: Optional[float] = Field(3.0, description="Breach height in meters")
    simulation_time: Optional[float] = Field(60.0, description="Simulation time in seconds")
    simulation_time_min: Optional[float] = Field(None, description="Simulation time in minutes")
    crs: Optional[str] = Field("EPSG:4326", description="Coordinate reference system")


class SimulationMetadata(BaseModel):
    terrain_reference: Optional[str] = Field(None, description="DEM reference")
    dam_location: Optional[Dict[str, float]] = Field(
        None, description="Dam location {lat, lon}"
    )
    initial_water_level: Optional[float] = Field(None, description="Initial water level in meters")


# Water Depth Result

class WaterDepthResult(BaseModel):
    simulation_id: str = Field(..., description="Simulation ID")
    location: Dict[str, float] = Field(
        ..., description="Location {lat, lon} in decimal degrees"
    )
    water_depth: float = Field(..., description="Water depth in meters")
    timestamp: Optional[str] = Field(None, description="ISO8601 timestamp")


# Flood Extent Result

class FloodExtentResult(BaseModel):
    simulation_id: str = Field(..., description="Simulation ID")
    polygon: Dict[str, Any] = Field(
        ..., description="GeoJSON polygon geometry"
    )
    arrival_time: Optional[float] = Field(
        None, description="Arrival time in seconds"
    )


# Model Comparison Result

class ModelComparisonResult(BaseModel):
    metric: ComparisonMetric = Field(..., description="Comparison metric")
    sph_data: Optional[WaterDepthResult] = Field(
        None, description="SPH result data"
    )
    hecras_data: Optional[WaterDepthResult] = Field(
        None, description="HEC-RAS result data"
    )
    delft3d_data: Optional[WaterDepthResult] = Field(
        None, description="Delft3D result data"
    )
    timestamp: str = Field(..., description="Comparison timestamp")
    overlap_area: Optional[float] = Field(
        None, description="Overlapping area in m² (optional)"
    )


# Damage Statistics

class DamageStatistics(BaseModel):
    population_affected: int = Field(
        ..., description="Number of people affected"
    )
    population_at_risk: int = Field(
        ..., description="Number of people at risk"
    )
    residential_units_destroyed: int = Field(
        ..., description="Number of residential units destroyed"
    )
    residential_units_damaged: int = Field(
        ..., description="Number of residential units damaged"
    )
    road_km_affected: float = Field(
        ..., description="Road length affected in kilometers"
    )
    bridge_count_affected: int = Field(
        ..., description="Number of bridges affected"
    )
    land_area_flooded_km2: float = Field(
        ..., description="Land area flooded in square kilometers"
    )
    evacuation_centers_needed: int = Field(
        ..., description="Number of evacuation centers needed"
    )
    timestamp: str = Field(
        ..., description="Timestamp of analysis"
    )


# Downloadable Output Format

class DownloadRequest(BaseModel):
    format: str = Field(
        ..., description="Output format: shp, kml, geojson"
    )
    simulation_id: str = Field(..., description="Simulation to download")
    crs: Optional[str] = Field(
        "EPSG:4326", description="Target CRS"
    )


# API Response Models

class SimulationStatusResponse(BaseModel):
    simulation_id: str = Field(..., description="Simulation ID")
    status: SimulationStatus = Field(..., description="Current status")
    progress: float = Field(
        0.0, description="Progress percentage 0-100"
    )
    updated_at: str = Field(
        ..., description="ISO8601 timestamp of last update"
    )
    result_summary: Optional[Dict[str, Any]] = Field(
        None, description="Computed hydrodynamic physics summary (Peak Velocity, Discharge, PAR)"
    )
    result_url: Optional[str] = Field(
        None, description="Direct URL to fetch full GeoJSON polygon & SPH results"
    )


class SimulationResultResponse(BaseModel):
    simulation_id: str = Field(..., description="Simulation ID")
    model: ModelType = Field(..., description="Hydraulic model")
    scenario_id: str = Field(..., description="Scenario identifier")
    breach_width: Optional[float] = Field(None, description="Breach width")
    breach_height: Optional[float] = Field(None, description="Breach height")
    water_depth: WaterDepthResult = Field(
        ..., description="Water depth result"
    )
    flood_extent: FloodExtentResult = Field(
        ..., description="Flood extent polygon"
    )
    comparison: Optional[ModelComparisonResult] = Field(
        None, description="SPH vs Delft3D comparison (if model is 'both')"
    )
    metadata: SimulationMetadata = Field(
        ..., description="Simulation metadata"
    )
    created_at: str = Field(
        ..., description="ISO8601 timestamp of creation"
    )
    completed_at: Optional[str] = Field(
        None, description="ISO8601 timestamp of completion"
    )


class DownloadResponse(BaseModel):
    success: bool = Field(..., description="Whether download was initiated")
    simulation_id: str = Field(..., description="Simulation ID")
    format: str = Field(..., description="Requested format")
    filename: str = Field(
        ..., description="Suggested filename including extension"
    )
    file_size: Optional[int] = Field(
        None, description="File size in bytes (if available)"
    )
