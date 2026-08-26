import React from "react";

function DownloadSection({
  currentResult,
  comparison,
  simulationId,
}) {
  const activeSimId = simulationId || currentResult?.simulation_id || "sim_sph_001";

  const handleDownload = (format) => {
    const apiBase = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
    const url = `${apiBase}/api/simulations/${activeSimId}/download/${format.toLowerCase()}`;
    const a = document.createElement("a");
    a.href = url;
    a.download = `${activeSimId}.${format.toLowerCase()}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="download-section">
      <h2>⬇️ GIS & Data Exports</h2>

      <div className="download-buttons">
        <button
          onClick={() => handleDownload("geojson")}
          className="btn-download"
          title="Download GeoJSON (QGIS, WebGIS)"
        >
          <span>📄</span> GeoJSON
        </button>

        <button
          onClick={() => handleDownload("kml")}
          className="btn-download"
          title="Download KML (Google Earth)"
        >
          <span>📂</span> KML (Google Earth)
        </button>

        <button
          onClick={() => handleDownload("shp")}
          className="btn-download"
          title="Download Shapefile Metadata"
        >
          <span>🗺️</span> Shapefile (SHP)
        </button>
      </div>

      <div className="download-info">
        <p>
          Active Dataset: <strong>{activeSimId}</strong> (CRS: EPSG:4326)
        </p>
        <p className="download-note">
          Compatible with QGIS, ArcGIS Pro, Google Earth & Web GIS map engines.
        </p>
      </div>
    </div>
  );
}

export default DownloadSection;