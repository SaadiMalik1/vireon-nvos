"""DEPRECATED: Use vireon_methods.spatial.vireon_ica.VireonICA instead.

This module provided an ICAPlugin wrapper. The native implementation
in vireon_ica.py is validated to match FastICA and offers the same API.
"""
import warnings
from vireon_methods.spatial.vireon_ica import VireonICA as ICAPlugin

warnings.warn(
    "vireon_methods.machine_learning.ica.ICAPlugin is deprecated. "
    "Use vireon_methods.spatial.vireon_ica.VireonICA instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ICAPlugin"]
