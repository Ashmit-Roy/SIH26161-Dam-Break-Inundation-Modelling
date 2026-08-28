import React, { useState, useMemo } from "react";

// Default SPH time series dataset from DualSPHysics 3D Solver (case_rishiganga)
const DEFAULT_SPH_TIME_SERIES = [
  { time_s: 0.0, particle_count: 9450, max_velocity_mps: 0.0, mean_velocity_mps: 0.0, front_position_x_local_m: 2806.0 },
  { time_s: 1.0, particle_count: 9450, max_velocity_mps: 14.56, mean_velocity_mps: 8.73, front_position_x_local_m: 2803.5 },
  { time_s: 2.0, particle_count: 9450, max_velocity_mps: 36.01, mean_velocity_mps: 16.19, front_position_x_local_m: 2794.2 },
  { time_s: 3.0, particle_count: 9450, max_velocity_mps: 74.23, mean_velocity_mps: 20.75, front_position_x_local_m: 2780.0 },
  { time_s: 4.0, particle_count: 9450, max_velocity_mps: 76.28, mean_velocity_mps: 25.22, front_position_x_local_m: 2764.6 },
  { time_s: 5.0, particle_count: 9450, max_velocity_mps: 96.06, mean_velocity_mps: 29.45, front_position_x_local_m: 2734.2 },
  { time_s: 6.0, particle_count: 9450, max_velocity_mps: 72.88, mean_velocity_mps: 33.7, front_position_x_local_m: 2706.4 },
  { time_s: 7.0, particle_count: 9449, max_velocity_mps: 86.81, mean_velocity_mps: 38.53, front_position_x_local_m: 2703.8 },
  { time_s: 8.0, particle_count: 9449, max_velocity_mps: 85.63, mean_velocity_mps: 43.86, front_position_x_local_m: 2686.7 },
  { time_s: 9.0, particle_count: 7831, max_velocity_mps: 94.1, mean_velocity_mps: 41.33, front_position_x_local_m: 2669.5 },
  { time_s: 10.0, particle_count: 5987, max_velocity_mps: 92.72, mean_velocity_mps: 33.1, front_position_x_local_m: 2654.0 },
  { time_s: 11.0, particle_count: 5187, max_velocity_mps: 93.64, mean_velocity_mps: 29.05, front_position_x_local_m: 2638.7 },
  { time_s: 12.0, particle_count: 4613, max_velocity_mps: 102.37, mean_velocity_mps: 25.78, front_position_x_local_m: 2623.6 },
  { time_s: 13.0, particle_count: 4274, max_velocity_mps: 95.58, mean_velocity_mps: 23.91, front_position_x_local_m: 2607.7 },
  { time_s: 14.0, particle_count: 3990, max_velocity_mps: 95.42, mean_velocity_mps: 21.66, front_position_x_local_m: 2587.3 },
  { time_s: 15.0, particle_count: 3738, max_velocity_mps: 86.2, mean_velocity_mps: 19.29, front_position_x_local_m: 2570.9 },
  { time_s: 16.0, particle_count: 3596, max_velocity_mps: 91.46, mean_velocity_mps: 18.4, front_position_x_local_m: 2550.4 },
  { time_s: 17.0, particle_count: 3320, max_velocity_mps: 87.95, mean_velocity_mps: 14.15, front_position_x_local_m: 2527.4 },
  { time_s: 18.0, particle_count: 3259, max_velocity_mps: 89.5, mean_velocity_mps: 13.7, front_position_x_local_m: 2502.6 },
  { time_s: 20.0, particle_count: 3040, max_velocity_mps: 95.9, mean_velocity_mps: 10.03, front_position_x_local_m: 2453.2 },
  { time_s: 25.0, particle_count: 2932, max_velocity_mps: 67.56, mean_velocity_mps: 9.2, front_position_x_local_m: 2335.9 },
  { time_s: 30.0, particle_count: 2888, max_velocity_mps: 80.18, mean_velocity_mps: 9.2, front_position_x_local_m: 2220.0 },
  { time_s: 35.0, particle_count: 2872, max_velocity_mps: 69.46, mean_velocity_mps: 9.53, front_position_x_local_m: 2105.2 },
  { time_s: 40.0, particle_count: 2831, max_velocity_mps: 42.1, mean_velocity_mps: 9.11, front_position_x_local_m: 1987.4 },
  { time_s: 48.0, particle_count: 2831, max_velocity_mps: 80.37, mean_velocity_mps: 10.07, front_position_x_local_m: 1894.3 },
  { time_s: 55.0, particle_count: 2806, max_velocity_mps: 40.62, mean_velocity_mps: 9.89, front_position_x_local_m: 1775.2 },
  { time_s: 60.0, particle_count: 2806, max_velocity_mps: 38.13, mean_velocity_mps: 9.93, front_position_x_local_m: 1715.0 },
  { time_s: 61.0, particle_count: 61, max_velocity_mps: 0.0, mean_velocity_mps: 0.0, front_position_x_local_m: 0.0 },
];

