import React from "react";
import {
  ModelType,
  ComparisonMetric,
  SimulationFormValues,
  Location,
  SimulationRequest,
} from "../types";
import { DEMO_SCENARIOS } from "../data/mockData";

/** @typedef {Object} SimulationControlsProps */
/** @property {SimulationFormValues} form */
/** @property {React.ChangeEvent} onChange */
/** @property {(e: React.FormEvent) => void} onSubmit */
/** @property {boolean} isRunning */
/** @property {typeof DEMO_SCENARIOS} DEMO_SCENARIOS */
/** @property {typeof ModelType} ModelType */

function SimulationControls(
  /** @param {SimulationControlsProps} props */
  /** @param {SimulationFormValues} form */
  /** @param {(e: React.ChangeEvent) => void} onChange */
  /** @param {(e: React.FormEvent) => void} onSubmit */
  /** @param {boolean} isRunning */
  /** @param {typeof DEMO_SCENARIOS} DEMO_SCENARIOS */
  /** @param {typeof ModelType} ModelType */
) {
  const /** @type {SimulationFormValues} */ form = /** @type {any} */ ({});
  // The component uses inline handlers, props are for type reference only

  return (
    <div className="control-panel">
      <h2>Simulation Setup</h2>

      <form onSubmit={() => {}} className="setup-form">
        <div className="form-row">
          <label htmlFor="simulation_id">Simulation ID</label>
          <input
            id="simulation_id"
            type="text"
            name="simulation_id"
            placeholder="e.g., demo_sph_001"
          />
        </div>

        <div className="form-row">
          <label htmlFor="model">Model</label>
          <select>
            <option value="SPH">SPH (Smoothed Particle Hydrodynamics)</option>
            <option value="Delft3D">Delft3D / Delft3D FM</option>
          </select>
        </div>

        <div className="form-row">
          <label htmlFor="scenario_id">Scenario</label>
          <select>
            {DEMO_SCENARIOS.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-row">
          <label htmlFor="breach_width">Breach Width (m)</label>
          <input type="number" placeholder="e.g., 10" />
        </div>

        <div className="form-row">
          <label htmlFor="breach_height">Breach Height (m)</label>
          <input type="number" placeholder="e.g., 2" />
        </div>

        <div className="form-row">
          <label htmlFor="crs">Coordinate Reference System</label>
          <input type="text" placeholder="EPSG:4326" />
        </div>

        <button type="submit" className="btn-primary">
          Run Simulation
        </button>
      </form>

      <div className="scenarios">
        <h3>Quick Scenarios</h3>
        <div className="scenarios-list">
          {DEMO_SCENARIOS.map((scenario) => (
            <div className="scenario-btn" onClick={() => {}}>{scenario.name}</div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default SimulationControls;