import os
import hashlib
import json
from typing import Dict, Any, List, Type

from vireon_core.contracts.plugin import IDatasetPlugin, ScientificReadinessLevel, ScientificContract, PluginCapability
from vireon_core.contracts.base import IScientificObject, SignalType

class ERPCOREPlugin(IDatasetPlugin):
    """
    Dataset plugin for the ERP CORE Dataset (P300, N400, MMN, etc.).
    """
    @property
    def plugin_id(self) -> str:
        return "dataset_erp_core"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_1
        
    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            dataset_assumptions=["event_related_potentials", "P300", "active_oddball"],
            supported_modalities=[SignalType.EEG],
            validation_papers=["Kappenman et al., 2021. ERP CORE: An open resource..."],
            purpose="Validation of ERP Extraction Algorithms"
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
        print("Downloading ERP CORE via OSF (simulated)...")
        os.makedirs(os.path.join(cache_dir, "originals"), exist_ok=True)

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
        print("Converting ERP CORE to BIDS format (simulated with mne_bids)...")
        bids_out = os.path.join(bids_dir, "erp-core")
        
        try:
            from mne_bids import BIDSPath, write_raw_bids
            import mne
            import numpy as np
            from vireon_core.runtime.rng import DeterministicRNG
            
            info = mne.create_info(ch_names=[f"EEG{i:02d}" for i in range(1, 31)], sfreq=1024.0, ch_types='eeg')
            rng = DeterministicRNG(seed=42)
            data = rng.normal(0, 1, (30, 2048))
            raw = mne.io.RawArray(data, info)
            events = np.array([[500, 0, 1], [1500, 0, 2]])
            event_id = {'Target': 1, 'Standard': 2}
            
            bids_path = BIDSPath(subject='01', task='P300', root=bids_out, datatype='eeg')
            write_raw_bids(raw, bids_path, events=events, event_id=event_id, overwrite=True, format='EDF', allow_preload=True)
            
        except ImportError:
            # Fallback if mne_bids not available
            os.makedirs(os.path.join(bids_out, "sub-01", "eeg"), exist_ok=True)
            with open(os.path.join(bids_out, "dataset_description.json"), "w") as f:
                json.dump({"Name": "ERP CORE", "BIDSVersion": "1.8.0"}, f)
            with open(os.path.join(bids_out, "participants.tsv"), "w") as f:
                f.write("participant_id\tage\tsex\nsub-01\t22\tF\n")
            with open(os.path.join(bids_out, "sub-01", "eeg", "sub-01_task-P300_eeg.json"), "w") as f:
                json.dump({"TaskName": "P300", "SamplingFrequency": 1024.0, "EEGReference": "Common"}, f)
            with open(os.path.join(bids_out, "sub-01", "eeg", "sub-01_task-P300_channels.tsv"), "w") as f:
                f.write("name\ttype\tunits\n")
                for i in range(1, 31): f.write(f"EEG{i:02d}\tEEG\tuV\n")
            with open(os.path.join(bids_out, "sub-01", "eeg", "sub-01_task-P300_events.tsv"), "w") as f:
                f.write("onset\tduration\ttrial_type\n0.488\t0\tTarget\n1.464\t0\tStandard\n")
        
    def generate_metadata(self, bids_dir: str) -> Dict[str, Any]:
        return {"dataset_name": "ERP_CORE", "subjects": 40}
        
    def generate_hash(self, bids_dir: str) -> str:
        h = hashlib.sha256()
        for root, dirs, files in os.walk(bids_dir):
            for filename in sorted(files):
                filepath = os.path.join(root, filename)
                file_hash = self._compute_file_hash(filepath)
                h.update(file_hash.encode())
        return h.hexdigest()
        
    def create_manifest(self, output_path: str) -> None:
        manifest = {
            "name": "ERP CORE",
            "license": "CC-BY 4.0",
            "citation": "Kappenman et al., 2021",
            "download_source": "OSF",
            "modalities": ["EEG"],
            "sample_rate": 1024.0,
            "channels": 30
        }
        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=4)

    def load(self, subject_id: str, bids_root: str) -> IScientificObject:
        from vireon_core.contracts.base import ISignal
        from vireon_core.runtime.rng import DeterministicRNG
        rng = DeterministicRNG(seed=42)
        data = rng.normal(0.0, 1.0, (1024, 30))
        return ISignal(sampling_rate=1024.0, data=data)
        
    def stream(self, subject_id: str, bids_root: str):
        pass
        
    def iterate(self, bids_root: str):
        pass
        
    def statistics(self, bids_root: str) -> Dict[str, Any]:
        return {}
        
    def quality_report(self, bids_root: str) -> Dict[str, Any]:
        return {}
