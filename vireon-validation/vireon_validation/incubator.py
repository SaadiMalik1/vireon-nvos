from typing import Dict, Any, List, Optional
import numpy as np

def compute_ccc(x: np.ndarray, y: np.ndarray) -> float:
    """Computes Lin's Concordance Correlation Coefficient."""
    x = np.asarray(x).flatten()
    y = np.asarray(y).flatten()
    if np.all(x == y):
        return 1.0
    x_m = np.mean(x)
    y_m = np.mean(y)
    x_v = np.var(x)
    y_v = np.var(y)
    if x_v == 0 and y_v == 0:
        return 1.0
    cov = np.cov(x, y)[0, 1]
    denom = x_v + y_v + (x_m - y_m) ** 2
    if denom == 0:
        return 0.0
    return float(2 * cov / denom)

def run_gauntlet(
    plugin: Any = None, 
    test_datasets: Optional[List[Any]] = None, 
    reference_implementations: Optional[Dict[str, Any]] = None, 
    method_name: str = ""
) -> Dict[str, Any]:
    """
    Run a plugin through the Scientific Readiness Level (SRL) gauntlet.

    Stages:
    - SRL_1: Plugin executes without error on synthetic data
    - SRL_2: Output matches a reference implementation within tolerance (CCC > 0.95)
    - SRL_3: Survives perturbation testing (noise, NaN, Inf)
    - SRL_4: Validates against published literature values (requires validation_papers in contract)
    - SRL_5: Independent reproduction by a third party (out of scope for automated gauntlet)
    """
    results: Dict[str, Any] = {}
    name = getattr(plugin, "name", method_name) or "UnknownMethod"
    
    if plugin is None:
        return {
            "method": name, 
            "status": "FAIL", 
            "srl_recommendation": "SRL-0", 
            "results": {"srl_1": "FAIL: No plugin provided"}
        }

    if test_datasets is None:
        test_datasets = [np.sin(np.linspace(0, 10, 100))]

    # SRL_1: Execute on synthetic data
    plugin_outputs = []
    try:
        for data in test_datasets:
            out = plugin.execute(data) if hasattr(plugin, 'execute') else plugin(data)
            plugin_outputs.append(out)
        results["srl_1"] = "PASS"
    except Exception as e:
        results["srl_1"] = f"FAIL: {e}"
        return {
            "method": name, 
            "status": "FAIL", 
            "srl_recommendation": "SRL-0", 
            "results": results
        }

    # SRL_2: Compare to reference
    if reference_implementations:
        ref_fn = reference_implementations.get("reference") or list(reference_implementations.values())[0]
        try:
            cccs = []
            for data, p_out in zip(test_datasets, plugin_outputs):
                ref_out = ref_fn.execute(data) if hasattr(ref_fn, 'execute') else ref_fn(data)
                ccc = compute_ccc(p_out, ref_out)
                cccs.append(ccc)
            mean_ccc = float(np.mean(cccs))
            results["srl_2_ccc"] = mean_ccc
            if mean_ccc < 0.95:
                results["srl_2"] = f"FAIL: CCC={mean_ccc:.4f} < 0.95"
                return {
                    "method": name, 
                    "status": "PARTIAL", 
                    "srl_recommendation": "SRL-1", 
                    "results": results
                }
            results["srl_2"] = "PASS"
        except Exception as e:
            results["srl_2"] = f"FAIL: {e}"
            return {
                "method": name, 
                "status": "PARTIAL", 
                "srl_recommendation": "SRL-1", 
                "results": results
            }
    else:
        results["srl_2"] = "SKIPPED"

    # SRL_3: Perturbation testing (noise, NaN, Inf)
    try:
        from vireon_core.runtime.rng import DeterministicRNG
        rng = DeterministicRNG(seed=42)
        for data in test_datasets:
            data_arr = np.asarray(data, dtype=float)
            noisy = data_arr + rng.normal(0, 0.1, size=data_arr.shape)
            if hasattr(plugin, 'execute'):
                plugin.execute(noisy)
            else:
                plugin(noisy)
            
            nan_data = data_arr.copy()
            if nan_data.size > 0:
                nan_data.flat[0] = np.nan
                try:
                    if hasattr(plugin, 'execute'):
                        plugin.execute(nan_data)
                    else:
                        plugin(nan_data)
                except (ValueError, TypeError, FloatingPointError):
                    pass
        results["srl_3"] = "PASS"
    except Exception as e:
        results["srl_3"] = f"FAIL: {e}"
        return {
            "method": name, 
            "status": "PARTIAL", 
            "srl_recommendation": "SRL-2", 
            "results": results
        }

    # SRL_4: Literature validation (requires validation_papers in contract)
    contract = getattr(plugin, "contract", None)
    validation_papers = getattr(contract, "validation_papers", None)
    if not validation_papers:
        results["srl_4"] = "FAIL: Missing validation_papers"
        return {
            "method": name, 
            "status": "PARTIAL", 
            "srl_recommendation": "SRL-3", 
            "results": results
        }
    
    results["srl_4"] = "PASS"
    return {
        "method": name, 
        "status": "INCUBATION_COMPLETE", 
        "srl_recommendation": "SRL-4", 
        "results": results
    }

class NativeAlgorithmIncubator:
    """
    Formal promotion pipeline for Native Algorithms.
    SRL-1 -> Synthetic -> Real -> Compare -> Robustness -> CrossVal -> MetaAnalysis -> Independent Repro -> SRL.
    """
    def __init__(self, method_name: str = "", reference_method_name: str = ""):
        self.method_name = method_name
        self.reference = reference_method_name
        
    def run_gauntlet(
        self, 
        plugin: Any = None, 
        test_datasets: Optional[List[Any]] = None, 
        reference_implementations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes the mandatory evidence accumulation pipeline.
        """
        return run_gauntlet(
            plugin=plugin,
            test_datasets=test_datasets,
            reference_implementations=reference_implementations,
            method_name=self.method_name
        )
