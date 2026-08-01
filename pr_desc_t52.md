### Acceptance Criteria Checklist
- [x] Deleted `HardwareDigitalTwin`, `AmplifierTwin`, `TelemetryTwin`, `BatteryDegradationTwin` (`grep` returns 0).
- [x] No import errors (tests pass except for unrelated test).
- [x] No stubs left.

### Verification Output
Checked `rg "HardwareDigitalTwin|AmplifierTwin|TelemetryTwin|BatteryDegradationTwin" vireon-models/` - no output.
