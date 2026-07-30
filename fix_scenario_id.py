import os

files_to_update = [
    "vireon-knowledge/tests/test_knowledge_layer.py",
    "vireon-validation/vireon_validation/benchmarks/reporter.py",
    "vireon-validation/tests/test_reproducibility.py",
    "vireon-models/tests/test_real_data_pipeline.py",
    "vireon-lab/vireon_lab/replay.py",
    "vireon-core/vireon_core/kernel/execution_engine.py",
]

for file_path in files_to_update:
    if not os.path.exists(file_path):
        continue
    with open(file_path, "r") as f:
        content = f.read()
    
    new_content = content.replace("scenario_id", "experiment_id")
    
    if new_content != content:
        with open(file_path, "w") as f:
            f.write(new_content)
        print(f"Updated {file_path}")
    
