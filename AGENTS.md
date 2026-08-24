# AGENTS.md — SIH26161 Dam Break Inundation Modelling

## 1. PROJECT OVERVIEW

**Project:** SIH26161-Dam-Break-Inundation-Modelling

**Goal:** Build a dam-break inundation modelling system for flood-risk assessment, emergency planning, and disaster-management decision support.

**Domain:** Hydraulic engineering, flood modelling, computational fluid dynamics, GIS, remote sensing, and disaster management.

**Project Context:** Smart India Hackathon 2026 — Problem Statement SIH26161.

**Development Stage:** Early-stage hackathon prototype.

The immediate objective is a working, demonstrable proof-of-concept covering the major required deliverables. Do not assume that any component is production-ready or fully calibrated.

---

# 2. CORE DELIVERABLES

The system is intended to cover:

1. Hydrodynamic modelling using:
   - Smoothed Particle Hydrodynamics (SPH)
   - Delft3D / Delft3D FM

2. Comparison of:
   - Flood extent
   - Water depth
   - Arrival time
   - Computational time where available

3. Loss and damage analysis:
   - Population
   - Land use
   - Roads
   - Bridges/infrastructure

4. GIS output generation:
   - Flood-depth rasters
   - Flood-extent polygons
   - Shapefile (`.shp`)
   - KML (`.kml`)
   - GeoJSON where appropriate

5. Web dashboard:
   - Input/scenario selection
   - Simulation execution
   - Interactive flood map
   - Damage/loss information
   - SPH vs Delft3D comparison
   - Downloadable outputs

6. Near-real-time flood detection:
   - Google Earth Engine
   - Sentinel-1/2
   - SAR-based flood detection
   - ML classification only where explicitly implemented and justified

---

# 3. INTENDED PIPELINE

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

---

# 4. TECHNOLOGY RULES

## Hydrodynamic Modelling

### SPH

* DualSPHysics
* GenCase
* ParaView

### Grid-Based Modelling

* Delft3D
* Delft3D Flexible Mesh (Delft3D FM)

Do not silently replace DualSPHysics or Delft3D with another hydraulic engine.

## Scientific Computing

* Python
* NumPy
* pandas
* rasterio
* GeoPandas
* Shapely
* GDAL/OGR where appropriate

## GIS

* QGIS
* GDAL/OGR
* rasterio
* GeoPandas
* Shapely

## Remote Sensing

* Google Earth Engine
* Sentinel-1
* Sentinel-2
* Python Earth Engine API
* GEE JavaScript where appropriate

## Dashboard

Intended architecture:

* Frontend: React or an already-approved frontend
* Mapping: Leaflet or Mapbox
* Backend: FastAPI or Flask
* Database: PostgreSQL + PostGIS where required

Do not make major technology substitutions without team approval.

---

# 5. REPOSITORY STRUCTURE

The actual repository structure always takes precedence over this example.

```text
/
├── src/
│   ├── data/
│   ├── simulation/
│   │   ├── sph/
│   │   └── delft3d/
│   ├── gis/
│   ├── dashboard/
│   ├── gee/
│   ├── models/
│   ├── io/
│   ├── visualization/
│   └── utils/
│
├── tests/
├── data/
├── notebooks/
├── docs/
│
├── requirements.txt
├── pyproject.toml
├── README.md
└── AGENTS.md
```

Do not create this entire structure simply because it is listed here.

Follow the repository's existing structure.

---

# 6. MULTI-AGENT FILE OWNERSHIP POLICY

This project is developed by multiple AI agents and human team members simultaneously.

The following rules exist specifically to prevent agents from overwriting or interfering with each other's work.

## 6.1 Fundamental Rule

**An agent may freely modify only files inside its assigned ownership area.**

An agent may:

* Read any repository file.
* Inspect any module.
* Run any relevant code.
* Run tests belonging to other modules.
* Understand interfaces between modules.

However:

**Read access does NOT imply write access.**

