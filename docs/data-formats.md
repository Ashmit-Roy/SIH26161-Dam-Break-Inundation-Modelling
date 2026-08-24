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
| Format | TBD (GeoTIFF expected) |
| Units | metres |
| CRS | TBD |

### 3.2 Flood Extent Polygons

| Property | Value |
|---|---|
| Formats | `.shp`, `.kml`, GeoJSON where appropriate |

### 3.3 Common Simulation Output

Normalized result representation consumed by GIS/Dashboard — see [api-contract.md](api-contract.md).

## 4. Validation Rules

All ingested files must be validated for: existence, readable metadata, CRS presence, value ranges, and missing-data handling. Numerical failures must not be silently ignored (AGENTS.md §35).
