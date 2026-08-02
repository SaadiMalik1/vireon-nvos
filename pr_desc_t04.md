### Acceptance Criteria Checklist
- [x] NaN input raises ScientificContractViolation.
- [x] Inf input raises.
- [x] Short signal (< nperseg) raises.
- [x] Non-stationary signal raises (when stationarity assumed).
- [x] Valid input does not raise.
- [x] ExecutionEngine logs CONTRACT_VIOLATION event and continues (no crash).
- [x] rg "raise ScientificContractViolation" returns >= 3 matches.
- [x] pytest passes with coverage >= 80%.

### Verification Output
```
Required test coverage of 80% reached. Total coverage: 83.05%
============================== 6 passed in 0.33s ===============================
vireon-core/vireon_core/contracts/plugin.py
74:                raise ScientificContractViolation(
81:                raise ScientificContractViolation(
93:                        raise ScientificContractViolation(
117:                        raise ScientificContractViolation(
129:                        raise ScientificContractViolation(
99:                        from vireon_core.contracts.plugin import ContractValidator, ScientificContractViolation
102:                        except ScientificContractViolation as e:
```
