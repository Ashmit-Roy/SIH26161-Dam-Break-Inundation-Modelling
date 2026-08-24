# Simulation Specification

> Ownership: **SPH Agent** owns SPH sections; **Delft3D Agent** owns Delft3D sections. Project-wide changes require coordination (AGENTS.md §24).

**Status:** Placeholder. Document only configurations and parameters that are actually implemented or agreed. Never fabricate simulation results (AGENTS.md §31).

---

## 1. SPH / DualSPHysics *(Owner: SPH Agent)*

### 1.1 Toolchain

- DualSPHysics
- GenCase
- ParaView (post-processing/visual inspection)

### 1.2 Case Configuration

| Parameter | Value | Units | Notes |
|---|---|---|---|
| TBD | TBD | TBD | TBD |

### 1.3 Numerical Settings

| Parameter | Value | Notes |
|---|---|---|
| Time step / CFL handling | TBD | Must be explicit, never hidden |
| Wet/dry treatment | TBD | |
| Boundary conditions | TBD | |

### 1.4 Output Extraction

TBD — particle data → normalized result contract (see [api-contract.md](api-contract.md)).

### 1.5 Validation Cases

TBD — list analytical/benchmark/reference cases used, or state explicitly that validation is unavailable.

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
