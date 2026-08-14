from vireon_core.contracts.base import IEvidence, IMeasurement, IExecutionContext
from vireon_knowledge.rules import FDA_Guidance
from vireon_knowledge.decision_engine import DecisionEngine

def test_decision_engine_evaluation():
    rule1 = FDA_Guidance(
        rule_id="FDA-SNR-001",
        description="SNR must be greater than 10dB",
        target_metric="snr",
        operator=">",
        threshold=10.0,
        guidance_document="FDA-1234",
        section="4.1.2",
        regulatory_reference="FDA-1234 Section 4.1.2"
    )
    
    engine = DecisionEngine(rules=[rule1])
    
    # Passing evidence
    context = IExecutionContext(
        experiment_id="scen-1",
        deterministic_seed=42,
        provider_metadata={},
        version_info="1.0.0",
        environment_fingerprint="env1"
    )
    
    evidence_pass = IEvidence(
        experiment_id="scen-1",
        execution_hash="hash1",
        execution_context=context,
        telemetry_path="path",
        events=[],
        measurements=[IMeasurement(metric_name="snr", value=15.0, unit="dB")],
        assertions_met={}
    )
    
    result_pass = engine.evaluate(evidence_pass)
    assert result_pass.status == "PASS"
    assert len(result_pass.traces) == 1
    assert result_pass.traces[0].status == "PASS"
    assert result_pass.traces[0].regulatory_reference == "FDA-1234 Section 4.1.2"
    
    # Failing evidence
    evidence_fail = IEvidence(
        experiment_id="scen-1",
        execution_hash="hash2",
        execution_context=context,
        telemetry_path="path",
        events=[],
        measurements=[IMeasurement(metric_name="snr", value=5.0, unit="dB")],
        assertions_met={}
    )
    
    result_fail = engine.evaluate(evidence_fail)
    assert result_fail.status == "FAIL"
    assert result_fail.traces[0].status == "FAIL"
    
    # Missing evidence
    evidence_missing = IEvidence(
        experiment_id="scen-1",
        execution_hash="hash3",
        execution_context=context,
        telemetry_path="path",
        events=[],
        measurements=[IMeasurement(metric_name="bandpower", value=100.0, unit="uV2")],
        assertions_met={}
    )
    
    result_missing = engine.evaluate(evidence_missing)
    assert result_missing.status == "FAIL"
    assert result_missing.traces[0].status == "MISSING_DATA"
    assert "snr" in result_missing.missing_evidence
