import numpy as np
import pytest
import mne
from vireon_core.compat.mne_adapter import mne_to_vireon, vireon_to_mne
from vireon_core.contracts.base import ISignal


def test_mne_raw_to_vireon():
    data = np.random.default_rng(42).normal(size=(4, 1000))
    info = mne.create_info(ch_names=["C3", "C4", "Cz", "Pz"], sfreq=250.0, ch_types="eeg")
    raw = mne.io.RawArray(data, info)

    signal = mne_to_vireon(raw)
    assert isinstance(signal, ISignal)
    assert signal.sampling_rate == 250.0
    assert signal.channel_names == ["C3", "C4", "Cz", "Pz"]
    assert np.allclose(signal.data, data)


def test_mne_epochs_to_vireon():
    data = np.random.default_rng(42).normal(size=(10, 4, 250))
    info = mne.create_info(ch_names=["C3", "C4", "Cz", "Pz"], sfreq=250.0, ch_types="eeg")
    events = np.column_stack([np.arange(10) * 100, np.zeros(10, dtype=int), np.tile([1, 2], 5)])
    epochs = mne.EpochsArray(data, info, events=events)

    signal = mne_to_vireon(epochs)
    assert isinstance(signal, ISignal)
    assert signal.sampling_rate == 250.0
    assert signal.channel_names == ["C3", "C4", "Cz", "Pz"]
    assert np.allclose(signal.data, data)


def test_vireon_to_mne_raw():
    data = np.random.default_rng(42).normal(size=(4, 1000))
    signal = ISignal(sampling_rate=250.0, data=data, channel_names=["C3", "C4", "Cz", "Pz"])

    raw = vireon_to_mne(signal)
    assert isinstance(raw, mne.io.RawArray)
    assert raw.info["sfreq"] == 250.0
    assert raw.ch_names == ["C3", "C4", "Cz", "Pz"]
    assert np.allclose(raw.get_data(), data)


def test_invalid_type_raises():
    with pytest.raises(TypeError, match="Expected mne.io.BaseRaw or mne.Epochs"):
        mne_to_vireon("invalid_string_obj")
