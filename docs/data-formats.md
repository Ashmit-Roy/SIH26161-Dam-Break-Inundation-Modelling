# Data Formats

> Ownership: **Data Agent** owns data-ingestion specifications; **GIS Agent** owns GIS output specifications (AGENTS.md §24). Do not modify another owner's section without coordination.

**Status:** Placeholder. Fill in only formats that are actually implemented or agreed. Label all sample data as `SAMPLE DATA` / `DEMO DATA` — see AGENTS.md §33.

## 1. Input Data

### 1.1 Terrain / DEM

| Property | Value |
|---|---|
| Format | TBD (e.g., GeoTIFF) |
| CRS | TBD |
| Resolution | TBD |
| NoData handling | TBD |

### 1.2 Dam / Breach Parameters

| Field | Type | Units | Constraints |
|---|---|---|---|
| TBD | TBD | TBD | TBD |

### 1.3 Auxiliary Datasets

- Population: TBD
- Land use: TBD
- Roads: TBD
- Bridges/infrastructure: TBD

## 2. Simulation Inputs

- SPH / DualSPHysics case configuration: see [simulation-spec.md](simulation-spec.md)
- Delft3D model configuration: see [simulation-spec.md](simulation-spec.md)

## 3. Output Data

### 3.1 Flood-Depth Raster

| Property | Value |
|---|---|
| File Path | `outputs/flood_depth.tif` |
| Format | Cloud-Optimized GeoTIFF (`GTiff`) |
| Data Type | `float32` |
| Units | Metres (`m`) above local terrain |
| CRS | `EPSG:32644` (WGS 84 / UTM Zone 44N) |
| Resolution | 30.0 m × 30.0 m |
| NoData Value | `-9999.0` |

### 3.2 Flood Velocity Raster

| Property | Value |
|---|---|
| File Path | `outputs/flow_velocity.tif` |
| Format | Cloud-Optimized GeoTIFF (`GTiff`) |
| Data Type | `float32` |
| Units | Metres per second (`m/s`) |
| CRS | `EPSG:32644` (WGS 84 / UTM Zone 44N) |
| Resolution | 30.0 m × 30.0 m |
| NoData Value | `-9999.0` |

### 3.3 Flood Hazard Rating Raster

| Property | Value |
|---|---|
| File Path | `outputs/hazard_index.tif` |
| Format | GeoTIFF (`GTiff`) |
| Formulation | DEFRA Standard: $HR = d \times (v + 0.5) + DF$ |
| CRS | `EPSG:32644` (WGS 84 / UTM Zone 44N) |

### 3.4 Flood Extent Polygons

| Property | Value |
|---|---|
| File Paths | `outputs/flood_extent.geojson` (Web) / `outputs/flood_extent.shp` (GIS) / `outputs/flood_extent.gpkg` |
| Formats | GeoJSON (RFC 7946), ESRI Shapefile, OGC GeoPackage |
| Web CRS | `EPSG:4326` (WGS 84 geographic coordinates) |
| Projected CRS | `EPSG:32644` (for Shapefile and GeoPackage) |
| Schema Fields | `scenario` (string), `flooded` (int), `min_depth_m` (float), `flooded_area_ha` (float) |

### 3.5 Flood Hazard Zones Polygons

| Property | Value |
|---|---|
| File Paths | `outputs/hazard_zones.geojson` (Web) / `outputs/hazard_zones.gpkg` |
| Format | GeoJSON, GeoPackage |
| Classification | 1: Low Hazard, 2: Moderate Hazard, 3: Significant Hazard, 4: Extreme Hazard |

### 3.6 Summary Metadata

| Property | Value |
|---|---|
| File Path | `outputs/metadata.json` |
| Contents | Flood area (ha), peak depth, peak velocity, wave arrival time, and infrastructure vulnerability status |

### 3.7 SPH vs Satellite Hazard Overlay Layers

| Property | Value |
|---|---|
| File Paths | `outputs/sph_satellite_overlay.geojson` (Web) / `outputs/sph_satellite_overlay.gpkg` / `outputs/sph_satellite_overlay.shp` / `outputs/sph_satellite_overlay.kml` |
| Formats | GeoJSON (RFC 7946), OGC GeoPackage, ESRI Shapefile, OGC KML |
| Web / KML CRS | `EPSG:4326` (WGS 84 geographic coordinates) |
| Projected CRS | `EPSG:32644` (WGS 84 / UTM Zone 44N) |
| Categories | 1: Agreement (Simulated & Observed), 2: SPH Simulated Only, 3: Satellite Observed Only |
| Schema Fields | `category_code` (int), `category` (string), `description` (string), `fill_color` (hex), `stroke_color` (hex), `area_ha` (float), `area_sqm` (float) |

### 3.8 SPH vs Satellite Validation Report

| Property | Value |
|---|---|
| File Path | `outputs/sph_satellite_validation_report.json` |
| Metrics | IoU (Jaccard Index), Dice / F1 Score, Critical Success Index (CSI), Hit Rate / Sensitivity (TPR), False Alarm Ratio (FAR), SPH Area (ha), Satellite Area (ha), Agreement Area (ha) |

### 3.9 Delft3D GIS Deliverables & Shapefiles

| Property | Value |
|---|---|
| File Paths | `outputs/delft3d_flood_extent.shp` / `.gpkg` / `.geojson`, `outputs/delft3d_damaged_roads.shp` / `.gpkg` / `.geojson`, `outputs/delft3d_damaged_bridges.shp` / `.gpkg` / `.geojson` |
| Formats | ESRI Shapefile (`.shp`), OGC GeoPackage (`.gpkg`), GeoJSON (`.geojson`), OGC KML (`.kml`) |
| Raster Inputs | `delft3d_max_depth.tif`, `delft3d_arrival_time.tif` (or ASCII Grid / NetCDF) |
| Projected CRS | `EPSG:32644` (WGS 84 / UTM Zone 44N) |
| Web / KML CRS | `EPSG:4326` (WGS 84 geographic coordinates) |

### 3.10 Road & Bridge Spatial Damage Assessment

| Property | Value |
|---|---|
| File Path | `outputs/delft3d_road_bridge_damage_assessment.json` |
| KML Export | `outputs/delft3d_dam_break_damage_assessment.kml` |
| Road Assessment | Flooded segment length (km), percentage inundated, accessibility severance, severity class, replacement cost (INR) |
| Bridge Assessment | Bridge location, deck elevation, overtopping water depth (m), structural risk (washout vs submerged deck), replacement cost (INR) |

## 4. Validation Rules

All ingested files must be validated for: existence, readable metadata, CRS presence, value ranges, and missing-data handling. Numerical failures must not be silently ignored (AGENTS.md §35).