An agent must not modify another agent's owned files simply because the modification would make its own task easier.

---

# 7. AGENT OWNERSHIP MAP

The following ownership map defines the default write boundaries.

| Agent   | Module                 | Primary Write Area          |
| ------- | ---------------------- | --------------------------- |
| Agent 1 | Data                   | `src/data/**`               |
| Agent 2 | SPH                    | `src/simulation/sph/**`     |
| Agent 3 | Delft3D                | `src/simulation/delft3d/**` |
| Agent 4 | GIS / Output           | `src/gis/**`                |
| Agent 5 | Dashboard / Full Stack | `src/dashboard/**`          |
| Agent 6 | GEE / ML               | `src/gee/**`                |

Additional test and documentation ownership is defined below.

---

# 8. AGENT 1 — DATA AGENT

## Write Ownership

```text
src/data/**
tests/data/**
notebooks/data/**
```

The agent may also modify:

```text
docs/data-formats.md
```

only when the change specifically concerns data formats or ingestion.

## Responsibilities

* DEM acquisition
* DEM preprocessing
* Terrain preparation
* Dataset ingestion
* Data normalization
* Dam data preparation
* River/hydrological data preparation
* Population data preparation
* Land-use data preparation
* Data metadata
* Input validation

## Must Not Modify

```text
src/simulation/sph/**
src/simulation/delft3d/**
src/gis/**
src/dashboard/**
src/gee/**
```

unless explicitly authorized.

---

# 9. AGENT 2 — SPH AGENT

## Write Ownership

```text
src/simulation/sph/**
tests/simulation/sph/**
notebooks/sph/**
```

The agent may modify:

```text
docs/simulation-spec.md
```

only for SPH-specific information.

## Responsibilities

* DualSPHysics integration
* GenCase configuration
* SPH input preparation
* SPH execution
* SPH parameters
* SPH result extraction
* SPH post-processing
* SPH metadata
* SPH validation

## Must Not Modify

```text
src/data/**
src/simulation/delft3d/**
src/gis/**
src/dashboard/**
src/gee/**
```

unless explicitly authorized.

## Important

The SPH Agent must not change Delft3D implementation to make SPH comparison easier.

---

# 10. AGENT 3 — DELFT3D AGENT

## Write Ownership

```text
src/simulation/delft3d/**
tests/simulation/delft3d/**
notebooks/delft3d/**
```

The agent may modify:

```text
docs/simulation-spec.md
```

only for Delft3D-specific information.

## Responsibilities

* Delft3D configuration
* Delft3D FM configuration
* Grid/mesh preparation
* Boundary conditions
* Dam-break configuration
* Delft3D execution
* Delft3D result extraction
* Delft3D post-processing
* Delft3D metadata
* Delft3D validation

## Must Not Modify

```text
src/data/**
src/simulation/sph/**
src/gis/**
src/dashboard/**
src/gee/**
```

unless explicitly authorized.

## Important

The Delft3D Agent must not change SPH implementation code.

---

# 11. AGENT 4 — GIS / OUTPUT AGENT

## Write Ownership

```text
src/gis/**
tests/gis/**
notebooks/gis/**
```

The agent may modify:

```text
src/visualization/**
```

only when the visualization is specifically related to GIS/model outputs.

The agent may modify:

```text
docs/data-formats.md
```

only for GIS output specifications.

## Responsibilities

* Raster processing
* Flood-depth raster generation
* Flood extent generation
* Polygon generation
* CRS/reprojection
* Shapefile generation
* KML generation
* GeoJSON generation
* Spatial overlays
* Population impact analysis
* Land-use impact analysis
* Road impact analysis
* Bridge/infrastructure impact analysis
* GIS visualization

## Must Not Modify

```text
src/data/**
src/simulation/sph/**
src/simulation/delft3d/**
src/dashboard/**
src/gee/**
```

unless explicitly authorized.

---

