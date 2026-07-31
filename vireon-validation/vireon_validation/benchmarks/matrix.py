from typing import List, Dict, Any, Callable
from vireon_validation.registry.method_registry import CanonicalMethod

class BenchmarkMatrix:
    """
    Executes a benchmark matrix: Method x Dataset x Perturbation -> EvidenceBundle
    """
    def __init__(self):
        self.datasets: List[str] = []
        self.methods: List[CanonicalMethod] = []
        self.perturbations: List[Callable] = []
        
    def add_dataset(self, dataset_name: str):
        self.datasets.append(dataset_name)
        
    def add_method(self, method: CanonicalMethod):
        self.methods.append(method)
        
    def add_perturbation(self, perturbation: Callable):
        self.perturbations.append(perturbation)
        
    def execute_matrix(self) -> List[Dict[str, Any]]:
        """
        Runs the Cartesian product of methods x datasets x perturbations.
        Returns a list of EvidenceBundles (stubbed).
        """
        results = []
        for method in self.methods:
            for dataset in self.datasets:
                # Add unperturbed baseline
                results.append({
                    "method": method.method_name,
                    "dataset": dataset,
                    "perturbation": "None",
                    "status": "COMPLETED"
                })
                for pert in self.perturbations:
                    pert_name = pert.__name__ if hasattr(pert, '__name__') else str(pert)
                    results.append({
                        "method": method.method_name,
                        "dataset": dataset,
                        "perturbation": pert_name,
                        "status": "COMPLETED"
                    })
        return results
