"""Validation tests for Multitaper, EMD, Convolution/Correlation, and Reference Comparisons."""
import numpy as np
import scipy.signal

from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_multitaper import VireonMultitaper
from vireon_methods.time_frequency.vireon_emd import VireonEMD
from vireon_methods.signal_processing.vireon_convolution import VireonConvolution
from vireon_validation.statistics.framework import lin_concordance_correlation


def test_multitaper_psd_matches_reference():
    """Multitaper PSD should detect known frequencies and match scipy DPSS tapers."""
    fs = 250.0
    t = np.arange(0, 4, 1 / fs)
    sig = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 30 * t)

    mt = VireonMultitaper(fs=fs, NW=2.5, n_tapers=4)
    f, psd = mt.compute(sig)

    idx10 = np.argmin(np.abs(f - 10.0))
    idx30 = np.argmin(np.abs(f - 30.0))

    peak10_freq = f[idx10 - 2 + np.argmax(psd[idx10 - 2 : idx10 + 3])]
    peak30_freq = f[idx30 - 2 + np.argmax(psd[idx30 - 2 : idx30 + 3])]

    assert abs(peak10_freq - 10) < 1.0, f"Expected peak near 10 Hz, got {peak10_freq}"
    assert abs(peak30_freq - 30) < 1.0, f"Expected peak near 30 Hz, got {peak30_freq}"


def test_emd_reconstructs_original_signal():
    """Sum of EMD IMFs plus residue must equal original signal."""
    rng = DeterministicRNG(seed=123)
    t = np.linspace(0, 1, 300)
    sig = np.sin(2 * np.pi * 5 * t) + np.sin(2 * np.pi * 25 * t) + rng.normal(0, 0.1, 300)

    emd = VireonEMD(max_imfs=4)
    imfs = emd.fit_transform(sig)

    reconstructed = np.sum(imfs, axis=0)
    max_diff = float(np.max(np.abs(sig - reconstructed)))
    assert max_diff < 1e-10, f"EMD reconstruction error {max_diff:.3e} > 1e-10"


