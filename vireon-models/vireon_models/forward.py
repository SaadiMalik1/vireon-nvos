import numpy as np
from vireon_core.runtime.rng import DeterministicRNG

class RandomMixingMatrix:
    """
    Test fixture, not a forward model.
    Simulates a random volume conduction mixing matrix.
    """
    def __init__(self, num_sources: int, num_sensors: int, seed: int = 42):
        self.num_sources = num_sources
        self.num_sensors = num_sensors
        self.rng = DeterministicRNG(seed)
        
        # Simulate random locations in a bounding box [-10, 10]
        source_locs = self.rng.uniform(-10, 10, (num_sources, 3))
        sensor_locs = self.rng.uniform(-10, 10, (num_sensors, 3))
        
        # Calculate inverse-square distance for leadfield spatial decay
        mixing_matrix = np.zeros((num_sensors, num_sources), dtype=np.float32)
        for i in range(num_sensors):
            for j in range(num_sources):
                dist = np.linalg.norm(sensor_locs[i] - source_locs[j])
                # Avoid division by zero, add small epsilon and scale
                mixing_matrix[i, j] = 1.0 / (dist**2 + 0.1)
                
        self.mixing_matrix = mixing_matrix

    def project(self, source_signals: np.ndarray) -> np.ndarray:
        """
        Projects source signals (samples, sources) to sensor signals (samples, sensors).
        """
        # source_signals: (N, num_sources)
        # mixing_matrix: (num_sensors, num_sources)
        # result: (N, num_sensors)
        return source_signals @ self.mixing_matrix.T
