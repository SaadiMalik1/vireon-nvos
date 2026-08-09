"""vireon_methods main package."""
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_methods.spectral.vireon_fft import VireonFFT
from vireon_methods.spectral.vireon_stft import VireonSTFT
from vireon_methods.spectral.vireon_wavelets import VireonWavelet
from vireon_methods.spectral.vireon_multitaper import VireonMultitaper
from vireon_methods.filtering.vireon_fir import VireonFIR
from vireon_methods.filtering.vireon_iir import VireonIIR
from vireon_methods.spatial.vireon_ica import VireonICA
from vireon_methods.spatial.vireon_csp import VireonCSP, VireonCSP as CSPPlugin
from vireon_methods.spatial.vireon_riemannian import VireonRiemannianMDM
from vireon_methods.spatial.vireon_xdawn import VireonxDAWN
from vireon_methods.spatial.vireon_fbcsp import VireonFBCSP
from vireon_methods.source_localization.vireon_source_localization import VireonMinimumNorm
from vireon_methods.source_localization.vireon_beamforming import VireonLCMV
from vireon_methods.connectivity.vireon_connectivity import VireonCoherence, VireonPLV, VireonPLI, VireonWPLI, VireonAEC
from vireon_methods.connectivity.vireon_wavelet_coherence import VireonWaveletCoherence
from vireon_methods.connectivity.vireon_transfer_entropy import VireonTransferEntropy
from vireon_methods.connectivity.vireon_mutual_information import VireonMutualInformation
from vireon_methods.time_frequency.vireon_emd import VireonEMD
from vireon_methods.signal_processing.vireon_convolution import VireonConvolution

__version__ = "1.0.2"
__all__ = [
    "VireonWelch", "VireonFFT", "VireonSTFT", "VireonWavelet", "VireonMultitaper",
    "VireonFIR", "VireonIIR", "VireonICA", "VireonCSP", "VireonRiemannianMDM",
    "VireonxDAWN", "VireonFBCSP", "CSPPlugin", "VireonMinimumNorm", "VireonLCMV",
    "VireonCoherence", "VireonPLV", "VireonPLI", "VireonWPLI", "VireonAEC",
    "VireonWaveletCoherence", "VireonTransferEntropy", "VireonMutualInformation",
    "VireonEMD", "VireonConvolution"
]
