import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import {
  FloodExtentResult,
  WaterDepthResult,
  ComparisonResult,
  ModelType,
  ComparisonMetric,
} from "../types";
import { SAMPLE_FLOOD_EXTENT, SAMPLE_WATER_DEPTH, SAMPLE_COMPARISON } from "../data/mockData";

L.Icon.Default.imagePath =
  "https://unpkg.com/leaflet@1.9.4/dist/images";

/** @typedef {Object} FloodMapProps */
/** @typedef {import("../types").FloodExtentResult} FloodExtentResult */
/** @typedef {import("../types").WaterDepthResult} WaterDepthResult */
/** @typedef {import("../types").ComparisonResult} ComparisonResult */

/**
 * @param {FloodMapProps} props
 * @param {FloodExtentResult|null} props.floodExtent
 * @param {WaterDepthResult|null} props.currentResult
 * @param {ComparisonResult|null} props.comparison
 * @param {boolean} props.isRunning
 * @param {typeof ModelType} props.ModelType
 */
function FloodMap(
  /** @param {FloodExtentResult|null} floodExtent */
  floodExtent,
  /** @param {WaterDepthResult|null} currentResult */
  currentResult,
  /** @param {ComparisonResult|null} comparison */
  comparison,
  /** @param {boolean} isRunning */
  isRunning,
  /** @param {typeof ModelType} ModelType */
  ModelType
) {
  const mapRef = useRef(null);

  useEffect(() => {
    if (mapRef.current) return;

    const map = L.map(mapRef.current, {
      center: [6.2, 100.5],
      zoom: 9,
      preferCanvas: true,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    // Add flood extent polygon if available
    if (floodExtent && floodExtent.polygon) {
      const polygon = L.polygon(
        floodExtent.polygon.coordinates[0],
        {
          color: "#e94560",
          fillColor: "#ff7878",
          fillOpacity: 0.4,
          weight: 2,
        }
      ).addTo(map);
      map.fitBounds(polygon.getBounds());
    } else if (currentResult) {
      // Fallback: show dam location as marker
      L.marker([currentResult.location.lat, currentResult.location.lon])
        .addTo(map)
        .bindPopup(
          `<b>Dam Location</b><br/>Water Depth: ${currentResult.water_depth} m`
        )
        .openPopup();
    } else {
      // Default view - no data yet
      L.marker([6.2, 100.5])
        .addTo(map)
        .bindPopup("<i>Select a model and run simulation</i>")
        .openPopup();
    }

    return () => {
      map?.remove();
    };
  }, [floodExtent, currentResult, isRunning]);

  // Show comparison info
  useEffect(() => {
    if (!comparison) return;

    const damLoc = { lat: 6.2, lon: 100.5 };
    const sphMarker = L.marker([damLoc.lat, damLoc.lon])
      .bindPopup(
        `<b>SPH</b><br/>Depth: ${comparison.sph_data?.water_depth} m`
      );
    const delftMarker = L.marker([
      damLoc.lat + 0.01,
      damLoc.lon,
    ])
      .bindPopup(
        `<b>Delft3D</b><br/>Depth: ${comparison.delft3d_data?.water_depth} m`
      );

    // These are just created for display; map already has markers from above
    return () => {
      // cleanup
    };
  }, [comparison]);

  return (
    <div className="flood-map-card">
      <h2>Flood Inundation Map</h2>
      {isRunning && (
        <p><i>Simulation running - map updating...</i></p>
      )}
      {!(isRunning || floodExtent || currentResult) && (
        <p><i>Select a model and click "Run Simulation" to display flood extent</i></p>
      )}
      <div ref={mapRef} className="map-container" />
    </div>
  );
}

export default FloodMap;