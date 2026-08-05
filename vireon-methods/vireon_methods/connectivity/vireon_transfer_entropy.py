"""Transfer Entropy Directional Connectivity Estimator.

Reference: Schreiber, T. (2000). Measuring information transfer. Physical Review Letters, 85(2), 461-464.
DOI: 10.1103/PhysRevLett.85.461
"""
import numpy as np


class VireonTransferEntropy:
    """Non-parametric Transfer Entropy estimator measuring directional information flow TE_{X->Y}."""
    
    def compute(self, x: np.ndarray, y: np.ndarray, delay: int = 1) -> float:
        """Compute Transfer Entropy TE_{X -> Y} conditioning on past states y_past and x_past."""
        n_samples = len(x)
        if n_samples <= delay:
            return 0.0
            
        # Target current state, target past history, source past history
        y_curr = y[delay:]
        y_past = y[:-delay]
        x_past = x[:-delay]
        
        # Calculate covariance matrix over joint vector [y_curr, y_past, x_past]
        joint_matrix = np.vstack([y_curr, y_past, x_past])
        cov_joint = np.cov(joint_matrix)
        
        # Marginal covariance matrix over [y_curr, y_past]
        cov_y_joint = np.cov(np.vstack([y_curr, y_past]))
        
        # Marginal covariance matrix over [y_past, x_past]
        cov_past = np.cov(np.vstack([y_past, x_past]))
        
        # Variance of y_past
        var_y_past = float(np.var(y_past))
        
        # Determinant calculations for Gaussian conditional entropy: TE = 0.5 * log( (det(C_y_past) * det(C_past)) / (det(C_y_past_alone) * det(C_joint)) )
        det_joint = max(1e-10, float(np.linalg.det(cov_joint)))
        det_y_joint = max(1e-10, float(np.linalg.det(cov_y_joint)))
        det_past = max(1e-10, float(np.linalg.det(cov_past)))
        
        # Conditional transfer entropy formula
        te_score = 0.5 * np.log((det_y_joint * det_past) / (var_y_past * det_joint + 1e-10) + 1e-10)
        return float(max(0.0, te_score))
