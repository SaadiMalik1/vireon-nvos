import numpy as np

def compare_welch_with_mne(vireon_psd, mne_psd, tolerance=1e-5):
    """
    Numerically compares VIREON's Welch implementation with MNE-Python's.
    Returns True if the results agree within the specified tolerance.
    """
    diff = np.abs(vireon_psd - mne_psd)
    max_diff = np.max(diff)
    
    if max_diff < tolerance:
        print(f"Agreement confirmed. Max difference {max_diff} is below tolerance {tolerance}.")
        return True
    else:
        print(f"Agreement failed! Max difference {max_diff} exceeds tolerance {tolerance}.")
        return False
