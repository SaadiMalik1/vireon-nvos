"""NaN and Inf contract validation tests across all algorithms."""
import numpy as np
import pytest
from vireon_core.contracts.plugin import ScientificContractViolation

from vireon_methods.spectral.vireon_fft import VireonFFT
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_methods.spectral.vireon_multitaper import VireonMultitaper
from vireon_methods.time_frequency.vireon_emd import VireonEMD
from vireon_methods.signal_processing.vireon_convolution import VireonConvolution


def test_nan_raises_contract_violation():
    """All algorithms must raise ScientificContractViolation when NaN is in input."""
    nan_sig = np.array([1.0, 2.0, np.nan, 4.0, 5.0] * 10)
    
    with pytest.raises(ScientificContractViolation):
        VireonFFT(fs=100).compute(nan_sig)
        
    with pytest.raises(ScientificContractViolation):
        VireonWelch(fs=100).compute(nan_sig)
        
    with pytest.raises(ScientificContractViolation):
        VireonMultitaper(fs=100).compute(nan_sig)
        
    with pytest.raises(ScientificContractViolation):
        VireonEMD().fit_transform(nan_sig)
        
    with pytest.raises(ScientificContractViolation):
        VireonConvolution().convolve(nan_sig, np.array([1, 1]))


def test_inf_raises_contract_violation():
    """All algorithms must raise ScientificContractViolation when Inf is in input."""
    inf_sig = np.array([1.0, 2.0, np.inf, 4.0, 5.0] * 10)
    
    with pytest.raises(ScientificContractViolation):
        VireonFFT(fs=100).compute(inf_sig)
        
    with pytest.raises(ScientificContractViolation):
        VireonWelch(fs=100).compute(inf_sig)
        
    with pytest.raises(ScientificContractViolation):
        VireonMultitaper(fs=100).compute(inf_sig)
        
    with pytest.raises(ScientificContractViolation):
        VireonEMD().fit_transform(inf_sig)
        
    with pytest.raises(ScientificContractViolation):
        VireonConvolution().convolve(inf_sig, np.array([1, 1]))
