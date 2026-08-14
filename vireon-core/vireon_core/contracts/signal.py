from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import numpy as np

class NeuralSignal(BaseModel):
    """
    Base contract for any type of neural signal data passed between providers, models, and validation engines.
    """
    duration_sec: float
    metadata: Dict[str, Any] = {}
    
    model_config = {"arbitrary_types_allowed": True}

class ContinuousSignal(NeuralSignal):
    """
    Represents continuous timeseries data (e.g., EEG, ECoG, LFP, MEG).
    """
    data: np.ndarray  # Shape: (num_samples, num_channels)
    sample_rate: float
    channel_names: Optional[List[str]] = None

    @property
    def num_samples(self) -> int:
        return self.data.shape[0]

    @property
    def num_channels(self) -> int:
        return self.data.shape[1]

class DiscreteSpikeTrain(NeuralSignal):
    """
    Represents discrete neural events (e.g., Neuropixels spike times).
    """
    spike_times: np.ndarray  # 1D array of spike timestamps (seconds)
    unit_ids: np.ndarray     # 1D array of corresponding neuron/unit IDs

    @property
    def num_spikes(self) -> int:
        return len(self.spike_times)
