export type ModelType = "SPH" | "Delft3D";

export type ComparisonMetric =
  | "flood_extent"
  | "water_depth"
  | "arrival_time"
  | "computational_time";

export interface Location {
  lat: number;
  lon: number;
}

export interface SimulationRequest {
  simulation_id: string;
  model: ModelType;
  scenario_id: string;
  breach_width?: number;
  breach_height?: number;
  simulation_time?: number;
  crs?: string;
}

export interface SimulationMetadata {
  terrain_reference?: string;
  dam_location: Location;
  initial_water_level?: number;
}

export interface WaterDepthResult {
  simulation_id: string;
  location: Location;
  water_depth: number;
  timestamp?: string;
}

export interface FloodExtentResult {
  simulation_id: string;
  polygon: {
    type: string;
    coordinates: number[][][];
  };
  arrival_time?: number;
}

export interface ComparisonResult {
  metric: ComparisonMetric;
  sph_data?: WaterDepthResult;
  delft3d_data?: WaterDepthResult;
  timestamp: string;
}

export interface DownloadRequest {
  format: string;
  simulation_id: string;
  crs?: string;
}

/** Simulation status states */
export enum SimulationStatus {
  IDLE = "idle",
  UPLOADING = "uploading",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed",
  TIMED_OUT = "timed_out",
}

/** High-level simulation result combining all output data */
export interface SimulationResult {
  simulation_id: string;
  model: ModelType;
  scenario_id: string;
  breach_width: number;
  breach_height: number;
  water_depth: WaterDepthResult;
  flood_extent: FloodExtentResult;
  comparison?: ModelComparison;
  timestamp: string;
}

/** Comparison between SPH and Delft3D results */
export interface ModelComparison {
  metric: ComparisonMetric;
  sph_data: WaterDepthResult;
  delft3d_data: WaterDepthResult;
  overlap_area?: number; // in square meters
  timestamp: string;
}

/** GeoJSON flood layer for map display */
export interface FloodLayer {
  type: "Feature";
  geometry: {
    type: "Polygon";
    coordinates: number[][][];
  };
  properties: {
    model: ModelType;
    simulation_id: string;
    water_depth_at_peak: number;
    breach_width: number;
    breach_height: number;
    arrival_time: number;
    confidence: "high" | "medium" | "low";
    source: string;
  };
}

/** Aggregated damage/loss statistics */
export interface DamageStatistics {
  population_affected: number;
  population_at_risk: number;
  residential_units_destroyed: number;
  residential_units_damaged: number;
  road_km_affected: number;
  bridge_count_affected: number;
  land_area_flooded_km2: number;
  evacuation_centers_needed: number;
  timestamp: string;
}

/** Output formats available for download */
export enum DownloadableOutput {
  SHAPEFILE = "shp",
  KML = "kml",
  GEOJSON = "geojson",
}

/** Request payload for starting a simulation */
export interface SimulationRequest {
  simulation_id: string;
  model: ModelType;
  scenario_id: string;
  breach_width?: number;
  breach_height?: number;
  simulation_time?: number;
  crs?: string;
}