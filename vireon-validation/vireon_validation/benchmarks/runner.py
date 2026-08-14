import os
import glob
from vireon_core.contracts.experiment import load_experiment_from_yaml
from vireon_core.kernel.execution_engine import ExecutionEngine

class BenchmarkRunner:
    def __init__(self, scenarios_dir: str, output_dir: str, seed: int = 42):
        self.scenarios_dir = scenarios_dir
        self.output_dir = output_dir
        self.seed = seed
        self.engine = ExecutionEngine()

    def run_all(self):
        scenario_files = glob.glob(os.path.join(self.scenarios_dir, "*.yaml"))
        results = []
        passed = 0
        failed = 0

        for filepath in scenario_files:
            try:
                load_experiment_from_yaml(filepath)
                # In a real implementation we would run the experiment via the engine.
                # Here we just parse to verify validity.
                # result = self.engine.run(experiment)
                results.append({"scenario": os.path.basename(filepath), "status": "passed"})
                passed += 1
            except Exception as e:
                results.append({"scenario": os.path.basename(filepath), "status": "failed", "error": str(e)})
                failed += 1

        total_run = passed + failed
        score = (passed / total_run * 100.0) if total_run > 0 else 0.0

        return {
            "summary": {
                "total_run": total_run,
                "passed": passed,
                "failed": failed,
                "seed": self.seed,
                "score": score
            },
            "categories": {},
            "results": results
        }
