import numpy as np
from scipy.spatial.distance import cdist
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonLaplacian:
    """
    Surface Laplacian (Current Source Density).
    """
    def __init__(self, channel_positions: np.ndarray, n_neighbors: int = 4):
        if channel_positions is None:
            raise ValueError("channel_positions cannot be None")
        if not isinstance(channel_positions, np.ndarray):
            channel_positions = np.array(channel_positions)
        self.channel_positions = channel_positions
        self.n_neighbors = n_neighbors

    def apply(self, data: np.ndarray) -> np.ndarray:
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            raise ScientificContractViolation(
                "NaN or Inf detected.", 
                violated_assumption="finite_values", 
                details="Input contains non-finite values.", 
                remediation="Clean the data before processing."
            )
            
        n_channels = data.shape[0]
        if self.channel_positions.shape[0] != n_channels:
            raise ValueError(f"channel_positions must have {n_channels} rows.")
            
        dists = cdist(self.channel_positions, self.channel_positions)
        np.fill_diagonal(dists, np.inf)
        
        laplacian_data = np.zeros_like(data)
        for i in range(n_channels):
            neighbors = np.argsort(dists[i])[:self.n_neighbors]
            laplacian_data[i] = data[i] - np.mean(data[neighbors], axis=0)
            
        return laplacian_data

class VireonREST:
    """
    Reference Electrode Standardization Technique (REST).
    """
    def __init__(self, leadfield: np.ndarray):
        if leadfield is None:
            raise ValueError("leadfield cannot be None")
        if not isinstance(leadfield, np.ndarray):
            leadfield = np.array(leadfield)
        self.L = leadfield

    def apply(self, data: np.ndarray) -> np.ndarray:
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            raise ScientificContractViolation(
                "NaN or Inf detected.", 
                violated_assumption="finite_values", 
                details="Input contains non-finite values.", 
                remediation="Clean the data before processing."
            )
            
        L = self.L
        Lt_L = L.T @ L
        Lt_data = L.T @ data
        
        try:
            S = np.linalg.solve(Lt_L, Lt_data)
        except np.linalg.LinAlgError:
            S = np.linalg.pinv(L) @ data
            
        data_rest = L @ S
        return data_rest
