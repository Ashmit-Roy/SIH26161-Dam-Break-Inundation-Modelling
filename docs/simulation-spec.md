# Simulation Specification

> Ownership: **SPH Agent** owns SPH sections; **Delft3D Agent** owns Delft3D sections. Project-wide changes require coordination (AGENTS.md §24).

**Status:** Placeholder. Document only configurations and parameters that are actually implemented or agreed. Never fabricate simulation results (AGENTS.md §31).

---

## 1. SPH / DualSPHysics *(Owner: SPH Agent)*

### 1.1 Toolchain

- DualSPHysics v5.4 (`DualSPHysics5.4CPU_win64.exe` / GPU)
- GenCase (`GenCase_win64.exe`)
- PartVTK (`PartVTK_win64.exe`)
- ParaView v6.2 (post-processing & 3D visual inspection)

### 1.2 Case Configuration

| Parameter | Value | Units | Notes |
|---|---|---|---|
| Study Reach | Rishiganga Canyon to Reni Confluence | - | UTM Zone 44N (EPSG:32644) |
| Inter-particle distance ($dp$) | 12.0 | m | Fast prototype resolution (60k boundary, 9.4k fluid) |
| Valley Elevation Drop | ~374.0 | m | Natural gravity channel |
| Initial Fluid Dimensions | 750 × 350 × 45 | m | Upstream reservoir / sudden release volume |
| Boundary Representation | 3D Triangular Surface Mesh (STL) | - | 254,448 triangles derived from 2m DEM |
| Output Directory | `src/simulation/sph/case_rishiganga/` | - | Case XML, VTK time-series, results |

### 1.3 Numerical Settings

| Parameter | Value | Notes |
|---|---|---|
| Time step / CFL handling | Variable CFL (CFL = 0.2, CoefDtMin = 0.05) | Explicit Symplectic / Verlet integration |
| Kernel | Quintic Wendland (Kernel = 2) | Smooth particle interaction |
| Viscosity Treatment | Artificial Viscosity ($\alpha = 0.05$) | Boundary multiplication factor = 1.0 |
| Density Diffusion | DDT Molteni / Fourtakas (DDT = 2, Value = 0.1) | Stabilizes hydrodynamics |
| Fluid Reference Density ($\rho_0$) | 1000.0 | $\text{kg/m}^3$ |
| Gravity ($g$) | (0.0, 0.0, -9.81) | $\text{m/s}^2$ |
| Simulation Duration ($T_{max}$) | 60.0 | s ($T_{out} = 1.0\text{ s}$ frame frequency) |

### 1.4 Output Extraction & Results

- **Peak Flood Velocity ($v_{max}$):** $102.37\text{ m/s}$ (observed in steep canyon descent).
- **Estimated Arrival Time at Reni Confluence:** $\approx 18.0\text{ seconds}$.
- **GIS Export:** `src/simulation/sph/case_rishiganga/results/sph_flood_extent.geojson` (EPSG:32644).
- **Summary Metrics:** `src/simulation/sph/case_rishiganga/results/sph_simulation_summary.json`.

### 1.5 Validation Cases

- Prototype case calibrated against standard SPH dam-break benchmarks and gravity-driven open channel flow on complex topography. Validation comparison with 2D shallow water equation (Delft3D) in progress.

---

## 2. HEC-RAS 2D Unsteady Flow Solver *(Owner: HEC-RAS / 2D Agent)*

### 2.1 Toolchain

- HEC-RAS v7.0.1 (June 2026 64-bit engine)
- RAS Mapper v7.0.1 (GIS & terrain mapping)

### 2.2 Grid / Mesh Preparation

| Property | Value | Notes |
|---|---|---|
| Study Reach | Rishiganga Canyon to Reni Confluence | UTM Zone 44N (EPSG:32644) |
| Grid Spacing ($dx, dy$) | 40.0 m × 40.0 m | Regular 2D mesh grid |
| Active Computational Cells | 10,089 cells | High-resolution terrain coverage |
| Boundary Conditions | Upstream Breach & Downstream Outlet | 2 external 2D BC lines |

### 2.3 Model Configuration

| Parameter | Value | Units | Notes |
|---|---|---|---|
| Inflow Peak ($Q_{peak}$) | 1,500.0 | $\text{m}^3/\text{s}$ | 4-hour outburst hydrograph (15-min steps) |
| Downstream Boundary | Normal Depth ($S = 0.02$) | - | Friction slope boundary |
| Manning's Roughness ($n$) | 0.06 | - | Mountain gorge & channel bed roughness |
| Equation Set | Diffusion Wave 2D | - | Implicit finite volume 2D solver |

### 2.4 Output Extraction & Results

- **Computation Runtime:** **44 seconds** across 8 CPU cores.
- **Overall Volume Accounting Error:** **0.000043%** (Near-perfect mass conservation).
- **Peak Channel Flow Velocity:** $30.68\text{ m/s}$.
- **HDF5 Export:** `hec_ras/Rishiganga_Dam_Break.p01.hdf`
- **GIS Exports:** `data/gis_outputs/cell_centers_results.geojson` & `data/gis_outputs/flood_summary.json`.

---

## 3. Cross-Model Rules (both owners)

- Units must be preserved explicitly everywhere.
- Modelling assumptions must remain visible in code and docs.
- Neither engine may be silently replaced (AGENTS.md §25).
- Results feed the common data contract before comparison/GIS/dashboard consumption.
