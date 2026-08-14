"""Educational Tutorial Example: EEG Fundamentals & Spectral Analysis.

Demonstrates educational pipeline explaining sampling rates, Nyquist theorem,
and spectral power estimation.
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_core.contracts.evidence import EvidenceBundle


def run_educational_tutorial():
    rng = DeterministicRNG(seed=101)
    fs = 250.0
    t = np.arange(0, 5, 1 / fs)

    # 10 Hz Alpha wave
    sig = 2.0 * np.sin(2 * np.pi * 10.0 * t) + rng.normal(0, 0.2, len(t))

    welch = VireonWelch(fs=fs, nperseg=256)
    f, psd = welch.compute(sig)

    peak_freq = float(f[np.argmax(psd)])

    bundle = EvidenceBundle(
        evidence_hash="educational_eeg_fundamentals_hash",
        algorithm="Educational EEG Tutorial",
        dataset="Synthetic Alpha Wave",
        statistical_agreement={"detected_peak_hz": peak_freq}
    )
    print(f"[Educational Tutorial] Detected Peak Frequency: {peak_freq:.1f} Hz (Expected: 10.0 Hz)")
    return bundle


if __name__ == "__main__":
    run_educational_tutorial()
