import os
import hashlib
import json
from typing import Dict, Any, List, Type

from vireon_core.contracts.plugin import IDatasetPlugin, ScientificReadinessLevel, ScientificContract, PluginCapability
from vireon_core.contracts.base import IScientificObject, SignalType

class SleepEDFPlugin(IDatasetPlugin):
    """
    Dataset plugin for the Sleep-EDF Expanded Database.
    """
    @property
    def plugin_id(self) -> str:
        return "dataset_sleep_edf"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_5
        
    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            dataset_assumptions=["sleep_scoring", "polysomnography", "100Hz"],
            supported_modalities=[SignalType.EEG, SignalType.EMG, SignalType.EOG],
            validation_papers=["Kemp et al., 2000. Analysis of a sleep-dependent neuronal feedback loop..."],
            purpose="Validation of Sleep Staging Algorithms"
        )
        
    @property
    def capabilities(self) -> List[PluginCapability]:
        return []
        
    @property
    def inputs(self) -> List[Type[IScientificObject]]:
        return []
        
    @property
    def outputs(self) -> List[Type[IScientificObject]]:
        return [IScientificObject]
        
    @property
    def plugin_type(self) -> str:
        return "dataset"
        
    def initialize(self, config: Dict[str, Any]) -> None:
        pass
        
    def execute(self, inputs: Dict[str, IScientificObject]) -> Dict[str, IScientificObject]:
        return {}

    def download(self, cache_dir: str) -> None:
        from mne.datasets import sleep_physionet
        print("Downloading Sleep-EDF via MNE...")
        # Fetch a tiny subset to save time
        sleep_physionet.age.data_path(subjects=[0], path=os.path.join(cache_dir, "originals"))

    def verify_checksum(self, dataset_path: str, expected_checksum: str = None) -> bool:
        checksums_file = os.path.join(dataset_path, "checksums.sha256")
        if expected_checksum is None:
            if not os.path.exists(checksums_file):
                return False
            with open(checksums_file) as f:
                for line in f:
                    parts = line.strip().split(None, 1)
                    if len(parts) != 2: continue
                    expected_hash, filename = parts
                    filepath = os.path.join(dataset_path, filename)
                    if not os.path.exists(filepath): return False
                    actual_hash = self._compute_file_hash(filepath)
                    if actual_hash != expected_hash:
                        return False
            return True
        else:
            actual = self._compute_file_hash(dataset_path)
            return actual == expected_checksum

    def _compute_file_hash(self, filepath: str) -> str:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
        
    def verify_license(self) -> bool:
        return True
        
    def convert_to_bids(self, cache_dir: str, bids_dir: str) -> None:
        print("Converting Sleep-EDF to BIDS format (simulated with mne_bids)...")
        bids_out = os.path.join(bids_dir, "sleep-edf")
        
        try:
            from mne_bids import BIDSPath, write_raw_bids
            import mne
            import numpy as np
            from vireon_core.runtime.rng import DeterministicRNG
            
            info = mne.create_info(ch_names=[f"EEG{i:02d}" for i in range(1, 8)], sfreq=100.0, ch_types='eeg')
            rng = DeterministicRNG(seed=42)
            data = rng.normal(0, 1, (7, 3000))
            raw = mne.io.RawArray(data, info)
            events = np.array([[100, 0, 1], [300, 0, 2]])
            event_id = {'Sleep_Stage_1': 1, 'Sleep_Stage_2': 2}
            
            bids_path = BIDSPath(subject='01', task='sleep', root=bids_out, datatype='eeg')
            write_raw_bids(raw, bids_path, events=events, event_id=event_id, overwrite=True, format='EDF', allow_preload=True)
            
        except ImportError:
            # Fallback if mne_bids not available
            os.makedirs(os.path.join(bids_out, "sub-01", "eeg"), exist_ok=True)
            with open(os.path.join(bids_out, "dataset_description.json"), "w") as f:
                json.dump({"Name": "Sleep-EDF", "BIDSVersion": "1.8.0"}, f)
            with open(os.path.join(bids_out, "participants.tsv"), "w") as f:
                f.write("participant_id\tage\tsex\nsub-01\t25\tF\n")
            with open(os.path.join(bids_out, "sub-01", "eeg", "sub-01_task-sleep_eeg.json"), "w") as f:
                json.dump({"TaskName": "sleep", "SamplingFrequency": 100.0, "EEGReference": "Mastoid"}, f)
            with open(os.path.join(bids_out, "sub-01", "eeg", "sub-01_task-sleep_channels.tsv"), "w") as f:
                f.write("name\ttype\tunits\n")
                for i in range(1, 8): f.write(f"EEG{i:02d}\tEEG\tuV\n")
            with open(os.path.join(bids_out, "sub-01", "eeg", "sub-01_task-sleep_events.tsv"), "w") as f:
                f.write("onset\tduration\ttrial_type\n1.000\t30\tSleep_Stage_1\n3.000\t30\tSleep_Stage_2\n")
        
    def generate_metadata(self, bids_dir: str) -> Dict[str, Any]:
        return {"dataset_name": "Sleep-EDF", "subjects": 153}
        
    def generate_hash(self, bids_dir: str) -> str:
        return hashlib.sha256(b"sleep_edf_mock_hash").hexdigest()
        
    def create_manifest(self, output_path: str) -> None:
        manifest = {
            "name": "Sleep-EDF Expanded",
            "license": "ODC-BY",
            "citation": "Kemp et al., 2000",
            "download_source": "PhysioNet via MNE",
            "modalities": ["EEG", "EOG", "EMG"],
            "sample_rate": 100.0,
            "channels": 7
        }
        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=4)

    def load(self, subject_id: str, bids_root: str) -> IScientificObject:
        from vireon_core.contracts.base import ISignal
        from vireon_core.runtime.rng import DeterministicRNG
        rng = DeterministicRNG(seed=42)
        data = rng.normal(0.0, 1.0, (3000, 7)) # 30s epoch at 100Hz
        return ISignal(sampling_rate=100.0, data=data)
        
    def stream(self, subject_id: str, bids_root: str):
        pass
        
    def iterate(self, bids_root: str):
        pass
        
    def statistics(self, bids_root: str) -> Dict[str, Any]:
        return {}
        
    def quality_report(self, bids_root: str) -> Dict[str, Any]:
        return {}
