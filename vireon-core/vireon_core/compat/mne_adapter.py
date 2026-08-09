"""Adapter to use MNE-Python objects (Raw, Epochs) with VIREON plugins.

Example:
    import mne
    from vireon_core.compat.mne_adapter import mne_to_vireon, vireon_to_mne
    from vireon_methods.spectral.vireon_welch import VireonWelch

    raw = mne.io.read_raw_fif("subject_raw.fif", preload=True)
    signal = mne_to_vireon(raw)  # ISignal wrapper
    psd, freqs = VireonWelch(fs=raw.info["sfreq"], nperseg=512).compute(signal.data)
"""
from typing import Union, TYPE_CHECKING
from vireon_core.contracts.base import ISignal

if TYPE_CHECKING:
    import mne


def mne_to_vireon(mne_obj: Union["mne.io.BaseRaw", "mne.BaseEpochs"]) -> ISignal:
    """Convert MNE Raw or Epochs to VIREON ISignal."""
    import mne
    if isinstance(mne_obj, mne.io.BaseRaw):
        data = mne_obj.get_data()  # (n_channels, n_samples)
        return ISignal(
            data=data,
            sampling_rate=float(mne_obj.info["sfreq"]),
            channel_names=list(mne_obj.ch_names),
            metadata={"source": "mne.Raw", "subject": mne_obj.info.get("subject_id")},
        )
    elif isinstance(mne_obj, (mne.BaseEpochs, getattr(mne, "Epochs", object))):
        data = mne_obj.get_data()  # type: ignore
        return ISignal(
            data=data,
            sampling_rate=float(mne_obj.info["sfreq"]),  # type: ignore
            channel_names=list(mne_obj.ch_names),  # type: ignore
            metadata={"source": "mne.Epochs", "events": mne_obj.events},  # type: ignore
        )
    else:
        raise TypeError(f"Expected mne.io.BaseRaw or mne.Epochs, got {type(mne_obj)}")


def vireon_to_mne(signal: ISignal) -> "mne.io.RawArray":
    """Convert VIREON ISignal to MNE RawArray."""
    import mne
    ch_names = getattr(signal, "channel_names", None) or [f"EEG{i}" for i in range(signal.data.shape[0])]
    info = mne.create_info(
        ch_names=list(ch_names),
        sfreq=float(signal.sampling_rate),
        ch_types="eeg",
    )
    return mne.io.RawArray(signal.data, info)
