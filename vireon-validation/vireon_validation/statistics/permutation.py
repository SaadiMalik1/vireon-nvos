"""Permutation testing framework.

Reference: Maris, E., & Oostenveld, R. (2007). Nonparametric statistical testing 
of EEG- and MEG-data. Journal of Neuroscience Methods, 164(1), 177-190.
"""
import numpy as np
from typing import Callable, Optional, Dict, Any
from scipy import stats
from scipy.ndimage import label
from vireon_core.runtime.rng import DeterministicRNG


def permutation_test(
    group1: np.ndarray,
    group2: np.ndarray,
    statistic: Optional[Callable] = None,
    n_permutations: int = 10000,
    seed: int = 42
) -> Dict[str, Any]:
    """Two-sample permutation test.

    Args:
        group1, group2: Arrays of observations.
        statistic: Function(group1, group2) -> scalar. Default: mean difference.
        n_permutations: Number of permutations.
        seed: Random seed.

    Returns:
        {"statistic": observed, "p_value": p, "null_distribution": dist, "n_permutations": n}
    """
    if statistic is None:
        def statistic(g1, g2):
            return np.mean(g1) - np.mean(g2)

    rng = DeterministicRNG(seed)
    group1 = np.asarray(group1, dtype=float)
    group2 = np.asarray(group2, dtype=float)
    observed = statistic(group1, group2)

    combined = np.concatenate([group1, group2])
    n1 = len(group1)

    null_dist = np.zeros(n_permutations)
    for i in range(n_permutations):
        perm_idx = rng.permutation(len(combined))
        perm1 = combined[perm_idx[:n1]]
        perm2 = combined[perm_idx[n1:]]
        null_dist[i] = statistic(perm1, perm2)

    p_value = float(np.mean(np.abs(null_dist) >= np.abs(observed)))

    return {
        "statistic": float(observed),
        "p_value": p_value,
        "null_distribution": null_dist,
        "n_permutations": n_permutations
    }


def max_stat_permutation_test(
    data: np.ndarray,
    labels: np.ndarray,
    n_permutations: int = 10000,
    seed: int = 42
) -> Dict[str, Any]:
    """Max-statistic permutation test for multiple comparisons.

    Corrects for multiple comparisons by using the maximum statistic across
    all comparisons in each permutation.

    Args:
        data: (n_observations, n_comparisons) array.
        labels: (n_observations,) binary labels (0 and 1).
        n_permutations: Number of permutations.
        seed: Random seed.

    Returns:
        {"statistics": obs_stats, "p_values": corrected_p, "threshold_95": threshold_95}
    """
    rng = DeterministicRNG(seed)
    data = np.asarray(data, dtype=float)
    labels = np.asarray(labels)
    n_obs, n_comp = data.shape

    # Observed statistics (mean difference for each comparison)
    obs_stats = np.zeros(n_comp)
    for c in range(n_comp):
        g1 = data[labels == 0, c]
        g2 = data[labels == 1, c]
        obs_stats[c] = np.mean(g1) - np.mean(g2)

    # Permutation distribution of max |statistic|
    max_stats = np.zeros(n_permutations)
    for i in range(n_permutations):
        perm_labels = rng.permutation(labels)
        perm_stats = np.zeros(n_comp)
        for c in range(n_comp):
            g1 = data[perm_labels == 0, c]
            g2 = data[perm_labels == 1, c]
            if len(g1) > 0 and len(g2) > 0:
                perm_stats[c] = np.mean(g1) - np.mean(g2)
        max_stats[i] = np.max(np.abs(perm_stats))

    threshold_95 = float(np.percentile(max_stats, 95))
    corrected_p = np.zeros(n_comp)
    for c in range(n_comp):
        corrected_p[c] = float(np.mean(max_stats >= np.abs(obs_stats[c])))

    return {
        "statistics": obs_stats,
        "p_values": corrected_p,
        "threshold_95": threshold_95,
        "n_permutations": n_permutations
    }


def cluster_based_permutation_test(
    data1: np.ndarray,
    data2: np.ndarray,
    threshold: float = 0.05,
    n_permutations: int = 1000,
    seed: int = 42
) -> Dict[str, Any]:
    """Cluster-based permutation test (Maris & Oostenveld 2007).

    For EEG time-frequency data: finds clusters of adjacent significant
    time-frequency points, computes cluster mass, and tests against
    permutation distribution of max cluster mass.

    Args:
        data1: (n_subjects1, n_time, n_freq) — condition 1
        data2: (n_subjects2, n_time, n_freq) — condition 2
        threshold: p-value threshold for cluster-forming
        n_permutations: Number of permutations
        seed: Random seed

    Returns:
        {"n_clusters": int, "cluster_masses": list, "p_values": list, "n_permutations": n}
    """
    rng = DeterministicRNG(seed)
    data1 = np.asarray(data1, dtype=float)
    data2 = np.asarray(data2, dtype=float)

    n_time, n_freq = data1.shape[1], data1.shape[2]
    t_obs = np.zeros((n_time, n_freq))
    p_obs = np.zeros((n_time, n_freq))
    for t in range(n_time):
        for f in range(n_freq):
            t_stat, p_val = stats.ttest_ind(data1[:, t, f], data2[:, t, f])
            t_obs[t, f] = t_stat
            p_obs[t, f] = p_val

    # Find clusters (adjacent significant points)
    significant = p_obs < threshold
    labeled, n_clusters = label(significant)

    cluster_masses = []
    for c in range(1, n_clusters + 1):
        mass = float(np.sum(np.abs(t_obs[labeled == c])))
        cluster_masses.append(mass)

    combined = np.concatenate([data1, data2], axis=0)
    n1 = data1.shape[0]
    max_cluster_masses = np.zeros(n_permutations)

    for i in range(n_permutations):
        perm_idx = rng.permutation(len(combined))
        perm1 = combined[perm_idx[:n1]]
        perm2 = combined[perm_idx[n1:]]

        t_perm = np.zeros((n_time, n_freq))
        p_perm = np.zeros((n_time, n_freq))
        for t in range(n_time):
            for f in range(n_freq):
                t_stat, p_val = stats.ttest_ind(perm1[:, t, f], perm2[:, t, f])
                t_perm[t, f] = t_stat
                p_perm[t, f] = p_val
        sig_perm = p_perm < threshold
        labeled_perm, n_clust_perm = label(sig_perm)
        if n_clust_perm > 0:
            masses = [np.sum(np.abs(t_perm[labeled_perm == c])) for c in range(1, n_clust_perm + 1)]
            max_cluster_masses[i] = max(masses)

    cluster_p_values = []
    for mass in cluster_masses:
        p = float(np.mean(max_cluster_masses >= mass))
        cluster_p_values.append(p)

    return {
        "n_clusters": n_clusters,
        "cluster_masses": cluster_masses,
        "p_values": cluster_p_values,
        "n_permutations": n_permutations
    }
