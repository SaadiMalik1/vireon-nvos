"""
Signal-level validation metrics for VIREON.

Computes real spectral and statistical measurements from numpy signal arrays
produced by IProvider implementations.
"""

from typing import Dict, Any, Optional, Tuple, List
import numpy as np

from vireon_core.contracts.base import IMeasurement
from vireon_validation.statistics import compute_bootstrap_ci
from vireon_validation.decoder import DecoderEvaluator

def compute_snr_raw(signal: np.ndarray, noise_estimate: Optional[np.ndarray] = None) -> float:
    if signal.ndim == 2:
        snrs = [compute_snr_raw(signal[:, ch], noise_estimate[:, ch] if noise_estimate is not None else None)
                for ch in range(signal.shape[1])]
        return float(np.mean(snrs))

    signal_power = np.var(signal)
    
    if noise_estimate is not None:
        noise_power = np.var(noise_estimate)
    else:
        diff = np.diff(signal)
        mad = np.median(np.abs(diff - np.median(diff)))
        noise_std = mad * 1.4826
        noise_power = noise_std ** 2
    
    if noise_power < 1e-12:
        return 100.0
    
    snr = 10.0 * np.log10(signal_power / noise_power)
    return float(max(0.0, snr))

def compute_psd(data: np.ndarray, sample_rate: float) -> Tuple[np.ndarray, np.ndarray]:
    """Computes power spectral density via rfft. Extracted for verification."""
    n = len(data)
    fft_vals = np.fft.rfft(data)
    fft_freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    psd = np.abs(fft_vals) ** 2 / n
    return fft_freqs, psd

def _compute_band_power_raw(data: np.ndarray, sample_rate: float, band: Tuple[float, float]) -> float:
    if data.ndim == 2:
        powers = [_compute_band_power_raw(data[:, ch], sample_rate, band)
                  for ch in range(data.shape[1])]
        return float(np.mean(powers))
    
    fft_freqs, psd = compute_psd(data, sample_rate)
    
    band_mask = (fft_freqs >= band[0]) & (fft_freqs <= band[1])
    if not np.any(band_mask):
        return 0.0
    
    return float(np.mean(psd[band_mask]))


def detect_powerline_artifact(data: np.ndarray, sample_rate: float,
                               freq: float = 50.0, threshold_ratio: float = 3.0) -> bool:
    if data.ndim == 2:
        return any(detect_powerline_artifact(data[:, ch], sample_rate, freq, threshold_ratio)
                   for ch in range(data.shape[1]))
    
    n = len(data)
    fft_vals = np.fft.rfft(data)
    fft_freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    psd = np.abs(fft_vals) ** 2 / n
    
    target_mask = (fft_freqs >= freq - 0.5) & (fft_freqs <= freq + 0.5)
    if not np.any(target_mask):
        return False
    target_power = np.max(psd[target_mask])
    
    bg_mask = ((fft_freqs >= freq - 3.0) & (fft_freqs <= freq - 1.0)) | \
              ((fft_freqs >= freq + 1.0) & (fft_freqs <= freq + 3.0))
    
    if not np.any(bg_mask):
        return False
    
    bg_power = np.median(psd[bg_mask])
    
    if bg_power < 1e-12:
        return target_power > 1e-6
    
    return (target_power / bg_power) > threshold_ratio


def detect_p300_erp(data_dict: Dict[str, Any], event_onset_sec: Optional[float] = None) -> bool:
    data = data_dict["data"]
    fs = float(data_dict.get("sample_rate", 250.0))
    
    if event_onset_sec is None:
        event_onset_sec = data_dict.get("event_onset_sec")
    if event_onset_sec is None:
        event_onset_sec = data_dict.get("cue_time_sec", 0.0)
    
    window_start_idx = int((event_onset_sec + 0.25) * fs)
    window_end_idx = int((event_onset_sec + 0.60) * fs)
    
    if window_end_idx > data.shape[0] or window_start_idx >= data.shape[0]:
        return False

    mean_signal = np.mean(data, axis=1)
    window_data = mean_signal[window_start_idx:window_end_idx]
    bg_data = np.concatenate([mean_signal[:window_start_idx], mean_signal[window_end_idx:]])
    
    if len(bg_data) == 0:
        return False
        
    bg_mean = np.mean(bg_data)
    bg_std = np.std(bg_data)
    
    if bg_std == 0:
        return False

    window_max = np.max(window_data)
    return ((window_max - bg_mean) / bg_std) > 2.5


BANDS = {
    "delta": (0.5, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta":  (13.0, 30.0),
    "gamma": (30.0, 100.0),
    "mu":    (8.0, 12.0),
}


def generate_signal_metrics(provider_data: Dict[str, Any], event_onset_sec: Optional[float] = None) -> List[IMeasurement]:
    """
    Compute all signal-level metrics from a provider's output data dict.
    Returns probabilistic IMeasurement objects with bootstrapped uncertainty.
    """
    data = provider_data.get("data")
    if data is None or not isinstance(data, np.ndarray):
        return []
    
    sample_rate = provider_data.get("sample_rate", 250.0)
    
    metrics = []
    
    # SNR with bootstrap
    def snr_statistic(sample):
        return compute_snr_raw(sample, None)
    
    from vireon_core.contracts.base import IUncertainty
    
    point_est, var, ci = compute_bootstrap_ci(data, snr_statistic, n_resamples=100)
    uncertainty = IUncertainty(
        mean=point_est,
        variance=var,
        distribution="bootstrap",
        confidence_interval=ci,
        sample_size=100,
        method="bootstrap"
    )
    metrics.append(IMeasurement(
        metric_name="snr_db", 
        value=point_est, 
        unit="dB", 
        uncertainty=uncertainty
    ))
    
    # Band powers with bootstrap
    for name, band in BANDS.items():
        def band_statistic(sample, b=band):
            return _compute_band_power_raw(sample, sample_rate, b)
        
        bp_est, bp_var, bp_ci = compute_bootstrap_ci(data, band_statistic, n_resamples=100)
        uncertainty = IUncertainty(
            mean=bp_est,
            variance=bp_var,
            distribution="bootstrap",
            confidence_interval=bp_ci,
            sample_size=100,
            method="bootstrap"
        )
        metrics.append(IMeasurement(
            metric_name=f"{name}_band_power",
            value=bp_est,
            unit="uV2/Hz",
            uncertainty=uncertainty
        ))
    
    # Powerline artifact detection
    val_50 = 1.0 if detect_powerline_artifact(data, sample_rate, 50.0) else 0.0
    metrics.append(IMeasurement(metric_name="powerline_50hz_detected", value=val_50, unit="bool"))
    
    val_60 = 1.0 if detect_powerline_artifact(data, sample_rate, 60.0) else 0.0
    metrics.append(IMeasurement(metric_name="powerline_60hz_detected", value=val_60, unit="bool"))
    
    # P300 detection
    val_p300 = 1.0 if detect_p300_erp(provider_data, event_onset_sec) else 0.0
    metrics.append(IMeasurement(metric_name="p300_detected", value=val_p300, unit="bool"))
    
    # Decoder Evaluation via CSP + LDA Pipeline
    decoder_metrics = DecoderEvaluator.evaluate(data, sample_rate)
    for name, val in decoder_metrics.items():
        metrics.append(IMeasurement(metric_name=name, value=val, unit="metric"))
    
    return metrics
