from vireon_core.contracts.plugin import IPlugin, PluginCapability, ScientificContract

class CSPPlugin(IPlugin):
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
    def srl(self): from vireon_core.contracts.plugin import ScientificReadinessLevel; return ScientificReadinessLevel.SRL_4
    
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
            raise ValueError("Expected ISignal as 'signal' input")
            
        X = signal.data # (epochs, channels, times)
        
        if labels is not None:
            # Fit CSP
            y = labels.data.flatten() if hasattr(labels, 'data') else np.array(labels)
            
            # Find unique classes
            classes = np.unique(y)
            if len(classes) != 2:
                raise ValueError("Native CSP implementation currently supports binary classification only.")
                
            covs = []
            for c in classes:
                x_c = X[y == c]
                # Compute spatial covariance for this class
                # Reshape to (channels, epochs * times)
                x_c = np.transpose(x_c, [1, 0, 2])
                x_c = x_c.reshape(x_c.shape[0], -1)
                cov = np.cov(x_c)
                covs.append(cov)
                
            # Solve generalized eigenvalue problem: C1 * W = lambda * (C1 + C2) * W
            evals, evecs = eigh(covs[0], covs[0] + covs[1])
            
            # Sort eigenvectors by eigenvalues descending
            idx = np.argsort(evals)[::-1]
            evecs = evecs[:, idx]
            
            self._filters = evecs
            
        if not hasattr(self, '_filters'):
            raise RuntimeError("CSPPlugin must be fitted with 'labels' before transforming.")
            
        # Transform (project) data: X_csp = W.T @ X
        # For each epoch, project channels
        epochs, channels, times = X.shape
        X_trans = np.zeros((epochs, self._filters.shape[1], times))
        
        for i in range(epochs):
            X_trans[i] = self._filters.T @ X[i]
            
        return {"features": ISignal(sampling_rate=signal.sampling_rate, data=X_trans)}
