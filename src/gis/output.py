from pathlib import Path

import geopandas as gpd


def save_vector(
    gdf: gpd.GeoDataFrame,
    output_path: str,
) -> str:
    """
    Save a GeoDataFrame as a spatial vector file.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    suffix = output_path.suffix.lower()

    if suffix == ".geojson":
        driver = "GeoJSON"
    elif suffix == ".gpkg":
        driver = "GPKG"
    elif suffix == ".shp":
        driver = "ESRI Shapefile"
    elif suffix == ".kml":
        driver = "KML"
    else:
        raise ValueError("Unsupported vector format. Use .geojson, .gpkg, .shp, or .kml.")

    # Ensure KML is exported in EPSG:4326
    if suffix == ".kml" and gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")

    gdf.to_file(output_path, driver=driver)

    return str(output_path)


def load_vector(input_path: str) -> gpd.GeoDataFrame:
    """
    Load a vector dataset into a GeoDataFrame.
    """

    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Vector file not found: {input_path}")

    return gpd.read_file(input_path)
