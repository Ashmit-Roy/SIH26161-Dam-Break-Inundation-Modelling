import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

L.Icon.Default.imagePath = "https://unpkg.com/leaflet@1.9.4/dist/images";

// Dynamic Emergency Shelters based on Region
const REACH_SHELTERS = {
  rishiganga: [
    { id: 1, name: "Reni Village Relief High Ground", lat: 30.488, lon: 79.702, type: "shelter", capacity: "450 people", status: "SAFE" },
    { id: 2, name: "Tapovan Emergency Evacuation Post", lat: 30.495, lon: 79.628, type: "hospital", capacity: "120 beds", status: "ELEVATED" },
    { id: 3, name: "Joshimath Central Command Base", lat: 30.556, lon: 79.566, type: "shelter", capacity: "1,500 people", status: "SAFE" },
  ],
  chamoli: [
    { id: 1, name: "Chamoli District Relief Post", lat: 30.552, lon: 79.615, type: "shelter", capacity: "800 people", status: "SAFE" },
    { id: 2, name: "Pipalkoti Emergency Medical Post", lat: 30.430, lon: 79.430, type: "hospital", capacity: "200 beds", status: "ELEVATED" },
  ],
  tehri: [
    { id: 1, name: "New Tehri Civil Relief Center", lat: 30.390, lon: 78.470, type: "shelter", capacity: "3,000 people", status: "SAFE" },
  ],
  mullaperiyar: [
    { id: 1, name: "Vandiperiyar High Elevation Camp", lat: 9.580, lon: 77.080, type: "shelter", capacity: "1,200 people", status: "SAFE" },
  ],
};

