# GIS Workflow & Hydrodynamic Inundation Modelling

This document describes the complete GIS and hydrodynamic dam-break inundation modelling workflow for the **SIH26161 Dam Break Inundation Modelling** project.

---

## 1. Study Area & Project Domain

- **Geographical Region:** Rishi Ganga & Dhauliganga River Basin, Chamoli District, Uttarakhand, India.
- **Hydrological Focus:** Glacial lake outburst / rock-ice avalanche triggered dam breach and flash flood (Chamoli disaster corridor).
- **Key Hydraulic Structures:**
  - **Rishi Ganga Small Hydroelectric Project:** Upstream run-of-river dam ($30.4850^\circ\text{ N}, 79.6880^\circ\text{ E}$, 2050 m ASL).
  - **Tapovan Vishnugad Hydroelectric Project (NTPC):** Downstream barrage with intake & desilting tunnels ($30.4950^\circ\text{ N}, 79.6210^\circ\text{ E}$, 1803 m ASL).
- **Downstream River Reach:** 27.8 km corridor traversing Raini Village confluence, Tapovan, Dhak, and terminating at the Alaknanda confluence near Joshimath / Helang.

---

## 2. Coordinate Reference Systems (CRS)

| Scope | Coordinate Reference System | EPSG Code | Units | Rationale |
|---|---|---|---|---|
| **Computation / GIS Simulation** | WGS 84 / UTM Zone 44N | `EPSG:32644` | Metres (`m`) | Preserves accurate distances, channel widths, slopes, and volumes for hydraulic calculations in Uttarakhand. |
| **Web Dashboard / APIs / Leaflet** | WGS 84 (Geographic) | `EPSG:4326` | Decimal Degrees | Universal standard for RFC 7946 GeoJSON, vector tile layers, and frontend map components. |

---

## 3. Workflow Pipeline

```text
1. Vector Layers Generation
   ├── Dam Locations (GeoJSON / GPKG)
   ├── River Centerline (GeoJSON / GPKG)
   ├── Critical Infrastructure & Habitations (GeoJSON / GPKG)
   └── Catchment Boundary (GeoJSON / GPKG)
           ↓
2. DEM Acquisition & Terrain Conditioning
   ├── 30m Digital Elevation Model (GeoTIFF)
   └── Preprocessing: Slope, Hillshade, Flow Direction & Accumulation
           ↓
3. Hydrodynamic Dam-Break Inundation Simulation
   ├── Breach Hydrograph (Peak Q = 14,500 m³/s, Vol = 6.2M m³)
   ├── 2D Hydraulic Wave Propagation & Channel Routing
   └── Peak Water Depth, Flow Velocity, and Arrival Time Computation
           ↓
4. Flood Hazard & Impact Classification
   ├── DEFRA Flood Hazard Rating (Low, Moderate, Significant, Extreme)
   └── Infrastructure Inundation / Critical Asset Exposure
           ↓
5. Web-Ready Output Exports & QGIS Packaging
   ├── GeoJSON, GeoPackage, Shapefile
   ├── GeoTIFF Rasters (Depth, Velocity, Hazard, Hillshade)
   └── Packaged QGIS Project (`qgis/dam_break.qgz`)
```

---

## 4. Hydrodynamic Simulation Methodology & Equations

The simulation engine implements 2D overland and channel hydrodynamic routing over the terrain DEM:

1. **Breach Outflow Hydrograph:**
   Triangular breach hydrograph calibrated to the peak discharge of $Q_p = 14,500\text{ m}^3/\text{s}$ over a 60-minute time base releasing $6.2 \times 10^6\text{ m}^3$ of water and debris.
2. **Channel Hydraulics (Manning's Equation):**
   $$V = \frac{1}{n} R_h^{2/3} S_0^{1/2}$$
   where:
   - $n = 0.045$ (Manning's roughness for steep, rocky mountain torrents).
   - $S_0$ is the local hydraulic gradient derived from the DEM.
   - $R_h \approx h$ (hydraulic radius for wide channels).
3. **Flood Wave Celerity & Arrival Time:**
   $$c = V + \sqrt{g \cdot h}$$
   $$T_{\text{arr}}(s) = \int_0^s \frac{1}{c(u)} du$$
4. **DEFRA Flood Hazard Rating (HR):**
   $$\text{HR} = d \times (v + 0.5) + \text{DF}$$
   - $d$: Water depth ($\text{m}$).
   - $v$: Flow velocity ($\text{m/s}$).
   - $\text{DF} = 0.5$ (Debris Factor for high-sediment flash floods).
   - **Hazard Categories:**
     - $\text{HR} < 0.75$: Low Hazard (Caution)
     - $0.75 \le \text{HR} < 1.25$: Moderate Hazard (Dangerous for vulnerable persons)
     - $1.25 \le \text{HR} < 2.0$: Significant Hazard (Dangerous for most people)
     - $\text{HR} \ge 2.0$: Extreme Hazard (High fatality risk, structural destruction)

---

## 5. Output Inventory

All generated artifacts are organized in `outputs/`:

| File | Type | CRS | Description |
|---|---|---|---|
| `outputs/flood_extent.geojson` | Vector | `EPSG:4326` | Inundation footprint polygon for web dashboards. |
| `outputs/hazard_zones.geojson` | Vector | `EPSG:4326` | Categorized flood hazard zones (1 to 4). |
| `outputs/dam_locations.geojson` | Vector | `EPSG:4326` | Dam points with metadata (crest height, capacity). |
| `outputs/river_reach.geojson` | Vector | `EPSG:4326` | Centerline of the 27.8 km river reach. |
| `outputs/critical_infrastructure.geojson` | Vector | `EPSG:4326` | Bridges, tunnels, powerhouses, settlements. |
| `outputs/study_area_boundary.geojson` | Vector | `EPSG:4326` | Watershed study area polygon. |
| `outputs/flood_depth.tif` | Raster | `EPSG:32644` | Peak flood depth raster ($30\text{m}$ resolution). |
| `outputs/flow_velocity.tif` | Raster | `EPSG:32644` | Peak flow velocity raster ($\text{m/s}$). |
| `outputs/hazard_index.tif` | Raster | `EPSG:32644` | Continuous Flood Hazard Rating (HR) raster. |
| `outputs/arrival_time.tif` | Raster | `EPSG:32644` | Wave arrival time in minutes. |
| `outputs/terrain_hillshade.tif` | Raster | `EPSG:32644` | Multi-directional terrain shaded relief. |
| `outputs/metadata.json` | JSON | N/A | Summary metrics, impacted assets, and schema. |

---

## 6. How to Reproduce the Workflow

### Running the Python Pipeline
From the repository root:
```powershell
python src/gis/export_web_outputs.py
python src/gis/build_qgis_project.py
```

### Running Automated GIS Tests
```powershell
pytest tests/gis/test_gis.py -v
```

### Opening the Project in QGIS
1. Launch **QGIS** (version 3.28 or later).
2. Open `qgis/dam_break.qgz` (or `qgis/dam_break.qgs`).
3. The project will open with the full organized layer tree, symbology, transparencies, and color ramps.
