# Integration Specification: SPH/Delft3D → GIS → Dashboard

> **Purpose:** Define the standardized result format that connects simulation output members (SPH/Delft3D) with the GIS member and the dashboard frontend.

> **Owner:** Dashboard Agent (integration layer). Member B (SPH), Member C (Delft3D), and Member D (GIS) must coordinate changes to this contract.

> **Status:** Draft. Mock/demo functionality preserved. Integration points marked with TODO.

---

## 1. Standardized Result Format

The dashboard frontend **only** consumes this standardized format. The backend translates SPH/Delft3D outputs into this format.

### 1.1 `SimulationResult` (Full Simulation Output)

| Field | Type | Description | Provided By |
|---|---|---|---|
| `simulation_id` | `string` | Unique simulation identifier | Backend |
| `model` | `"SPH"` \| `"Delft3D"` | Hydraulic model type | Backend |
| `scenario_id` | `string` | Scenario identifier | Backend |
| `breach_width` | `number` \| `null` | Breach width in meters | Backend |
| `breach_height` | `number` \| `null` | Breach height in meters | Backend |
| `water_depth` | `WaterDepthResult` | **Single point** water depth at location | **GIS Member D** |
| `flood_extent` | `FloodExtentGeoJSON` | **Polygon** flood extent (GeoJSON) | **GIS Member D** |
| `comparison` | `ComparisonResult` \| `null` | SPH vs Delft3D metrics (if model="both") | **Backend** (aggregated) |
| `metadata` | `SimulationMetadata` | Simulation configuration & DEM reference | **Backend** |
| `created_at` | `string` (ISO8601) | When simulation result was created | Backend |
| `completed_at` | `string` \| `null` | When simulation finished | Backend |

### 1.2 `WaterDepthResult`

| Field | Type | Description | Provided By |
|---|---|---|---|
| `simulation_id` | `string` | Link to simulation | Backend |
| `location` | `{lat: number, lon: number}` | Observation point in EPSG:4326 | **GIS Member D** (from DEM sampling) |
| `water_depth` | `number` | Water depth in meters | **GIS Member D** (derived from raster/analysis) |
| `timestamp` | `string` (ISO8601) | When depth was computed | **GIS Member D** |

> **Note:** The frontend displays `water_depth` at the dam location. The GIS member samples the DEM/flood raster at the dam coordinate to produce this value.

### 1.3 `FloodExtentGeoJSON`

Standard GeoJSON `Feature` geometry representing the flooded area.

| Field | Type | Description | Provided By |
|---|---|---|---|
| `type` | `"Feature"` | GeoJSON feature type | **GIS Member D** |
| `geometry.type` | `"Polygon"` | Flood polygon geometry | **GIS Member D** |
| `geometry.coordinates` | `number[][][]` | [[lon, lat], ...] ring coordinates | **GIS Member D** |
| `properties.model` | `"SPH"` \| `"Delft3D"` | Source model | **Backend** (set from request) |
| `properties.simulation_id` | `string` | Link to simulation | **Backend** |
| `properties.water_depth_at_peak` | `number` | Maximum water depth in meters | **GIS Member D** (from raster analysis) |
| `properties.breach_width` | `number` | Breach width in meters | **Backend** |
| `properties.breach_height` | `number` | Breach height in meters | **Backend** |
| `properties.arrival_time` | `number` | Time to flood arrival in seconds | **GIS Member D** (from arrival time analysis) |
| `properties.confidence` | `"high"` \| `"medium"` \| `"low"` | Confidence level | **GIS Member D** |
| `properties.source` | `string` | Data source identifier | **GIS Member D** |

> **Important:** All coordinates must be in **EPSG:4326** (decimal degrees: [longitude, latitude]).

### 1.4 `ComparisonResult`

| Field | Type | Description | Provided By |
|---|---|---|---|
| `metric` | `"flood_extent"` \| `"water_depth"` \| `"arrival_time"` \| `"computational_time"` | Comparison type | **Backend** |
| `sph_data` | `WaterDepthResult` | SPH result at comparison point | **Backend** (from SPH output) |
| `delft3d_data` | `WaterDepthResult` | Delft3D result at comparison point | **Backend** (from Delft3D output) |
| `timestamp` | `string` (ISO8601) | When comparison was computed | **Backend** |
| `overlap_area` | `number` \| `null` | Overlapping flooded area in m² (optional) | **Backend** (computed from intersection) |

### 1.5 `SimulationMetadata`

| Field | Type | Description | Provided By |
|---|---|---|---|
| `terrain_reference` | `string` \| `null` | DEM filename or source identifier | **Backend** / **GIS Member D** |
| `dam_location` | `{lat: number, lon: number}` | Dam breach point in EPSG:4326 | **Backend** (from request) |
| `initial_water_level` | `number` \| `null` | Initial reservoir level in meters | **Backend** (from request) |

---

## 2. Member Responsibilities

### 2.1 Member B: SPH (DualSPHysics)

**Output to provide** (via GIS Member D or direct API):

