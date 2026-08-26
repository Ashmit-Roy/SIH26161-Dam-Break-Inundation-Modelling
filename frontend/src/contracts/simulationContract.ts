// ============================================================
// SIH26161 - SIMULATION DATA CONTRACT
// ============================================================
// This file defines the shared data contract between the Dashboard
// (Member E) and the simulation modules (SPH/Delft3D, Member B/C).
//
// The contract uses explicit types so that the frontend can consume
// real API responses without modification when the backend is ready.
//
// DEFINITION OF DONE: A task is complete only when:
// - Requested functionality is implemented
// - Existing functionality has not unintentionally broken
// - Relevant tests are added or updated
// - Relevant tests pass
// - Final Git diff contains only intended changes
// - No secrets were introduced
// - No machine-specific paths were introduced
// - API/data contracts remain consistent
// - Important assumptions are documented
// - Limitations are clearly stated
// ============================================================

import { ModelType } from "./types";

// ============================================================
// 1. SIMULATION REQUEST
// ============================================================

/** @typedef {Object} SimulationRequest */
export type SimulationRequest = {
  /** Unique simulation identifier (UUID v4 recommended) */
  simulation_id: string;
  /** Hydraulic model: SPH | Delft3D | Both */
  model: ModelType;
  /** Scenario identifier */
  scenario_id: string;
  /** Breach width in metres */
  breach_width?: number;
  /** Breach height in metres */
  breach_height?: number;
  /** Simulation time in seconds */
  simulation_time?: number;
  /** Coordinate reference system, e.g. "EPSG:4326" */
  crs?: string;
  /** DEM/terrain reference identifier */
  terrain_reference?: string;
};

/** Default simulation request values */
export const DEFAULT_SIMULATION_REQUEST: SimulationRequest = {
  simulation_id: "",
  model: "SPH",
  scenario_id: "scenario_a",
  crs: "EPSG:4326",
};

// ============================================================
// 2. SIMULATION STATUS
// ============================================================

/** @typedef {Object} SimulationStatus */
export type SimulationStatus = {
  /** Current simulation ID */
  simulation_id: string;
  /** Current stage: idle | uploading | running | completed | failed */
  stage: "idle" | "uploading" | "running" | "completed" | "failed";
  /** Progress percentage 0-100 */
  progress: number;
  /** Current stage description */
  message: string;
  /** Model being used */
  model: ModelType;
  /** Timestamp when current stage started */
  stage_started_at: string; // ISO8601
  /** Elapsed time in seconds */
  elapsed_time: number;
  /** Error details if stage is "failed" */
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
};

/** Initial simulation status */
export const INITIAL_SIMULATION_STATUS: SimulationStatus = {
  simulation_id: "",
  stage: "idle",
  progress: 0,
  message: "Select a model and run simulation",
  model: "SPH",
  stage_started_at: new Date().toISOString(),
  elapsed_time: 0,
};

// ============================================================
// 3. SIMULATION RESULT (Common normalized result)
// ============================================================

/** Water depth at a specific location */
export type WaterDepthPoint = {
  /** Location in CRS coordinates */
  location: Location;
  /** Water depth in metres */
  water_depth: number;
  /** Timestamp of this measurement */
  timestamp: string; // ISO8601
  /** Model that produced this result */
  model: ModelType;
};

/** Flood extent polygon with associated data */
export type FloodExtentResult = {
  /** Simulation ID */
  simulation_id: string;
  /** Model that produced this result */
  model: ModelType;
  /** GeoJSON polygon geometry */
  polygon: GeoJSONGeometry;
  /** Arrival time in seconds */
  arrival_time?: number;
  /** Peak water depth in metres */
  peak_water_depth?: number;
  /** Timestamp of peak */
  peak_timestamp?: string;
  /** Simulation metadata */
  metadata?: Record<string, unknown>;
};

/** GeoJSON geometry type union */
export type GeoJSONGeometry =
  | GeoJSON.Point
  | GeoJSON.MultiPoint
  | GeoJSON.LineString
  | GeoJSON.MultiLineString
  | GeoJSON.Polygon
  | GeoJSON.MultiPolygon
  | null;

/** Complete simulation result container */
export type SimulationResult = {
  /** Simulation identifier */
  simulation_id: string;
  /** Hydraulic model */
  model: ModelType;
  /** Water depth points (sampled locations) */
  water_depth_points: WaterDepthPoint[];
  /** Flood extent polygon */
  flood_extent: FloodExtentResult;
  /** Comparison data if SPH vs Delft3D */
  comparison?: ModelComparison;
  /** Simulation metadata */
  metadata?: Record<string, unknown>;
  /** Timestamp when result was generated */
  generated_at: string; // ISO8601
};

/** Population impact data */
export type PopulationImpact = {
  /** Number of people affected */
  count: number;
  /** Affected area in km² */
  affected_area_km2: number;
  /** Breakdown by age group (optional) */
  age_breakdown?: Record<string, number>;
  /** Social vulnerability index (optional) */
  vulnerability_index?: number;
};

/** Road/Infrastructure impact data */
export type InfrastructureImpact = {
  /** Number of roads affected */
  roads_affected: number;
  /** Length of roads affected in km */
  road_length_km: number;
  /** Number of bridges affected */
  bridges_affected: number;
};

