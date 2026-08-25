from ..src.dashboard.models import (
    SimulationRequest,
    SimulationMetadata,
    ModelType,
    ComparisonMetric,
    WaterDepthResult,
    FloodExtentResult,
    ComparisonResult,
    DownloadRequest,
    DashboardState,
)


def test_simulation_request():
    req = SimulationRequest(
        simulation_id="test_001",
        model=ModelType.SPH,
        scenario_id="scenario_a",
        breach_width=10.0,
        breach_height=2.0,
    )
    assert req.simulation_id == "test_001"
    assert req.model == ModelType.SPH
    assert req.scenario_id == "scenario_a"


def test_model_type_enum():
    assert ModelType.SPH.value == "SPH"
    assert ModelType.DELFT3D.value == "Delft3D"


def test_comparison_metric_enum():
    assert ComparisonMetric.FLOOD_EXTENT.value == "flood_extent"
    assert ComparisonMetric.WATER_DEPTH.value == "water_depth"


def test_water_depth_result():
    result = WaterDepthResult(
        simulation_id="test_001",
        location={"lat": 6.2, "lon": 100.5},
        water_depth=3.5,
    )
    assert result.simulation_id == "test_001"
    assert result.water_depth == 3.5


def test_flood_extent_result():
    result = FloodExtentResult(
        simulation_id="test_001",
        polygon={"type": "Polygon", "coordinates": []},
    )
    assert result.simulation_id == "test_001"


def test_download_request():
    req = DownloadRequest(format="geojson", simulation_id="test_001")
    assert req.format == "geojson"
    assert req.simulation_id == "test_001"


def test_dashboard_state():
    state = DashboardState()
    assert state.simulation_progress == 0.0
    assert state.comparison_active == False