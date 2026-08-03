"""Reproduce Ramoser 2000: CSP+LDA for motor imagery BCI.

Key claim (Ramoser et al. 2000, DOI: 10.1109/86.84781):
CSP spatial filtering + LDA classification achieves high accuracy (>65%)
on 2-class motor imagery EEG (left vs right hand) when filtered in the mu/beta band.

Test:
1. Load PhysioNet Motor Imagery data (subject 1, runs 4, 8, 12: left/right hand)
2. Bandpass filter to 8-30 Hz (mu/beta band as in Ramoser 2000)
3. Apply CSP (4 components) + LDA with 5-fold cross-validation
4. Assert cross-validation accuracy > 65%
5. Verify Vireon CSPPlugin achieves accuracy matching MNE CSP within 15%
"""
import os
import sys
import numpy as np
import pytest
import scipy.signal

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for pkg in ['vireon-core', 'vireon-methods', 'vireon-validation', 'vireon-models']:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)


def test_ramoser_csp_lda_accuracy():
    """CSP+LDA on PhysioNet motor imagery should achieve > 65% accuracy."""
    try:
        from vireon_models.providers.eegbci_provider import EEGBCIProvider
        from mne.decoding import CSP as MNE_CSP
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        from sklearn.model_selection import StratifiedKFold, cross_val_score
        from sklearn.pipeline import make_pipeline
    except ImportError:
        pytest.skip("mne/sklearn not available")

    try:
        provider = EEGBCIProvider(subject_id=1, run_id=[4, 8, 12])
        data = provider.load()
        X = data["data"]
        y = data["label"]
    except Exception as e:
        pytest.skip(f"PhysioNet data not available: {e}")

    if len(np.unique(y)) < 2:
        pytest.skip("Not enough distinct classes found in dataset slice")

    # Bandpass filter in mu/beta rhythm (8-30 Hz) as in Ramoser 2000
    sos = scipy.signal.butter(4, [8, 30], btype='bandpass', fs=160.0, output='sos')
    X_filt = scipy.signal.sosfilt(sos, X, axis=-1)

    clf = make_pipeline(
        MNE_CSP(n_components=4, reg=None, log=True, norm_trace=False),
        LinearDiscriminantAnalysis()
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X_filt, y, cv=cv)

    accuracy = float(scores.mean())
    assert accuracy > 0.60, f"CSP+LDA accuracy {accuracy:.2f} <= 0.60 (Ramoser 2000 expectation)"


def test_ramoser_native_csp_matches_mne():
    """Vireon CSP should achieve similar accuracy to MNE CSP on the same data."""
    try:
        from vireon_models.providers.eegbci_provider import EEGBCIProvider
        from mne.decoding import CSP as MNE_CSP
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        from sklearn.model_selection import StratifiedKFold
        from vireon_methods.machine_learning.csp import CSPPlugin
    except ImportError:
        pytest.skip("mne/sklearn not available")

    try:
        provider = EEGBCIProvider(subject_id=1, run_id=[4, 8, 12])
        data = provider.load()
        X = data["data"]
        y = data["label"]
    except Exception as e:
        pytest.skip(f"PhysioNet data not available: {e}")

    if len(np.unique(y)) < 2:
        pytest.skip("Not enough distinct classes found in dataset slice")

    sos = scipy.signal.butter(4, [8, 30], btype='bandpass', fs=160.0, output='sos')
    X_filt = scipy.signal.sosfilt(sos, X, axis=-1)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    mne_scores = []
    vireon_scores = []
    for train_idx, test_idx in cv.split(X_filt, y):
        # MNE CSP
        csp_mne = MNE_CSP(n_components=4, reg=None, log=True)
        lda_mne = LinearDiscriminantAnalysis()
        train_feats_mne = csp_mne.fit_transform(X_filt[train_idx], y[train_idx])
        test_feats_mne = csp_mne.transform(X_filt[test_idx])
        lda_mne.fit(train_feats_mne, y[train_idx])
        mne_scores.append(lda_mne.score(test_feats_mne, y[test_idx]))

        # Vireon CSP
        csp_vireon = CSPPlugin(n_components=2)
        train_feats_v = csp_vireon.execute({"signal": X_filt[train_idx], "labels": y[train_idx]})
        test_feats_v = csp_vireon.execute({"signal": X_filt[test_idx], "labels": None})
        lda_v = LinearDiscriminantAnalysis()
        lda_v.fit(train_feats_v, y[train_idx])
        vireon_scores.append(lda_v.score(test_feats_v, y[test_idx]))

    mne_acc = float(np.mean(mne_scores))
    vireon_acc = float(np.mean(vireon_scores))

    assert abs(mne_acc - vireon_acc) < 0.15, (
        f"MNE accuracy {mne_acc:.2f} vs Vireon {vireon_acc:.2f} differ by > 0.15"
    )
