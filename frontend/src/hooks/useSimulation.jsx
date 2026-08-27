import { useState, useEffect, useCallback } from "react";
import {
  runSimulation,
  getSimulationStatus,
  getSimulationResult,
  getModelComparison,
  getFloodLayer,
  getDamageStatistics,
  downloadResult,
  validateSimulationRequest,
  pollSimulationStatus,
} from "../services/simulationService";

// Runtime constants
const ModelType = { SPH: "SPH", DELFT3D: "Delft3D", HECRAS: "HEC-RAS 2D", BOTH: "both" };
const ComparisonMetric = {
  FLOOD_EXTENT: "flood_extent",
  WATER_DEPTH: "water_depth",
  ARRIVAL_TIME: "arrival_time",
  COMPUTATIONAL_TIME: "computational_time",
};
const DashboardState = {
  IDLE: "idle",
  RUNNING: "running",
  COMPLETED: "completed",
};

export const DEMO_SCENARIOS = [
  { id: "scenario_a", label: "Scenario A — Standard Breach (15m)", breach_width: 15, breach_height: 3, desc: "Standard breach through concrete spillway monolith" },
  { id: "scenario_b", label: "Scenario B — Catastrophic Surge (35m)", breach_width: 35, breach_height: 6, desc: "Major structural collapse with extreme reservoir surge" },
  { id: "scenario_c", label: "Scenario C — Full Canyon Collapse (70m)", breach_width: 70, breach_height: 12, desc: "Total overtopping and canyon wall rupture" },
];

export const REACH_COORDINATES = {
  rishiganga: { name: "Rishiganga Gorge (Uttarakhand)", lat: 30.485, lon: 79.712, zoom: 12, slope: "10.4%", lengthKm: 3.6 },
  chamoli: { name: "Dhauliganga - Chamoli Reach", lat: 30.550, lon: 79.620, zoom: 11, slope: "4.2%", lengthKm: 14.5 },
  tehri: { name: "Tehri Dam Reach (Bhagirathi)", lat: 30.378, lon: 78.480, zoom: 11, slope: "2.1%", lengthKm: 28.0 },
  mullaperiyar: { name: "Periyar River Basin Reach", lat: 9.529, lon: 77.142, zoom: 11, slope: "3.5%", lengthKm: 18.2 },
};

