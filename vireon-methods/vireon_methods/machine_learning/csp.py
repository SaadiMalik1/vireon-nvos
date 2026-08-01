from vireon_core.contracts.plugin import IPlugin, PluginCapability, ScientificContract

class CSPPlugin(IPlugin):
    def __init__(self, n_components: int = 4, norm_trace: bool = False):
        self.n_components = n_components
        self.norm_trace = norm_trace
        self._filters = None

    @property
    def capabilities(self):
        return [PluginCapability(id="machine_learning.csp", version="1.0.0", consumes=["ISignal"], produces=["IFeatureMatrix"])]
    
    @property
    def plugin_id(self): return "vk:Method:MachineLearning:CSP"
    
    @property
    def version(self): return "1.0.0"
    
    @property
    def plugin_type(self): return "Method"
    
    @property
    def srl(self): from vireon_core.contracts.plugin import ScientificReadinessLevel; return ScientificReadinessLevel.SRL_2
    
    @property
    def inputs(self): from vireon_core.contracts.base import ISignal; return [ISignal]
    
    @property
    def outputs(self): from vireon_core.contracts.base import ISignal; return [ISignal]
    
    def initialize(self, config=None): pass
    
    @property
    def method_name(self): return self.plugin_id

    @property
    def contract(self):
        return ScientificContract(
            purpose="Common Spatial Patterns for BCI",
            mathematical_assumptions=["Balanced class distributions", "Stationary covariance"],
            supported_modalities=["EEG"],
            validation_papers=["10.1109/86.84781"]
        )

    def execute(self, inputs):
        from vireon_core.contracts.base import ISignal
        import numpy as np
        from scipy.linalg import eigh
        
        signal = inputs.get("signal")
        labels = inputs.get("labels")
        
        if not isinstance(signal, ISignal):
            # Attempt to use as raw numpy array for ease of testing
            if isinstance(signal, np.ndarray):
                X = signal
            else:
                raise ValueError("Expected ISignal as 'signal' input")
        else:
            X = signal.data # (epochs, channels, times)
            
        if labels is not None:
            if isinstance(labels, np.ndarray):
                y = labels.flatten()
            elif hasattr(labels, 'data'):
                y = np.array(labels.data).flatten()
            else:
                y = np.array(labels).flatten()
            
            # Find unique classes
            classes = np.unique(y)
            if len(classes) != 2:
                raise ValueError("Native CSP implementation currently supports binary classification only.")
                
            covs = []
            for c in classes:
                x_c = X[y == c]
                # Compute spatial covariance for this class
                # x_c is (epochs, channels, times)
                # We need (channels, epochs * times)
                x_c = np.transpose(x_c, [1, 0, 2])
                x_c = x_c.reshape(x_c.shape[0], -1)
                cov = np.cov(x_c)
                
                if self.norm_trace:
                    cov /= np.trace(cov)
                    
                covs.append(cov)
                
            # Solve generalized eigenvalue problem: C1 * W = lambda * (C1 + C2) * W
            evals, evecs = eigh(covs[0], covs[0] + covs[1])
            
            # Sort eigenvectors by eigenvalues descending
            idx = np.argsort(evals)[::-1]
            evecs = evecs[:, idx]
            
            # Select top n_components and bottom n_components
            n = self.n_components
            if 2 * n > evecs.shape[1]:
                # If requested more components than available channels
                n = evecs.shape[1] // 2
                
            if n > 0:
                selected_idx = np.concatenate([np.arange(n), np.arange(evecs.shape[1] - n, evecs.shape[1])])
                self._filters = evecs[:, selected_idx]
            else:
                self._filters = evecs
            
        if self._filters is None:
            raise RuntimeError("CSPPlugin must be fitted with 'labels' before transforming.")
            
        # Transform (project) data: X_csp = W.T @ X
        # For each epoch, project channels
        epochs, channels, times = X.shape
        X_trans = np.zeros((epochs, self._filters.shape[1], times))
        
        for i in range(epochs):
            X_trans[i] = self._filters.T @ X[i]
            
        # Extract log-variance features: features = log(var(X_trans, axis=-1))
        features = np.log(np.var(X_trans, axis=-1))
        
        # Return features. If input was ISignal, return ISignal. Else just return features.
        if hasattr(signal, "sampling_rate"):
            return {"features": ISignal(sampling_rate=signal.sampling_rate, data=features)}
        return features
