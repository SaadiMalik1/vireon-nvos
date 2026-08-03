"""Connectivity metrics validation suite.

Validates all 6 connectivity metrics in Vireon:
1. Coherence (>0.9 for phase-locked, <0.3 for noise, symmetric, diagonal=1)
2. PLV (>0.95 for phase-locked, <0.2 for noise, bounded in [0, 1])
3. PLI (>0.8 for π/2 lag, <0.2 for zero lag)
4. wPLI (>0.8 for π/4 lag, <0.2 for independent noise)
5. AEC (>0.7 for amplitude-correlated signals)
6. Imaginary Coherence (>0.8 for π/2 lag, <0.2 for zero lag)
"""
import numpy as np
import pytest

import sys, os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for pkg in ['vireon-core', 'vireon-methods']:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from vireon_methods.connectivity.vireon_connectivity import (
    VireonCoherence,
    VireonPLV,
    VireonPLI,
    VireonAEC,
    VireonWPLI,
    VireonImaginaryCoherence,
)


@pytest.fixture
def phase_locked_signals():
    """Two channels with constant phase difference (π/4)."""
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)
    phase_diff = np.pi / 4
    ch1 = np.sin(2 * np.pi * 10 * t)
    ch2 = np.sin(2 * np.pi * 10 * t + phase_diff)
    X = np.vstack([ch1, ch2])
    return X, fs, phase_diff


@pytest.fixture
def independent_noise():
    """Two channels of independent white noise (sufficient samples for spectral estimates)."""
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1, (2, 25000))
    return X, 250.0


# ===== Coherence Tests =====

def test_coherence_phase_locked(phase_locked_signals):
    """Coherence of phase-locked signals should be > 0.9."""
    X, fs, _ = phase_locked_signals
    coh = VireonCoherence().compute(X, fs=fs, band=(8, 12))
    assert coh[0, 1] > 0.9, f"Coherence {coh[0, 1]:.3f} < 0.9 for phase-locked signals"


def test_coherence_independent_noise(independent_noise):
    """Coherence of independent noise should be < 0.3."""
    X, fs = independent_noise
    coh = VireonCoherence().compute(X, fs=fs, band=(8, 12))
    assert coh[0, 1] < 0.3, f"Coherence {coh[0, 1]:.3f} > 0.3 for independent noise"


def test_coherence_symmetric(phase_locked_signals):
    """Coherence matrix must be symmetric with diagonal = 1."""
    X, fs, _ = phase_locked_signals
    coh = VireonCoherence().compute(X, fs=fs, band=(8, 12))
    assert np.allclose(coh, coh.T, atol=1e-10), "Coherence not symmetric"
    assert np.allclose(np.diag(coh), 1.0, atol=1e-10), "Diagonal not 1.0"


# ===== PLV Tests =====

def test_plv_phase_locked(phase_locked_signals):
    """PLV of phase-locked signals should be > 0.95."""
    X, fs, _ = phase_locked_signals
    plv = VireonPLV().compute(X, fs=fs, band=(8, 12))
    assert plv[0, 1] > 0.95, f"PLV {plv[0, 1]:.3f} < 0.95"


def test_plv_independent_noise(independent_noise):
    """PLV of independent noise should be < 0.2."""
    X, fs = independent_noise
    plv = VireonPLV().compute(X, fs=fs, band=(8, 12))
    assert plv[0, 1] < 0.2, f"PLV {plv[0, 1]:.3f} > 0.2"


def test_plv_range(phase_locked_signals, independent_noise):
    """PLV must be bounded in [0, 1]."""
    X_locked, fs_l, _ = phase_locked_signals
    X_noise, fs_n = independent_noise
    for X, fs in [(X_locked, fs_l), (X_noise, fs_n)]:
        plv = VireonPLV().compute(X, fs=fs, band=(8, 12))
        assert np.all(plv >= -1e-10) and np.all(plv <= 1.0 + 1e-10), "PLV out of [0, 1] range"


# ===== PLI Tests =====

def test_pli_pi2_lag():
    """PLI for π/2 phase lag should be high (close to 1)."""
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)
    ch1 = np.sin(2 * np.pi * 10 * t)
    ch2 = np.sin(2 * np.pi * 10 * t + np.pi / 2)  # 90° phase lag
    X = np.vstack([ch1, ch2])
    pli = VireonPLI().compute(X, fs=fs, band=(8, 12))
    assert pli[0, 1] > 0.8, f"PLI {pli[0, 1]:.3f} < 0.8 for π/2 lag"


def test_pli_zero_lag():
    """PLI for zero phase lag should be ~0 (imaginary part is 0)."""
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)
    ch1 = np.sin(2 * np.pi * 10 * t)
    ch2 = np.sin(2 * np.pi * 10 * t)  # zero lag
    X = np.vstack([ch1, ch2])
    pli = VireonPLI().compute(X, fs=fs, band=(8, 12))
    assert pli[0, 1] < 0.2, f"PLI {pli[0, 1]:.3f} > 0.2 for zero lag"


# ===== wPLI Tests =====

def test_wpli_pi4_lag():
    """wPLI for π/4 phase lag should be high."""
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)
    ch1 = np.sin(2 * np.pi * 10 * t)
    ch2 = np.sin(2 * np.pi * 10 * t + np.pi / 4)
    X = np.vstack([ch1, ch2])
    wpli = VireonWPLI().compute(X, fs=fs, band=(8, 12))
    assert wpli[0, 1] > 0.8, f"wPLI {wpli[0, 1]:.3f} < 0.8 for π/4 lag"


def test_wpli_independent_noise(independent_noise):
    """wPLI of independent noise should be < 0.2."""
    X, fs = independent_noise
    wpli = VireonWPLI().compute(X, fs=fs, band=(8, 12))
    assert wpli[0, 1] < 0.2, f"wPLI {wpli[0, 1]:.3f} > 0.2"


# ===== AEC Tests =====

def test_aec_amplitude_correlated():
    """AEC of amplitude-correlated signals should be high."""
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)
    env = 1 + 0.5 * np.sin(2 * np.pi * 1 * t)  # shared 1 Hz envelope
    ch1 = env * np.sin(2 * np.pi * 10 * t)
    ch2 = env * np.sin(2 * np.pi * 10 * t + np.pi / 3)
    X = np.vstack([ch1, ch2])
    aec = VireonAEC().compute(X, fs=fs, band=(8, 12))
    assert aec[0, 1] > 0.7, f"AEC {aec[0, 1]:.3f} < 0.7 for amplitude-correlated signals"


# ===== Imaginary Coherence Tests =====

def test_imaginary_coherence_pi2_lag():
    """Imaginary coherence for π/2 lag should be high."""
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)
    ch1 = np.sin(2 * np.pi * 10 * t)
    ch2 = np.sin(2 * np.pi * 10 * t + np.pi / 2)
    X = np.vstack([ch1, ch2])
    icoh = VireonImaginaryCoherence().compute(X, fs=fs, band=(8, 12))
    assert icoh[0, 1] > 0.8, f"Imaginary coherence {icoh[0, 1]:.3f} < 0.8 for π/2 lag"


def test_imaginary_coherence_zero_lag():
    """Imaginary coherence for zero lag should be ~0."""
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)
    ch1 = np.sin(2 * np.pi * 10 * t)
    ch2 = np.sin(2 * np.pi * 10 * t)
    X = np.vstack([ch1, ch2])
    icoh = VireonImaginaryCoherence().compute(X, fs=fs, band=(8, 12))
    assert icoh[0, 1] < 0.2, f"Imaginary coherence {icoh[0, 1]:.3f} > 0.2 for zero lag"