| Output | Format | Description |
|---|---|---|
| Particle surface elevation | Raw SPH output | Array of particle positions (z-coordinate = elevation) |
| Flood depth at points | `WaterDepthResult`-compatible | Sample DEM at dam location + downstream points |
| Flood extent polygon | GeoJSON `Feature` | Convex hull or threshold-based inundation polygon |
| Arrival time at points | `number` (seconds) | Time each point was first wetted |
| peak water depth | `number` (meters) | Maximum depth observed in simulation |

**Integration path:**
1. Member B provides raw SPH output to Member D (GIS)
2. Member D samples the SPH results at the dam location and produces `WaterDepthResult`
3. Member D produces `FloodExtentGeoJSON` from the SPH particle distribution (e.g., >0.1m depth threshold)
4. Member D provides `comparison_data` for SPH vs Delft3D overlap analysis

**TODO in backend code** (services.py, line ~252):
```python
# Member B / C should output standardized WaterDepthResult + FloodExtentGeoJSON
# The backend will aggregate these into SimulationResultResponse
```

### 2.2 Member C: Delft3D (Delft3D FM)

**Output to provide** (via GIS Member D or direct API):

| Output | Format | Description |
|---|---|---|
| Water depth at points | `WaterDepthResult`-compatible | Sample at dam location & downstream profile |
| Flood extent polygon | GeoJSON `Feature` | Binary threshold (depth > 0.01m) or raster-derived polygon |
| Arrival time at points | `number` (seconds) | From simulation output `arrival_time` |
| Peak water depth | `number` (meters) | Maximum depth over simulation period |
| Bathymetry | DEM mesh coordinates | For raster intersection |

**Integration path:**
1. Member C provides raw Delft3D output to Member D (GIS)
2. Member D produces `WaterDepthResult` from Delft3D output at dam location
3. Member D produces `FloodExtentGeoJSON` from Delft3D flooded mesh
4. Member D provides overlap analysis data for SPH vs Delft3D comparison

**TODO in backend code** (services.py, line ~324):
```python
# Member C should output standardized WaterDepthResult + FloodExtentGeoJSON
# Backend will set model="Delft3D" and aggregate comparison
```

### 2.3 Member D: GIS (GIS / Raster Analysis)

**This member bridges the simulation outputs to the dashboard standard format.**

**Input from Member B (SPH):**
- Raw particle data or pre-processed depth values
- Flood extent boundary
- Arrival time series

**Input from Member C (Delft3D):**
- Mesh-based flood depth values  
- Flooded area polygon
- Water level time series

**Output to Dashboard (Standardized Format):**

| Output | Method | Description |
|---|---|---|
| `WaterDepthResult` | `get_damage_statistics()` or direct API | Sample DEM/flood raster at dam coordinate (`{lat, lon}`). Return `water_depth` in meters. |
| `FloodExtentGeoJSON` | `get_flood_layer()` | Convert flood depth raster > threshold to GeoJSON Polygon. Include `water_depth_at_peak`, `arrival_time`, `confidence`. |
| `ComparisonResult` | `get_model_comparison()` | Compute overlap area between SPH and Delft3D extents. Return `sph_data` and `delft3d_data` as `WaterDepthResult` at same location. |
| `DamageStatistics` | `get_damage_statistics()` | Aggregate population, roads, bridges, land area from spatial join with census/road datasets. |

**Example GIS output format:**
```json
{
  "water_depth": 3.85,           // from DEM sampling at dam location
  "flood_extent": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[100.4, 6.1], [100.6, 6.1], [100.6, 6.3], [100.4, 6.3], [100.4, 6.1]]]
    },
    "properties": {
      "water_depth_at_peak": 3.85,
      "arrival_time": 12.5,
      "confidence": "high",
      "source": "DualSPHysics v6.4"
    }
  },
  "comparison": {
    "metric": "water_depth",
    "sph_data": {"water_depth": 3.85, "location": {"lat": 6.2, "lon": 100.5}},
    "delft3d_data": {"water_depth": 4.12, "location": {"lat": 6.2, "lon": 100.5}},
    "overlap_area": 9.5
  }
}
```

**Integration path:**
1. Member D receives raw SPH/Delft3D outputs
2. Member D performs raster/spatial analysis
3. Member D outputs standardized `WaterDepthResult`, `FloodExtentGeoJSON`, `ComparisonResult`
4. Member D provides outputs to the backend (or directly to frontend via API)
5. **TODO in frontend** (useSimulation.jsx): Currently uses mock data; replace API calls with real outputs when GIS member provides them

**TODO markers in code:**
- `frontend/src/services/simulationService.ts`: Lines with `// TODO: Replace with real API call`
- `frontend/src/hooks/useSimulation.jsx`: Mock fallback functions
- `docs/integration-spec.md`: This file

---

## 3. Backend API Changes (Minimal)

The backend currently mocks the standardized format. When Members B, C, D provide real outputs:

1. **Backend `services.py`**: Replace `MockSPHExecution` and `MockDelft3DExecution` with calls to GIS member APIs
2. **Backend `models.py`**: No changes needed - already defines the standardized format
3. **Backend `api.py`**: No changes needed - endpoints already return `SimulationResultResponse`
4. **Frontend `simulationService.ts`**: Already designed to consume the standardized format; just need real API responses

