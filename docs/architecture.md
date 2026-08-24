# Architecture

> Owner: Team (shared). Project-wide changes require team approval — see AGENTS.md §24.

**Status:** Placeholder. This document must describe the *actual implemented* architecture as it evolves. Do not document planned components as if they exist.

## 1. System Context

Dam-break inundation modelling system for flood-risk assessment, emergency planning, and disaster-management decision support (SIH26161).

## 2. Intended Pipeline

```text
Raw Data
   ↓
Data Preparation / GIS Preprocessing
   ↓
Clean Terrain + Model Inputs
   ↓
 ┌───────────────────────┐
 │                       │
 ▼                       ▼
SPH / DualSPHysics    Delft3D / Delft3D FM
 │                       │
 └───────────┬───────────┘
             ↓
       Result Comparison
             ↓
     Damage / Loss Analysis
             ↓
     GIS Output Generation
             ↓
          Dashboard
             ↑
             │
   GEE Near-Real-Time Flood Module
```

## 3. Module Responsibilities

| Module | Path | Owner |
|---|---|---|
| Data preparation / ingestion | `src/data/` | Data Agent |
| SPH simulation (DualSPHysics) | `src/simulation/sph/` | SPH Agent |
| Delft3D simulation | `src/simulation/delft3d/` | Delft3D Agent |
| GIS outputs / impact analysis | `src/gis/` | GIS Agent |
| Web dashboard | `src/dashboard/` | Dashboard Agent |
| GEE near-real-time flood detection | `src/gee/` | GEE/ML Agent |

## 4. Interfaces

- Simulation results are normalized into a **common data contract** before downstream consumption — see [api-contract.md](api-contract.md).
- Input/output file formats are specified in [data-formats.md](data-formats.md).
- Hydrodynamic configuration is specified in [simulation-spec.md](simulation-spec.md).

## 5. Decisions

Record significant architectural decisions here (date, decision, rationale, affected modules). Major technology substitutions require team approval — see AGENTS.md §25.
