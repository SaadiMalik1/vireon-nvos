import numpy as np
from scipy.signal import butter, filtfilt

from vireon_core.contracts.base import ISignal
from vireon_core.runtime.rng import DeterministicRNG

class NoiseGenerator:
    @staticmethod
    def white_noise(duration: float, sfreq: float, n_channels: int, 
                    amplitude: float = 1.0, seed: int = 42) -> ISignal:
        """
        Generates pure white noise.
        """
        rng = DeterministicRNG(seed=seed)
        n_samples = int(duration * sfreq)
        data = rng.normal(0, amplitude, (n_samples, n_channels))
        return ISignal(sampling_rate=sfreq, data=data)

    @staticmethod
    def pink_noise(duration: float, sfreq: float, n_channels: int, 
                   amplitude: float = 1.0, seed: int = 42) -> ISignal:
        """
        Generates pink noise (1/f) by filtering white noise.
        Simplified implementation using 1/f spectral shaping.
        """
        rng = DeterministicRNG(seed=seed)
        n_samples = int(duration * sfreq)
        
        # Generate white noise in frequency domain
        X_white = np.fft.rfft(rng.normal(0, 1.0, (n_samples, n_channels)), axis=0)
        
        # Create 1/f filter
        f = np.fft.rfftfreq(n_samples, d=1/sfreq)
        f[0] = f[1] # Avoid division by zero
        S_f = 1 / np.sqrt(f)
        
        # Apply filter and transform back
        X_pink = X_white * S_f[:, np.newaxis]
        data = np.fft.irfft(X_pink, n=n_samples, axis=0)
        
        # Normalize amplitude
        data = (data / np.std(data, axis=0)) * amplitude
        return ISignal(sampling_rate=sfreq, data=data)

class OscillationGenerator:
    @staticmethod
    def pure_sine(duration: float, sfreq: float, n_channels: int, 
                  freq: float, amplitude: float = 1.0, phase: float = 0.0) -> ISignal:
        """
        Generates a pure sine wave at a specific frequency.
        """
        n_samples = int(duration * sfreq)
        t = np.arange(n_samples) / sfreq
        base_signal = amplitude * np.sin(2 * np.pi * freq * t + phase)
        data = np.tile(base_signal, (n_channels, 1)).T
        return ISignal(sampling_rate=sfreq, data=data)

    @staticmethod
    def _bandpass_noise(duration: float, sfreq: float, n_channels: int, low: float, high: float, amplitude: float, seed: int) -> ISignal:
        pink_sig = NoiseGenerator.pink_noise(duration, sfreq, n_channels, amplitude, seed)
        nyq = 0.5 * sfreq
        b, a = butter(4, [low / nyq, high / nyq], btype='band')
        data_filtered = filtfilt(b, a, pink_sig.data, axis=0)
        data_filtered = (data_filtered / np.std(data_filtered, axis=0)) * amplitude
        return ISignal(sampling_rate=sfreq, data=data_filtered)

    @staticmethod
    def delta_rhythm(duration: float, sfreq: float, n_channels: int, amplitude: float = 1.0, seed: int = 42) -> ISignal:
        return OscillationGenerator._bandpass_noise(duration, sfreq, n_channels, 0.5, 4.0, amplitude, seed)
        
    @staticmethod
    def theta_rhythm(duration: float, sfreq: float, n_channels: int, amplitude: float = 1.0, seed: int = 42) -> ISignal:
        return OscillationGenerator._bandpass_noise(duration, sfreq, n_channels, 4.0, 8.0, amplitude, seed)

    @staticmethod
    def alpha_rhythm(duration: float, sfreq: float, n_channels: int, amplitude: float = 1.0, seed: int = 42) -> ISignal:
        return OscillationGenerator._bandpass_noise(duration, sfreq, n_channels, 8.0, 12.0, amplitude, seed)
        
    @staticmethod
    def mu_rhythm(duration: float, sfreq: float, n_channels: int, amplitude: float = 1.0, seed: int = 42) -> ISignal:
        # Mu is morphologically similar to alpha, but often concentrated at 9-11Hz over sensorimotor cortex
        return OscillationGenerator._bandpass_noise(duration, sfreq, n_channels, 9.0, 11.0, amplitude, seed)
        
    @staticmethod
    def beta_rhythm(duration: float, sfreq: float, n_channels: int, amplitude: float = 1.0, seed: int = 42) -> ISignal:
        return OscillationGenerator._bandpass_noise(duration, sfreq, n_channels, 13.0, 30.0, amplitude, seed)
        
    @staticmethod
    def gamma_rhythm(duration: float, sfreq: float, n_channels: int, amplitude: float = 1.0, seed: int = 42) -> ISignal:
        return OscillationGenerator._bandpass_noise(duration, sfreq, n_channels, 30.0, 80.0, amplitude, seed)
        
    @staticmethod
    def hfo(duration: float, sfreq: float, n_channels: int, amplitude: float = 1.0, seed: int = 42) -> ISignal:
        return OscillationGenerator._bandpass_noise(duration, sfreq, n_channels, 80.0, 250.0, amplitude, seed)

class CognitiveGenerator:
    @staticmethod
    def p300_wave(sfreq: float, n_channels: int, latency: float = 0.3, amplitude: float = 5.0) -> ISignal:
        """
        Synthesizes a precise P300 event.
        """
        duration = 1.0
        n_samples = int(duration * sfreq)
        t = np.arange(n_samples) / sfreq
        # Simulate P300 as a Gaussian centered at latency
        p300 = amplitude * np.exp(-((t - latency) ** 2) / (2 * (0.05 ** 2)))
        data = np.tile(p300, (n_channels, 1)).T
        return ISignal(sampling_rate=sfreq, data=data)

class ClinicalGenerator:
    @staticmethod
    def epileptic_spike(sfreq: float, n_channels: int, amplitude: float = 100.0) -> ISignal:
        """
        Simulates an epileptic spike (very short duration, high amplitude).
        """
        duration = 0.5
        n_samples = int(duration * sfreq)
        t = np.arange(n_samples) / sfreq
        spike = amplitude * np.exp(-((t - 0.25) ** 2) / (2 * (0.01 ** 2)))
        data = np.tile(spike, (n_channels, 1)).T
        return ISignal(sampling_rate=sfreq, data=data)

class ArtifactGenerator:
    @staticmethod
    def line_noise(signal: ISignal, freq: float = 50.0, amplitude: float = 0.5) -> ISignal:
        """
        Adds 50/60Hz line noise to an existing signal.
        """
        n_samples = signal.data.shape[0]
        n_channels = signal.data.shape[1]
        t = np.arange(n_samples) / signal.sampling_rate
        noise = amplitude * np.sin(2 * np.pi * freq * t)
        noise_expanded = np.tile(noise, (n_channels, 1)).T
        
        new_data = signal.data + noise_expanded
        return ISignal(sampling_rate=signal.sampling_rate, data=new_data)
        
    @staticmethod
    def hardware_saturation(signal: ISignal, clip_min: float, clip_max: float) -> ISignal:
        """
        Simulates amplifier saturation (clipping).
        """
        clipped_data = np.clip(signal.data, clip_min, clip_max)
        return ISignal(sampling_rate=signal.sampling_rate, data=clipped_data)
