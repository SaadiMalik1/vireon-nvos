'use client';

import React, { useState, useEffect } from 'react';

type ExecutionResponse = {
  scenario_id: string;
  execution_hash: string;
  bundle_path: string;
  metrics: Record<string, number>;
  passed: boolean;
};

type EvidenceData = {
  events: any[];
  measurements: any[];
};

export function ValidationPanel() {
  const [scenarios, setScenarios] = useState<string[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [executionResult, setExecutionResult] = useState<ExecutionResponse | null>(null);
  const [evidenceData, setEvidenceData] = useState<EvidenceData | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/scenarios`)
      .then(res => res.json())
      .then(data => {
        setScenarios(data.scenarios);
        if (data.scenarios.length > 0) {
          setSelectedScenario(data.scenarios[0]);
        }
      })
      .catch(err => console.error("Failed to load scenarios:", err));
  }, []);

  const handleExecute = async () => {
    if (!selectedScenario) return;
    setIsRunning(true);
    setExecutionResult(null);
    setEvidenceData(null);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/execute/${selectedScenario}`, { method: 'POST' });
      const data = await res.json();
      setExecutionResult(data);

      const evRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/evidence/${data.execution_hash}`);
      const evData = await evRes.json();
      setEvidenceData(evData);
    } catch (err) {
      console.error("Execution failed:", err);
    } finally {
      setIsRunning(false);
    }
  };

  const renderCausalGraph = () => {
    if (!evidenceData) return null;
    const events = evidenceData.events;
    // Extract unique causal stages in order
    const stages = ['INTENTION', 'NEURAL_STATE', 'SIGNAL', 'DECODER_STATE', 'COMMAND', 'ACTUATOR_STATE', 'FEEDBACK'];
    
    return (
      <div className="mt-8 border rounded-lg p-6 bg-card text-card-foreground">
        <h3 className="text-xl font-bold mb-4">Causal Integrity Graph</h3>
        <div className="flex flex-wrap items-center gap-2">
          {stages.map((stage, idx) => {
            const stageEvents = events.filter(e => e.causal_stage === stage);
            const hasEvent = stageEvents.length > 0;
            const isPerturbed = stageEvents.some(e => e.is_perturbed);
            
            let bgClass = "bg-muted text-muted-foreground";
            if (hasEvent) {
              bgClass = isPerturbed ? "bg-destructive text-destructive-foreground font-bold" : "bg-primary text-primary-foreground";
            }
            
            return (
              <React.Fragment key={stage}>
                <div className={`px-4 py-2 rounded-full text-sm ${bgClass}`}>
                  {stage}
                </div>
                {idx < stages.length - 1 && (
                  <div className="text-muted-foreground">→</div>
                )}
              </React.Fragment>
            );
          })}
        </div>
        
        {executionResult && (
          <div className="mt-6 pt-6 border-t grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold text-sm text-muted-foreground mb-2">Agency Metrics</h4>
              <ul className="space-y-1">
                {Object.entries(executionResult.metrics).map(([k, v]) => (
                  <li key={k} className="flex justify-between">
                    <span className="text-sm">{k}</span>
                    <span className="font-mono text-sm">{typeof v === 'number' ? v.toFixed(3) : v}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-sm text-muted-foreground mb-2">Assertion Result</h4>
              <div className={`inline-block px-3 py-1 rounded text-sm font-bold ${executionResult.passed ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'}`}>
                {executionResult.passed ? 'PASSED' : 'FAILED'}
              </div>
              <div className="mt-2 text-xs text-muted-foreground truncate" title={executionResult.bundle_path}>
                Bundle: {executionResult.bundle_path}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold tracking-tight">Validation Studio</h2>
        <p className="text-muted-foreground text-sm">VIREON SDK Kernel</p>
      </div>
      
      <div className="bg-card border rounded-lg p-6">
        <div className="space-y-4">
          <label className="text-sm font-medium">Select Scenario Blueprint</label>
          <div className="flex gap-4">
            <select 
              className="flex-1 rounded-md border bg-background px-3 py-2"
              value={selectedScenario || ''}
              onChange={(e) => setSelectedScenario(e.target.value)}
              disabled={isRunning || scenarios.length === 0}
            >
              {scenarios.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <button 
              onClick={handleExecute}
              disabled={isRunning || !selectedScenario}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md font-medium disabled:opacity-50"
            >
              {isRunning ? 'Executing...' : 'Run Scenario'}
            </button>
          </div>
        </div>
      </div>

      {renderCausalGraph()}
    </div>
  );
}