# 12. AGENT 5 — DASHBOARD / FULL-STACK AGENT

## Write Ownership

```text
src/dashboard/**
tests/dashboard/**
```

If the repository separates frontend/backend directories, the Dashboard Agent owns the existing frontend/backend directories associated with the dashboard.

## Responsibilities

* Frontend
* Backend
* API routes
* API request/response models
* Dashboard state
* Interactive maps
* Simulation controls
* Progress/status UI
* Comparison UI
* Damage/loss UI
* Output download interface
* Dashboard integration

## Must Not Modify

```text
src/data/**
src/simulation/sph/**
src/simulation/delft3d/**
src/gis/**
src/gee/**
```

unless explicitly authorized.

## Important

The Dashboard Agent must not implement hydraulic physics inside the dashboard.

The dashboard should orchestrate and visualize simulations rather than replace simulation modules.

---

# 13. AGENT 6 — GEE / ML AGENT

## Write Ownership

```text
src/gee/**
tests/gee/**
notebooks/gee/**
```

## Responsibilities

* Google Earth Engine integration
* Sentinel-1 processing
* Sentinel-2 processing
* SAR preprocessing
* Flood/water detection
* Baseline water extent comparison
* GEE API integration
* Optional ML classification
* ML preprocessing
* ML evaluation

## Must Not Modify

```text
src/data/**
src/simulation/sph/**
src/simulation/delft3d/**
src/gis/**
src/dashboard/**
```

unless explicitly authorized.

## Important

The GEE/ML Agent must not introduce ML into the SPH or Delft3D physics pipeline unless the team explicitly approves it.

---

# 14. TEST OWNERSHIP

Tests follow the module they test.

```text
tests/
├── data/                 → Data Agent
├── simulation/
│   ├── sph/              → SPH Agent
│   └── delft3d/          → Delft3D Agent
├── gis/                  → GIS Agent
├── dashboard/            → Dashboard Agent
└── gee/                  → GEE/ML Agent
```

An agent must not rewrite another module's tests simply to make its own implementation pass.

If a test exposes a genuine contract problem in another module:

1. Report the issue.
2. Explain the expected behavior.
3. Request the owning agent to fix it.

---

# 15. SHARED FILES

Some files may legitimately be shared by multiple agents.

Examples:

```text
README.md
AGENTS.md
pyproject.toml
requirements.txt
docs/architecture.md
docs/api-contract.md
docs/data-formats.md
docs/simulation-spec.md
```

These files are **protected shared resources**.

## Shared-file rule

An agent must not modify a shared file unless:

1. The change is directly required by its task.
2. The agent has checked the current contents.
3. The change does not overwrite another agent's unrelated work.
4. The change is compatible with the existing project architecture.

## Never do this

Do not replace an entire shared file with an older version.

Do not regenerate a shared configuration file from scratch unless explicitly required.

Prefer the smallest possible edit.

---

# 16. CROSS-MODULE CHANGES

Cross-module changes are the biggest source of multi-agent conflicts.

A cross-module change occurs when an agent needs to modify files outside its ownership boundary.

Examples:

* SPH Agent changing GIS code.
* GIS Agent changing SPH output code.
* Dashboard Agent changing simulation code.
* GEE Agent changing the dashboard.
* Data Agent changing API models.

## Required procedure

Before modifying another module:

```text
1. Inspect the other module.
2. Identify why the change is required.
3. Determine whether the change can be avoided.
4. If possible, expose or update an interface instead.
5. Communicate the required change to the owning agent.
6. Only modify the other module with explicit approval.
```

Do not silently cross ownership boundaries.

---

# 17. INTERFACE-FIRST RULE

When two agents need to work together, prefer changing the interface rather than directly modifying the other agent's implementation.

For example:

```text
SPH Agent
    ↓
SPH Output Contract
    ↓
GIS Agent
```

and:

```text
Delft3D Agent
    ↓
Delft3D Output Contract
    ↓
GIS Agent
```

