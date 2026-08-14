"""Rivet et al. (2009) xDAWN ERP Enhancement Literature Test.

Reference: Rivet, B., Cecotti, H., Souloumiac, A., Maby, E., & Mattout, J. (2009). xDAWN algorithm to enhance evoked potentials: application to brain-computer interfaces. IEEE Transactions on Biomedical Engineering, 56(8), 2035-2043.
DOI: 10.1109/TBME.2009.2019709
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_xdawn import VireonxDAWN


def test_rivet_2009():
    rng = DeterministicRNG(seed=2009)
    n_epochs, n_channels, n_samples = 30, 8, 250
    X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))

    # Inject an ERP response (event-related potential) into target epochs:
    # a positive deflection ~100 ms after epoch onset on channels 0-1.
    # xDAWN is designed to maximize the SNR of this evoked response by
    # finding a spatial filter that maximizes the ratio of target-signal
    # covariance to total-signal covariance.
    t = np.arange(n_samples) / 250.0
    erp_pattern = 3.0 * np.exp(-((t - 0.1) ** 2) / 0.002)
    for i in range(n_epochs):
        if y[i] == 1:
            X[i, 0:2] += erp_pattern

    xdawn = VireonxDAWN(n_filter=2)
    xdawn.fit(X, y)
    proj = xdawn.transform(X)
    assert proj.shape == (30, 2, 250)

    # Strengthened falsifiable assertion: xDAWN should enhance the ERP
    # signal-to-noise ratio — the projected target epochs (y==1) should
    # exhibit larger peak variance at the ERP latency (~100 ms) than the
    # projected non-target epochs (y==0). Compute the per-class variance of
    # the projected epochs at the ERP time sample and assert target > non-target.
    erp_sample = int(0.1 * 250)  # ~100 ms
    window = slice(max(erp_sample - 5, 0), erp_sample + 6)
    proj_target_var = float(np.var(proj[y == 1, :, window].mean(axis=2)))
    proj_nontarget_var = float(np.var(proj[y == 0, :, window].mean(axis=2)))
    assert proj_target_var > proj_nontarget_var, (
        f"xDAWN projected target variance {proj_target_var:.3f} not > "
        f"non-target variance {proj_nontarget_var:.3f} at ERP latency — "
        "xDAWN failed to enhance ERP SNR"
    )

    # The evoked (averaged) target response should also have larger amplitude
    # than the evoked non-target response in the projected space.
    evoked_target = proj[y == 1].mean(axis=0)
    evoked_nontarget = proj[y == 0].mean(axis=0)
    target_amp = float(np.max(np.abs(evoked_target)))
    nontarget_amp = float(np.max(np.abs(evoked_nontarget)))
    assert target_amp > nontarget_amp, (
        f"xDAWN evoked target amplitude {target_amp:.3f} not > "
        f"non-target amplitude {nontarget_amp:.3f} — "
        "xDAWN failed to enhance the target ERP amplitude"
    )


if __name__ == "__main__":
    test_rivet_2009()
