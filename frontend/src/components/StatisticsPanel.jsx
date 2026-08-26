import React from "react";
import { WaterDepthResult, ComparisonResult } from "../types";
import { SAMPLE_WATER_DEPTH, SAMPLE_COMPARISON } from "../data/mockData";

function StatisticsPanel() {
  const [showComparison, setShowComparison] = React.useState(false);

  const stats = currentResult
    ? {
        metric: "Water Depth",
        value: `${currentResult.water_depth} m`,
        location: currentResult.location,
        timestamp: currentResult.timestamp,
        simulationId: currentResult.simulation_id,
      }
    : null;

  const comparisonStats = comparison
    ? {
        metric: comparison.metric,
        sphDepth: comparison.sph_data?.water_depth ?? "N/A",
        delft3dDepth: comparison.delft3d_data?.water_depth ?? "N/A",
        difference:
          (comparison.delft3d_data?.water_depth ?? 0) -
          (comparison.sph_data?.water_depth ?? 0),
        simulationId: comparison.simulation_id,
      }
    : null;

  return (
    <div className="statistics-card">
      <h2>Statistics</h2>

      {/* Current Result */}
      {stats ? (
        <div className="stat-box">
          <h3>Current Result</h3>
          <p><b>Metric:</b> {stats.metric}</p>
          <p><b>Water Depth:</b> {stats.value}</p>
          <p><b>Location:</b> {stats.location.lat.toFixed(4)}, {stats.location.lon.toFixed(
            4
          )}</p>
          <p><b>Timestamp:</b> {stats.timestamp}</p>
          <p><b>Simulation ID:</b> {stats.simulationId}</p>
        </div>
      ) : (
        <p><i>Run a simulation to display statistics</i></p>
      )}

      {/* Comparison Section */}
      {comparison && (
        <div className="comparison-box">
          <h3>SPH vs Delft3D Comparison</h3>
          <p>
            <b>SPH:</b> {comparison.sph_data?.water_depth ?? "N/A"} m &nbsp;|&nbsp;
            <b>Delft3D:</b> {comparison.delft3d_data?.water_depth ?? "N/A"} m
          </p>
          <p>
            <b>Difference:</b> {(
              (comparison.delft3d_data?.water_depth ?? 0) -
              (comparison.sph_data?.water_depth ?? 0)
            ).toFixed(3)} m
          </p>
          <button
            onClick={() => setShowComparison(!showComparison)}
            className="toggle-btn"
          >
            {showComparison ? "Hide Comparison" : "Show Detailed Comparison"}
          </button>
        </div>
      )}

      {/* Dashboard State */}
      <div className="dashboard-state">
        <h3>Dashboard State</h3>
        <p>
          <b>Current Simulation:</b> {dashboardState.current_simulation ?? "None"}
        </p>
        <p>
          <b>Progress:</b> {dashboardState.simulation_progress}%
        </p>
        <p>
          <b>Comparison Active:</b> {dashboardState.comparison_active ? "Yes" : "No"}
        </p>
        <p>
          <b>Last Update:</b> {dashboardState.last_update}
        </p>
      </div>
    </div>
  );
}

/** @type {{current_simulation: string|null, simulation_progress: number, comparison_active: boolean, last_update: string}} */
const dashboardState = {
  current_simulation: null,
  simulation_progress: 0,
  comparison_active: false,
  last_update: new Date().toISOString() + "Z",
}

/** @type {WaterDepthResult|null} */
let currentResultVal = null;

/** @type {ComparisonResult|null} */
let comparisonVal = null;

/** @type {{current_simulation: string|null, simulation_progress: number, comparison_active: boolean, last_update: string}} */
const DashboardState = dashboardState;

/** @type {import("../types").DashboardState} */
export default StatisticsPanel;