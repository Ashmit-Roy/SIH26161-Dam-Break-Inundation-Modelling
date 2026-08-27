import React from "react";

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
          <label htmlFor="river_dam">River / Dam Reach</label>
          <select
            id="river_dam"
            name="river_dam"
            value={form.river_dam ?? "rishiganga"}
            onChange={onChange}
            disabled={isRunning}
          >
            <option value="rishiganga">🌊 Rishiganga Dam & Gorge (DualSPHysics Case)</option>
            <option value="chamoli">🏔️ Dhauliganga - Chamoli River Reach</option>
            <option value="tehri">🏞️ Tehri Reservoir & Dam Reach</option>
            <option value="mullaperiyar">🌲 Periyar River Basin Reach</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="model">Hydraulic Model</label>
          <select
            id="model"
            name="model"
            value={form.model ?? "SPH"}
            onChange={onChange}
            disabled={isRunning}
          >
            <option value="SPH">SPH (Smoothed Particle Hydrodynamics)</option>
            <option value="Delft3D">Delft3D / Delft3D FM</option>
            <option value="both">Both (Comparison)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="scenario_id">Scenario</label>
          <select
            id="scenario_id"
            name="scenario_id"
            value={form.scenario_id ?? "scenario_a"}
            onChange={onChange}
            disabled={isRunning}
          >
            {(DEMO_SCENARIOS || []).map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.label || scenario.name || scenario.id}
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
            step="any"
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
            min="0.1"
            max="20"
            step="any"
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
          {isRunning ? "Running Simulation..." : "Run Simulation"}
        </button>
      </form>

      <div className="scenarios-section">
        <h3>Quick Scenarios</h3>
        <div className="scenarios-grid">
          {(DEMO_SCENARIOS || []).map((scenario) => (
            <div
              key={scenario.id}
              className="scenario-card"
              onClick={() => {
                onChange({ target: { name: "scenario_id", value: scenario.id } });
                onChange({
                  target: { name: "breach_width", value: scenario.breach_width || scenario.breachWidth || 10 },
                });
                onChange({
                  target: { name: "breach_height", value: scenario.breach_height || scenario.breachHeight || 2 },
                });
              }}
            >
              <div className="scenario-icon">📊</div>
              <div>
                <strong>{scenario.label || scenario.name}</strong><br/>
                {scenario.breach_width || scenario.breachWidth || 10} m width × {scenario.breach_height || scenario.breachHeight || 2} m height
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}

export default ControlPanel;