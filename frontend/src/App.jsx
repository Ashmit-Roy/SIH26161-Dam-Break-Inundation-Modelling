import React, { useEffect } from "react";
import { useSimulation } from "./hooks/useSimulation";
import { INITIAL_DASHBOARD_STATE } from "./hooks/useSimulation";
import Header from "./components/Header";
import ControlPanel from "./components/ControlPanel";
import MapDisplay from "./components/MapDisplay";
import StatusBar from "./components/StatusBar";
import ResultsPanel from "./components/ResultsPanel";
import ComparisonPanel from "./components/ComparisonPanel";
import DownloadSection from "./components/DownloadSection";
import "./assets/style.css";

function App() {
  const {
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
  } = useSimulation();

  const [dismissedError, setDismissedError] = React.useState(false);

  const [simulationStatus, setSimulationStatus] = React.useState({
    stage: "idle",
    message: "Select a model and run simulation",
    model: null,
    startTime: null,
    endTime: null,
  });

  // Update status machine
  useEffect(() => {
    if (isRunning && simulationStatus.stage === "idle") {
      setSimulationStatus({
        stage: "uploading",
        message: "Uploading input data...",
        model: form.model,
        startTime: new Date(),
      });
    } else if (!isRunning && simulationStatus.stage === "uploading") {
      setSimulationStatus({
        stage: "running",
        message: "Running simulation...",
        model: form.model,
        startTime: simulationStatus.startTime,
        endTime: new Date(),
      });
    }
  }, [isRunning, form.model, simulationStatus]);

  useEffect(() => {
    if (!isRunning && simulationStatus.stage === "running") {
      // Simulation completed
      if (error) {
        setSimulationStatus({
          stage: "failed",
          message: error || "Simulation failed",
          model: simulationStatus.model,
          startTime: simulationStatus.startTime,
          endTime: new Date(),
        });
      } else {
        setSimulationStatus({
          stage: "completed",
          message: "Simulation completed successfully",
          model: simulationStatus.model,
          startTime: simulationStatus.startTime,
          endTime: new Date(),
        });
      }
    }
  }, [isRunning, error, simulationStatus]);

  return (
    <div className="app">
      <Header />

      <div className="main-layout">
        <ControlPanel
          form={form}
          onChange={onFormChange}
          onSubmit={handleStartSimulation}
          isRunning={isRunning}
          DEMO_SCENARIOS={DEMO_SCENARIOS}
          ModelType={ModelType}
          setSimulationStatus={setSimulationStatus}
        />

        <main className="main-content">
          <MapDisplay
            floodExtent={floodExtent}
            currentResult={currentResult}
            comparison={comparison}
            isRunning={isRunning}
          />

          <div className="panels-wrapper">
            <ResultsPanel
              currentResult={currentResult}
              comparison={comparison}
            />
            <ComparisonPanel
              comparison={comparison}
              ModelType={ModelType}
            />
          </div>
        </main>
      </div>

      <StatusBar
        stage={simulationStatus.stage}
        message={simulationStatus.message}
        model={simulationStatus.model}
        startTime={simulationStatus.startTime}
        endTime={simulationStatus.endTime}
      />

      <DownloadSection
        currentResult={currentResult}
        comparison={comparison}
        simulationId={state?.current_simulation}
      />

      {error && !dismissedError && (
        <div className="error-overlay">
          <div className="error-panel">
            <h3>Error</h3>
            <p>{error}</p>
            <button onClick={() => setDismissedError(true)}>Dismiss</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;