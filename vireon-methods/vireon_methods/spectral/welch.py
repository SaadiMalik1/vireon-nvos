"""DEPRECATED: Use vireon_methods.spectral.vireon_welch.VireonWelch instead.

This module provided a scipy.signal.welch wrapper. The native implementation
in vireon_welch.py is validated to match scipy within 1e-10 RMSE and offers
the same API plus scientific contract enforcement.
"""
import warnings
from vireon_methods.spectral.vireon_welch import VireonWelch as WelchPSDPlugin

warnings.warn(
    "vireon_methods.spectral.welch.WelchPSDPlugin is deprecated. "
    "Use vireon_methods.spectral.vireon_welch.VireonWelch instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["WelchPSDPlugin"]
