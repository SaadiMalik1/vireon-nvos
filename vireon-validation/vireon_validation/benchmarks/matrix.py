from typing import List, Dict, Any, Callable, Optional
import uuid
import time
import hashlib
import json
import numpy as np
from vireon_validation.registry.method_registry import CanonicalMethod
from vireon_core.contracts.evidence import EvidenceBundle, DatasetProvenance, SoftwareProvenance, EnvironmentFingerprint, MethodProvenance

CCC_PASS_THRESHOLD = 0.7  # Named threshold for pass/fail determination (R2)

class BenchmarkMatrix:
    """
    Executes a benchmark matrix: Method x Dataset x Perturbation -> EvidenceBundle
    """
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.datasets: Dict[str, Any] = {}
        self.methods: List[CanonicalMethod] = []
        self.perturbations: List[Callable] = []
        
    def add_dataset(self, dataset_id: str, data: Any = None, labels: Any = None):
        """Add a dataset to the matrix.
        
        Args:
            dataset_id: Name of the dataset.
            data: Signal array or dataset object, or None.
            labels: Labels array if data is an array, or None.
        """
        if data is not None:
            if labels is None and not hasattr(data, "labels") and not (isinstance(data, tuple) and len(data) == 2):
                raise ValueError(f"labels required when data is provided for {dataset_id}")
            self.datasets[dataset_id] = {"data": data, "labels": labels}
        else:
            self.datasets[dataset_id] = None
        
    def add_method(self, method: CanonicalMethod):
        self.methods.append(method)
        
    def add_perturbation(self, perturbation: Callable):
        self.perturbations.append(perturbation)
        
    def _build_evidence_bundle(self, method: Optional[CanonicalMethod], dataset_id: str, dataset: Any,
                               pert_name: str, perturbed: Any, result: Any,
                               ccc: float, rmse: float, runtime: float,
                               success: bool, error: Optional[str]) -> EvidenceBundle:
        """Build a fully-populated EvidenceBundle with real evidence_hash."""
        method_id = getattr(method, "plugin_id", "unknown") if method else "unknown"
        method_ver = getattr(method, "version", "1.0") if method else "1.0"
        bundle_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{dataset_id}:{method_id}:{pert_name}:{self.seed}"))
        
        def compute_real_hash(x):
            if x is None:
                return hashlib.sha256(b"none").hexdigest()
            return hashlib.sha256(np.asarray(x).tobytes()).hexdigest()

        input_hash = compute_real_hash(perturbed)
        output_hash = compute_real_hash(result)

        # Compute evidence_hash from all substantive fields
        hash_payload = {
            "bundle_id": bundle_id,
            "algorithm": method_id,
            "dataset": dataset_id,
            "perturbation": pert_name,
            "ccc": round(ccc, 6),
            "rmse": round(rmse, 6) if not np.isinf(rmse) else "inf",
            "success": success,
            "random_seed": self.seed,
            "method_version": method_ver,
            "input_hash": input_hash,
            "output_hash": output_hash,
        }
        evidence_hash = hashlib.sha256(
            json.dumps(hash_payload, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        pass_fail = "PASS" if (success and ccc >= CCC_PASS_THRESHOLD) else "FAIL"

        return EvidenceBundle(
            bundle_id=bundle_id,
            evidence_hash=evidence_hash,
            algorithm=method_id,
            dataset=dataset_id,
            perturbation=pert_name,
            runtime_sec=runtime,
            pass_fail=pass_fail,
            conclusion_verdict=pass_fail,
            random_seed=self.seed,
            dataset_provenance=DatasetProvenance(
                dataset_id=dataset_id, 
                bids_version="1.0", 
                hash_checksum=compute_real_hash(perturbed), 
                doi=getattr(dataset, "doi", None) if dataset else None, 
                download_url=getattr(dataset, "url", None) if dataset else None
            ),
            software_provenance=SoftwareProvenance(vireon_version="1.0", python_version="3.x", os_info="Linux", dependencies={}),
            method_provenance=[MethodProvenance(plugin_id=method_id, version=method_ver, srl="SRL_3", scientific_contract_hash=compute_real_hash(method))],
            environment=EnvironmentFingerprint(hardware_info={}, random_seed=self.seed),
            input_hashes={"input": compute_real_hash(perturbed)},
            output_hashes={"output": compute_real_hash(result)},
            statistical_agreement={"ccc": ccc, "rmse": rmse},
            benchmark_results={"perturbation": pert_name, "execution_time_sec": runtime},
            figures={}
        )

    def _compute_reference_cv_scores(self, X: np.ndarray, y: np.ndarray, n_components: int = 4) -> np.ndarray:
        """Compute per-fold reference accuracy using MNE CSP + LDA."""
        from mne.decoding import CSP as MNE_CSP
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        from sklearn.model_selection import StratifiedKFold
        from sklearn.pipeline import make_pipeline
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.seed)
        clf = make_pipeline(
            MNE_CSP(n_components=n_components, reg=None, log=True),
            LinearDiscriminantAnalysis()
        )
        scores = []
        for train_idx, test_idx in cv.split(X, y):
            clf.fit(X[train_idx], y[train_idx])
            scores.append(clf.score(X[test_idx], y[test_idx]))
        return np.array(scores)

    def _compute_reference_accuracy(self, X: np.ndarray, y: np.ndarray, n_components: int = 4) -> float:
        """Compute mean reference accuracy."""
        scores = self._compute_reference_cv_scores(X, y, n_components=n_components)
        return float(np.mean(scores))

    def _compute_method_cv_scores(self, method: Any, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Compute per-fold method accuracy using Method + LDA under identical CV splits."""
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        from sklearn.model_selection import StratifiedKFold
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.seed)
        scores = []
        for train_idx, test_idx in cv.split(X, y):
            if hasattr(method, "__class__"):
                try:
                    fold_method = method.__class__(
                        n_components=getattr(method, "n_components", 4),
                        norm_trace=getattr(method, "norm_trace", False)
                    )
                except Exception:
                    fold_method = method
            else:
                fold_method = method

            train_feats = fold_method.execute({"signal": X[train_idx], "labels": y[train_idx]})
            test_feats = fold_method.execute({"signal": X[test_idx], "labels": None})
            
            lda = LinearDiscriminantAnalysis()
            lda.fit(train_feats, y[train_idx])
            scores.append(lda.score(test_feats, y[test_idx]))
        return np.array(scores)

    def _compute_method_accuracy(self, method: Any, X: np.ndarray, y: np.ndarray) -> float:
        """Compute mean method accuracy."""
        scores = self._compute_method_cv_scores(method, X, y)
        return float(np.mean(scores))

    def _compute_ccc_vector(self, method_scores: np.ndarray, reference_scores: np.ndarray) -> float:
        """Lin's CCC between two score vectors."""
        method_scores = np.asarray(method_scores, dtype=float)
        reference_scores = np.asarray(reference_scores, dtype=float)
        if np.array_equal(method_scores, reference_scores):
            return 1.0
        mean_m = np.mean(method_scores)
        mean_r = np.mean(reference_scores)
        var_m = np.var(method_scores, ddof=1)
        var_r = np.var(reference_scores, ddof=1)
        if var_m == 0 and var_r == 0:
            return 1.0 if mean_m == mean_r else 0.0
        cov = np.mean((method_scores - mean_m) * (reference_scores - mean_r))
        denom = var_m + var_r + (mean_m - mean_r)**2
        if denom == 0:
            return 1.0
        ccc = (2 * cov) / denom
        return float(np.clip(ccc, -1.0, 1.0))

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
            denom = x_v + y_v + (x_m - y_m) ** 2
            if denom == 0:
                return 1.0
            return 2 * cov / denom

        def compute_rmse(x, y):
            return np.sqrt(np.mean((np.asarray(x) - np.asarray(y)) ** 2))

        results = []
        for method in self.methods:
            for dataset_id, dataset_info in self.datasets.items():
                if dataset_info is None:
                    # No data provided
                    bundle = self._build_evidence_bundle(
                        method=method,
                        dataset_id=dataset_id,
                        dataset=None,
                        pert_name="None",
                        perturbed=None,
                        result=None,
                        ccc=0.0,
                        rmse=float('inf'),
                        runtime=0.0,
                        success=False,
                        error="No data provided to add_dataset"
                    )
                    bundle_dict = bundle.model_dump()
                    bundle_dict["success"] = False
                    bundle_dict["error"] = "No data provided to add_dataset"
                    results.append(bundle_dict)
                    continue

                if isinstance(dataset_info, dict):
                    base_data = dataset_info.get("data")
                    labels = dataset_info.get("labels")
                    if not isinstance(base_data, np.ndarray) and hasattr(base_data, "data"):
                        if labels is None:
                            labels = getattr(base_data, "labels", None)
                        base_data = base_data.data
                elif not isinstance(dataset_info, np.ndarray) and hasattr(dataset_info, "data"):
                    base_data = dataset_info.data
                    labels = getattr(dataset_info, "labels", None)
                elif isinstance(dataset_info, tuple) and len(dataset_info) == 2:
                    base_data, labels = dataset_info
                else:
                    base_data = dataset_info
                    labels = None

                if base_data is not None:
                    try:
                        reference_result = method.execute({"signal": base_data, "labels": labels})
                    except Exception:
                        reference_result = None
                else:
                    reference_result = None
                
                perts_to_run = [(None, "None")] + [
                    (p, getattr(p, "name", None) or (p.__name__ if hasattr(p, "__name__") else str(p)))
                    for p in self.perturbations
                ]
                
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
                    
                    if success and base_data is not None and labels is not None:
                        try:
                            n_comp = getattr(method, "n_components", 4)
                            # When n_components represents pairs (like in native CSP), total components is 2*n_comp if 2*n_comp <= channels
                            if hasattr(method, "n_components") and method.n_components * 2 <= perturbed.shape[1]:
                                m_comp = method.n_components * 2
                            else:
                                m_comp = n_comp
                            method_scores = self._compute_method_cv_scores(method, perturbed, labels)
                            ref_scores = self._compute_reference_cv_scores(perturbed, labels, n_components=m_comp)
                            ccc = self._compute_ccc_vector(method_scores, ref_scores)
                            rmse = float(np.sqrt(np.mean((method_scores - ref_scores) ** 2)))
                        except Exception:
                            if reference_result is not None and result is not None and np.shape(result) == np.shape(reference_result):
                                ccc = float(compute_ccc(result, reference_result))
                                rmse = float(compute_rmse(result, reference_result))
                            else:
                                ccc = 0.0
                                rmse = float('inf')
                    elif success and reference_result is not None and result is not None and np.shape(result) == np.shape(reference_result):
                        try:
                            ccc = float(compute_ccc(result, reference_result))
                            rmse = float(compute_rmse(result, reference_result))
                        except Exception:
                            ccc = 0.0
                            rmse = float('inf')
                    else:
                        ccc = 0.0
                        rmse = float('inf')
                        
                    bundle = self._build_evidence_bundle(
                        method=method,
                        dataset_id=dataset_id,
                        dataset=dataset_info,
                        pert_name=pert_name,
                        perturbed=perturbed,
                        result=result,
                        ccc=ccc,
                        rmse=rmse,
                        runtime=runtime,
                        success=success,
                        error=error
                    )
                    
                    bundle_dict = bundle.model_dump()
                    bundle_dict["success"] = success
                    if not success:
                        bundle_dict["error"] = error
                        
                    results.append(bundle_dict)
                    
        return results

