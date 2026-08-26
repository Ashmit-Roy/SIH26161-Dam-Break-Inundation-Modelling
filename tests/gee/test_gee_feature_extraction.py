from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from src.gee.gee_feature_extraction import (
    add_optical_water_indices,
    add_sar_features,
    apply_speckle_filter,
    extract_multitemporal_sar_change,
    feature_collection_to_dataframe,
    get_sentinel1_feature_stack,
    get_sentinel2_optical_composite,
    mask_sentinel2_clouds,
    sample_training_points,
)


@pytest.fixture
def mock_ee_image():
    image = MagicMock()
    image.select.return_value = image
    image.subtract.return_value = image
    image.add.return_value = image
    image.divide.return_value = image
    image.rename.return_value = image
    image.addBands.return_value = image
    image.normalizedDifference.return_value = image
    image.focalMedian.return_value = image
    image.updateMask.return_value = image
    image.clip.return_value = image
    return image


def test_add_sar_features_mock(mock_ee_image):
    result = add_sar_features(mock_ee_image)
    assert result is not None
    assert mock_ee_image.select.called
    assert mock_ee_image.addBands.called


def test_apply_speckle_filter(mock_ee_image):
    result = apply_speckle_filter(mock_ee_image, radius_pixels=2)
    assert result is not None
    mock_ee_image.focalMedian.assert_called_with(radius=2, units="pixels")


def test_mask_sentinel2_clouds(mock_ee_image):
    result = mask_sentinel2_clouds(mock_ee_image)
    assert result is not None
    assert mock_ee_image.updateMask.called


def test_add_optical_water_indices(mock_ee_image):
    result = add_optical_water_indices(mock_ee_image)
    assert result is not None
    assert mock_ee_image.normalizedDifference.called


def test_sample_training_points(mock_ee_image):
    sample_pts = MagicMock()
    mock_ee_image.sampleRegions.return_value = MagicMock()
    result = sample_training_points(mock_ee_image, sample_pts, scale=10)
    assert result is not None
    mock_ee_image.sampleRegions.assert_called_once()


def test_feature_collection_to_dataframe():
    fc = MagicMock()
    fc.getInfo.return_value = {
        "features": [
            {"properties": {"VV": -12.5, "VH": -18.2, "label": 1}},
            {"properties": {"VV": -8.1, "VH": -14.0, "label": 0}},
        ]
    }
    df = feature_collection_to_dataframe(fc, selected_columns=["VV", "VH", "label"])
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "VV" in df.columns
    assert "label" in df.columns


@patch("src.gee.gee_feature_extraction.ee")
def test_get_sentinel1_feature_stack(mock_ee, mock_ee_image):
    aoi = MagicMock()
    mock_coll_instance = MagicMock()
    mock_ee.ImageCollection.return_value = mock_coll_instance
    mock_coll_instance.filterBounds.return_value = mock_coll_instance
    mock_coll_instance.filterDate.return_value = mock_coll_instance
    mock_coll_instance.filter.return_value = mock_coll_instance
    mock_coll_instance.select.return_value = mock_coll_instance
    mock_coll_instance.median.return_value = mock_ee_image

    result = get_sentinel1_feature_stack(aoi, "2023-01-01", "2023-01-15")
    assert result is not None


@patch("src.gee.gee_feature_extraction.ee")
def test_get_sentinel2_optical_composite(mock_ee, mock_ee_image):
    aoi = MagicMock()
    mock_coll_instance = MagicMock()
    mock_ee.ImageCollection.return_value = mock_coll_instance
    mock_coll_instance.filterBounds.return_value = mock_coll_instance
    mock_coll_instance.filterDate.return_value = mock_coll_instance
    mock_coll_instance.filter.return_value = mock_coll_instance
    mock_coll_instance.map.return_value = mock_coll_instance
    mock_coll_instance.median.return_value = mock_ee_image

    result = get_sentinel2_optical_composite(aoi, "2023-01-01", "2023-01-15")
    assert result is not None


@patch("src.gee.gee_feature_extraction.get_sentinel1_feature_stack")
def test_extract_multitemporal_sar_change(mock_get_s1, mock_ee_image):
    mock_get_s1.return_value = mock_ee_image
    aoi = MagicMock()
    result = extract_multitemporal_sar_change(
        aoi,
        ("2023-05-01", "2023-05-31"),
        ("2023-07-01", "2023-07-31"),
    )
    assert result is not None
