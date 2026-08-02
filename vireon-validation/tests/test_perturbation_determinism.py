import numpy as np
import pytest
from vireon_core.runtime.rng import DeterministicRNG
from vireon_validation.perturbations.library import (
    WhiteNoisePerturbation,
    ChannelDropoutPerturbation,
    LineNoisePerturbation,
    QuantizationPerturbation,
)

def test_white_noise_perturbation_deterministic():
    p1 = WhiteNoisePerturbation(severity=0.5, seed=42)
    p2 = WhiteNoisePerturbation(severity=0.5, seed=42)
    rng = DeterministicRNG(100)
    data = rng.normal(0, 1, size=(8, 250))
    res1 = p1.apply(data)
    res2 = p2.apply(data)
    assert np.array_equal(res1, res2)

def test_channel_dropout_deterministic():
    p1 = ChannelDropoutPerturbation(severity=0.2, seed=42)
    p2 = ChannelDropoutPerturbation(severity=0.2, seed=42)
    rng = DeterministicRNG(100)
    data = rng.normal(0, 1, size=(8, 250))
    res1 = p1.apply(data)
    res2 = p2.apply(data)
    assert np.array_equal(res1, res2)

def test_callable_interface():
    p = WhiteNoisePerturbation(severity=0.5, seed=42)
    rng = DeterministicRNG(100)
    data = rng.normal(0, 1, size=(8, 250))
    # Matrix may call perturbation as callable
    res = p(data)
    assert res.shape == data.shape
