"""
GIS Export & Processing Pipeline for Web and Backend Integration.

Generates:
1. Vector datasets (GeoJSON in EPSG:4326, GPKG/SHP in EPSG:32644)
   - Dam points & metadata
   - River centerline reach
   - Catchment study boundary
   - Critical infrastructure & settlements
   - Inundation polygon extent
   - Hazard zoning polygons (Low, Moderate, Significant, Extreme)
2. Raster datasets (GeoTIFF in EPSG:32644)
   - Preprocessed DEM & Hillshade
   - Peak Flood Depth raster
   - Max Velocity raster
   - Flood Hazard Rating raster
3. Metadata JSON for Backend / Frontend consumption
"""

import json
from pathlib import Path
from typing import Any, Dict

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
from rasterio.transform import from_bounds
from shapely.geometry import LineString, Point, Polygon, shape


def create_study_area_vectors(
    output_vector_dir: Path,
) -> Dict[str, gpd.GeoDataFrame]:
    """
    Generate study area vector layers for Rishi Ganga - Tapovan - Joshimath reach:
    - Dam locations (Tapovan Barrage, Rishiganga Dam)
    - River centerline (Rishiganga to Alaknanda)
    - Critical infrastructure & settlements
    - Catchment boundary polygon
    """
    output_vector_dir.mkdir(parents=True, exist_ok=True)

    # 1. Dam Locations
    dams = [
        {
            "id": "DAM_01",
            "name": "Rishi Ganga Small Hydroelectric Project",
            "river": "Rishi Ganga",
            "type": "Run-of-River Concrete Gravity",
            "height_m": 22.0,
            "crest_elev_m": 2050.0,
            "status_2021": "Severely damaged / Overwashed (Feb 7 2021)",
            "latitude": 30.4850,
            "longitude": 79.6880,
            "geometry": Point(79.6880, 30.4850),
        },
        {
            "id": "DAM_02",
            "name": "Tapovan Vishnugad Hydroelectric Project (NTPC)",
            "river": "Dhauliganga",
            "type": "Barrage with Desilting Basin",
            "height_m": 22.0,
            "crest_elev_m": 1803.0,
            "status_2021": "Severely silted / Breached",
            "latitude": 30.4950,
            "longitude": 79.6210,
            "geometry": Point(79.6210, 30.4950),
        },
    ]
    gdf_dams = gpd.GeoDataFrame(dams, crs="EPSG:4326")

    # 2. River Centerline
    # Originates at glacier snout (79.74, 30.46) -> Rishiganga (79.688, 30.485) -> Raini confluence (79.655, 30.491)
    # -> Tapovan Barrage (79.621, 30.495) -> Dhak (79.585, 30.520) -> Joshimath/Helang (79.525, 30.550)
    river_coords = [
        (79.7450, 30.4620),
        (79.7150, 30.4730),
        (79.6880, 30.4850),  # Rishiganga Dam
        (79.6650, 30.4890),
        (79.6550, 30.4910),  # Raini Confluence
        (79.6380, 30.4930),
        (79.6210, 30.4950),  # Tapovan Barrage
        (79.6050, 30.5050),
        (79.5850, 30.5200),  # Dhak
        (79.5600, 30.5350),
        (79.5400, 30.5420),
        (79.5250, 30.5500),  # Joshimath / Helang Confluence
    ]
    river_geom = LineString(river_coords)
    gdf_river = gpd.GeoDataFrame(
        [
            {
                "reach_id": "REACH_RISHI_DHAULI",
                "name": "Rishi Ganga - Dhauliganga - Alaknanda Valley",
                "length_km": 27.8,
                "slope_pct": 3.4,
                "geometry": river_geom,
            }
        ],
        crs="EPSG:4326",
    )

    # 3. Critical Infrastructure & Settlements
    infra = [
        {
            "infra_id": "INFRA_01",
            "name": "Raini Village Highway Bridge (BRO)",
            "type": "Road Bridge",
            "vulnerability": "High",
            "geometry": Point(79.6545, 30.4915),
        },
        {
            "infra_id": "INFRA_02",
            "name": "NTPC Tapovan Powerhouse & Tunnel",
            "type": "Hydroelectric Plant",
            "vulnerability": "Critical",
            "geometry": Point(79.6205, 30.4955),
        },
        {
            "infra_id": "INFRA_03",
            "name": "Raini Chak Lata Settlement",
            "type": "Village / Habitation",
            "vulnerability": "High",
            "geometry": Point(79.6600, 30.4950),
        },
        {
            "infra_id": "INFRA_04",
            "name": "Dhak Village Settlement",
            "type": "Village / Habitation",
            "vulnerability": "Moderate",
            "geometry": Point(79.5840, 30.5220),
        },
        {
            "infra_id": "INFRA_05",
            "name": "Helang Alaknanda Road Junction",
            "type": "National Highway Infrastructure",
            "vulnerability": "Moderate",
            "geometry": Point(79.5240, 30.5510),
        },
    ]
    gdf_infra = gpd.GeoDataFrame(infra, crs="EPSG:4326")

    # 4. Study Area Boundary (Watershed & Flood Corridor)
    # Bounding polygon with 2.5km valley buffer
    study_polygon = Polygon(
        [
            (79.5000, 30.5650),
            (79.5800, 30.5400),
            (79.6700, 30.5100),
            (79.7600, 30.4850),
            (79.7650, 30.4450),
            (79.6800, 30.4600),
            (79.6000, 30.4800),
            (79.5100, 30.5250),
            (79.5000, 30.5650),
        ]
    )
    gdf_boundary = gpd.GeoDataFrame(
        [
            {
                "basin_id": "CHAMOLI_RISHI_DHAULI",
                "name": "Rishi Ganga - Dhauliganga Valley Catchment",
                "area_sqkm": 284.5,
                "state": "Uttarakhand",
                "district": "Chamoli",
                "geometry": study_polygon,
            }
        ],
        crs="EPSG:4326",
    )

    # Save standard GeoJSON (WGS84)
    gdf_dams.to_file(output_vector_dir / "dam_locations.geojson", driver="GeoJSON")
    gdf_river.to_file(output_vector_dir / "river_centerline.geojson", driver="GeoJSON")
    gdf_infra.to_file(output_vector_dir / "critical_infrastructure.geojson", driver="GeoJSON")
    gdf_boundary.to_file(output_vector_dir / "study_area_boundary.geojson", driver="GeoJSON")

    # Save Projected GPKG (UTM Zone 44N)
    gdf_dams.to_crs("EPSG:32644").to_file(output_vector_dir / "dam_locations.gpkg", driver="GPKG")
    gdf_river.to_crs("EPSG:32644").to_file(
        output_vector_dir / "river_centerline.gpkg", driver="GPKG"
    )
    gdf_infra.to_crs("EPSG:32644").to_file(
        output_vector_dir / "critical_infrastructure.gpkg", driver="GPKG"
    )
    gdf_boundary.to_crs("EPSG:32644").to_file(
        output_vector_dir / "study_area_boundary.gpkg", driver="GPKG"
    )

    return {
        "dams": gdf_dams,
        "river": gdf_river,
        "infrastructure": gdf_infra,
        "boundary": gdf_boundary,
    }


