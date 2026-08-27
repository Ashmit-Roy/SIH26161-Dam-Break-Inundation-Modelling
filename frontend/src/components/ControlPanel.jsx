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
  const handleScenarioSelect = (scenarioId) => {
    const sc = (DEMO_SCENARIOS || []).find((s) => s.id === scenarioId);
    if (sc) {
      onChange({ target: { name: "scenario_id", value: sc.id } });
      onChange({ target: { name: "breach_width", value: sc.breach_width } });
      onChange({ target: { name: "breach_height", value: sc.breach_height } });
    }
  };

  const breachWidth = Number(form.breach_width) || 15;
  const breachHeight = Number(form.breach_height) || 3;
  const estDischarge = Math.round(0.607 * Math.sqrt(9.81) * breachWidth * Math.pow(breachHeight, 1.5) * 1.45);

  return (
    <aside className="control-panel">
      <div className="panel-header-badge">
        <h2>🏗️ Hydraulic Scenario Setup</h2>
        <span className="live-engine-tag">DualSPHysics 5.4</span>
      </div>

      <form onSubmit={onSubmit} className="control-form">
        {/* River Basin / Reach */}
        <div className="form-group">
          <label htmlFor="river_dam">River Basin & Study Reach</label>
          <select
            id="river_dam"
            name="river_dam"
            value={form.river_dam ?? "rishiganga"}
            onChange={onChange}
            disabled={isRunning}
            className="modern-select"
          >
            <option value="rishiganga">🌊 Rishiganga Gorge & Reni Reach (Uttarakhand)</option>
            <option value="chamoli">🏔️ Dhauliganga - Chamoli River Reach</option>
            <option value="tehri">🏞️ Tehri Reservoir & Dam Gorge</option>
            <option value="mullaperiyar">🌲 Periyar River Basin Reach</option>
          </select>
        </div>

        {/* Hydraulic Model Architecture */}
        <div className="form-group">
          <label htmlFor="model">Hydrodynamic Solver Architecture</label>
          <select
            id="model"
            name="model"
            value={form.model ?? "SPH"}
            onChange={onChange}
            disabled={isRunning}
            className="modern-select"
          >
            <option value="SPH">💧 3D SPH (DualSPHysics Particle Navier-Stokes)</option>
            <option value="Delft3D">🌊 2D HEC-RAS / Delft3D (Shallow Water SWE)</option>
            <option value="both">⚡ Dual-Model Comparison (3D SPH vs 2D HEC-RAS)</option>
          </select>
        </div>

        {/* Preset Scenarios */}
        <div className="form-group">
          <label htmlFor="scenario_id">Calibrated Breach Scenario</label>
          <select
            id="scenario_id"
            name="scenario_id"
            value={form.scenario_id ?? "scenario_a"}
            onChange={(e) => handleScenarioSelect(e.target.value)}
            disabled={isRunning}
            className="modern-select"
          >
            {(DEMO_SCENARIOS || []).map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.label}
              </option>
            ))}
          </select>
        </div>

        {/* Breach Geometry Controls */}
        <div className="form-group">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <label htmlFor="breach-width">Breach Width (m)</label>
            <span className="slider-val-badge">{breachWidth} m</span>
          </div>
          <input
            id="breach-width"
            type="range"
            name="breach_width"
            value={breachWidth}
            onChange={onChange}
            disabled={isRunning}
            min="5"
            max="80"
            step="1"
            className="modern-slider"
          />
        </div>

        <div className="form-group">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <label htmlFor="breach-height">Breach Depth / Water Head (m)</label>
            <span className="slider-val-badge">{breachHeight} m</span>
          </div>
          <input
            id="breach-height"
            type="range"
            name="breach_height"
            value={breachHeight}
            onChange={onChange}
            disabled={isRunning}
            min="1"
            max="15"
            step="0.5"
            className="modern-slider"
          />
        </div>

        {/* Live Hydrodynamic Estimation Preview */}
        <div className="hydro-preview-card">
          <div className="hydro-preview-title">⚡ Real-Time Physics Estimate</div>
          <div className="hydro-preview-row">
            <span>Peak Breach Discharge (Q_p):</span>
            <strong>{estDischarge.toLocaleString()} m³/s</strong>
          </div>
          <div className="hydro-preview-row">
            <span>Spatial Reference:</span>
            <code>EPSG:32644 (UTM 44N)</code>
          </div>
        </div>

        <button
          type="submit"
          disabled={isRunning}
          className={`btn-run ${isRunning ? "btn-running" : ""}`}
        >
          {isRunning ? (
            <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
              <span className="spinner-icon">⏳</span> Computing Hydrodynamics...
            </span>
          ) : (
            "🚀 Execute Hydraulic Simulation"
          )}
        </button>
      </form>

      {/* Quick Scenario Cards */}
      <div className="scenarios-section">
        <h3>⚡ Quick Scenario Selector</h3>
        <div className="scenarios-grid">
          {(DEMO_SCENARIOS || []).map((scenario) => {
            const isSelected = form.scenario_id === scenario.id;
            return (
              <div
                key={scenario.id}
                className={`scenario-card ${isSelected ? "scenario-card-active" : ""}`}
                onClick={() => handleScenarioSelect(scenario.id)}
              >
                <div className="scenario-header">
                  <span className="scenario-badge">{scenario.id.toUpperCase()}</span>
                  <strong>{scenario.label.split("—")[0]}</strong>
                </div>
                <div className="scenario-specs">
                  📐 {scenario.breach_width}m width × {scenario.breach_height}m depth
                </div>
                <div className="scenario-desc">{scenario.desc}</div>
              </div>
            );
          })}
        </div>
      </div>
    </aside>
  );
}

export default ControlPanel;