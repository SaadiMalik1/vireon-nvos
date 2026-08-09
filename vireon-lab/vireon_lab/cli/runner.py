import os
from datetime import datetime

from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_lab.cli.registry import ExperimentRegistry, CampaignRegistry
from vireon_lab.cli.generators import CSVGenerator, PlotGenerator, PaperGenerator, ProvenanceGenerator
from vireon_validation.evidence_quality import EvidenceQualityEngine

class ExperimentRunner:
    def __init__(self, experiments_dir: str, results_dir: str, repetitions: int = 1):
        self.experiments_dir = experiments_dir
        self.results_dir = results_dir
        self.repetitions = repetitions
        
        self.experiment_registry = ExperimentRegistry(experiments_dir)
        self.campaign_registry = CampaignRegistry(self.experiment_registry)

    def run_campaign(self, campaign_name: str):
        try:
            experiments = self.campaign_registry.get_campaign_experiments(campaign_name)
        except ValueError as e:
            print(f"Error: {e}")
            return
            
        if not experiments:
            print(f"No experiments found for campaign '{campaign_name}'.")
            return

        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(self.results_dir, f"run_{run_id}")
        
        # Create full output pipeline structure
        for subdir in ["manifest", "evidence", "telemetry", "metrics", "statistics", "plots", "decision", "publication", "provenance"]:
            os.makedirs(os.path.join(run_dir, subdir), exist_ok=True)
            
        print(f"Starting Experiment Campaign: run_{run_id}")
        print(f"Found {len(experiments)} experiments. Repetitions: {self.repetitions}")
        
        for experiment in experiments:
            experiment_id = experiment.schema.id if hasattr(experiment, 'schema') else "unknown_experiment"
            print(f"-> Executing Experiment: {experiment_id}")
            
            try:
                evidence_bundles = []
                # 1. Execution
                from vireon_validation.agency import AgencyValidator
                from vireon_validation.metrics import generate_signal_metrics
                for i in range(self.repetitions):
                    # We pass seed = i to get different noise/attacks per repetition
                    evidence = ExecutionEngine.run(
                        experiment, 
                        seed=i,
                        agency_validator_cls=AgencyValidator,
                        signal_metrics_func=generate_signal_metrics
                    )
                    evidence_bundles.append(evidence)
                    
                # 2. Decision Engine
                # We aggregate measurements across repetitions for decision
                all_measurements = []
                for bundle in evidence_bundles:
                    all_measurements.extend(bundle.measurements)
                    
                # Compute averages for simple decision
                avg_metrics = {}
                count_metrics = {}
                for m in all_measurements:
                    if m.metric_name not in avg_metrics:
                        avg_metrics[m.metric_name] = 0.0
                        count_metrics[m.metric_name] = 0
                    avg_metrics[m.metric_name] += m.value
                    count_metrics[m.metric_name] += 1
                
                # Mock average measurement list
                from vireon_core.contracts import IMeasurement
                avg_measurements = [IMeasurement(metric_name=k, value=v/count_metrics[k], unit="avg") for k, v in avg_metrics.items()]
                
                expected = experiment.schema.expected if hasattr(experiment, 'schema') else {}
                
                # We extract the execution context from the first bundle
                execution_context = evidence_bundles[0].execution_context if evidence_bundles else None
                evidence_quality = EvidenceQualityEngine.evaluate(avg_measurements, expected, execution_context)
                
                from vireon_knowledge.rules import IRule
                rules = []
                for k, v in expected.items():
                    if isinstance(v, str) and ("<" in v or ">" in v or "=" in v):
                        parts = v.strip().split(" ")
                        if len(parts) == 2:
                            op, target = parts
                            metric_name = k
                        elif len(parts) == 3:
                            metric_name, op, target = parts
                        else:
                            continue
                        try:
                            rules.append(IRule(rule_id=f"rule_{k}", description=f"Expected {k} {op} {target}", target_metric=metric_name, operator=op, threshold=float(target)))
                        except ValueError:
                            pass
                    else:
                        rules.append(IRule(rule_id=f"rule_{k}", description=f"Expected {k} == {v}", target_metric=k, operator="==", threshold=v))
                        
                from vireon_core.contracts.base import IEvidence, IExecutionContext
                import hashlib
                exec_hash = hashlib.sha256(f"{experiment_id}_{avg_measurements}".encode()).hexdigest()
                dummy_evidence = IEvidence(
                    experiment_id=experiment_id,
                    execution_hash=exec_hash,
                    execution_context=execution_context or IExecutionContext(environment_fingerprint="env", dependencies={}, hardware_info={}, execution_timestamp=0.0),
                    telemetry_path="",
                    events=[],
                    measurements=avg_measurements,
                    assertions_met={}
                )
                decision = decision_engine.evaluate(dummy_evidence)
                
                # Validation Graph
                validation_graph = {
                    "dataset": "SyntheticSignalProvider",
                    "experiment": experiment_id,
                    "evidence_hashes": [b.execution_hash for b in evidence_bundles],
                    "decision": decision.status == "PASS",
                    "evidence_quality": evidence_quality.overall,
                    "publication": "generated"
                }
                
                for bundle in evidence_bundles:
                    bundle.evidence_quality = evidence_quality
                    bundle.decision = decision # This is now DecisionResult instead of IDecision
                    bundle.validation_graph = validation_graph
                
                # 3. Artifact Generation & Publication
                print(f"   Generating evidence artifacts for {experiment_id}...")
                
                CSVGenerator.generate(evidence_bundles, os.path.join(run_dir, "metrics", f"{experiment_id}.csv"))
                PlotGenerator.generate(evidence_bundles, os.path.join(run_dir, "plots", f"{experiment_id}.png"))
                PaperGenerator.generate(experiment_id, evidence_bundles, os.path.join(run_dir, "publication"))
                ProvenanceGenerator.generate(evidence_bundles, os.path.join(run_dir, "provenance", f"{experiment_id}_provenance.json"))
                
                print(f"   Completed {experiment_id}. Decision: {decision.status}")
                print(f"   Reasoning: {decision.reason}")
                
            except Exception as e:
                print(f"   [ERROR] Failed to run {experiment_id}: {e}")
                
        print(f"Experiment Campaign completed. Results saved to {run_dir}")
