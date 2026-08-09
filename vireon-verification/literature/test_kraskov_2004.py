"""Kraskov et al. (2004) Mutual Information Literature Test.

Reference: Kraskov, A., Stogbauer, H., & Grassberger, P. (2004). Estimating mutual information.
Physical Review E, 69(6), 066138. DOI: 10.1103/PhysRevE.69.066138
"""
import numpy as np
import pytest
from vireon_methods.connectivity.vireon_mutual_information import VireonMutualInformation
from vireon_core.contracts.plugin import ScientificContractViolation


def test_kraskov_mi_independent_variables():
    """MI(X,Y) ≈ 0 for independent Gaussian variables."""
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 3000)
    y = rng.normal(0, 1, 3000)
    mi = VireonMutualInformation(k=4).compute(x, y)
    assert mi < 0.05, f"MI for independent variables should be ~0, got {mi}"


def test_kraskov_mi_functional_dependence():
    """MI(sin(t), cos(t)) should be high for non-linearly dependent variables."""
    t = np.linspace(0, 100, 3000)
    x = np.sin(t)
    y = np.cos(t)
    mi = VireonMutualInformation(k=4).compute(x, y)
    assert mi > 0.5, f"MI for sin/cos should be > 0.5, got {mi}"


def test_kraskov_mi_correlated_gaussians():
    """MI for correlated Gaussians: I = -0.5 * log(1 - rho^2)."""
    rng = np.random.default_rng(42)
    rho = 0.8
    n = 3000
    x = rng.normal(0, 1, n)
    y = rho * x + np.sqrt(1 - rho**2) * rng.normal(0, 1, n)
    mi = VireonMutualInformation(k=4).compute(x, y)
    expected = -0.5 * np.log(1 - rho**2)  # ≈ 0.483 nats for rho=0.8
    assert abs(mi - expected) < 0.25, f"MI {mi:.3f} far from expected {expected:.3f}"


def test_kraskov_mi_rejects_short_signals():
    """Should raise if signal length < k+1."""
    with pytest.raises(ScientificContractViolation):
        VireonMutualInformation(k=10).compute(np.array([1.0, 2.0]), np.array([3.0, 4.0]))


if __name__ == "__main__":
    test_kraskov_mi_independent_variables()
    test_kraskov_mi_functional_dependence()
    test_kraskov_mi_correlated_gaussians()
    test_kraskov_mi_rejects_short_signals()
