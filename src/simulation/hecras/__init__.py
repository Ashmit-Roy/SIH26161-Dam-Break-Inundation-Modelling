"""
HEC-RAS 7.0.1 Hydrodynamic Simulation Module.

Provides integration for HEC-RAS 2D grid-based hydraulic modeling:
- Project & Mesh Configuration
- Controller Execution Wrapper
- Result Extraction & Output Normalization
"""

from .config import HECRASConfig, GeometryConfig, BoundaryConfig, TimeStepConfig, BreachConfig
from .executor import HECRASExecutor
from .output import extract_hecras_results, normalize_to_common_contract

__all__ = [
    "HECRASConfig",
    "GeometryConfig",
    "BoundaryConfig",
    "TimeStepConfig",
    "BreachConfig",
    "HECRASExecutor",
    "extract_hecras_results",
    "normalize_to_common_contract",
]
