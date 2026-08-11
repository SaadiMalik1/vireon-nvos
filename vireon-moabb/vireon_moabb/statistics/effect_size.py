import numpy as np

class CohensD:
    """Compute Cohen's d effect size."""

    @staticmethod
    def compute(group1: list[float], group2: list[float]) -> float:
        """Compute Cohen's d between two groups."""
        if not group1 or not group2:
            return 0.0
            
        a, b = np.array(group1), np.array(group2)
        n1, n2 = len(a), len(b)
        var1, var2 = np.var(a, ddof=1), np.var(b, ddof=1)
        
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        if pooled_std == 0:
            return 0.0
            
        return (np.mean(a) - np.mean(b)) / pooled_std


class HedgesG:
    """Compute Hedges' g effect size (corrected for small samples)."""

    @staticmethod
    def compute(group1: list[float], group2: list[float]) -> float:
        d = CohensD.compute(group1, group2)
        n = len(group1) + len(group2)
        
        # Approximation of the correction factor
        correction = 1.0 - (3.0 / (4 * n - 9)) if n > 3 else 1.0
        return d * correction
