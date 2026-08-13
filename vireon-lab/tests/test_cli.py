import os
import subprocess

def test_cli_help():
    env = os.environ.copy()
    env["PYTHONPATH"] = ".:vireon-core:vireon-models:vireon-lab:vireon-corpus:vireon-validation:vireon-knowledge:vireon-evidence:vireon-methods:vireon-moabb"
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    result = subprocess.run(
        ["python", "vireon-lab/vireon_lab/cli/main.py", "--help"],
        cwd=root_dir,
        env=env,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "validate" in result.stdout
    assert "inspect" in result.stdout
