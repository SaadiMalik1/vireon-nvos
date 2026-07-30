import os
import sys
import subprocess

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    env = os.environ.copy()
    
    # Add all modules to PYTHONPATH
    paths = [
        os.path.join(base_dir, "vireon-core"),
        os.path.join(base_dir, "vireon-models"),
        os.path.join(base_dir, "vireon-devices"),
        os.path.join(base_dir, "vireon-validation"),
        os.path.join(base_dir, "vireon-knowledge"),
        os.path.join(base_dir, "vireon-lab")
    ]
    
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = ":".join(paths) + (":" + current_pythonpath if current_pythonpath else "")
    
    print("==================================================")
    print("  VIREON VALIDATION ENGINE - REGRESSION SUITE")
    print("==================================================")
    
    # 1. Run unit tests for validators
    print("\n[1/2] Running Statistical & Metric Validators (PyTest)...")
    tests_dir = os.path.join(base_dir, "vireon-validation", "vireon_validation", "tests")
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", tests_dir], env=env)
    
    if result.returncode != 0:
        print("\n[ERROR] Validation of the Validators FAILED.")
        sys.exit(result.returncode)
        
    print("\n[OK] Validation of the Validators PASSED.")
    
    # 2. Run Reference Benchmark
    print("\n[2/2] Running Reference Benchmark Campaign...")
    cli_path = os.path.join(base_dir, "vireon-lab", "vireon_lab", "cli", "main.py")
    result = subprocess.run([sys.executable, cli_path, "experiment", "run", "--campaign", "reference_benchmark_01", "--repetitions", "1"], env=env)
    
    if result.returncode != 0:
        print("\n[ERROR] Reference Benchmark FAILED.")
        sys.exit(result.returncode)
        
    print("\n[OK] Reference Benchmark PASSED.")
    
    print("\n==================================================")
    print("  ALL VALIDATION SUITES PASSED SUCCESSFULLY")
    print("==================================================")

if __name__ == "__main__":
    main()
