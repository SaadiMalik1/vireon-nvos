"""vireon_models main package."""
from vireon_models.providers.datasets import (
    SyntheticSignalProvider, MotorImageryProvider, SyntheticMotorImageryProvider, PhysioNetMotorImageryProvider
)
from vireon_models.providers.mne_provider import MNEProvider
from vireon_models.providers.eegbci_provider import EEGBCIProvider

__version__ = "1.0.2"
__all__ = [
    "SyntheticSignalProvider", "MotorImageryProvider", "SyntheticMotorImageryProvider",
    "PhysioNetMotorImageryProvider", "MNEProvider", "EEGBCIProvider"
]
