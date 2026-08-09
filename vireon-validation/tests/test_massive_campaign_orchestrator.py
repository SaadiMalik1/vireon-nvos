import pytest
from vireon_validation.benchmarks.orchestrator import MassiveCampaignOrchestrator
from vireon_evidence.registry.core import EvidenceRegistry
from vireon_evidence.registry.failure_atlas import FailureAtlas


def test_massive_campaign_orchestrator():
    yaml_config = """
    massive_campaign:
      methods: ["VireonWelch", "VireonSTFT"]
      datasets: ["physionet_bci"]
      perturbations:
        white_noise: [0.1, 0.5]
      hardware_profiles: ["cpu"]
      random_seeds: [42, 43]
    """
    registry = EvidenceRegistry(db_path=":memory:")
    atlas = FailureAtlas(db_path=":memory:")
    orchestrator = MassiveCampaignOrchestrator.from_yaml(yaml_config, registry=registry, failure_atlas=atlas)

    res = orchestrator.execute()
    assert res["status"] == "MASSIVE_CAMPAIGN_COMPLETED"
    # 2 methods * 1 dataset * 2 severities * 1 hw * 2 seeds = 8 runs
    assert res["total_factorial_runs"] == 8
    assert len(res["evidence_hashes"]) == 8
    assert res["failures_logged"] == 0
