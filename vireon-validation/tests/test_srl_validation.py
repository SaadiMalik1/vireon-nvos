from vireon_validation.srl_automation import validate_srl_claim
from vireon_core.contracts.plugin import ScientificReadinessLevel, ScientificContract

class MockPlugin:
    def __init__(self, srl, contract):
        self._srl = srl
        self._contract = contract
        
    @property
    def srl(self) -> ScientificReadinessLevel:
        return self._srl
        
    @property
    def contract(self) -> ScientificContract:
        return self._contract

def test_validate_srl_claim_violations():
    # Test SRL_5 without evidence
    contract = ScientificContract()
    plugin = MockPlugin(ScientificReadinessLevel.SRL_5, contract)
    
    violations = validate_srl_claim(plugin)
    
    assert len(violations) == 3
    assert "SRL_4+ requires validation_papers" in violations
    assert "SRL_4+ requires expected_numerical_tolerances" in violations
    assert "SRL_5 requires independent reproduction evidence" in violations
    
    # Test SRL_1 without evidence (should have no violations)
    plugin_srl1 = MockPlugin(ScientificReadinessLevel.SRL_1, contract)
    violations_srl1 = validate_srl_claim(plugin_srl1)
    
    assert len(violations_srl1) == 0