The GIS Agent should consume the agreed output contract rather than modifying SPH/Delft3D internals.

Similarly:

```text
Simulation Modules
        ↓
Common Simulation Output
        ↓
Dashboard
```

The Dashboard Agent should consume the defined API/data contract instead of directly editing simulation internals.

---

# 18. COMMON DATA CONTRACT

Where practical, SPH and Delft3D results should be normalized into a common representation before being consumed by downstream modules.

A conceptual result may contain:

```text
simulation_id
model
scenario_id
crs
terrain_reference
water_depth
water_level
velocity
arrival_time
flood_extent
simulation_time
metadata
```

Do not introduce or remove fields from an existing contract without checking all consumers.

If a contract needs to change:

1. Document the change.
2. Identify affected modules.
3. Notify the owning agents.
4. Update consumers as part of the coordinated change.

---

# 19. FILE-LEVEL SAFETY RULE

Directory ownership alone is not enough.

Before editing a file:

1. Check whether the file already contains uncommitted changes.
2. Inspect its current content.
3. Determine whether another agent may be working on it.
4. Do not overwrite changes that were not created by you.
5. Modify only the necessary sections.

If the file contains unexpected changes:

**STOP and inspect before continuing.**

Do not use commands such as:

```bash
git checkout -- <file>
git restore <file>
```

on another agent's work.

Do not reset the repository merely to obtain a clean working tree.

---

# 20. GIT SAFETY FOR MULTIPLE AGENTS

## Never

Agents must not:

```bash
git reset --hard
git clean -fd
git checkout -- .
```

unless explicitly instructed by the team.

These commands can destroy another agent's uncommitted work.

## Branches

Each agent should preferably work on its own feature branch.

Examples:

```text
feature/data-pipeline
feature/sph-model
feature/delft3d-model
feature/gis-processing
feature/dashboard
feature/gee-flood-detection
```

## Commits

Commits should contain only the agent's intended changes.

Before committing:

```bash
git status
git diff
```

Verify that unrelated files are not included.

---

# 21. UNRELATED FILE PROTECTION

An agent must not modify files merely because:

* Formatting differs.
* A linter suggests a change.
* The code could be cleaner.
* The file is nearby.
* The agent prefers another architecture.
* The agent wants to refactor the project.
* The change is unrelated to the current task.

If a task requires changes to multiple modules, identify this explicitly before implementation.

---

# 22. GENERATED FILES

Generated artifacts should generally not be manually edited.

Examples:

```text
simulation outputs
large rasters
generated shapefiles
temporary GIS files
compiled frontend assets
cache files
model output directories
```

Do not commit large generated files unless explicitly required.

Use `.gitignore` appropriately.

---

# 23. DATA DIRECTORY SAFETY

Large datasets must be treated as protected resources.

Examples:

```text
DEM files
satellite imagery
simulation outputs
particle datasets
Delft3D output files
large rasters
```

Agents must not:

* Delete another agent's dataset.
* Replace datasets without notice.
* Rename shared datasets without updating consumers.
* Commit large datasets accidentally.

If a dataset must be changed, document:

```text
Dataset name
Old version
New version
Reason for change
Affected modules
```

---

# 24. DOCUMENTATION OWNERSHIP

Documentation is shared but should remain scoped.

### Architecture

```text
docs/architecture.md
```

Changes affecting project-wide architecture require team approval.

### Data Formats

```text
docs/data-formats.md
```

Data Agent owns data-ingestion specifications.

GIS Agent owns GIS output specifications.

### Simulation Specification

```text
docs/simulation-spec.md
```

SPH Agent owns SPH sections.

Delft3D Agent owns Delft3D sections.

Project-wide changes require coordination.

### API Contract

```text
docs/api-contract.md
```

Dashboard Agent owns implementation details.

Any change affecting simulation/GIS/GEE interfaces must be coordinated with the relevant owners.

---

# 25. MAJOR ARCHITECTURAL DECISION RULE

