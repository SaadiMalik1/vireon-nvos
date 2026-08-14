"""DEPRECATED: Use vireon_methods.spatial.vireon_csp.VireonCSP instead.

This module provided a CSPPlugin wrapper. The native implementation
in vireon_csp.py is validated to match MNE CSP and offers the same API.
"""
import warnings
from vireon_core.contracts.plugin import IPlugin, PluginCapability, ScientificContract


class CSPPlugin(IPlugin):
    def __init__(self, n_components: int = 4, norm_trace: bool = False):
        warnings.warn(
            "vireon_methods.machine_learning.csp.CSPPlugin is deprecated. "
            "Use vireon_methods.spatial.vireon_csp.VireonCSP instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.n_components = n_components
        self.norm_trace = norm_trace
        self._filters = None

    @property
    def capabilities(self):
        return [PluginCapability(id="machine_learning.csp", version="1.0.0", consumes=["ISignal"], produces=["IFeatureMatrix"])]

    @property
    def plugin_id(self):
        return "vk:Method:MachineLearning:CSP"

    @property
    def version(self):
        return "1.0.0"

    @property
    def plugin_type(self):
        return "Method"

    @property
    def srl(self):
        from vireon_core.contracts.plugin import ScientificReadinessLevel
        return ScientificReadinessLevel.SRL_2

    @property
    def inputs(self):
        from vireon_core.contracts.base import ISignal
        return [ISignal]

    @property
    def outputs(self):
        from vireon_core.contracts.base import ISignal
        return [ISignal]

    def initialize(self, config=None):
        pass

    @property
    def method_name(self):
        return self.plugin_id

    @property
    def contract(self):
        return ScientificContract(
            purpose="Common Spatial Patterns for BCI",
            mathematical_assumptions=["Balanced class distributions", "Stationary covariance"],
            supported_modalities=["EEG"],
            validation_papers=["10.1109/86.84781"],
        )

    def execute(self, inputs):
        from vireon_core.contracts.base import ISignal
        import numpy as np
        from scipy.linalg import eigh

        signal = inputs.get("signal")
        labels = inputs.get("labels")

        if not isinstance(signal, ISignal):
            if isinstance(signal, (np.ndarray, memoryview)):
                X = np.asarray(signal)
            else:
                raise ValueError("Expected ISignal as 'signal' input")
        else:
            X = np.asarray(signal.data)

        if labels is not None:
            if hasattr(labels, "data"):
                y = np.asarray(labels.data).flatten()
            else:
                y = np.asarray(labels).flatten()

            classes = np.unique(y)
            if len(classes) != 2:
                raise ValueError("Native CSP implementation currently supports binary classification only.")

            covs = []
            for c in classes:
                x_c = X[y == c]
                x_c = np.transpose(x_c, [1, 0, 2])
                x_c = x_c.reshape(x_c.shape[0], -1)
                cov = np.cov(x_c)

                if self.norm_trace:
                    cov /= np.trace(cov)

                covs.append(cov)

            n_ch = covs[0].shape[0]
            reg = 1e-6 * np.trace(covs[0]) / n_ch
            covs[0] += reg * np.eye(n_ch)
            covs[1] += reg * np.eye(n_ch)

            evals, evecs = eigh(covs[0], covs[0] + covs[1])
            idx = np.argsort(evals)[::-1]
            evecs = evecs[:, idx]

            n = self.n_components
            if 2 * n > evecs.shape[1]:
                n = evecs.shape[1] // 2

            if n > 0:
                selected_idx = np.concatenate([np.arange(n), np.arange(evecs.shape[1] - n, evecs.shape[1])])
                self._filters = evecs[:, selected_idx]
            else:
                self._filters = evecs

        if self._filters is None:
            raise RuntimeError("CSPPlugin must be fitted with 'labels' before transforming.")

        epochs, channels, times = X.shape
        X_trans = np.zeros((epochs, self._filters.shape[1], times))

        for i in range(epochs):
            X_trans[i] = self._filters.T @ X[i]

        features = np.log(np.var(X_trans, axis=-1))

        if hasattr(signal, "sampling_rate"):
            return {"features": ISignal(sampling_rate=signal.sampling_rate, data=features)}
        return features


__all__ = ["CSPPlugin"]
