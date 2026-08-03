import numpy as np
import pytest
from vireon_core.runtime.rng import DeterministicRNG
from vireon_validation.statistics.effect_sizes import (
    cohens_d,
    hedges_g,
    eta_squared,
    partial_eta_squared,
    odds_ratio,
    interpret_cohens_d,
)


def test_cohens_d_zero():
    rng = DeterministicRNG(42)
    g = rng.normal(5, 1, 100)
    assert abs(cohens_d(g, g)) < 0.1


def test_cohens_d_large():
    rng = DeterministicRNG(42)
    g1 = rng.normal(0, 1, 100)
    g2 = rng.normal(3, 1, 100)
    d = cohens_d(g1, g2)
    assert abs(d) > 2.0  # large effect
    assert interpret_cohens_d(d) == "large"


def test_hedges_g_smaller_than_cohens_d():
    rng = DeterministicRNG(42)
    g1 = rng.normal(0, 1, 10)  # small sample
    g2 = rng.normal(1, 1, 10)
    d = cohens_d(g1, g2)
    g = hedges_g(g1, g2)
    assert abs(g) < abs(d)  # Hedges' g is always slightly smaller in magnitude


def test_eta_squared():
    g1 = np.array([1, 2, 3, 4, 5])
    g2 = np.array([6, 7, 8, 9, 10])
    eta = eta_squared([g1, g2])
    assert 0 < eta <= 1.0
    assert eta > 0.5  # large effect


def test_odds_ratio_and_partial_eta():
    assert odds_ratio(10, 5, 2, 20) == 20.0
    assert partial_eta_squared(50.0, 50.0) == 0.5
