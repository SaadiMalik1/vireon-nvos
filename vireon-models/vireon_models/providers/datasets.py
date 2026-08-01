"""
Real physiological signal providers for the VIREON canonical execution pipeline.

Salvaged from legacy VIREON v0 dataset generators and wrapped as IProvider
implementations that produce actual multi-channel numpy signal arrays.
"""

from typing import Dict, Any, List, Optional
import numpy as np

from vireon_core.contracts import IProvider


class DatasetProvider(IProvider):
    """Base interface for loading empirical real-world datasets."""
    def load_subject(self, subject_id: str):
        raise NotImplementedError
    def iterate_trials(self):
        raise NotImplementedError
    def metadata(self) -> Dict[str, Any]:
        raise NotImplementedError
    def start(self) -> None:
        raise NotImplementedError
    def stop(self) -> None:
        raise NotImplementedError
    def get_data(self) -> Dict[str, Any]:
        raise NotImplementedError


class SyntheticBCICompetitionProvider(DatasetProvider):
    """Synthetic dataset provider that mimics BCI Competition IV 2a for testing."""
    def __init__(self, data_dir: str, subject_id: int):
        self.data_dir = data_dir
        self.subject_id = subject_id
    def start(self):
        self.mock = MockBCICompetitionIVDataset(subject_id=self.subject_id)
        X, y = self.mock.load_trials(num_trials=5)
        self._data = {"data": X, "labels": y, "sample_rate": self.mock.sample_rate}
    def stop(self): pass
    def get_data(self): return self._data

class SyntheticCHBMITProvider(DatasetProvider):
    """Synthetic dataset provider that mimics CHB-MIT Scalp EEG for testing."""
    def __init__(self, data_dir: str, subject_id: str):
        self.data_dir = data_dir
        self.subject_id = subject_id
    def start(self):
        self.gen = SyntheticDataGenerator(seed=hash(self.subject_id) % 10000, num_channels=21, sample_rate=256.0)
        self._data = self.gen.generate_eeg_stream(duration_sec=10.0, noise_level=0.1, powerline_hum_freq=60.0)
    def stop(self): pass
    def get_data(self): return self._data

class SyntheticSleepEDFProvider(DatasetProvider):
    """Synthetic dataset provider that mimics Sleep-EDF for testing."""
    def __init__(self, data_dir: str, subject_id: int):
        self.data_dir = data_dir
        self.subject_id = subject_id
    def start(self):
        self.gen = SyntheticDataGenerator(seed=self.subject_id, num_channels=2, sample_rate=100.0)
        # Sleep-EDF typically has specific frequency bands, we mock it with pink noise + alpha bursts
        self._data = self.gen.generate_eeg_stream(duration_sec=30.0, noise_level=0.05)
    def stop(self): pass
    def get_data(self): return self._data

# ---------------------------------------------------------------------------
# Signal Generator Core (salvaged from legacy vireon/datasets/synthetic.py)
# ---------------------------------------------------------------------------

