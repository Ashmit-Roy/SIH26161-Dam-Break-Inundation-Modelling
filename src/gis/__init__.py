"""
GIS & Spatial Output Processing Package (SIH26161).
Module ownership: Member D (GIS / Output Agent).
"""

from src.gis.delft3d_processor import (
    generate_study_bridges,
    generate_study_road_network,
    process_delft3d_hydrodynamic_outputs,
)
from src.gis.output import load_vector, save_vector
from src.gis.overlay import (
    compute_spatial_agreement_metrics,
    generate_overlay_kml,
    overlay_sph_on_satellite_hazard,
)
from src.gis.validation import check_crs_match, validate_raster, validate_vector

__all__ = [
    "compute_spatial_agreement_metrics",
    "generate_overlay_kml",
    "overlay_sph_on_satellite_hazard",
    "process_delft3d_hydrodynamic_outputs",
    "generate_study_road_network",
    "generate_study_bridges",
    "load_vector",
    "save_vector",
    "check_crs_match",
    "validate_raster",
    "validate_vector",
]