**Example real API response flow:**
```
Member B (SPH)  ─────────────────────┐
                                       ├── Member D (GIS) processes ──────► WaterDepthResult (3.85m)
                                       ├── Member D (GIS) processes ──────► FloodExtentGeoJSON
                                       └──► Backend SimulationResultResponse ←───► Frontend

Member C (Delft3D) ──────────────────┘
                                       (same path through Member D + Backend)
```

---

## 4. Frontend Consumption (Already Designed)

The frontend only knows about these types (from `frontend/src/types.ts`):

| Type | Used By |
|---|---|
| `WaterDepthResult` | `MapDisplay`, `ResultsPanel`, `ComparisonPanel` |
| `FloodExtentResult` | `MapDisplay` (Leaflet polygon) |
| `ModelComparison` | `ComparisonPanel`, `ResultsPanel` |
| `DamageStatistics` | `ResultsPanel` (currently mock) |
| `SimulationResult` | `useSimulation` hook (via `getSimulationResult()`) |
| `FloodLayer` | `getFloodLayer()` service function → Leaflet |

**Frontend does NOT know about:**
- SPH particle data
- Delft3D mesh coordinates
- Raw simulation output files
- Numerical parameters (time step, CFL, etc.)

---

## 4. Migration Path

### Phase 1: Mock (Current)
- Backend mocks `SimulationResultResponse` with sample data
- Frontend consumes mock data via `useSimulation` hook
- All tests pass

### Phase 2: GIS Member D Integration
- Member D provides `WaterDepthResult`, `FloodExtentGeoJSON`, `ComparisonResult`
- Backend passes through (no changes to types)
- Frontend continues working (API returns real data instead of mock)
- TODO markers remain but are no longer hitting mock fallbacks

### Phase 3: SPH + Delft3D Members B, C Integration
- Members B & C provide their raw outputs to Member D
- Member D produces all three standardized outputs
- Backend aggregates comparison data
- Frontend displays SPH vs Delft3D comparison

### Phase 4: Downloadable Outputs (SHP/KML)
- Member D generates SHP/KML from `FloodExtentGeoJSON`
- Backend `download_result()` returns proper Blob
- Frontend `downloadResult()` triggers file download

---

## 5. Checklist for Integration

### For Member B (SPH):
- [ ] Provide flood extent polygon (GeoJSON `Feature` with `coordinates`)
- [ ] Provide water depth at dam location (meters)
- [ ] Provide arrival time at dam location (seconds)
- [ ] Provide peak water depth (meters)
- [ ] Coordinate with Member D for standardized format

### For Member C (Delft3D):
- [ ] Provide flood extent polygon (GeoJSON `Feature`)
- [ ] Provide water depth at dam location (meters)
- [ ] Provide arrival time at dam location (seconds)
- [ ] Provide peak water depth (meters)
- [ ] Coordinate with Member D for standardized format

### For Member D (GIS):
- [ ] Sample DEM/flood raster at dam coordinate → produce `WaterDepthResult`
- [ ] Convert flood depth raster to GeoJSON Polygon → produce `FloodExtentGeoJSON`
- [ ] Compute SPH vs Delft3D overlap → produce `ComparisonResult`
- [ ] Aggregate damage statistics → produce `DamageStatistics`
- [ ] Provide all outputs in EPSG:4326 coordinates
- [ ] Coordinate with Members B & C on data formats

### For Dashboard Team:
- [ ] Keep frontend types unchanged (they already consume standardized format)
- [ ] Replace mock data with real API calls when GIS outputs available
- [ ] Update `VITE_API_BASE` to point to production backend
- [ ] Test download functionality (SHP/KML)
- [ ] Maintain backward compatibility with mock/demo mode

### For Backend Team:
- [ ] Keep `models.py` unchanged (already defines standardized format)
- [ ] Keep `api.py` endpoints unchanged
- [ ] Replace mock execution in `services.py` with real GIS API calls
- [ ] Add error handling for missing GIS output fields
- [ ] Maintain backward compatibility with mock mode

---

## 6. Code Structure Preservation

**Do NOT modify:**
- `frontend/src/components/*` - React components unchanged
- `frontend/src/hooks/useSimulation.jsx` - logic structure unchanged (mock fallbacks preserved)
- `backend/app/models.py` - Pydantic models unchanged
- `backend/app/api.py` - endpoints unchanged
- `backend/app/main.py` - FastAPI app unchanged
- `tests/dashboard/test_models.py` - tests unchanged

**Will modify (integration only):**
- `frontend/src/services/simulationService.ts` - API call URLs, TODO removal
- `docs/integration-spec.md` - new file documenting integration
- `docs/api-contract.md` - already updated with full contract
- `docs/data-formats.md` - may need updating for GeoJSON spec

**Mock/demo functionality preserved:** All existing tests pass, ruff checks pass, and the frontend falls back to mock data if the backend returns errors or is unavailable.