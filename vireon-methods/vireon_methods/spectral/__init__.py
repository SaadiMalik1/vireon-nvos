"""Spectral analysis methods subpackage."""
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_methods.spectral.vireon_fft import VireonFFT
from vireon_methods.spectral.vireon_stft import VireonSTFT
from vireon_methods.spectral.vireon_wavelets import VireonWavelet
from vireon_methods.spectral.vireon_multitaper import VireonMultitaper

__version__ = "1.1.0"
__all__ = ["VireonWelch", "VireonFFT", "VireonSTFT", "VireonWavelet", "VireonMultitaper"]