AI agents must not independently make project-wide architectural changes.

Examples:

* Replacing DualSPHysics.
* Replacing Delft3D.
* Replacing React.
* Replacing FastAPI/Flask.
* Replacing PostgreSQL/PostGIS.
* Changing the core data format.
* Redesigning repository structure.
* Introducing a new major framework.
* Moving ownership between agents.

Required procedure:

```text
Identify problem
      ↓
Explain proposed solution
      ↓
Identify affected modules
      ↓
Estimate integration impact
      ↓
Obtain team approval
      ↓
Implement
```

---

# 26. TASK BOUNDARY RULE

Every agent must determine the smallest set of files required to complete its task.

Before implementation, answer:

```text
What files do I need to modify?
Why does each file need modification?
Which agent owns each file?
Can the task be completed without crossing ownership boundaries?
```

If the answer requires another agent's files, coordinate before editing them.

---

# 27. AGENT WORKFLOW

Every agent must follow:

```text
Inspect
   ↓
Understand
   ↓
Identify Owner
   ↓
Check File Boundaries
   ↓
Plan
   ↓
Implement
   ↓
Test
   ↓
Review Diff
   ↓
Report
```

---

# 28. INSPECTION RULES

Before changing code:

* Read `AGENTS.md`.
* Inspect the repository.
* Inspect the relevant module.
* Inspect relevant tests.
* Inspect related documentation.
* Identify module dependencies.
* Check the Git working tree.
* Check whether relevant files already contain changes.

Do not assume the repository matches the example structure in this document.

---

# 29. IMPLEMENTATION RULES

Agents should:

* Make the smallest appropriate change.
* Reuse existing utilities.
* Follow existing conventions.
* Avoid unrelated refactoring.
* Avoid unnecessary dependencies.
* Preserve existing functionality.
* Keep module boundaries intact.

---

# 30. PYTHON RULES

Where Python is used:

* Follow PEP 8-compatible conventions.
* Use type hints for public APIs.
* Use clear names.
* Keep functions reasonably focused.
* Add docstrings to important public functions/classes.
* Follow the project's configured formatter/linter.

Do not introduce a new formatter or linter without approval.

---

# 31. NUMERICAL / HYDRAULIC RULES

For numerical modelling:

* Preserve units explicitly.
* Document assumptions.
* Validate input ranges.
* Handle numerical instability explicitly.
* Consider CFL/time-step constraints.
* Handle wet/dry conditions carefully.
* Do not silently hide numerical failures.
* Keep modelling assumptions visible.

Never fabricate simulation results.

---

# 32. TESTING

Potential commands:

```bash
pytest
ruff check .
mypy .
```

Use the repository's configured commands when available.

For new functionality:

* Add unit tests.
* Add integration tests where required.
* Test invalid inputs.
* Test important edge cases.
* Test API contracts.
* Test numerical behavior where applicable.

For modelling code, validate against available:

* Analytical cases
* Benchmark cases
* Published/reference results
* Internal consistency checks

If validation is unavailable, explicitly state this.

---

# 33. DEMO / PROTOTYPE INTEGRITY

Agents must distinguish between:

1. Real computed results
2. Sample/test results
3. Placeholder/demo data
4. Planned functionality

Never fabricate:

* Flood depths
* Flood extents
* Arrival times
* Damage estimates
* Accuracy scores
* Validation results
* Performance benchmarks

If sample data is used, label it clearly as:

```text
DEMO DATA
```

or:

```text
SAMPLE DATA
```

---

# 34. API / DATA CONTRACT RULES

Shared interfaces are critical.

Agents must:

* Define clear inputs and outputs.
* Use explicit schemas.
* Preserve existing contracts.
* Document interface changes.
* Avoid silently breaking consumers.

Where APIs exist:

* Validate inputs.
* Document request formats.
* Document response formats.
* Keep frontend/backend contracts synchronized.

---

# 35. ERROR HANDLING

