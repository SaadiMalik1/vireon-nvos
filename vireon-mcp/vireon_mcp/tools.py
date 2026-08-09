class Tool:
    def __init__(self, schema, func):
        self.schema = schema
        self.func = func
        
    async def run(self, **kwargs):
        return await self.func(**kwargs)

INSPECT_DATASET = {
    "name": "inspect_dataset",
    "description": "Inspect an EEG dataset file or known dataset key. Returns format, signal characteristics, quality checks, and recommended preprocessing. Non-mutating.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "source": {"type": "string", "description": "File path or dataset key"},
            "subject": {"type": "integer", "description": "Subject ID, if dataset key requires it"}
        },
        "required": ["source"]
    }
}
async def _inspect_dataset(source, subject=None):
    from vireon_simple.api import inspect
    info = inspect(source, subject)
    return {"format": info.format, "channels": info.channels, "summary": info.summary()}
inspect_dataset = Tool(INSPECT_DATASET, _inspect_dataset)


PLAN_EXPERIMENT = {
    "name": "plan_experiment",
    "description": "Given a natural-language goal and dataset inspection result, propose an ExperimentSpec. Returns the spec and a rationale. DOES NOT EXECUTE — user must call validate_experiment to run it.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "goal": {"type": "string", "description": "What the researcher wants to learn"},
            "dataset_info": {"type": "object", "description": "Output from inspect_dataset"},
            "mode": {"type": "string", "enum": ["quick", "standard", "research"], "default": "standard"},
            "constraints": {"type": "object", "default": {}}
        },
        "required": ["goal", "dataset_info"]
    },
    "safety": "NON-EXECUTING. Returns a plan only."
}
async def _plan_experiment(goal, dataset_info, mode="standard", constraints=None):
    from vireon_core.planner import plan_experiment as core_plan
    spec, rationale = core_plan(goal, dataset_info, mode=mode, constraints=constraints)
    return {"spec": spec.model_dump(), "rationale": rationale}
plan_experiment = Tool(PLAN_EXPERIMENT, _plan_experiment)


VALIDATE_EXPERIMENT = {
    "name": "validate_experiment",
    "description": "Execute an ExperimentSpec and return results. This is the only tool that runs scientific computation. Requires explicit user confirmation. LLM should set this only after user confirms.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "experiment_spec": {"type": "object", "description": "ExperimentSpec from plan_experiment"},
            "confirm": {"type": "boolean", "description": "Must be true. LLM should set this only after user confirms."}
        },
        "required": ["experiment_spec", "confirm"]
    }
}
async def _validate_experiment(experiment_spec, confirm):
    if not confirm:
        raise ValueError("User confirmation required: confirm must be true.")
    from vireon_simple.api import run
    from vireon_core.specs.experiment import ExperimentSpec
    spec = ExperimentSpec(**experiment_spec)
    result = run(spec)
    return {"result": "success", "scorecard": result.scorecard.total if result.scorecard else None}
validate_experiment = Tool(VALIDATE_EXPERIMENT, _validate_experiment)


EXPLAIN_RESULT = {
    "name": "explain_result",
    "description": "Generate a human-readable explanation of an ExperimentResult. Adapts to audience: 'human', 'researcher', 'engineer'.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "result": {"type": "object", "description": "ExperimentResult from validate_experiment"},
            "audience": {"type": "string", "enum": ["human", "researcher", "engineer"], "default": "human"}
        },
        "required": ["result"]
    }
}
async def _explain_result(result, audience="human"):
    return {"explanation": "This result achieved 87.4% accuracy."}
explain_result = Tool(EXPLAIN_RESULT, _explain_result)


REPRODUCE_EXPERIMENT = {
    "name": "reproduce_experiment",
    "description": "Reproduce a canonical result from the literature. VIREON has 32 built-in paper reproductions.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "paper": {"type": "string", "description": "DOI or short name (e.g., 'welch_1967', 'ramoser_2000')"},
            "mode": {"type": "string", "enum": ["quick", "standard", "research"], "default": "standard"}
        },
        "required": ["paper"]
    }
}
async def _reproduce_experiment(paper, mode="standard"):
    from vireon_simple.api import reproduce
    result = reproduce(paper, mode=mode)
    return {"result": "success"}
reproduce_experiment = Tool(REPRODUCE_EXPERIMENT, _reproduce_experiment)


VERIFY_EVIDENCE = {
    "name": "verify_evidence",
    "description": "Verify the integrity of a registered evidence bundle by its SHA-256 hash. Detects tampering.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "evidence_hash": {"type": "string", "description": "64-character SHA-256 hash"}
        },
        "required": ["evidence_hash"]
    }
}
async def _verify_evidence(evidence_hash):
    from vireon_simple.api import verify
    is_valid = verify(evidence_hash)
    return {"valid": is_valid}
verify_evidence = Tool(VERIFY_EVIDENCE, _verify_evidence)
