import hashlib
import json
import numpy as np
import graphlib
from typing import List, Dict, Any, Optional

from vireon_core.contracts.base import IExperimentDef, IProvider, IObservation, IEvent, IMeasurement, IEvidence, IExecutionContext, ExecutionDAG, DAGNode
from vireon_core.contracts.decoder import IDecoder
from vireon_core.agency.causal_graph import CausalGraph, CausalStage
from vireon_core.runtime.rng import DeterministicRNG
from vireon_core.runtime.clock import DeterministicClock, ClockMode
from vireon_core.kernel.plugins import PluginManager

class ExecutionEngine:
    """
    The canonical execution model loop.
    Builds a causal graph of the neurotech pipeline execution using a DAG.
    
    All timestamps come from DeterministicClock (virtual mode) and all
    random values from DeterministicRNG, ensuring bit-exact reproducibility
    when the same seed is used.
    """
    @classmethod
    def run(cls, experiment: IExperimentDef, seed: int = 42, agency_validator_cls=None, signal_metrics_func=None, dag: Optional[ExecutionDAG] = None, plugin_manager: Optional[PluginManager] = None, assertion_evaluator=None) -> IEvidence:
        engine = cls(experiment, seed, agency_validator_cls, signal_metrics_func, plugin_manager, assertion_evaluator)
        return engine.execute(dag)

    def __init__(self, experiment: IExperimentDef, seed: int = 42, agency_validator_cls=None, signal_metrics_func=None, plugin_manager: Optional[PluginManager] = None, assertion_evaluator=None):
        from vireon_core.contracts.base import DefaultAssertionEvaluator
        self.experiment = experiment
        self.seed = seed
        self.agency_validator_cls = agency_validator_cls
        self.signal_metrics_func = signal_metrics_func
        self.plugin_manager = plugin_manager or PluginManager()
        self.assertion_evaluator = assertion_evaluator or DefaultAssertionEvaluator()
        self.rng = DeterministicRNG(seed=seed)
        self.clock = DeterministicClock(mode=ClockMode.VIRTUAL, step_dt_ms=1.0)
        self.provider = experiment.get_provider()
        
        experiment_id = getattr(self.experiment, 'schema', None)
        self.experiment_id_str = experiment_id.id if experiment_id else "unknown_experiment"

        self.causal_graph = CausalGraph(seed=seed, clock=self.clock)
        self.observations: List[IObservation] = []
        self.measurements: List[IMeasurement] = []
        self.assertions_met: Dict[str, bool] = {}
        
        self.node_outputs: Dict[str, Any] = {}

    def log_event(self, description: str, stage: str, causal_parents: List[str] = [], is_perturbed: bool = False) -> str:
        try:
            enum_stage = CausalStage[stage]
        except KeyError:
            enum_stage = CausalStage.UNKNOWN
        return self.causal_graph.add_node(stage=enum_stage, description=description, parents=causal_parents, is_perturbed=is_perturbed)

    @staticmethod
    def _topological_order(dag: ExecutionDAG) -> List[str]:
        graph = {n.node_id: n.inputs for n in dag.nodes}
        ts = graphlib.TopologicalSorter(graph)
        try:
            return list(ts.static_order())
        except graphlib.CycleError as e:
            raise ValueError(f"ExecutionDAG contains a cycle: {e}")

    @staticmethod
    def _validate_dag(dag: ExecutionDAG):
        ExecutionEngine._topological_order(dag)

    def execute(self, dag: Optional[ExecutionDAG] = None) -> IEvidence:
        if dag is None:
            dag = ExecutionDAG.from_stages()
            
        order = self._topological_order(dag)
        node_map = {n.node_id: n for n in dag.nodes}
        event_ids: Dict[str, str] = {}
        
        self.provider.start()
        
        from vireon_core.contracts.base import EnvironmentCapture
        self.execution_context = EnvironmentCapture.capture(
            experiment_id=self.experiment_id_str,
            deterministic_seed=self.seed,
            provider_metadata={"provider_type": self.provider.__class__.__name__},
            version_info="vireon-kernel-0.1.0"
        )
        
        try:
            for node_id in order:
                node = node_map[node_id]
                stage = node.stage
                parents = [event_ids[inp] for inp in node.inputs if inp in event_ids]
                
                inputs_dict = {inp: self.node_outputs.get(inp) for inp in node.inputs}
                is_perturbed = False
                plugin = None
                
                if node.plugin_id:
                    plugin = self.plugin_manager.get_plugin(node.plugin_id)
                    if plugin:
                        from vireon_core.contracts.plugin import ContractValidator, ScientificContractViolation
                        try:
                            ContractValidator.validate(plugin, inputs_dict)
                        except ScientificContractViolation as e:
                            import logging
                            logging.error(f"Contract violation in {node_id}: {e}")
                            evt_id = self.log_event(f"CONTRACT_VIOLATION: {e.violated_assumption}", stage, parents)
                            event_ids[node_id] = evt_id
                            self.node_outputs[node_id] = {"error": "FAILED"}
                            continue
                            
                        if isinstance(plugin, IDecoder) and stage == "DECODER_STATE":
                            # Extract signal from inputs
                            signal = inputs_dict
                            if not getattr(plugin, '_fitted', False):
                                # Dummy fit if labels aren't strictly provided
                                plugin.fit(np.array([]), np.array([]))
                            out = plugin.predict(signal)
                            self.node_outputs[node_id] = out
                            desc = "Decoder processed signal"
                        else:
                            out = plugin.execute(inputs_dict)
                            self.node_outputs[node_id] = out
                            desc = f"{stage} processed"
                    else:
                        self.node_outputs[node_id] = inputs_dict
                        desc = f"{stage} stage skipped (no plugin)" if stage == "DECODER_STATE" else f"{stage} processed"
                else:
                    self.node_outputs[node_id] = inputs_dict
                    desc = f"{stage} stage skipped (no plugin)" if stage == "DECODER_STATE" else f"{stage} processed"
                    
                if stage == "SIGNAL":
                    stimuli = self.experiment.get_stimulus()
                    if stimuli and any(s.type == "perturbation" for s in stimuli):
                        is_perturbed = True
                
                if stage == "SIGNAL" and not self.observations:
                    data = self.provider.get_data()
                    obs_timestamp = self.clock.advance()
                    obs = IObservation(timestamp=obs_timestamp, data_source="provider", data=data)
                    self.observations.append(obs)
                
                evt_id = self.log_event(desc, stage, parents, is_perturbed=is_perturbed)
                event_ids[node_id] = evt_id
                
                if isinstance(plugin, IDecoder) and stage == "DECODER_STATE":
                    self.log_event("DECODER_OUTPUT produced", "UNKNOWN", [evt_id])
                    
        finally:
            self.provider.stop()
            
        events = []
        for node in self.causal_graph.get_nodes():
            events.append(IEvent(
                event_id=node.id,
                timestamp=node.timestamp,
                description=node.description,
                causal_stage=node.stage.value,
                causal_parents=node.parents,
                is_perturbed=node.is_perturbed
            ))

        if self.agency_validator_cls:
            validator = self.agency_validator_cls(self.causal_graph)
            agency_metrics = validator.generate_metrics()
            for name, val in agency_metrics.items():
                self.measurements.append(IMeasurement(metric_name=name, value=val, unit="metric"))

        data = self.observations[0].data if self.observations else None

        if self.signal_metrics_func and isinstance(data, dict) and isinstance(data.get("data"), np.ndarray):
            onset_sec = None
            stim_node = next((n for n in self.causal_graph.get_nodes() if n.stage == CausalStage.SIGNAL and n.is_perturbed), None)
            if stim_node:
                onset_sec = stim_node.timestamp
            elif hasattr(self.experiment, 'stimulus_time_sec'):
                onset_sec = self.experiment.stimulus_time_sec

            signal_metrics = self.signal_metrics_func(data, event_onset_sec=onset_sec)
            self.measurements.extend(signal_metrics)

        assertions = self.experiment.get_assertions()
        m_dict = {m.metric_name: m.value for m in self.measurements}
        for a in assertions:
            self.assertions_met[a.name] = self.assertion_evaluator.evaluate(a, m_dict)

        self.execution_context.random_seed_state = self.rng.get_state()

        execution_hash = self._compute_execution_hash(self.experiment_id_str, events, self.node_outputs, order)

        evidence = IEvidence(
            experiment_id=self.experiment_id_str, 
            execution_hash=execution_hash,
            execution_context=self.execution_context,
            telemetry_path=f"evidence/run_{execution_hash}/telemetry.npz",
            events=events,
            measurements=self.measurements,
            assertions_met=self.assertions_met
        )
        return evidence

    def _compute_execution_hash(self, experiment_id: str, events: List[IEvent], node_outputs: Dict[str, Any] = None, order: List[str] = None) -> str:
        hasher = hashlib.sha256()
        hasher.update(experiment_id.encode("utf-8"))
        hasher.update(str(self.seed).encode("utf-8"))
        hasher.update(self.execution_context.environment_fingerprint.encode("utf-8"))

        for evt in events:
            evt_dict = evt.model_dump(exclude={"object_id"})
            hasher.update(json.dumps(evt_dict, sort_keys=True).encode("utf-8"))

        for m in self.measurements:
            m_dict = m.model_dump(exclude={"object_id"})
            hasher.update(json.dumps(m_dict, sort_keys=True).encode("utf-8"))
            
        if node_outputs and order:
            for node_id in order:
                val = node_outputs.get(node_id)
                hasher.update(node_id.encode("utf-8"))
                hasher.update(str(val).encode("utf-8"))

        return hasher.hexdigest()
