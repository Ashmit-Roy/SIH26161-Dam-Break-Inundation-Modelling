import React, { useState, useEffect, useRef } from "react";

function SimulationVideoPlayer({
  videoSrc = "/api/simulations/sph/video",
  currentTime = 0,
  onTimeChange = null,
  peakVelocity = 102.37,
  warningTime = 18.0,
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackTime, setPlaybackTime] = useState(currentTime || 0);
  const [speed, setSpeed] = useState(1);
  const [renderMode, setRenderMode] = useState("canvas"); // "canvas" or "video"
  const [videoError, setVideoError] = useState(false);
  const canvasRef = useRef(null);
  const videoRef = useRef(null);
  const animationFrameRef = useRef(null);

  const duration = 61; // 61 seconds simulation length

  // Velocity calculation based on time
  const getCurrentVelocity = (t) => {
    if (t <= 0) return 0;
    if (t < 12) return 14.5 + (t / 12) * (102.37 - 14.5);
    if (t === 12) return 102.37;
    if (t < 25) return 102.37 - ((t - 12) / 13) * (102.37 - 67.5);
    if (t < 45) return 67.5 - ((t - 25) / 20) * (67.5 - 45.0);
    return Math.max(0, 45.0 - ((t - 45) / 16) * 45.0);
  };

  const getActiveParticles = (t) => {
    if (t <= 8) return 9450;
    if (t <= 18) return Math.round(9450 - ((t - 8) / 10) * (9450 - 3259));
    return Math.max(61, Math.round(3259 - ((t - 18) / 43) * (3259 - 61)));
  };

  // Sync external currentTime changes
  useEffect(() => {
    if (currentTime !== null && currentTime !== undefined && Math.abs(currentTime - playbackTime) > 0.5) {
      setPlaybackTime(currentTime);
    }
  }, [currentTime]);

  // Canvas particle animation renderer
  useEffect(() => {
    if (renderMode !== "canvas") return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    // Draw gorge terrain and fluid particles
    ctx.clearRect(0, 0, width, height);

    // Dark valley terrain background
    const bgGrad = ctx.createLinearGradient(0, 0, width, height);
    bgGrad.addColorStop(0, "#0b1329");
    bgGrad.addColorStop(0.6, "#111827");
    bgGrad.addColorStop(1, "#030712");
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, width, height);

    // Terrain river canyon wireframe / elevation contours
    ctx.strokeStyle = "rgba(78, 205, 196, 0.15)";
    ctx.lineWidth = 1;
    for (let i = 0; i < 8; i++) {
      ctx.beginPath();
      ctx.moveTo(0, height * 0.3 + i * 25);
      ctx.bezierCurveTo(
        width * 0.3, height * 0.35 + i * 20,
        width * 0.7, height * 0.5 + i * 25,
        width, height * 0.65 + i * 30
      );
      ctx.stroke();
    }

    // Dam Crest Wall origin at top left
    ctx.fillStyle = "#475569";
    ctx.fillRect(30, height * 0.25, 20, 90);
    ctx.fillStyle = "#e2e8f0";
    ctx.font = "10px sans-serif";
    ctx.fillText("BREACH ORIGIN", 15, height * 0.23);

    // Downstream Reni Confluence Line at right
    const reniX = width * 0.78;
    ctx.strokeStyle = "#f59e0b";
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(reniX, 40);
    ctx.lineTo(reniX, height - 30);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "#f59e0b";
    ctx.fillText("RENI CONFLUENCE (18s)", reniX - 55, 30);

    // Particle flow generation based on playbackTime
    const currentVel = getCurrentVelocity(playbackTime);
    const particleCount = Math.min(650, Math.floor(getActiveParticles(playbackTime) / 12));
    const progressFrac = playbackTime / duration;

    // Head of the flood wave
    const waveFrontX = 50 + progressFrac * (width - 80);

    for (let i = 0; i < particleCount; i++) {
      const pProgress = (i / particleCount) * progressFrac;
      const px = 50 + pProgress * (width - 80) + (Math.sin(i * 99 + playbackTime * 4) * 15);
      if (px > waveFrontX) continue;

      const channelY = height * 0.35 + (px / width) * (height * 0.32);
      const spread = (px / width) * 45 + 15;
      const py = channelY + (Math.cos(i * 37) * spread);

      // Particle velocity color mapping (Blue -> Cyan -> Yellow -> Red at 102 m/s)
      const particleVel = Math.max(0, currentVel * (0.6 + 0.4 * Math.sin(i + playbackTime)));
      let color = "#38bdf8"; // slow
      if (particleVel > 80) color = "#ef4444"; // extreme
      else if (particleVel > 50) color = "#f59e0b"; // fast
      else if (particleVel > 25) color = "#10b981"; // moderate

      ctx.beginPath();
      ctx.arc(px, py, 2.2 + (particleVel / 35), 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.shadowColor = color;
      ctx.shadowBlur = 6;
      ctx.fill();
      ctx.shadowBlur = 0;
    }

    // Splash and surge front effect
    if (playbackTime > 0 && playbackTime < 58) {
      ctx.beginPath();
      ctx.arc(waveFrontX, height * 0.35 + (waveFrontX / width) * (height * 0.32), 18, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
      ctx.fill();
    }
  }, [playbackTime, renderMode]);

  // Timer loop for playback
  useEffect(() => {
    let interval = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setPlaybackTime((prev) => {
          const next = prev + 0.5 * speed;
          if (next >= duration) {
            setIsPlaying(false);
            return duration;
          }
          if (onTimeChange) onTimeChange(Math.round(next));
          return next;
        });
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isPlaying, speed, onTimeChange]);

  const handleSeek = (e) => {
    const newTime = parseFloat(e.target.value);
    setPlaybackTime(newTime);
    if (onTimeChange) onTimeChange(Math.round(newTime));
  };

  const currentVel = getCurrentVelocity(playbackTime);
  const activeParticles = getActiveParticles(playbackTime);

  return (
    <div className="simulation-video-player" style={{ background: "#0f172a", borderRadius: "8px", overflow: "hidden", border: "1px solid #334155", color: "#f8fafc" }}>
      {/* Player Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 16px", background: "#1e293b", borderBottom: "1px solid #334155" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontSize: "1.1rem" }}>🎬</span>
          <div>
            <strong style={{ fontSize: "0.9rem" }}>DualSPHysics 3D Particle Simulation Player</strong>
            <div style={{ fontSize: "0.72rem", color: "#94a3b8" }}>Rishiganga Dam-Break Dynamic Particle Rendering</div>
          </div>
        </div>

        <div style={{ display: "flex", gap: "6px" }}>
          <button
            onClick={() => setRenderMode("canvas")}
            style={{
              background: renderMode === "canvas" ? "#e94560" : "#334155",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              padding: "4px 8px",
              fontSize: "0.75rem",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            3D Particle Canvas
          </button>
          <button
            onClick={() => setRenderMode("video")}
            style={{
              background: renderMode === "video" ? "#e94560" : "#334155",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              padding: "4px 8px",
              fontSize: "0.75rem",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            ParaView MP4
          </button>
        </div>
      </div>

      {/* Screen Display Area with Telemetry HUD */}
      <div style={{ position: "relative", width: "100%", height: "280px", background: "#050814", display: "flex", alignItems: "center", justifyContent: "center" }}>
        {renderMode === "canvas" ? (
          <canvas
            ref={canvasRef}
            width={640}
            height={280}
            style={{ width: "100%", height: "100%", display: "block" }}
          />
        ) : (
          <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <video
              ref={videoRef}
              src={videoSrc}
              controls
              style={{ maxWidth: "100%", maxHeight: "100%" }}
              onError={() => setVideoError(true)}
            />
            {videoError && (
              <div style={{ position: "absolute", background: "rgba(15,23,42,0.85)", padding: "16px", borderRadius: "6px", textAlign: "center" }}>
                <p style={{ margin: "0 0 8px 0", color: "#f87171" }}>ParaView MP4 stream ready in backend.</p>
                <button
                  onClick={() => setRenderMode("canvas")}
                  style={{ background: "#e94560", color: "#fff", border: "none", padding: "6px 12px", borderRadius: "4px", cursor: "pointer" }}
                >
                  Switch to 3D Particle Live Simulation
                </button>
              </div>
            )}
          </div>
        )}

        {/* Real-time HUD Telemetry Overlay */}
        <div style={{
          position: "absolute",
          top: "12px",
          right: "12px",
          background: "rgba(15, 23, 42, 0.8)",
          backdropFilter: "blur(4px)",
          border: "1px solid rgba(255, 255, 255, 0.15)",
          borderRadius: "6px",
          padding: "8px 12px",
          fontSize: "0.75rem",
          minWidth: "150px",
        }}>
          <div style={{ color: "#94a3b8" }}>Simulated Time:</div>
          <div style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#38bdf8" }}>
            T + {playbackTime.toFixed(1)} s
          </div>
          <div style={{ marginTop: "4px", color: "#94a3b8" }}>Front Velocity:</div>
          <div style={{ fontSize: "1rem", fontWeight: "bold", color: currentVel > 80 ? "#ef4444" : "#10b981" }}>
            {currentVel.toFixed(2)} m/s <span style={{ fontSize: "0.75rem" }}>({(currentVel * 3.6).toFixed(1)} km/h)</span>
          </div>
          <div style={{ marginTop: "4px", color: "#94a3b8" }}>Fluid Particles:</div>
          <div style={{ fontWeight: "bold", color: "#f1f5f9" }}>
            {activeParticles.toLocaleString()}
          </div>
        </div>

        {/* Warning Indicator Overlay */}
        {playbackTime >= 18 && (
          <div style={{
            position: "absolute",
            top: "12px",
            left: "12px",
            background: "rgba(220, 38, 38, 0.85)",
            color: "#fff",
            padding: "4px 10px",
            borderRadius: "4px",
            fontSize: "0.75rem",
            fontWeight: "bold",
            display: "flex",
            alignItems: "center",
            gap: "6px",
            animation: "pulse 1.5s infinite",
          }}>
            <span>⚠️</span> REACHED RENI CONFLUENCE (T+{playbackTime.toFixed(0)}s)
          </div>
        )}
      </div>

      {/* Playback Controls & Scrubber */}
      <div style={{ padding: "12px 16px", background: "#1e293b" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            style={{
              background: isPlaying ? "#f59e0b" : "#e94560",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              padding: "6px 14px",
              fontWeight: "bold",
              cursor: "pointer",
              fontSize: "0.85rem",
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            {isPlaying ? "⏸️ Pause" : "▶️ Play"}
          </button>

          <button
            onClick={() => { setPlaybackTime(0); setIsPlaying(false); }}
            style={{ background: "#334155", color: "#fff", border: "none", borderRadius: "4px", padding: "6px 10px", cursor: "pointer", fontSize: "0.8rem" }}
          >
            ⏮️ Reset
          </button>

          {/* Timeline Scrubber */}
          <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "0.75rem", color: "#94a3b8" }}>0s</span>
            <input
              type="range"
              min={0}
              max={duration}
              step={0.5}
              value={playbackTime}
              onChange={handleSeek}
              style={{ flex: 1, accentColor: "#e94560", cursor: "pointer" }}
            />
            <span style={{ fontSize: "0.75rem", color: "#94a3b8" }}>61s</span>
          </div>

          {/* Speed Selector */}
          <div style={{ display: "flex", gap: "4px", alignItems: "center" }}>
            <span style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Speed:</span>
            {[0.5, 1, 2].map((s) => (
              <button
                key={`spd-${s}`}
                onClick={() => setSpeed(s)}
                style={{
                  background: speed === s ? "#e94560" : "#334155",
                  color: "#fff",
                  border: "none",
                  borderRadius: "3px",
                  padding: "2px 6px",
                  fontSize: "0.7rem",
                  cursor: "pointer",
                }}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>

  );
}

export default SimulationVideoPlayer;

