"""
Google Earth Engine (GEE) Flood Detection & Permanent Water Baseline Module
Owner: Agent 6 (GEE / ML Lead)
Project: Dam Break Inundation Modelling (SIH 26161)

Provides functions for near-real-time flood mapping using Sentinel-1 SAR imagery,
JRC Global Surface Water baseline masking, and export to standard GeoJSON vector format.
"""

from typing import Any, Dict, Optional, Tuple

import ee


def init_gee(project_id: str = "sih-dam-break", authenticate_if_needed: bool = True) -> bool:
    """
    Initializes the Earth Engine client. Attempts initialization with the
    specified cloud project ID, falling back to interactive authentication if requested.
    """
    try:
        ee.Initialize(project=project_id)
        return True
    except Exception as e:
        if authenticate_if_needed:
            try:
                ee.Authenticate()
                ee.Initialize(project=project_id)
                return True
            except Exception as err:
                print(f"Failed to initialize Earth Engine: {err}")
                return False
        return False


def get_sar_composite(
    aoi: ee.Geometry,
    start_date: str,
    end_date: str,
    polarization: str = "VV",
    speckle_filter_radius: int = 1,
) -> ee.Image:
    """
    Fetches a Sentinel-1 IW GRD SAR median composite over an AOI for a given date range.

    Parameters:
      - aoi: Earth Engine Geometry
      - start_date: Start date string 'YYYY-MM-DD'
      - end_date: End date string 'YYYY-MM-DD'
      - polarization: Desired polarization band ('VV' or 'VH')
      - speckle_filter_radius: Focal median kernel radius in pixels (0 disables filter)
    """
    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", polarization))
        .select(polarization)
    )

    composite = collection.median()
    if speckle_filter_radius > 0:
        composite = composite.focalMedian(radius=speckle_filter_radius, units="pixels")

    return composite.clip(aoi)


def get_permanent_water_mask(
    aoi: ee.Geometry,
    seasonality_threshold: int = 80,
) -> ee.Image:
    """
    Retrieves the JRC Global Surface Water permanent water mask over an AOI.
    Pixels with seasonality >= threshold (e.g. 80%) are considered permanent water.

    Returns:
      - ee.Image binary mask (1 = permanent water, 0 = non-permanent)
    """
    jrc_gsw = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("seasonality")
    permanent_water = jrc_gsw.gte(seasonality_threshold).clip(aoi)
    return permanent_water.rename("permanent_water")


def extract_flood_extent(
    aoi: ee.Geometry,
    pre_dates: Tuple[str, str],
    post_dates: Tuple[str, str],
    threshold_db: float = -17.0,
    mask_permanent_water: bool = True,
    seasonality_threshold: int = 80,
    scale: int = 10,
) -> Tuple[ee.Image, Dict[str, Any]]:
    """
    Computes flood extent: Water detected post-event that was NOT permanent water before.

    Parameters:
      - aoi: Earth Engine Geometry bounding the region of interest
      - pre_dates: Tuple of ('YYYY-MM-DD', 'YYYY-MM-DD') for baseline SAR
      - post_dates: Tuple of ('YYYY-MM-DD', 'YYYY-MM-DD') for crisis / post-flood SAR
      - threshold_db: SAR backscatter threshold (dB) for water classification
      - mask_permanent_water: If True, uses JRC permanent water baseline to mask permanent bodies
      - seasonality_threshold: JRC seasonality threshold percentage (default 80%)
      - scale: Resolution in meters for area reduction (default 10m)

    Returns:
      - (new_flood_image, area_stats_dict)
    """
    pre_sar = get_sar_composite(aoi, pre_dates[0], pre_dates[1])
    post_sar = get_sar_composite(aoi, post_dates[0], post_dates[1])

    pre_water = pre_sar.lt(threshold_db)
    post_water = post_sar.lt(threshold_db)

    # Isolated new water
    new_flood = post_water.And(pre_water.Not())

    # Optionally exclude permanent water using JRC global dataset
    if mask_permanent_water:
        permanent_water = get_permanent_water_mask(aoi, seasonality_threshold=seasonality_threshold)
        new_flood = new_flood.And(permanent_water.Not())

    new_flood = new_flood.rename("flood_extent").selfMask()

    # Calculate flooded surface area (m²)
    area_img = new_flood.multiply(ee.Image.pixelArea())
    stats = area_img.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=aoi,
        scale=scale,
        maxPixels=1e9,
    )

    return new_flood, stats


def compute_flood_summary(stats_dict: Any) -> Dict[str, float]:
    """
    Converts raw reduceRegion stats (m²) into structured units (m², hectares, km²).
    Handles both ee.Dictionary (ComputedObject) and Python dicts.
    """
    if hasattr(stats_dict, "getInfo"):
        try:
            stats_dict = stats_dict.getInfo()
        except Exception:
            stats_dict = {}

    if not isinstance(stats_dict, dict):
        stats_dict = {}

    raw_val = stats_dict.get("flood_extent", 0.0)
    if hasattr(raw_val, "getInfo"):
        try:
            raw_val = raw_val.getInfo()
        except Exception:
            raw_val = 0.0

    try:
        area_m2 = float(raw_val or 0.0)
    except (ValueError, TypeError):
        area_m2 = 0.0

    area_ha = area_m2 / 10000.0
    area_km2 = area_m2 / 1000000.0

    return {
        "area_m2": round(area_m2, 2),
        "area_ha": round(area_ha, 2),
        "area_km2": round(area_km2, 4),
    }


def flood_extent_to_geojson(
    flood_image: ee.Image,
    aoi: ee.Geometry,
    scale: int = 30,
    max_pixels: int = 1000000,
) -> Dict[str, Any]:
    """
    Converts a binary flood extent raster into a vector GeoJSON FeatureCollection.
    Useful for integration with web dashboard mapping (Leaflet/Mapbox) and GIS layers.
    """
    vectors = flood_image.reduceToVectors(
        geometry=aoi,
        scale=scale,
        geometryType="polygon",
        eightConnected=True,
        labelProperty="flood",
        maxPixels=max_pixels,
    )
    return vectors.getInfo()
