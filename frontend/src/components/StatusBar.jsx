import React from "react";

const statusStages = {
  idle: {
    label: "Idle",
    labelColor: "#6c757d",
    bgColor: "rgba(108, 117, 125, 0.1)",
    icon: "⏸️",
    borderColor: "#6c757d",
  },
  uploading: {
    label: "Uploading",
    labelColor: "#ffc107",
    bgColor: "rgba(255, 193, 7, 0.1)",
    icon: "↑",
    borderColor: "#ffc107",
  },
  running: {
    label: "Running",
    labelColor: "#e94560",
    bgColor: "rgba(233, 69, 96, 0.1)",
    icon: "▶",
    borderColor: "#e94560",
  },
  completed: {
    label: "Completed",
    labelColor: "#28a745",
    bgColor: "rgba(40, 167, 69, 0.1)",
    icon: "✓",
    borderColor: "#28a745",
  },
  failed: {
    label: "Failed",
    labelColor: "#dc3545",
    bgColor: "rgba(220, 53, 69, 0.1)",
    icon: "✗",
    borderColor: "#dc3545",
  },
};

function StatusBar({
  stage,
  message,
  model,
  startTime,
  endTime,
}) {
  const stageInfo = statusStages[stage] || statusStakes.idle;

  const duration = startTime && endTime
    ? Math.round((endTime - startTime) / 1000) + " s"
    : "—";

  return (
    <div className="status-bar">
      <div className="status-indicator">
        <span className="status-icon">{stageInfo.icon}</span>
        <span className="status-label">{stageInfo.label}</span>
      </div>

      <div className="status-details">
        <div>
          <strong>Model:</strong> {model ?? "None selected"}
        </div>
        <div>
          <strong>Status:</strong> {message}
        </div>
        {startTime && endTime && (
          <div>
            <strong>Duration:</strong> {duration}
          </div>
        )}
      </div>
    </div>
  );
}

export default StatusBar;