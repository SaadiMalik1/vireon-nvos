import numpy as np
from vireon_validation.statistics.framework import StatisticalFramework

def test_mcc_perfect():
    y_true = np.array([1, 1, 0, 0, 1, 0])
    y_pred = np.array([1, 1, 0, 0, 1, 0])
    mcc = StatisticalFramework.matthews_correlation_coefficient(y_true, y_pred)
    assert abs(mcc - 1.0) < 1e-6

def test_mcc_anti_correlated():
    y_true = np.array([1, 1, 0, 0, 1, 0])
    y_pred = np.array([0, 0, 1, 1, 0, 1])
    mcc = StatisticalFramework.matthews_correlation_coefficient(y_true, y_pred)
    assert abs(mcc - (-1.0)) < 1e-6

def test_mcc_random():
    rng = np.random.default_rng(42)
    y_true = rng.integers(0, 2, 1000)
    y_pred = rng.integers(0, 2, 1000)
    mcc = StatisticalFramework.matthews_correlation_coefficient(y_true, y_pred)
    assert abs(mcc - 0.0) < 0.1

def test_mcc_division_by_zero():
    # Only true positives, no other classes => denominator will have terms that are 0
    y_true = np.array([1, 1, 1, 1])
    y_pred = np.array([1, 1, 1, 1])
    mcc = StatisticalFramework.matthews_correlation_coefficient(y_true, y_pred)
    assert mcc == 0.0
