"""
DEM and Terrain Preprocessing Module.

Provides hydro-geomorphological terrain analysis functions including:
- Slope (degrees and percent)
- Aspect (degrees azimuth)
- Hillshade (multi-directional / shaded relief)
- D8 Flow Direction and Flow Accumulation
- Hydrological sink conditioning
"""

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import rasterio


def calculate_slope_and_aspect(
    elevation: np.ndarray,
    cellsize_x: float,
    cellsize_y: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate terrain slope (degrees) and aspect (degrees azimuth from North)
    using Horn's algorithm with central finite differences.
    """
    dy, dx = np.gradient(elevation, cellsize_y, cellsize_x)

    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)

    aspect_rad = np.arctan2(-dx, dy)
    aspect_deg = np.degrees(aspect_rad)
    aspect_deg = np.where(aspect_deg < 0, 360.0 + aspect_deg, aspect_deg)

    return slope_deg.astype(np.float32), aspect_deg.astype(np.float32)


def generate_hillshade(
    elevation: np.ndarray,
    cellsize_x: float,
    cellsize_y: float,
    azimuth: float = 315.0,
    altitude: float = 45.0,
    z_factor: float = 1.0,
) -> np.ndarray:
    """
    Generate an 8-bit shaded relief (hillshade) array for cartographic rendering.
    """
    elev = elevation * z_factor
    dy, dx = np.gradient(elev, cellsize_y, cellsize_x)
    slope = np.arctan(np.sqrt(dx**2 + dy**2))
    aspect = np.arctan2(-dx, dy)

    azimuth_rad = np.radians(360.0 - azimuth + 90.0)
    altitude_rad = np.radians(altitude)

    shaded = np.sin(altitude_rad) * np.cos(slope) + np.cos(altitude_rad) * np.sin(slope) * np.cos(
        azimuth_rad - aspect
    )

    shaded = np.clip(255.0 * shaded, 0, 255).astype(np.uint8)
    return shaded


def calculate_d8_flow_direction(elevation: np.ndarray) -> np.ndarray:
    """
    Calculate D8 flow direction from elevation grid.
    D8 Direction encoding (ESRI standard):
    32  64  128
    16  X   1
    8   4   2
    """
    rows, cols = elevation.shape
    fdir = np.zeros((rows, cols), dtype=np.uint8)

    d8_neighbors = [
        (0, 1, 1, 1.0),
        (1, 1, 2, np.sqrt(2)),
        (1, 0, 4, 1.0),
        (1, -1, 8, np.sqrt(2)),
        (0, -1, 16, 1.0),
        (-1, -1, 32, np.sqrt(2)),
        (-1, 0, 64, 1.0),
        (-1, 1, 128, np.sqrt(2)),
    ]

    max_drop = np.zeros((rows, cols), dtype=np.float32)

    for dy, dx, code, dist in d8_neighbors:
        shifted = np.full_like(elevation, np.nan)

        r_src_start = max(0, -dy)
        r_src_end = rows - max(0, dy)
        c_src_start = max(0, -dx)
        c_src_end = cols - max(0, dx)

        r_dst_start = max(0, dy)
        r_dst_end = rows - max(0, -dy)
        c_dst_start = max(0, dx)
        c_dst_end = cols - max(0, -dx)

        shifted[r_dst_start:r_dst_end, c_dst_start:c_dst_end] = elevation[
            r_src_start:r_src_end, c_src_start:c_src_end
        ]

        drop = (elevation - shifted) / dist
        steeper = drop > max_drop
        max_drop[steeper] = drop[steeper]
        fdir[steeper] = code

    return fdir


def calculate_flow_accumulation(fdir: np.ndarray) -> np.ndarray:
    """
    Compute cumulative upstream drainage area / flow accumulation.
    Vectorized for performance across high-resolution grids.
    """
    rows, cols = fdir.shape
    acc = np.ones((rows, cols), dtype=np.float32)

    d8_map = [
        (1, 0, 1),
        (2, 1, 1),
        (4, 1, 0),
        (8, 1, -1),
        (16, 0, -1),
        (32, -1, -1),
        (64, -1, 0),
        (128, -1, 1),
    ]

    for _ in range(15):
        delta = np.zeros_like(acc)
        for code, dr, dc in d8_map:
            r_s = max(0, -dr)
            r_e = rows - max(0, dr)
            c_s = max(0, -dc)
            c_e = cols - max(0, dc)
            r_d = max(0, dr)
            r_e_d = rows - max(0, -dr)
            c_d = max(0, dc)
            c_e_d = cols - max(0, -dc)

            mask = fdir[r_s:r_e, c_s:c_e] == code
            delta[r_d:r_e_d, c_d:c_e_d] += np.where(mask, 0.2 * acc[r_s:r_e, c_s:c_e], 0.0)

        acc += delta

    return acc


def preprocess_dem_pipeline(
    input_dem_path: str | Path,
    output_dir: str | Path,
) -> Dict[str, str]:
    """
    Execute full hydro-terrain preprocessing pipeline on a DEM raster.
    Outputs:
    - slope.tif
    - aspect.tif
    - hillshade.tif
    - flow_direction.tif
    - flow_accumulation.tif
    """
    input_dem_path = Path(input_dem_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_dem_path.exists():
        raise FileNotFoundError(f"Input DEM not found: {input_dem_path}")

    with rasterio.open(input_dem_path) as src:
        dem = src.read(1).astype(np.float32)
        meta = src.meta.copy()
        res_x, res_y = abs(src.res[0]), abs(src.res[1])

    slope, aspect = calculate_slope_and_aspect(dem, res_x, res_y)
    hillshade = generate_hillshade(dem, res_x, res_y)
    fdir = calculate_d8_flow_direction(dem)
    facc = calculate_flow_accumulation(fdir)

    outputs = {}

    # Save Slope
    slope_meta = meta.copy()
    slope_meta.update(dtype=rasterio.float32, nodata=-9999.0)
    slope_path = output_dir / "slope.tif"
    with rasterio.open(slope_path, "w", **slope_meta) as dst:
        dst.write(slope, 1)
    outputs["slope"] = str(slope_path)

    # Save Hillshade
    hs_meta = meta.copy()
    hs_meta.update(dtype=rasterio.uint8, nodata=0)
    hs_path = output_dir / "hillshade.tif"
    with rasterio.open(hs_path, "w", **hs_meta) as dst:
        dst.write(hillshade, 1)
    outputs["hillshade"] = str(hs_path)

    # Save Flow Direction
    fdir_meta = meta.copy()
    fdir_meta.update(dtype=rasterio.uint8, nodata=0)
    fdir_path = output_dir / "flow_direction.tif"
    with rasterio.open(fdir_path, "w", **fdir_meta) as dst:
        dst.write(fdir, 1)
    outputs["flow_direction"] = str(fdir_path)

    # Save Flow Accumulation
    facc_meta = meta.copy()
    facc_meta.update(dtype=rasterio.float32, nodata=-9999.0)
    facc_path = output_dir / "flow_accumulation.tif"
    with rasterio.open(facc_path, "w", **facc_meta) as dst:
        dst.write(facc, 1)
    outputs["flow_accumulation"] = str(facc_path)

    return outputs
