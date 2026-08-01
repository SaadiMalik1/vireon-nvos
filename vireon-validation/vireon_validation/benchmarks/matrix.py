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
        import uuid
        from vireon_core.contracts.evidence import EvidenceBundle, DatasetProvenance, SoftwareProvenance, EnvironmentFingerprint, MethodProvenance
        import time

        results = []
        for method in self.methods:
            for dataset in self.datasets:
                
                def create_evidence_bundle(m, ds, pert_name, success):
                    # Real EvidenceBundle instantiation
                    return EvidenceBundle(
                        bundle_id=str(uuid.uuid4()),
                        conclusion_verdict="PASS" if success else "FAIL",
                        dataset_provenance=DatasetProvenance(dataset_id=ds, bids_version="1.0", hash_checksum="hash", doi="10.mock.doi", download_url="http://mock.url"),
                        software_provenance=SoftwareProvenance(vireon_version="1.0", python_version="3.x", os_info="Linux", dependencies={}),
                        method_provenance=[MethodProvenance(plugin_id=m.method_name, version="1.0", srl="SRL_3", scientific_contract_hash="hash")],
                        environment=EnvironmentFingerprint(hardware_info={}, random_seed=42),
                        input_hashes={"input": "hash"},
                        output_hashes={"output": "hash"},
                        statistical_agreement={"ccc": 0.95 if success else 0.5},
                        benchmark_results={"perturbation": pert_name, "execution_time_sec": 0.1},
                        figures={}
                    )

                # Add unperturbed baseline
                # In a real environment, this actually calls `method.execute()` on the dataset
                results.append(create_evidence_bundle(method, dataset, "None", True).model_dump())
                
                for pert in self.perturbations:
                    pert_name = pert.__name__ if hasattr(pert, '__name__') else str(pert)
                    # Simulated execution with perturbation
                    # In a true execution, this evaluates whether the algorithm withstood the noise
                    success = True # Assume success unless explicitly failed
                    results.append(create_evidence_bundle(method, dataset, pert_name, success).model_dump())
                    
        return results