class SyntheticDataGenerator:
    """
    Generates reproducible multi-band physiological telemetry streams with
    configurable noise, powerline hum, P300 ERP spikes, packet loss, and channel dropouts.
    """

    def __init__(self, seed: int = 42, num_channels: int = 8, sample_rate: float = 250.0):
        self.seed = seed
        self.num_channels = num_channels
        self.sample_rate = sample_rate
        self._rng = np.random.default_rng(seed)

    def generate_eeg_stream(
        self,
        duration_sec: float = 1.0,
        noise_level: float = 0.1,
        include_p300: bool = False,
        powerline_hum_freq: Optional[float] = 60.0,
        packet_loss_rate: float = 0.0,
        dropout_channels: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Generates multi-frequency EEG with 1/f background and oscillatory bursts."""
        num_samples = int(duration_sec * self.sample_rate)
        t = np.linspace(0, duration_sec, num_samples, endpoint=False)

        # Generate 1/f pink noise background
        white_noise = self._rng.standard_normal((num_samples, self.num_channels)).astype(np.float32) * 10.0
        fft = np.fft.rfft(white_noise, axis=0)
        freqs = np.fft.rfftfreq(num_samples)
        freqs[0] = 1.0  # avoid division by zero
        fft_pink = fft / np.sqrt(freqs)[:, None]
        data = np.fft.irfft(fft_pink, n=num_samples, axis=0).astype(np.float32)

        p300_latency = None
        for ch in range(self.num_channels):
            # Oscillatory burst (alpha)
            env = np.maximum(0, np.sin(2 * np.pi * 1.5 * t + self._rng.uniform(0, 2*np.pi)))
            alpha = np.sin(2 * np.pi * (10.0 + self._rng.uniform(-0.5, 0.5)) * t) * 15.0 * env
            data[:, ch] += alpha

            if powerline_hum_freq:
                data[:, ch] += np.sin(2 * np.pi * powerline_hum_freq * t) * 8.0

        if include_p300:
            # P300 with latency and amplitude jitter
            jitter = float(self._rng.uniform(0.25, 0.40))
            amp_jitter = float(self._rng.uniform(20.0, 50.0))
            pulse = amp_jitter * np.exp(-0.5 * ((t - jitter) / 0.05) ** 2)
            for ch in range(self.num_channels):
                data[:, ch] += pulse
            p300_latency = jitter

        if noise_level > 0.0:
            data += self._rng.normal(0.0, noise_level * 10.0, size=data.shape).astype(np.float32)

        if dropout_channels:
            for ch in dropout_channels:
                if 0 <= ch < self.num_channels:
                    data[:, ch] = 0.0

        if packet_loss_rate > 0.0:
            loss_mask = self._rng.uniform(0.0, 1.0, size=num_samples) < packet_loss_rate
            data[loss_mask, :] = 0.0

        return {
            "num_samples": num_samples,
            "num_channels": self.num_channels,
            "sample_rate": self.sample_rate,
            "data": data,
            "seed": self.seed,
            "p300_included": include_p300,
            "p300_latency_sec": p300_latency,
            "duration_sec": duration_sec,
        }


# ---------------------------------------------------------------------------
# Motor Imagery Generator (salvaged from legacy vireon/datasets/biopotentials.py)
# ---------------------------------------------------------------------------

class MotorImageryEEGGenerator:
    """
    Generates synthetic Motor Imagery EEG signals exhibiting Event-Related Desynchronization (ERD)
    in Mu (8-12 Hz) and Beta (13-30 Hz) bands during imagined limb movements.
    """

    CLASSES = ["left_hand", "right_hand", "feet", "tongue"]

    def __init__(self, seed: int = 42, num_channels: int = 8, sample_rate: float = 250.0):
        self.seed = seed
        self.num_channels = num_channels
        self.sample_rate = sample_rate
        self._rng = np.random.default_rng(seed)

    def generate_trial(
        self,
        target_class: str = "left_hand",
        trial_duration_sec: float = 4.0,
        cue_time_sec: float = 1.0,
    ) -> Dict[str, Any]:
        if target_class not in self.CLASSES:
            raise ValueError(f"Invalid class {target_class}. Must be one of {self.CLASSES}")

        num_samples = int(trial_duration_sec * self.sample_rate)
        t = np.linspace(0, trial_duration_sec, num_samples, endpoint=False)

        # 1/f background
        white_noise = self._rng.standard_normal((num_samples, self.num_channels)).astype(np.float32) * 5.0
        fft = np.fft.rfft(white_noise, axis=0)
        freqs = np.fft.rfftfreq(num_samples)
        freqs[0] = 1.0
        fft_pink = fft / np.sqrt(freqs)[:, None]
        data = np.fft.irfft(fft_pink, n=num_samples, axis=0).astype(np.float32)

        cue_mask = (t >= cue_time_sec) & (t <= cue_time_sec + 2.5)

        for ch in range(self.num_channels):
            # Generate mu and beta specifically
            mu = np.sin(2 * np.pi * 10.0 * t) * 15.0
            beta = np.sin(2 * np.pi * 20.0 * t) * 8.0
            
            # Apply ERD specific to bands
            if target_class == "left_hand" and ch in [3, 4]:
                mu[cue_mask] *= 0.3
                beta[cue_mask] *= 0.3
            elif target_class == "right_hand" and ch in [1, 2]:
                mu[cue_mask] *= 0.3
                beta[cue_mask] *= 0.3
            elif target_class == "feet" and ch in [0, 7]:
                mu[cue_mask] *= 0.2
                beta[cue_mask] *= 0.2
                
            data[:, ch] += mu + beta

        data += self._rng.normal(0.0, 3.0, size=data.shape).astype(np.float32)

        return {
            "num_samples": num_samples,
            "num_channels": self.num_channels,
            "sample_rate": self.sample_rate,
            "target_class": target_class,
            "cue_time_sec": cue_time_sec,
            "data": data,
            "duration_sec": trial_duration_sec,
        }


# ---------------------------------------------------------------------------
# BCI Competition IV Dataset (salvaged from legacy vireon/datasets/benchmarks.py)
# ---------------------------------------------------------------------------

class MockBCICompetitionIVDataset:
    """
    Mock loader for BCI Competition IV 2a Motor Imagery dataset.
    Generates deterministic 22-channel, 4-class synthetic motor imagery trials.
    """

    def __init__(self, subject_id: int = 1, seed: int = 42):
        self.subject_id = subject_id
        self.seed = seed + subject_id
        self.sample_rate = 250.0
        self.num_channels = 22

    def load_trials(self, num_trials: int = 40):
        gen = MotorImageryEEGGenerator(
            seed=self.seed, num_channels=self.num_channels, sample_rate=self.sample_rate
        )
        classes = ["left_hand", "right_hand", "feet", "tongue"]
        X_list, y_list = [], []

        for i in range(num_trials):
            target_class_idx = i % len(classes)
            trial = gen.generate_trial(target_class=classes[target_class_idx], trial_duration_sec=4.0)
            X_list.append(trial["data"])
            y_list.append(target_class_idx)

        return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.int64)


# ============================================================================
# IProvider Implementations
# ============================================================================

class SyntheticSignalProvider(IProvider):
    """
    Wraps SyntheticDataGenerator as a canonical IProvider.
    Produces real multi-channel signal numpy arrays.
    """

    def __init__(self, seed: int = 42, num_channels: int = 8, duration_sec: float = 2.0,
                 noise_level: float = 0.1, powerline_hum_freq: Optional[float] = 60.0,
                 include_p300: bool = False, sample_rate: float = 250.0):
        self.generator = SyntheticDataGenerator(seed=seed, num_channels=num_channels, sample_rate=sample_rate)
        self.duration_sec = duration_sec
        self.noise_level = noise_level
        self.powerline_hum_freq = powerline_hum_freq
        self.include_p300 = include_p300
        self._data = None

    def start(self) -> None:
        self._data = self.generator.generate_eeg_stream(
            duration_sec=self.duration_sec,
            noise_level=self.noise_level,
            powerline_hum_freq=self.powerline_hum_freq,
            include_p300=self.include_p300,
        )

    def stop(self) -> None:
        pass

    def get_data(self) -> Dict[str, Any]:
        if self._data is None:
            self.start()
        return self._data


class MotorImageryProvider(IProvider):
    """
    Wraps MotorImageryEEGGenerator as a canonical IProvider.
    Produces motor imagery EEG trials with ERD in mu/beta bands.
    """

    def __init__(self, seed: int = 42, num_channels: int = 8,
                 target_class: str = "left_hand", trial_duration_sec: float = 4.0):
        self.generator = MotorImageryEEGGenerator(seed=seed, num_channels=num_channels)
        self.target_class = target_class
        self.trial_duration_sec = trial_duration_sec
        self._data = None

    def start(self) -> None:
        self._data = self.generator.generate_trial(
            target_class=self.target_class,
            trial_duration_sec=self.trial_duration_sec,
        )

    def stop(self) -> None:
        pass

    def get_data(self) -> Dict[str, Any]:
        if self._data is None:
            self.start()
        return self._data


class SyntheticMotorImageryProvider(IProvider):
    """
    Wraps MockBCICompetitionIVDataset as a synthetic canonical IProvider.
    Generates physiologically inspired motor imagery signals with configurable 1/f noise, 
    ERD/ERS dynamics, and controllable ground truth. It is intended for deterministic 
    benchmarking and CI when external datasets are unavailable.
    """

    def __init__(self, subject_id: int = 1, seed: int = 42, trial_index: int = 0):
        self.dataset = MockBCICompetitionIVDataset(subject_id=subject_id, seed=seed)
        self.trial_index = trial_index
        self._data = None

    def start(self) -> None:
        X, y = self.dataset.load_trials(num_trials=max(self.trial_index + 1, 4))
        self._data = {
            "data": X[self.trial_index],
            "label": int(y[self.trial_index]),
            "num_samples": X[self.trial_index].shape[0],
            "num_channels": X[self.trial_index].shape[1],
            "sample_rate": self.dataset.sample_rate,
            "duration_sec": X[self.trial_index].shape[0] / self.dataset.sample_rate,
        }

    def stop(self) -> None:
        pass

    def get_data(self) -> Dict[str, Any]:
        if self._data is None:
            self.start()
        return self._data

from vireon_models.patient import DigitalPatient
from vireon_models.forward import LeadfieldProjector
from vireon_models.hardware import ADS1299

class DigitalTwinProvider(IProvider):
    """
    Implements the true causal simulation chain:
    Digital Patient (Source Space) -> Forward Model (Volume Conduction) -> Hardware (ADC/Amp) -> Output Signal.
    """
    def __init__(self, seed: int = 42, duration_sec: float = 2.0, sample_rate: float = 250.0):
        self.seed = seed
        self.duration_sec = duration_sec
        self.sample_rate = sample_rate
        
        # 1. Digital Patient (Generates Source Space)
        self.patient = DigitalPatient(age=25, seed=seed)
        
        # 2. Forward Model (Volume Conduction)
        self.projector = LeadfieldProjector(num_sources=4, num_sensors=8, seed=seed)
        
        # 3. Hardware Device (Amplifier and ADC Quantization)
        self.device = ADS1299()
        
        self._data = None

    def start(self) -> None:
        # Step 1: Biological Source Generation
        sources = self.patient.generate_brain_activity(self.duration_sec, self.sample_rate)
        
        # Step 2: Forward Projection to Sensor Space
        sensors_raw = self.projector.project(sources)
        
        # Step 3: Hardware Constraints
        sensors_hardware = self.device.process(sensors_raw, self.sample_rate)
        
        self._data = {
            "num_samples": sensors_hardware.shape[0],
            "num_channels": sensors_hardware.shape[1],
            "sample_rate": self.sample_rate,
            "data": sensors_hardware,
            "seed": self.seed,
            "duration_sec": self.duration_sec,
        }

    def stop(self) -> None:
        pass

    def get_data(self) -> Dict[str, Any]:
        if self._data is None:
            self.start()
        return self._data


class PhysioNetMotorImageryProvider(IProvider):
    """
    Loads real Motor Imagery EEG data from the PhysioNet eegmmidb dataset.
    Requires the dataset to be downloaded locally to ~/mne_data.
    """
    def __init__(self, subject_id: int = 1, run_id: int = 4):
        self.subject_id = subject_id
        self.run_id = run_id
        
        import os
        import mne
        # MNE defaults to ~/mne_data
        mne_data = os.path.expanduser("~/mne_data")
        file_path = os.path.join(mne_data, "MNE-eegbci-data", "files", "eegmmidb", "1.0.0", 
                                 f"S{subject_id:03d}", f"S{subject_id:03d}R{run_id:02d}.edf")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PhysioNet data not found at {file_path}. Please download it.")
            
        # Load raw data
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
        events, event_id = mne.events_from_annotations(raw, verbose=False)
        
        # MNE eegbci events: T0 (rest), T1 (left fist), T2 (right fist)
        # We will extract epochs for T1 and T2 (binary classification for CSP)
        # T1 = 2, T2 = 3 in the events array
        picks = mne.pick_types(raw.info, meg=False, eeg=True, stim=False, eog=False, exclude='bads')
        epochs = mne.Epochs(raw, events, event_id=dict(T1=2, T2=3), tmin=-1.0, tmax=4.0, proj=True, picks=picks,
                            baseline=None, preload=True, verbose=False)
                            
        self.epochs = epochs
        
    def get_data(self) -> dict:
        import numpy as np
        # get_data() on MNE epochs returns (n_epochs, n_channels, n_times)
        X = self.epochs.get_data(copy=True)
        # convert labels to 0 and 1
        y = self.epochs.events[:, -1] - 2 
        
        return {
            "data": X,
            "label": y,
            "sample_rate": self.epochs.info['sfreq'],
            "ch_names": self.epochs.ch_names
        }
        
    def start(self): pass
    def stop(self): pass