function HydrographChart({ timeSeries, peakVelocity = 89.1, arrivalTime = 18.0, peakDischarge = 1420, activeTimeStep = 12, onSelectTime = null }) {
  const [hoveredPoint, setHoveredPoint] = useState(null);
  const [showMean, setShowMean] = useState(true);

  const warnTimeNum = Number(arrivalTime) || 18.0;
  const currentPeakVel = Number(peakVelocity) || 89.1;

  // Chart dimensions
  const width = 640;
  const height = 260;
  const padding = { top: 30, right: 30, bottom: 40, left: 50 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;

  const maxT = useMemo(() => {
    return Math.max(60, Math.ceil((warnTimeNum + 5) / 10) * 10);
  }, [warnTimeNum]);

  const data = useMemo(() => {
    const base = (Array.isArray(timeSeries) && timeSeries.length > 0)
      ? [...timeSeries]
      : [...DEFAULT_SPH_TIME_SERIES];
    
    // Scale velocities relative to peakVelocity dynamically
    const scaleFactor = currentPeakVel / 102.37;
    let formatted = base.map((pt) => ({
      ...pt,
      max_velocity_mps: Number((pt.max_velocity_mps * scaleFactor).toFixed(2)),
      mean_velocity_mps: Number((pt.mean_velocity_mps * scaleFactor).toFixed(2)),
    }));

    // If warning time extends beyond 60s, extend curve smoothly to maxT so graph is full & continuous
    const lastPt = formatted[formatted.length - 1];
    const lastTime = lastPt ? lastPt.time_s : 61;
    if (maxT > lastTime) {
      // Intermediate warning point
      formatted.push({
        time_s: Number(warnTimeNum.toFixed(1)),
        particle_count: 2806,
        max_velocity_mps: Number((currentPeakVel * 0.32).toFixed(2)),
        mean_velocity_mps: Number((currentPeakVel * 0.08).toFixed(2)),
        front_position_x_local_m: 1400.0,
      });
      // Tail point at maxT
      formatted.push({
        time_s: maxT,
        particle_count: 800,
        max_velocity_mps: 0.0,
        mean_velocity_mps: 0.0,
        front_position_x_local_m: 0.0,
      });
    }

    return formatted;
  }, [timeSeries, currentPeakVel, warnTimeNum, maxT]);

  // Clean, evenly spaced X-axis ticks to prevent label collision
  const xTicks = useMemo(() => {
    const ticks = [];
    const step = Math.max(10, Math.ceil(maxT / 5 / 10) * 10);
    for (let t = 0; t <= maxT; t += step) {
      ticks.push(t);
    }
    return ticks;
  }, [maxT]);

  const maxV = useMemo(() => {
    const vals = data.map((d) => (typeof d.max_velocity_mps === "number" ? d.max_velocity_mps : 0));
    return Math.max(...vals, currentPeakVel + 15, 100);
  }, [data, currentPeakVel]);

  const scaleX = (t) => {
    const val = typeof t === "number" && !isNaN(t) ? t : 0;
    return padding.left + (val / (maxT || 61)) * innerWidth;
  };

  const scaleY = (v) => {
    const val = typeof v === "number" && !isNaN(v) ? v : 0;
    return padding.top + innerHeight - (val / (maxV || 110)) * innerHeight;
  };

  // SVG path for Max Velocity
  const maxVelPath = useMemo(() => {
    if (!data || data.length === 0) return "";
    return data
      .map((d, i) => `${i === 0 ? "M" : "L"} ${scaleX(d.time_s).toFixed(1)},${scaleY(d.max_velocity_mps).toFixed(1)}`)
      .join(" ");
  }, [data, maxT, maxV]);

  // Area under curve for Max Velocity
  const areaPath = useMemo(() => {
    if (!data || data.length === 0) return "";
    const first = data[0];
    const last = data[data.length - 1];
    return `${maxVelPath} L ${scaleX(last.time_s).toFixed(1)},${(padding.top + innerHeight).toFixed(1)} L ${scaleX(first.time_s).toFixed(1)},${(padding.top + innerHeight).toFixed(1)} Z`;
  }, [data, maxVelPath, innerHeight]);

  // SVG path for Mean Velocity
  const meanVelPath = useMemo(() => {
    if (!data || data.length === 0) return "";
    return data
      .map((d, i) => `${i === 0 ? "M" : "L"} ${scaleX(d.time_s).toFixed(1)},${scaleY(d.mean_velocity_mps || 0).toFixed(1)}`)
      .join(" ");
  }, [data, maxT, maxV]);

  // Find peak point
  const peakPoint = useMemo(() => {
    if (!data || data.length === 0) return { time_s: 12.0, max_velocity_mps: currentPeakVel, particle_count: 4613 };
    return data.reduce((prev, curr) => ((curr.max_velocity_mps || 0) > (prev.max_velocity_mps || 0) ? curr : prev), data[0]);
  }, [data, currentPeakVel]);

  // Warning point at t = warnTimeNum
  const warningPoint = useMemo(() => {
    if (!data || data.length === 0) return { time_s: warnTimeNum, max_velocity_mps: currentPeakVel * 0.32 };
    return data.find((d) => Math.abs(d.time_s - warnTimeNum) < 2.0) || { time_s: warnTimeNum, max_velocity_mps: currentPeakVel * 0.32 };
  }, [data, warnTimeNum, currentPeakVel]);

  const activePoint = hoveredPoint || (activeTimeStep !== null ? data.find((d) => Math.abs(d.time_s - activeTimeStep) < 1.0) : peakPoint);

  return (
    <div className="hydrograph-card" style={{ background: "#16213e", borderRadius: "8px", padding: "16px", color: "#f1f5f9", border: "1px solid #323f5c", boxShadow: "0 4px 16px rgba(0,0,0,0.3)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
        <div>
          <h3 style={{ margin: 0, fontSize: "1.05rem", display: "flex", alignItems: "center", gap: "8px", color: "#f8fafc" }}>
            <span>🌊</span> Velocity Hydrograph (DualSPHysics Solver)
          </h3>
          <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>
            Peak Velocity: <strong style={{ color: "#ef4444" }}>{currentPeakVel} m/s</strong> · Arrival Window: <strong style={{ color: "#fbbf24" }}>{warnTimeNum.toFixed(1)}s</strong> · Peak Discharge: <strong style={{ color: "#38bdf8" }}>{Number(peakDischarge).toLocaleString()} m³/s</strong>
          </div>
        </div>

        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <label style={{ fontSize: "0.75rem", display: "flex", alignItems: "center", gap: "4px", cursor: "pointer", color: "#38bdf8" }}>
            <input
              type="checkbox"
              checked={showMean}
              onChange={(e) => setShowMean(e.target.checked)}
              style={{ cursor: "pointer", accentColor: "#38bdf8" }}
            />
            Show Mean Velocity
          </label>
        </div>
      </div>

      <div style={{ position: "relative", width: "100%", overflowX: "auto" }}>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          style={{ width: "100%", height: "auto", display: "block" }}
          onMouseLeave={() => setHoveredPoint(null)}
        >
          <defs>
            <linearGradient id="velGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#e94560" stopOpacity="0.5" />
              <stop offset="60%" stopColor="#e94560" stopOpacity="0.1" />
              <stop offset="100%" stopColor="#e94560" stopOpacity="0.0" />
            </linearGradient>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#fbbf24" />
              <stop offset="20%" stopColor="#e94560" />
              <stop offset="80%" stopColor="#ef4444" />
              <stop offset="100%" stopColor="#38bdf8" />
            </linearGradient>
          </defs>

          {/* Y-axis Grid lines */}
          {[0, Math.round(maxV * 0.25), Math.round(maxV * 0.5), Math.round(maxV * 0.75), Math.round(maxV)].map((v) => (
            <g key={`grid-y-${v}`}>
              <line
                x1={padding.left}
                y1={scaleY(v)}
                x2={width - padding.right}
                y2={scaleY(v)}
                stroke="#334155"
                strokeDasharray="3 3"
              />
              <text
                x={padding.left - 8}
                y={scaleY(v) + 4}
                fill="#94a3b8"
                fontSize="10"
                textAnchor="end"
              >
                {v} m/s
              </text>
            </g>
          ))}

          {/* X-axis Even Grid Ticks */}
          {xTicks.map((t) => (
            <g key={`grid-x-${t}`}>
              <line
                x1={scaleX(t)}
                y1={padding.top}
                x2={scaleX(t)}
                y2={height - padding.bottom}
                stroke="#334155"
                strokeDasharray="3 3"
                strokeWidth={1}
              />
              <text
                x={scaleX(t)}
                y={height - padding.bottom + 16}
                fill="#94a3b8"
                fontSize="10"
                textAnchor="middle"
              >
                {t}s
              </text>
            </g>
          ))}

          {/* Dynamic Warning arrival line highlight */}
          <line
            x1={scaleX(warnTimeNum)}
            y1={padding.top}
            x2={scaleX(warnTimeNum)}
            y2={height - padding.bottom}
            stroke="#f59e0b"
            strokeWidth="2"
            strokeDasharray="4 2"
          />

          {/* Area Fill */}
          <path d={areaPath} fill="url(#velGradient)" />

          {/* Mean Velocity Line */}
          {showMean && (
            <path
              d={meanVelPath}
              fill="none"
              stroke="#38bdf8"
              strokeWidth="2"
              strokeDasharray="4 3"
            />
          )}

          {/* Max Velocity Line */}
          <path
            d={maxVelPath}
            fill="none"
            stroke="url(#lineGradient)"
            strokeWidth="3"
          />

          {/* Peak velocity callout pin */}
          {peakPoint && (
            <g transform={`translate(${scaleX(peakPoint.time_s)}, ${scaleY(peakPoint.max_velocity_mps)})`}>
              <circle r="6" fill="#e94560" stroke="#ffffff" strokeWidth="2" />
              <rect x="-45" y="-26" width="90" height="18" rx="4" fill="#e94560" opacity="0.95" />
              <text x="0" y="-14" fill="#ffffff" fontSize="9" fontWeight="bold" textAnchor="middle">
                PEAK: {peakPoint.max_velocity_mps} m/s
              </text>
            </g>
          )}

          {/* Dynamic Warning arrival callout pin */}
          {warningPoint && (
            <g transform={`translate(${scaleX(warnTimeNum)}, ${scaleY(warningPoint.max_velocity_mps || (currentPeakVel * 0.32))})`}>
              <circle r="6" fill="#f59e0b" stroke="#ffffff" strokeWidth="2" />
              <rect x="-56" y="8" width="112" height="18" rx="4" fill="#b45309" opacity="0.95" />
              <text x="0" y="21" fill="#fef3c7" fontSize="9" fontWeight="bold" textAnchor="middle">
                Warning: {warnTimeNum.toFixed(1)}s (Reni)
              </text>
            </g>
          )}

          {/* Hover interactive data points */}
          {data.map((d, idx) => (
            <circle
              key={`dot-${idx}`}
              cx={scaleX(d.time_s)}
              cy={scaleY(d.max_velocity_mps)}
              r={activePoint && activePoint.time_s === d.time_s ? 5 : 3}
              fill={activePoint && activePoint.time_s === d.time_s ? "#ffffff" : "#e94560"}
              stroke="#ffffff"
              strokeWidth={activePoint && activePoint.time_s === d.time_s ? 2 : 0.5}
              style={{ cursor: "pointer", transition: "r 0.15s ease" }}
              onMouseEnter={() => {
                setHoveredPoint(d);
                if (onSelectTime) onSelectTime(d.time_s);
              }}
            />
          ))}
        </svg>
      </div>

      {/* Interactive Tooltip HUD / Summary Footer */}
      <div style={{ marginTop: "10px", display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "8px", background: "rgba(15, 23, 42, 0.7)", padding: "10px", borderRadius: "6px", fontSize: "0.8rem", border: "1px solid rgba(255,255,255,0.08)" }}>
        <div>
          <span style={{ color: "#94a3b8" }}>Selected Time:</span>{" "}
          <strong style={{ color: "#38bdf8" }}>{activePoint ? `${activePoint.time_s}s` : "Hover points"}</strong>
        </div>
        <div>
          <span style={{ color: "#94a3b8" }}>Max Flow Velocity:</span>{" "}
          <strong style={{ color: "#e94560" }}>{activePoint?.max_velocity_mps ?? 102.37} m/s</strong>
        </div>
        <div>
          <span style={{ color: "#94a3b8" }}>Mean Velocity:</span>{" "}
          <strong style={{ color: "#38bdf8" }}>{activePoint?.mean_velocity_mps ?? 20.8} m/s</strong>
        </div>
        <div>
          <span style={{ color: "#94a3b8" }}>Active Particles:</span>{" "}
          <strong style={{ color: "#10b981" }}>{activePoint?.particle_count?.toLocaleString() ?? "9,450"}</strong>
        </div>
      </div>
    </div>

  );
}

export default HydrographChart;

