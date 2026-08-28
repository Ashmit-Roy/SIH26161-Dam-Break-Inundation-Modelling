import React, { useState } from "react";

function ControlPanel({
  form,
  onChange,
  onSubmit,
  isRunning,
  DEMO_SCENARIOS,
}) {
  const [openSections, setOpenSections] = useState({
    boundary: true,
    geometry: true,
    roughness: false,
  });

  const toggleSection = (section) => {
    setOpenSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const handleScenarioSelect = (scenarioId) => {
    onChange({ target: { name: "scenario_id", value: scenarioId } });
  };

  const breachWidth = Number(form.breach_width) || 15;
  const breachHeight = Number(form.breach_height) || 3;
  const estDischarge = Math.round(0.607 * Math.sqrt(9.81) * breachWidth * Math.pow(breachHeight, 1.5) * 1.45);

  return (
    <aside className="control-panel" style={{
      width: "350px",
      minWidth: "350px",
      background: "#0b1326",
      borderRight: "1px solid #31394d",
      display: "flex",
      flexDirection: "column",
      gap: "12px",
      padding: "14px",
      overflowY: "auto",
    }}>
      {/* 1. Project Branding & Hackathon Pitch Badge */}
      <div style={{ background: "rgba(15, 23, 42, 0.9)", border: "1px solid #31394d", borderRadius: "8px", padding: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "6px" }}>
          <span style={{
            background: "linear-gradient(135deg, #d946ef 0%, #a855f7 100%)",
            color: "#ffffff",
            padding: "2px 8px",
            borderRadius: "4px",
            fontSize: "0.68rem",
            fontWeight: 800,
            fontFamily: "'JetBrains Mono', monospace",
            letterSpacing: "0.5px",
          }}>
            🏆 HACKATHON PITCH
          </span>
          <span style={{ color: "#fb923c", fontSize: "0.7rem", fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>
            SIH26161
          </span>
        </div>
        <h2 style={{ fontSize: "1.1rem", fontWeight: 800, color: "#f8fafc", margin: "2px 0 4px 0" }}>
          PROJECT ALPHA-01
        </h2>
        
        {/* Scenario Context Summary */}
        <p style={{ fontSize: "0.76rem", color: "#94a3b8", lineHeight: 1.35 }}>
          Real-time hydrodynamic dam breach forecast & disaster response orchestration for high-altitude glacial canyons.
        </p>
      </div>

      <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {/* GROUP 1: BOUNDARY & SOLVER */}
        <div style={{ background: "#0f172a", border: "1px solid #31394d", borderRadius: "8px", overflow: "hidden" }}>
          <button
            type="button"
            onClick={() => toggleSection("boundary")}
            style={{
              width: "100%",
              background: "#1e293b",
              border: "none",
              padding: "8px 12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              color: "#f8fafc",
              fontSize: "0.78rem",
              fontWeight: 700,
              fontFamily: "'JetBrains Mono', monospace",
              cursor: "pointer",
            }}
          >
            <span>🛡️ BOUNDARY & SOLVER ENGINE</span>
            <span>{openSections.boundary ? "▼" : "▶"}</span>
          </button>

          {openSections.boundary && (
            <div style={{ padding: "10px", display: "flex", flexDirection: "column", gap: "8px" }}>
              <div>
                <label style={{ fontSize: "0.7rem", color: "#94a3b8", display: "block", marginBottom: "4px", fontWeight: 600 }}>Study Reach Selection</label>
                <select
                  name="river_dam"
                  value={form.river_dam ?? "rishiganga"}
                  onChange={onChange}
                  disabled={isRunning}
                  style={{
                    width: "100%",
                    background: "#0b1326",
                    color: "#f8fafc",
                    border: "1px solid #31394d",
                    borderRadius: "6px",
                    padding: "6px 8px",
                    fontSize: "0.76rem",
                    fontFamily: "'JetBrains Mono', monospace",
                  }}
                >
                  <option value="rishiganga">🌊 Rishiganga Glacial Gorge (Uttarakhand)</option>
                  <option value="chamoli">🏔️ Dhauliganga - Chamoli Reach</option>
                  <option value="tehri">🏞️ Tehri Reservoir & Dam Spillway</option>
                  <option value="mullaperiyar">🌲 Periyar River Basin (Mullaperiyar)</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: "0.7rem", color: "#94a3b8", display: "block", marginBottom: "4px", fontWeight: 600 }}>Hydrodynamic Solver Model</label>
                <select
                  name="model"
                  value={form.model ?? "SPH"}
                  onChange={onChange}
                  disabled={isRunning}
                  style={{
                    width: "100%",
                    background: "#0b1326",
                    color: "#f8fafc",
                    border: "1px solid #31394d",
                    borderRadius: "6px",
                    padding: "6px 8px",
                    fontSize: "0.76rem",
                    fontFamily: "'JetBrains Mono', monospace",
                  }}
                >
                  <option value="SPH">💧 3D SPH (DualSPHysics Particle Solver)</option>
                  <option value="HEC-RAS">🌊 2D HEC-RAS (Unsteady Flow Mesh)</option>
                  <option value="both">⚡ Dual-Model Cross-Validation (3D SPH + 2D HEC-RAS)</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* GROUP 2: GEOMETRY PARAMETERS */}
        <div style={{ background: "#0f172a", border: "1px solid #31394d", borderRadius: "8px", overflow: "hidden" }}>
          <button
            type="button"
            onClick={() => toggleSection("geometry")}
            style={{
              width: "100%",
              background: "#1e293b",
              border: "none",
              padding: "8px 12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              color: "#f8fafc",
              fontSize: "0.78rem",
              fontWeight: 700,
              fontFamily: "'JetBrains Mono', monospace",
              cursor: "pointer",
            }}
          >
            <span>📐 BREACH GEOMETRY CONTROLS</span>
            <span>{openSections.geometry ? "▼" : "▶"}</span>
          </button>

          {openSections.geometry && (
            <div style={{ padding: "10px", display: "flex", flexDirection: "column", gap: "10px" }}>
              {/* Breach Width */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.7rem", color: "#94a3b8", marginBottom: "4px" }}>
                  <label htmlFor="breach_width_input">Breach Width (B)</label>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    <input
                      id="breach_width_input"
                      type="number"
                      name="breach_width"
                      value={breachWidth}
                      onChange={onChange}
                      disabled={isRunning}
                      min="5"
                      max="80"
                      style={{
                        width: "50px",
                        background: "#0b1326",
                        color: "#fb923c",
                        border: "1px solid #31394d",
                        borderRadius: "4px",
                        padding: "2px 4px",
                        fontSize: "0.76rem",
                        fontFamily: "'JetBrains Mono', monospace",
                        fontWeight: 700,
                        textAlign: "right",
                      }}
                    />
                    <span style={{ color: "#94a3b8", fontSize: "0.7rem" }}>m</span>
                  </div>
                </div>
                <input
                  type="range"
                  name="breach_width"
                  value={breachWidth}
                  onChange={onChange}
                  disabled={isRunning}
                  min="5"
                  max="80"
                  step="1"
                  style={{ width: "100%", accentColor: "#fb923c", height: "4px", cursor: "pointer" }}
                />
              </div>

              {/* Breach Height */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.7rem", color: "#94a3b8", marginBottom: "4px" }}>
                  <label htmlFor="breach_height_input">Breach Depth / Water Head (H)</label>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    <input
                      id="breach_height_input"
                      type="number"
                      name="breach_height"
                      value={breachHeight}
                      onChange={onChange}
                      disabled={isRunning}
                      min="1"
                      max="15"
                      step="0.5"
                      style={{
                        width: "50px",
                        background: "#0b1326",
                        color: "#38bdf8",
                        border: "1px solid #31394d",
                        borderRadius: "4px",
                        padding: "2px 4px",
                        fontSize: "0.76rem",
                        fontFamily: "'JetBrains Mono', monospace",
                        fontWeight: 700,
                        textAlign: "right",
                      }}
                    />
                    <span style={{ color: "#94a3b8", fontSize: "0.7rem" }}>m</span>
                  </div>
                </div>
                <input
                  type="range"
                  name="breach_height"
                  value={breachHeight}
                  onChange={onChange}
                  disabled={isRunning}
                  min="1"
                  max="15"
                  step="0.5"
                  style={{ width: "100%", accentColor: "#38bdf8", height: "4px", cursor: "pointer" }}
                />
              </div>
            </div>
          )}
        </div>
      </form>

      {/* Preset Scenario Benchmarks */}
      <div style={{ background: "#0f172a", border: "1px solid #31394d", borderRadius: "8px", padding: "10px" }}>
        <div style={{ fontSize: "0.68rem", color: "#94a3b8", fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", marginBottom: "6px" }}>
          PRESET BENCHMARK SCENARIOS
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
          {(DEMO_SCENARIOS || []).map((sc) => {
            const isSelected = form.scenario_id === sc.id;
            return (
              <button
                key={sc.id}
                onClick={() => handleScenarioSelect(sc.id)}
                style={{
                  background: isSelected ? "rgba(251, 146, 60, 0.15)" : "#0b1326",
                  color: isSelected ? "#fb923c" : "#cbd5e1",
                  border: isSelected ? "1px solid #fb923c" : "1px solid #31394d",
                  borderRadius: "6px",
                  padding: "6px 10px",
                  fontSize: "0.74rem",
                  fontFamily: "'JetBrains Mono', monospace",
                  textAlign: "left",
                  cursor: "pointer",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span style={{ fontWeight: isSelected ? 700 : 500 }}>{sc.label.split("—")[0]}</span>
                <span style={{ fontSize: "0.68rem", opacity: 0.8 }}>{sc.breach_width}m × {sc.breach_height}m</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 💡 Key Insights Panel for Judges (Bottom of Sidebar) */}
      <div style={{
        marginTop: "auto",
        background: "linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%)",
        border: "1px solid rgba(56, 189, 248, 0.3)",
        borderRadius: "8px",
        padding: "12px",
        boxShadow: "0 4px 14px rgba(0,0,0,0.4)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#38bdf8", fontWeight: 700, fontSize: "0.75rem", fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", marginBottom: "8px", borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: "4px" }}>
          💡 KEY INSIGHTS (EXECUTIVE NARRATIVE)
        </div>

        <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "6px", fontSize: "0.74rem", color: "#cbd5e1", lineHeight: 1.35 }}>
          <li style={{ display: "flex", gap: "6px" }}>
            <span style={{ color: "#fb923c" }}>⚡</span>
            <span><b>Breach Surge Flow:</b> Peak outflow (<b>{estDischarge.toLocaleString()} m³/s</b>) exceeds gorge channel capacity within <b>18 mins</b>.</span>
          </li>
          <li style={{ display: "flex", gap: "6px" }}>
            <span style={{ color: "#ef4444" }}>🚨</span>
            <span><b>Critical Impact:</b> Reni Suspension Bridge & Tapovan Hydro Project in direct flash flood surge path.</span>
          </li>
          <li style={{ display: "flex", gap: "6px" }}>
            <span style={{ color: "#34d399" }}>🛡️</span>
            <span><b>Actionable Response:</b> Early warning window provides <b>18 mins</b> for safe evacuation to Sector-B heights.</span>
          </li>
        </ul>
      </div>
    </aside>
  );
}

export default ControlPanel;