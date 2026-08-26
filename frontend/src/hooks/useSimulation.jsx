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

// Runtime constants (mirrors the TypeScript types in ../types.ts)
const ModelType = { SPH: "SPH", DELFT3D: "Delft3D" };
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
const DEMO_SCENARIOS = [
  { id: "scenario_a", label: "Scenario A — Small Breach", breach_width: 10, breach_height: 2 },
  { id: "scenario_b", label: "Scenario B — Large Breach", breach_width: 15, breach_height: 3 },
  { id: "scenario_c", label: "Scenario C — Full Collapse", breach_width: 25, breach_height: 5 },
];


// Initial dashboard state (exported for reuse in App.jsx)
export const INITIAL_DASHBOARD_STATE = {
  current_simulation: null,
  simulation_progress: 0.0,
  comparison_active: false,
  last_update: new Date().toISOString() + "Z",
};

export function useSimulation() {
  const [state, setState] = useState(INITIAL_DASHBOARD_STATE);
  const [progress, setProgress] = useState(0);
  const [currentResult, setCurrentResult] = useState(null);
  const [floodExtent, setFloodExtent] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  /** @type {import("../types").SimulationRequest} */
  const [form, setForm] = useState({
    simulation_id: "",
    model: ModelType.SPH,
    scenario_id: "scenario_a",
  });

  // Load initial dashboard state
  useEffect(() => {
    async function loadState() {
      try {
        const dashboardState = await (async () => {
          // Try to get from API if available
          const apiBase = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
          const resp = await fetch(`${apiBase}/api/simulation/state`, {
            method: "GET",
            credentials: "omit",
          });
          if (resp.ok) {
            const data = await resp.json();
            return data;
          }
        })();
        setState(dashboardState);
      } catch (e) {
        // Keep initial state if API not available
        console.log("Dashboard state loaded from initial mock");
      }
    }
    loadState();
  }, []);

  // Form change handler
  const onFormChange = useCallback(
    (e) => {
      const { name, value, type, checked } = e.target;
      setForm((prev) => ({
        ...prev,
        [name]:
          type === "number" ? Number(value) : value === "true" ? true : value === "false"
            ? false
            : checked,
      }));
    },
    []
  );

  // Start simulation
  const handleStartSimulation = useCallback(async (formValues) => {
    setIsRunning(true);
    setError(null);

    // Validate the form
    const validation = validateSimulationRequest(formValues as SimulationRequest);
    if (!validation.isValid) {
      setError(validation.errors.join(", "));
      setIsRunning(false);
      return;
    }

    // Disable run button during simulation
    setState((prev) => ({
      ...prev,
      current_simulation: formValues.simulation_id,
      simulation_progress: 0.0,
    }));

    try {
      // Start the simulation via API
      const result = await runSimulation({
        simulation_id: formValues.simulation_id,
        model: formValues.model,
        scenario_id: formValues.scenario_id,
        breach_width: formValues.breach_width,
        breach_height: formValues.breach_height,
        simulation_time: formValues.simulation_time,
        crs: formValues.crs,
      });

      setState((prev) => ({
        ...prev,
        current_simulation: result.simulation_id,
      }));

      // Poll status until completed using helper
      const pollPromise = pollSimulationStatus(
        result.simulation_id,
        (progress, status) => {
          setProgress(progress);
          // Update status text through state if needed
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
        setCurrentResult(simResult.water_depth);
        setFloodExtent(simResult.flood_extent);

        // Get comparison if model is "both" or Delft3D
        if (result.model !== "SPH" || formValues.model === "both") {
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
          // Silently fall back - dashboard state updates on next poll
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
  }, []);

  // Load results after simulation ID changes (for cases where results are available separately)
  useEffect(() => {
    async function loadResults() {
      if (!state.current_simulation) return;

      try {
        const simResult = await getSimulationResult(state.current_simulation);
        if (simResult) {
          setCurrentResult(simResult.water_depth);
          setFloodExtent(simResult.flood_extent);

          // Get comparison if applicable
          if (state.model !== "SPH" || form.model === "both") {
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
  }, [state.current_simulation]);

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