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

## 2. Delft3D / Delft3D FM *(Owner: Delft3D Agent)*

### 2.1 Toolchain

- Delft3D
- Delft3D Flexible Mesh (Delft3D FM)

### 2.2 Grid / Mesh Preparation

| Property | Value | Notes |
|---|---|---|
| TBD | TBD | TBD |

### 2.3 Model Configuration

| Parameter | Value | Units | Notes |
|---|---|---|---|
| Boundary conditions | TBD | | |
| Breach configuration | TBD | | |
| Roughness | TBD | | |
| Time step / CFL | TBD | | Explicit; instability must not be hidden |

### 2.4 Output Extraction

TBD — model output → normalized result contract (see [api-contract.md](api-contract.md)).

### 2.5 Validation Cases

TBD — list analytical/benchmark/reference cases used, or state explicitly that validation is unavailable.

---

## 3. Cross-Model Rules (both owners)

- Units must be preserved explicitly everywhere.
- Modelling assumptions must remain visible in code and docs.
- Neither engine may be silently replaced (AGENTS.md §25).
- Results feed the common data contract before comparison/GIS/dashboard consumption.
