import {
  WaterDepthResult,
  FloodExtentResult,
  ComparisonResult,
  DownloadRequest,
  DashboardState,
  ModelType,
  ComparisonMetric,
  SimulationFormValues,
  Location,
  SimulationRequest,
  SimulationMetadata,
  DemoScenario,
} from "../types";

// ============================================================
// MOCK GEOJSON DATA FOR SIH26161 DEMONSTRATION
// ============================================================
// These are SAMPLE/DEMO data only. They resemble realistic flood
// polygons but are NOT scientifically calculated results.
// They are designed so Member B (SPH) and Member C (Delft3D)
// can replace the mock data with real outputs later.

// Demo dam location
const DEMO_DAM_LOCATION = { lat: 6.2, lon: 100.5 };

// ============================================================
// MOCK SPH FLOOD EXTENT GEOJSON
// Simulated SPH particle-based flood extent for SIH26161
// ============================================================
const SPH_FLOOD_GEOJSON = {
  type: "Feature",
  geometry: {
    type: "Polygon",
    coordinates: [
      // Main inundation polygon - realistic shape for breached dam
      [
        [6.12, 100.42], // SW corner
        [6.35, 100.38], // SE corner
        [6.42, 100.55], // NE corner
        [6.20, 100.62], // NW corner
        [6.12, 100.42], // back to start
      ],
      // Internal "island" of non-flooded terrain
      [
        [6.25, 100.48],
        [6.32, 100.48],
        [6.32, 100.52],
        [6.25, 100.52],
        [6.25, 100.48],
      ],
    ],
  },
  properties: {
    model: "SPH",
    simulation_id: "demo_sph_001",
    water_depth_at_peak: 3.85, // metres
    breach_width: 10,
    breach_height: 2,
    arrival_time: 12.5,
    confidence: "high",
    source: "DualSPHysics v6.4",
  },
};

// ============================================================
// MOCK DELTAF3D FLOOD EXTENT GEOJSON
// Simulated Delft3D FM mesh-based flood extent for SIH26161
// ============================================================
const DELTAF3D_FLOOD_GEOJSON = {
  type: "Feature",
  geometry: {
    type: "Polygon",
    coordinates: [
      // Main inundation polygon - slightly different shape
      [
        [6.10, 100.40], // SW corner
        [6.40, 100.35], // SE corner
        [6.48, 100.58], // NE corner
        [6.18, 100.65], // NW corner
        [6.10, 100.40], // back to start
      ],
    ],
  },
  properties: {
    model: "Delft3D",
    simulation_id: "demo_delft3d_001",
    water_depth_at_peak: 4.12, // metres
    breach_width: 15,
    breach_height: 3,
    arrival_time: 11.8,
    confidence: "medium",
    source: "Delft3D FM Flexible Mesh",
  },
};

// ============================================================
// MOCK COMPARISON/ OVERLAP GEOJSON
// Shows the overlapping area between SPH and Delft3D extents
// ============================================================
const OVERLAP_FLOOD_GEOJSON = {
  type: "Feature",
  geometry: {
    type: "Polygon",
    coordinates: [
      // Overlapping region where both models agree on flooding
      [
        [6.15, 100.43], // SW overlap corner
        [6.30, 100.40], // SE overlap corner
        [6.35, 100.50], // NE overlap corner
        [6.18, 100.55], // NW overlap corner
        [6.15, 100.43], // back to start
      ],
    ],
  },
  properties: {
    model: "Both",
    simulation_id: "demo_comparison_001",
    water_depth_at_peak: 3.95, // metres (average)
    breach_width: 12.5,
    breach_height: 2.5,
    arrival_time: 12.1,
    confidence: "comparison",
    source: "SPH vs Delft3D Comparison",
  },
};

// ============================================================
// EXPORT MOCK DATA
// ============================================================
export {
  DEMO_DAM_LOCATION,
  SPH_FLOOD_GEOJSON,
  DELTAF3D_FLOOD_GEOJSON,
  OVERLAP_FLOOD_GEOJSON,
};