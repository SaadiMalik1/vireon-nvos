import numpy as np
from vireon_validation.statistics.framework import StatisticalFramework

def test_icc_perfect_agreement():
    ratings = np.array([[5,5,5],[3,3,3],[4,4,4]])  # 3 subjects, 3 raters, perfect
    icc = StatisticalFramework.intraclass_correlation(ratings)
    assert abs(icc - 1.0) < 0.01

def test_icc_random():
    rng = np.random.default_rng(42)
    ratings = rng.normal(size=(20, 5))
    icc = StatisticalFramework.intraclass_correlation(ratings)
    assert -0.1 < icc < 0.5  # low for random

def test_icc_no_longer_returns_094():
    # Zeros will cause ms_residual to be 0 or ms_subjects to be 0, leading to a specific ICC (should be NaN or 1.0 depending on limits, but definitely not 0.94)
    # Let's use systematic disagreement
    ratings = np.array([[1, 5, 9], [2, 6, 10], [3, 7, 11]])
    icc = StatisticalFramework.intraclass_correlation(ratings)
    assert icc != 0.94
    assert icc < 0.5 # Since raters systematically disagree
