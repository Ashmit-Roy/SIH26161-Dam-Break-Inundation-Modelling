import React from "react";
import { WaterDepthResult, ComparisonResult } from "../types";
import { SAMPLE_WATER_DEPTH, SAMPLE_COMPARISON } from "../data/mockData";

function ResultsPanel({
  currentResult,
  comparison,
}) {
  const [showDetails, setShowDetails] = React.useState(false);

  const resultData = currentResult
    ? {
        floodedArea: "1.2 km²",
        maxDepth: `${currentResult.water_depth} m`,
        arrivalTime: "12.5 s",
        populationAffected: "2,450",
        roadsAffected: "3",
        location: currentResult.location,
        simulationId: currentResult.simulation_id,
        timestamp: currentResult.timestamp,
      }
    : null;

  const comparisonData = comparison
    ? {
        sphArea: "1.1 km²",
        sphMaxDepth: `${comparison.sph_data?.water_depth ?? "N/A"} m`,
        sphArrival: "13.2 s",
        delftArea: "1.3 km²",
        delftMaxDepth: `${comparison.delft3d_data?.water_depth ?? "N/A"} m`,
        delftArrival: "11.8 s",
        delftCompTime: "45.2 s",
      }
    : null;

  return (
    <div className="results-panel">
      <h2>📊 Results</h2>

      {/* Current Result */}
      {resultData ? (
        <div className="result-card">
          <div className="result-header">
            <span>Current Simulation</span>
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="toggle-small"
            >
              {showDetails ? "▲" : "▼"}
            </button>
          </div>

          <div className="result-grid">
            <div className="result-item">
              <div className="result-label">Flooded Area</div>
              <div className="result-value">{resultData.floodedArea}</div>
            </div>
            <div className="result-item">
              <div className="result-label">Max Water Depth</div>
              <div className="result-value">{resultData.maxDepth}</div>
            </div>
            <div className="result-item">
              <div className="result-label">Arrival Time</div>
              <div className="result-value">{resultData.arrivalTime}</div>
            </div>
          </div>

          <div className="result-section">
            <div className="result-item">
              <div className="result-label">Population Affected</div>
              <div className="result-value">{resultData.populationAffected}</div>
            </div>
            <div className="result-item">
              <div className="result-label">Roads Affected</div>
              <div className="result-value">{resultData.roadsAffected}</div>
            </div>
          </div>

          <div className="result-meta">
            <div>Simulation ID: {resultData.simulationId}</div>
            <div>Timestamp: {resultData.timestamp}</div>
            <div>Location: {resultData.location.lat.toFixed(4)}, {resultData.location.lon.toFixed(4)}</div>
          </div>
        </div>
      ) : (
        <div className="result-card empty">
          <i className="icon-placeholder">📋</i>
          <p>Run a simulation to display results</p>
        </div>
      )}

      {/* Comparison Section */}
      {comparison && (
        <div className="comparison-summary">
          <h3>🔬 SPH vs Delft3D Comparison</h3>
          <div className="comparison-grid">
            <div className="comparison-box sph">
              <div>SPH</div>
              <div>{comparison.sph_data?.water_depth ?? "N/A"} m max</div>
              <div>{comparison.sph_data?.simulation_id ?? "N/A"}</div>
            </div>
            <div className="comparison-box delft3d">
              <div>Delft3D</div>
              <div>{comparison.delft3d_data?.water_depth ?? "N/A"} m max</div>
              <div>{comparison.delft3d_data?.simulation_id ?? "N/A"}</div>
            </div>
          </div>
<div className="comp-difference">
              <strong>Difference:</strong> {
                ((comparison.delft3d_data?.water_depth ?? 0) -
                (comparison.sph_data?.water_depth ?? 0)).toFixed(3)
              } m</div>
        </div>
      )}
    </div>
  );
}

export default ResultsPanel;