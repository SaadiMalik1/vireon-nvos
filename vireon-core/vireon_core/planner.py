from typing import Literal, Tuple, Dict, Any
from vireon_core.specs.experiment import ExperimentSpec
from vireon_core.specs.presets import quick_spec, standard_spec, research_spec

def plan_experiment(
    goal: str,
    dataset_info: Dict[str, Any],
    mode: Literal["quick", "standard", "research"] = "standard",
    constraints: Dict[str, Any] | None = None,
) -> Tuple[ExperimentSpec, str]:
    """Plan an experiment from a natural-language goal + dataset info.
    
    Returns (spec, rationale). Does NOT execute.
    """
    goal_lower = goal.lower()
    
    # 1. Detect experiment type from goal keywords
    is_generalize = "generalize" in goal_lower
    is_robust = "robust" in goal_lower
    
    # 2. Heuristics for method selection
    method = "csp"
    if "welch" in goal_lower or "spectral" in goal_lower:
        method = "welch"
    
    dataset_source = dataset_info.get("source", "unknown_dataset")
    
    # 3. Build spec from template
    if mode == "quick":
        spec = quick_spec(dataset_source, method, goal=goal)
    elif mode == "standard":
        spec = standard_spec(dataset_source, method, goal=goal)
    else:
        spec = research_spec(dataset_source, method, goal=goal)
        
    # 4. Apply rule-driven overrides
    rationale_lines = [f"Selected method '{method}' based on goal and dataset."]
    
    if is_generalize and mode != "quick":
        spec.validation.strategy = "subject_wise"
        rationale_lines.append("Used subject_wise cross-validation to test generalization.")
        
    if is_robust and mode == "standard":
        rationale_lines.append("Upgraded to research mode to enable robustness testing.")
        spec = research_spec(dataset_source, method, goal=goal)
        
    rationale = " ".join(rationale_lines)
    return spec, rationale
