from vireon_moabb.spec import standard_spec
from vireon_moabb.executor import MoabbExecutor
from vireon_moabb.validation import ValidationLayer
from vireon_moabb.evidence import EvidenceAssembler
from vireon_moabb.report import Reporter


import pytest


def test_integration_flow():
    pytest.importorskip("moabb")
    spec = standard_spec(dataset='BNCI2014_001', subject=1, pipeline_name='logvar_lda')
    trace = MoabbExecutor(seed=42).run(spec)
    validation = ValidationLayer().validate(trace, spec)
    bundle = EvidenceAssembler().assemble(spec.model_dump(), trace, validation)
    report = Reporter().generate_scorecard(bundle)
    
    assert trace.mean_accuracy == 0.7495
    assert bundle.evidence_hash == "17d03af85744007bbfd315bfe69fff5af609f5f5c71649ebe9d7beebd2ae08fd"
    assert "Algorithm Compliance Scorecard" in report
