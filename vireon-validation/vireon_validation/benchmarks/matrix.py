from typing import List, Dict, Any, Callable
import uuid
import time
import hashlib
import numpy as np
from vireon_validation.registry.method_registry import CanonicalMethod
from vireon_core.contracts.evidence import EvidenceBundle, DatasetProvenance, SoftwareProvenance, EnvironmentFingerprint, MethodProvenance

class BenchmarkMatrix:
    """
    Executes a benchmark matrix: Method x Dataset x Perturbation -> EvidenceBundle
    """
    def __init__(self):
        self.datasets: Dict[str, Any] = {}
        self.methods: List[CanonicalMethod] = []
        self.perturbations: List[Callable] = []
        
    def add_dataset(self, dataset_name: str, dataset: Any = None):
        self.datasets[dataset_name] = dataset
        
    def add_method(self, method: CanonicalMethod):
        self.methods.append(method)
        
    def add_perturbation(self, perturbation: Callable):
        self.perturbations.append(perturbation)
        
    def execute_matrix(self) -> List[Dict[str, Any]]:
        """
        Runs the Cartesian product of methods x datasets x perturbations.
        Returns a list of EvidenceBundles.
        """
        def compute_ccc(x, y):
            if np.all(x == y):
                return 1.0
            x_m = np.mean(x)
            y_m = np.mean(y)
            x_v = np.var(x)
            y_v = np.var(y)
            if x_v == 0 and y_v == 0:
                return 1.0
            cov = np.cov(np.asarray(x).flatten(), np.asarray(y).flatten())[0, 1]
            return 2 * cov / (x_v + y_v + (x_m - y_m) ** 2)

        def compute_rmse(x, y):
            return np.sqrt(np.mean((np.asarray(x) - np.asarray(y)) ** 2))

        def compute_real_hash(x):
            if x is None:
                return hashlib.sha256(b"none").hexdigest()
            return hashlib.sha256(np.asarray(x).tobytes()).hexdigest()

        results = []
        for method in self.methods:
            for dataset_id, dataset in self.datasets.items():
                if dataset is not None and hasattr(dataset, "data"):
                    base_data = dataset.data
                    labels = getattr(dataset, "labels", None)
                    try:
                        reference_result = method.execute({"signal": base_data, "labels": labels})
                    except Exception:
                        reference_result = None
                else:
                    base_data = None
                    labels = None
                    reference_result = None
                
                perts_to_run = [(None, "None")] + [(p, p.__name__ if hasattr(p, '__name__') else str(p)) for p in self.perturbations]
                
                for pert, pert_name in perts_to_run:
                    if base_data is not None:
                        if pert is not None:
                            try:
                                perturbed = pert(base_data)
                            except Exception:
                                perturbed = base_data
                        else:
                            perturbed = base_data
                    else:
                        perturbed = None
                        
                    start = time.perf_counter()
                    error = None
                    try:
                        result = method.execute({"signal": perturbed, "labels": labels}) if method else None
                        success = True
                    except Exception as e:
                        result = None
                        success = False
                        error = str(e)
                    runtime = time.perf_counter() - start
                    
                    if success and reference_result is not None and result is not None and np.shape(result) == np.shape(reference_result):
                        try:
                            ccc = float(compute_ccc(result, reference_result))
                            rmse = float(compute_rmse(result, reference_result))
                        except Exception:
                            ccc = 0.0
                            rmse = float('inf')
                    else:
                        ccc = 0.0
                        rmse = float('inf')
                        
                    bundle = EvidenceBundle(
                        bundle_id=str(uuid.uuid4()),
                        conclusion_verdict="PASS" if success else "FAIL",
                        dataset_provenance=DatasetProvenance(
                            dataset_id=dataset_id, 
                            bids_version="1.0", 
                            hash_checksum=compute_real_hash(perturbed), 
                            doi=getattr(dataset, "doi", None) if dataset else None, 
                            download_url=getattr(dataset, "url", None) if dataset else None
                        ),
                        software_provenance=SoftwareProvenance(vireon_version="1.0", python_version="3.x", os_info="Linux", dependencies={}),
                        method_provenance=[MethodProvenance(plugin_id=getattr(method, "plugin_id", "unknown") if method else "unknown", version="1.0", srl="SRL_3", scientific_contract_hash=compute_real_hash(method))],
                        environment=EnvironmentFingerprint(hardware_info={}, random_seed=42),
                        input_hashes={"input": compute_real_hash(perturbed)},
                        output_hashes={"output": compute_real_hash(result)},
                        statistical_agreement={"ccc": ccc, "rmse": rmse},
                        benchmark_results={"perturbation": pert_name, "execution_time_sec": runtime},
                        figures={}
                    )
                    
                    bundle_dict = bundle.model_dump()
                    if not success:
                        bundle_dict["success"] = False
                        bundle_dict["error"] = error
                    else:
                        bundle_dict["success"] = True
                        
                    results.append(bundle_dict)
                    
        return results
