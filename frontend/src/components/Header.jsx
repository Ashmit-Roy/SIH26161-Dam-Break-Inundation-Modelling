import React from "react";

function Header({ onSubmit, isRunning, reachKey = "rishiganga", scenarioId = "scenario_a", activeTab = "Simulation", onTabChange }) {
  const reachNames = {
    rishiganga: "Rishiganga Glacial Gorge (UTM 44N)",
    chamoli: "Dhauliganga - Chamoli Basin",
    tehri: "Tehri Hydro Reservoir",
    mullaperiyar: "Periyar River Basin",
  };

  const handleTabClick = (tab) => {
    if (onTabChange) onTabChange(tab);
    let targetId = "map-section";
    if (tab === "Models") targetId = "comparison-section";
    if (tab === "Analysis") targetId = "results-section";

    const elem = document.getElementById(targetId);
    if (elem) {
      elem.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <header className="main-header" style={{
      background: "#0b1326",
      borderBottom: "1px solid #31394d",
      padding: "8px 20px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      minHeight: "52px",
      zIndex: 1000,
      boxShadow: "0 2px 14px rgba(0,0,0,0.5)",
    }}>
      {/* Left: Brand Logo, SIH Tag & Breadcrumbs */}
      <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
        <span style={{
          background: "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
          color: "#ffffff",
          padding: "3px 8px",
          borderRadius: "4px",
          fontSize: "0.7rem",
          fontWeight: 800,
          fontFamily: "'JetBrains Mono', monospace",
          letterSpacing: "0.5px",
          boxShadow: "0 0 10px rgba(2, 132, 199, 0.4)",
        }}>
          🏛️ SIH26161 DSS
        </span>

        <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#f8fafc", fontWeight: 800, fontSize: "1rem", letterSpacing: "0.2px" }}>
          HYDROLOGIC <span style={{ color: "#38bdf8", fontWeight: 600, fontSize: "0.85rem" }}>| Decision Support System</span>
        </div>

        <div style={{ width: "1px", height: "18px", background: "#31394d" }}></div>

        {/* Breadcrumbs */}
        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.78rem", color: "#94a3b8", fontFamily: "'JetBrains Mono', monospace" }}>
          <span>PROJECT ALPHA-01</span>
          <span>&gt;</span>
          <span style={{ color: "#38bdf8", fontWeight: 700 }}>{reachNames[reachKey] || "Rishiganga Glacial Gorge"}</span>
          <span>&gt;</span>
          <span style={{ color: "#fb923c", fontWeight: 700 }}>{(scenarioId || "scenario_a").toUpperCase()}</span>
        </div>
      </div>

      {/* Center: Navigation Tabs (Models | Simulation | Analysis) */}
      <nav style={{ display: "flex", gap: "4px", background: "#0f172a", padding: "3px", borderRadius: "6px", border: "1px solid #31394d" }}>
        {["Simulation", "Models", "Analysis"].map((tab) => {
          const isActive = activeTab === tab;
          return (
            <button
              key={tab}
              onClick={() => handleTabClick(tab)}
              style={{
                background: isActive ? "#38bdf8" : "transparent",
                color: isActive ? "#0f172a" : "#94a3b8",
                border: isActive ? "1px solid #38bdf8" : "1px solid transparent",
                borderRadius: "4px",
                padding: "4px 16px",
                fontSize: "0.78rem",
                fontWeight: isActive ? 800 : 500,
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
            >
              {tab === "Models" ? "🔬 Models" : (tab === "Analysis" ? "📊 Analysis" : "🗺️ Simulation")}
            </button>
          );
        })}
      </nav>

      {/* Right: Live Status Pulse & Safety Orange Action Button */}
      <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
        {/* Pulsing Status Badge */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          background: isRunning ? "rgba(239, 68, 68, 0.15)" : "rgba(52, 211, 153, 0.12)",
          border: `1px solid ${isRunning ? '#ef4444' : '#34d399'}`,
          padding: "3px 10px",
          borderRadius: "6px",
          fontSize: "0.75rem",
          fontFamily: "'JetBrains Mono', monospace",
          fontWeight: 700,
          color: isRunning ? "#fca5a5" : "#6ee7b7",
        }}>
          <span style={{
            display: "inline-block",
            width: "8px",
            height: "8px",
            borderRadius: "50%",
            background: isRunning ? "#ef4444" : "#34d399",
            boxShadow: isRunning ? "0 0 10px #ef4444" : "0 0 8px #34d399",
          }}></span>
          <span>{isRunning ? "SOLVER COMPUTING..." : "SOLVER READY"}</span>
        </div>

        <button
          onClick={onSubmit}
          disabled={isRunning}
          style={{
            background: isRunning ? "#64748b" : "#fb923c",
            color: "#0f172a",
            border: "none",
            borderRadius: "6px",
            padding: "6px 20px",
            fontSize: "0.82rem",
            fontWeight: 800,
            fontFamily: "'JetBrains Mono', monospace",
            letterSpacing: "0.5px",
            cursor: isRunning ? "not-allowed" : "pointer",
            boxShadow: isRunning ? "none" : "0 0 14px rgba(251, 146, 60, 0.5)",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            transition: "all 0.15s ease",
          }}
        >
          {isRunning ? "⏳ COMPUTING..." : "▶ RUN SIMULATION"}
        </button>
      </div>
    </header>
  );
}

export default Header;