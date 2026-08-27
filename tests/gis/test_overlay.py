"""
Unit tests for SPH Simulated Flood Extent vs Satellite Hazard Map Overlay module.
Module: tests/gis/test_overlay.py
"""

from pathlib import Path
import geopandas as gpd
import pytest
from shapely.geometry import Point, Polygon

from src.gis.overlay import (
    compute_spatial_agreement_metrics,
    generate_overlay_kml,
    overlay_sph_on_satellite_hazard,
)


@pytest.fixture
def sample_overlay_data(tmp_path):
    """Create synthetic SPH, Satellite, and Infrastructure layers for testing."""
    # SPH extent in EPSG:32644 (e.g. 1000x1000m polygon)
    poly_sph = Polygon([(1000.0, 1000.0), (2000.0, 1000.0), (2000.0, 2000.0), (1000.0, 2000.0)])
    gdf_sph = gpd.GeoDataFrame(
        [{"model": "DualSPHysics SPH", "scenario": "Test Dam Break", "geometry": poly_sph}],
        crs="EPSG:32644",
    )
    sph_path = tmp_path / "sph_flood_extent.geojson"
    gdf_sph.to_file(sph_path, driver="GeoJSON")

    # Satellite extent overlapping by 50% (from 1500 to 2500)
    poly_sat = Polygon([(1500.0, 1000.0), (2500.0, 1000.0), (2500.0, 2000.0), (1500.0, 2000.0)])
    gdf_sat = gpd.GeoDataFrame(
        [{"satellite": "Sentinel-1", "event": "Post-Break", "geometry": poly_sat}],
        crs="EPSG:32644",
    )
    sat_path = tmp_path / "satellite_flood_extent.geojson"
    gdf_sat.to_file(sat_path, driver="GeoJSON")

    # Critical Infrastructure points
    pt_in_agree = Point(1750.0, 1500.0)  # In agreement zone
    pt_in_sph = Point(1200.0, 1500.0)    # In SPH only
    pt_outside = Point(3000.0, 3000.0)   # Outside
    gdf_infra = gpd.GeoDataFrame(
        [
            {"name": "Bridge In Overlap", "type": "Bridge", "geometry": pt_in_agree},
            {"name": "Powerhouse in SPH", "type": "Hydro Plant", "geometry": pt_in_sph},
            {"name": "Safe Village", "type": "Village", "geometry": pt_outside},
        ],
        crs="EPSG:32644",
    )
    infra_path = tmp_path / "infrastructure.geojson"
    gdf_infra.to_file(infra_path, driver="GeoJSON")

    return {
        "sph_path": sph_path,
        "sat_path": sat_path,
        "infra_path": infra_path,
        "poly_sph": poly_sph,
        "poly_sat": poly_sat,
    }


def test_compute_spatial_agreement_metrics(sample_overlay_data):
    """Test geometric and validation metrics computation."""
    poly_sph = sample_overlay_data["poly_sph"]
    poly_sat = sample_overlay_data["poly_sat"]

    # Both are 1,000,000 sqm (100 ha)
    # Overlap is 500m * 1000m = 500,000 sqm (50 ha)
    # Union is 1500m * 1000m = 1,500,000 sqm (150 ha)
    metrics = compute_spatial_agreement_metrics(poly_sph, poly_sat)

    assert metrics["sph_flooded_area_ha"] == 100.0
    assert metrics["satellite_hazard_area_ha"] == 100.0
    assert metrics["agreement_intersection_area_ha"] == 50.0
    assert metrics["combined_union_area_ha"] == 150.0

    # IoU = 50 / 150 = 0.3333
    assert abs(metrics["iou_jaccard_index"] - (1.0 / 3.0)) < 0.01

    # Dice = 2 * 50 / (100 + 100) = 0.50
    assert abs(metrics["dice_f1_score"] - 0.50) < 0.01

    # Hit rate = 50 / 100 = 0.50
    assert abs(metrics["hit_rate_sensitivity"] - 0.50) < 0.01

    # FAR = (100 - 50) / 100 = 0.50
    assert abs(metrics["false_alarm_ratio"] - 0.50) < 0.01


def test_overlay_sph_on_satellite_hazard(sample_overlay_data, tmp_path):
    """Test end-to-end overlay processing pipeline."""
    out_dir = tmp_path / "outputs"
    res = overlay_sph_on_satellite_hazard(
        sph_extent_path=sample_overlay_data["sph_path"],
        satellite_hazard_path=sample_overlay_data["sat_path"],
        output_dir=out_dir,
        infrastructure_path=sample_overlay_data["infra_path"],
        computation_crs="EPSG:32644",
    )

    assert "spatial_agreement_metrics" in res
    assert "infrastructure_exposure_analysis" in res
    assert (out_dir / "sph_satellite_overlay.geojson").exists()
    assert (out_dir / "sph_satellite_overlay.gpkg").exists()
    assert (out_dir / "sph_satellite_overlay.shp").exists()
    assert (out_dir / "sph_satellite_overlay.kml").exists()
    assert (out_dir / "sph_satellite_validation_report.json").exists()

    # Check vector contents
    gdf_out = gpd.read_file(out_dir / "sph_satellite_overlay.geojson")
    assert len(gdf_out) == 3  # Agreement, SPH only, Satellite only
    categories = set(gdf_out["category"].tolist())
    assert "Agreement (Simulated & Observed)" in categories
    assert "SPH Simulated Only" in categories
    assert "Satellite Observed Only" in categories

    # Check infrastructure exposure results
    infra = res["infrastructure_exposure_analysis"]
    assert len(infra) == 3
    asset_agree = next(item for item in infra if item["name"] == "Bridge In Overlap")
    assert asset_agree["in_agreement_zone"] is True
    assert "High Confidence Hazard" in asset_agree["exposure_assessment"]

    asset_sph = next(item for item in infra if item["name"] == "Powerhouse in SPH")
    assert asset_sph["in_sph_extent"] is True
    assert asset_sph["in_agreement_zone"] is False

    asset_safe = next(item for item in infra if item["name"] == "Safe Village")
    assert asset_safe["in_sph_extent"] is False
    assert asset_safe["in_satellite_extent"] is False
    assert asset_safe["exposure_assessment"] == "Safe"


def test_generate_overlay_kml(sample_overlay_data, tmp_path):
    """Test KML export functionality."""
    gdf = gpd.GeoDataFrame(
        [
            {"category": "Agreement (Simulated & Observed)", "area_ha": 50.0, "geometry": sample_overlay_data["poly_sph"]},
            {"category": "SPH Simulated Only", "area_ha": 30.0, "geometry": sample_overlay_data["poly_sat"]},
        ],
        crs="EPSG:32644",
    )
    kml_file = tmp_path / "test_overlay.kml"
    out_path = generate_overlay_kml(gdf, kml_file, "Test Title")

    assert Path(out_path).exists()
    content = Path(out_path).read_text(encoding="utf-8")
    assert "<?xml version=" in content
    assert "<kml" in content
    assert "Agreement (Simulated &amp; Observed)" in content or "Agreement (Simulated & Observed)" in content
