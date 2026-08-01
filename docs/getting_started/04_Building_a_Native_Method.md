# Building a Native Method

To evaluate your custom algorithm in VIREON, you must wrap it in an `IPlugin`. This interface elevates your script into a scientifically sound software object bound by a **Scientific Contract**.

## The Scientific Contract

A standard Python function signature doesn't specify if it assumes wide-sense stationarity or finite variance. The `ScientificContract` forces explicit declaration:

```python
from vireon_core.contracts.plugin import IPlugin, ScientificContract
from vireon_core.contracts.base import ISignal

class MyNovelFilter(IPlugin):
    @property
    def plugin_id(self): return "vk:Method:MyLab:NovelFilter"

    @property
    def contract(self):
        return ScientificContract(
            purpose="Advanced morphological artifact suppression",
            mathematical_assumptions=["Non-Gaussianity", "Time-invariance"],
            supported_modalities=["EEG", "SEEG"],
            validation_papers=["10.1109/TNE.2023.12345"]
        )
        
    def execute(self, inputs):
        signal = inputs.get("signal")
        # Your custom logic here
        return {"features": ISignal(sampling_rate=signal.sampling_rate, data=clean_data)}
```

Once defined, this plugin is immediately executable by the `BenchmarkMatrix`, granting it access to the perturbation suites, the digital twin simulations, and the cryptographic evidence generation.
