# API Contract

> Owner: **Dashboard Agent** owns implementation details. Any change affecting simulation/GIS/GEE interfaces must be coordinated with the relevant owners (AGENTS.md §24).

**Status:** Placeholder. Define endpoints/schemas here **before** implementing them, and keep frontend/backend contracts synchronized.

## 1. Conventions

- Base URL: TBD
- All request/response bodies use JSON unless stated otherwise.
- All inputs are validated; invalid requests return structured errors.
- No endpoint may be invented in code without being documented here first (AGENTS.md §34).

## 2. Simulation

### 2.1 Create / Run Simulation

```text
TBD — method, path, request schema, response schema
```

### 2.2 Simulation Status / Progress

```text
TBD
```

## 3. Results

### 3.1 Common Simulation Result Object

Normalized representation shared by SPH and Delft3D results before downstream consumption (AGENTS.md §18):

```json
{
  "simulation_id": "TBD",
  "model": "sph | delft3d",
  "scenario_id": "TBD",
  "crs": "TBD",
  "terrain_reference": "TBD",
  "water_depth": null,
  "water_level": null,
  "velocity": null,
  "arrival_time": null,
  "flood_extent": null,
  "simulation_time": null,
  "metadata": {}
}
```

Do not add/remove fields without checking all consumers and coordinating the change (AGENTS.md §18).

### 3.2 Comparison (SPH vs Delft3D)

```text
TBD — flood extent, water depth, arrival time, computational time
```

## 4. Damage / Loss Analysis

```text
TBD — population, land use, roads, bridges/infrastructure
```

## 5. GIS Outputs / Downloads

```text
TBD — flood-depth raster, extent polygons (.shp/.kml/GeoJSON)
```

## 6. Near-Real-Time Flood Detection (GEE)

```text
TBD
```

## 7. Error Responses

```json
{
  "error": {
    "code": "TBD",
    "message": "TBD",
    "details": {}
  }
}
```

Critical failures must not be silently swallowed (AGENTS.md §35).
