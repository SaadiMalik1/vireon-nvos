import numpy as np

class SubjectLevelBootstrap:
    """Bootstrap confidence intervals for subject-level accuracies."""

    def __init__(self, n_iterations: int = 1000, seed: int = 42):
        self.n_iterations = n_iterations
        self.seed = seed

    def compute_ci(self, accuracies: list[float], alpha: float = 0.05) -> tuple[float, float]:
        """Compute the (1-alpha) confidence interval."""
        if not accuracies:
            return (0.0, 0.0)
            
        rng = np.random.default_rng(self.seed)
        acc = np.array(accuracies)
        n = len(acc)
        
        means = []
        for _ in range(self.n_iterations):
            sample = rng.choice(acc, size=n, replace=True)
            means.append(np.mean(sample))
            
        means = np.sort(means)
        lower_idx = int(self.n_iterations * (alpha / 2))
        upper_idx = int(self.n_iterations * (1 - alpha / 2))
        
        return (float(means[lower_idx]), float(means[upper_idx]))