/** Damage/loss statistics */
export type DamageStatistics = {
  /** Flooded area in km² */
  flooded_area_km2: number;
  /** Maximum water depth in metres */
  max_water_depth_m: number;
  /** Average water depth in metres */
  avg_water_depth_m: number;
  /** Estimated arrival time in seconds */
  estimated_arrival_time_s: number;
  /** Population affected */
  population_affected: PopulationImpact;
  /** Infrastructure impact */
  infrastructure_affected: InfrastructureImpact;
  /** Timestamp */
  calculated_at: string; // ISO8601
};

/** SPH vs Delft3D comparison metrics */
export type ModelComparison = {
  /** Flooded area comparison */
  flooded_area: {
    sph_km2: number;
    delft3d_km2: number;
    difference_km2: number;
    sph_percentage: number;
    delft3d_percentage: number;
  };
  /** Maximum depth comparison */
  max_depth: {
    sph_m: number;
    delft3d_m: number;
    difference_m: number;
  };
  /** Arrival time comparison */
  arrival_time: {
    sph_s: number;
    delft3d_s: number;
    difference_s: number;
    faster_model: "SPH" | "Delft3D";
  };
  /** Computational time comparison */
  computational_time: {
    sph_s: number;
    delft3d_s: number;
    difference_s: number;
    more_efficient: "SPH" | "Delft3D";
  };
};

/** Downloadable output format */
export type DownloadFormat = "GeoJSON" | "SHP" | "KML" | "CSV";

/** @typedef {Object} DownloadableOutput */
export type DownloadableOutput = {
  /** Simulation ID */
  simulation_id: string;
  /** Format */
  format: DownloadFormat;
  /** Download URL (or base64 data) */
  url_or_data: string;
  /** File size in bytes */
  file_size: number;
  /** Generated at timestamp */
  generated_at: string; // ISO8601
  /** CRS */
  crs: string;
};

/** Error response structure */
export type ApiError = {
  /** Error code */
  code: string;
  /** Human-readable message */
  message: string;
  /** Additional details (optional) */
  details?: Record<string, unknown>;
  /** Timestamp */
  timestamp: string; // ISO8601
};

/** Success API response wrapper */
export type ApiResponse<T> = {
  /** Whether the request was successful */
  success: boolean;
  /** Data payload */
  data: T;
  /** Error information if unsuccessful */
  error?: ApiError;
  /** Request timestamp */
  timestamp: string; // ISO8601
};

// ============================================================
// 4. FLOOD LAYER STATE (for frontend map)
// ============================================================

/** @typedef {Object} FloodLayerState */
export type FloodLayerState = {
  /** Currently loaded flood extent layer */
  extent: GeoJSONFeature | null;
  /** SPH flood extent layer */
  sph: GeoJSONFeature | null;
  /** Delft3D flood extent layer */
  delft3d: GeoJSONFeature | null;
  /** Overlap/comparison layer */
  overlap: GeoJSONFeature | null;
  /** Whether layer data is currently loading */
  loading: boolean;
  /** Error information if load failed */
  error: ApiError | null;
};

/** @typedef {Object} GeoJSONFeature */
export type GeoJSONFeature = {
  /** GeoJSON geometry */
  geometry: GeoJSONGeometry;
  /** GeoJSON properties */
  properties: Record<string, unknown>;
};

/** @typedef {Object} MapLayerConfig */
export type MapLayerConfig = {
  /** Layer name for legend/control */
  name: string;
  /** Leaflet-style style object */
  style: {
    color: string;
    fillColor: string;
    fillOpacity: number;
    weight: number;
  };
  /** Whether layer is visible */
  visible: boolean;
};

/** ============================================================
// 5. PREDICTED API ENDPOINTS (Documentation only)
// ============================================================

/**
 * Expected FastAPI endpoints (to be implemented by backend team):
 *
 * POST /api/simulation/start
 *   Request:  SimulationRequest
 *   Response: ApiResponse<{ simulation_id: string; status: string }>
 *
 * GET /api/simulation/status/{simulation_id}
 *   Response: ApiResponse<SimulationStatus>
 *
 * GET /api/simulation/result/{simulation_id}
 *   Response: ApiResponse<SimulationResult>
 *
 * GET /api/results/download/{simulation_id}/{format}
 *   Parameters: format ∈ {GeoJSON, SHP, KML, CSV}
 *   Response: ApiResponse<DownloadableOutput>
 *
 * GET /api/damage/statistics/{simulation_id}
 *   Response: ApiResponse<DamageStatistics>
 *
 * GET /api/comparison/{simulation_id}
 *   Response: ApiResponse<ModelComparison>
 */

// ============================================================
// EXPORTS
// ============================================================

export type {
  SimulationRequest,
  SimulationStatus,
  SimulationResult,
  WaterDepthPoint,
  FloodExtentResult,
  GeoJSONGeometry,
  GeoJSONFeature,
  SimulationResult, // alias
  DamageStatistics,
  ModelComparison,
  DownloadFormat,
  DownloadableOutput,
  ApiError,
  ApiResponse,
  FloodLayerState,
  MapLayerConfig,
};

export {
  DEFAULT_SIMULATION_REQUEST,
  INITIAL_SIMULATION_STATUS,
};