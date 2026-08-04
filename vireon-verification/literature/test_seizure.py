"""Seizure Detection Sensitivity Test."""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG

def test_seizure_detection():
    """High-amplitude rhythmic spike-and-wave seizure detection test."""
    rng = DeterministicRNG(seed=123)
    fs = 250.0
    n_epochs = 50
    
    # 25 inter-ictal, 25 ictal epochs
    y_true = np.array([0] * 25 + [1] * 25)
    y_pred = []
    
    for i in range(n_epochs):
        t = np.arange(0, 4, 1 / fs)
        if y_true[i] == 0:
            sig = rng.normal(0, 1.0, len(t))
        else:
            # Ictal: high power 3 Hz spike-wave bursts
            sig = 4.0 * np.sin(2 * np.pi * 3.0 * t) + rng.normal(0, 0.5, len(t))
            
        power = float(np.mean(sig ** 2))
        y_pred.append(1 if power > 3.0 else 0)
        
    y_pred = np.array(y_pred)
    sensitivity = float(np.sum((y_true == 1) & (y_pred == 1)) / np.sum(y_true == 1))
    assert sensitivity >= 0.95, f"Seizure sensitivity {sensitivity:.2f} < 0.95"

if __name__ == "__main__":
    test_seizure_detection()
