"""Reproduce Kraskov 2004: Estimating Mutual Information.

Reference: Kraskov, A., Stogbauer, H., & Grassberger, P. (2004). Estimating mutual information.
Physical Review E, 69(6), 066138. DOI: 10.1103/PhysRevE.69.066138
"""
import numpy as np
import pytest
from vireon_methods.connectivity.vireon_mutual_information import VireonMutualInformation


def test_kraskov_mutual_information_functional_dependence():
    """Mutual Information I(X; Y) should be high (> 0.5) for deterministic functional relationship."""
    t = np.linspace(0, 4 * np.pi, 500)
    x = np.sin(t)
    y = np.cos(t)  # Non-linear functional relationship (circle in 2D space)
    
    mi = VireonMutualInformation(n_bins=10)
    score = mi.compute(x, y)
    
    assert score > 0.50, f"Expected MI > 0.50 for functional relationship, got {score:.4f}"


def test_kraskov_mutual_information_uncorrelated_noise():
    """Mutual Information for independent white noise should be near zero (< 0.15)."""
    np.random.seed(2004)
    x = np.random.randn(500)
    y = np.random.randn(500)
    
    mi = VireonMutualInformation(n_bins=10)
    score = mi.compute(x, y)
    
    assert score < 0.15, f"Expected MI < 0.15 for independent noise, got {score:.4f}"
