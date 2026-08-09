"""Reproduce Schreiber 2000: Measuring Information Transfer (Transfer Entropy).

Reference: Schreiber, T. (2000). Measuring information transfer. Physical Review Letters, 85(2), 461-464.
DOI: 10.1103/PhysRevLett.85.461
"""
import numpy as np
from vireon_methods.connectivity.vireon_transfer_entropy import VireonTransferEntropy


def test_schreiber_transfer_entropy_directional_flow():
    """Transfer Entropy TE(X->Y) should be positive when X drives Y with delay."""
    np.random.seed(2000)
    n = 500
    x = np.random.randn(n)
    # y is driven by x with delay 1 plus noise
    y = np.zeros(n)
    y[1:] = 0.8 * x[:-1] + 0.2 * np.random.randn(n - 1)
    
    te = VireonTransferEntropy()
    te_xy = te.compute(x, y, delay=1)
    te_yx = te.compute(y, x, delay=1)
    
    assert te_xy > 0.05, f"Expected TE(X->Y) > 0.05 for driving relationship, got {te_xy:.4f}"
    assert te_xy > te_yx, f"Expected directional TE(X->Y) {te_xy:.4f} > TE(Y->X) {te_yx:.4f}"


def test_schreiber_transfer_entropy_independent_signals():
    """Transfer Entropy between independent random signals should be near zero (< 0.1)."""
    np.random.seed(42)
    x = np.random.randn(300)
    y = np.random.randn(300)
    
    te = VireonTransferEntropy()
    score = te.compute(x, y, delay=1)
    
    assert score < 0.10, f"Expected TE < 0.10 for independent signals, got {score:.4f}"
