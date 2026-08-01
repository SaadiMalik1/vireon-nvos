import numpy as np

class StatisticalFramework:
    """
    Publishable biostatistical validation framework (Phase D).
    """
    
    @staticmethod
    def bland_altman_agreement(method_a: np.ndarray, method_b: np.ndarray) -> dict:
        mean = np.mean([method_a, method_b], axis=0)
        diff = method_a - method_b
        md = np.mean(diff)
        sd = np.std(diff, axis=0)
        return {
            "mean_difference": md,
            "limits_of_agreement": (md - 1.96 * sd, md + 1.96 * sd)
        }
        
    @staticmethod
    def intraclass_correlation(ratings: np.ndarray) -> float:
        """
        Shrout & Fleiss (1979) ICC(2,1).
        ratings shape: (n_subjects, n_raters).
        """
        n, k = ratings.shape
        mean_per_subject = ratings.mean(axis=1)
        mean_per_rater = ratings.mean(axis=0)
        grand_mean = ratings.mean()

        ss_between = n * np.sum((mean_per_rater - grand_mean)**2)
        ss_within = np.sum((ratings - mean_per_subject[:, None])**2)
        ss_subjects = k * np.sum((mean_per_subject - grand_mean)**2)
        ss_total = np.sum((ratings - grand_mean)**2)
        ss_residual = ss_total - ss_subjects - ss_between

        ms_subjects = ss_subjects / (n - 1)
        ms_raters = ss_between / (k - 1)
        ms_residual = ss_residual / ((n - 1) * (k - 1))

        icc = (ms_subjects - ms_residual) / (ms_subjects + (k - 1) * ms_residual + k * (ms_raters - ms_residual) / n)
        return float(icc)
        
    @staticmethod
    def kolmogorov_smirnov(data_a: np.ndarray, data_b: np.ndarray) -> dict:
        from scipy.stats import ks_2samp
        stat, pval = ks_2samp(data_a, data_b)
        return {"statistic": stat, "p_value": pval}
        
    @staticmethod
    def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        pooled_se = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        return (np.mean(group1) - np.mean(group2)) / pooled_se
        
    @staticmethod
    def bayesian_credible_interval(data: np.ndarray, confidence: float = 0.95) -> tuple:
        # Stub for Bayesian posterior sampling
        mean = np.mean(data)
        std = np.std(data)
        return (mean - 1.96 * std, mean + 1.96 * std)

    @staticmethod
    def passing_bablok(x: np.ndarray, y: np.ndarray) -> dict:
        """Passing-Bablok regression for method comparison.

        Reference: Passing & Bablok (1983). A new biometrical procedure for testing
        the equality of measurements from two different analytical methods.
        Journal of Clinical Chemistry and Clinical Biochemistry, 21(11), 709-720.
        """
        if np.any(np.isnan(x)) or np.any(np.isnan(y)):
            raise ValueError("NaN values not supported")
        n = len(x)
        slopes = []
        for i in range(n):
            for j in range(i+1, n):
                if x[j] != x[i]:
                    slopes.append((y[j] - y[i]) / (x[j] - x[i]))
        slopes = np.sort(slopes)
        b = np.median(slopes)
        a = np.median(y - b * x)

        import scipy.stats
        k = len(slopes)
        c_gamma = scipy.stats.norm.ppf(0.975) * np.sqrt(n * (n - 1) * (2 * n + 5) / 18)
        m1 = int(np.round((k - c_gamma) / 2))
        m2 = int(np.round(k - m1 + 1))

        m1 = max(0, min(m1, k - 1))
        m2 = max(0, min(m2 - 1, k - 1))

        b_low, b_high = slopes[m1], slopes[m2]
        a_low, a_high = np.median(y - b_high * x), np.median(y - b_low * x)

        return {
            "slope": float(b),
            "intercept": float(a),
            "ci_slope": [float(b_low), float(b_high)],
            "ci_intercept": [float(min(a_low, a_high)), float(max(a_low, a_high))]
        }
