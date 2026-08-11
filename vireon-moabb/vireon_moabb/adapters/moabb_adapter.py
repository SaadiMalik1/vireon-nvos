from vireon_moabb.adapters.base import BaseAdapter, AdapterResult
from vireon_moabb.executor import MoabbExecutor
from vireon_moabb.spec import ExperimentSpec
import hashlib, json


class MoabbAdapter(BaseAdapter):
    """Adapter for MOABB BCI benchmarks."""

    @property
    def name(self) -> str:
        return "moabb"

    @property
    def library_version(self) -> str:
        try:
            import moabb
            return moabb.__version__
        except ImportError:
            return "unknown"

    def can_handle(self, spec: dict) -> bool:
        """Check if spec is a MOABB experiment."""
        return all(k in spec for k in ["dataset", "paradigm", "pipeline", "evaluation"])

    def execute(self, spec: dict, **kwargs) -> AdapterResult:
        """Execute a MOABB benchmark.

        Args:
            spec: ExperimentSpec as dict.

        Returns:
            AdapterResult with execution trace.
        """
        experiment_spec = ExperimentSpec.model_validate(spec)
        executor = MoabbExecutor(seed=kwargs.get("seed", 42))
        trace = executor.run(experiment_spec)

        # Compute execution hash
        trace_dict = trace.to_dict()
        hash_content = json.dumps(trace_dict, sort_keys=True, default=str)
        exec_hash = hashlib.sha256(hash_content.encode()).hexdigest()

        return AdapterResult(
            outputs=trace,
            metadata={
                "n_folds": len(trace.fold_results),
                "mean_accuracy": trace.mean_accuracy,
                "n_subjects": trace.dataset_metadata.n_subjects,
            },
            execution_hash=exec_hash,
            adapter_name=self.name,
        )
