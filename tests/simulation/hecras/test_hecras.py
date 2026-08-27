"""Unit tests for HEC-RAS 7.0.1 module."""

from pathlib import Path
from src.simulation.hecras.config import (
    HECRASConfig,
    HECRASVersion,
    GeometryConfig,
    BoundaryConfig,
    BoundaryCondition,
    BoundaryType,
    BreachConfig,
    TimeStepConfig,
    load_hecras_config_from_yaml,
)
from src.simulation.hecras.executor import HECRASExecutor
from src.simulation.hecras.output import normalize_to_common_contract


def test_hecras_config_creation(tmp_path):
    dem_file = tmp_path / "test_dem.tif"
    dem_file.touch()

    config = HECRASConfig(
        simulation_id="sim_test_001",
        scenario_id="scenario_rishiganga",
        version=HECRASVersion.V7_0_1,
        geometry=GeometryConfig(
            area_name="Rishiganga_2D",
            cell_size_x=10.0,
            cell_size_y=10.0,
            terrain_raster=dem_file,
        ),
        boundary=BoundaryConfig(
            conditions=[
                BoundaryCondition(
                    name="Inflow",
                    type=BoundaryType.FLOW_HYDROGRAPH,
                    flow_value_m3s=1000.0,
                )
            ]
        ),
        breach=BreachConfig(
            enabled=True,
            breach_center_x=374000.0,
            breach_center_y=3371000.0,
            bottom_width=25.0,
            top_width=50.0,
            crest_level=1900.0,
            formation_time_s=1200.0,
        ),
        timestep=TimeStepConfig(
            computation_interval_s=2.0,
            hydrograph_output_interval_s=60.0,
            mapping_interval_s=60.0,
            simulation_duration_s=3600.0,
        ),
    )

    assert config.simulation_id == "sim_test_001"
    assert config.version == HECRASVersion.V7_0_1
    assert config.geometry.area_name == "Rishiganga_2D"
    assert config.boundary.conditions[0].flow_value_m3s == 1000.0


def test_hecras_executor_preparation(tmp_path):
    dem_file = tmp_path / "test_dem.tif"
    dem_file.touch()

    config = HECRASConfig(
        simulation_id="sim_exec_001",
        scenario_id="scenario_test",
        project_dir=tmp_path / "hec_ras_proj",
        geometry=GeometryConfig(terrain_raster=dem_file),
        boundary=BoundaryConfig(),
        breach=BreachConfig(
            breach_center_x=1.0,
            breach_center_y=2.0,
            bottom_width=10.0,
            top_width=20.0,
            crest_level=100.0,
            formation_time_s=300.0,
        ),
        timestep=TimeStepConfig(),
    )

    executor = HECRASExecutor(config)
    res = executor.run_simulation()

    assert res["status"] in ["ready_for_gui", "success"]
    assert Path(res["project_file"]).exists()


def test_hecras_normalize_contract():
    raw_res = {
        "simulation_id": "hecras_123",
        "scenario_id": "test_scen",
        "max_water_depth_m": 4.85,
        "max_velocity_ms": 12.3,
        "arrival_time_s": 25.0,
    }
    normalized = normalize_to_common_contract(raw_res)

    assert normalized["model"] == "HEC-RAS"
    assert normalized["summary_metrics"]["max_water_depth_m"] == 4.85
    assert normalized["crs"] == "EPSG:32644"


def test_load_yaml_config():
    yaml_path = Path("src/simulation/hecras/config_template.yaml")
    assert yaml_path.exists()
    config = load_hecras_config_from_yaml(yaml_path)
    assert config.project_name == "Rishiganga_Dam_Break"
    assert config.version == HECRASVersion.V7_0_1
