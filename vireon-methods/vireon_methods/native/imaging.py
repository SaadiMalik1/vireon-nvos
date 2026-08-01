import numpy as np

class VireonForwardModel:
    """
    Native VIREON implementation of Forward Modeling.
    (Stage 4.2)
    """
    plugin_id = "vireon.methods.imaging.forward"
    version = "1.0.0"
    
    def __init__(self, head_model: str = "fsaverage", conductivity: tuple = (0.3, 0.006, 0.3)):
        self.head_model = head_model
        self.conductivity = conductivity
        
    def compute_leadfield(self, source_space: np.ndarray, sensor_geometry: np.ndarray) -> np.ndarray:
        # Stub: Return random leadfield matrix mapping sources to sensors
        n_sensors = sensor_geometry.shape[0]
        n_sources = source_space.shape[0]
        return np.random.normal(0, 1, size=(n_sensors, n_sources))

class VireonMinimumNorm:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Use vireon_methods.source_localization.vireon_source_localization.VireonMinimumNorm")

class VireonLCMV:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Use vireon_methods.source_localization.vireon_beamforming.VireonLCMV")
