"""
Cartographic Visualization of SPH Flood Simulation vs Satellite Hazard Overlay.
Module: src/visualization/map_overlay.py
Ownership: Member D (GIS / Output Agent)

Generates visual maps displaying:
- SPH Simulated Flood Extent
- Satellite-Detected Flood Hazard Map
- Spatial Overlap / Agreement Zones
- Critical Infrastructure & Settlements
- Valley Terrain / River Centerline
- Summary Metrics Callout
"""

from pathlib import Path
from typing import Optional, Union
import json
import geopandas as gpd


def generate_svg_overlay_map(
    gdf_overlay: gpd.GeoDataFrame,
    gdf_infra: Optional[gpd.GeoDataFrame],
    gdf_river: Optional[gpd.GeoDataFrame],
    output_svg_path: Path,
    metrics: Optional[dict] = None,
    width: int = 1000,
    height: int = 700,
) -> str:
    """
    Generate an ultra-fast, zero-dependency standalone SVG map visualization.
    """
    gdf_wgs84 = gdf_overlay.to_crs("EPSG:4326")
    bounds = gdf_wgs84.total_bounds  # minx, miny, maxx, maxy
    minx, miny, maxx, maxy = bounds

    pad_x = (maxx - minx) * 0.15 if maxx > minx else 0.05
    pad_y = (maxy - miny) * 0.15 if maxy > miny else 0.05
    minx -= pad_x
    maxx += pad_x
    miny -= pad_y
    maxy += pad_y

    def to_screen(x: float, y: float) -> tuple:
        sx = 50 + (x - minx) / (maxx - minx) * (width - 250)
        sy = height - 50 - (y - miny) / (maxy - miny) * (height - 120)
        return sx, sy

    svg_elements = []

    # Background
    svg_elements.append(f'<rect width="{width}" height="{height}" fill="#0f172a" rx="10"/>')
    svg_elements.append(f'<rect x="30" y="30" width="{width-60}" height="{height-60}" fill="#1e293b" stroke="#334155" stroke-width="1.5" rx="6"/>')

    # Grid lines
    for i in range(1, 5):
        gx = 30 + i * (width - 60) / 5
        gy = 30 + i * (height - 60) / 5
        svg_elements.append(f'<line x1="{gx}" y1="30" x2="{gx}" y2="{height-30}" stroke="#334155" stroke-dasharray="4,4" stroke-width="0.8"/>')
        svg_elements.append(f'<line x1="30" y1="{gy}" x2="{width-30}" y2="{gy}" stroke="#334155" stroke-dasharray="4,4" stroke-width="0.8"/>')

    # River centerline
    if gdf_river is not None and not gdf_river.empty:
        gdf_r_wgs84 = gdf_river.to_crs("EPSG:4326")
        for _, row in gdf_r_wgs84.iterrows():
            geom = row.geometry
            if geom and geom.geom_type == "LineString":
                pts = [f"{to_screen(x, y)[0]:.1f},{to_screen(x, y)[1]:.1f}" for x, y in geom.coords]
                svg_elements.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#38bdf8" stroke-width="3.5" stroke-dasharray="6,3" opacity="0.85"/>')

    # Overlay polygons
    cat_colors = {
        "Agreement (Simulated & Observed)": ("#06b6d4", "#0891b2", 0.7),
        "SPH Simulated Only": ("#6366f1", "#4f46e5", 0.6),
        "Satellite Observed Only": ("#f97316", "#ea580c", 0.6),
    }

    for _, row in gdf_wgs84.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        cat = row.get("category", "Overlay")
        fill_col, stroke_col, opacity = cat_colors.get(cat, ("#06b6d4", "#0891b2", 0.6))

        polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        for p in polys:
            pts = [f"{to_screen(x, y)[0]:.1f},{to_screen(x, y)[1]:.1f}" for x, y in p.exterior.coords]
            svg_elements.append(f'<polygon points="{" ".join(pts)}" fill="{fill_col}" stroke="{stroke_col}" stroke-width="2" opacity="{opacity}"/>')

    # Infrastructure points
    if gdf_infra is not None and not gdf_infra.empty:
        gdf_inf_wgs84 = gdf_infra.to_crs("EPSG:4326")
        for _, row in gdf_inf_wgs84.iterrows():
            geom = row.geometry
            if geom and geom.geom_type == "Point":
                sx, sy = to_screen(geom.x, geom.y)
                name = row.get("name", "Asset")
                # Red triangle marker
                tri_pts = f"{sx},{sy-7} {sx+6},{sy+5} {sx-6},{sy+5}"
                svg_elements.append(f'<polygon points="{tri_pts}" fill="#ef4444" stroke="#ffffff" stroke-width="1.2"/>')
                svg_elements.append(f'<text x="{sx+10}" y="{sy+4}" fill="#f1f5f9" font-family="Segoe UI, sans-serif" font-size="10" font-weight="bold">{name}</text>')

    # Title & Header
    svg_elements.append(f'<text x="50" y="65" fill="#f8fafc" font-family="Segoe UI, sans-serif" font-size="18" font-weight="bold">SIH26161: SPH Flood Simulation vs Satellite Hazard Overlay</text>')
    svg_elements.append(f'<text x="50" y="88" fill="#94a3b8" font-family="Segoe UI, sans-serif" font-size="12">Rishi Ganga - Dhauliganga Valley Flood Extent Multi-Model Spatial Validation</text>')

    # Legend Panel
    leg_x = width - 210
    leg_y = 110
    svg_elements.append(f'<rect x="{leg_x-10}" y="{leg_y-10}" width="200" height="230" fill="#0f172a" stroke="#475569" stroke-width="1" rx="6" opacity="0.9"/>')
    svg_elements.append(f'<text x="{leg_x}" y="{leg_y+12}" fill="#e2e8f0" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold">Map Legend</text>')

    items = [
        ("#06b6d4", "Spatial Agreement"),
        ("#6366f1", "SPH Extent Only"),
        ("#f97316", "Satellite Hazard Only"),
        ("#38bdf8", "River Centerline"),
        ("#ef4444", "Critical Infrastructure"),
    ]
    for idx, (col, lbl) in enumerate(items):
        iy = leg_y + 35 + idx * 24
        if lbl == "River Centerline":
            svg_elements.append(f'<line x1="{leg_x}" y1="{iy+5}" x2="{leg_x+18}" y2="{iy+5}" stroke="{col}" stroke-width="3" stroke-dasharray="4,2"/>')
        elif lbl == "Critical Infrastructure":
            svg_elements.append(f'<polygon points="{leg_x+9},{iy} {leg_x+16},{iy+10} {leg_x+2},{iy+10}" fill="{col}" stroke="#fff" stroke-width="0.8"/>')
        else:
            svg_elements.append(f'<rect x="{leg_x}" y="{iy}" width="16" height="12" fill="{col}" stroke="#fff" stroke-width="0.5" rx="2"/>')
        svg_elements.append(f'<text x="{leg_x+26}" y="{iy+10}" fill="#cbd5e1" font-family="Segoe UI, sans-serif" font-size="11">{lbl}</text>')

    # Metrics Panel
    if metrics:
        met_y = leg_y + 175
        iou = metrics.get("iou_jaccard_index", 0.0)
        dice = metrics.get("dice_f1_score", 0.0)
        sph_ha = metrics.get("sph_flooded_area_ha", 0.0)
        sat_ha = metrics.get("satellite_hazard_area_ha", 0.0)

        svg_elements.append(f'<text x="{leg_x}" y="{met_y+15}" fill="#38bdf8" font-family="Segoe UI, sans-serif" font-size="11" font-weight="bold">Validation Metrics</text>')
        svg_elements.append(f'<text x="{leg_x}" y="{met_y+32}" fill="#94a3b8" font-family="Segoe UI, sans-serif" font-size="10">SPH Area: {sph_ha:.1f} ha</text>')
        svg_elements.append(f'<text x="{leg_x}" y="{met_y+47}" fill="#94a3b8" font-family="Segoe UI, sans-serif" font-size="10">Sat Area: {sat_ha:.1f} ha</text>')
        svg_elements.append(f'<text x="{leg_x}" y="{met_y+62}" fill="#94a3b8" font-family="Segoe UI, sans-serif" font-size="10">IoU (Jaccard): {iou:.3f}</text>')
        svg_elements.append(f'<text x="{leg_x}" y="{met_y+77}" fill="#94a3b8" font-family="Segoe UI, sans-serif" font-size="10">Dice Score: {dice:.3f}</text>')

    # North Arrow
    na_x, na_y = 65, height - 70
    svg_elements.append(f'<circle cx="{na_x}" cy="{na_y}" r="18" fill="#0f172a" stroke="#64748b" stroke-width="1.2"/>')
    svg_elements.append(f'<polygon points="{na_x},{na_y-13} {na_x+5},{na_y+5} {na_x},{na_y+2} {na_x-5},{na_y+5}" fill="#38bdf8"/>')
    svg_elements.append(f'<text x="{na_x}" y="{na_y+13}" fill="#e2e8f0" font-family="Segoe UI, sans-serif" font-size="9" font-weight="bold" text-anchor="middle">N</text>')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
{chr(10).join(svg_elements)}
</svg>'''

    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return str(output_svg_path)


def plot_sph_satellite_overlay_map(
    overlay_geojson_path: Union[str, Path],
    infrastructure_path: Optional[Union[str, Path]],
    river_path: Optional[Union[str, Path]],
    output_image_path: Union[str, Path],
    metrics: Optional[dict] = None,
) -> str:
    """
    Render and save cartographic map comparing SPH Simulation and Satellite Hazard.
    Supports Matplotlib PNG generation if installed, with native SVG generation always guaranteed.
    """
    overlay_geojson_path = Path(overlay_geojson_path)
    output_image_path = Path(output_image_path)
    output_image_path.parent.mkdir(parents=True, exist_ok=True)

    gdf_overlay = gpd.read_file(overlay_geojson_path)
    gdf_infra = gpd.read_file(infrastructure_path) if infrastructure_path and Path(infrastructure_path).exists() else None
    gdf_river = gpd.read_file(river_path) if river_path and Path(river_path).exists() else None

    # Always generate SVG map
    svg_path = output_image_path.with_suffix(".svg")
    generate_svg_overlay_map(gdf_overlay, gdf_infra, gdf_river, svg_path, metrics)

    # Attempt Matplotlib PNG generation if available
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Patch

        gdf_wgs84 = gdf_overlay.to_crs("EPSG:4326")
        fig, ax = plt.subplots(figsize=(12, 9), dpi=200)

        category_colors = {
            "Agreement (Simulated & Observed)": ("#00bcd4", "#00838f", 0.75, "Spatial Agreement (SPH + Satellite)"),
            "SPH Simulated Only": ("#3f51b5", "#283593", 0.55, "SPH Simulation Extent Only"),
            "Satellite Observed Only": ("#ff5722", "#d84315", 0.55, "Satellite SAR Hazard Only"),
        }

        if gdf_river is not None:
            gdf_r = gdf_river.to_crs("EPSG:4326")
            gdf_r.plot(ax=ax, color="#1976d2", linewidth=2.5, linestyle="--", alpha=0.8, label="River Centerline Reach", zorder=2)

        legend_patches = []
        for cat_name, (face_col, edge_col, alpha_val, label_text) in category_colors.items():
            subset = gdf_wgs84[gdf_wgs84["category"] == cat_name]
            if not subset.empty:
                subset.plot(ax=ax, color=face_col, edgecolor=edge_col, linewidth=1.2, alpha=alpha_val, zorder=3)
                legend_patches.append(Patch(facecolor=face_col, edgecolor=edge_col, alpha=alpha_val, label=label_text))

        if gdf_infra is not None:
            gdf_inf = gdf_infra.to_crs("EPSG:4326")
            gdf_inf.plot(ax=ax, color="#d50000", marker="^", markersize=80, edgecolor="black", linewidth=1.0, label="Critical Infrastructure", zorder=5)
            for _, row in gdf_inf.iterrows():
                ax.annotate(
                    row.get("name", ""),
                    xy=(row.geometry.x, row.geometry.y),
                    xytext=(6, 6),
                    textcoords="offset points",
                    fontsize=8,
                    fontweight="bold",
                    color="#212121",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor="#bdbdbd", lw=0.5),
                    zorder=6,
                )

        ax.set_title(
            "SIH26161: SPH Dam-Break Simulation vs Satellite SAR Hazard Map Overlay\n"
            "Rishi Ganga - Dhauliganga Valley Flood Extent Validation",
            fontsize=13,
            fontweight="bold",
            pad=14,
        )
        ax.set_xlabel("Longitude (Degrees East)", fontsize=10)
        ax.set_ylabel("Latitude (Degrees North)", fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.6, color="#9e9e9e")

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=legend_patches + handles, loc="upper right", framealpha=0.92, fontsize=8.5)

        plt.tight_layout()
        plt.savefig(output_image_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        return str(output_image_path)

    except ImportError:
        # Return generated SVG path if matplotlib is absent
        return str(svg_path)
