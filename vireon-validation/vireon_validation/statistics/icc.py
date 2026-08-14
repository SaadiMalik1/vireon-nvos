"""Intraclass Correlation Coefficient (ICC) statistics module.

Reference: Shrout, P. E., & Fleiss, J. L. (1979). Intraclass correlations: 
uses in assessing rater reliability. Psychological Bulletin, 86(2), 420.
"""
import numpy as np


def intraclass_correlation(data: np.ndarray, icc_type: str = "ICC(3,1)") -> float:
    """Compute Intraclass Correlation Coefficient (Shrout & Fleiss, 1979).

    Parameters
    ----------
    data : np.ndarray
        Array of shape (n_subjects, n_sessions) or (n_targets, n_raters).
    icc_type : str
        Type of ICC, default "ICC(3,1)" (Two-way mixed, single score, consistency).

    Returns
    -------
    float
        Intraclass correlation coefficient in [-1, 1].
    """
    data = np.asarray(data, dtype=float)
    if data.ndim != 2:
        raise ValueError(f"Expected 2D array of shape (n_subjects, n_sessions), got {data.ndim}D.")
    n, k = data.shape
    if n < 2 or k < 2:
        raise ValueError("Data must have at least 2 subjects and 2 sessions/raters.")

    grand_mean = np.mean(data)
    subject_means = np.mean(data, axis=1)
    session_means = np.mean(data, axis=0)

    ss_total = np.sum((data - grand_mean) ** 2)
    ss_b = k * np.sum((subject_means - grand_mean) ** 2)
    ss_c = n * np.sum((session_means - grand_mean) ** 2)
    ss_e = ss_total - ss_b - ss_c

    ms_b = ss_b / (n - 1)
    ms_e = ss_e / max((n - 1) * (k - 1), 1e-12)

    denom = ms_b + (k - 1) * ms_e
    if abs(denom) < 1e-12:
        return 0.0

    icc_val = (ms_b - ms_e) / denom
    return float(np.clip(icc_val, -1.0, 1.0))
