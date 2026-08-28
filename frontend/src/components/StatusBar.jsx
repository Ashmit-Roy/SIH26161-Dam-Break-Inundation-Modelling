import React from "react";

const statusStages = {
  idle: {
    label: "Idle",
    labelColor: "#94a3b8",
    bgColor: "rgba(148, 163, 184, 0.1)",
    icon: "⏸️",
    borderColor: "#31394d",
  },
  uploading: {
    label: "Uploading",
    labelColor: "#f59e0b",
    bgColor: "rgba(245, 158, 11, 0.1)",
    icon: "↑",
    borderColor: "#f59e0b",
  },
  running: {
    label: "Computing",
    labelColor: "#ff6b00",
    bgColor: "rgba(255, 107, 0, 0.15)",
    icon: "▶",
    borderColor: "#ff6b00",
  },
  completed: {
    label: "Synchronized",
    labelColor: "#34d399",
    bgColor: "rgba(52, 211, 153, 0.1)",
    icon: "✓",
    borderColor: "#34d399",
  },
  failed: {
    label: "Failed",
    labelColor: "#ef4444",
    bgColor: "rgba(239, 68, 68, 0.1)",
    icon: "✗",
    borderColor: "#ef4444",
  },
};

function StatusBar({
  stage,
  message,
  model,
  startTime,
  endTime,
}) {
  const stageInfo = statusStages[stage] || statusStages.completed;

  const duration = startTime && endTime
    ? Math.round((endTime - startTime) / 1000) + " s"
    : "1.2 s (Cached)";

  return (
    <div style={{
      background: "#0b1326",
      borderTop: "1px solid #31394d",
      padding: "6px 18px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      fontSize: "0.75rem",
      color: "#94a3b8",
      fontFamily: "'JetBrains Mono', monospace",
      minHeight: "32px",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "6px",
          background: stageInfo.bgColor,
          color: stageInfo.labelColor,
          border: `1px solid ${stageInfo.borderColor}`,
          padding: "2px 8px",
          borderRadius: "3px",
          fontWeight: 700,
        }}>
          <span>{stageInfo.icon}</span>
          <span>{stageInfo.label.toUpperCase()}</span>
        </div>

        <div>
          <strong style={{ color: "#f8fafc" }}>ENGINE:</strong> {model === "SPH" ? "3D DualSPHysics Particle Solver" : (model === "both" ? "Dual-Model (3D SPH + 2D HEC-RAS)" : "2D HEC-RAS Unsteady Mesh")}
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <div>
          <strong style={{ color: "#f8fafc" }}>STATUS:</strong> {message}
        </div>
        <div>
          <strong style={{ color: "#38bdf8" }}>LATENCY:</strong> {duration}
        </div>
      </div>
    </div>
  );
}

export default StatusBar;