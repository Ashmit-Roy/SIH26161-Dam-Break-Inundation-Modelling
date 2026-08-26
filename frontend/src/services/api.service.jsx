import { WaterDepthResult, FloodExtentResult, ComparisonResult, DownloadRequest } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

/**
 * Make a request to the API.
 * @param {string} endpoint
 * @param {RequestInit} options
 * @returns {Promise<Response>}
 */
function apiRequest(endpoint, options) {
  const url = `${API_BASE}/api${endpoint}`;
  const response = fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });
  if (!response.ok) {
    const err = response.text();
    throw new Error(`API error: ${response.status} - ${err}`);
  }
  return response;
}

/**
 * Start a simulation.
 * @param {{simulation_id: string, model: string, scenario_id: string, breach_width?: number, breach_height?: number, simulation_time?: number, crs?: string}} request
 * @returns {Promise<{simulation_id: string, model: string, status: string}>}
 */
function startSimulation(request) {
  const resp = apiRequest("/simulation/start", {
    method: "POST",
    body: JSON.stringify(request),
  });
  return resp.json();
}

/**
 * Check simulation status.
 * @param {string} simulationId
 * @returns {Promise<{model: string, status: string, request: any}>}
 */
function checkSimulationStatus(simulationId) {
  const resp = apiRequest(`/simulation/status/${simulationId}`);
  return resp.json();
}

/**
 * Get dashboard state.
 * @returns {Promise<DashboardState>}
 */
function getDashboardState() {
  const resp = apiRequest("/simulation/state");
  return resp.json();
}

/**
 * Update dashboard state.
 * @param {Partial<DashboardState>} state
 * @returns {Promise<DashboardState>}
 */
function updateDashboardState(state) {
  const resp = apiRequest("/simulation/state", {
    method: "POST",
    body: JSON.stringify(state),
  });
  return resp.json();
}

/**
 * Get water depth result.
 * @param {string} simulationId
 * @returns {Promise<WaterDepthResult>}
 */
function getWaterDepth(simulationId) {
  const resp = apiRequest(`/results/${simulationId}/depth`);
  return resp.json();
}

/**
 * Get flood extent result.
 * @param {string} simulationId
 * @returns {Promise<FloodExtentResult>}
 */
function getFloodExtent(simulationId) {
  const resp = apiRequest(`/results/${simulationId}/extent`);
  return resp.json();
}

/**
 * Get comparison result.
 * @param {string} simulationId
 * @param {string} metric
 * @returns {Promise<ComparisonResult>}
 */
function getComparisonResult(simulationId, metric) {
  const resp = apiRequest(`/results/comparison/${simulationId}?metric=${metric}`);
  return resp.json();
}

/**
 * Download results.
 * @param {DownloadRequest} request
 * @returns {Promise<Blob>}
 */
function downloadResults(request) {
  const resp = apiRequest("/results/download", {
    method: "POST",
    body: JSON.stringify(request),
    responseType: "blob",
  });
  return resp.blob();
}

/**
 * Get comparison metrics.
 * @param {string} simulationId
 * @returns {Promise{{
 *   sph: WaterDepthResult,
 *   delft3d: WaterDepthResult,
 *   metric: ComparisonMetric[]
 * }>}
 */
function getComparisonMetrics(simulationId) {
  const resp = apiRequest(`/results/comparison/${simulationId}`);
  return resp.json();
}

/**
 * Get mock water depth when API is not available.
 * @returns {WaterDepthResult}
 */
function getMockWaterDepth() {
  return {
    simulation_id: "demo_sph_001",
    model: "SPH",
    location: { lat: 6.2, lon: 100.5 },
    water_depth: 3.85,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Get mock flood extent when API is not available.
 * @returns {FloodExtentResult}
 */
function getMockFloodExtent() {
  return {
    simulation_id: "demo_sph_001",
    polygon: {
      type: "Polygon",
      coordinates: [
        [
          [6.1, 100.4],
          [6.3, 100.4],
          [6.3, 100.6],
          [6.1, 100.6],
          [6.1, 100.4],
        ],
      ],
    },
    arrival_time: 12.5,
  };
}

/**
 * Get mock comparison when API is not available.
 * @returns {ComparisonResult}
 */
function getMockComparison() {
  return {
    metric: "water_depth",
    sph_data: {
      simulation_id: "demo_sph_001",
      location: { lat: 6.2, lon: 100.5 },
      water_depth: 3.85,
      timestamp: new Date().toISOString(),
    },
    delft3d_data: {
      simulation_id: "demo_delft3d_001",
      location: { lat: 6.2, lon: 100.5 },
      water_depth: 4.12,
      timestamp: new Date().toISOString(),
    },
    timestamp: new Date().toISOString(),
  };
}

/**
 * Dashboard state type.
 * @typedef {Object} DashboardState
 * @property {string} [current_simulation]
 * @property {number} simulation_progress
 * @property {boolean} comparison_active
 * @property {string} last_update
 */

/**
 * Export the DashboardState type.
 * @type {DashboardState}
 */
const DashboardState = {
  current_simulation: null,
  simulation_progress: 0.0,
  comparison_active: false,
  last_update: new Date().toISOString() + "Z",
}

export {
  apiRequest,
  startSimulation,
  checkSimulationStatus,
  getDashboardState,
  updateDashboardState,
  getWaterDepth,
  getFloodExtent,
  getComparisonResult,
  downloadResults,
  getComparisonMetrics,
  getMockWaterDepth,
  getMockFloodExtent,
  getMockComparison,
  DashboardState,
};