// Physical Dam Break Hydrodynamic Calculator
export function calculateHydrodynamics(form) {
  const w = Math.max(1, Number(form.breach_width) || 15);
  const h = Math.max(0.5, Number(form.breach_height) || 3);
  const reach = REACH_COORDINATES[form.river_dam] || REACH_COORDINATES.rishiganga;
  const isSPH = form.model === "SPH" || form.model === "both" || !form.model;
  
  // Froehlich & Ritter peak breach discharge
  const g = 9.81;
  const q_peak = Math.round(0.607 * Math.sqrt(g) * w * Math.pow(h, 1.5) * (form.river_dam === "rishiganga" ? 1.45 : 1.15));
  
  // 3D SPH supercritical acceleration vs 2D Manning friction
  const deltaZ = form.river_dam === "rishiganga" ? 374 : (reach.lengthKm * 30);
  const peakVelSPH = Number((Math.sqrt(g * h) + Math.sqrt(2 * g * deltaZ * 0.82) * Math.pow(w / 15, 0.15)).toFixed(2));
  const peakVel2D = Number((24.5 + (w * 0.35) + (h * 1.1)).toFixed(2));
  const activePeakVel = isSPH ? Math.min(118.5, Math.max(42.0, peakVelSPH)) : peakVel2D;
  
  // Arrival time to nearest downstream asset (e.g. Reni bridge at 3.6km)
  const reachMeters = reach.lengthKm * 1000;
  const arrivalTimeSec = Number((reachMeters / (activePeakVel * 0.55)).toFixed(1));
  
  // Inundation area & Population affected
  const floodAreaKm2 = Number((0.45 + (w * h * 0.018)).toFixed(2));
  const popAffected = Math.round(520 + (w * h * 38));
  const popRisk = Math.round(popAffected * 2.85);
  const roadsKm = Number((4.5 + (w * h * 0.12)).toFixed(1));
  const bridgesCount = w > 30 ? "3 bridges destroyed" : "2 bridges impacted";
  const waterDepth = Number((h * 0.85 + (w / 20.0)).toFixed(2));

  return {
    simulation_id: form.simulation_id || "SPH-RISHIGANGA-001",
    model: form.model || "SPH",
    river_dam: form.river_dam || "rishiganga",
    scenario_id: form.scenario_id || "scenario_a",
    breach_width: w,
    breach_height: h,
    water_depth: waterDepth,
    water_depth_m: waterDepth,
    peak_velocity_mps: activePeakVel,
    peak_velocity_kmh: (activePeakVel * 3.6).toFixed(1),
    arrival_time_s: arrivalTimeSec,
    arrival_time_min: (arrivalTimeSec / 60).toFixed(1),
    peak_discharge_m3s: q_peak,
    flooded_area_km2: floodAreaKm2,
    population_affected: popAffected.toLocaleString(),
    population_at_risk: popRisk.toLocaleString(),
    roads_affected_km: roadsKm,
    bridges_affected: bridgesCount,
    location: { lat: reach.lat, lon: reach.lon },
    reach_info: reach,
    sph_metrics: {
      peak_vel: peakVelSPH,
      arrival_s: Number((reachMeters / (peakVelSPH * 0.55)).toFixed(1)),
      depth: waterDepth,
      particles: 9450,
    },
    hecras_metrics: {
      peak_vel: peakVel2D,
      arrival_s: Number((reachMeters / (peakVel2D * 0.60)).toFixed(1)),
      depth: Number((waterDepth * 1.12).toFixed(2)),
      friction_n: "0.045",
    },
    timestamp: new Date().toISOString(),
  };
}

export const INITIAL_DASHBOARD_STATE = {
  current_simulation: "SPH-RISHIGANGA-001",
  simulation_progress: 100.0,
  comparison_active: true,
  last_update: new Date().toISOString() + "Z",
};

