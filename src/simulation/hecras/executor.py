"""HEC-RAS 7.0.1 Simulation Executor Wrapper."""

import os
from pathlib import Path
import subprocess
from typing import Dict, Any

from .config import HECRASConfig


class HECRASExecutor:
    """
    Executor for HEC-RAS 7.0.1 2D Hydraulic Simulations.
    Manages project file setup, execution, and verification.
    """

    DEFAULT_HECRAS_PATHS = [
        Path(r"C:\Program Files (x86)\HEC\HEC-RAS\7.0.1\Ras.exe"),
        Path(r"C:\Program Files\HEC\HEC-RAS\7.0.1\Ras.exe"),
        Path(r"C:\Program Files (x86)\HEC\HEC-RAS\6.4\Ras.exe"),
    ]

    def __init__(self, config: HECRASConfig, hecras_exe_path: Path | None = None):
        self.config = config
        self.project_dir = Path(config.project_dir)
        self.hecras_exe = hecras_exe_path or self._find_hecras_executable()

    def _find_hecras_executable(self) -> Path | None:
        """Attempt to locate HEC-RAS installation executable on Windows."""
        for path in self.DEFAULT_HECRAS_PATHS:
            if path.exists():
                return path
        return None

    def prepare_project_directory(self) -> Path:
        """Create the HEC-RAS project directory structure and base template files."""
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.config.output.output_dir.mkdir(parents=True, exist_ok=True)

        prj_file = self.project_dir / f"{self.config.project_name}.prj"
        if not prj_file.exists():
            self._write_project_file(prj_file)

        return self.project_dir

    def _write_project_file(self, prj_file: Path) -> None:
        """Generate a standard HEC-RAS .prj project file."""
        prj_content = f"""Proj Title={self.config.project_name}
Default Directory=
SI Units
Geom File=g01
Unsteady File=u01
Plan File=p01
BEGIN DESCRIPTION:
Dam-break inundation simulation for scenario {self.config.scenario_id}.
Generated automatically for SIH26161.
END DESCRIPTION:
"""
        with open(prj_file, "w", encoding="utf-8") as f:
            f.write(prj_content)

    def run_simulation(self) -> Dict[str, Any]:
        """
        Execute the HEC-RAS 2D simulation.
        If HEC-RAS executable is present, launches the calculation engine.
        Otherwise, creates workspace structures and returns simulation metadata.
        """
        self.prepare_project_directory()
        prj_file = self.project_dir / f"{self.config.project_name}.prj"

        result_info: Dict[str, Any] = {
            "simulation_id": self.config.simulation_id,
            "scenario_id": self.config.scenario_id,
            "model": "HEC-RAS 7.0.1",
            "project_file": str(prj_file),
            "status": "prepared",
            "hecras_exe": str(self.hecras_exe) if self.hecras_exe else "Not Found (Manual GUI Execution)",
        }

        if self.hecras_exe and self.hecras_exe.exists():
            cmd = [str(self.hecras_exe), str(prj_file)]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                result_info["status"] = "success" if proc.returncode == 0 else "ready_for_gui"
                result_info["stdout"] = proc.stdout
                result_info["stderr"] = proc.stderr
            except Exception as e:
                result_info["status"] = "ready_for_gui"
                result_info["error"] = str(e)
        else:
            result_info["status"] = "ready_for_gui"
            result_info["message"] = (
                "HEC-RAS project files prepared. Launch HEC-RAS 7.0.1 GUI to run computation."
            )

        return result_info
