"""Spatial filtering methods subpackage."""
from vireon_methods.spatial.vireon_ica import VireonICA
from vireon_methods.spatial.vireon_csp import VireonCSP
from vireon_methods.spatial.vireon_riemannian import VireonRiemannianMDM
from vireon_methods.spatial.vireon_xdawn import VireonxDAWN
from vireon_methods.spatial.vireon_fbcsp import VireonFBCSP
from vireon_methods.native.spatial import VireonLaplacian, VireonREST

__version__ = "1.0.2"
__all__ = ["VireonICA", "VireonCSP", "VireonRiemannianMDM", "VireonxDAWN", "VireonFBCSP", "VireonLaplacian", "VireonREST"]
