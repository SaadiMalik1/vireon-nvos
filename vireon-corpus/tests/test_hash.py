import pytest
import os
import tempfile
import hashlib
from vireon_corpus.plugins.eegbci_plugin import EEGBCIPlugin
from vireon_corpus.plugins.erp_core_plugin import ERPCOREPlugin

def test_generate_hash_different_datasets():
    p1 = EEGBCIPlugin()
    p2 = ERPCOREPlugin()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dataset 1
        d1 = os.path.join(tmpdir, "ds1")
        os.makedirs(d1)
        with open(os.path.join(d1, "file.txt"), "w") as f:
            f.write("dataset 1")
            
        # Create dataset 2
        d2 = os.path.join(tmpdir, "ds2")
        os.makedirs(d2)
        with open(os.path.join(d2, "file.txt"), "w") as f:
            f.write("dataset 2")
            
        h1 = p1.generate_hash(d1)
        h2 = p2.generate_hash(d2)
        
        assert len(h1) == 64
        assert len(h2) == 64
        assert h1 != h2

def test_no_stub_hash_string():
    # this is tested via ripgrep in the AC, but we can assert the hashes don't equal the old mock ones
    p = EEGBCIPlugin()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "file.txt"), "w") as f:
            f.write("data")
        assert p.generate_hash(tmpdir) != hashlib.sha256(b"eegbci_stub_data").hexdigest()
