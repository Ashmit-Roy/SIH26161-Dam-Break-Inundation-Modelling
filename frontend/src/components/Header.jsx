import React from "react";

function Header() {
  return (
    <header className="main-header">
      <div className="header-content">
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <div className="logo-badge">🌊</div>
          <div>
            <h1 className="header-title">
              Dam Break Inundation & Hydrodynamic Modelling
            </h1>
            <div className="header-sub-bar">
              <span className="sih-tag">🏆 SIH 26161 · Smart India Hackathon 2026</span>
              <span className="reach-tag">Case Study: Rishiganga Valley & Mountain Gorge</span>
            </div>
          </div>
        </div>

        {/* Live System Status Telemetry */}
        <div className="header-telemetry">
          <div className="telemetry-pill">
            <span className="pulse-dot"></span>
            <span>3D DualSPHysics Particle Engine: <strong style={{ color: "#38bdf8" }}>Active (9.4k particles)</strong></span>
          </div>
          <div className="telemetry-pill">
            <span className="pulse-dot green-dot"></span>
            <span>2D HEC-RAS / SWE: <strong style={{ color: "#34d399" }}>Synchronized</strong></span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;