"""Reproduce Vinck 2011: wPLI is insensitive to volume conduction.

Key claims (Vinck et al. 2011, DOI: 10.1016/j.neuroimage.2011.01.055):
1. wPLI is 0 for zero-lag (volume-conducted) interactions.
2. wPLI is high for true phase-lagged interactions.
3. wPLI is less biased by sample size and zero-lag spurious synchrony than PLI/PLV.

Test:
1. Two signals with zero phase lag (volume conduction simulation)
   -> wPLI should be ~0 (< 0.2), PLV should be ~1 (> 0.95)
2. Two signals with π/4 phase lag (true interaction)
   -> wPLI should be > 0.8
3. wPLI of independent noise should be < 0.2
4. wPLI vs PLI in volume conduction scenario
5. Generate valid evidence bundle
"""
import os
import sys
import numpy as np
import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for pkg in ['vireon-core', 'vireon-methods', 'vireon-validation']:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from vireon_methods.connectivity.vireon_connectivity import VireonWPLI, VireonPLV, VireonPLI
from vireon_validation.benchmarks.matrix import BenchmarkMatrix


def test_wpli_zero_for_volume_conduction():
    """wPLI should be ~0 for zero-lag interactions (volume conduction)."""
    fs = 250.0
    t = np.arange(0, 20, 1 / fs)
    # Two channels with ZERO phase difference (simulating volume conduction)
    ch1 = np.sin(2 * np.pi * 10 * t)
    ch2 = np.sin(2 * np.pi * 10 * t)
    X = np.vstack([ch1, ch2])
    wpli = VireonWPLI().compute(X, fs=fs, band=(8, 12))
    assert wpli[0, 1] < 0.2, f"wPLI {wpli[0, 1]:.3f} > 0.2 for zero-lag (should be ~0)"


def test_plv_high_for_volume_conduction():
    """PLV should be ~1 for zero-lag interactions (unlike wPLI)."""
    fs = 250.0
    t = np.arange(0, 20, 1 / fs)
    ch1 = np.sin(2 * np.pi * 10 * t)
    ch2 = np.sin(2 * np.pi * 10 * t)
    X = np.vstack([ch1, ch2])
    plv = VireonPLV().compute(X, fs=fs, band=(8, 12))
    assert plv[0, 1] > 0.95, f"PLV {plv[0, 1]:.3f} < 0.95 for zero-lag (should be ~1)"


def test_wpli_high_for_phase_lagged():
    """wPLI should be > 0.8 for true phase-lagged interactions (π/4 lag)."""
    fs = 250.0
    t = np.arange(0, 20, 1 / fs)
    ch1 = np.sin(2 * np.pi * 10 * t)
    ch2 = np.sin(2 * np.pi * 10 * t + np.pi / 4)
    X = np.vstack([ch1, ch2])
    wpli = VireonWPLI().compute(X, fs=fs, band=(8, 12))
    assert wpli[0, 1] > 0.8, f"wPLI {wpli[0, 1]:.3f} < 0.8 for π/4 lag"


def test_wpli_low_for_independent_noise():
    """wPLI of independent noise should be < 0.2."""
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1, (2, 20000))
    wpli = VireonWPLI().compute(X, fs=250.0, band=(8, 12))
    assert wpli[0, 1] < 0.2, f"wPLI {wpli[0, 1]:.3f} > 0.2 for independent noise"


def test_wpli_vs_pli_volume_conduction_sensitivity():
    """wPLI should be less sensitive to volume conduction than PLI."""
    fs = 250.0
    t = np.arange(0, 20, 1 / fs)
    source1 = np.sin(2 * np.pi * 10 * t)
    source2 = np.sin(2 * np.pi * 10 * t + np.pi / 3)
    # Volume conduction mixture
    ch1 = 0.7 * source1 + 0.3 * source2
    ch2 = 0.3 * source1 + 0.7 * source2
    X = np.vstack([ch1, ch2])

    wpli = VireonWPLI().compute(X, fs=fs, band=(8, 12))
    pli = VireonPLI().compute(X, fs=fs, band=(8, 12))
    assert wpli[0, 1] <= pli[0, 1] + 0.15, (
        f"wPLI {wpli[0, 1]:.3f} should be <= PLI {pli[0, 1]:.3f} (volume conduction)"
    )


def test_wpli_evidence_bundle():
    """Generate an evidence bundle for the wPLI reproduction."""
    class WPLIMethod:
        plugin_id = "vk:Method:Connectivity:wPLI"
        version = "1.0.0"
        n_components = 1

        def execute(self, inputs):
            sig = inputs["signal"]
            if sig.ndim == 3:
                sig = sig[0]  # take first epoch
            return VireonWPLI().compute(sig, fs=250.0, band=(8, 12)).flatten()

    fs = 250.0
    t = np.arange(0, 5, 1 / fs)
    ch1 = np.sin(2 * np.pi * 10 * t)
    ch2 = np.sin(2 * np.pi * 10 * t + np.pi / 4)
    X = np.vstack([ch1, ch2]).reshape(1, 2, len(t))

    matrix = BenchmarkMatrix(seed=42)
    matrix.add_method(WPLIMethod())
    matrix.add_dataset("Vinck2011_PhaseLagged", data=X, labels=np.array([0]))
    bundles = matrix.execute_matrix()
    assert len(bundles) > 0
    assert bundles[0]["evidence_hash"] != ""
