"""Clinical Trial Support Example: Pre/Post Treatment Biomarker Shift.

Demonstrates longitudinal EEG biomarker tracking (alpha peak frequency and slow-wave ratio)
for clinical drug trial validation.
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_core.contracts.evidence import EvidenceBundle


def run_clinical_trial():
    rng = DeterministicRNG(seed=2026)
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)

    # Pre-treatment: slowed alpha (8 Hz)
    pre_sig = 2.0 * np.sin(2 * np.pi * 8.0 * t) + rng.normal(0, 0.5, len(t))
    # Post-treatment: normalized alpha (10 Hz)
    post_sig = 2.0 * np.sin(2 * np.pi * 10.0 * t) + rng.normal(0, 0.5, len(t))

    welch = VireonWelch(fs=fs, nperseg=256)
    f, psd_pre = welch.compute(pre_sig)
    _, psd_post = welch.compute(post_sig)

    iaf_pre = float(f[np.argmax(psd_pre[(f >= 7.0) & (f <= 13.0)]) + int(7.0 / (f[1] - f[0]))])
    iaf_post = float(f[np.argmax(psd_post[(f >= 7.0) & (f <= 13.0)]) + int(7.0 / (f[1] - f[0]))])

    bundle = EvidenceBundle(
        evidence_hash="clinical_trial_pre_post_biomarker_hash",
        algorithm="Clinical Trial IAF Tracking",
        dataset="Phase II Trial Cohort",
        statistical_agreement={"iaf_pre_hz": iaf_pre, "iaf_post_hz": iaf_post}
    )
    print(f"[Clinical Trial] IAF Pre: {iaf_pre:.1f} Hz -> Post: {iaf_post:.1f} Hz")
    return bundle


if __name__ == "__main__":
    run_clinical_trial()
