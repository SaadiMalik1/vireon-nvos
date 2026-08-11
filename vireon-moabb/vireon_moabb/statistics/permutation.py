import numpy as np

class SubjectLevelPermutation:
    """Permutation test for subject-level accuracy against chance."""

    def __init__(self, n_permutations: int = 1000, seed: int = 42):
        self.n_permutations = n_permutations
        self.seed = seed

    def test(self, accuracies: list[float], chance_level: float = 0.5) -> float:
        """Compute p-value of accuracies against chance_level."""
        if not accuracies:
            return 1.0
            
        rng = np.random.default_rng(self.seed)
        acc = np.array(accuracies)
        obs_mean = np.mean(acc)
        
        # Simple permutation test: flip signs of (acc - chance)
        diff = acc - chance_level
        n = len(acc)
        
        count = 0
        for _ in range(self.n_permutations):
            signs = rng.choice([-1, 1], size=n)
            perm_mean = np.mean(signs * diff) + chance_level
            if perm_mean >= obs_mean:
                count += 1
                
        return count / self.n_permutations
