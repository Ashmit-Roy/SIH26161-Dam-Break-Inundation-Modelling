from pathlib import Path

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling


def get_raster_info(raster_path: str) -> dict:
    """
    Return basic metadata and spatial information about a raster.
    """

    raster_path = Path(raster_path)

    if not raster_path.exists():
        raise FileNotFoundError(f"Raster not found: {raster_path}")

    with rasterio.open(raster_path) as src:
        return {
            "path": str(raster_path),
            "width": src.width,
            "height": src.height,
            "bands": src.count,
            "crs": str(src.crs),
            "resolution": src.res,
            "bounds": tuple(src.bounds),
            "dtype": src.dtypes[0],
            "nodata": src.nodata,
        }


def reproject_raster(
    input_path: str,
    output_path: str,
    target_crs: str,
) -> str:
    """
    Reproject a raster into the requested coordinate reference system.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Raster not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(input_path) as src:

        transform, width, height = calculate_default_transform(
            src.crs,
            target_crs,
            src.width,
            src.height,
            *src.bounds,
        )

        profile = src.profile.copy()

        profile.update(
            {
                "crs": target_crs,
                "transform": transform,
                "width": width,
                "height": height,
            }
        )

        with rasterio.open(output_path, "w", **profile) as dst:

            for band in range(1, src.count + 1):

                reproject(
                    source=rasterio.band(src, band),
                    destination=rasterio.band(dst, band),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.nearest,
                )

    return str(output_path)