def generate_synthetic_study_dem(
    output_dem_path: Path,
    gdf_river: gpd.GeoDataFrame,
) -> str:
    """
    Generate realistic high-resolution DEM (30m cell size) in UTM Zone 44N
    covering the Rishi Ganga - Tapovan - Joshimath canyon reach.
    """
    output_dem_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert river to UTM Zone 44N
    river_utm = gdf_river.to_crs("EPSG:32644")
    bounds = river_utm.total_bounds  # minx, miny, maxx, maxy

    pad = 3000.0  # 3km padding
    minx, miny, maxx, maxy = bounds[0] - pad, bounds[1] - pad, bounds[2] + pad, bounds[3] + pad

    res = 30.0  # 30m spatial resolution
    width = int(np.ceil((maxx - minx) / res))
    height = int(np.ceil((maxy - miny) / res))

    transform = from_bounds(minx, miny, maxx, maxy, width, height)

    # Coordinate matrices
    rows, cols = np.indices((height, width))
    xs = (minx + (cols + 0.5) * res).astype(np.float32)
    ys = (maxy - (rows + 0.5) * res).astype(np.float32)

    # Valley centerline interpolation
    line = river_utm.geometry.iloc[0]

    # Base regional mountain slope: 3800m ASL at glacier (SE) down to 1400m at Joshimath (NW)
    # Direction vector from SE to NW
    se_point = np.array(line.coords[0])
    nw_point = np.array(line.coords[-1])
    vec = nw_point - se_point
    vec_len = np.linalg.norm(vec)
    vec_unit = vec / vec_len

    # Sample river points along actual channel
    sample_dists = np.linspace(0, line.length, 400)
    line_sample_pts = np.array([line.interpolate(d).coords[0] for d in sample_dists])

    # Precompute distance and along-river index
    dist_to_channel = np.full((height, width), 99999.0, dtype=np.float32)
    thalweg_elev_grid = np.full((height, width), 3800.0, dtype=np.float32)

    for i, (px, py) in enumerate(line_sample_pts[::2]):
        d = np.sqrt((xs - px) ** 2 + (ys - py) ** 2).astype(np.float32)
        closer = d < dist_to_channel
        dist_to_channel[closer] = d[closer]
        # Interpolate elevation from 3600m at headwater down to 1420m at outlet
        frac = (i * 2) / len(sample_dists)
        elev_at_pt = 3600.0 - frac * (3600.0 - 1420.0)
        thalweg_elev_grid[closer] = elev_at_pt

    # Flat river channel bed (~75m width) and steep mountain walls
    dist_eff = np.maximum(0.0, dist_to_channel - 60.0)
    canyon_walls = 0.48 * dist_eff + 120.0 * (1.0 - np.exp(-dist_eff / 250.0))

    terrain_noise = 8.0 * np.sin(xs / 500.0) * np.cos(ys / 500.0)
    dem = (thalweg_elev_grid + canyon_walls + terrain_noise).astype(np.float32)
    dem = np.maximum(dem, 1380.0)

    profile = {
        "driver": "GTiff",
        "dtype": "float32",
        "nodata": -9999.0,
        "width": width,
        "height": height,
        "count": 1,
        "crs": "EPSG:32644",
        "transform": transform,
    }

    with rasterio.open(output_dem_path, "w", **profile) as dst:
        dst.write(dem, 1)

    return str(output_dem_path)


