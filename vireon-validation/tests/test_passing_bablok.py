import numpy as np
import pytest
from vireon_validation.statistics.framework import StatisticalFramework

def test_passing_bablok_synthetic():
    rng = np.random.default_rng(42)
    x = rng.uniform(0, 10, 50)
    # y = 2x + 1 + noise
    y = 2.0 * x + 1.0 + rng.normal(0, 0.5, 50)
    
    res = StatisticalFramework.passing_bablok(x, y)
    
    assert abs(res["slope"] - 2.0) < 0.2
    assert abs(res["intercept"] - 1.0) < 0.5
    
    assert "ci_slope" in res
    assert "ci_intercept" in res
    
    assert res["ci_slope"][0] <= res["slope"] <= res["ci_slope"][1]

def test_passing_bablok_nan():
    x = np.array([1, 2, np.nan])
    y = np.array([2, 4, 6])
    with pytest.raises(ValueError, match="NaN"):
        StatisticalFramework.passing_bablok(x, y)
