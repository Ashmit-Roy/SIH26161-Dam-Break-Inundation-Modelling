from pathlib import Path

import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape


def raster_to_flood_extent(
    raster_path: str,
    output_path: str,
    threshold: float = 0.5,
) -> str:
    """
    Convert a flood raster into a polygon flood-extent GeoJSON.

    Pixels with values greater than or equal to `threshold`
    are considered flooded.
    """

    raster_path = Path(raster_path)
    output_path = Path(output_path)

    with rasterio.open(raster_path) as src:
        data = src.read(1)
        transform = src.transform
        crs = src.crs

        mask = data >= threshold

        polygons = []

        for geometry, value in shapes(
            data,
            mask=mask,
            transform=transform,
        ):
            if value >= threshold:
                polygons.append(shape(geometry))

    if not polygons:
        raise ValueError("No flooded area found in the raster.")

    flood_gdf = gpd.GeoDataFrame(
        {"flooded": [1] * len(polygons)},
        geometry=polygons,
        crs=crs,
    )

    # Merge adjacent flood polygons into cleaner geometry
    flood_gdf = flood_gdf.dissolve(by="flooded").reset_index()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    flood_gdf.to_file(
        output_path,
        driver="GeoJSON",
    )

    return str(output_path)


def calculate_flooded_area(geojson_path: str) -> float:
    """
    Calculate flooded area in square metres.
    """

    flood_gdf = gpd.read_file(geojson_path)

    if flood_gdf.empty:
        return 0.0

    # Reproject to a metre-based CRS if necessary.
    if flood_gdf.crs is None:
        raise ValueError("Flood extent has no CRS.")

    projected = flood_gdf.to_crs(flood_gdf.estimate_utm_crs())

    return float(projected.geometry.area.sum())
