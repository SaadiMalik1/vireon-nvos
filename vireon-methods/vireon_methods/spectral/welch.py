from vireon_core.contracts.plugin import IPlugin, PluginCapability, ScientificContract

class WelchPSDPlugin(IPlugin):
    @property
    def capabilities(self):
        return [PluginCapability(id="spectral_estimation.welch", version="1.0.0", consumes=["ISignal"], produces=["ISignal"])]
    
    @property
    def contract(self):
        return ScientificContract(
            purpose="Estimate PSD via Welch's Method",
            mathematical_assumptions=["Wide-Sense Stationarity", "Ergodicity"],
            supported_modalities=["EEG", "ECOG"],
            validation_papers=["10.1109/TAU.1967.1161901"]
        )

    def execute(self, inputs):
        from vireon_core.contracts.base import ISignal
        import numpy as np
        from scipy.signal import welch
        
        signal = inputs.get("signal")
        if not isinstance(signal, ISignal):
            raise ValueError("Expected ISignal as 'signal' input")
            
        X = signal.data
        fs = signal.sampling_rate
        
        # Determine appropriate axis (last axis usually time)
        axis = -1
        
        # Compute Welch PSD
        f, Pxx = welch(X, fs=fs, axis=axis, nperseg=int(fs*2))
        
        # Pxx holds the power density. Wrap in ISignal.
        return {"signal": ISignal(sampling_rate=fs, data=Pxx)}
