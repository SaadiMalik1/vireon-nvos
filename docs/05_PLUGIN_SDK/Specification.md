# Plugin SDK Specification

## 1. Interface Definition
All VIREON plugins must inherit from `vireon_core.contracts.plugin.IPlugin`.

### Required Methods
- `capabilities()`: Returns a list of `PluginCapability` defining inputs and outputs.
- `contract()`: Returns a `ScientificContract` defining bounds, assumptions, and literature backing.
- `execute(inputs: Dict[str, IScientificObject]) -> Dict[str, IScientificObject]`: The main transformation logic.

## 2. Scientific Readiness Levels (SRL)
Plugins must self-declare their SRL in their contract:
- **SRL 0-3**: Proof of concept, toy models.
- **SRL 4-6**: Validation against synthetic and small-scale empirical datasets.
- **SRL 7-8**: Large-scale empirical validation across populations.
- **SRL 9**: Regulatory Grade (matches FDA Software Precertification standards).

## 3. The `IScientificObject` Envelope
Data is never passed as raw arrays. It is always wrapped in an `IScientificObject` which tracks:
- `provenance_id`
- `sampling_rate`
- `unit_of_measure`
- `uncertainty_bounds`

Failure to propagate these metadata fields correctly during `execute` will cause the Evidence Engine to reject the plugin's output.


## Phase E Implementation Status
> [!NOTE]
