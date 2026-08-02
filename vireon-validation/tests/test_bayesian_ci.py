import numpy as np
import pytest
from vireon_validation.statistics.framework import StatisticalFramework

def test_bayesian_credible_interval():
    # True mean 5.0, sample size 100
    rng = np.random.default_rng(42)
    data = rng.normal(loc=5.0, scale=1.0, size=100)
    
    res = StatisticalFramework.bayesian_credible_interval(data, prior_mean=0.0, prior_var=1e6, cred_mass=0.95)
    
    assert abs(res["posterior_mean"] - 5.0) < 0.2
    assert res["credible_interval"][0] < res["posterior_mean"] < res["credible_interval"][1]
    assert res["cred_mass"] == 0.95
    assert res["posterior_var"] > 0.0

def test_bayesian_credible_interval_prior_dominance():
    # Very strong prior at 10.0, tiny sample size 2
    data = np.array([2.0, 2.1])
    res = StatisticalFramework.bayesian_credible_interval(data, prior_mean=10.0, prior_var=1e-4, cred_mass=0.95)
    # Posterior should be pulled strongly to prior mean
    assert abs(res["posterior_mean"] - 10.0) < 0.5
