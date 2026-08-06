"""Connectivity methods subpackage."""
from vireon_methods.connectivity.vireon_connectivity import VireonCoherence, VireonPLV, VireonPLI, VireonWPLI, VireonAEC
from vireon_methods.connectivity.vireon_wavelet_coherence import VireonWaveletCoherence
from vireon_methods.connectivity.vireon_transfer_entropy import VireonTransferEntropy
from vireon_methods.connectivity.vireon_mutual_information import VireonMutualInformation

__version__ = "1.0.2"
__all__ = [
    "VireonCoherence", "VireonPLV", "VireonPLI", "VireonWPLI", "VireonAEC",
    "VireonWaveletCoherence", "VireonTransferEntropy", "VireonMutualInformation"
]
