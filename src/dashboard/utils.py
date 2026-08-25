import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List

import geopandas as gpd
from shapely.geometry import shape, mapping


def validate_crs(crs: str) -> bool:
    """Validate that a CRS string is recognized by GDAL/Proj."""
    try:
        from pyproj import CRS
        CRS(crs)
        return True
    except Exception:
        return False


def geojson_to_gdf(geojson: Dict[str, Any]) -> gpd.GeoDataFrame:
    """Convert GeoJSON geometry to GeoDataFrame."""
    return gpd.GeoDataFrame([{"geometry": shape(geojson)}], crs="EPSG:4326")


def gdf_to_geojson(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
    """Convert GeoDataFrame to GeoJSON."""
    return json.loads(gdf.to_json())


def calculate_flood_stats(
    depths: List[float], areas: List[float]
) -> Dict[str, float]:
    """Calculate basic flood statistics from depth-area data."""
    if not depths or not areas or len(depths) != len(areas):
        return {"mean_depth": 0.0, "max_depth": 0.0, "total_area": 0.0}

    max_depth = max(depths)
    mean_depth = sum(depths) / len(depths)
    total_area = sum(areas)

    return {
        "mean_depth": round(mean_depth, 3),
        "max_depth": round(max_depth, 3),
        "total_area": round(total_area, 3),
    }


def format_for_dashboard(
    result: Dict[str, Any], metric: str = "water_depth"
) -> Dict[str, Any]:
    """Format simulation result for dashboard consumption."""
    return {
        "metric": metric,
        "data": result,
        "timestamp": result.get("timestamp"),
        "simulation_id": result.get("simulation_id"),
    }