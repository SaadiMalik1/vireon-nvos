import os
import json
from glob import glob

def generate_dashboard():
    results_dir = "/home/ronin/Documents/VIREON/vireon-verification/results"
    
    if not os.path.exists(results_dir):
        print("No verification results found. Run the test suites first.")
        return

    print("========================================")
    print("      VIREON VERIFICATION DASHBOARD     ")
    print("========================================\n")

    # Numerical / Statistical (Metrics)
    print("--- 1. Numerical & Statistical Agreement ---")
    metrics_files = [f for f in glob(os.path.join(results_dir, "*_metrics.json")) if "interoperability" not in f and "literature" not in f]
    
    all_passed = True
    
    for mf in metrics_files:
        with open(mf, 'r') as f:
            data = json.load(f)
            status = "PASS" if data.get("pass") else "FAIL"
            if not data.get("pass"): all_passed = False
            
            print(f"[{status}] {data.get('algorithm')} vs {data.get('reference')} (v{data.get('tool_version', 'N/A')})")
            print(f"       RMSE:        {data.get('rmse'):.8e} (Tol: {data.get('tolerance', 'N/A')})")
            print(f"       MAE:         {data.get('mae', 0.0):.8e}")
            print(f"       Max Error:   {data.get('max_error'):.8e}")
            print(f"       Pearson:     {data.get('pearson', data.get('correlation', 0.0)):.6f}")
            if 'spearman' in data:
                print(f"       Spearman:    {data.get('spearman'):.6f}")
            if 'ci_95' in data:
                print(f"       95% CI:      [{data.get('ci_95')[0]:.8e}, {data.get('ci_95')[1]:.8e}]")
            print(f"       N Samples:   {data.get('sample_count', 'N/A')}\n")

    # Interoperability
    print("--- 2. Interoperability ---")
    interop_file = os.path.join(results_dir, "interoperability_metrics.json")
    if os.path.exists(interop_file):
        with open(interop_file, 'r') as f:
            data = json.load(f)
            for k, v in data.items():
                print(f"[{v['status']}] {k}: {v['reason']}")
                if v['status'] == "FAIL": all_passed = False
    else:
        print("No interoperability results.")

    # Literature
    print("\n--- 3. Literature Reproduction ---")
    lit_file = os.path.join(results_dir, "literature_metrics.json")
    if os.path.exists(lit_file):
        with open(lit_file, 'r') as f:
            data = json.load(f)
            for k, v in data.items():
                if v['status'] == "SKIPPED":
                    print(f"[{v['status']}] {k}: {v['reason']}")
                else:
                    print(f"[{v['status']}] {k}: Expected {v['expected']}, Actual {v['actual']}")
                if v['status'] == "FAIL": all_passed = False
    else:
        print("No literature results.")

    print("\n========================================")
    print(f"OVERALL VERIFICATION STATUS: {'PASS' if all_passed else 'FAIL'}")
    print("========================================")

if __name__ == "__main__":
    generate_dashboard()
