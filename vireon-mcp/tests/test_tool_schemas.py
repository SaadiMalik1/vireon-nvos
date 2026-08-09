import pytest
from vireon_mcp.tools import plan_experiment, validate_experiment

def test_plan_experiment_is_non_executing():
    assert "DOES NOT EXECUTE" in plan_experiment.schema["description"]
    assert plan_experiment.schema.get("safety") == "NON-EXECUTING. Returns a plan only."
    
    import inspect
    src = inspect.getsource(plan_experiment.func)
    assert 'execute' not in src.lower() or 'execution_engine' not in src.lower()

@pytest.mark.asyncio
async def test_validate_experiment_requires_confirm():
    assert "confirm" in validate_experiment.schema["inputSchema"]["required"]
    
    with pytest.raises(ValueError, match="confirm"):
        await validate_experiment.run(experiment_spec={}, confirm=False)
