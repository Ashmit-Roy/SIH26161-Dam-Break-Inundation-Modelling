"""HEC-RAS 7.0.1 simulation configuration models."""

from enum import Enum
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class HECRASVersion(str, Enum):
    V7_0_1 = "7.0.1"
    V6_4_0 = "6.4.0"


class GeometryConfig(BaseModel):
    """HEC-RAS 2D Flow Area & Mesh configuration."""

    area_name: str = Field("Rishiganga_2D", description="2D Flow Area Name in RAS Mapper")
    cell_size_x: float = Field(10.0, gt=0, description="Mesh cell size X (m)")
    cell_size_y: float = Field(10.0, gt=0, description="Mesh cell size Y (m)")
    terrain_raster: Path = Field(..., description="Path to input DEM raster (.tif)")
    friction_manning_n: float = Field(0.035, gt=0, description="Default Manning's n roughness")

    @field_validator("terrain_raster", mode="before")
    @classmethod
    def resolve_path(cls, v):
        if v is not None:
            return Path(v)
        return v


class BoundaryType(str, Enum):
    FLOW_HYDROGRAPH = "flow_hydrograph"
    STAGE_HYDROGRAPH = "stage_hydrograph"
    NORMAL_DEPTH = "normal_depth"
    RATING_CURVE = "rating_curve"


class BoundaryCondition(BaseModel):
    """HEC-RAS 2D Boundary condition definition."""

    name: str = Field(..., description="BC line name")
    type: BoundaryType = Field(..., description="BC type")
    flow_value_m3s: Optional[float] = Field(None, description="Peak discharge flow (m3/s)")
    friction_slope: Optional[float] = Field(0.02, gt=0, description="Normal depth friction slope (m/m)")
    hydrograph_file: Optional[Path] = Field(None, description="Optional external hydrograph file")


class BoundaryConfig(BaseModel):
    """Collection of boundary conditions for HEC-RAS simulation."""

    conditions: list[BoundaryCondition] = Field(default_factory=list)


class BreachConfig(BaseModel):
    """Dam breach geometry and formation parameters."""

    enabled: bool = Field(True, description="Enable dam breach in simulation")
    breach_center_x: float = Field(..., description="Breach center UTM X coordinate")
    breach_center_y: float = Field(..., description="Breach center UTM Y coordinate")
    bottom_width: float = Field(..., gt=0, description="Final breach bottom width (m)")
    top_width: float = Field(..., gt=0, description="Final breach top width (m)")
    crest_level: float = Field(..., description="Breach crest level elevation (m)")
    formation_time_s: float = Field(..., gt=0, description="Breach development time (seconds)")
    side_slope: float = Field(1.0, gt=0, description="Side slope H:V")


class TimeStepConfig(BaseModel):
    """HEC-RAS Unsteady analysis time step controls."""

    computation_interval_s: float = Field(2.0, gt=0, description="Computation time step (seconds)")
    hydrograph_output_interval_s: float = Field(60.0, gt=0, description="Hydrograph output interval (seconds)")
    mapping_interval_s: float = Field(60.0, gt=0, description="RAS Mapper spatial output interval (seconds)")
    simulation_duration_s: float = Field(7200.0, gt=0, description="Total simulation duration (seconds)")


class OutputConfig(BaseModel):
    """HEC-RAS output export parameters."""

    output_dir: Path = Field(Path("data/hecras_output"), description="Directory to save exported results")
    export_water_depth_tif: bool = Field(True, description="Export max water depth raster (.tif)")
    export_flood_extent_geojson: bool = Field(True, description="Export flood extent polygon (.geojson)")
    export_velocity_tif: bool = Field(True, description="Export max velocity raster (.tif)")

    @field_validator("output_dir", mode="before")
    @classmethod
    def resolve_path(cls, v):
        return Path(v)


class HECRASConfig(BaseModel):
    """Complete HEC-RAS 7.0.1 Dam-Break Simulation Configuration."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    simulation_id: str = Field(..., description="Unique simulation ID")
    scenario_id: str = Field(..., description="Scenario identifier")
    version: HECRASVersion = Field(HECRASVersion.V7_0_1, description="HEC-RAS version")
    project_name: str = Field("Rishiganga_Dam_Break", description="HEC-RAS project title")
    project_dir: Path = Field(Path("hec_ras"), description="Directory containing .prj, .g01, .p01 files")

    geometry: GeometryConfig
    boundary: BoundaryConfig
    breach: BreachConfig
    timestep: TimeStepConfig
    output: OutputConfig = Field(default_factory=OutputConfig)

    crs: str = Field("EPSG:32644", description="Coordinate Reference System (UTM Zone 44N)")


def load_hecras_config_from_yaml(path: str | Path) -> HECRASConfig:
    """Load HECRASConfig from a YAML file."""
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return HECRASConfig(**data)
