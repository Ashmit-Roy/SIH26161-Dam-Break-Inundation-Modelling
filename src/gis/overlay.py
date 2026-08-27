"""
SPH Hydrodynamic Simulation & Satellite Hazard Map Overlay Module.
Module: src/gis/overlay.py
Ownership: Member D (GIS / Output Agent)

Performs spatial overlays and quantitative validation between:
1. SPH Simulated Flood Inundation Extent (DualSPHysics / SPH Agent)
2. Satellite-Detected Hazard Extent (Sentinel-1 SAR / GEE ML Classifier)
3. Critical Infrastructure & Habitations

Generates:
- Multi-category spatial agreement polygons (Agreement, Simulated Only, Satellite Only)
- Quantitative validation metrics (IoU, Dice/F1, CSI, Hit Rate, False Alarm Ratio)
- Standard GIS outputs: GeoJSON (WGS84), GeoPackage (UTM 44N), Shapefile, KML, and JSON report.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import geopandas as gpd
import numpy as np
from shapely.geometry import MultiPolygon, Point, Polygon
from shapely.ops import unary_union


def compute_spatial_agreement_metrics(
    geom_sim: Union[Polygon, MultiPolygon],
    geom_obs: Union[Polygon, MultiPolygon],
) -> Dict[str, float]:
    """
    Compute quantitative GIS comparison metrics between simulated (SPH) and observed (Satellite) extents.
    Assumes geometries are in a projected, metre-based CRS (e.g., EPSG:32644).

    Metrics:
    - Area SPH (ha, km2)
    - Area Satellite (ha, km2)
    - Area Intersection / Agreement (ha, km2)
    - Area Union (ha, km2)
    - Intersection over Union (IoU / Jaccard Index): A_int / A_union
    - Dice Coefficient (F1 Score): 2 * A_int / (A_sim + A_obs)
    - Critical Success Index (CSI): A_int / (A_sim + A_obs - A_int)
    - Hit Rate / True Positive Rate (TPR / Recall): A_int / A_obs
    - False Alarm Ratio (FAR): (A_sim - A_int) / A_sim
    """
    area_sim = float(geom_sim.area) if geom_sim and not geom_sim.is_empty else 0.0
    area_obs = float(geom_obs.area) if geom_obs and not geom_obs.is_empty else 0.0

    if area_sim > 0.0 and area_obs > 0.0 and geom_sim.intersects(geom_obs):
        geom_int = geom_sim.intersection(geom_obs)
        area_int = float(geom_int.area)
    else:
        area_int = 0.0

    if area_sim > 0.0 or area_obs > 0.0:
        geom_union = unary_union([geom_sim, geom_obs])
        area_union = float(geom_union.area)
    else:
        area_union = 0.0

    # IoU / Jaccard
    iou = area_int / area_union if area_union > 0.0 else 0.0

    # Dice / F1
    dice = (2.0 * area_int) / (area_sim + area_obs) if (area_sim + area_obs) > 0.0 else 0.0

    # Critical Success Index (CSI)
    denom_csi = area_sim + area_obs - area_int
    csi = area_int / denom_csi if denom_csi > 0.0 else 0.0

    # Hit Rate / Recall (TPR)
    hit_rate = area_int / area_obs if area_obs > 0.0 else 0.0

    # False Alarm Ratio (FAR)
    area_sim_only = max(0.0, area_sim - area_int)
    far = area_sim_only / area_sim if area_sim > 0.0 else 0.0

    return {
        "sph_flooded_area_sqm": round(area_sim, 2),
        "sph_flooded_area_ha": round(area_sim / 10000.0, 2),
        "sph_flooded_area_km2": round(area_sim / 1e6, 4),
        "satellite_hazard_area_sqm": round(area_obs, 2),
        "satellite_hazard_area_ha": round(area_obs / 10000.0, 2),
        "satellite_hazard_area_km2": round(area_obs / 1e6, 4),
        "agreement_intersection_area_sqm": round(area_int, 2),
        "agreement_intersection_area_ha": round(area_int / 10000.0, 2),
        "agreement_intersection_area_km2": round(area_int / 1e6, 4),
        "combined_union_area_sqm": round(area_union, 2),
        "combined_union_area_ha": round(area_union / 10000.0, 2),
        "combined_union_area_km2": round(area_union / 1e6, 4),
        "iou_jaccard_index": round(iou, 4),
        "dice_f1_score": round(dice, 4),
        "critical_success_index": round(csi, 4),
        "hit_rate_sensitivity": round(hit_rate, 4),
        "false_alarm_ratio": round(far, 4),
    }


def generate_overlay_kml(
    gdf_overlay: gpd.GeoDataFrame,
    output_path: Union[str, Path],
    title: str = "SPH Simulation vs Satellite Hazard Overlay",
) -> str:
    """
    Generate an OGC KML file with distinct styling for:
    - Spatial Agreement (Simulated & Observed) -> Cyan/Teal
    - SPH Simulated Extent Only -> Blue
    - Satellite Hazard Extent Only -> Amber/Orange
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    gdf_wgs84 = gdf_overlay.to_crs("EPSG:4326") if gdf_overlay.crs and gdf_overlay.crs.to_epsg() != 4326 else gdf_overlay

    styles = {
        "Agreement (Simulated & Observed)": {
            "line_color": "ff00d0ff",  # AABBGGRR (bright cyan)
            "poly_color": "8000d0ff",
        },
        "SPH Simulated Only": {
            "line_color": "ffff8000",  # bright blue
            "poly_color": "80ff8000",
        },
        "Satellite Observed Only": {
            "line_color": "ff0080ff",  # amber/orange
            "poly_color": "800080ff",
        },
    }

    placemarks = []
    for idx, row in gdf_wgs84.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue

        cat = row.get("category", "Overlay")
        style = styles.get(cat, {"line_color": "ffffffff", "poly_color": "80ffffff"})
        area_ha = row.get("area_ha", 0.0)

        poly_list = []
        if geom.geom_type == "Polygon":
            coords = " ".join([f"{x},{y},0" for x, y in geom.exterior.coords])
            poly_list.append(f"<Polygon><outerBoundaryIs><LinearRing><coordinates>{coords}</coordinates></LinearRing></outerBoundaryIs></Polygon>")
        elif geom.geom_type == "MultiPolygon":
            for p in geom.geoms:
                coords = " ".join([f"{x},{y},0" for x, y in p.exterior.coords])
                poly_list.append(f"<Polygon><outerBoundaryIs><LinearRing><coordinates>{coords}</coordinates></LinearRing></outerBoundaryIs></Polygon>")

        geom_kml = poly_list[0] if len(poly_list) == 1 else f"<MultiGeometry>{''.join(poly_list)}</MultiGeometry>"

        placemark = f"""  <Placemark>
    <name>{cat}</name>
    <description>Area: {area_ha:.2f} ha | SIH 26161 Dam Break Inundation Modelling</description>
    <Style>
      <LineStyle><color>{style['line_color']}</color><width>2</width></LineStyle>
      <PolyStyle><color>{style['poly_color']}</color></PolyStyle>
    </Style>
    {geom_kml}
  </Placemark>"""
        placemarks.append(placemark)

    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>{title}</name>
  <description>DualSPHysics SPH Simulated Inundation Extent overlaid on Sentinel-1 SAR Satellite Hazard Map</description>
{chr(10).join(placemarks)}
</Document>
</kml>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(kml_content)

    return str(output_path)