Validate:

* Uploaded files
* DEM metadata
* Coordinates
* Breach parameters
* Numerical parameters
* API requests
* Geometry
* Missing terrain values

Numerical failures must be handled explicitly.

Do not silently continue after a critical failure.

---

# 36. SECURITY

Never commit:

* API keys
* Passwords
* Credentials
* Private tokens
* Secrets

Never expose secrets in logs.

Use environment variables or configuration files for machine-specific settings.

Never hardcode machine-specific absolute paths.

---

# 37. DEFINITION OF DONE

A task is complete only when:

* Requested functionality is implemented.
* Existing functionality has not unintentionally broken.
* Relevant tests are added or updated.
* Relevant tests pass.
* Relevant lint/type/build checks pass where applicable.
* Final Git diff contains only intended changes.
* No secrets were introduced.
* No machine-specific paths were introduced.
* API/data contracts remain consistent.
* Important assumptions are documented.
* Limitations are clearly stated.
* Ownership boundaries were respected.
* Cross-module changes were coordinated.

---

# 38. FINAL MULTI-AGENT SAFETY RULES

These rules have priority when multiple agents work simultaneously.

### Rule 1 — Read Anything, Write Only Your Area

An agent may inspect the entire repository.

An agent may write only to its assigned ownership area unless explicitly authorized.

### Rule 2 — Never Overwrite Another Agent's Work

If another agent has modified a file, preserve its changes.

### Rule 3 — Never Reset Someone Else's Work

Do not use destructive Git commands to remove changes you did not create.

### Rule 4 — Shared Files Are Protected

Modify shared files only when necessary and only with minimal changes.

### Rule 5 — Interfaces Before Internals

When modules need to communicate, prefer updating contracts/interfaces rather than modifying another module's internals.

### Rule 6 — No Silent Cross-Boundary Changes

Never modify another agent's module without communicating the reason.

### Rule 7 — Small Diffs

Only modify files required for the task.

### Rule 8 — Inspect Before Edit

Always inspect the current state before changing a file.

### Rule 9 — Verify Before Commit

Run:

```bash
git status
git diff
```

before committing.

### Rule 10 — Stop on Conflict

If an agent discovers unexpected changes, conflicting implementations, or unclear ownership:

**STOP → INSPECT → COMMUNICATE → RESOLVE → CONTINUE**

Do not guess.

---

# 39. QUICK OWNERSHIP REFERENCE

```text
DATA AGENT
├── src/data/**
├── tests/data/**
└── notebooks/data/**

SPH AGENT
├── src/simulation/sph/**
├── tests/simulation/sph/**
└── notebooks/sph/**

DELFT3D AGENT
├── src/simulation/delft3d/**
├── tests/simulation/delft3d/**
└── notebooks/delft3d/**

GIS AGENT
├── src/gis/**
├── tests/gis/**
└── notebooks/gis/**

DASHBOARD AGENT
├── src/dashboard/**
└── tests/dashboard/**

GEE / ML AGENT
├── src/gee/**
├── tests/gee/**
└── notebooks/gee/**
```

---

# 40. WHEN AN AGENT NEEDS ANOTHER AGENT'S FILE

Use this process:

```text
Agent A needs file owned by Agent B
             ↓
       Inspect the file
             ↓
     Determine exact change
             ↓
 Can the change be avoided?
        ↙           ↘
      YES            NO
       ↓              ↓
Use existing       Contact owner
interface          / coordinate
                       ↓
                 Agree on change
                       ↓
                 Make minimal edit
                       ↓
                 Run integration tests
```

Do not bypass this process.

---

# 41. FINAL RULE

When in doubt:

**Inspect → Identify Owner → Understand → Plan → Coordinate → Implement → Test → Review → Report**

The safest implementation is the smallest implementation that satisfies the task while preserving module ownership and shared interfaces.

**Never guess when the repository, contract, documentation, Git history, or owning agent can provide the answer.**