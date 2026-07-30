import os
import sys
import subprocess

def run_gatekeeper():
    print("========================================")
    print("      VIREON VERIFICATION GATEKEEPER    ")
    print("========================================\n")
    
    # Define verification tests
    base_dir = os.environ.get("VIREON_HOME", ".")
    suites = [
        "vireon-verification/numerical/test_psd_crossval.py",
        "vireon-verification/statistical/test_csp_crossval.py",
        "vireon-verification/interoperability/test_format_roundtrip.py",
        "vireon-verification/literature/test_bci_competition.py",
        "vireon-verification/literature/test_seizure.py",
        "vireon-verification/literature/test_sleep_staging.py",
        "vireon-verification/literature/test_erp_p300.py"
    ]
    
    env = os.environ.copy()
    python_path = ":".join([
        os.path.join(base_dir, "vireon-core"),
        os.path.join(base_dir, "vireon-models"),
        os.path.join(base_dir, "vireon-lab"),
        os.path.join(base_dir, "vireon-validation")
    ])
    env["PYTHONPATH"] = python_path
    
    failed = False
    
    for suite in suites:
        print(f"Running {suite}...")
        script_path = os.path.join(base_dir, suite)
        result = subprocess.run(["python3", script_path], env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[FAIL] {suite} failed with exit code {result.returncode}")
            print("--- STDOUT ---")
            print(result.stdout)
            print("--- STDERR ---")
            print(result.stderr)
            failed = True
        else:
            print(f"[PASS] {suite} completed successfully.")
            
    print("\nGenerating Verification Dashboard...")
    dashboard_path = os.path.join(base_dir, "vireon-verification/dashboard.py")
    result = subprocess.run(["python3", dashboard_path], env=env, capture_output=True, text=True)
    
    print(result.stdout)
    
    if "OVERALL VERIFICATION STATUS: FAIL" in result.stdout or failed:
        print("\n[GATEKEEPER REJECTED] Verification suites failed. Release aborted.")
        sys.exit(1)
    else:
        print("\n[GATEKEEPER APPROVED] All verification suites passed. Ready for release.")
        sys.exit(0)

if __name__ == "__main__":
    run_gatekeeper()
