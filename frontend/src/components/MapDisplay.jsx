import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import {
  WaterDepthResult,
  ComparisonResult,
  ModelType,
  ComparisonMetric,
} from "../types";
import { SAMPLE_FLOOD_EXTENT, SAMPLE_WATER_DEPTH, SAMPLE_COMPARISON } from "../data/mockData";

L.Icon.Default.imagePath =
  "https://unpkg.com/leaflet@1.9.4/dist/images";

function MapDisplay({
  floodExtent,
  currentResult,
  comparison,
  isRunning,
}) {
  const mapRef = useRef(null);

  useEffect(() => {
    if (mapRef.current) return;

    const map = L.map(mapRef.current, {
      center: [6.2, 100.5],
      zoom: 9,
      preferCanvas: true,
    });

    // Basemap toggle
    const baseLayer = L.tileLayer(
      "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 19,
        name: "OpenStreetMap",
        alt: "OpenStreetMap basemap",
      }
    ).addTo(map);

    // Satellite basemap option
    const satelliteLayer = L.tileLayer(
      "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
      {
        attribution:
          '&copy; <a href="https://www.opentopomap.org/">OpenTopoMap</a> contributors',
        maxZoom: 17,
        name: "OpenTopoMap",
        alt: "OpenTopoMap satellite basemap",
      }
    );

    // Layer control
    L.control.layers(
      { "OpenStreetMap": baseLayer, "Satellite": satelliteLayer },
      {}
    ).addTo(map);

    // Add flood extent polygon if available
    if (floodExtent && floodExtent.polygon) {
      const polygon = L.polygon(
        floodExtent.polygon.coordinates[0],
        {
          color: "#e94560",
          fillColor: "#ff7878",
          fillOpacity: 0.4,
          weight: 2,
          className: "flood-polygon",
        }
      ).addTo(map);
      map.fitBounds(polygon.getBounds());
    } else if (currentResult) {
      // Show dam location marker
      L.marker([currentResult.location.lat, currentResult.location.lon])
        .addTo(map)
        .bindPopup(
          `<b>Dam Location</b><br/>Water Depth: ${currentResult.water_depth} m`
        )
        .openPopup();
    } else {
      // Default marker - waiting for data
      L.marker([6.2, 100.5])
        .addTo(map)
        .bindPopup(
          "<i>Select a model and run simulation</i>"
        )
        .openPopup();
    }

    // Zoom control
    L.control.zoom({
      position: "bottomright",
    }).addTo(map);

    return () => {
      map?.remove();
    };
  }, [floodExtent, currentResult, comparison, isRunning]);

  // Show comparison info as popup legend
  useEffect(() => {
    if (!comparison) return;

    const updateLegend = () => {
      const existing = document.querySelector(".comparison-legend");
      if (existing) existing.remove();

      const legend = L.control({ position: "bottomright" });
      legend.onAdd = () => {
        const div = L.DomUtil.create("div", "comparison-legend");
        div.innerHTML = `
          <div style="background: rgba(255,255,255,0.9); padding: 8px; border-radius: 4px; font-size: 0.75rem; ">
            <b>SPH vs Delft3D</b><br/>
            <span style="color: #e94560; font-weight: bold;">SPH:</span> ${comparison.sph_data?.water_depth ?? "N/A"} m<br/>
            <span style="color: #4ecdc4; font-weight: bold;">Delft3D:</span> ${comparison.delft3d_data?.water_depth ?? "N/A"} m<br/>
            <span style="color: #ffd27f; font-weight: bold;">Difference:</span> {
              (comparison.delft3d_data?.water_depth ?? 0) -
              (comparison.sph_data?.water_depth ?? 0)
            }.toFixed(3)} m
          </div>
        `;
        return div;
      };
      legend.addTo(map);
      // Cleanup on unmount
      return () => {
        map?.removeControl(legend);
      };
    };

    updateLegend();
    const resizeHandler = () => {
      map?.invalidateSize();
    };
    window.addEventListener("resize", resizeHandler);
    return () => {
      window.removeEventListener("resize", resizeHandler);
    };
  }, [comparison]);

  return (
    <div className="flood-map-area">
      <h2>🗺️ Flood Inundation Map</h2>

      {isRunning && (
        <p className="status-running">
          <span>▶</span> Simulation running - map updating in real time
        </p>
      )}

      {!(isRunning || floodExtent || currentResult) && (
        <p className="status-empty">
          <i>Select a model and click "Run Simulation" to display flood extent</i>
        </p>
      )}

      <div className="map-canvas" ref={mapRef} />
    </div>
  );
}

export default MapDisplay;