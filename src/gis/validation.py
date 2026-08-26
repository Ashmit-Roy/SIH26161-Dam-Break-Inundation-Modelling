from pathlib import Path

import geopandas as gpd
import rasterio


def validate_raster(raster_path: str | Path) -> dict:
    """
    Validate a raster file for GIS processing.

    Returns a dictionary containing validation status
    and basic raster metadata.
    """

    path = Path(raster_path)

    if not path.exists():
        return {
            "valid": False,
            "error": f"Raster file does not exist: {path}",
        }

    if not path.is_file():
        return {
            "valid": False,
            "error": f"Path is not a file: {path}",
        }

    try:
        with rasterio.open(path) as src:
            if src.count < 1:
                return {
                    "valid": False,
                    "error": "Raster contains no bands.",
                }

            if src.width <= 0 or src.height <= 0:
                return {
                    "valid": False,
                    "error": "Raster has invalid dimensions.",
                }

            if src.crs is None:
                return {
                    "valid": False,
                    "error": "Raster has no coordinate reference system (CRS).",
                }

            return {
                "valid": True,
                "path": str(path),
                "width": src.width,
                "height": src.height,
                "bands": src.count,
                "crs": str(src.crs),
                "dtype": src.dtypes[0],
                "nodata": src.nodata,
            }

    except rasterio.errors.RasterioIOError as exc:
        return {
            "valid": False,
            "error": f"Unable to open raster: {exc}",
        }


def validate_vector(vector_path: str | Path) -> dict:
    """
    Validate a vector dataset for GIS processing.
    """

    path = Path(vector_path)

    if not path.exists():
        return {
            "valid": False,
            "error": f"Vector file does not exist: {path}",
        }

    if not path.is_file():
        return {
            "valid": False,
            "error": f"Path is not a file: {path}",
        }

    try:
        gdf = gpd.read_file(path)

        if gdf.empty:
            return {
                "valid": False,
                "error": "Vector dataset is empty.",
            }

        if gdf.crs is None:
            return {
                "valid": False,
                "error": "Vector dataset has no CRS.",
            }

        invalid_count = int((~gdf.geometry.is_valid).sum())
        empty_count = int(gdf.geometry.is_empty.sum())

        return {
            "valid": invalid_count == 0 and empty_count == 0,
            "path": str(path),
            "feature_count": len(gdf),
            "crs": str(gdf.crs),
            "invalid_geometries": invalid_count,
            "empty_geometries": empty_count,
        }

    except Exception as exc:
        return {
            "valid": False,
            "error": f"Unable to read vector dataset: {exc}",
        }


def check_crs_match(
    first_path: str | Path,
    second_path: str | Path,
) -> bool:
    """
    Check whether two vector datasets use the same CRS.
    """

    first = gpd.read_file(first_path)
    second = gpd.read_file(second_path)

    if first.crs is None or second.crs is None:
        return False

    return first.crs == second.crs
