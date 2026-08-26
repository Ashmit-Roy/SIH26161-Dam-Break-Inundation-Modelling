import React from "react";
import { ModelType, ComparisonMetric } from "../types";
import { DEMO_SCENARIOS } from "../data/mockData";

function ControlPanel({
  form,
  onChange,
  onSubmit,
  isRunning,
  DEMO_SCENARIOS,
  ModelType,
  setSimulationStatus,
}) {
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onChange({ target: { name: "simulation_id", value: file.name } });
    }
  };

  return (
    <aside className="control-panel">
      <h2>🏗️ Simulation Controls</h2>

      <form onSubmit={onSubmit} className="control-form">
        <div className="form-group">
          <label htmlFor="river-dam">River / Dam</label>
          <select
            id="river-dam"
            name="river-dam"
            value={form.river_dam ?? ""}
            onChange={onChange}
            disabled={isRunning}
          >
            <option value="">Select demo river/dam</option>
            <option value="river_a">River A - Himalayan Tributary</option>
            <option value="river_b">River B - Delta Region</option>
            <option value="river_c">River C - Urban Reach</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="model">Hydraulic Model</label>
          <select
            id="model"
            name="model"
            value={form.model}
            onChange={onChange}
            disabled={isRunning}
          >
            <option value="SPH">SPH (Smoothed Particle Hydrodynamics)</option>
            <option value="Delft3D">Delft3D / Delft3D FM</option>
            <option value="both">Both (Comparison)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="scenario">Scenario</label>
          <select
            id="scenario"
            name="scenario"
            value={form.scenario_id ?? "scenario_a"}
            onChange={onChange}
            disabled={isRunning}
          >
            {DEMO_SCENARIOS.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="breach-width">Breach Width (m)</label>
          <input
            id="breach-width"
            type="number"
            name="breach_width"
            value={form.breach_width ?? ""}
            onChange={onChange}
            disabled={isRunning}
            placeholder="e.g., 15"
            min="1"
            max="100"
          />
        </div>

        <div className="form-group">
          <label htmlFor="breach-height">Breach Height (m)</label>
          <input
            id="breach-height"
            type="number"
            name="breach_height"
            value={form.breach_height ?? ""}
            onChange={onChange}
            disabled={isRunning}
            placeholder="e.g., 3"
            min="0.5"
            max="10"
          />
        </div>

        <div className="form-group">
          <label htmlFor="crs">Coordinate System</label>
          <input
            id="crs"
            type="text"
            name="crs"
            value={form.crs ?? "EPSG:4326"}
            onChange={onChange}
            disabled={isRunning}
            placeholder="EPSG:4326"
          />
        </div>

        <button
          type="submit"
          disabled={isRunning}
          className="btn-run"
        >
          {isRunning ? "Running Simulation" : "Run Simulation"}
        </button>
      </form>

      <div className="scenarios-section">
        <h3>Quick Scenarios</h3>
        <div className="scenarios-grid">
          {DEMO_SCENARIOS.map((scenario) => (
            <div
              key={scenario.id}
              className="scenario-card"
              onClick={() => {
                onChange({ target: { name: "scenario_id", value: scenario.id } });
                onChange({
                  target: { name: "breach_width", value: scenario.breachWidth },
                });
                onChange({
                  target: { name: "breach_height", value: scenario.breachHeight },
                });
              }}
            >
              <div className="scenario-icon">📊</div>
              <div>
                <strong>{scenario.name}</strong><br/>
                {scenario.breachWidth} m width × {scenario.breachHeight} m height
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}

export default ControlPanel;