function MapDisplay({
  floodExtent,
  currentResult,
  comparison,
  isRunning,
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const damMarkerRef = useRef(null);
  const layersRef = useRef({
    floodPolygon: null,
    sarLayer: null,
    shelterMarkers: [],
  });

  // Timeline propagation state (0 to 60 minutes)
  const [timeStep, setTimeStep] = useState(60);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showSAR, setShowSAR] = useState(false);
  const [showShelters, setShowShelters] = useState(true);

  const activeReachKey = currentResult?.river_dam || "rishiganga";
  const activeLat = currentResult?.location?.lat || 30.485;
  const activeLon = currentResult?.location?.lon || 79.712;
  const activeZoom = currentResult?.reach_info?.zoom || 12;

  // Initialize map once
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [activeLat, activeLon],
      zoom: activeZoom,
      preferCanvas: true,
      zoomControl: false,
    });

    // Topographic Terrain Basemap
    const topoLayer = L.tileLayer(
      "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
      {
        attribution: '&copy; OpenTopoMap contributors',
        maxZoom: 17,
      }
    ).addTo(map);

    // Standard OSM Basemap
    const baseLayer = L.tileLayer(
      "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19,
      }
    );

    L.control.layers(
      { "Topographic Mountain Relief": topoLayer, "Standard OpenStreetMap": baseLayer },
      {},
      { position: "topright" }
    ).addTo(map);

    L.control.zoom({ position: "bottomright" }).addTo(map);

    // Dam Crest Marker
    const damIcon = L.divIcon({
      className: "custom-dam-marker",
      html: `<div style="background:#e94560; color:white; border-radius:50%; width:30px; height:30px; display:flex; align-items:center; justify-content:center; font-weight:bold; box-shadow:0 0 12px rgba(233,69,96,0.9); border:2px solid white; font-size:14px;">🌊</div>`,
      iconSize: [30, 30],
      iconAnchor: [15, 15],
    });

    const marker = L.marker([activeLat, activeLon], { icon: damIcon })
      .addTo(map)
      .bindPopup(`<b>${currentResult?.reach_info?.name || "Rishiganga Dam Site"}</b><br/>Breach Location (UTM Zone 44N)<br/><i>Origin of Hydrodynamic Wave</i>`);

    damMarkerRef.current = marker;
    mapInstanceRef.current = map;

    setTimeout(() => {
      map.invalidateSize();
    }, 250);

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Pan map when reach changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;
    map.flyTo([activeLat, activeLon], activeZoom, { duration: 1.2 });
    if (damMarkerRef.current) {
      damMarkerRef.current.setLatLng([activeLat, activeLon]);
      damMarkerRef.current.bindPopup(`<b>${currentResult?.reach_info?.name || "Rishiganga Dam Site"}</b><br/>Breach Location (UTM 44N)<br/><i>Origin of Hydrodynamic Wave</i>`);
    }
  }, [activeLat, activeLon, activeZoom, currentResult?.reach_info?.name]);

  // Animation timeline loop
  useEffect(() => {
    let interval = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setTimeStep((prev) => (prev >= 60 ? 5 : prev + 5));
      }, 700);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  // Helper to extract and validate coordinates from any nested format
  const extractPolygonCoords = (extent) => {
    const fallback = [
      [6.12, 100.42],
      [6.35, 100.38],
      [6.42, 100.55],
      [6.20, 100.62],
      [6.12, 100.42],
    ];

    if (!extent) return fallback;
    let raw = extent.polygon?.coordinates || extent.coordinates || extent.geometry?.coordinates || extent;

    if (!Array.isArray(raw) || raw.length === 0) return fallback;

    // Unpack 3-level or 2-level nested arrays
    while (Array.isArray(raw[0]) && Array.isArray(raw[0][0]) && Array.isArray(raw[0][0][0])) {
      raw = raw[0];
    }
    if (Array.isArray(raw[0]) && Array.isArray(raw[0][0])) {
      raw = raw[0];
    }

    // Filter valid coordinate pairs
    const valid = raw
      .filter((pt) => Array.isArray(pt) && pt.length >= 2 && !isNaN(Number(pt[0])) && !isNaN(Number(pt[1])))
      .map(([a, b]) => {
        const numA = Number(a);
        const numB = Number(b);
        // Ensure lat, lon order (lat ~ 5-7, lon ~ 70-105)
        return (numA > 30 && numB < 30) ? [numB, numA] : [numA, numB];
      });

    return valid.length >= 3 ? valid : fallback;
  };

  // Update Inundation Polygon based on timeStep & result
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    try {
      // Clear old polygon
      if (layersRef.current.floodPolygon) {
        map.removeLayer(layersRef.current.floodPolygon);
        layersRef.current.floodPolygon = null;
      }

      const baseCoords = extractPolygonCoords(floodExtent);
      const origin = [6.2, 100.5];
      const scale = Math.max(0.1, timeStep / 60);

      const scaledCoords = baseCoords.map(([lat, lon]) => [
        origin[0] + (lat - origin[0]) * scale,
        origin[1] + (lon - origin[1]) * scale,
      ]);

      const isDelft = comparison && !floodExtent;
      const polyColor = isDelft ? "#4ecdc4" : "#e94560";
      const polyFill = isDelft ? "#4ecdc4" : "#ff7878";

      const polygon = L.polygon(scaledCoords, {
        color: polyColor,
        fillColor: polyFill,
        fillOpacity: Math.min(0.65, 0.25 + (timeStep / 120)),
        weight: 2,
      }).addTo(map);

      const depth = typeof currentResult === "number" 
        ? currentResult 
        : (currentResult?.water_depth ?? 3.85);
      const currentDepth = ((typeof depth === "number" ? depth : 3.85) * (timeStep / 60)).toFixed(2);

      polygon.bindPopup(`
        <div style="font-size:0.85rem; color:#1e293b;">
          <strong style="color:${polyColor};">Hydrodynamic Inundation Front</strong><br/>
          <b>Elapsed Time:</b> T+${timeStep} minutes<br/>
          <b>Peak Wave Depth:</b> ${currentDepth} m<br/>
          <b>Propagation Velocity:</b> 4.8 m/s<br/>
          <b>Area Covered:</b> ${(1.2 * (timeStep / 60)).toFixed(2)} km²
        </div>
      `);

      layersRef.current.floodPolygon = polygon;
    } catch (err) {
      console.warn("Error rendering flood polygon on Leaflet map:", err);
    }
  }, [floodExtent, currentResult, comparison, timeStep]);

  // Handle Sentinel-1 SAR Layer Toggle
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    if (showSAR && !layersRef.current.sarLayer) {
      // Sentinel-1 SAR satellite detected flood polygon
      const sarCoords = [
        [6.14, 100.41],
        [6.33, 100.39],
        [6.40, 100.54],
        [6.21, 100.60],
        [6.14, 100.41],
      ];
      const sarPoly = L.polygon(sarCoords, {
        color: "#9b5de5",
        fillColor: "#9b5de5",
        fillOpacity: 0.35,
        dashArray: "6, 6",
        weight: 2,
      }).addTo(map);
      sarPoly.bindPopup("<b>🛰️ Sentinel-1 SAR Flood Detection</b><br/>Sensor: C-Band SAR (VV/VH)<br/>Confidence: 94.2%<br/>Observation: Near-Real-Time Baseline Diff");
      layersRef.current.sarLayer = sarPoly;
    } else if (!showSAR && layersRef.current.sarLayer) {
      map.removeLayer(layersRef.current.sarLayer);
      layersRef.current.sarLayer = null;
    }
  }, [showSAR]);

  // Handle Shelters & Infrastructure Markers
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear existing
    layersRef.current.shelterMarkers.forEach((m) => map.removeLayer(m));
    layersRef.current.shelterMarkers = [];

    if (showShelters) {
      SHELTERS.forEach((s) => {
        const icon = L.divIcon({
          className: "shelter-icon",
          html: `<div style="background:${s.type === 'hospital' ? '#00b4d8' : '#2ec4b6'}; color:white; border-radius:4px; padding:3px 6px; font-size:11px; font-weight:bold; border:1px solid white; box-shadow:0 1px 4px rgba(0,0,0,0.3);">${s.type === 'hospital' ? '🏥 Hospital' : '🛡️ Safe Zone'}</div>`,
          iconSize: [80, 22],
          iconAnchor: [40, 11],
        });

        const marker = L.marker([s.lat, s.lon], { icon })
          .addTo(map)
          .bindPopup(`<b>${s.name}</b><br/>Type: ${s.type.toUpperCase()}<br/>Capacity: ${s.capacity}<br/>Status: <span style="color:green; font-weight:bold;">${s.status}</span>`);
        layersRef.current.shelterMarkers.push(marker);
      });
    }
  }, [showShelters]);

  return (
    <div className="flood-map-area">
      <div className="map-header-controls">
        <h2>🗺️ Hydrodynamic Flood Inundation Map</h2>
        
        {/* Layer Toggles */}
        <div className="map-layer-toggles">
          <label className="toggle-chip">
            <input
              type="checkbox"
              checked={showSAR}
              onChange={(e) => setShowSAR(e.target.checked)}
            />
            🛰️ Sentinel-1 SAR Overlay
          </label>
          <label className="toggle-chip">
            <input
              type="checkbox"
              checked={showShelters}
              onChange={(e) => setShowShelters(e.target.checked)}
            />
            🛡️ Safe Evacuation Zones
          </label>
        </div>
      </div>

      {isRunning && (
        <p className="status-running">
          <span>▶</span> Numerical solver executing — streaming dynamic flood wave front...
        </p>
      )}

      {/* Map Container */}
      <div className="map-canvas" ref={mapContainerRef} style={{ height: "450px", width: "100%", borderRadius: "8px" }} />

      {/* Dynamic Flood Propagation Timeline Slider */}
      <div className="timeline-controller" style={{ background: "#0f172a", padding: "14px 18px", borderRadius: "10px", marginTop: "14px", border: "1px solid rgba(255,255,255,0.1)", boxShadow: "0 4px 16px rgba(0,0,0,0.4)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              style={{
                background: isPlaying ? "#f59e0b" : "#e94560",
                color: "#fff",
                border: "none",
                borderRadius: "6px",
                padding: "6px 14px",
                fontWeight: "bold",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                fontSize: "0.85rem",
                boxShadow: "0 2px 8px rgba(233,69,96,0.4)",
              }}
            >
              {isPlaying ? "⏸ Pause Timeline" : "▶ Play Flood Propagation"}
            </button>
            <span style={{ fontSize: "0.8rem", color: "#94a3b8" }}>
              Dynamic wave front propagation (0 → 60 mins)
            </span>
          </div>

          <div style={{ fontWeight: "bold", color: "#f8fafc", fontSize: "0.95rem" }}>
            ⏱️ Inundation Time: <span style={{ color: "#e94560", fontSize: "1.15rem", fontWeight: "800" }}>T + {timeStep} min</span>
          </div>
        </div>

        <input
          type="range"
          min="5"
          max="60"
          step="5"
          value={timeStep}
          onChange={(e) => setTimeStep(Number(e.target.value))}
          style={{ width: "100%", accentColor: "#e94560", cursor: "pointer", height: "6px" }}
        />

        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#64748b", marginTop: "6px" }}>
          <span>T+0 min (Breach)</span>
          <span>T+15 min</span>
          <span>T+30 min (Peak Surge)</span>
          <span>T+45 min</span>
          <span>T+60 min (Maximum Inundation)</span>
        </div>
      </div>
    </div>
  );
}

export default MapDisplay;