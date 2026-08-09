import subprocess
import os
import tempfile
import json
import hashlib

def create_mock_bundle(path, tampered=False):
    os.makedirs(path, exist_ok=True)
    manifest = {}
    
    # Create a valid file
    file1_path = os.path.join(path, "data.json")
    with open(file1_path, "w") as f:
        f.write('{"test": 1}')
    
    with open(file1_path, "rb") as f:
        file1_hash = hashlib.sha256(f.read()).hexdigest()
        
    if tampered:
        # Create hash mismatch
        manifest["data.json"] = "wrong_hash"
    else:
        manifest["data.json"] = file1_hash
        
    with open(os.path.join(path, "hashes.json"), "w") as f:
        json.dump(manifest, f)

def test_verify_cli_valid():
    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_path = os.path.join(tmpdir, "valid_bundle")
        create_mock_bundle(bundle_path, tampered=False)
        
        env = os.environ.copy()
        env["PYTHONPATH"] = "vireon-core:vireon-models:vireon-lab:vireon-corpus:vireon-validation:vireon-knowledge"
        result = subprocess.run(
            ["python", "-m", "vireon_lab.cli.main", "verify", "--bundle", bundle_path],
            env=env,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "[OK]" in result.stdout

def test_verify_cli_tampered():
    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_path = os.path.join(tmpdir, "tampered_bundle")
        create_mock_bundle(bundle_path, tampered=True)
        
        env = os.environ.copy()
        env["PYTHONPATH"] = "vireon-core:vireon-models:vireon-lab:vireon-corpus:vireon-validation:vireon-knowledge"
        result = subprocess.run(
            ["python", "-m", "vireon_lab.cli.main", "verify", "--bundle", bundle_path],
            env=env,
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "[FAIL]" in result.stdout
