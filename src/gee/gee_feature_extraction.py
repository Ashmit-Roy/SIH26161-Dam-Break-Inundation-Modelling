"""
Google Earth Engine (GEE) Remote Sensing Feature Extraction Module
Owner: Agent 6 (GEE / ML Lead)
Project: Dam Break Inundation Modelling (SIH 26161)

Provides functions to extract SAR (Sentinel-1) and Optical (Sentinel-2) multi-spectral
and dual-polarization features for near-real-time flood detection and ML classification.
"""

from typing import List, Optional, Tuple

import ee
import pandas as pd


def add_sar_features(image: ee.Image) -> ee.Image:
    """
    Computes derived SAR polarization features on a Sentinel-1 image.

    Derived bands:
      - VV_minus_VH: VV - VH (Polarization difference)
      - VV_plus_VH:  VV + VH (Polarization sum)
      - SAR_Ratio:   VV / (VH + 1e-5) (Backscatter ratio)
      - NDPI:        (VV - VH) / (VV + VH + 1e-5) (Normalized Difference Polarization Index)
    """
    vv = image.select("VV")
    vh = image.select("VH")

    diff = vv.subtract(vh).rename("VV_minus_VH")
    add = vv.add(vh).rename("VV_plus_VH")

    # Avoid zero division with small epsilon
    ratio = vv.divide(vh.add(1e-5)).rename("SAR_Ratio")
    ndpi = diff.divide(add.add(1e-5)).rename("NDPI")

    return image.addBands(diff).addBands(add).addBands(ratio).addBands(ndpi)


def apply_speckle_filter(image: ee.Image, radius_pixels: int = 1) -> ee.Image:
    """
    Applies a focal median speckle filter to smooth radar noise
    while retaining water-land boundary gradients.
    """
    return image.focalMedian(radius=radius_pixels, units="pixels")


def get_sentinel1_feature_stack(
    aoi: ee.Geometry,
    start_date: str,
    end_date: str,
    speckle_filter: bool = True,
    speckle_radius: int = 1,
    orbit_pass: Optional[str] = None,
) -> ee.Image:
    """
    Fetches Sentinel-1 IW GRD SAR composite over an AOI and computes
    dual-polarization (VV, VH) backscatter and derived features.

    Parameters:
      - aoi: Earth Engine Geometry (Region of Interest)
      - start_date: Start date string 'YYYY-MM-DD'
      - end_date: End date string 'YYYY-MM-DD'
      - speckle_filter: Whether to apply focal median speckle filtering
      - speckle_radius: Kernel radius for speckle filter
      - orbit_pass: Optional orbit pass ('ASCENDING' or 'DESCENDING')

    Returns:
      - ee.Image containing [VV, VH, VV_minus_VH, VV_plus_VH, SAR_Ratio, NDPI]
    """
    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
    )

    if orbit_pass:
        collection = collection.filter(ee.Filter.eq("orbitProperties_pass", orbit_pass))

    # Compute median composite
    sar_composite = collection.select(["VV", "VH"]).median()

    if speckle_filter:
        sar_composite = apply_speckle_filter(sar_composite, radius_pixels=speckle_radius)

    return add_sar_features(sar_composite).clip(aoi)


def mask_sentinel2_clouds(image: ee.Image) -> ee.Image:
    """
    Masks clouds and cirrus in Sentinel-2 MSI imagery using the QA60 band.
    """
    qa = image.select("QA60")
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    return image.updateMask(mask)


def add_optical_water_indices(image: ee.Image) -> ee.Image:
    """
    Calculates optical water indices on a Sentinel-2 SR/TOA image:
      - MNDWI: (Green - SWIR1) / (Green + SWIR1)  -> (B3 - B11) / (B3 + B11)
      - NDWI:  (Green - NIR) / (Green + NIR)      -> (B3 - B8) / (B3 + B8)
      - NDVI:  (NIR - Red) / (NIR + Red)          -> (B8 - B4) / (B8 + B4)
    """
    mndwi = image.normalizedDifference(["B3", "B11"]).rename("MNDWI")
    ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

    return image.addBands(mndwi).addBands(ndwi).addBands(ndvi)


def get_sentinel2_optical_composite(
    aoi: ee.Geometry,
    start_date: str,
    end_date: str,
    max_cloud_percent: float = 30.0,
    apply_cloud_mask: bool = True,
) -> ee.Image:
    """
    Fetches cloud-filtered Sentinel-2 surface reflectance composite and computes water indices.
    """
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud_percent))
    )

    if apply_cloud_mask:
        collection = collection.map(mask_sentinel2_clouds)

    composite = collection.median()
    return add_optical_water_indices(composite).clip(aoi)


def sample_training_points(
    image: ee.Image,
    sample_points: ee.FeatureCollection,
    scale: int = 10,
    properties: Optional[List[str]] = None,
) -> ee.FeatureCollection:
    """
    Samples image bands at ground-truth / labeled points for ML training.
    """
    return image.sampleRegions(
        collection=sample_points,
        properties=properties if properties is not None else ["label"],
        scale=scale,
        geometries=True,
    )


def feature_collection_to_dataframe(
    feature_collection: ee.FeatureCollection,
    selected_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Extracts attributes from an ee.FeatureCollection into a Pandas DataFrame.
    """
    features_info = feature_collection.getInfo()
    features = features_info.get("features", []) if isinstance(features_info, dict) else []
    records = [f.get("properties", {}) for f in features if isinstance(f, dict)]
    df = pd.DataFrame(records)

    if selected_columns and not df.empty:
        available_cols = [c for c in selected_columns if c in df.columns]
        df = df[available_cols]

    return df


def extract_multitemporal_sar_change(
    aoi: ee.Geometry,
    pre_event_dates: Tuple[str, str],
    post_event_dates: Tuple[str, str],
) -> ee.Image:
    """
    Extracts multi-temporal SAR backscatter change features between pre-flood and post-flood.

    Bands:
      - VV_post, VH_post
      - VV_diff = VV_post - VV_pre (Negative values indicate flood water inundation)
      - VH_diff = VH_post - VH_pre
    """
    pre_sar = get_sentinel1_feature_stack(aoi, pre_event_dates[0], pre_event_dates[1])
    post_sar = get_sentinel1_feature_stack(aoi, post_event_dates[0], post_event_dates[1])

    vv_diff = post_sar.select("VV").subtract(pre_sar.select("VV")).rename("VV_diff")
    vh_diff = post_sar.select("VH").subtract(pre_sar.select("VH")).rename("VH_diff")

    return post_sar.addBands(vv_diff).addBands(vh_diff)
