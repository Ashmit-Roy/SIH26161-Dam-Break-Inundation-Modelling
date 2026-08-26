"""
Unit tests for GIS data processing and hydrodynamic dam-break inundation module.
"""

import geopandas as gpd
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_bounds
from shapely.geometry import Point, Polygon
from src.gis.dam_break_hydraulic import (
    categorize_hazard_zones,
    simulate_dam_break_inundation,
)
from src.gis.dem_preprocessing import (
    calculate_d8_flow_direction,
    calculate_flow_accumulation,
    calculate_slope_and_aspect,
    generate_hillshade,
)
from src.gis.output import load_vector, save_vector
from src.gis.raster import get_raster_info
from src.gis.validation import validate_raster, validate_vector


@pytest.fixture
def sample_dem_raster(tmp_path):
    """Create a temporary synthetic GeoTIFF DEM for testing."""
    raster_path = tmp_path / "test_dem.tif"
    width, height = 50, 50
    transform = from_bounds(1000.0, 1000.0, 2500.0, 2500.0, width, height)

    # Elevation ramp
    elevation = np.linspace(2000.0, 1500.0, height)[:, None] * np.ones((1, width))
    elevation = elevation.astype(np.float32)

    profile = {
        "driver": "GTiff",
        "dtype": "float32",
        "nodata": -9999.0,
        "width": width,
        "height": height,
        "count": 1,
        "crs": "EPSG:32644",
        "transform": transform,
    }

    with rasterio.open(raster_path, "w", **profile) as dst:
        dst.write(elevation, 1)

    return raster_path


def test_validate_raster(sample_dem_raster):
    """Test validation of valid and invalid rasters."""
    res = validate_raster(sample_dem_raster)
    assert res["valid"] is True
    assert res["width"] == 50
    assert res["height"] == 50
    assert "EPSG:32644" in res["crs"]

    invalid = validate_raster("non_existent_raster.tif")
    assert invalid["valid"] is False


def test_get_raster_info(sample_dem_raster):
    """Test get_raster_info metadata extractor."""
    info = get_raster_info(str(sample_dem_raster))
    assert info["bands"] == 1
    assert info["dtype"] == "float32"
    assert info["nodata"] == -9999.0


def test_dem_preprocessing_functions():
    """Test slope, aspect, hillshade, and D8 calculations."""
    elev = np.array(
        [
            [100.0, 90.0, 80.0],
            [95.0, 85.0, 75.0],
            [90.0, 80.0, 70.0],
        ],
        dtype=np.float32,
    )

    slope, aspect = calculate_slope_and_aspect(elev, 10.0, 10.0)
    assert slope.shape == (3, 3)
    assert aspect.shape == (3, 3)
    assert np.all(slope >= 0.0)

    hillshade = generate_hillshade(elev, 10.0, 10.0)
    assert hillshade.shape == (3, 3)
    assert hillshade.dtype == np.uint8

    fdir = calculate_d8_flow_direction(elev)
    assert fdir.shape == (3, 3)

    facc = calculate_flow_accumulation(fdir)
    assert facc.shape == (3, 3)


def test_vector_io_and_validation(tmp_path):
    """Test vector saving, loading, and validation."""
    gdf = gpd.GeoDataFrame(
        {"id": [1, 2], "name": ["Dam A", "Dam B"]},
        geometry=[Point(79.6, 30.5), Point(79.7, 30.4)],
        crs="EPSG:4326",
    )

    out_geojson = tmp_path / "test_dams.geojson"
    out_gpkg = tmp_path / "test_dams.gpkg"
    out_shp = tmp_path / "test_dams.shp"

    save_vector(gdf, str(out_geojson))
    save_vector(gdf, str(out_gpkg))
    save_vector(gdf, str(out_shp))

    loaded = load_vector(str(out_geojson))
    assert len(loaded) == 2
    assert "name" in loaded.columns

    valid_res = validate_vector(out_geojson)
    assert valid_res["valid"] is True


def test_hydrodynamic_simulation(sample_dem_raster):
    """Test dam break hydrodynamic inundation simulation engine."""
    results = simulate_dam_break_inundation(
        dem_path=sample_dem_raster,
        breach_coords=(1750.0, 2200.0),
        breach_discharge_peak=5000.0,
        reservoir_volume_m3=1.0e6,
        breach_duration_sec=600.0,
        min_depth_threshold=0.10,
    )

    assert "max_depth" in results
    assert "max_velocity" in results
    assert "hazard_index" in results
    assert results["max_depth"].shape == (50, 50)
    assert np.max(results["max_depth"]) > 0.0

    # Categorize hazard
    mask = results["max_depth"] >= 0.10
    haz_zones = categorize_hazard_zones(results["hazard_index"], mask)
    assert haz_zones.shape == (50, 50)


def test_damage_analysis_and_kml(tmp_path):
    """Test land use, population damage overlay and KML generation."""
    from src.gis.damage_analysis import compute_damage_overlay, export_kml_file

    poly = Polygon([(79.60, 30.48), (79.70, 30.48), (79.70, 30.52), (79.60, 30.52), (79.60, 30.48)])
    gdf_flood = gpd.GeoDataFrame([{"flooded": 1, "geometry": poly}], crs="EPSG:4326")
    flood_path = tmp_path / "flood_extent.geojson"
    gdf_flood.to_file(flood_path, driver="GeoJSON")

    infra_pt = Point(79.65, 30.49)
    gdf_infra = gpd.GeoDataFrame([{"name": "Bridge 1", "type": "Road Bridge", "geometry": infra_pt}], crs="EPSG:4326")
    infra_path = tmp_path / "infra.geojson"
    gdf_infra.to_file(infra_path, driver="GeoJSON")

    out_dir = tmp_path / "outputs"
    res = compute_damage_overlay(flood_path, infra_path, out_dir)

    assert "land_use_damage_assessment" in res
    assert "population_exposure_assessment" in res
    assert len(res["land_use_damage_assessment"]) == 4
    assert (out_dir / "flood_extent.kml").exists()
