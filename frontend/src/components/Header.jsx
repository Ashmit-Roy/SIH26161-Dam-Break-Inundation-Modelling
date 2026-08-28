import React from "react";

function Header() {
  return (
    <header className="main-header">
      <div className="header-content">
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <div className="logo-badge" style={{ fontSize: "1.8rem" }}>🏛️</div>
          <div>
            <h1 className="header-title" style={{ fontSize: "1.4rem", fontWeight: 800 }}>
              INUNDATION-OPS: Dam-Break Emergency Decision Support System
            </h1>
            <div className="header-sub-bar" style={{ display: "flex", gap: "10px", alignItems: "center", marginTop: "4px", flexWrap: "wrap" }}>
              <span className="sih-tag" style={{ background: "rgba(239, 68, 68, 0.2)", color: "#fca5a5", border: "1px solid rgba(239, 68, 68, 0.4)" }}>
                🏆 SIH26161 · National Disaster Risk Assessment
              </span>
              <span className="reach-tag" style={{ color: "#38bdf8" }}>
                📍 Rishiganga Glacial Gorge & Dhauliganga Basin (Chamoli, Uttarakhand)
              </span>
            </div>
          </div>
        </div>

        {/* Live Hydrodynamic Telemetry */}
        <div className="header-telemetry">
          <div className="telemetry-pill">
            <span className="pulse-dot"></span>
            <span>3D DualSPHysics Engine: <strong style={{ color: "#38bdf8" }}>Active</strong></span>
          </div>
          <div className="telemetry-pill">
            <span className="pulse-dot green-dot"></span>
            <span>2D HEC-RAS Solver: <strong style={{ color: "#34d399" }}>Synchronized (10.1k cells)</strong></span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;