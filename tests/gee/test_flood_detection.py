from unittest.mock import MagicMock, patch

import pytest
from src.gee.flood_detection import (
    compute_flood_summary,
    extract_flood_extent,
    flood_extent_to_geojson,
    get_permanent_water_mask,
    get_sar_composite,
    init_gee,
)


@pytest.fixture
def mock_ee_image():
    image = MagicMock()
    image.select.return_value = image
    image.lt.return_value = image
    image.gte.return_value = image
    image.And.return_value = image
    image.Not.return_value = image
    image.rename.return_value = image
    image.selfMask.return_value = image
    image.focalMedian.return_value = image
    image.clip.return_value = image
    image.multiply.return_value = image
    image.reduceRegion.return_value = {"flood_extent": 2500000.0}
    return image


@patch("src.gee.flood_detection.ee")
def test_init_gee_success(mock_ee):
    mock_ee.Initialize.return_value = None
    assert init_gee("test-project") is True
    mock_ee.Initialize.assert_called_with(project="test-project")


@patch("src.gee.flood_detection.ee")
def test_init_gee_fallback_authenticate(mock_ee):
    mock_ee.Initialize.side_effect = [Exception("Not authenticated"), None]
    mock_ee.Authenticate.return_value = None
    assert init_gee("test-project") is True
    mock_ee.Authenticate.assert_called_once()


@patch("src.gee.flood_detection.ee")
def test_get_sar_composite(mock_ee, mock_ee_image):
    mock_coll = MagicMock()
    mock_ee.ImageCollection.return_value = mock_coll
    mock_coll.filterBounds.return_value = mock_coll
    mock_coll.filterDate.return_value = mock_coll
    mock_coll.filter.return_value = mock_coll
    mock_coll.select.return_value = mock_coll
    mock_coll.median.return_value = mock_ee_image

    aoi = MagicMock()
    res = get_sar_composite(aoi, "2023-01-01", "2023-01-10", polarization="VV", speckle_filter_radius=1)
    assert res is not None
    mock_ee_image.focalMedian.assert_called_with(radius=1, units="pixels")
    mock_ee_image.clip.assert_called_with(aoi)


@patch("src.gee.flood_detection.ee")
def test_get_permanent_water_mask(mock_ee, mock_ee_image):
    mock_ee.Image.return_value = mock_ee_image
    aoi = MagicMock()
    res = get_permanent_water_mask(aoi, seasonality_threshold=80)
    assert res is not None
    mock_ee.Image.assert_called_with("JRC/GSW1_4/GlobalSurfaceWater")
    mock_ee_image.gte.assert_called_with(80)


@patch("src.gee.flood_detection.get_permanent_water_mask")
@patch("src.gee.flood_detection.get_sar_composite")
@patch("src.gee.flood_detection.ee")
def test_extract_flood_extent(mock_ee, mock_get_sar, mock_get_perm, mock_ee_image):
    mock_get_sar.return_value = mock_ee_image
    mock_get_perm.return_value = mock_ee_image
    mock_ee.Image.pixelArea.return_value = mock_ee_image

    aoi = MagicMock()
    flood_img, stats = extract_flood_extent(
        aoi,
        ("2023-01-01", "2023-01-15"),
        ("2023-02-01", "2023-02-15"),
        threshold_db=-17.0,
        mask_permanent_water=True,
    )
    assert flood_img is not None
    assert stats == {"flood_extent": 2500000.0}
    mock_get_perm.assert_called_once()


def test_compute_flood_summary():
    stats = {"flood_extent": 5000000.0}  # 5,000,000 m² = 500 ha = 5 km²
    summary = compute_flood_summary(stats)
    assert summary["area_m2"] == 5000000.0
    assert summary["area_ha"] == 500.0
    assert summary["area_km2"] == 5.0

    # Test empty or zero
    summary_empty = compute_flood_summary({})
    assert summary_empty["area_m2"] == 0.0
    assert summary_empty["area_ha"] == 0.0
    assert summary_empty["area_km2"] == 0.0


def test_flood_extent_to_geojson(mock_ee_image):
    mock_vectors = MagicMock()
    mock_vectors.getInfo.return_value = {
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "properties": {"flood": 1}, "geometry": {"type": "Polygon", "coordinates": []}}],
    }
    mock_ee_image.reduceToVectors.return_value = mock_vectors

    aoi = MagicMock()
    geojson = flood_extent_to_geojson(mock_ee_image, aoi, scale=30)
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 1
    mock_ee_image.reduceToVectors.assert_called_once()
