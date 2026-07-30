import numpy as np

class LeadfieldProjector:
    """
    Simulates the volume conduction (Forward Model) from source space to sensor space.
    """
    def __init__(self, num_sources: int, num_sensors: int, seed: int = 42):
        self.num_sources = num_sources
        self.num_sensors = num_sensors
        self.rng = np.random.default_rng(seed)
        
        # Simple random mixing matrix (Leadfield matrix)
        # In a real model, this would be computed via BEM/FEM on an anatomical MRI.
        self.mixing_matrix = self.rng.uniform(0.1, 1.0, (num_sensors, num_sources)).astype(np.float32)

    def project(self, source_signals: np.ndarray) -> np.ndarray:
        """
        Projects source signals (samples, sources) to sensor signals (samples, sensors).
        """
        # source_signals: (N, num_sources)
        # mixing_matrix: (num_sensors, num_sources)
        # result: (N, num_sensors)
        return source_signals @ self.mixing_matrix.T
