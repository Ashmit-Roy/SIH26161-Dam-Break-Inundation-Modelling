"""
Unit & Integration Tests for Delft3D Hydrodynamic Results, Shapefiles, KML, and Road/Bridge Damage Overlay.
Module: tests/gis/test_delft3d_gis.py
Ownership: Member D (GIS Lead / Agent 4)
"""

from pathlib import Path
import geopandas as gpd
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_bounds
from shapely.geometry import LineString, Point, Polygon

from src.gis.delft3d_processor import (
    export_delft3d_kml,
    generate_study_bridges,
    generate_study_road_network,
    process_delft3d_hydrodynamic_outputs,
)


@pytest.fixture
def sample_delft3d_depth_raster(tmp_path):
    """Create a temporary synthetic Delft3D peak water depth GeoTIFF in EPSG:32644 covering the valley reach."""
    raster_path = tmp_path / "delft3d_max_depth.tif"
    arr_path = tmp_path / "delft3d_arrival_time.tif"

    gdf_roads = generate_study_road_network("EPSG:32644")
    minx, miny, maxx, maxy = gdf_roads.total_bounds
    pad = 1000.0

    width, height = 80, 80
    transform = from_bounds(minx - pad, miny - pad, maxx + pad, maxy + pad, width, height)

    # Inundate the entire center band of the raster
    depth = np.zeros((height, width), dtype=np.float32)
    depth[20:60, :] = 5.5  # 5.5m depth across the valley

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
        dst.write(depth, 1)

    # Arrival time
    arr_time = np.full((height, width), 9999.0, dtype=np.float32)
    arr_time[depth > 0.2] = 12.5  # 12.5 minutes
    with rasterio.open(arr_path, "w", **profile) as dst:
        dst.write(arr_time, 1)

    return {"depth": raster_path, "arr_time": arr_path}


def test_generate_study_roads_and_bridges():
    """Test generation of road network and bridge layers."""
    gdf_roads = generate_study_road_network("EPSG:32644")
    gdf_bridges = generate_study_bridges("EPSG:32644")

    assert len(gdf_roads) >= 4
    assert "name" in gdf_roads.columns
    assert "replacement_cost_inr_per_km" in gdf_roads.columns
    assert str(gdf_roads.crs) == "EPSG:32644"

    assert len(gdf_bridges) >= 4
    assert "deck_elevation_m" in gdf_bridges.columns
    assert "replacement_cost_inr" in gdf_bridges.columns
    assert str(gdf_bridges.crs) == "EPSG:32644"


def test_process_delft3d_hydrodynamic_outputs(sample_delft3d_depth_raster, tmp_path):
    """Test full Delft3D GIS processing, Shapefiles, KML, and road/bridge damage overlay."""
    out_dir = tmp_path / "outputs"
    res = process_delft3d_hydrodynamic_outputs(
        max_depth_raster_path=sample_delft3d_depth_raster["depth"],
        arrival_time_raster_path=sample_delft3d_depth_raster["arr_time"],
        outputs_dir=out_dir,
        min_depth_threshold=0.20,
    )

    # Assert structural integrity of summary metrics
    assert "hydrodynamic_metrics" in res
    assert "road_network_damage_analysis" in res
    assert "bridge_infrastructure_damage_analysis" in res
    assert "total_infrastructure_loss_estimate" in res

    assert res["hydrodynamic_metrics"]["total_inundation_area_ha"] > 0.0
    assert res["road_network_damage_analysis"]["total_flooded_road_length_km"] > 0.0
    assert res["bridge_infrastructure_damage_analysis"]["impacted_bridges_count"] >= 1
    assert res["total_infrastructure_loss_estimate"]["total_loss_crores"] > 0.0

    # Verify Shapefiles exist
    assert (out_dir / "delft3d_flood_extent.shp").exists()
    assert (out_dir / "delft3d_damaged_roads.shp").exists()
    assert (out_dir / "delft3d_damaged_bridges.shp").exists()

    # Verify GeoPackages exist
    assert (out_dir / "delft3d_flood_extent.gpkg").exists()
    assert (out_dir / "delft3d_damaged_roads.gpkg").exists()
    assert (out_dir / "delft3d_damaged_bridges.gpkg").exists()

    # Verify GeoJSONs exist
    assert (out_dir / "delft3d_flood_extent.geojson").exists()
    assert (out_dir / "delft3d_damaged_roads.geojson").exists()
    assert (out_dir / "delft3d_damaged_bridges.geojson").exists()

    # Verify KML exists and has valid content
    kml_file = out_dir / "delft3d_dam_break_damage_assessment.kml"
    assert kml_file.exists()
    kml_text = kml_file.read_text(encoding="utf-8")
    assert "<kml" in kml_text
    assert "<Placemark>" in kml_text
    assert "Delft3D Inundation Extent" in kml_text


def test_export_delft3d_kml(tmp_path):
    """Test OGC KML generator for Delft3D flood and asset layers."""
    extent_poly = Polygon([(375000, 3373000), (377000, 3373000), (377000, 3375000), (375000, 3375000)])
    gdf_ext = gpd.GeoDataFrame([{"model": "Delft3D", "geometry": extent_poly}], crs="EPSG:32644")

    road_line = LineString([(374000, 3374000), (378000, 3374000)])
    gdf_road = gpd.GeoDataFrame([{"name": "NH-107A", "flooded": True, "status": "Inundated", "flooded_length_km": 2.5, "estimated_damage_inr": 5000000, "geometry": road_line}], crs="EPSG:32644")

    bridge_pt = Point(376000, 3374000)
    gdf_brg = gpd.GeoDataFrame([{"name": "Raini Bridge", "flooded": True, "structural_risk": "Severe", "overtopping_depth_m": 5.2, "estimated_loss_inr": 20000000, "geometry": bridge_pt}], crs="EPSG:32644")

    out_kml = tmp_path / "test_delft3d.kml"
    result_path = export_delft3d_kml(gdf_ext, gdf_road, gdf_brg, out_kml)

    assert Path(result_path).exists()
    content = Path(result_path).read_text(encoding="utf-8")
    assert "Raini Bridge" in content
    assert "NH-107A" in content
