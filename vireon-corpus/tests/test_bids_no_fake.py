import sys
import pytest
from vireon_corpus.plugins.eegbci_plugin import EEGBCIPlugin
from vireon_corpus.plugins.sleep_edf_plugin import SleepEDFPlugin
from vireon_corpus.plugins.erp_core_plugin import ERPCOREPlugin

def test_bids_conversion_raises_without_mne_bids(monkeypatch):
    """If mne_bids is not installed, convert_to_bids should raise ImportError."""
    monkeypatch.setitem(sys.modules, 'mne_bids', None)
    
    for PluginClass in [EEGBCIPlugin, SleepEDFPlugin, ERPCOREPlugin]:
        plugin = PluginClass()
        with pytest.raises(ImportError, match="mne_bids"):
            plugin.convert_to_bids("dummy_source", "/tmp/dummy_bids")

def test_no_fake_edf_files(tmp_path):
    """Ensure no plugin writes fake byte stubs."""
    for PluginClass in [EEGBCIPlugin, SleepEDFPlugin, ERPCOREPlugin]:
        plugin = PluginClass()
        try:
            plugin.convert_to_bids(str(tmp_path / "src"), str(tmp_path / "dst"))
        except (ImportError, FileNotFoundError, Exception):
            pass
            
    forbidden_stub = b"0" * 1000 + b"0" * 24
    for f in tmp_path.rglob("*.edf"):
        content = f.read_bytes()
        assert content != forbidden_stub, f"{f} contains fake stub"
