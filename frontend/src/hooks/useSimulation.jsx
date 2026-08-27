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


export const INITIAL_DASHBOARD_STATE = {
  current_simulation: "SPH-RISHIGANGA-001",
  simulation_progress: 100.0,
  comparison_active: true,
  last_update: new Date().toISOString() + "Z",
};

export function useSimulation() {
  const [state, setState] = useState(INITIAL_DASHBOARD_STATE);
  const [progress, setProgress] = useState(100);
  const [currentResult, setCurrentResult] = useState({
    simulation_id: "SPH-RISHIGANGA-001",
    model: "SPH",
    water_depth: 3.85,
    location: { lat: 6.2, lon: 100.5 },
    timestamp: new Date().toISOString(),
  });
  const [floodExtent, setFloodExtent] = useState({
    simulation_id: "SPH-RISHIGANGA-001",
    polygon: {
      type: "Polygon",
      coordinates: [
        [
          [6.12, 100.42],
          [6.35, 100.38],
          [6.42, 100.55],
          [6.20, 100.62],
          [6.12, 100.42],
        ]
      ],
    },
    arrival_time: 18.0,
  });
  const [comparison, setComparison] = useState({
    metric: "water_depth",
    sph_data: {
      simulation_id: "SPH-RISHIGANGA-001",
      location: { lat: 6.2, lon: 100.5 },
      water_depth: 3.85,
      timestamp: new Date().toISOString(),
    },
    delft3d_data: {
      simulation_id: "DELFT3D-FM-001",
      location: { lat: 6.2, lon: 100.5 },
      water_depth: 4.12,
      timestamp: new Date().toISOString(),
    },
    timestamp: new Date().toISOString(),
  });
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  /** @type {import("../types").SimulationRequest} */
  const [form, setForm] = useState({
    simulation_id: "SPH-RISHIGANGA-001",
    river_dam: "rishiganga",
    model: ModelType.SPH,
    scenario_id: "scenario_a",
    breach_width: 15,
    breach_height: 3,
    crs: "EPSG:4326",
  });

  // Load initial dashboard state
  useEffect(() => {
    async function loadState() {
      try {
        const apiBase = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
        const resp = await fetch(`${apiBase}/api/simulation/state`, {
          method: "GET",
          credentials: "omit",
        });
        if (resp.ok) {
          const data = await resp.json();
          if (data && typeof data === "object") {
            setState(data);
          }
        }
      } catch (e) {
        console.log("Dashboard state loaded from initial fallback");
      }
    }
    loadState();
  }, []);

  // Form change handler
  const onFormChange = useCallback(
    (e) => {
      const { name, value, type, checked } = e.target;
      let fieldName = name;
      if (name === "river-dam") fieldName = "river_dam";
      if (name === "scenario") fieldName = "scenario_id";

      let parsedValue;
      if (type === "number") {
        parsedValue = value === "" ? "" : Number(value);
      } else if (type === "checkbox") {
        parsedValue = checked;
      } else if (value === "true") {
        parsedValue = true;
      } else if (value === "false") {
        parsedValue = false;
      } else {
        parsedValue = value;
      }

      setForm((prev) => ({
        ...prev,
        [fieldName]: parsedValue,
      }));
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