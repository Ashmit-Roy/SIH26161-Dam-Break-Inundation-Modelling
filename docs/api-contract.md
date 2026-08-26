# API Contract

> Owner: **Dashboard Agent** owns implementation details. Any change affecting simulation/GIS/GEE interfaces must be coordinated with the relevant owners (AGENTS.md §24).

**Status:** Active. This document defines the API contract between the frontend dashboard and backend simulation services.

## 1. Conventions

- **Base URL:** `http://127.0.0.1:8000` (development) or `VITE_API_BASE` environment variable
- All request/response bodies use JSON unless stated otherwise.
- All inputs are validated; invalid requests return structured error responses.
- Status codes: `200` for success, `400` for validation errors, `404` for not found, `500` for server errors.

## 2. Simulation Endpoints

### 2.1 POST /api/simulation/start

Start a new hydrodynamic simulation (SPH or Delft3D).

**Request Schema (SimulationRequest):**

| Field | Type | Required | Description |
|---|---|---|---|
| `simulation_id` | `string` | ✓ | Unique simulation identifier |
| `model` | `ModelType` | ✓ | Hydraulic model: `"SPH"` or `"Delft3D"` |
| `scenario_id` | `string` | ✓ | Scenario identifier |
| `breach_width` | `number` | Optional | Breach width in meters |
| `breach_height` | `number` | Optional | Breach height in meters |
| `simulation_time` | `number` | Optional | Simulation time in seconds |
| `crs` | `string` | Optional | Coordinate reference system (default: `"EPSG:4326"`) |

**Response (SimulationResult):**

| Field | Type | Description |
|---|---|---|
| `simulation_id` | `string` | Unique simulation identifier |
| `model` | `ModelType` | Hydraulic model used |
| `scenario_id` | `string` | Scenario identifier |
| `breach_width` | `number` | Breach width in meters |
| `breach_height` | `number` | Breach height in meters |
| `water_depth` | `WaterDepthResult` | Water depth result at location |
| `flood_extent` | `FloodExtentResult` | Flood extent polygon and arrival time |
| `comparison?` | `ModelComparison` | SPH vs Delft3D comparison (if model is "both") |
| `timestamp` | `string` | ISO8601 timestamp of result generation |

**WaterDepthResult:**

| Field | Type | Description |
|---|---|---|
| `simulation_id` | `string` | Link to simulation |
| `location` | `Location` | `{ lat: number, lon: number }` |
| `water_depth` | `number` | Water depth in meters |
| `timestamp?` | `string` | ISO8601 timestamp |

**FloodExtentResult:**

| Field | Type | Description |
|---|---|---|
| `simulation_id` | `string` | Link to simulation |
| `polygon` | `GeoJSON Polygon` | Flood extent geometry |
| `arrival_time?` | `number` | Time to flood arrival in seconds |

**ModelComparison:**

| Field | Type | Description |
|---|---|---|
| `metric` | `ComparisonMetric` | Comparison metric (e.g., `"water_depth"`) |
| `sph_data` | `WaterDepthResult` | SPH result data |
| `delft3d_data` | `WaterDepthResult` | Delft3D result data |
| `overlap_area?` | `number` | Overlapping flood area in m² (optional) |
| `timestamp` | `string` | Comparison timestamp |

**Location:**

| Field | Type | Description |
|---|---|---|
| `lat` | `number` | Latitude in decimal degrees |
| `lon` | `number` | Longitude in decimal degrees |

**ComparisonMetric enum:**

| Value | Description |
|---|---|
| `flood_extent` | Flood extent comparison |
| `water_depth` | Water depth comparison |
| `arrival_time` | Arrival time comparison |
| `computational_time` | Computational time comparison |

### 2.2 GET /api/simulation/status/{simulationId}

Check simulation progress status.

**Response:**

| Field | Type | Description |
|---|---|---|
| `status` | `SimulationStatus` | One of: `"idle"`, `"uploading"`, `"running"`, `"completed"`, `"failed"`, `"timed_out"` |
| `progress` | `number` | Progress percentage 0-100 |

**SimulationStatus enum:**

| Value | Description |
|---|---|
| `idle` | No simulation running |
| `uploading` | Input data being uploaded |
| `running` | Simulation in progress |
| `completed` | Simulation finished successfully |
| `failed` | Simulation terminated with error |
| `timed_out` | Simulation exceeded time limit |

### 2.3 GET /api/results/{simulationId}

Get full simulation result by ID.

**Response:** `SimulationResult` (as defined in §2.1)

### 2.4 GET /api/results/comparison/{simulationId}

Get SPH vs Delft3D comparison metrics.

**Response:** `ModelComparison` (as defined in §2.1)

### 2.5 GET /api/results/{simulationId}/extent

Get flood extent GeoJSON for map display.

**Response:** `FloodExtentResult` (as defined in §2.1)

### 2.6 POST /api/results/download

Download simulation results in specified format.

**Request (DownloadableOutput):**

| Field | Type | Required | Description |
|---|---|---|---|
| `format` | `DownloadableOutput` | ✓ | Output format: `"shp"`, `"kml"`, or `"geojson"` |
| `simulation_id` | `string` | ✓ | Simulation to download |
| `crs?` | `string` | Optional | Target CRS (default: `"EPSG:4326"`) |

**Response:**

| Field | Type | Description |
|---|---|---|
| `success` | `boolean` | Whether download was initiated |
| `filename` | `string` | Suggested filename (e.g., `"sim123.geojson"`) |
| `format` | `DownloadableOutput` | Requested format |

### 2.7 POST /api/simulation/state

Update dashboard state.

**Request (Partial<DashboardState>):**

| Field | Type | Description |
|---|---|---|
| `current_simulation?` | `string` | Active simulation ID |
| `simulation_progress?` | `number` | Progress 0-100% |
| `comparison_active?` | `boolean` | Whether comparison is active |
| `last_update?` | `string` | ISO8601 timestamp |

**Response:** `DashboardState`

### 2.8 GET /api/simulation/state

Get current dashboard state.

**Response:** `DashboardState`

## 3. Error Responses

All endpoints return structured error objects on failure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR | NOT_FOUND | INTERNAL_ERROR",
    "message": "Human-readable error description",
    "details": {
      "field": "Specific field that caused the error",
      "received": "Value that was provided",
      "expected": "Expected format or value"
    }
  }
}
```

**Validation Error (400):**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more required fields are missing or invalid",
    "details": {
      "field": "simulation_id",
      "received": "",
      "expected": "Non-empty string"
    }
  }
}
```

**Not Found (404):**

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Simulation result not found",
    "details": {}
  }
}
```

## 4. Response Codes Summary

| Code | Meaning |
|---|---|
| `200` | Success - request understood and processed |
| `202` | Accepted - simulation started, not yet complete |
| `400` | Bad Request - validation failed |
| `404` | Not Found - simulation ID does not exist |
| `500` | Internal Server Error - unexpected condition |

## 5. Versioning

- Current version: `0.1.0`
- API changes that break backward compatibility must increment the minor version.
- Minor additions (new optional fields, new endpoints) are backward compatible.

## 6. Migration Guide

When updating the API:

1. Document the change in this file.
2. Update the `VITE_API_BASE` type definitions if needed.
3. Update the `simulationService.ts` mock implementations to match new shapes.
4. Update frontend components to handle new fields.
5. Test with both old and new API versions during transition.