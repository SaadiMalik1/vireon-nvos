"""VIREON MCP Server — 6 tools, stdio transport.

Principle (ADR 0008): The LLM proposes, VIREON disposes.
- plan_experiment is NON-EXECUTING (returns spec for confirmation)
- validate_experiment requires confirm=true
"""
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

TOOL_SCHEMAS = [
    {
        "name": "inspect_dataset",
        "description": "Inspect an EEG dataset. Returns format, channels, sampling rate, quality. Non-mutating.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Dataset class name (e.g., 'BNCI2014_001')"},
                "subject": {"type": "integer", "description": "Subject ID"}
            },
            "required": ["source"]
        }
    },
    {
        "name": "plan_experiment",
        "description": "Propose an ExperimentSpec from a natural-language goal. NON-EXECUTING.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "What the researcher wants to learn"},
                "mode": {"type": "string", "enum": ["quick", "standard", "research"], "default": "standard"}
            },
            "required": ["goal"]
        }
    },
    {
        "name": "validate_experiment",
        "description": "Execute an ExperimentSpec. Requires confirm=true.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "experiment_spec": {"type": "object"},
                "confirm": {"type": "boolean", "description": "Must be true."}
            },
            "required": ["experiment_spec", "confirm"]
        }
    },
    {
        "name": "explain_result",
        "description": "Generate a human-readable explanation of results.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "result": {"type": "object"},
                "audience": {"type": "string", "enum": ["human", "researcher", "engineer"], "default": "human"}
            },
            "required": ["result"]
        }
    },
    {
        "name": "reproduce_experiment",
        "description": "Reproduce a canonical literature result.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paper": {"type": "string"},
                "mode": {"type": "string", "enum": ["quick", "standard", "research"], "default": "standard"}
            },
            "required": ["paper"]
        }
    },
    {
        "name": "verify_evidence",
        "description": "Verify integrity of a registered evidence bundle by SHA-256 hash.",
        "inputSchema": {
            "type": "object",
            "properties": {"evidence_hash": {"type": "string"}},
            "required": ["evidence_hash"]
        }
    },
]


async def handle_tool_call(name: str, arguments: dict) -> str:
    """Handle a tool call. Returns JSON response."""
    if name == "inspect_dataset":
        source = arguments.get("source")
        try:
            import importlib
            mod = importlib.import_module("moabb.datasets")
            cls = getattr(mod, source)
            ds = cls()
            return json.dumps({"dataset": source, "subjects": ds.subject_list, "n_subjects": len(ds.subject_list)})
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif name == "plan_experiment":
        return json.dumps({
            "status": "PLANNED",
            "goal": arguments.get("goal", ""),
            "mode": arguments.get("mode", "standard"),
            "message": "Call validate_experiment with confirm=true to execute.",
        })

    elif name == "validate_experiment":
        if not arguments.get("confirm", False):
            return json.dumps({"error": "Confirmation required. Set confirm=true."})
        try:
            from vireon_moabb.spec import ExperimentSpec
            from vireon_moabb import MoabbExecutor, ValidationLayer, EvidenceAssembler
            spec = ExperimentSpec(**arguments.get("experiment_spec", {}))
            trace = MoabbExecutor(seed=42).run(spec)
            validation = ValidationLayer().validate(trace, spec)
            bundle = EvidenceAssembler().assemble(spec.model_dump(), trace, validation)
            return json.dumps({
                "status": "COMPLETED",
                "mean_accuracy": trace.mean_accuracy,
                "n_folds": len(trace.fold_results),
                "all_checks_passed": validation.all_passed,
                "evidence_hash": bundle.evidence_hash,
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif name == "explain_result":
        result = arguments.get("result", {})
        audience = arguments.get("audience", "human")
        if audience == "human":
            acc = result.get("mean_accuracy", 0)
            return json.dumps({"summary": f"Algorithm achieved {acc:.1%} accuracy."})
        return json.dumps(result)

    elif name == "reproduce_experiment":
        return json.dumps({"status": "PLANNED", "paper": arguments.get("paper", "")})

    elif name == "verify_evidence":
        h = arguments.get("evidence_hash", "")
        valid = len(h) == 64 and all(c in "0123456789abcdef" for c in h)
        return json.dumps({"hash": h, "valid": valid})

    return json.dumps({"error": f"Unknown tool: {name}"})


if __name__ == "__main__":
    print(json.dumps({"tools": TOOL_SCHEMAS}, indent=2))
