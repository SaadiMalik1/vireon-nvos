from vireon_core.contracts.plugin import IPlugin, PluginCapability, ScientificContract

class ICAPlugin(IPlugin):
    @property
    def capabilities(self):
        return [PluginCapability(id="machine_learning.ica", version="1.0.0", consumes=["ISignal"], produces=["ISignal", "IComponents"])]
    
    @property
    def contract(self):
        return ScientificContract(
            purpose="Independent Component Analysis",
            mathematical_assumptions=["Non-Gaussianity", "Full rank data matrix"],
            supported_modalities=["EEG", "MEG"],
            validation_papers=["10.1162/089976600300015015"]
        )

    def execute(self, inputs):
        from vireon_core.contracts.base import ISignal
        import numpy as np
        
        signal = inputs.get("signal")
        if not isinstance(signal, ISignal):
            raise ValueError("Expected ISignal as 'signal' input")
            
        try:
            from sklearn.decomposition import FastICA
        except ImportError:
            raise RuntimeError("ICAPlugin requires scikit-learn. Please install 'scikit-learn'.")
            
        X = signal.data
        # Typically shape is (samples, channels) or (epochs, channels, times)
        # FastICA expects (samples, features)
        original_shape = X.shape
        if len(original_shape) == 3:
            X_flat = np.transpose(X, [0, 2, 1]).reshape(-1, original_shape[1])
        else:
            X_flat = X
            
        ica = FastICA(random_state=42)
        S_flat = ica.fit_transform(X_flat)
        
        if len(original_shape) == 3:
            S = S_flat.reshape(original_shape[0], original_shape[2], -1)
            S = np.transpose(S, [0, 2, 1])
        else:
            S = S_flat
            
        # Returning components (unmixing matrix) and the separated signals
        # For simplicity, returning just the separated signals under "signal" key
        return {"signal": ISignal(sampling_rate=signal.sampling_rate, data=S)}
