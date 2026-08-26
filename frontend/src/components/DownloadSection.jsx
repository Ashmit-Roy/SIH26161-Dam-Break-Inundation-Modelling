import React from "react";
import { WaterDepthResult, ComparisonResult, DashboardState } from "../types";
import { SAMPLE_WATER_DEPTH, SAMPLE_FLOOD_EXTENT, SAMPLE_COMPARISON } from "../data/mockData";

function DownloadSection({
  currentResult,
  comparison,
  simulationId,
}) {
  const handleDownload = (format) => {
    if (!simulationId) {
      alert("No simulation results to download. Run a simulation first.");
      return;
    }
    alert(
      `Download in ${format} format for ${simulationId} - ` +
        `Real export will connect to simulation outputs when available.`
    );
  };

  return (
    <div className="download-section">
      <h2>⬇️ Download Results</h2>

      <div className="download-buttons">
        <button
          onClick={() => handleDownload("GeoJSON")}
          className="btn-download"
          title="Download GeoJSON"
          disabled={!simulationId}
        >
          <span>📄</span> GeoJSON
        </button>

        <button
          onClick={() => handleDownload("SHP")}
          className="btn-download"
          title="Download Shapefile"
          disabled={!simulationId}
        >
          <span>🗺️</span> SHP
        </button>

        <button
          onClick={() => handleDownload("KML")}
          className="btn-download"
          title="Download KML"
          disabled={!simulationId}
        >
          <span>📂</span> KML
        </button>
      </div>

      <div className="download-info">
        <p>
          {simulationId ? (
            `Results for simulation <strong>{simulationId}</strong>`
          ) : (
            "No active simulation - use mock data for preview"
          )}
        </p>
        <p className="download-note">
          Formats: GeoJSON (compatible with QGIS, ArcGIS, QGIS) ·
          SHP (ESRI Shapefile) · KML (Google Earth, Google Maps) ·
          All outputs reference EPSG:4326 coordinate system
        </p>
      </div>
    </div>
  );
}

export default DownloadSection;