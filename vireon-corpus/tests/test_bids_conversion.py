import os
import tempfile
from vireon_corpus.plugins.eegbci_plugin import EEGBCIPlugin
from vireon_corpus.plugins.erp_core_plugin import ERPCOREPlugin
from vireon_corpus.plugins.sleep_edf_plugin import SleepEDFPlugin

def test_convert_to_bids_structure():
    plugins = [
        (EEGBCIPlugin(), "eegbci", "motorimagery"),
        (ERPCOREPlugin(), "erp-core", "P300"),
        (SleepEDFPlugin(), "sleep-edf", "sleep")
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for plugin, name, task in plugins:
            plugin.convert_to_bids(cache_dir=tmpdir, bids_dir=tmpdir)
            
            bids_root = os.path.join(tmpdir, name)
            assert os.path.exists(bids_root)
            assert os.path.exists(os.path.join(bids_root, "dataset_description.json"))
            assert os.path.exists(os.path.join(bids_root, "participants.tsv"))
            
            eeg_dir = os.path.join(bids_root, "sub-01", "eeg")
            assert os.path.exists(eeg_dir)
            
            files = os.listdir(eeg_dir)
            assert any(f.endswith('.edf') for f in files) or any(f.endswith('.vhdr') for f in files) or any(f.endswith('.set') for f in files)
            assert any(f.endswith('_eeg.json') for f in files)
            assert any(f.endswith('_channels.tsv') for f in files)
            assert any(f.endswith('_events.tsv') for f in files)