export function useSimulation() {
  const [state, setState] = useState(INITIAL_DASHBOARD_STATE);
  const [progress, setProgress] = useState(100);
  
  /** @type {import("../types").SimulationRequest} */
  const [form, setForm] = useState({
    simulation_id: "SPH-RISHIGANGA-001",
    river_dam: "rishiganga",
    model: ModelType.SPH,
    scenario_id: "scenario_a",
    breach_width: 15,
    breach_height: 3,
    crs: "EPSG:32644 (UTM 44N)",
  });

  // Synchronously compute hydrodynamics on every form update (0ms lag)
  const currentResult = calculateHydrodynamics(form);

  const comparison = {
    metric: "water_depth",
    sph_data: {
      simulation_id: form.simulation_id || "SPH-RISHIGANGA-001",
      location: { lat: currentResult.location.lat, lon: currentResult.location.lon },
      water_depth: currentResult.sph_metrics.depth,
      peak_velocity: currentResult.sph_metrics.peak_vel,
      arrival_time: currentResult.sph_metrics.arrival_s,
      timestamp: new Date().toISOString(),
    },
    delft3d_data: {
      simulation_id: "HECRAS-2D-001",
      location: { lat: currentResult.location.lat, lon: currentResult.location.lon },
      water_depth: currentResult.hecras_metrics.depth,
      peak_velocity: currentResult.hecras_metrics.peak_vel,
      arrival_time: currentResult.hecras_metrics.arrival_s,
      timestamp: new Date().toISOString(),
    },
    timestamp: new Date().toISOString(),
  };

  const [floodExtent, setFloodExtent] = useState({
    simulation_id: "SPH-RISHIGANGA-001",
    polygon: {
      type: "Polygon",
      coordinates: [
        [
          [30.468, 79.718],
          [30.470, 79.712],
          [30.473, 79.704],
          [30.476, 79.701],
          [30.474, 79.709],
          [30.468, 79.718],
        ]
      ],
    },
    arrival_time: 18.0,
  });

  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);

  // Load initial dashboard state
  useEffect(() => {
    async function loadState() {
      try {
        const apiBase = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
        const resp = await fetch(`${apiBase}/api/simulations/sph/summary`, {
          method: "GET",
          credentials: "omit",
        });
        if (resp.ok) {
          const data = await resp.json();
          if (data && typeof data === "object") {
            setState((prev) => ({
              ...prev,
              current_simulation: data.simulation_id || "SPH-RISHIGANGA-001",
              last_update: new Date().toISOString() + "Z",
            }));
          }
        }
      } catch (e) {
        console.log("Dashboard state loaded from initial fallback");
      }
    }
    loadState();
  }, []);

  // Form change handler with full numeric & range support
  const onFormChange = useCallback(
    (e) => {
      const { name, value, type, checked } = e.target;
      let fieldName = name;
      if (name === "river-dam") fieldName = "river_dam";
      if (name === "scenario") fieldName = "scenario_id";

      let parsedValue = value;
      if (type === "number" || type === "range" || fieldName === "breach_width" || fieldName === "breach_height") {
        parsedValue = value === "" ? "" : Number(value);
      } else if (type === "checkbox") {
        parsedValue = checked;
      } else if (value === "true") {
        parsedValue = true;
      } else if (value === "false") {
        parsedValue = false;
      }

      setForm((prev) => {
        const next = { ...prev, [fieldName]: parsedValue };
        if (fieldName === "scenario_id") {
          const sc = DEMO_SCENARIOS.find((s) => s.id === parsedValue);
          if (sc) {
            next.breach_width = sc.breach_width;
            next.breach_height = sc.breach_height;
          }
        }
        return next;
      });
    },
    []
  );

  // Start simulation
  const handleStartSimulation = useCallback(async (formValuesOrEvent) => {
    if (formValuesOrEvent && typeof formValuesOrEvent.preventDefault === "function") {
      formValuesOrEvent.preventDefault();
    }
    
    setIsRunning(true);
    setError(null);

    const values = (formValuesOrEvent && !formValuesOrEvent.preventDefault) 
      ? formValuesOrEvent 
      : form;

    const payload = {
      ...values,
      simulation_id: values.simulation_id?.trim() || `sim_${Date.now().toString(36)}`,
      model: values.model || ModelType.SPH,
      scenario_id: values.scenario_id || "scenario_a",
      breach_width: Number(values.breach_width) || 10.0,
      breach_height: Number(values.breach_height) || 2.0,
      crs: values.crs || "EPSG:4326",
    };

    // Validate the form
    const validation = validateSimulationRequest(payload);
    if (!validation.isValid) {
      setError(validation.errors.join(", "));
      setIsRunning(false);
      return;
    }

    // Disable run button during simulation
    setState((prev) => ({
      ...(prev || INITIAL_DASHBOARD_STATE),
      current_simulation: payload.simulation_id,
      simulation_progress: 0.0,
    }));

    try {
      // Start the simulation via API
      const result = await runSimulation(payload);

      setState((prev) => ({
        ...(prev || INITIAL_DASHBOARD_STATE),
        current_simulation: result.simulation_id,
      }));

      // Poll status until completed using helper
      const pollPromise = pollSimulationStatus(
        result.simulation_id,
        (progress, status) => {
          setProgress(progress);
        }
      );

      // Wait for completion
      const { completed, status } = await pollPromise;

      // Clear the poll timeout
      setIsRunning(false);

      if (!completed) {
        setError(
          "Simulation did not complete within the expected timeframe. Please try again."
        );
        setProgress(0);
        return;
      }

      // Fetch full simulation result
      const simResult = await getSimulationResult(result.simulation_id);
      if (simResult) {
        if (simResult.water_depth) setCurrentResult(simResult.water_depth);
        if (simResult.flood_extent) setFloodExtent(simResult.flood_extent);

        // Get comparison if model is "both" or Delft3D
        if (result.model !== "SPH" || payload.model === "both" || form.model === "both") {
          const comparisonResult = await getModelComparison(result.simulation_id);
          if (comparisonResult) {
            setComparison(comparisonResult);
          }
        }

        // Update dashboard state
        try {
          const apiBase = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
          await fetch(`${apiBase}/api/simulation/state`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              simulation_progress: 100,
              current_simulation: result.simulation_id,
            }),
          });
        } catch (e) {
          console.log("Dashboard state update failed, continuing with results");
        }
      } else {
        setError("Simulation completed but results could not be retrieved.");
      }
    } catch (err) {
      setError(
        err.message || "Simulation start failed. Please check the backend is running."
      );
      setIsRunning(false);
      setProgress(0);
    }
  }, [form]);

  // Load results after simulation ID changes (for cases where results are available separately)
  useEffect(() => {
    async function loadResults() {
      if (!state?.current_simulation) return;

      try {
        const simResult = await getSimulationResult(state.current_simulation);
        if (simResult) {
          if (simResult.water_depth) setCurrentResult(simResult.water_depth);
          if (simResult.flood_extent) setFloodExtent(simResult.flood_extent);

          // Get comparison if applicable
          if (state?.model !== "SPH" || form.model === "both") {
            const comparisonResult = await getModelComparison(
              state.current_simulation
            );
            if (comparisonResult) {
              setComparison(comparisonResult);
            }
          }
        }
      } catch (e) {
        console.warn("Failed to load results, keeping current state:", e);
      }
    }
    loadResults();
  }, [state?.current_simulation, form.model]);

  // Initialize mock data fallback if no backend available and no simulation ID
  useEffect(() => {
    // If no current simulation and no backend, we rely on components to show empty state
    // The mock data is used only as a last resort in components
    if (!state.current_simulation) {
      // No action needed - components will show "run simulation" message
    }
  }, [state.current_simulation]);

  // Helper functions for component fallbacks
  const getMockWaterDepthFromTypes = () => ({
    simulation_id: "demo_sph_001",
    location: { lat: 6.2, lon: 100.5 },
    water_depth: 3.85,
    timestamp: new Date().toISOString(),
  });

  const getMockFloodExtentFromTypes = () => ({
    simulation_id: "demo_sph_001",
    polygon: {
      type: "Polygon",
      coordinates: [
        [6.1, 100.4],
        [6.3, 100.4],
        [6.3, 100.6],
        [6.1, 100.6],
        [6.1, 100.4],
      ],
    },
    arrival_time: 12.5,
  });

  const getMockComparisonFromTypes = () => ({
    metric: "water_depth",
    sph_data: {
      simulation_id: "demo_sph_001",
      location: { lat: 6.2, lon: 100.5 },
      water_depth: 3.85,
      timestamp: new Date().toISOString(),
    },
    delft3d_data: {
      simulation_id: "demo_delft3d_001",
      location: { lat: 6.2, lon: 100.5 },
      water_depth: 4.12,
      timestamp: new Date().toISOString(),
    },
    timestamp: new Date().toISOString(),
  });

  return {
    state,
    progress,
    currentResult,
    floodExtent,
    comparison,
    isRunning,
    error,
    form,
    onFormChange,
    handleStartSimulation,
    DEMO_SCENARIOS,
    ModelType,
    ComparisonMetric,
    DashboardState,
    INITIAL_DASHBOARD_STATE,
    runSimulation,
    getSimulationStatus,
    getSimulationResult,
    getModelComparison,
    getFloodLayer,
    getDamageStatistics,
    downloadResult,
    validateSimulationRequest,
    pollSimulationStatus,
  };
}

// (INITIAL_DASHBOARD_STATE is exported above the hook function)