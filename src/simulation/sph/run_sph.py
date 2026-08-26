"""
DualSPHysics Automation Pipeline for Rishiganga Case
Module: src/simulation/sph/run_sph.py
Ownership: Member B (SPH Agent)

Automates:
1. GenCase: Converts STL terrain + Dam/Breach + Reni Bridge + Reservoir into SPH particles.
2. DualSPHysics (CPU / GPU): Solves Navier-Stokes hydrodynamic equations.
3. PartVTK: Converts particles into VTK / CSV for ParaView and GIS.
4. IsoSurface: Reconstructs realistic 3D continuous fluid surface mesh.
"""

import os
import sys
import subprocess
import time

DUALSPHYSICS_BIN = r"E:\DualSPHysics_v5.4.3\DualSPHysics_v5.4\bin\windows"
CASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "case_rishiganga"))

def run_gencase():
    print("=" * 60)
    print("STEP 1: Running GenCase (Dam, Bridge, Terrain & Reservoir)...")
    print("=" * 60)
    
    gencase_exe = os.path.join(DUALSPHYSICS_BIN, "GenCase_win64.exe")
    cmd = [gencase_exe, "CaseRishiganga_Def", "CaseRishiganga", "-save:all"]
    
    start_t = time.time()
    res = subprocess.run(cmd, cwd=CASE_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print("GenCase Error Output:\n", res.stderr or res.stdout)
        raise RuntimeError("GenCase execution failed.")
    print(res.stdout)
    print(f"GenCase completed in {time.time() - start_t:.2f} seconds.\n")

def run_dualsphysics(threads=8):
    print("=" * 60)
    print("STEP 2: Running DualSPHysics Hydrodynamic Solver...")
    print("=" * 60)
    
    solver_exe = os.path.join(DUALSPHYSICS_BIN, "DualSPHysics5.4CPU_win64.exe")
    out_dir = "CaseRishiganga_out"
    cmd = [
        solver_exe,
        "-cpu",
        f"-ompthreads:{threads}",
        "CaseRishiganga",
        out_dir,
        "-dirdataout", "data",
        "-sv:binx,vtk"
    ]
    
    start_t = time.time()
    res = subprocess.run(cmd, cwd=CASE_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print("DualSPHysics Error Output:\n", res.stderr or res.stdout)
        raise RuntimeError("DualSPHysics solver failed.")
    print(res.stdout)
    print(f"Simulation completed in {time.time() - start_t:.2f} seconds.\n")

def run_isosurface():
    print("=" * 60)
    print("STEP 3: Generating 3D Continuous Water Surface Meshes (IsoSurface)...")
    print("=" * 60)
    
    iso_exe = os.path.join(DUALSPHYSICS_BIN, "IsoSurface_win64.exe")
    data_dir = os.path.join("CaseRishiganga_out", "data")
    iso_dir = os.path.join("CaseRishiganga_out", "iso")
    os.makedirs(os.path.join(CASE_DIR, iso_dir), exist_ok=True)
    
    cmd = [
        iso_exe,
        "-dirdata", data_dir,
        "-saveiso", os.path.join(iso_dir, "SurfaceWater"),
        "-vars:vel",
        "-threads:8"
    ]
    
    start_t = time.time()
    res = subprocess.run(cmd, cwd=CASE_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print("IsoSurface Output / Notice:\n", res.stdout)
    else:
        print(res.stdout)
        print(f"3D Surface generation completed in {time.time() - start_t:.2f} seconds.\n")

def run_partvtk():
    print("=" * 60)
    print("STEP 4: Post-Processing VTK Particle Data for ParaView...")
    print("=" * 60)
    
    partvtk_exe = os.path.join(DUALSPHYSICS_BIN, "PartVTK_win64.exe")
    data_dir = os.path.join("CaseRishiganga_out", "data")
    vtk_dir = os.path.join("CaseRishiganga_out", "vtk")
    os.makedirs(os.path.join(CASE_DIR, vtk_dir), exist_ok=True)
    
    cmd = [
        partvtk_exe,
        "-dirin", data_dir,
        "-savevtk", os.path.join(vtk_dir, "PartFluid"),
        "-onlytype:-all,fluid",
        "-vars:+vel,+rhop,+idp,+press"
    ]
    
    start_t = time.time()
    res = subprocess.run(cmd, cwd=CASE_DIR, capture_output=True, text=True)
    print(res.stdout)
    print(f"VTK export completed in {time.time() - start_t:.2f} seconds.\n")

if __name__ == "__main__":
    run_gencase()
    run_dualsphysics(threads=8)
    run_isosurface()
    run_partvtk()
