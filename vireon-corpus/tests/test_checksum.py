import os
import tempfile
import hashlib
from vireon_corpus.plugins.eegbci_plugin import EEGBCIPlugin

def test_verify_checksum():
    plugin = EEGBCIPlugin()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy file
        dummy_file = os.path.join(tmpdir, "data.bin")
        content = b"test data"
        with open(dummy_file, "wb") as f:
            f.write(content)
            
        expected_hash = hashlib.sha256(content).hexdigest()
        
        # Test 1: expected_checksum provided
        assert plugin.verify_checksum(dummy_file, expected_checksum=expected_hash)
        assert not plugin.verify_checksum(dummy_file, expected_checksum="wrong_hash")
        
        # Test 2: checksums.sha256 provided
        checksums_file = os.path.join(tmpdir, "checksums.sha256")
        with open(checksums_file, "w") as f:
            f.write(f"{expected_hash} data.bin\n")
            
        assert plugin.verify_checksum(tmpdir)
        
        # Test 3: altered file
        with open(dummy_file, "wb") as f:
            f.write(b"altered data")
            
        assert not plugin.verify_checksum(tmpdir)
