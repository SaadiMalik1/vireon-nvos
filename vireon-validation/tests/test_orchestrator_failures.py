import pytest
from vireon_validation.benchmarks.orchestrator import MassiveCampaignOrchestrator, WorkflowOrchestrator

def test_massive_campaign_failures_logged_is_real():
    campaign_def = {
        "massive_campaign": {
            "methods": ["csp_lda"],
            "workflows": [],
            "datasets": ["eegbci"],
            "perturbations": {"white_noise": [0.1, 0.2]},
            "hardware_profiles": ["fp32"],
            "random_seeds": [42, 43]
        }
    }
    orchestrator = MassiveCampaignOrchestrator(campaign_def)
    result = orchestrator.execute()
    
    assert result["total_factorial_runs"] == 4
    # When no failures occur during execution, failures_logged must be 0, not fabricated 5%
    assert result["failures_logged"] == 0

def test_workflow_orchestrator_execution():
    wf_def = {
        "dataset": {"name": "eegbci"},
        "preprocessing": ["bandpass"],
        "feature_extraction": ["csp"],
        "classifier": ["lda"],
        "evaluation": ["accuracy"],
        "campaign": {"class": "Robustness", "expect_failure": False}
    }
    orch = WorkflowOrchestrator(wf_def)
    res = orch.execute()
    assert res["status"] == "COMPLETED"
    assert res["executed_steps"] == 4
    assert res["campaign_class"] == "Robustness"
