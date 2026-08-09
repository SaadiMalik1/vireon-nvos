import numpy as np


def lin_concordance_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """Lin's Concordance Correlation Coefficient (CCC).
    
    Reference: Lin, L. I. (1989). A concordance correlation coefficient to evaluate reproducibility.
    Biometrics, 45(1), 255-268.
    """
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    if np.array_equal(x, y):
        return 1.0
    x_m = np.mean(x)
    y_m = np.mean(y)
    x_v = np.var(x, ddof=1) if len(x) > 1 else np.var(x)
    y_v = np.var(y, ddof=1) if len(y) > 1 else np.var(y)
    if x_v == 0.0 and y_v == 0.0:
        return 1.0 if x_m == y_m else 0.0
    cov = np.cov(x, y)[0, 1] if len(x) > 1 else 0.0
    denom = x_v + y_v + (x_m - y_m) ** 2
    if denom == 0.0:
        return 0.0
    return float(2.0 * cov / denom)


class StatisticalFramework:
    """
    Publishable biostatistical validation framework (Phase D).
    """

    @staticmethod
    def lin_concordance_correlation(x: np.ndarray, y: np.ndarray) -> float:
        return lin_concordance_correlation(x, y)
    
    @staticmethod
    def bland_altman_agreement(method_a: np.ndarray, method_b: np.ndarray) -> dict:
        np.mean([method_a, method_b], axis=0)
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
        np.sum((ratings - mean_per_subject[:, None])**2)
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
    def bayesian_credible_interval(data: np.ndarray, prior_mean: float = 0.0, 
                                   prior_var: float = 1e6, cred_mass: float = 0.95) -> dict:
        """
        Bayesian credible interval using conjugate normal-normal model.
        
        Posterior: N(mu_post, var_post) where:
        var_post = 1 / (1/prior_var + n/data_var)
        mu_post = var_post * (prior_mean/prior_var + n*mean/data_var)
        """
        import scipy.stats
        data = np.asarray(data)
        n = len(data)
        if n == 0:
            return {
                "posterior_mean": float(prior_mean),
                "posterior_var": float(prior_var),
                "credible_interval": [float(prior_mean), float(prior_mean)],
                "cred_mass": float(cred_mass)
            }
            
        data_var = float(np.var(data, ddof=1)) if n > 1 else 1.0
        if data_var == 0.0:
            data_var = 1e-10
        data_mean = float(np.mean(data))
        
        var_post = 1.0 / (1.0 / prior_var + n / data_var)
        mu_post = var_post * (prior_mean / prior_var + n * data_mean / data_var)
        
        alpha = (1.0 - cred_mass) / 2.0
        ci_lower = mu_post + scipy.stats.norm.ppf(alpha) * np.sqrt(var_post)
        ci_upper = mu_post + scipy.stats.norm.ppf(1.0 - alpha) * np.sqrt(var_post)
        
        return {
            "posterior_mean": float(mu_post),
            "posterior_var": float(var_post),
            "credible_interval": [float(ci_lower), float(ci_upper)],
            "cred_mass": float(cred_mass)
        }

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

    @staticmethod
    def matthews_correlation_coefficient(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """MCC.

        Reference: Matthews (1975). Comparison of the predicted and observed secondary
        structure of T4 phage lysozyme. Biochimica et Biophysica Acta, 405(2), 442-451.
        """
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)
        tp = np.sum((y_true == 1) & (y_pred == 1))
        tn = np.sum((y_true == 0) & (y_pred == 0))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        
        numerator = tp * tn - fp * fn
        denominator = np.sqrt(float((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)))
        
        if denominator == 0:
            return 0.0
        return float(numerator / denominator)