def run_full_gis_pipeline(
    workspace_root: Path,
) -> Dict[str, Any]:
    """
    Execute end-to-end GIS pipeline:
    1. Vector generation
    2. DEM generation & hydro-preprocessing
    3. Dam break hydrodynamic simulation
    4. Web-ready exports (GeoJSON & GeoTIFF)
    5. Summary metrics generation
    """
    data_dir = workspace_root / "data"
    vector_dir = data_dir / "vector"
    dem_dir = data_dir / "dem"
    outputs_dir = workspace_root / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    print("--- 1. Generating Vector Layers ---")
    layers = create_study_area_vectors(vector_dir)

    print("--- 2. Preparing High-Resolution Terrain DEM ---")
    dem_path = dem_dir / "rishi_ganga_dem_30m.tif"
    generate_synthetic_study_dem(dem_path, layers["river"])

    import sys

    if str(workspace_root) not in sys.path:
        sys.path.insert(0, str(workspace_root))

    print("--- 3. Preprocessing DEM (Slope, Hillshade, Flow Direction) ---")
    from src.gis.dem_preprocessing import preprocess_dem_pipeline

    prep_results = preprocess_dem_pipeline(dem_path, dem_dir / "preprocessed")

    # Copy hillshade to outputs for visualization
    with rasterio.open(prep_results["hillshade"]) as src:
        hs_meta = src.meta.copy()
        hs_data = src.read(1)
    with rasterio.open(outputs_dir / "terrain_hillshade.tif", "w", **hs_meta) as dst:
        dst.write(hs_data, 1)

    print("--- 4. Running Hydrodynamic Dam-Break Simulation ---")
    from src.gis.dam_break_hydraulic import categorize_hazard_zones, simulate_dam_break_inundation

    # Breach location at Rishi Ganga Dam (converted to UTM Zone 44N)
    dam_utm = layers["dams"].to_crs("EPSG:32644")
    breach_pt = dam_utm.iloc[0].geometry
    breach_coords = (breach_pt.x, breach_pt.y)

    sim_results = simulate_dam_break_inundation(
        dem_path=dem_path,
        breach_coords=breach_coords,
        breach_discharge_peak=14500.0,
        reservoir_volume_m3=6.2e6,
        breach_duration_sec=3600.0,
        manning_n=0.045,
        min_depth_threshold=0.20,
        river_geojson_path=vector_dir / "river_centerline.geojson",
    )

    max_depth = sim_results["max_depth"]
    max_vel = sim_results["max_velocity"]
    hazard_index = sim_results["hazard_index"]
    arrival_time = sim_results["arrival_time"]

    # Save Output Rasters (EPSG:32644 GeoTIFF)
    with rasterio.open(dem_path) as src:
        raster_meta = src.meta.copy()
        raster_crs = src.crs
        raster_transform = src.transform

    raster_meta.update(dtype="float32", nodata=-9999.0)

    # 1. Flood Depth Raster
    depth_path = outputs_dir / "flood_depth.tif"
    with rasterio.open(depth_path, "w", **raster_meta) as dst:
        dst.write(max_depth, 1)

    # 2. Flow Velocity Raster
    vel_path = outputs_dir / "flow_velocity.tif"
    with rasterio.open(vel_path, "w", **raster_meta) as dst:
        dst.write(max_vel, 1)

    # 3. Hazard Index Raster
    haz_path = outputs_dir / "hazard_index.tif"
    with rasterio.open(haz_path, "w", **raster_meta) as dst:
        dst.write(hazard_index, 1)

    # 4. Arrival Time Raster
    arr_path = outputs_dir / "arrival_time.tif"
    with rasterio.open(arr_path, "w", **raster_meta) as dst:
        dst.write(arrival_time, 1)

    print("--- 5. Vectorizing Flood Inundation Extent & Hazard Polygons ---")
    # Vectorize flood extent
    mask = max_depth >= 0.20
    extent_polys = []
    for geom, val in shapes(max_depth, mask=mask, transform=raster_transform):
        if val >= 0.20:
            poly = shape(geom)
            if poly.is_valid and poly.area > 500.0:
                extent_polys.append(poly)

    gdf_extent_utm = gpd.GeoDataFrame(
        {
            "scenario": ["Rishi_Ganga_Dam_Break_Peak_Discharge"] * len(extent_polys),
            "flooded": [1] * len(extent_polys),
            "min_depth_m": [0.20] * len(extent_polys),
        },
        geometry=extent_polys,
        crs=raster_crs,
    )
    # Dissolve to clean multipolygon
    gdf_extent_utm = gdf_extent_utm.dissolve(by="flooded").reset_index()
    gdf_extent_utm["flooded_area_sqm"] = gdf_extent_utm.geometry.area
    gdf_extent_utm["flooded_area_ha"] = gdf_extent_utm["flooded_area_sqm"] / 10000.0

    # Reproject to WGS84 for web GeoJSON
    gdf_extent_wgs84 = gdf_extent_utm.to_crs("EPSG:4326")
    gdf_extent_wgs84.to_file(outputs_dir / "flood_extent.geojson", driver="GeoJSON")
    gdf_extent_utm.to_file(outputs_dir / "flood_extent.gpkg", driver="GPKG")
    gdf_extent_utm.to_file(outputs_dir / "flood_extent.shp", driver="ESRI Shapefile")

    # Vectorize Hazard Zones
    hazard_class = categorize_hazard_zones(hazard_index, mask)
    haz_names = {
        1: "Low Hazard (Caution)",
        2: "Moderate Hazard (Dangerous for vulnerable persons)",
        3: "Significant Hazard (Dangerous for most persons)",
        4: "Extreme Hazard (Structural damage / High fatality risk)",
    }

    haz_records = []
    for code, desc in haz_names.items():
        h_mask = hazard_class == code
        if not np.any(h_mask):
            continue
        h_polys = []
        for geom, val in shapes(hazard_class, mask=h_mask, transform=raster_transform):
            poly = shape(geom)
            if poly.is_valid and poly.area > 300.0:
                h_polys.append(poly)
        if h_polys:
            for p in h_polys:
                haz_records.append(
                    {
                        "hazard_code": int(code),
                        "hazard_level": desc,
                        "geometry": p,
                    }
                )

    gdf_haz_utm = gpd.GeoDataFrame(haz_records, crs=raster_crs)
    gdf_haz_wgs84 = gdf_haz_utm.to_crs("EPSG:4326")
    gdf_haz_wgs84.to_file(outputs_dir / "hazard_zones.geojson", driver="GeoJSON")
    gdf_haz_utm.to_file(outputs_dir / "hazard_zones.gpkg", driver="GPKG")

    # Copy vectors to outputs folder for web access
    layers["dams"].to_file(outputs_dir / "dam_locations.geojson", driver="GeoJSON")
    layers["river"].to_file(outputs_dir / "river_reach.geojson", driver="GeoJSON")
    layers["infrastructure"].to_file(
        outputs_dir / "critical_infrastructure.geojson", driver="GeoJSON"
    )
    layers["boundary"].to_file(outputs_dir / "study_area_boundary.geojson", driver="GeoJSON")

    # 6. Calculate Damage / Impact Statistics
    infra_utm = layers["infrastructure"].to_crs(raster_crs)
    flooded_geom = gdf_extent_utm.geometry.iloc[0]

    affected_infra = []
    for idx, row in infra_utm.iterrows():
        is_flooded = flooded_geom.intersects(row.geometry.buffer(80.0))
        status = "Inundated / Damaged" if is_flooded else "Safe"
        affected_infra.append(
            {
                "name": row["name"],
                "type": row["type"],
                "vulnerability": row["vulnerability"],
                "flooded": bool(is_flooded),
                "status": status,
            }
        )

    total_flooded_ha = float(gdf_extent_utm["flooded_area_ha"].sum())
    max_flood_depth_m = float(np.max(max_depth))
    mean_flood_depth_m = float(np.mean(max_depth[mask])) if np.any(mask) else 0.0
    max_flow_vel_ms = float(np.max(max_vel))
    mean_flow_vel_ms = float(np.mean(max_vel[mask])) if np.any(mask) else 0.0

    # 6. SPH vs Satellite Hazard Map Overlay (if available)
    sph_extent_file = workspace_root / "src" / "simulation" / "sph" / "case_rishiganga" / "results" / "sph_flood_extent.geojson"
    sat_hazard_file = data_dir / "satellite_flood_extent.geojson"

    overlay_metrics = None
    if sph_extent_file.exists() and sat_hazard_file.exists():
        print("--- 6. Running SPH vs Satellite Hazard Spatial Overlay ---")
        from src.gis.overlay import overlay_sph_on_satellite_hazard
        from src.visualization.map_overlay import plot_sph_satellite_overlay_map

        overlay_res = overlay_sph_on_satellite_hazard(
            sph_extent_path=sph_extent_file,
            satellite_hazard_path=sat_hazard_file,
            output_dir=outputs_dir,
            infrastructure_path=vector_dir / "critical_infrastructure.geojson",
        )
        overlay_metrics = overlay_res.get("spatial_agreement_metrics")

        # Generate cartographic overlay visual map
        plot_sph_satellite_overlay_map(
            overlay_geojson_path=outputs_dir / "sph_satellite_overlay.geojson",
            infrastructure_path=vector_dir / "critical_infrastructure.geojson",
            river_path=vector_dir / "river_centerline.geojson",
            output_image_path=outputs_dir / "sph_satellite_hazard_overlay.png",
            metrics=overlay_metrics,
        )

    summary = {
        "study_area": "Rishi Ganga - Dhauliganga Valley (Chamoli, Uttarakhand)",
        "simulation_scenario": "Dam-Break Outflow Wave Propagation",
        "breach_dam": "Rishi Ganga Small Hydroelectric Project",
        "peak_discharge_m3s": 14500.0,
        "total_volume_released_m3": 6200000.0,
        "crs_computation": "EPSG:32644 (WGS 84 / UTM Zone 44N)",
        "crs_web_export": "EPSG:4326 (WGS 84)",
        "grid_resolution_m": 30.0,
        "metrics": {
            "total_flooded_area_ha": round(total_flooded_ha, 2),
            "total_flooded_area_sqkm": round(total_flooded_ha / 100.0, 3),
            "peak_flood_depth_m": round(max_flood_depth_m, 2),
            "mean_flood_depth_m": round(mean_flood_depth_m, 2),
            "peak_flow_velocity_ms": round(max_flow_vel_ms, 2),
            "mean_flow_velocity_ms": round(mean_flow_vel_ms, 2),
            "min_arrival_time_min": 0.0,
            "max_reach_travel_time_min": round(
                float(np.max(arrival_time[arrival_time < 9000.0])), 1
            ),
        },
        "sph_vs_satellite_overlay": overlay_metrics,
        "affected_critical_infrastructure": affected_infra,
        "exported_files": {
            "vectors": [
                "outputs/flood_extent.geojson",
                "outputs/hazard_zones.geojson",
                "outputs/dam_locations.geojson",
                "outputs/river_reach.geojson",
                "outputs/critical_infrastructure.geojson",
                "outputs/study_area_boundary.geojson",
                "outputs/sph_satellite_overlay.geojson",
                "outputs/sph_satellite_overlay.kml",
            ],
            "rasters": [
                "outputs/flood_depth.tif",
                "outputs/flow_velocity.tif",
                "outputs/hazard_index.tif",
                "outputs/arrival_time.tif",
                "outputs/terrain_hillshade.tif",
            ],
            "visualizations": [
                "outputs/sph_satellite_hazard_overlay.png",
            ],
        },
    }

    metadata_path = outputs_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("--- 7. GIS Pipeline Successfully Completed! ---")
    return summary


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    results = run_full_gis_pipeline(root)
    print(json.dumps(results, indent=2))
