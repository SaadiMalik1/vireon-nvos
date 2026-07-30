import os

for root, _, files in os.walk('.'):
    if '.git' in root or '.venv' in root or '__pycache__' in root:
        continue
    for file in files:
        if not file.endswith('.py'):
            continue
        filepath = os.path.join(root, file)
        with open(filepath, 'r') as f:
            content = f.read()
            
        modified = False
        if 'vireon_lab.experiments' in content:
            content = content.replace('vireon_lab.experiments', 'vireon_lab.experiments')
            modified = True
        if 'load_experiment_from_yaml' in content:
            content = content.replace('load_experiment_from_yaml', 'load_experiment_from_yaml')
            modified = True
            
        if modified:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Fixed {filepath}")
