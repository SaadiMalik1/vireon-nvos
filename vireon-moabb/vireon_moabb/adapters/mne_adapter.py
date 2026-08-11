from vireon_moabb.adapters.base import BaseAdapter, AdapterResult
import hashlib, json, numpy as np


class MneAdapter(BaseAdapter):
    """Adapter for MNE-Python operations (filtering, ICA, CSP, etc.)."""

    @property
    def name(self) -> str:
        return "mne"

    @property
    def library_version(self) -> str:
        try:
            import mne
            return mne.__version__
        except ImportError:
            return "unknown"

    def can_handle(self, spec: dict) -> bool:
        return spec.get("library") == "mne"

    def execute(self, spec: dict, **kwargs) -> AdapterResult:
        """Execute an MNE operation.

        Spec format:
            {
                "library": "mne",
                "operation": "filter" | "ica" | "csp" | "epochs",
                "parameters": {...},
                "data": np.ndarray or path
            }
        """
        operation = spec["operation"]
        params = spec.get("parameters", {})

        if operation == "filter":
            return self._filter(params, kwargs.get("data"))
        elif operation == "ica":
            return self._ica(params, kwargs.get("data"))
        elif operation == "csp":
            return self._csp(params, kwargs.get("data"), kwargs.get("labels"))
        else:
            raise ValueError(f"Unknown MNE operation: {operation}")

    def _filter(self, params, data):
        import mne
        sfreq = params.get("sfreq", 250)
        l_freq = params.get("l_freq", 8)
        h_freq = params.get("h_freq", 32)
        info = mne.create_info(data.shape[0], sfreq, ch_types="eeg")
        raw = mne.io.RawArray(data, info, verbose=False)
        raw.filter(l_freq, h_freq, verbose=False)
        filtered = raw.get_data()
        return AdapterResult(
            outputs=filtered,
            metadata={"l_freq": l_freq, "h_freq": h_freq, "sfreq": sfreq},
            execution_hash=hashlib.sha256(filtered.tobytes()).hexdigest(),
            adapter_name=self.name,
        )

    def _csp(self, params, data, labels):
        from mne.decoding import CSP
        n_components = params.get("n_components", 4)
        csp = CSP(n_components=n_components)
        features = csp.fit_transform(data, labels)
        return AdapterResult(
            outputs=features,
            metadata={"n_components": n_components},
            execution_hash=hashlib.sha256(features.tobytes()).hexdigest(),
            adapter_name=self.name,
        )

    def _ica(self, params, data):
        n_components = params.get("n_components", 8)
        # Mocking ICA
        return AdapterResult(
            outputs=data,
            metadata={"n_components": n_components},
            execution_hash="mock",
            adapter_name=self.name
        )
