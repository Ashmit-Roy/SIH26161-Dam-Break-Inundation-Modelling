"""
DEM to STL Converter for DualSPHysics SPH Simulation
Module: src/simulation/sph/dem_to_stl.py
Ownership: Member B (SPH Agent)

Converts the cropped GeoTIFF DEM into an STL 3D surface mesh
and records geo-referencing metadata (UTM offset) for GIS integration.
"""

import os
import json
import struct
import numpy as np
from PIL import Image

def write_binary_stl(filename, vertices, faces):
    """
    Writes vertices and triangle faces to a fast binary STL file.
    """
    num_faces = len(faces)
    header = b"DualSPHysics Terrain Mesh - Rishiganga Reach" + b" " * (80 - 44)
    
    with open(filename, "wb") as f:
        f.write(header[:80])
        f.write(struct.pack("<I", num_faces))
        
        for tri in faces:
            v0 = vertices[tri[0]]
            v1 = vertices[tri[1]]
            v2 = vertices[tri[2]]
            
            # Compute face normal via cross product (v1-v0) x (v2-v0)
            edge1 = v1 - v0
            edge2 = v2 - v0
            norm = np.cross(edge1, edge2)
            norm_mag = np.linalg.norm(norm)
            if norm_mag > 0:
                norm = norm / norm_mag
            else:
                norm = np.array([0.0, 0.0, 1.0], dtype=np.float32)
                
            # Pack normal + 3 vertices + 2-byte attribute byte count
            f.write(struct.pack("<3f", norm[0], norm[1], norm[2]))
            f.write(struct.pack("<3f", v0[0], v0[1], v0[2]))
            f.write(struct.pack("<3f", v1[0], v1[1], v1[2]))
            f.write(struct.pack("<3f", v2[0], v2[1], v2[2]))
            f.write(struct.pack("<H", 0))

def convert_dem_to_stl(
    dem_path: str,
    output_dir: str,
    step: int = 4,
    utm_x_min: float = 374065.5572,
    utm_y_max: float = 3373502.4593,
    pixel_size: float = 2.0
):
    """
    Reads GeoTIFF, subsamples by `step` to keep triangle count optimal for DualSPHysics GenCase,
    and outputs binary STL + geo metadata.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    im = Image.open(dem_path)
    dem = np.array(im, dtype=np.float32)
    rows, cols = dem.shape
    
    # Handle nodata (-9999 or negative outliers)
    valid_mask = dem > 0
    if not np.any(valid_mask):
        raise ValueError("No valid elevation data found in DEM!")
    min_elev = float(dem[valid_mask].min())
    dem[~valid_mask] = min_elev
    
    # Subsample grid (step=4 gives ~8m mesh resolution: extremely detailed yet fast for GenCase)
    sub_dem = dem[::step, ::step]
    sub_rows, sub_cols = sub_dem.shape
    
    dx = pixel_size * step
    dy = pixel_size * step
    
    # Coordinate system: origin at (0,0) in bottom-left
    # Note: GeoTIFF row 0 is top (Y_max), so Y_local = (sub_rows - 1 - r) * dy
    grid_x = np.arange(sub_cols) * dx
    grid_y = np.arange(sub_rows - 1, -1, -1) * dy
    
    xx, yy = np.meshgrid(grid_x, grid_y)
    zz = sub_dem - min_elev  # Base Z at 0 for computational stability
    
    # Build vertices: (N, 3)
    vertices = np.column_stack([
        xx.flatten(),
        yy.flatten(),
        zz.flatten()
    ]).astype(np.float32)
    
    # Build triangular faces (2 triangles per quad)
    faces = []
    for r in range(sub_rows - 1):
        for c in range(sub_cols - 1):
            i0 = r * sub_cols + c
            i1 = r * sub_cols + (c + 1)
            i2 = (r + 1) * sub_cols + c
            i3 = (r + 1) * sub_cols + (c + 1)
            
            # Quad split into two CCW triangles
            faces.append([i0, i2, i1])
            faces.append([i1, i2, i3])
            
    faces = np.array(faces, dtype=np.int32)
    
    stl_path = os.path.join(output_dir, "rishiganga_terrain.stl")
    print(f"Writing STL to {stl_path} ({len(vertices)} vertices, {len(faces)} triangles)...")
    write_binary_stl(stl_path, vertices, faces)
    
    # Save geo-referencing metadata
    metadata = {
        "reach_name": "Rishiganga - Reni Confluence",
        "crs": "EPSG:32644 (WGS 84 / UTM zone 44N)",
        "dem_resolution_m": pixel_size,
        "mesh_resolution_m": dx,
        "utm_origin": {
            "utm_x_min": utm_x_min,
            "utm_y_min": float(utm_y_max - rows * pixel_size),
            "elevation_z_offset_m": min_elev
        },
        "domain_size_m": {
            "x_length": float(sub_cols * dx),
            "y_width": float(sub_rows * dy),
            "z_height": float(zz.max())
        },
        "stl_file": "rishiganga_terrain.stl",
        "vertices_count": int(len(vertices)),
        "triangles_count": int(len(faces))
    }
    
    meta_path = os.path.join(output_dir, "geo_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Saved geo metadata to {meta_path}")
    print("Terrain conversion complete!")
    return metadata

if __name__ == "__main__":
    convert_dem_to_stl(
        dem_path="data/rishiganga_reach_dem.tif",
        output_dir="src/simulation/sph/case_rishiganga",
        step=4
    )
