import pytest
import subprocess
import os

def test_reproduce_cli_invalid_doi():
    # Calling the CLI with a missing DOI
    env = os.environ.copy()
    env["PYTHONPATH"] = "vireon-core:vireon-models:vireon-lab:vireon-corpus:vireon-validation:vireon-knowledge"
    
    # We run it from the root of the workspace
    # Since we are in vireon-lab/tests, root is ../../
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    result = subprocess.run(
        ["python", "vireon-lab/vireon_lab/cli/main.py", "reproduce", "invalid.doi"],
        cwd=root_dir,
        env=env,
        capture_output=True,
        text=True
    )
    
    # Should exit with code 2
    assert result.returncode == 2
    assert "[ERROR] DOI invalid.doi not found in registry." in result.stdout

def test_reproduce_cli_valid_doi():
    # Calling the CLI with a valid DOI
    env = os.environ.copy()
    env["PYTHONPATH"] = "vireon-core:vireon-models:vireon-lab:vireon-corpus:vireon-validation:vireon-knowledge"
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    result = subprocess.run(
        ["python", "vireon-lab/vireon_lab/cli/main.py", "reproduce", "10.1109/TAU.1967.1161901"],
        cwd=root_dir,
        env=env,
        capture_output=True,
        text=True
    )
    
    # In mock scenario, measurements are empty so fallback deviation fails, returns 1
    assert result.returncode == 1
    assert "NOT reproduced" in result.stdout
    assert "psd_peak_hz: Expected=10.0000" in result.stdout
