"""DEPRECATED: Use vireon_methods.spatial.vireon_csp.VireonCSP instead.

This module provided a CSPPlugin wrapper. The native implementation
in vireon_csp.py is validated to match MNE CSP and offers the same API.
"""
import warnings
from vireon_methods.spatial.vireon_csp import VireonCSP as CSPPlugin

warnings.warn(
    "vireon_methods.machine_learning.csp.CSPPlugin is deprecated. "
    "Use vireon_methods.spatial.vireon_csp.VireonCSP instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["CSPPlugin"]
