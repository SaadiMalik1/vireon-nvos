"""DEPRECATED: Use vireon_methods.spectral.vireon_welch.VireonWelch instead.

This module provided a scipy.signal.welch wrapper. The native implementation
in vireon_welch.py is validated to match scipy within 1e-10 RMSE and offers
the same API plus scientific contract enforcement.
"""
import warnings
from vireon_core.contracts.plugin import IPlugin, PluginCapability, ScientificContract, ScientificReadinessLevel


class WelchPSDPlugin(IPlugin):
    def __init__(self, fs: float = 250.0, nperseg: int = 256):
        warnings.warn(
            "vireon_methods.spectral.welch.WelchPSDPlugin is deprecated. "
            "Use vireon_methods.spectral.vireon_welch.VireonWelch instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.fs = fs
        self.nperseg = nperseg

    @property
    def plugin_id(self) -> str:
        return "vk:Method:Spectral:WelchPSD"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def plugin_type(self) -> str:
        return "Method"

    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_3

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
    def capabilities(self):
        return [PluginCapability(id="spectral_estimation.welch", version="1.0.0", consumes=["ISignal"], produces=["ISignal"])]

    @property
    def contract(self):
        return ScientificContract(
            purpose="Estimate PSD via Welch's Method",
            mathematical_assumptions=["Wide-Sense Stationarity", "Ergodicity"],
            supported_modalities=["EEG", "ECOG"],
            validation_papers=["10.1109/TAU.1967.1161901"],
        )

    def execute(self, inputs):
        from vireon_core.contracts.base import ISignal
        from scipy.signal import welch

        signal = inputs.get("signal")
        if not isinstance(signal, ISignal):
            raise ValueError("Expected ISignal as 'signal' input")

        X = signal.data
        fs = signal.sampling_rate
        f, Pxx = welch(X, fs=fs, axis=-1, nperseg=int(fs * 2))
        return {"signal": ISignal(sampling_rate=fs, data=Pxx)}


__all__ = ["WelchPSDPlugin"]
