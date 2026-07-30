import os
import csv
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import List
from vireon_core.contracts.base import IEvidence

class CSVGenerator:
    @staticmethod
    def generate(evidence_bundles: List[IEvidence], out_path: str):
        with open(out_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["repetition", "experiment_id", "metric", "value", "variance"])
            
            for i, bundle in enumerate(evidence_bundles):
                for m in bundle.measurements:
                    writer.writerow([i, bundle.experiment_id, m.metric_name, m.value, m.variance or 0.0])

class PlotGenerator:
    @staticmethod
    def generate(evidence_bundles: List[IEvidence], out_path: str):
        metrics_dict = {}
        
        for bundle in evidence_bundles:
            for m in bundle.measurements:
                if m.metric_name not in metrics_dict:
                    metrics_dict[m.metric_name] = []
                metrics_dict[m.metric_name].append(m.value)
                
        if not metrics_dict:
            return
            
        fig, axes = plt.subplots(len(metrics_dict), 1, figsize=(8, 4 * len(metrics_dict)))
        if len(metrics_dict) == 1:
            axes = [axes]
            
        for ax, (metric_name, values) in zip(axes, metrics_dict.items()):
            ax.plot(values, marker='o')
            ax.set_title(f"{metric_name} over repetitions")
            ax.set_xlabel("Repetition")
            ax.set_ylabel("Value")
            
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close(fig)

class PaperGenerator:
    @staticmethod
    def generate(name: str, evidence_bundles: List[IEvidence], out_dir: str):
        if not evidence_bundles:
            return
            
        bundle = evidence_bundles[0]
        decision = bundle.decision
        
        abstract = f"# Abstract\n\nThis paper presents the empirical validation of the `{name}` experiment. The system achieved a decision of **{'PASS' if decision and decision.passed else 'FAIL'}** with a confidence score of {decision.confidence if decision else 0.0}%."
        methods = f"# Methods\n\n- **Experiment ID**: {bundle.experiment_id}\n- **Repetitions**: {len(evidence_bundles)}"
        
        avg_metrics = {}
        for b in evidence_bundles:
            for m in b.measurements:
                if m.metric_name not in avg_metrics:
                    avg_metrics[m.metric_name] = []
                avg_metrics[m.metric_name].append(m.value)
                
        results = "# Results\n\nAverage Metrics:\n"
        for metric, values in avg_metrics.items():
            mean_val = sum(values) / len(values)
            results += f"- **{metric}**: {mean_val:.4f}\n"
            
        discussion = f"# Discussion\n\n- **Reasoning**: {decision.reasoning if decision else 'N/A'}\n- **Next Steps**: {decision.recommended_next_step if decision else 'N/A'}"
        appendix = "# Appendix\n\n- **Environment Fingerprint**: {bundle.execution_context.environment_fingerprint}"
        
        os.makedirs(os.path.join(out_dir, "paper"), exist_ok=True)
        
        with open(os.path.join(out_dir, "paper", "abstract.md"), "w") as f: f.write(abstract)
        with open(os.path.join(out_dir, "paper", "methods.md"), "w") as f: f.write(methods)
        with open(os.path.join(out_dir, "paper", "results.md"), "w") as f: f.write(results)
        with open(os.path.join(out_dir, "paper", "discussion.md"), "w") as f: f.write(discussion)
        with open(os.path.join(out_dir, "paper", "appendix.md"), "w") as f: f.write(appendix)
        
        # Assemble full paper
        with open(os.path.join(out_dir, "paper.md"), "w") as f:
            f.write(f"{abstract}\n\n{methods}\n\n{results}\n\n{discussion}\n\n{appendix}")

class ProvenanceGenerator:
    @staticmethod
    def generate(evidence_bundles: List[IEvidence], out_path: str):
        if not evidence_bundles:
            return
            
        bundle = evidence_bundles[0]
        ctx = bundle.execution_context
        
        provenance = {
            "experiment_id": ctx.experiment_id,
            "deterministic_seed": ctx.deterministic_seed,
            "version_info": ctx.version_info,
            "environment_fingerprint": ctx.environment_fingerprint,
            "git_sha": ctx.git_sha or "unknown",
            "dependency_versions": ctx.dependency_versions or {},
            "verification_status": "GATEKEEPER_APPROVED",
            "scientific_context": {
                "hypothesis": bundle.hypothesis,
                "experiment_design": bundle.experiment_design,
                "methodology": bundle.methodology,
                "algorithm": bundle.algorithm
            }
        }
        
        # 1. Reproducibility metadata (Provenance)
        with open(out_path, 'w') as f:
            json.dump(provenance, f, indent=4)
            
        # 2. Validation Graph (Provenance)
        if bundle.validation_graph:
            graph_path = os.path.join(os.path.dirname(out_path), f"{bundle.experiment_id}_validation_graph.json")
            with open(graph_path, 'w') as f:
                json.dump(bundle.validation_graph, f, indent=4)
                
        # 3. Evidence Quality
        if hasattr(bundle, 'evidence_quality') and bundle.evidence_quality:
            eq_path = os.path.join(os.path.dirname(out_path), f"{bundle.experiment_id}_evidence_quality.json")
            with open(eq_path, 'w') as f:
                json.dump(bundle.evidence_quality.model_dump(), f, indent=4)

        # 4. Decision
        if hasattr(bundle, 'decision') and bundle.decision:
            dec_path = os.path.join(os.path.dirname(out_path), f"{bundle.experiment_id}_decision.json")
            with open(dec_path, 'w') as f:
                json.dump(bundle.decision.model_dump(), f, indent=4)

        # 5. Manifest (combines context, telemetry path, schema, etc)
        manifest_path = os.path.join(os.path.dirname(out_path), f"{bundle.experiment_id}_manifest.json")
        manifest = {
            "experiment_id": bundle.experiment_id,
            "execution_hash": bundle.execution_hash,
            "schema": bundle.json_ld_schema,
            "telemetry_path": bundle.telemetry_path,
            "assertions_met": bundle.assertions_met
        }
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=4)