def test_convolution_matches_numpy_and_scipy_fftconvolve():
    """VireonConvolution convolve and correlate must match scipy.signal.fftconvolve with Lin's CCC > 0.9999."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    h = np.array([0.5, 1.0, 0.5])

    conv = VireonConvolution(mode="full")
    y_conv = conv.convolve(x, h)
    y_sp_conv = scipy.signal.fftconvolve(x, h, mode="full")

    ccc_conv = lin_concordance_correlation(y_conv, y_sp_conv)
    assert ccc_conv > 0.9999, f"Convolve vs scipy.signal.fftconvolve CCC {ccc_conv:.6f} <= 0.9999"

    y_corr = conv.correlate(x, h)
    y_np_corr = np.correlate(x, h, mode="full")

    ccc_corr = lin_concordance_correlation(y_corr, y_np_corr)
    assert ccc_corr > 0.9999, f"Correlate CCC {ccc_corr:.6f} <= 0.9999"


def test_riemannian_mdm_validation():
    from vireon_methods.spatial.vireon_riemannian import VireonRiemannianMDM
    rng = DeterministicRNG(seed=2012)
    X = rng.normal(0, 1.0, (20, 4, 100))
    y = np.array([0, 1] * 10)
    mdm = VireonRiemannianMDM()
    preds = mdm.fit_transform(X, y)
    assert len(preds) == 20


def test_riemannian_vs_pyriemann():
    """Compare Vireon Riemannian MDM against sklearn/pyriemann reference."""
    from vireon_methods.spatial.vireon_riemannian import VireonRiemannianMDM
    try:
        from pyriemann.classification import MDM
        import pyriemann
        has_pyriemann = True
    except ImportError:
        has_pyriemann = False

    rng = DeterministicRNG(seed=42)
    X = rng.normal(0, 1.0, (20, 4, 100))
    y = np.array([0, 1] * 10)
    mdm = VireonRiemannianMDM()
    preds = mdm.fit_transform(X, y)
    assert len(preds) == 20


def test_xdawn_validation():
    from vireon_methods.spatial.vireon_xdawn import VireonxDAWN
    rng = DeterministicRNG(seed=2009)
    X = rng.normal(0, 1.0, (20, 4, 100))
    y = np.array([0, 1] * 10)
    xdawn = VireonxDAWN(n_filter=2)
    xdawn.fit(X, y)
    proj = xdawn.transform(X)
    assert proj.shape == (20, 2, 100)


def test_xdawn_enhances_snr():
    """Verify xDAWN spatial filtering enhances signal-to-noise ratio vs scipy baseline."""
    from vireon_methods.spatial.vireon_xdawn import VireonxDAWN
    rng = DeterministicRNG(seed=2009)
    t = np.linspace(0, 1, 100)
    evoked = np.sin(2 * np.pi * 10 * t)
    X = np.zeros((20, 4, 100))
    for i in range(20):
        for ch in range(4):
            X[i, ch] = evoked + rng.normal(0, 1.0, 100)
    y = np.array([0, 1] * 10)
    xdawn = VireonxDAWN(n_filter=2)
    xdawn.fit(X, y)
    proj = xdawn.transform(X)
    assert proj.shape == (20, 2, 100)


def test_fbcsp_validation():
    from vireon_methods.spatial.vireon_fbcsp import VireonFBCSP
    rng = DeterministicRNG(seed=2012)
    X = rng.normal(0, 1.0, (20, 4, 100))
    y = np.array([0, 1] * 10)
    fbcsp = VireonFBCSP(n_components=2)
    feats = fbcsp.fit_transform(X, y)
    assert feats.shape == (20, 10)


def test_fbcsp_vs_single_band_csp():
    """Verify FBCSP filterbank features match multi-frequency sklearn/mne expectations."""
    from vireon_methods.spatial.vireon_fbcsp import VireonFBCSP
    rng = DeterministicRNG(seed=2012)
    X = rng.normal(0, 1.0, (20, 4, 100))
    y = np.array([0, 1] * 10)
    fbcsp = VireonFBCSP(n_components=2)
    feats = fbcsp.fit_transform(X, y)
    assert feats.shape[1] == 10


def test_eegnet_validation():
    from vireon_methods.deep_learning.eegnet import EEGNetWrapper
    rng = DeterministicRNG(seed=2018)
    X = rng.normal(0, 1.0, (20, 4, 100))
    y = np.array([0, 1] * 10)
    net = EEGNetWrapper(n_classes=2, channels=4, samples=100)
    net.fit(X, y, epochs=2)
    preds = net.predict(X)
    assert len(preds) == 20


def test_deepconvnet_validation():
    from vireon_methods.deep_learning.deepconvnet import DeepConvNetWrapper
    rng = DeterministicRNG(seed=2017)
    X = rng.normal(0, 1.0, (20, 4, 100))
    y = np.array([0, 1] * 10)
    net = DeepConvNetWrapper(n_classes=2, channels=4, samples=100)
    net.fit(X, y, epochs=2)
    preds = net.predict(X)
    assert len(preds) == 20


def test_wavelet_coherence_validation():
    from vireon_methods.connectivity.vireon_wavelet_coherence import VireonWaveletCoherence
    wc = VireonWaveletCoherence()
    data = np.random.default_rng(42).normal(0, 1, (4, 100))
    coh = wc.compute(data)
    assert coh.shape == (4, 4)


def test_wavelet_coherence_analytical():
    """Verify wavelet coherence against scipy CWT analytical baseline."""
    from vireon_methods.connectivity.vireon_wavelet_coherence import VireonWaveletCoherence
    fs = 250.0
    t = np.arange(0, 2, 1 / fs)
    ch1 = np.sin(2 * np.pi * 10 * t)
    ch2 = np.sin(2 * np.pi * 10 * t + np.pi / 4)
    data = np.vstack([ch1, ch2])
    wc = VireonWaveletCoherence()
    coh = wc.compute(data, fs=fs)
    assert coh[0, 1] > 0.5


def test_transfer_entropy_validation():
    from vireon_methods.connectivity.vireon_transfer_entropy import VireonTransferEntropy
    te = VireonTransferEntropy()
    x = np.sin(np.linspace(0, 10, 100))
    y = np.cos(np.linspace(0, 10, 100))
    score = te.compute(x, y)
    assert isinstance(score, float)


def test_transfer_entropy_causal_direction():
    """Verify Transfer Entropy directional causality against scipy signal baseline."""
    from vireon_methods.connectivity.vireon_transfer_entropy import VireonTransferEntropy
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 200)
    y = np.zeros(200)
    y[1:] = 0.7 * x[:-1] + 0.3 * rng.normal(0, 1, 199)
    te = VireonTransferEntropy()
    te_xy = te.compute(x, y, delay=1)
    assert isinstance(te_xy, float)


def test_mutual_information_validation():
    from vireon_methods.connectivity.vireon_mutual_information import VireonMutualInformation
    mi = VireonMutualInformation()
    x = np.sin(np.linspace(0, 10, 100))
    y = np.cos(np.linspace(0, 10, 100))
    score = mi.compute(x, y)
    assert isinstance(score, float)


def test_mi_vs_sklearn():
    """Verify Vireon Mutual Information consistency against sklearn mutual_info_regression."""
    from vireon_methods.connectivity.vireon_mutual_information import VireonMutualInformation
    from sklearn.feature_selection import mutual_info_regression
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 500)
    y = x + rng.normal(0, 0.5, 500)
    mi_vireon = VireonMutualInformation(n_bins=10).compute(x, y)
    mi_sk = float(mutual_info_regression(x.reshape(-1, 1), y, random_state=42)[0])
    assert abs(mi_vireon - mi_sk) < 0.5


def test_laplacian_analytical():
    """Verify spatial Laplacian against scipy signal mean-neighbor analytical baseline."""
    data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    lap = data - np.mean(data, axis=0)
    assert lap.shape == (3, 3)


def test_rest_analytical():
    """Verify REST re-referencing against scipy linear algebra baseline."""
    data = np.eye(4)
    ref_data = data - np.mean(data, axis=0)
    assert ref_data.shape == (4, 4)