def overlay_sph_on_satellite_hazard(
    sph_extent_path: Union[str, Path],
    satellite_hazard_path: Union[str, Path],
    output_dir: Union[str, Path],
    infrastructure_path: Optional[Union[str, Path]] = None,
    computation_crs: str = "EPSG:32644",
) -> Dict[str, Any]:
    """
    Perform end-to-end overlay analysis between SPH simulated extent and Satellite Hazard Map.

    Parameters:
    - sph_extent_path: Path to sph_flood_extent.geojson
    - satellite_hazard_path: Path to satellite_flood_extent.geojson or hazard map
    - output_dir: Directory to save processed overlay layers and metrics report
    - infrastructure_path: Optional path to critical infrastructure vector layer
    - computation_crs: Projected CRS for metric area computations (default: EPSG:32644)

    Returns:
    - Dictionary with validation metrics, overlay file paths, and infrastructure impacts.
    """
    sph_extent_path = Path(sph_extent_path)
    satellite_hazard_path = Path(satellite_hazard_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not sph_extent_path.exists():
        raise FileNotFoundError(f"SPH flood extent file not found: {sph_extent_path}")
    if not satellite_hazard_path.exists():
        raise FileNotFoundError(f"Satellite hazard file not found: {satellite_hazard_path}")

    # Load SPH extent
    gdf_sph = gpd.read_file(sph_extent_path)
    if gdf_sph.empty:
        raise ValueError("SPH flood extent dataset is empty.")
    if gdf_sph.crs is None:
        # Default SPH output CRS is EPSG:32644
        gdf_sph.set_crs(computation_crs, inplace=True)

    gdf_sph_utm = gdf_sph.to_crs(computation_crs)
    sph_geom_utm = unary_union(gdf_sph_utm.geometry)

    # Load Satellite Hazard extent
    gdf_sat = gpd.read_file(satellite_hazard_path)
    if gdf_sat.empty:
        raise ValueError("Satellite hazard dataset is empty.")
    if gdf_sat.crs is None:
        gdf_sat.set_crs("EPSG:4326", inplace=True)

    gdf_sat_utm = gdf_sat.to_crs(computation_crs)
    sat_geom_utm = unary_union(gdf_sat_utm.geometry)

    # Spatial Overlay Calculations
    # 1. Agreement / Intersection
    geom_agreement = sph_geom_utm.intersection(sat_geom_utm) if sph_geom_utm.intersects(sat_geom_utm) else Polygon()
    # 2. SPH Only (Simulated but not satellite-observed)
    geom_sph_only = sph_geom_utm.difference(sat_geom_utm) if not sph_geom_utm.is_empty else Polygon()
    # 3. Satellite Only (Satellite-flagged but not reached by SPH)
    geom_sat_only = sat_geom_utm.difference(sph_geom_utm) if not sat_geom_utm.is_empty else Polygon()
    # 4. Union
    geom_union = unary_union([sph_geom_utm, sat_geom_utm])

    # Quantitative GIS metrics
    metrics = compute_spatial_agreement_metrics(sph_geom_utm, sat_geom_utm)

    # Construct Categorized GeoDataFrame
    records = []
    if not geom_agreement.is_empty and geom_agreement.area > 0.0:
        records.append({
            "category_code": 1,
            "category": "Agreement (Simulated & Observed)",
            "description": "Area inundated in both SPH 3D simulation and Satellite SAR detection",
            "fill_color": "#00d0ff",
            "stroke_color": "#0088cc",
            "area_sqm": round(float(geom_agreement.area), 2),
            "area_ha": round(float(geom_agreement.area) / 10000.0, 2),
            "geometry": geom_agreement,
        })

    if not geom_sph_only.is_empty and geom_sph_only.area > 0.0:
        records.append({
            "category_code": 2,
            "category": "SPH Simulated Only",
            "description": "Area inundated by DualSPHysics SPH model not detected in satellite pass",
            "fill_color": "#ff9900",
            "stroke_color": "#cc6600",
            "area_sqm": round(float(geom_sph_only.area), 2),
            "area_ha": round(float(geom_sph_only.area) / 10000.0, 2),
            "geometry": geom_sph_only,
        })

    if not geom_sat_only.is_empty and geom_sat_only.area > 0.0:
        records.append({
            "category_code": 3,
            "category": "Satellite Observed Only",
            "description": "Area flagged by Sentinel-1 SAR / GEE not reached by SPH model extent",
            "fill_color": "#ff3366",
            "stroke_color": "#b3002d",
            "area_sqm": round(float(geom_sat_only.area), 2),
            "area_ha": round(float(geom_sat_only.area) / 10000.0, 2),
            "geometry": geom_sat_only,
        })

    if not records:
        # Fallback if extents are disjoint / empty
        records.append({
            "category_code": 2,
            "category": "SPH Simulated Only",
            "description": "DualSPHysics Inundation Extent",
            "fill_color": "#ff9900",
            "stroke_color": "#cc6600",
            "area_sqm": round(float(sph_geom_utm.area), 2),
            "area_ha": round(float(sph_geom_utm.area) / 10000.0, 2),
            "geometry": sph_geom_utm,
        })

    gdf_overlay_utm = gpd.GeoDataFrame(records, crs=computation_crs)
    gdf_overlay_wgs84 = gdf_overlay_utm.to_crs("EPSG:4326")

    # Save Vector formats
    geojson_out = output_dir / "sph_satellite_overlay.geojson"
    gpkg_out = output_dir / "sph_satellite_overlay.gpkg"
    shp_out = output_dir / "sph_satellite_overlay.shp"
    kml_out = output_dir / "sph_satellite_overlay.kml"

    gdf_overlay_wgs84.to_file(geojson_out, driver="GeoJSON")
    gdf_overlay_utm.to_file(gpkg_out, driver="GPKG")
    gdf_overlay_utm.to_file(shp_out, driver="ESRI Shapefile")
    generate_overlay_kml(gdf_overlay_wgs84, kml_out, "SPH Simulation vs Satellite Hazard Overlay")

    # Infrastructure Exposure Analysis
    infra_results = []
    if infrastructure_path and Path(infrastructure_path).exists():
        gdf_infra = gpd.read_file(infrastructure_path)
        gdf_infra_utm = gdf_infra.to_crs(computation_crs)

        for idx, row in gdf_infra_utm.iterrows():
            pt_geom = row.geometry
            # Check proximity / intersection with 60m tolerance
            buf = pt_geom.buffer(60.0)
            in_sph = bool(buf.intersects(sph_geom_utm))
            in_sat = bool(buf.intersects(sat_geom_utm))
            in_agree = bool(buf.intersects(geom_agreement))

            zone_status = "Safe"
            if in_agree:
                zone_status = "High Confidence Hazard (Simulated + Satellite Confirmed)"
            elif in_sph:
                zone_status = "Simulated Hazard (SPH Predicted)"
            elif in_sat:
                zone_status = "Satellite Hazard (Observation Flagged)"

            infra_results.append({
                "name": row.get("name", f"Asset #{idx+1}"),
                "type": row.get("type", "Infrastructure"),
                "vulnerability": row.get("vulnerability", "Moderate"),
                "in_sph_extent": in_sph,
                "in_satellite_extent": in_sat,
                "in_agreement_zone": in_agree,
                "exposure_assessment": zone_status,
            })

    # Generate Structured Validation & Comparison Report
    validation_report = {
        "title": "SPH Hydrodynamic Simulation vs Satellite SAR Hazard Map Spatial Validation",
        "scenario": "Rishi Ganga Dam Break / Flash Flood Hydrodynamic Wave",
        "models_evaluated": {
            "simulation_model": "DualSPHysics SPH (Smoothed Particle Hydrodynamics)",
            "satellite_observation": "Sentinel-1 IW GRD SAR (GEE Feature Extraction + RF Classifier)",
        },
        "crs_used": {
            "computation": computation_crs,
            "web_export": "EPSG:4326 (WGS 84)",
        },
        "spatial_agreement_metrics": metrics,
        "infrastructure_exposure_analysis": infra_results,
        "exported_files": {
            "overlay_geojson": str(geojson_out.relative_to(output_dir.parent) if output_dir.parent in geojson_out.parents else geojson_out),
            "overlay_gpkg": str(gpkg_out.relative_to(output_dir.parent) if output_dir.parent in gpkg_out.parents else gpkg_out),
            "overlay_shp": str(shp_out.relative_to(output_dir.parent) if output_dir.parent in shp_out.parents else shp_out),
            "overlay_kml": str(kml_out.relative_to(output_dir.parent) if output_dir.parent in kml_out.parents else kml_out),
        },
    }

    report_json_path = output_dir / "sph_satellite_validation_report.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(validation_report, f, indent=2)

    return validation_report


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent
    sph_extent = repo_root / "src" / "simulation" / "sph" / "case_rishiganga" / "results" / "sph_flood_extent.geojson"
    satellite_hazard = repo_root / "data" / "satellite_flood_extent.geojson"
    infra_path = repo_root / "data" / "vector" / "critical_infrastructure.geojson"
    out_dir = repo_root / "outputs"

    print("Running SPH vs Satellite Hazard Overlay Pipeline...")
    res = overlay_sph_on_satellite_hazard(
        sph_extent_path=sph_extent,
        satellite_hazard_path=satellite_hazard,
        output_dir=out_dir,
        infrastructure_path=infra_path,
    )
    print("Overlay Analysis Complete!")
    print(f"  * IoU / Jaccard: {res['spatial_agreement_metrics']['iou_jaccard_index']}")
    print(f"  * Dice F1 Score: {res['spatial_agreement_metrics']['dice_f1_score']}")
    print(f"  * SPH Flooded Area: {res['spatial_agreement_metrics']['sph_flooded_area_ha']} ha")
    print(f"  * Satellite Hazard Area: {res['spatial_agreement_metrics']['satellite_hazard_area_ha']} ha")
